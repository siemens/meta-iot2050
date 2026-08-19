const form = document.getElementById('onboarding-form');
const statusBanner = document.getElementById('status-banner');
const hostnameHint = document.getElementById('hostname-hint');
const submitButton = document.getElementById('submit-button');
const setupView = document.getElementById('setup-view');
const waitView = document.getElementById('wait-view');
const waitEyebrow = document.getElementById('wait-eyebrow');
const waitTitle = document.getElementById('wait-title');
const waitCopy = document.getElementById('wait-copy');
const waitFootnote = document.getElementById('wait-footnote');
const passwordGuidance = document.getElementById('password-guidance');
const passwordVisibilityButtons = document.querySelectorAll('[data-password-toggle]');

const cockpit = window.cockpit || {
  language: 'en',
  language_direction: 'ltr',
  gettext(context, string) {
    return string === undefined ? context : string;
  },
};

const _ = cockpit.gettext.bind(cockpit);
const rootElement = document.documentElement;
const UNCONFIGURED_HOSTNAMES = new Set(['', 'localhost', 'localhost.localdomain', 'localhost6', 'localhost6.localdomain6', '(none)', 'none']);
const RESERVED_USERNAMES = new Set(['root']);
const WAIT_TITLE = 'Applying your configuration';
const WAIT_FOOTNOTE = 'Please keep this page open to ensure your configuration is applied safely.';
const REDIRECT_FALLBACK_FOOTNOTE = 'If automatic redirection does not complete, open {url} manually.';
const REDIRECT_FALLBACK_COPY = 'Automatic redirection did not complete. Open {url} manually.';
const REDIRECT_FALLBACK_DELAY_MS = 4000;

let cockpitRedirectFallbackTimer = 0;
let isSubmitting = false;

const MESSAGE_ALIASES = {
  'Use at least 8 characters.': 'Choose a stronger password',
  'Use at least 12 characters.': 'Choose a stronger password',
  'Cockpit did not become ready in time.': 'Timed out while waiting for Cockpit to start.',
};

const fieldMap = {
  deviceName: document.getElementById('device-name'),
  username: document.getElementById('user-name'),
  password: document.getElementById('password'),
  confirmPassword: document.getElementById('confirm-password'),
};

function t(messageId, replacements = {}) {
  let message = _(messageId);
  Object.entries(replacements).forEach(([name, value]) => {
    message = message.replace(`{${name}}`, value);
  });
  return message;
}

function localizeMessage(message) {
  if (!message) {
    return message;
  }

  const messageId = MESSAGE_ALIASES[message] || message;
  return _(messageId);
}

function hasConfiguredHostname(hostname) {
  const normalized = String(hostname || '').trim().toLowerCase();
  return Boolean(normalized) && !UNCONFIGURED_HOSTNAMES.has(normalized);
}

function applyTranslations() {
  document.documentElement.lang = (cockpit.language || 'en').replace('_', '-');
  document.documentElement.dir = cockpit.language_direction || 'ltr';
  document.title = 'IOT2050 onboarding';

  document.getElementById('setup-title').textContent = _('Create your account');
  document.getElementById('device-name-label').textContent = _('Host name');
  document.getElementById('user-name-label').textContent = _('User name');
  document.getElementById('password-label').textContent = _('Password');
  document.getElementById('confirm-password-label').textContent = _('Confirm password');
  document.getElementById('password-guidance-title').textContent = _('Password requirements');
  const passwordTexts = {
    length: 'At least 12 characters',
    classes: 'At least 3 of 4: lowercase, uppercase, number, and symbol',
    repeat: 'No more than 3 repeated characters in a row',
    sequence: 'Avoid simple sequential characters',
    username: 'Do not include the user name',
    'system-policy': 'The system also checks dictionary words and account information.',
  };
  Object.entries(passwordTexts).forEach(([rule, message]) => {
    const element = document.querySelector(`[data-password-text="${rule}"]`);
    if (element) {
      element.textContent = _(message);
    }
  });
  waitEyebrow.hidden = true;
  waitEyebrow.textContent = '';
  waitCopy.hidden = true;
  waitCopy.textContent = '';
  waitFootnote.textContent = _(WAIT_FOOTNOTE);
  hostnameHint.hidden = true;
  hostnameHint.textContent = '';

  fieldMap.deviceName.placeholder = 'iot2050-edge-01';
  fieldMap.username.placeholder = _('username');
  fieldMap.password.placeholder = _('Enter a strong password');
  fieldMap.confirmPassword.placeholder = _('Repeat the password');

  resetSubmitButton();
}

