/*
 * Copyright (c) Siemens AG, 2026
 *
 * Authors:
 *  Li Hua Qian <huaqian.li@siemens.com>
 *
 * SPDX-License-Identifier: MIT
 *
 * External Signer Provider
 *
 * OpenSSL provider that delegates signing operations to an external
 * command-line tool for external-signer hash signing while supporting
 * X.509-style flows that require a signer certificate and RSA
 * public-key export.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <errno.h>
#include <stdarg.h>
#include <sys/wait.h>

#include <openssl/provider.h>
#include <openssl/core.h>
#include <openssl/core_dispatch.h>
#include <openssl/core_names.h>
#include <openssl/core_object.h>
#include <openssl/store.h>
#include <openssl/x509v3.h>
#include <openssl/pem.h>
#include <openssl/evp.h>
#include <openssl/params.h>
#include <openssl/param_build.h>
#include <openssl/crypto.h>

#define EXTSIGN_PROVIDER_NAME "OpenSSL External Signer Provider"
#define EXTSIGN_PROVIDER_VERSION "0.1.0"
#define EXTSIGN_PROVIDER_BUILDINFO "External signer provider"
#define EXTSIGN_DEFAULT_SCHEME "extsign"
#define EXTSIGN_MAX_SIGNATURE_SIZE 4096

#define EXTSIGN_PARAM_CLIENT_COMMAND "CLIENT_COMMAND"
#define EXTSIGN_PARAM_CLIENT_HASHFILE "CLIENT_HASHFILE"
#define EXTSIGN_PARAM_CLIENT_SIGNATUREFILE "CLIENT_SIGNATUREFILE"
#define EXTSIGN_PARAM_SIGNER_CERTIFICATE "SIGNER_CERTIFICATE"
#define EXTSIGN_PARAM_SCHEME "SCHEME"
#define EXTSIGN_PARAM_ALGORITHM "ALGORITHM"
#define EXTSIGN_ENV_PREFIX "EXTSIGN_"

#ifdef WITH_DEBUG
#define EXTSIGN_DEBUG(...) extsign_log("DEBUG", __VA_ARGS__)
#else
#define EXTSIGN_DEBUG(...) ((void)0)
#endif
#define EXTSIGN_WARN(...) extsign_log("WARN", __VA_ARGS__)
#define EXTSIGN_ERROR(...) extsign_log("ERROR", __VA_ARGS__)

typedef struct extsign_provider_st EXTSIGN_PROVIDER;
typedef struct extsign_key_st EXTSIGN_KEY;
typedef struct extsign_sigctx_st EXTSIGN_SIGCTX;
typedef struct extsign_store_st EXTSIGN_STORE;

typedef struct extsign_config_st {
	char *command;
	char *hash_path;
	char *signature_path;
	char *certificate_path;
	char *scheme;
	char *algorithm;
} EXTSIGN_CONFIG;

struct extsign_provider_st {
	OSSL_LIB_CTX *libctx;
	char *core_name;
	EXTSIGN_CONFIG config;
	OSSL_ALGORITHM *signature_algorithms;
	OSSL_ALGORITHM *keymgmt_algorithms;
	OSSL_ALGORITHM *store_algorithms;
	unsigned char *certificate_der;
	size_t certificate_der_len;
	EVP_PKEY *public_key;
	BIGNUM *rsa_n;
	BIGNUM *rsa_e;
	int running_command;
};

struct extsign_key_st {
	EXTSIGN_PROVIDER *provider;
	char *uri;
};

struct extsign_sigctx_st {
	EXTSIGN_PROVIDER *provider;
	EVP_MD *md;
	EVP_MD_CTX *mdctx;
	char *key_uri;
};

struct extsign_store_st {
	EXTSIGN_PROVIDER *provider;
	char *uri;
	int expected_type;
	int finished;
};

static int extsign_provider_get_params(void *provctx, OSSL_PARAM params[]);
static const OSSL_PARAM *extsign_provider_gettable_params(void *provctx);
static void extsign_provider_teardown(void *provctx);
static const OSSL_ALGORITHM *extsign_provider_query_operation(void *provctx,
		int operation_id, int *no_cache);

static void *extsign_sig_newctx(void *provctx, const char *propq);
static void extsign_sig_freectx(void *ctx);
static void *extsign_sig_dupctx(void *ctx);
static int extsign_sig_sign_init(void *ctx, void *provkey,
		const OSSL_PARAM params[]);
static int extsign_sig_sign(void *ctx, unsigned char *sigret, size_t *siglen,
		size_t sigsize, const unsigned char *tbs, size_t tbslen);
static int extsign_sig_digest_sign_init(void *ctx, const char *mdname,
		void *provkey, const OSSL_PARAM params[]);
static int extsign_sig_digest_sign_update(void *ctx,
		const unsigned char *data, size_t datalen);
static int extsign_sig_digest_sign_final(void *ctx, unsigned char *sig,
		size_t *siglen, size_t sigsize);
static int extsign_sig_get_ctx_params(void *ctx, OSSL_PARAM params[]);
static const OSSL_PARAM *extsign_sig_gettable_ctx_params(void *ctx,
		void *provctx);

static void *extsign_key_new(void *provctx);
static void extsign_key_free_dispatch(void *keydata);
static void *extsign_key_dup(const void *keydata_from, int selection);
static void *extsign_key_load(const void *reference, size_t reference_sz);
static int extsign_key_match(const void *keydata1, const void *keydata2,
		int selection);
static int extsign_key_has(const void *keydata, int selection);
static int extsign_key_get_params(void *keydata, OSSL_PARAM params[]);
static const OSSL_PARAM *extsign_key_gettable_params(void *provctx);
static int extsign_key_export(void *keydata, int selection,
		OSSL_CALLBACK *param_cb, void *cbarg);
static const OSSL_PARAM *extsign_key_export_types(int selection);

static void *extsign_store_open(void *provctx, const char *uri);
static void *extsign_store_attach(void *provctx, OSSL_CORE_BIO *cin);
static const OSSL_PARAM *extsign_store_settable_ctx_params(void *loaderctx,
		const OSSL_PARAM params[]);
static int extsign_store_set_ctx_params(void *loaderctx,
		const OSSL_PARAM params[]);
static int extsign_store_load(void *loaderctx, OSSL_CALLBACK *data_cb,
		void *data_cbarg, OSSL_PASSPHRASE_CALLBACK *pw_cb, void *pw_cbarg);
static int extsign_store_eof(void *loaderctx);
static int extsign_store_close(void *loaderctx);

static void extsign_log(const char *level, const char *fmt, ...);
static char *extsign_dup(const char *value);
static void extsign_config_cleanup(EXTSIGN_CONFIG *config);
static int extsign_config_load(EXTSIGN_PROVIDER *provider,
		const OSSL_CORE_HANDLE *handle,
		OSSL_FUNC_core_get_params_fn *core_get_params);
static const char *extsign_read_config_value(const char *name,
		const char *fallback);
static int extsign_config_validate(const EXTSIGN_CONFIG *config);
static int extsign_load_certificate(EXTSIGN_PROVIDER *provider);
static OSSL_ALGORITHM *extsign_make_algorithms(const char *algorithm_name,
		const OSSL_DISPATCH *implementation);
static void extsign_provider_free(EXTSIGN_PROVIDER *provider);
static EXTSIGN_KEY *extsign_key_clone(const EXTSIGN_KEY *source);
static void extsign_key_free(EXTSIGN_KEY *key);
static int extsign_set_key_uri(EXTSIGN_SIGCTX *sigctx, const EXTSIGN_KEY *key);
static int extsign_write_all(const char *path, const unsigned char *buffer,
		size_t length);
static int extsign_read_some(const char *path, unsigned char *buffer,
		size_t capacity, size_t *actual_length);
static int extsign_run_signer(EXTSIGN_PROVIDER *provider, const char *key_uri);
static int extsign_store_emit_key(EXTSIGN_STORE *store,
		OSSL_CALLBACK *data_cb, void *data_cbarg);
static int extsign_store_emit_certificate(EXTSIGN_STORE *store,
		OSSL_CALLBACK *data_cb, void *data_cbarg);

#define EXTSIGN_DISPATCH(id, fn) { id, (void (*)(void))(fn) }

static const OSSL_PARAM extsign_provider_param_types[] = {
	OSSL_PARAM_DEFN(OSSL_PROV_PARAM_NAME, OSSL_PARAM_UTF8_PTR, NULL, 0),
	OSSL_PARAM_DEFN(OSSL_PROV_PARAM_VERSION, OSSL_PARAM_UTF8_PTR, NULL, 0),
	OSSL_PARAM_DEFN(OSSL_PROV_PARAM_BUILDINFO, OSSL_PARAM_UTF8_PTR, NULL, 0),
	OSSL_PARAM_DEFN(OSSL_PROV_PARAM_STATUS, OSSL_PARAM_INTEGER, NULL, 0),
	OSSL_PARAM_END
};

static const OSSL_PARAM extsign_key_param_types[] = {
	OSSL_PARAM_DEFN(OSSL_PKEY_PARAM_DEFAULT_DIGEST, OSSL_PARAM_UTF8_STRING, NULL, 0),
	OSSL_PARAM_DEFN(OSSL_PKEY_PARAM_MAX_SIZE, OSSL_PARAM_INTEGER, NULL, 0),
	OSSL_PARAM_END
};

static const OSSL_DISPATCH extsign_signature_functions[] = {
	EXTSIGN_DISPATCH(OSSL_FUNC_SIGNATURE_NEWCTX, extsign_sig_newctx),
	EXTSIGN_DISPATCH(OSSL_FUNC_SIGNATURE_FREECTX, extsign_sig_freectx),
	EXTSIGN_DISPATCH(OSSL_FUNC_SIGNATURE_DUPCTX, extsign_sig_dupctx),
	EXTSIGN_DISPATCH(OSSL_FUNC_SIGNATURE_SIGN_INIT, extsign_sig_sign_init),
	EXTSIGN_DISPATCH(OSSL_FUNC_SIGNATURE_SIGN, extsign_sig_sign),
	EXTSIGN_DISPATCH(OSSL_FUNC_SIGNATURE_DIGEST_SIGN_INIT, extsign_sig_digest_sign_init),
	EXTSIGN_DISPATCH(OSSL_FUNC_SIGNATURE_DIGEST_SIGN_UPDATE, extsign_sig_digest_sign_update),
	EXTSIGN_DISPATCH(OSSL_FUNC_SIGNATURE_DIGEST_SIGN_FINAL, extsign_sig_digest_sign_final),
	EXTSIGN_DISPATCH(OSSL_FUNC_SIGNATURE_GET_CTX_PARAMS, extsign_sig_get_ctx_params),
	EXTSIGN_DISPATCH(OSSL_FUNC_SIGNATURE_GETTABLE_CTX_PARAMS, extsign_sig_gettable_ctx_params),
	EXTSIGN_DISPATCH(0, NULL)
};

static const OSSL_DISPATCH extsign_keymgmt_functions[] = {
	EXTSIGN_DISPATCH(OSSL_FUNC_KEYMGMT_NEW, extsign_key_new),
	EXTSIGN_DISPATCH(OSSL_FUNC_KEYMGMT_FREE, extsign_key_free_dispatch),
	EXTSIGN_DISPATCH(OSSL_FUNC_KEYMGMT_DUP, extsign_key_dup),
	EXTSIGN_DISPATCH(OSSL_FUNC_KEYMGMT_LOAD, extsign_key_load),
	EXTSIGN_DISPATCH(OSSL_FUNC_KEYMGMT_MATCH, extsign_key_match),
	EXTSIGN_DISPATCH(OSSL_FUNC_KEYMGMT_HAS, extsign_key_has),
	EXTSIGN_DISPATCH(OSSL_FUNC_KEYMGMT_EXPORT, extsign_key_export),
	EXTSIGN_DISPATCH(OSSL_FUNC_KEYMGMT_EXPORT_TYPES, extsign_key_export_types),
	EXTSIGN_DISPATCH(OSSL_FUNC_KEYMGMT_GET_PARAMS, extsign_key_get_params),
	EXTSIGN_DISPATCH(OSSL_FUNC_KEYMGMT_GETTABLE_PARAMS, extsign_key_gettable_params),
	EXTSIGN_DISPATCH(0, NULL)
};

static const OSSL_DISPATCH extsign_store_functions[] = {
	EXTSIGN_DISPATCH(OSSL_FUNC_STORE_OPEN, extsign_store_open),
	EXTSIGN_DISPATCH(OSSL_FUNC_STORE_ATTACH, extsign_store_attach),
	EXTSIGN_DISPATCH(OSSL_FUNC_STORE_SETTABLE_CTX_PARAMS, extsign_store_settable_ctx_params),
	EXTSIGN_DISPATCH(OSSL_FUNC_STORE_SET_CTX_PARAMS, extsign_store_set_ctx_params),
	EXTSIGN_DISPATCH(OSSL_FUNC_STORE_LOAD, extsign_store_load),
	EXTSIGN_DISPATCH(OSSL_FUNC_STORE_EOF, extsign_store_eof),
	EXTSIGN_DISPATCH(OSSL_FUNC_STORE_CLOSE, extsign_store_close),
	EXTSIGN_DISPATCH(0, NULL)
};

static const OSSL_DISPATCH extsign_provider_functions[] = {
	EXTSIGN_DISPATCH(OSSL_FUNC_PROVIDER_TEARDOWN, extsign_provider_teardown),
	EXTSIGN_DISPATCH(OSSL_FUNC_PROVIDER_GETTABLE_PARAMS, extsign_provider_gettable_params),
	EXTSIGN_DISPATCH(OSSL_FUNC_PROVIDER_GET_PARAMS, extsign_provider_get_params),
	EXTSIGN_DISPATCH(OSSL_FUNC_PROVIDER_QUERY_OPERATION, extsign_provider_query_operation),
	EXTSIGN_DISPATCH(0, NULL)
};

int OSSL_provider_init(const OSSL_CORE_HANDLE *handle, const OSSL_DISPATCH *in,
		const OSSL_DISPATCH **out, void **provctx)
{
	const OSSL_DISPATCH *entry;
	OSSL_FUNC_core_get_params_fn *core_get_params = NULL;
	OSSL_FUNC_core_gettable_params_fn *core_gettable_params = NULL;
	OSSL_LIB_CTX *child_ctx = NULL;
	EXTSIGN_PROVIDER *provider = NULL;

	for (entry = in; entry->function_id != 0; ++entry) {
		switch (entry->function_id) {
		case OSSL_FUNC_CORE_GET_PARAMS:
			core_get_params = OSSL_FUNC_core_get_params(entry);
			break;
		case OSSL_FUNC_CORE_GETTABLE_PARAMS:
			core_gettable_params = OSSL_FUNC_core_gettable_params(entry);
			break;
		default:
			break;
		}
	}
	if (core_get_params == NULL || core_gettable_params == NULL) {
		EXTSIGN_ERROR("missing required OpenSSL core callbacks");
		return 0;
	}

	child_ctx = OSSL_LIB_CTX_new_child(handle, in);
	if (child_ctx == NULL) {
		return 0;
	}

	provider = OPENSSL_zalloc(sizeof(*provider));
	if (provider == NULL) {
		OSSL_LIB_CTX_free(child_ctx);
		return 0;
	}
	provider->libctx = child_ctx;

	if (!extsign_config_load(provider, handle, core_get_params)) {
		extsign_provider_free(provider);
		return 0;
	}

	provider->signature_algorithms = extsign_make_algorithms(
			provider->config.algorithm, extsign_signature_functions);
	provider->keymgmt_algorithms = extsign_make_algorithms(
			provider->config.algorithm, extsign_keymgmt_functions);
	provider->store_algorithms = extsign_make_algorithms(
			provider->config.scheme, extsign_store_functions);
	if (provider->signature_algorithms == NULL
			|| provider->keymgmt_algorithms == NULL
			|| provider->store_algorithms == NULL) {
		extsign_provider_free(provider);
		return 0;
	}

	EXTSIGN_DEBUG("provider init scheme=%s algorithm=%s command=%s",
			provider->config.scheme,
			provider->config.algorithm,
			provider->config.command);

	*out = extsign_provider_functions;
	*provctx = provider;
	return 1;
}

static int extsign_provider_get_params(void *provctx, OSSL_PARAM params[])
{
	OSSL_PARAM *param;
	(void)provctx;

	param = OSSL_PARAM_locate(params, OSSL_PROV_PARAM_NAME);
	if (param != NULL) {
		OSSL_PARAM_set_utf8_ptr(param, EXTSIGN_PROVIDER_NAME);
	}
	param = OSSL_PARAM_locate(params, OSSL_PROV_PARAM_VERSION);
	if (param != NULL) {
		OSSL_PARAM_set_utf8_ptr(param, EXTSIGN_PROVIDER_VERSION);
	}
	param = OSSL_PARAM_locate(params, OSSL_PROV_PARAM_BUILDINFO);
	if (param != NULL) {
		OSSL_PARAM_set_utf8_ptr(param, EXTSIGN_PROVIDER_BUILDINFO);
	}
	param = OSSL_PARAM_locate(params, OSSL_PROV_PARAM_STATUS);
	if (param != NULL) {
		OSSL_PARAM_set_int(param, 1);
	}
	return 1;
}

static const OSSL_PARAM *extsign_provider_gettable_params(void *provctx)
{
	(void)provctx;
	return extsign_provider_param_types;
}

static void extsign_provider_teardown(void *provctx)
{
	extsign_provider_free((EXTSIGN_PROVIDER *)provctx);
}

static const OSSL_ALGORITHM *extsign_provider_query_operation(void *provctx,
		int operation_id, int *no_cache)
{
	EXTSIGN_PROVIDER *provider = (EXTSIGN_PROVIDER *)provctx;
	const char *op_name;

	switch (operation_id) {
	case OSSL_OP_SIGNATURE:
		op_name = "OSSL_OP_SIGNATURE";
		break;
	case OSSL_OP_KEYMGMT:
		op_name = "OSSL_OP_KEYMGMT";
		break;
	case OSSL_OP_STORE:
		op_name = "OSSL_OP_STORE";
		break;
	default:
		op_name = "Unknown operation";
		break;
	}
	EXTSIGN_DEBUG("query operation=%s provider=%s", op_name,
			provider->core_name != NULL ? provider->core_name : "<unknown>");
	(void)op_name;

	*no_cache = 0;
	if (provider->running_command) {
		EXTSIGN_DEBUG("suppress provider query while external signer is running");
		return NULL;
	}

	switch (operation_id) {
	case OSSL_OP_SIGNATURE:
		return provider->signature_algorithms;
	case OSSL_OP_KEYMGMT:
		return provider->keymgmt_algorithms;
	case OSSL_OP_STORE:
		return provider->store_algorithms;
	default:
		return NULL;
	}
}

static void *extsign_sig_newctx(void *provctx, const char *propq)
{
	EXTSIGN_SIGCTX *sigctx;
	(void)propq;

	sigctx = OPENSSL_zalloc(sizeof(*sigctx));
	if (sigctx != NULL) {
		sigctx->provider = (EXTSIGN_PROVIDER *)provctx;
	}
	return sigctx;
}

static void extsign_sig_freectx(void *ctx)
{
	EXTSIGN_SIGCTX *sigctx = (EXTSIGN_SIGCTX *)ctx;

	if (sigctx == NULL) {
		return;
	}
	EVP_MD_CTX_free(sigctx->mdctx);
	EVP_MD_free(sigctx->md);
	OPENSSL_free(sigctx->key_uri);
	OPENSSL_free(sigctx);
}

static void *extsign_sig_dupctx(void *ctx)
{
	EXTSIGN_SIGCTX *source = (EXTSIGN_SIGCTX *)ctx;
	EXTSIGN_SIGCTX *copy;
	const char *mdname;

	copy = OPENSSL_zalloc(sizeof(*copy));
	if (copy == NULL) {
		return NULL;
	}
	copy->provider = source->provider;
	if (source->key_uri != NULL) {
		copy->key_uri = OPENSSL_strdup(source->key_uri);
		if (copy->key_uri == NULL) {
			extsign_sig_freectx(copy);
			return NULL;
		}
	}
	if (source->md != NULL) {
		mdname = EVP_MD_get0_name(source->md);
		copy->md = mdname == NULL ? NULL : EVP_MD_fetch(source->provider->libctx,
				mdname, "provider=default");
		if (copy->md == NULL) {
			extsign_sig_freectx(copy);
			return NULL;
		}
	}
	if (source->mdctx != NULL) {
		copy->mdctx = EVP_MD_CTX_new();
		if (copy->mdctx == NULL || !EVP_MD_CTX_copy_ex(copy->mdctx, source->mdctx)) {
			extsign_sig_freectx(copy);
			return NULL;
		}
	}
	return copy;
}

static int extsign_sig_sign_init(void *ctx, void *provkey,
		const OSSL_PARAM params[])
{
	EXTSIGN_SIGCTX *sigctx = (EXTSIGN_SIGCTX *)ctx;
	(void)params;

	EVP_MD_CTX_free(sigctx->mdctx);
	sigctx->mdctx = NULL;
	EVP_MD_free(sigctx->md);
	sigctx->md = NULL;
	return extsign_set_key_uri(sigctx, (const EXTSIGN_KEY *)provkey);
}

static int extsign_sig_sign(void *ctx, unsigned char *sigret, size_t *siglen,
		size_t sigsize, const unsigned char *tbs, size_t tbslen)
{
	EXTSIGN_SIGCTX *sigctx = (EXTSIGN_SIGCTX *)ctx;
	EXTSIGN_PROVIDER *provider = sigctx->provider;

	if (sigret == NULL) {
		*siglen = EXTSIGN_MAX_SIGNATURE_SIZE;
		return 1;
	}
	if (sigsize < EXTSIGN_MAX_SIGNATURE_SIZE) {
		return 0;
	}
	if (!extsign_write_all(provider->config.hash_path, tbs, tbslen)) {
		return 0;
	}
	if (!extsign_run_signer(provider, sigctx->key_uri)) {
		return 0;
	}
	return extsign_read_some(provider->config.signature_path, sigret,
			EXTSIGN_MAX_SIGNATURE_SIZE, siglen);
}

static int extsign_sig_digest_sign_init(void *ctx, const char *mdname,
		void *provkey, const OSSL_PARAM params[])
{
	EXTSIGN_SIGCTX *sigctx = (EXTSIGN_SIGCTX *)ctx;
	(void)params;

	EVP_MD_CTX_free(sigctx->mdctx);
	sigctx->mdctx = NULL;
	EVP_MD_free(sigctx->md);
	sigctx->md = NULL;

	if (mdname == NULL) {
		return 0;
	}
	sigctx->md = EVP_MD_fetch(sigctx->provider->libctx, mdname,
			"provider=default");
	if (sigctx->md == NULL) {
		return 0;
	}
	sigctx->mdctx = EVP_MD_CTX_new();
	if (sigctx->mdctx == NULL) {
		return 0;
	}
	if (!EVP_DigestInit_ex(sigctx->mdctx, sigctx->md, NULL)) {
		return 0;
	}
	return extsign_set_key_uri(sigctx, (const EXTSIGN_KEY *)provkey);
}

static int extsign_sig_digest_sign_update(void *ctx,
		const unsigned char *data, size_t datalen)
{
	EXTSIGN_SIGCTX *sigctx = (EXTSIGN_SIGCTX *)ctx;

	if (sigctx->mdctx == NULL) {
		return 0;
	}
	return EVP_DigestUpdate(sigctx->mdctx, data, datalen);
}

static int extsign_sig_digest_sign_final(void *ctx, unsigned char *sig,
		size_t *siglen, size_t sigsize)
{
	EXTSIGN_SIGCTX *sigctx = (EXTSIGN_SIGCTX *)ctx;
	unsigned char digest[EVP_MAX_MD_SIZE];
	unsigned int digest_len = 0;

	if (sig == NULL) {
		*siglen = EXTSIGN_MAX_SIGNATURE_SIZE;
		return 1;
	}
	if (sigsize < EXTSIGN_MAX_SIGNATURE_SIZE) {
		return 0;
	}
	if (sigctx->mdctx == NULL) {
		return 0;
	}
	if (!EVP_DigestFinal_ex(sigctx->mdctx, digest, &digest_len)) {
		return 0;
	}
	return extsign_sig_sign(ctx, sig, siglen, sigsize, digest, digest_len);
}

static int extsign_sig_get_ctx_params(void *ctx, OSSL_PARAM params[])
{
	EXTSIGN_SIGCTX *sigctx = (EXTSIGN_SIGCTX *)ctx;
	OSSL_PARAM *param;
	static const unsigned char rsa_sha512_algorithm_id[] = {
		0x30, 0x0d, 0x06, 0x09, 0x2a, 0x86, 0x48, 0x86,
		0xf7, 0x0d, 0x01, 0x01, 0x0d, 0x05, 0x00
	};

	param = OSSL_PARAM_locate(params, OSSL_SIGNATURE_PARAM_ALGORITHM_ID);
	if (param == NULL) {
		return 1;
	}
	if (sigctx->provider->config.algorithm == NULL
			|| strcasecmp(sigctx->provider->config.algorithm, "RSA") != 0) {
		return 1;
	}
	return OSSL_PARAM_set_octet_string(param,
			rsa_sha512_algorithm_id, sizeof(rsa_sha512_algorithm_id));
}

static const OSSL_PARAM *extsign_sig_gettable_ctx_params(void *ctx,
		void *provctx)
{
	static const OSSL_PARAM gettable[] = {
		OSSL_PARAM_octet_string(OSSL_SIGNATURE_PARAM_ALGORITHM_ID, NULL, 0),
		OSSL_PARAM_END
	};
	(void)ctx;
	(void)provctx;
	return gettable;
}

static void *extsign_key_new(void *provctx)
{
	EXTSIGN_KEY *key;

	key = OPENSSL_zalloc(sizeof(*key));
	if (key != NULL) {
		key->provider = (EXTSIGN_PROVIDER *)provctx;
	}
	return key;
}

static void extsign_key_free_dispatch(void *keydata)
{
	extsign_key_free((EXTSIGN_KEY *)keydata);
}

static void *extsign_key_dup(const void *keydata_from, int selection)
{
	(void)selection;
	return extsign_key_clone((const EXTSIGN_KEY *)keydata_from);
}

static void *extsign_key_load(const void *reference, size_t reference_sz)
{
	EXTSIGN_KEY *key;
	(void)reference_sz;

	if (reference == NULL) {
		return NULL;
	}
	key = *(EXTSIGN_KEY **)reference;
	EXTSIGN_DEBUG("keymgmt load key=%p reference_sz=%zu", (void *)key, reference_sz);
	*(EXTSIGN_KEY **)reference = NULL;
	return key;
}

static int extsign_key_match(const void *keydata1, const void *keydata2,
		int selection)
{
	const EXTSIGN_KEY *left = (const EXTSIGN_KEY *)keydata1;
	const EXTSIGN_KEY *right = (const EXTSIGN_KEY *)keydata2;
	(void)selection;

	if (left == NULL || right == NULL) {
		return left == right;
	}
	if (left->uri == NULL || right->uri == NULL) {
		return left->uri == right->uri;
	}
	return strcmp(left->uri, right->uri) == 0;
}

static int extsign_key_has(const void *keydata, int selection)
{
	const EXTSIGN_KEY *key = (const EXTSIGN_KEY *)keydata;
	int supported = OSSL_KEYMGMT_SELECT_PRIVATE_KEY;

	if (selection == 0) {
		return 1;
	}
	if (key == NULL || key->provider == NULL) {
		return 0;
	}
	if (key->provider->public_key != NULL || key->provider->rsa_n != NULL) {
		supported |= OSSL_KEYMGMT_SELECT_PUBLIC_KEY;
	}
	return (selection & ~supported) == 0;
}

static int extsign_key_get_params(void *keydata, OSSL_PARAM params[])
{
	OSSL_PARAM *param;
	(void)keydata;

	param = OSSL_PARAM_locate(params, OSSL_PKEY_PARAM_DEFAULT_DIGEST);
	if (param != NULL && !OSSL_PARAM_set_utf8_string(param, "SHA512")) {
		return 0;
	}
	param = OSSL_PARAM_locate(params, OSSL_PKEY_PARAM_MAX_SIZE);
	if (param != NULL && !OSSL_PARAM_set_int(param, EXTSIGN_MAX_SIGNATURE_SIZE)) {
		return 0;
	}
	return 1;
}

static const OSSL_PARAM *extsign_key_gettable_params(void *provctx)
{
	(void)provctx;
	return extsign_key_param_types;
}

static int extsign_key_export(void *keydata, int selection,
		OSSL_CALLBACK *param_cb, void *cbarg)
{
	EXTSIGN_KEY *key = (EXTSIGN_KEY *)keydata;
	EXTSIGN_PROVIDER *provider;
	OSSL_PARAM_BLD *builder;
	OSSL_PARAM *params = NULL;
	int ok = 0;

	if (key == NULL || key->provider == NULL) {
		return 0;
	}
	provider = key->provider;
	if ((selection & OSSL_KEYMGMT_SELECT_PUBLIC_KEY) == 0
			|| (selection & OSSL_KEYMGMT_SELECT_PRIVATE_KEY) != 0) {
		return 0;
	}
	if (provider->rsa_n == NULL || provider->rsa_e == NULL) {
		return 0;
	}

	builder = OSSL_PARAM_BLD_new();
	if (builder == NULL) {
		return 0;
	}
	if (!OSSL_PARAM_BLD_push_BN(builder, OSSL_PKEY_PARAM_RSA_N, provider->rsa_n)
			|| !OSSL_PARAM_BLD_push_BN(builder, OSSL_PKEY_PARAM_RSA_E, provider->rsa_e)) {
		goto done;
	}
	params = OSSL_PARAM_BLD_to_param(builder);
	if (params == NULL) {
		goto done;
	}
	ok = param_cb(params, cbarg);

done:
	OSSL_PARAM_free(params);
	OSSL_PARAM_BLD_free(builder);
	return ok;
}

static const OSSL_PARAM *extsign_key_export_types(int selection)
{
	static const OSSL_PARAM rsa_export_types[] = {
		OSSL_PARAM_BN(OSSL_PKEY_PARAM_RSA_N, NULL, 0),
		OSSL_PARAM_BN(OSSL_PKEY_PARAM_RSA_E, NULL, 0),
		OSSL_PARAM_END
	};

	if ((selection & OSSL_KEYMGMT_SELECT_PUBLIC_KEY) != 0) {
		return rsa_export_types;
	}
	return NULL;
}

static void *extsign_store_open(void *provctx, const char *uri)
{
	EXTSIGN_STORE *store;

	store = OPENSSL_zalloc(sizeof(*store));
	if (store == NULL) {
		return NULL;
	}
	store->provider = (EXTSIGN_PROVIDER *)provctx;
	store->uri = extsign_dup(uri);
	if (uri != NULL && store->uri == NULL) {
		OPENSSL_free(store);
		return NULL;
	}
	store->expected_type = 0;
	store->finished = 0;
	EXTSIGN_DEBUG("store open uri=%s", uri != NULL ? uri : "<null>");
	return store;
}

static void *extsign_store_attach(void *provctx, OSSL_CORE_BIO *cin)
{
	(void)provctx;
	(void)cin;
	return NULL;
}

static const OSSL_PARAM *extsign_store_settable_ctx_params(void *loaderctx,
		const OSSL_PARAM params[])
{
	static const OSSL_PARAM settable[] = {
		OSSL_PARAM_int(OSSL_STORE_PARAM_EXPECT, NULL),
		OSSL_PARAM_END
	};
	(void)loaderctx;
	(void)params;
	return settable;
}

static int extsign_store_set_ctx_params(void *loaderctx,
		const OSSL_PARAM params[])
{
	EXTSIGN_STORE *store = (EXTSIGN_STORE *)loaderctx;
	const OSSL_PARAM *param;
	int expect_type = 0;

	if (params == NULL) {
		return 1;
	}
	param = OSSL_PARAM_locate_const(params, OSSL_STORE_PARAM_EXPECT);
	if (param == NULL) {
		return 1;
	}
	if (!OSSL_PARAM_get_int(param, &expect_type)) {
		return 0;
	}
	store->expected_type = expect_type;
	EXTSIGN_DEBUG("store expect type=%d", expect_type);
	return 1;
}

static int extsign_store_load(void *loaderctx, OSSL_CALLBACK *data_cb,
		void *data_cbarg, OSSL_PASSPHRASE_CALLBACK *pw_cb, void *pw_cbarg)
{
	EXTSIGN_STORE *store = (EXTSIGN_STORE *)loaderctx;
	(void)pw_cb;
	(void)pw_cbarg;

	if (store->finished) {
		return 0;
	}
	store->finished = 1;
	EXTSIGN_DEBUG("store load type=%d (4=pkey,5=cert)", store->expected_type);
	switch (store->expected_type) {
	case 0:
	case OSSL_STORE_INFO_PKEY:
		return extsign_store_emit_key(store, data_cb, data_cbarg);
	case OSSL_STORE_INFO_CERT:
		return extsign_store_emit_certificate(store, data_cb, data_cbarg);
	default:
		return 0;
	}
}

static int extsign_store_eof(void *loaderctx)
{
	EXTSIGN_STORE *store = (EXTSIGN_STORE *)loaderctx;
	return store->finished;
}

static int extsign_store_close(void *loaderctx)
{
	EXTSIGN_STORE *store = (EXTSIGN_STORE *)loaderctx;

	if (store == NULL) {
		return 1;
	}
	OPENSSL_free(store->uri);
	OPENSSL_free(store);
	return 1;
}

static void extsign_log(const char *level, const char *fmt, ...)
{
	va_list args;

	fprintf(stderr, "[extsign][%s]: ", level);
	va_start(args, fmt);
	vfprintf(stderr, fmt, args);
	va_end(args);
	fputc('\n', stderr);
}

static char *extsign_dup(const char *value)
{
	if (value == NULL) {
		return NULL;
	}
	return OPENSSL_strdup(value);
}

static void extsign_config_cleanup(EXTSIGN_CONFIG *config)
{
	OPENSSL_free(config->command);
	OPENSSL_free(config->hash_path);
	OPENSSL_free(config->signature_path);
	OPENSSL_free(config->certificate_path);
	OPENSSL_free(config->scheme);
	OPENSSL_free(config->algorithm);
	memset(config, 0, sizeof(*config));
}

static int extsign_config_load(EXTSIGN_PROVIDER *provider,
		const OSSL_CORE_HANDLE *handle,
		OSSL_FUNC_core_get_params_fn *core_get_params)
{
	char *core_name = NULL;
	char *raw_command = NULL;
	char *raw_hash = NULL;
	char *raw_signature = NULL;
	char *raw_certificate = NULL;
	char *raw_scheme = NULL;
	char *raw_algorithm = NULL;
	OSSL_PARAM core_params[] = {
		OSSL_PARAM_construct_utf8_ptr(OSSL_PROV_PARAM_CORE_PROV_NAME,
				&core_name, sizeof(core_name)),
		OSSL_PARAM_construct_utf8_ptr(EXTSIGN_PARAM_CLIENT_COMMAND,
				&raw_command, sizeof(raw_command)),
		OSSL_PARAM_construct_utf8_ptr(EXTSIGN_PARAM_CLIENT_HASHFILE,
				&raw_hash, sizeof(raw_hash)),
		OSSL_PARAM_construct_utf8_ptr(EXTSIGN_PARAM_CLIENT_SIGNATUREFILE,
				&raw_signature, sizeof(raw_signature)),
		OSSL_PARAM_construct_utf8_ptr(EXTSIGN_PARAM_SIGNER_CERTIFICATE,
				&raw_certificate, sizeof(raw_certificate)),
		OSSL_PARAM_construct_utf8_ptr(EXTSIGN_PARAM_SCHEME,
				&raw_scheme, sizeof(raw_scheme)),
		OSSL_PARAM_construct_utf8_ptr(EXTSIGN_PARAM_ALGORITHM,
				&raw_algorithm, sizeof(raw_algorithm)),
		OSSL_PARAM_END
	};

	if (!core_get_params(handle, core_params)) {
		EXTSIGN_ERROR("failed to read provider configuration from core");
		return 0;
	}

	provider->core_name = extsign_dup(core_name);
	provider->config.command = extsign_dup(
			extsign_read_config_value(EXTSIGN_PARAM_CLIENT_COMMAND, raw_command));
	provider->config.hash_path = extsign_dup(
			extsign_read_config_value(EXTSIGN_PARAM_CLIENT_HASHFILE, raw_hash));
	provider->config.signature_path = extsign_dup(
			extsign_read_config_value(EXTSIGN_PARAM_CLIENT_SIGNATUREFILE, raw_signature));
	provider->config.certificate_path = extsign_dup(
			extsign_read_config_value(EXTSIGN_PARAM_SIGNER_CERTIFICATE, raw_certificate));
	provider->config.scheme = extsign_dup(
			extsign_read_config_value(EXTSIGN_PARAM_SCHEME,
				raw_scheme != NULL ? raw_scheme : EXTSIGN_DEFAULT_SCHEME));
	provider->config.algorithm = extsign_dup(
			extsign_read_config_value(EXTSIGN_PARAM_ALGORITHM, raw_algorithm));

	if (!extsign_config_validate(&provider->config)) {
		return 0;
	}
	return extsign_load_certificate(provider);
}

static const char *extsign_read_config_value(const char *name,
		const char *fallback)
{
	char env_name[128];
	const char *value;
	int written;

	written = snprintf(env_name, sizeof(env_name), "%s%s", EXTSIGN_ENV_PREFIX, name);
	if (written <= 0 || (size_t)written >= sizeof(env_name)) {
		return fallback;
	}
	value = getenv(env_name);
	return value != NULL ? value : fallback;
}

static int extsign_config_validate(const EXTSIGN_CONFIG *config)
{
	if (config->command == NULL || config->command[0] == '\0') {
		EXTSIGN_ERROR("missing CLIENT_COMMAND / EXTSIGN_CLIENT_COMMAND");
		return 0;
	}
	if (config->hash_path == NULL || config->hash_path[0] == '\0') {
		EXTSIGN_ERROR("missing CLIENT_HASHFILE / EXTSIGN_CLIENT_HASHFILE");
		return 0;
	}
	if (config->signature_path == NULL || config->signature_path[0] == '\0') {
		EXTSIGN_ERROR("missing CLIENT_SIGNATUREFILE / EXTSIGN_CLIENT_SIGNATUREFILE");
		return 0;
	}
	if (config->scheme == NULL || config->scheme[0] == '\0') {
		EXTSIGN_ERROR("missing SCHEME / EXTSIGN_SCHEME");
		return 0;
	}
	if ((config->certificate_path == NULL || config->certificate_path[0] == '\0')
			&& (config->algorithm == NULL || config->algorithm[0] == '\0')) {
		EXTSIGN_ERROR("missing SIGNER_CERTIFICATE/ALGORITHM configuration");
		return 0;
	}
	return 1;
}

static int extsign_load_certificate(EXTSIGN_PROVIDER *provider)
{
	BIO *bio;
	X509 *cert;
	const char *pubkey_algorithm = NULL;

	if (provider->config.certificate_path == NULL) {
		return provider->config.algorithm != NULL;
	}
	bio = BIO_new_file(provider->config.certificate_path, "r");
	if (bio == NULL) {
		EXTSIGN_ERROR("could not load signer certificate from %s",
				provider->config.certificate_path);
		return 0;
	}
	cert = PEM_read_bio_X509(bio, NULL, NULL, NULL);
	BIO_free(bio);
	if (cert == NULL) {
		EXTSIGN_ERROR("could not parse signer certificate from %s",
				provider->config.certificate_path);
		return 0;
	}
	provider->public_key = X509_get_pubkey(cert);
	if (provider->public_key != NULL) {
		pubkey_algorithm = EVP_PKEY_get0_type_name(provider->public_key);
		EVP_PKEY_get_bn_param(provider->public_key, OSSL_PKEY_PARAM_RSA_N,
				&provider->rsa_n);
		EVP_PKEY_get_bn_param(provider->public_key, OSSL_PKEY_PARAM_RSA_E,
				&provider->rsa_e);
	}
	if (pubkey_algorithm != NULL) {
		OPENSSL_free(provider->config.algorithm);
		provider->config.algorithm = OPENSSL_strdup(pubkey_algorithm);
	}
	provider->certificate_der_len = i2d_X509(cert, &provider->certificate_der);
	X509_free(cert);
	return provider->config.algorithm != NULL;
}

static OSSL_ALGORITHM *extsign_make_algorithms(const char *algorithm_name,
		const OSSL_DISPATCH *implementation)
{
	static const char properties[] = "provider=extsign_provider";
	OSSL_ALGORITHM *algorithms;

	algorithms = OPENSSL_zalloc(2 * sizeof(*algorithms));
	if (algorithms == NULL) {
		return NULL;
	}
	algorithms[0].algorithm_names = algorithm_name;
	algorithms[0].property_definition = properties;
	algorithms[0].implementation = implementation;
	return algorithms;
}

static void extsign_provider_free(EXTSIGN_PROVIDER *provider)
{
	if (provider == NULL) {
		return;
	}
	OPENSSL_free(provider->core_name);
	OPENSSL_free(provider->signature_algorithms);
	OPENSSL_free(provider->keymgmt_algorithms);
	OPENSSL_free(provider->store_algorithms);
	OPENSSL_free(provider->certificate_der);
	EVP_PKEY_free(provider->public_key);
	BN_free(provider->rsa_n);
	BN_free(provider->rsa_e);
	extsign_config_cleanup(&provider->config);
	OSSL_LIB_CTX_free(provider->libctx);
	OPENSSL_free(provider);
}

static EXTSIGN_KEY *extsign_key_clone(const EXTSIGN_KEY *source)
{
	EXTSIGN_KEY *copy;

	if (source == NULL) {
		return NULL;
	}
	copy = OPENSSL_zalloc(sizeof(*copy));
	if (copy == NULL) {
		return NULL;
	}
	copy->provider = source->provider;
	copy->uri = extsign_dup(source->uri);
	if (source->uri != NULL && copy->uri == NULL) {
		extsign_key_free(copy);
		return NULL;
	}
	return copy;
}

static void extsign_key_free(EXTSIGN_KEY *key)
{
	if (key == NULL) {
		return;
	}
	OPENSSL_free(key->uri);
	OPENSSL_free(key);
}

static int extsign_set_key_uri(EXTSIGN_SIGCTX *sigctx, const EXTSIGN_KEY *key)
{
	OPENSSL_free(sigctx->key_uri);
	sigctx->key_uri = NULL;
	if (key == NULL || key->uri == NULL) {
		return 1;
	}
	sigctx->key_uri = OPENSSL_strdup(key->uri);
	return sigctx->key_uri != NULL;
}

static int extsign_write_all(const char *path, const unsigned char *buffer,
		size_t length)
{
	FILE *stream;

	stream = fopen(path, "wb");
	if (stream == NULL) {
		EXTSIGN_ERROR("cannot open hash file %s: %s", path, strerror(errno));
		return 0;
	}
	if (length != 0 && fwrite(buffer, 1, length, stream) != length) {
		EXTSIGN_ERROR("cannot write hash file %s", path);
		fclose(stream);
		return 0;
	}
	if (fclose(stream) != 0) {
		EXTSIGN_ERROR("cannot close hash file %s", path);
		return 0;
	}
	return 1;
}

static int extsign_read_some(const char *path, unsigned char *buffer,
		size_t capacity, size_t *actual_length)
{
	FILE *stream;
	size_t bytes_read;

	stream = fopen(path, "rb");
	if (stream == NULL) {
		EXTSIGN_ERROR("cannot open signature file %s: %s", path, strerror(errno));
		return 0;
	}
	bytes_read = fread(buffer, 1, capacity, stream);
	if (ferror(stream)) {
		EXTSIGN_ERROR("cannot read signature file %s", path);
		fclose(stream);
		return 0;
	}
	if (fclose(stream) != 0) {
		EXTSIGN_ERROR("cannot close signature file %s", path);
		return 0;
	}
	if (bytes_read == 0) {
		EXTSIGN_ERROR("signature file %s is empty", path);
		return 0;
	}
	*actual_length = bytes_read;
	return 1;
}

static int extsign_run_signer(EXTSIGN_PROVIDER *provider, const char *key_uri)
{
	char command_buffer[2048];
	const char *command = provider->config.command;
	const char *key_id = key_uri;
	char quote = '"';
	int system_result;
	int exit_status;

	if (key_id != NULL && provider->config.scheme != NULL) {
		size_t scheme_len = strlen(provider->config.scheme);
		if (strncasecmp(key_id, provider->config.scheme, scheme_len) == 0
				&& key_id[scheme_len] == ':') {
			key_id += scheme_len + 1;
		}
	}
	if (key_id != NULL) {
		if (strchr(key_id, '"') != NULL) {
			quote = '\'';
		}
		if (snprintf(command_buffer, sizeof(command_buffer), "%s %c%s%c",
				provider->config.command, quote, key_id, quote) >= (int)sizeof(command_buffer)) {
			EXTSIGN_ERROR("external signer command is too long");
			return 0;
		}
		command = command_buffer;
		setenv("EXTSIGN_SIGNER_KEY_ID", key_uri, 1);
	}

	EXTSIGN_DEBUG("running external signer command: %s", command);
	provider->running_command = 1;
	system_result = system(command);
	provider->running_command = 0;

	if (system_result == -1) {
		EXTSIGN_ERROR("system() failed for external signer command: %s",
				strerror(errno));
		return 0;
	}
	if (!WIFEXITED(system_result)) {
		EXTSIGN_ERROR("external signer command terminated abnormally");
		return 0;
	}
	exit_status = WEXITSTATUS(system_result);
	if (exit_status == 127) {
		EXTSIGN_ERROR("no shell available to run external signer command");
		return 0;
	}
	if (exit_status != 0) {
		EXTSIGN_WARN("external signer command exited with status %d", exit_status);
		return 0;
	}
	return 1;
}

static int extsign_store_emit_key(EXTSIGN_STORE *store,
		OSSL_CALLBACK *data_cb, void *data_cbarg)
{
	OSSL_PARAM params[5];
	OSSL_PARAM *param = params;
	EXTSIGN_KEY *key;
	int object_type = OSSL_OBJECT_PKEY;

	key = OPENSSL_zalloc(sizeof(*key));
	if (key == NULL) {
		return 0;
	}
	key->provider = store->provider;
	key->uri = extsign_dup(store->uri);
	if (store->uri != NULL && key->uri == NULL) {
		extsign_key_free(key);
		return 0;
	}

	*param++ = OSSL_PARAM_construct_utf8_string(OSSL_OBJECT_PARAM_DATA_TYPE,
			store->provider->config.algorithm, 0);
	*param++ = OSSL_PARAM_construct_utf8_string(OSSL_OBJECT_PARAM_DATA_STRUCTURE,
			"PrivateKeyInfo", 0);
	*param++ = OSSL_PARAM_construct_octet_string(OSSL_OBJECT_PARAM_REFERENCE,
			&key, sizeof(key));
	*param++ = OSSL_PARAM_construct_int(OSSL_OBJECT_PARAM_TYPE, &object_type);
	*param = OSSL_PARAM_construct_end();

	if (!data_cb(params, data_cbarg)) {
		extsign_key_free(key);
		return 0;
	}
	return 1;
}

static int extsign_store_emit_certificate(EXTSIGN_STORE *store,
		OSSL_CALLBACK *data_cb, void *data_cbarg)
{
	OSSL_PARAM params[5];
	OSSL_PARAM *param = params;
	int object_type = OSSL_OBJECT_CERT;

	if (store->provider->certificate_der == NULL
			|| store->provider->certificate_der_len == 0) {
		return 0;
	}

	*param++ = OSSL_PARAM_construct_utf8_string(OSSL_OBJECT_PARAM_DATA_TYPE,
			store->provider->config.scheme, 0);
	*param++ = OSSL_PARAM_construct_utf8_string(OSSL_OBJECT_PARAM_DATA_STRUCTURE,
			"Certificate", 0);
	*param++ = OSSL_PARAM_construct_octet_string(OSSL_OBJECT_PARAM_DATA,
			store->provider->certificate_der, store->provider->certificate_der_len);
	*param++ = OSSL_PARAM_construct_int(OSSL_OBJECT_PARAM_TYPE, &object_type);
	*param = OSSL_PARAM_construct_end();

	return data_cb(params, data_cbarg);
}
