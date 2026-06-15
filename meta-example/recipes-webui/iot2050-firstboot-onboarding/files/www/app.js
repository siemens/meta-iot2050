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
const grantAdminInput = document.getElementById('grant-admin');

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
  'Use at least 8 characters.': 'At least 8 characters',
  'Cockpit did not become ready in time.': 'Timed out while waiting for Cockpit to start.',
};

const fieldMap = {
  fullName: document.getElementById('full-name'),
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
  document.getElementById('full-name-label').textContent = _('Full name');
  document.getElementById('grant-admin-label').textContent = _('Grant administrator privileges');
  document.getElementById('user-name-label').textContent = _('User name');
  document.getElementById('password-label').textContent = _('Password');
  document.getElementById('confirm-password-label').textContent = _('Confirm password');
  waitEyebrow.hidden = true;
  waitEyebrow.textContent = '';
  waitCopy.hidden = true;
  waitCopy.textContent = '';
  waitFootnote.textContent = _(WAIT_FOOTNOTE);
  hostnameHint.hidden = true;
  hostnameHint.textContent = '';

  fieldMap.deviceName.placeholder = 'iot2050-edge-01';
  fieldMap.fullName.placeholder = _('Full name');
  fieldMap.username.placeholder = _('username');
  fieldMap.password.placeholder = _('At least 8 characters');
  fieldMap.confirmPassword.placeholder = _('Repeat the password');

  resetSubmitButton();
}

function resetSubmitButton() {
  submitButton.textContent = _('Save and continue');
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

function getClientFieldErrors(payload) {
  const fieldErrors = {};
  const normalizedUsername = String(payload.username || '').trim().toLowerCase();

  if (RESERVED_USERNAMES.has(normalizedUsername)) {
    fieldErrors.username = 'Create a non-root administrator account.';
  }

  return fieldErrors;
}

function updateSubmitButtonState() {
  submitButton.disabled = isSubmitting || Object.keys(getClientFieldErrors(collectPayload())).length > 0;
}

function handleUsernameInput() {
  const fieldErrors = getClientFieldErrors(collectPayload());

  if (fieldErrors.username) {
    setFieldError('username', fieldErrors.username);
  } else {
    clearFieldError('username');
  }

  updateSubmitButtonState();
}

function collectPayload() {
  return {
    fullName: fieldMap.fullName.value.trim(),
    deviceName: fieldMap.deviceName.value.trim(),
    username: fieldMap.username.value.trim(),
    password: fieldMap.password.value,
    confirmPassword: fieldMap.confirmPassword.value,
    grantAdmin: grantAdminInput.checked,
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
  const clientFieldErrors = getClientFieldErrors(payload);
  if (Object.keys(clientFieldErrors).length > 0) {
    applyFieldErrors(clientFieldErrors);
    setBanner('error', _('Please correct the highlighted fields.'));
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
  form.addEventListener('submit', submitOnboarding);
  updateSubmitButtonState();
  loadStatus();
}

bootstrap();