function resetSubmitButton() {
  submitButton.textContent = _('Save and continue');
}

function updatePasswordVisibilityButton(button, visible) {
  const message = visible ? _('Hide password') : _('Show password');
  button.setAttribute('aria-label', message);
  button.setAttribute('aria-pressed', String(visible));
  button.setAttribute('title', message);
}

function syncPasswordVisibilityButton(button) {
  const input = document.getElementById(button.dataset.passwordToggle);
  if (!input) {
    return;
  }

  const hasPassword = input.value.length > 0;
  button.hidden = !hasPassword;
  if (!hasPassword && input.type !== 'password') {
    input.type = 'password';
    updatePasswordVisibilityButton(button, false);
  }
}

function togglePasswordVisibility(event) {
  const button = event.currentTarget;
  const input = document.getElementById(button.dataset.passwordToggle);
  if (!input) {
    return;
  }
  const selectionStart = input.selectionStart;
  const selectionEnd = input.selectionEnd;
  const visible = input.type === 'password';
  input.type = visible ? 'text' : 'password';
  updatePasswordVisibilityButton(button, visible);
  input.focus();
  if (selectionStart !== null && selectionEnd !== null) {
    input.setSelectionRange(selectionStart, selectionEnd);
  }
}

function formatHostForUrl(host) {
  if (!host) {
    return window.location.hostname;
  }

  if (host.includes(':') && !host.startsWith('[')) {
    return `[${host}]`;
  }

  return host;
}

function resolveCockpitUrl(redirectUrl) {
  if (redirectUrl) {
    return redirectUrl;
  }

  return `https://${formatHostForUrl(window.location.hostname)}/`;
}

function clearCockpitRedirectFallbackTimer() {
  if (!cockpitRedirectFallbackTimer) {
    return;
  }

  window.clearTimeout(cockpitRedirectFallbackTimer);
  cockpitRedirectFallbackTimer = 0;
}

function showCockpitAccessFallback(message, redirectUrl) {
  const cockpitUrl = resolveCockpitUrl(redirectUrl);
  showWaitView(_('Unable to finish the handoff'), message, 'error', {
    footnote: t(REDIRECT_FALLBACK_FOOTNOTE, { url: cockpitUrl }),
  });
}

function redirectToCockpit(redirectUrl) {
  const cockpitUrl = resolveCockpitUrl(redirectUrl);

  clearCockpitRedirectFallbackTimer();
  showWaitView(_(WAIT_TITLE), '', 'success', {
    footnote: t(REDIRECT_FALLBACK_FOOTNOTE, { url: cockpitUrl }),
  });

  window.addEventListener('pagehide', clearCockpitRedirectFallbackTimer, { once: true });
  cockpitRedirectFallbackTimer = window.setTimeout(() => {
    showWaitView(_('Unable to finish the handoff'), t(REDIRECT_FALLBACK_COPY, { url: cockpitUrl }), 'error');
  }, REDIRECT_FALLBACK_DELAY_MS);

  window.location.href = cockpitUrl;
}

function showSetupView() {
  clearCockpitRedirectFallbackTimer();
  rootElement.dataset.view = 'setup';
  setupView.hidden = false;
  waitView.hidden = true;
}

function showWaitView(title, copy = '', variant = 'info', options = {}) {
  const footnote = Object.prototype.hasOwnProperty.call(options, 'footnote')
    ? options.footnote
    : (variant === 'error' ? '' : _(WAIT_FOOTNOTE));

  rootElement.dataset.view = 'wait';
  setupView.hidden = true;
  waitView.hidden = false;
  waitView.dataset.variant = variant;
  statusBanner.hidden = true;
  waitTitle.textContent = title;
  waitCopy.hidden = !copy;
  waitCopy.textContent = copy;
  waitFootnote.hidden = !footnote;
  waitFootnote.textContent = footnote;
}

function setBanner(type, message) {
  showSetupView();
  statusBanner.hidden = false;
  statusBanner.className = `status-banner ${type}`;
  statusBanner.textContent = message;
}

function clearBanner() {
  statusBanner.hidden = true;
  statusBanner.className = 'status-banner';
  statusBanner.textContent = '';
}

