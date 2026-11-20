/* Copyright (c) Siemens AG, 2026
 * SPDX-License-Identifier: MIT
 * Fixed-purpose PAM worker. Not setuid; invoked only by trusted root callers.
 */
#define _GNU_SOURCE
#include <fcntl.h>
#include <limits.h>
#include <pwd.h>
#include <security/pam_appl.h>
#include <shadow.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sysexits.h>
#include <sys/prctl.h>
#include <sys/resource.h>
#include <sys/stat.h>
#include <unistd.h>

#ifndef AUTH_ROOT
#define AUTH_ROOT "/var/lib/iot2050-node-red-auth/root"
#endif

/*
 * When changing the username, password or UID limits, update the matching
 * constants in backend.py, which also generates the private login.defs.
 */
enum {
    MAX_USERNAME_LENGTH = 32,
    MAX_PASSWORD_BYTES = PAM_MAX_RESP_SIZE,
    PASSWORD_BUFFER_SIZE = MAX_PASSWORD_BYTES + 2, /* newline and NUL */
    MIN_PRIVATE_UID = 15000,
    MAX_PRIVATE_UID = 60000,
};

enum operation {
    OP_AUTHENTICATE,
    OP_CHANGE,
    OP_ACCOUNT,
};

struct arguments {
    enum operation operation;
    const char *username;
};

