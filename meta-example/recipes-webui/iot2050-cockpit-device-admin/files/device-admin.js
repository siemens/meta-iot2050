/* global cockpit */
'use strict';

const command = '/usr/sbin/iot2050-device-admin';
const MAX_CERTIFICATE_SIZE = 512 * 1024;
const MAX_PRIVATE_KEY_SIZE = 256 * 1024;

function applyShellStyle (style) {
  const selected = style || window.localStorage.getItem('shell:style') || 'auto';
  const dark = selected === 'dark' ||
    (selected === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches);
  document.documentElement.classList.toggle('pf-v6-theme-dark', dark);
  document.documentElement.dataset.cockpitTheme = dark ? 'dark' : 'light';
  document.documentElement.style.colorScheme = dark ? 'dark' : 'light';
}

function installShellStyleSync () {
  applyShellStyle();
  window.addEventListener('storage', event => {
    if (event.key === 'shell:style') applyShellStyle(event.newValue);
  });
  window.addEventListener('cockpit-style', event => {
    applyShellStyle(event.detail?.style);
  });
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if ((window.localStorage.getItem('shell:style') || 'auto') === 'auto') applyShellStyle();
  });
}

installShellStyleSync();

function adminProcess (args, input) {
  const process = cockpit.spawn([command, ...args], {
    superuser: 'require',
    err: 'message',
  });
  if (input !== undefined) {
    process.input(input);
    process.input(null);
  }
  return process;
}

async function runJson (args, input) {
  const output = await adminProcess(args, input);
  let response;
  try {
    response = JSON.parse(output);
  } catch (error) {
    throw new Error('The system helper returned invalid JSON.');
  }
  if (!response.ok) throw new Error(response.error?.message || 'The system helper rejected the request.');
  return response.data || {};
}

function detail (label, value) {
  const row = document.createElement('div');
  const term = document.createElement('dt');
  const description = document.createElement('dd');
  term.textContent = label;
  description.textContent = value ?? 'Unavailable';
  row.append(term, description);
  return row;
}

function showError (error) {
  const alert = document.getElementById('error');
  alert.textContent = error && error.problem === 'access-denied'
    ? 'You don\'t have permission to access this page. If your account has administrator privileges, switch to Administrative access using the lock menu, authenticate if prompted, and refresh the page.'
    : error.message || String(error);
  alert.classList.remove('hidden');
}

function showMessage (message) {
  const notice = document.getElementById('message');
  notice.textContent = message;
  notice.classList.remove('hidden');
}

function clearMessages () {
  document.getElementById('error').classList.add('hidden');
  document.getElementById('message').classList.add('hidden');
}

function renderCertificate (certificate) {
  const status = document.getElementById('certificate-status');
  const details = document.getElementById('certificate-details');
  if (!certificate.available) {
    status.textContent = 'Unavailable';
    status.className = 'status bad';
    details.replaceChildren(detail('Status', certificate.error || 'Certificate is not installed.'));
    return;
  }

  status.textContent = certificate.valid ? certificate.source : 'Needs attention';
  status.className = `status ${certificate.valid ? 'good' : 'bad'}`;
  const validity = certificate.not_before && certificate.not_after
    ? `${certificate.not_before} – ${certificate.not_after}`
    : 'Unavailable';
  details.replaceChildren(
    detail('Subject', certificate.subject),
    detail('Issuer', certificate.issuer),
    detail('Validity', validity),
    detail('SHA-256 fingerprint', certificate.fingerprint_sha256),
    detail('State', certificate.error || (certificate.valid ? 'Active' : 'Invalid certificate or key'))
  );
}

async function loadStatus () {
  clearMessages();
  document.getElementById('loading').classList.remove('hidden');
  document.getElementById('settings').classList.add('hidden');
  try {
    const data = await runJson(['status']);
    renderCertificate(data.certificate || {});
    document.getElementById('settings').classList.remove('hidden');
  } catch (error) {
    showError(error);
  } finally {
    document.getElementById('loading').classList.add('hidden');
  }
}

function readAsBase64 (file) {
  return file.arrayBuffer().then(buffer => {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    const chunkSize = 0x8000;
    for (let offset = 0; offset < bytes.length; offset += chunkSize) {
      binary += String.fromCharCode(...bytes.subarray(offset, offset + chunkSize));
    }
    return btoa(binary);
  });
}

function setCertificateBusy (busy) {
  document.getElementById('install-certificate').disabled = busy;
  document.getElementById('certificate-file').disabled = busy;
  document.getElementById('private-key-file').disabled = busy;
  document.getElementById('refresh').disabled = busy;
  ['certificate', 'private-key'].forEach(name => {
    const button = document.getElementById(`choose-${name}-file`);
    button.classList.toggle('disabled', busy);
    button.setAttribute('aria-disabled', String(busy));
  });
}

function updateFileName (input) {
  const file = input.files[0];
  document.getElementById(`${input.id}-name`).textContent = file
    ? file.name
    : 'No file selected';
}

async function installCertificate () {
  const certificate = document.getElementById('certificate-file').files[0];
  const privateKey = document.getElementById('private-key-file').files[0];
  if (!certificate || !privateKey) throw new Error('Select both a certificate and a private key.');
  if (certificate.size > MAX_CERTIFICATE_SIZE) throw new Error('The certificate or full chain is larger than 512 KiB.');
  if (privateKey.size > MAX_PRIVATE_KEY_SIZE) throw new Error('The private key is larger than 256 KiB.');
  if (!window.confirm('Install this certificate and reload the HTTPS gateway? The existing certificate will be replaced only if validation and nginx configuration checks succeed.')) return;

  setCertificateBusy(true);
  clearMessages();
  try {
    const [certificateData, privateKeyData] = await Promise.all([
      readAsBase64(certificate),
      readAsBase64(privateKey),
    ]);
    await runJson(['certificate-install'], JSON.stringify({
      certificate: certificateData,
      private_key: privateKeyData,
    }));
    document.getElementById('certificate-file').value = '';
    document.getElementById('private-key-file').value = '';
    updateFileName(document.getElementById('certificate-file'));
    updateFileName(document.getElementById('private-key-file'));
    showMessage('The custom certificate is active and nginx has been reloaded.');
    await loadStatus();
  } finally {
    setCertificateBusy(false);
  }
}

document.getElementById('refresh').addEventListener('click', () => loadStatus().catch(showError));
document.getElementById('certificate-file').addEventListener('change', event => updateFileName(event.target));
document.getElementById('private-key-file').addEventListener('change', event => updateFileName(event.target));
document.getElementById('install-certificate').addEventListener('click', () => installCertificate().catch(showError));
loadStatus().catch(showError);