function setFieldError(name, message) {
  const input = fieldMap[name];
  const target = document.querySelector(`[data-error-for="${name}"]`);

  if (input) {
    input.classList.add('invalid');
  }

  if (target) {
    target.textContent = localizeMessage(message);
    target.classList.add('active');
  }
}

function clearFieldError(name) {
  const input = fieldMap[name];
  const target = document.querySelector(`[data-error-for="${name}"]`);

  if (input) {
    input.classList.remove('invalid');
  }

  if (target) {
    target.textContent = '';
    target.classList.remove('active');
  }
}

function clearErrors() {
  Object.keys(fieldMap).forEach((name) => {
    clearFieldError(name);
  });
}

function applyFieldErrors(fieldErrors = {}) {
  clearErrors();
  Object.entries(fieldErrors).forEach(([name, message]) => {
    setFieldError(name, message);
  });
}

function focusFirstFieldError(fieldErrors = {}) {
  const fieldName = Object.keys(fieldMap).find(name => fieldErrors[name]);
  if (fieldName) {
    fieldMap[fieldName].focus();
  }
}

function getPasswordGuidanceResults(password, username) {
  const normalizedPassword = String(password || '');
  const normalizedUsername = String(username || '').trim().toLowerCase();

  return {
    length: normalizedPassword.length >= 12,
    classes: [/[a-z]/, /[A-Z]/, /[0-9]/, /[^A-Za-z0-9]/]
      .filter(pattern => pattern.test(normalizedPassword)).length >= 3,
    repeat: !/(.)\1\1\1/.test(normalizedPassword),
    sequence: !hasSimpleSequence(normalizedPassword),
    username: !normalizedUsername || !normalizedPassword.toLowerCase().includes(normalizedUsername),
  };
}

const PASSWORD_RULE_MESSAGES = {
  length: 'Use at least 12 characters.',
  classes: 'Use at least 3 of 4 character types: lowercase, uppercase, number, and symbol.',
  repeat: 'Do not repeat the same character more than 3 times in a row.',
  sequence: 'Avoid simple sequential characters.',
  username: 'Do not include the user name in the password.',
};

function getClientFieldErrors(payload, options = {}) {
  const fieldErrors = {};
  const normalizedUsername = String(payload.username || '').trim().toLowerCase();
  const password = String(payload.password || '');
  const confirmPassword = String(payload.confirmPassword || '');
  const validateConfirmation = options.validateConfirmation || Boolean(confirmPassword);

  if (RESERVED_USERNAMES.has(normalizedUsername)) {
    fieldErrors.username = 'Create a non-root administrator account.';
  }

  if (!password) {
    fieldErrors.password = 'Choose a password.';
  } else {
    const passwordResults = getPasswordGuidanceResults(password, normalizedUsername);
    const failedRules = Object.keys(PASSWORD_RULE_MESSAGES)
      .filter(rule => !passwordResults[rule])
      .map(rule => PASSWORD_RULE_MESSAGES[rule]);
    if (failedRules.length > 0) {
      fieldErrors.password = failedRules.join(' ');
    }
  }

  if (validateConfirmation && confirmPassword !== password) {
    fieldErrors.confirmPassword = 'Passwords do not match.';
  }

  return fieldErrors;
}

function updatePasswordGuidance() {
  if (!passwordGuidance) {
    return;
  }

  const password = fieldMap.password.value;
  const username = fieldMap.username.value.trim().toLowerCase();
  const results = getPasswordGuidanceResults(password, username);

  Object.entries(results).forEach(([rule, met]) => {
    const item = passwordGuidance.querySelector(`[data-password-rule="${rule}"]`);
    if (!item) {
      return;
    }
    item.classList.toggle('met', met);
    const marker = item.querySelector('.password-rule-marker');
    if (marker) {
      marker.textContent = met ? '✓' : '○';
    }
  });
}

function hasSimpleSequence(password) {
  const normalized = password.toLowerCase();
  for (let index = 0; index <= normalized.length - 4; index += 1) {
    const chunk = normalized.slice(index, index + 4);
    let ascending = true;
    let descending = true;
    for (let offset = 1; offset < chunk.length; offset += 1) {
      const difference = chunk.charCodeAt(offset) - chunk.charCodeAt(offset - 1);
      ascending = ascending && difference === 1;
      descending = descending && difference === -1;
    }
    if (ascending || descending) {
      return true;
    }
  }
  return false;
}