/* Check the private username syntax and exclude reserved accounts. */
static bool valid_user(const char *name)
{
    size_t length = strlen(name);

    if (length == 0 || length > MAX_USERNAME_LENGTH ||
        !((name[0] >= 'a' && name[0] <= 'z') || name[0] == '_'))
        return false;

    for (size_t i = 1; i < length; i++) {
        char c = name[i];
        if (!((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') ||
              c == '_' || c == '-'))
            return false;
    }
    return strcmp(name, "root") != 0 && strcmp(name, "nodered") != 0;
}

/* Only the operation and username belong in argv; passwords come from stdin. */
static bool parse_args(int argc, char **argv, struct arguments *args)
{
    if (argc != 3 || !valid_user(argv[2]))
        return false;

    if (strcmp(argv[1], "authenticate") == 0)
        args->operation = OP_AUTHENTICATE;
    else if (strcmp(argv[1], "change") == 0)
        args->operation = OP_CHANGE;
    else if (strcmp(argv[1], "account") == 0)
        args->operation = OP_ACCOUNT;
    else
        return false;

    args->username = argv[2];
    return true;
}

/*
 * Supply the password only for prompts with echo disabled. Ignore PAM text
 * messages rather than passing them to the caller. PAM owns the responses on
 * success; on failure this callback wipes and frees any copies it allocated.
 */
static int conversation(int count, const struct pam_message **messages,
                        struct pam_response **responses, void *data)
{
    const char *password = data;

    if (count <= 0 || count > PAM_MAX_NUM_MSG)
        return PAM_CONV_ERR;

    struct pam_response *result = calloc((size_t)count, sizeof(*result));
    if (result == NULL)
        return PAM_BUF_ERR;

    for (int i = 0; i < count; i++) {
        switch (messages[i]->msg_style) {
        case PAM_PROMPT_ECHO_OFF:
            if (password == NULL)
                goto failure;
            result[i].resp = strdup(password);
            if (result[i].resp == NULL)
                goto failure;
            break;
        case PAM_TEXT_INFO:
        case PAM_ERROR_MSG:
            break;
        default:
            goto failure;
        }
    }
    *responses = result;
    return PAM_SUCCESS;

failure:
    for (int i = 0; i < count; i++) {
        if (result[i].resp != NULL) {
            explicit_bzero(result[i].resp, strlen(result[i].resp));
            free(result[i].resp);
        }
    }
    free(result);
    return PAM_CONV_ERR;
}

/*
 * Read one nonempty, newline-terminated password, then strip the newline.
 * The caller must wipe the buffer even on failure, as it may contain input.
 */
static bool read_password(char password[static PASSWORD_BUFFER_SIZE])
{
    if (fgets(password, PASSWORD_BUFFER_SIZE, stdin) == NULL)
        return false;

    size_t length = strlen(password);
    if (length < 2 || password[length - 1] != '\n' ||
        strchr(password, '\r') != NULL)
        return false;

    password[length - 1] = '\0';
    return true;
}

/*
 * Validate the opened directory and enter it so PAM uses private account files.
 * Close descriptors above stderr so PAM cannot reuse inherited host handles.
 * The root change is process-wide; the caller must exit on failure.
 */
static bool enter_private_root(void)
{
    struct stat info;
    int fd = open(AUTH_ROOT, O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);

    if (fd < 0)
        return false;
    if (fstat(fd, &info) != 0 || info.st_uid != 0 ||
        (info.st_mode & 0077) != 0 || fchdir(fd) != 0 ||
        chroot(".") != 0 || chdir("/") != 0) {
        close(fd);
        return false;
    }
    return close_range(STDERR_FILENO + 1, UINT_MAX, 0) == 0;
}

/* Reject empty or locked shadow entries that pam_acct_mgmt alone can accept. */
static bool has_unlocked_password(const char *username)
{
    const struct spwd *shadow = getspnam(username);

    if (shadow == NULL || shadow->sp_pwdp == NULL)
        return false;

    char first = shadow->sp_pwdp[0];
    return first != '\0' && first != '!' && first != '*';
}

/*
 * Run one operation in the private root and release any PAM handle obtained.
 * Pass NULL for an account-only check. Return a PAM status, not an exit code.
 */
static int run_private_pam(const struct arguments *args, char *password)
{
    pam_handle_t *handle = NULL;
    const struct pam_conv conv = {
        .conv = conversation,
        .appdata_ptr = password,
    };

    if (!enter_private_root())
        return PAM_SYSTEM_ERR;

    const struct passwd *user = getpwnam(args->username);
    if (user == NULL || user->pw_uid < MIN_PRIVATE_UID ||
        user->pw_uid > MAX_PRIVATE_UID)
        return PAM_USER_UNKNOWN;
    if (args->operation == OP_ACCOUNT && !has_unlocked_password(args->username))
        return PAM_AUTH_ERR;

    int status = pam_start("node-red", args->username, &conv, &handle);
    if (status == PAM_SUCCESS) {
        switch (args->operation) {
        case OP_AUTHENTICATE:
            status = pam_authenticate(handle, 0);
            if (status == PAM_SUCCESS)
                status = pam_acct_mgmt(handle, 0);
            break;
        case OP_ACCOUNT:
            status = pam_acct_mgmt(handle, 0);
            break;
        case OP_CHANGE:
            status = pam_chauthtok(handle, 0);
            break;
        default:
            status = PAM_SYSTEM_ERR;
            break;
        }
    }

    if (handle != NULL)
        pam_end(handle, status);
    return status;
}

int main(int argc, char **argv)
{
    struct arguments args;

    if (getuid() != 0 || geteuid() != 0)
        return EX_NOPERM;

    if (!parse_args(argc, argv, &args))
        return EX_USAGE;

    /* Set process protections before receiving a password. */
    const struct rlimit core = { .rlim_cur = 0, .rlim_max = 0 };
    if (setrlimit(RLIMIT_CORE, &core) != 0 || prctl(PR_SET_DUMPABLE, 0) != 0)
        return EX_OSERR;

    char password[PASSWORD_BUFFER_SIZE] = {0};
    bool needs_password = args.operation != OP_ACCOUNT;
    if (needs_password && !read_password(password)) {
        explicit_bzero(password, sizeof(password));
        return EX_DATAERR;
    }

    int status = run_private_pam(&args, needs_password ? password : NULL);
    if (needs_password)
        explicit_bzero(password, sizeof(password));

    printf("{\"status\":%d}\n", status);
    return status == PAM_SUCCESS ? EXIT_SUCCESS : EXIT_FAILURE;
}