function updateSubmitButtonState() {
  submitButton.disabled = isSubmitting;
}

function handleUsernameInput() {
  const fieldErrors = getClientFieldErrors(collectPayload());

  if (fieldErrors.username) {
    setFieldError('username', fieldErrors.username);
  } else {
    clearFieldError('username');
  }

  if (fieldErrors.password) {
    setFieldError('password', fieldErrors.password);
  } else {
    clearFieldError('password');
  }

  updateSubmitButtonState();
  updatePasswordGuidance();
}

function handlePasswordInput() {
  const fieldErrors = getClientFieldErrors(collectPayload());

  if (fieldErrors.password) {
    setFieldError('password', fieldErrors.password);
  } else {
    clearFieldError('password');
  }

  if (fieldErrors.confirmPassword) {
    setFieldError('confirmPassword', fieldErrors.confirmPassword);
  } else {
    clearFieldError('confirmPassword');
  }

  updatePasswordGuidance();
  updateSubmitButtonState();
}

function collectPayload() {
  return {
    deviceName: fieldMap.deviceName.value.trim(),
    username: fieldMap.username.value.trim(),
    password: fieldMap.password.value,
    confirmPassword: fieldMap.confirmPassword.value,
  };
}

async function fetchStatus() {
  const response = await fetch('/api/status', { cache: 'no-store' });
  return response.json();
}

async function loadStatus() {
  try {
    const payload = await fetchStatus();
    const configuredHostname = hasConfiguredHostname(payload.hostname);
    const currentHostname = configuredHostname ? payload.hostname : '';

    if (!fieldMap.deviceName.value) {
      fieldMap.deviceName.value = currentHostname;
    }

    if (configuredHostname) {
      hostnameHint.hidden = false;
      hostnameHint.textContent = t('Current system host name: {hostname}. You can keep it or replace it with a deployment-specific name.', { hostname: currentHostname });
    } else {
      hostnameHint.hidden = true;
      hostnameHint.textContent = '';
    }

    showSetupView();
  } catch (error) {
    hostnameHint.hidden = true;
    hostnameHint.textContent = '';
    showSetupView();
  }
}

async function submitOnboarding(event) {
  event.preventDefault();
  clearBanner();
  clearErrors();

  const payload = collectPayload();
  const clientFieldErrors = getClientFieldErrors(payload, { validateConfirmation: true });
  if (Object.keys(clientFieldErrors).length > 0) {
    applyFieldErrors(clientFieldErrors);
    setBanner('error', _('Please correct the highlighted fields.'));
    focusFirstFieldError(clientFieldErrors);
    updateSubmitButtonState();
    return;
  }

  isSubmitting = true;
  updateSubmitButtonState();
  submitButton.textContent = _('Saving...');
  showWaitView(_(WAIT_TITLE));

  try {
    const response = await fetch('/api/complete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const body = await response.json();
    if (!response.ok) {
      if (body.fieldErrors) {
        applyFieldErrors(body.fieldErrors);
      }
      setBanner('error', localizeMessage(body.message) || _('Onboarding failed.'));
      focusFirstFieldError(body.fieldErrors || {});
      return;
    }

    redirectToCockpit(body.redirectUrl || body.cockpitUrl);
  } catch (error) {
    setBanner('error', _('The onboarding service did not respond.'));
  } finally {
    isSubmitting = false;
    updateSubmitButtonState();
    resetSubmitButton();
  }
}

function bootstrap() {
  showSetupView();
  applyTranslations();
  fieldMap.username.addEventListener('input', handleUsernameInput);
  fieldMap.password.addEventListener('input', handlePasswordInput);
  passwordVisibilityButtons.forEach((button) => {
    updatePasswordVisibilityButton(button, false);
    const input = document.getElementById(button.dataset.passwordToggle);
    if (input) {
      input.addEventListener('input', () => syncPasswordVisibilityButton(button));
      input.addEventListener('focus', () => syncPasswordVisibilityButton(button));
    }
    syncPasswordVisibilityButton(button);
    button.addEventListener('click', togglePasswordVisibility);
  });
  updatePasswordGuidance();
  form.addEventListener('submit', submitOnboarding);
  updateSubmitButtonState();
  loadStatus();
}

bootstrap();
