#!/usr/bin/env node
//
// Copyright (c) Siemens AG, 2026
//
// Authors:
//  Li Hua Qian <huaqian.li@siemens.com>
//
// SPDX-License-Identifier: MIT

'use strict';

const fs = require('fs');
const http = require('http');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const STATE_DIR = '/var/lib/iot2050-firstboot-onboarding';
const COMPLETE_MARKER = path.join(STATE_DIR, 'complete');
const STATIC_DIR = '/usr/share/iot2050-firstboot-onboarding';
const APPLY_HELPER = '/usr/lib/iot2050/onboarding/iot2050-firstboot-apply-user.py';
const SERVICE_NAME = 'iot2050-firstboot-onboarding.service';
const GATEWAY_SELECTOR = '/usr/lib/iot2050/web-gateway/iot2050-web-gateway-select-mode';
const LISTEN_HOST = '127.0.0.1';
const LISTEN_PORT = 9080;
const PUBLIC_PORTS = [80, 443];
const MAX_BODY_SIZE = 16 * 1024;
const COCKPIT_WAIT_SECONDS = 60;
const ONBOARDING_SHUTDOWN_GRACE_MS = 3000;
const USERNAME_PATTERN = /^[a-z_][a-z0-9_-]{0,31}$/;
const HOSTNAME_PATTERN = /^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$/;
const RESERVED_USERNAMES = new Set(['root']);

const CONTENT_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.ico': 'image/x-icon',
};

const LOCALE_ALIASES = {
  zh: 'zh-cn',
  'zh-hans': 'zh-cn',
  'zh-hans-cn': 'zh-cn',
  'zh-hans-sg': 'zh-cn',
  'zh-cn': 'zh-cn',
  'zh-sg': 'zh-cn',
  'zh-hant': 'zh-tw',
  'zh-hant-hk': 'zh-tw',
  'zh-hant-tw': 'zh-tw',
  'zh-hk': 'zh-tw',
  'zh-mo': 'zh-tw',
  'zh-tw': 'zh-tw',
};

let server = null;
let isShuttingDown = false;

function jsonResponse(response, statusCode, payload) {
  const body = Buffer.from(JSON.stringify(payload, null, 2), 'utf8');
  response.writeHead(statusCode, {
    'Cache-Control': 'no-store',
    'Content-Length': String(body.length),
    'Content-Type': 'application/json; charset=utf-8',
  });
  response.end(body);
}

function textResponse(response, statusCode, body) {
  const payload = Buffer.from(body, 'utf8');
  response.writeHead(statusCode, {
    'Cache-Control': 'no-store',
    'Content-Length': String(payload.length),
    'Content-Type': 'text/plain; charset=utf-8',
  });
  response.end(payload);
}

function runCommand(argumentsList, options = {}) {
  const result = spawnSync(argumentsList[0], argumentsList.slice(1), {
    encoding: 'utf8',
    input: options.input,
    maxBuffer: 1024 * 1024,
  });

  return {
    status: result.status === null ? 1 : result.status,
    stdout: result.stdout || '',
    stderr: result.stderr || '',
    error: result.error || null,
  };
}

function ensureStateDir() {
  fs.mkdirSync(STATE_DIR, { recursive: true, mode: 0o755 });
}

function writeStateMarker(filePath, payload, timestampKey) {
  const content = {
    [timestampKey]: new Date().toISOString(),
    username: payload.username || '',
    deviceName: payload.deviceName || '',
  };

  fs.writeFileSync(filePath, JSON.stringify(content, null, 2), { mode: 0o600 });
  fs.chmodSync(filePath, 0o600);
}

function markComplete(payload) {
  writeStateMarker(COMPLETE_MARKER, payload, 'completed_at');
}

function extractRequestHost(hostHeader) {
  if (!hostHeader) {
    return os.hostname();
  }

  if (hostHeader.startsWith('[')) {
    const bracketIndex = hostHeader.indexOf(']');
    if (bracketIndex > 0) {
      return hostHeader.slice(0, bracketIndex + 1);
    }
  }

  return hostHeader.split(':', 1)[0];
}

function buildUrl(host, scheme, port, requestPath = '/') {
  const resolvedHost = host || os.hostname();
  const normalizedPath = requestPath || '/';
  const defaultPort = scheme === 'https' ? 443 : 80;

  if (port === defaultPort) {
    return `${scheme}://${resolvedHost}${normalizedPath}`;
  }

  return `${scheme}://${resolvedHost}:${port}${normalizedPath}`;
}

function buildCockpitUrl(host) {
  return buildUrl(host, 'https', 443, '/');
}

function buildWebUiUrl(host) {
  return buildUrl(host, 'https', 443, '/webui');
}

function normalizeLocale(locale) {
  return String(locale || '').trim().toLowerCase().replace(/_/g, '-');
}

function parseAcceptLanguage(headerValue) {
  const candidates = [];

  for (const [index, rawItem] of String(headerValue || '').split(',').entries()) {
    const item = rawItem.trim();
    if (!item) {
      continue;
    }

    const parts = item.split(';').map((part) => part.trim()).filter(Boolean);
    const locale = normalizeLocale(parts[0]);
    if (!locale || locale === '*') {
      continue;
    }

    let quality = 1.0;
    for (const parameter of parts.slice(1)) {
      if (!parameter.startsWith('q=')) {
        continue;
      }
      const parsedQuality = Number(parameter.slice(2));
      quality = Number.isFinite(parsedQuality) ? parsedQuality : 0.0;
      break;
    }

    if (quality <= 0.0) {
      continue;
    }

    candidates.push({ locale, quality, index });
  }

  candidates.sort((left, right) => {
    if (right.quality !== left.quality) {
      return right.quality - left.quality;
    }
    return left.index - right.index;
  });

  const locales = [];
  for (const candidate of candidates) {
    locales.push(candidate.locale);
    if (LOCALE_ALIASES[candidate.locale]) {
      locales.push(LOCALE_ALIASES[candidate.locale]);
    }

    if (candidate.locale.includes('-')) {
      const primaryLanguage = candidate.locale.split('-', 1)[0];
      locales.push(primaryLanguage);
      if (LOCALE_ALIASES[primaryLanguage]) {
        locales.push(LOCALE_ALIASES[primaryLanguage]);
      }
    }
  }

  locales.push('en');
  return [...new Set(locales)];
}

function getTranslationAssets() {
  const translations = new Map();
  for (const entry of fs.readdirSync(STATIC_DIR, { withFileTypes: true })) {
    if (!entry.isFile() || !entry.name.startsWith('po.') || !entry.name.endsWith('.js')) {
      continue;
    }

    const locale = normalizeLocale(entry.name.slice(3, -3));
    translations.set(locale, path.join(STATIC_DIR, entry.name));
  }
  return translations;
}

function resolveTranslationAsset(headerValue) {
  const translations = getTranslationAssets();
  if (translations.size === 0) {
    return null;
  }

  for (const locale of parseAcceptLanguage(headerValue)) {
    if (translations.has(locale)) {
      return translations.get(locale);
    }
  }

  return translations.get('en') || Array.from(translations.values())[0];
}

function validatePayload(payload) {
  const errors = {};
  const fullName = String(payload.fullName || '').trim();
  const username = String(payload.username || '').trim();
  const password = String(payload.password || '');
  const confirmPassword = String(payload.confirmPassword || '');
  const deviceName = String(payload.deviceName || '').trim();

  if (!username) {
    errors.username = 'Choose a user name.';
  } else if (RESERVED_USERNAMES.has(username)) {
    errors.username = 'Create a non-root administrator account.';
  } else if (!USERNAME_PATTERN.test(username)) {
    errors.username = 'Use a Linux-compatible user name starting with a lowercase letter or underscore.';
  }

  if (!password) {
    errors.password = 'Choose a password.';
  } else if (password.length < 8) {
    errors.password = 'Use at least 8 characters.';
  }

  if (confirmPassword !== password) {
    errors.confirmPassword = 'Passwords do not match.';
  }

  if (fullName && fullName.length > 64) {
    errors.fullName = 'Keep the full name under 64 characters.';
  }

  if (deviceName && (deviceName.length > 63 || !HOSTNAME_PATTERN.test(deviceName))) {
    errors.deviceName = 'Use letters, digits, or hyphens for the device name.';
  }

  return errors;
}

function applyOnboarding(payload) {
  if (!fs.existsSync(APPLY_HELPER)) {
    return {
      status: 'error',
      message: 'Onboarding apply helper is missing.',
    };
  }

  const helperPayload = {
    fullName: payload.fullName || '',
    username: payload.username || '',
    password: payload.password || '',
    confirmPassword: payload.confirmPassword || '',
    deviceName: payload.deviceName || '',
    grantAdmin: payload.grantAdmin !== false,
  };

  const result = runCommand([APPLY_HELPER], {
    input: JSON.stringify(helperPayload),
  });

  if (result.error) {
    return {
      status: 'error',
      message: result.error.message,
    };
  }

  if (result.status !== 0) {
    return {
      status: 'error',
      message: result.stderr.trim() || result.stdout.trim() || 'The onboarding helper failed.',
    };
  }

  if (!result.stdout.trim()) {
    return {
      status: 'ok',
      message: 'Onboarding helper completed successfully.',
    };
  }

  try {
    const helperResponse = JSON.parse(result.stdout);
    if (helperResponse && typeof helperResponse === 'object') {
      return helperResponse;
    }
  } catch (error) {
    return {
      status: 'error',
      message: 'The onboarding helper returned invalid JSON.',
    };
  }

  return {
    status: 'error',
    message: 'The onboarding helper returned an unexpected response.',
  };
}

function selectGatewayMode(mode) {
  if (!fs.existsSync(GATEWAY_SELECTOR)) {
    return {
      ok: false,
      message: 'The nginx gateway selector is missing.',
    };
  }

  const result = runCommand([GATEWAY_SELECTOR, mode]);
  if (result.error) {
    return {
      ok: false,
      message: result.error.message,
    };
  }

  if (result.status !== 0) {
    return {
      ok: false,
      message: result.stderr.trim() || result.stdout.trim() || `Failed to switch nginx to ${mode} mode.`,
    };
  }

  return { ok: true };
}

function delay(milliseconds) {
  return new Promise((resolve) => {
    setTimeout(resolve, milliseconds);
  });
}

function probeCockpitReady() {
  return new Promise((resolve) => {
    const request = http.request({
      host: '127.0.0.1',
      port: 9090,
      path: '/cockpit/login',
      method: 'GET',
      headers: {
        Accept: 'application/json',
        Host: 'localhost',
      },
    }, (response) => {
      response.resume();
      response.on('end', () => {
        resolve(response.statusCode === 200 || response.statusCode === 401);
      });
    });

    request.setTimeout(2000, () => {
      request.destroy(new Error('timeout'));
    });

    request.on('error', () => resolve(false));
    request.end();
  });
}

async function waitForCockpitReady(timeoutSeconds = COCKPIT_WAIT_SECONDS) {
  const deadline = Date.now() + timeoutSeconds * 1000;

  while (Date.now() < deadline) {
    const socketState = runCommand(['systemctl', 'is-active', 'cockpit.socket']);
    if (socketState.status === 0 && await probeCockpitReady()) {
      return {
        ready: true,
        message: 'Cockpit is ready.',
      };
    }

    await delay(1000);
  }

  return {
    ready: false,
    message: 'Cockpit did not become ready in time.',
  };
}

async function switchToRuntime(payload) {
  runCommand(['systemctl', 'enable', 'cockpit.socket']);
  runCommand(['systemctl', 'start', 'cockpit.socket']);
  runCommand(['systemctl', 'start', 'cockpit.service']);

  await delay(3000);

  const cockpitStatus = await waitForCockpitReady();
  if (!cockpitStatus.ready) {
    return {
      ok: false,
      message: cockpitStatus.message,
    };
  }

  const runtimeSwitch = selectGatewayMode('runtime');
  if (!runtimeSwitch.ok) {
    return {
      ok: false,
      message: runtimeSwitch.message,
    };
  }

  markComplete(payload);
  runCommand(['systemctl', 'disable', SERVICE_NAME]);
  return {
    ok: true,
    message: cockpitStatus.message,
  };
}

function scheduleShutdownAfterResponse(response) {
  response.once('finish', () => {
    setTimeout(() => {
      shutdownServers();
    }, ONBOARDING_SHUTDOWN_GRACE_MS).unref();
  });
}

function serveFile(response, filePath, contentType) {
  try {
    const stat = fs.statSync(filePath);
    response.writeHead(200, {
      'Cache-Control': 'no-store',
      'Content-Length': String(stat.size),
      'Content-Type': contentType,
    });
    fs.createReadStream(filePath).pipe(response);
  } catch (error) {
    jsonResponse(response, 404, { message: 'Static asset not found.' });
  }
}

async function readRequestBody(request) {
  return await new Promise((resolve, reject) => {
    const chunks = [];
    let size = 0;

    request.on('data', (chunk) => {
      size += chunk.length;
      if (size > MAX_BODY_SIZE) {
        reject(new Error('Invalid request size.'));
        request.destroy();
        return;
      }
      chunks.push(chunk);
    });

    request.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
    request.on('error', reject);
  });
}

async function handleGet(request, response, parsedUrl) {
  if (parsedUrl.pathname === '/healthz') {
    textResponse(response, 200, 'ok\n');
    return;
  }

  if (parsedUrl.pathname === '/api/status') {
    const requestHost = extractRequestHost(request.headers.host || '');
    jsonResponse(response, 200, {
      hostname: os.hostname(),
      ports: PUBLIC_PORTS,
      activePort: 443,
      httpEntryUrl: buildUrl(requestHost, 'http', 80),
      httpsEntryUrl: buildUrl(requestHost, 'https', 443),
      compatUrl: buildCockpitUrl(requestHost),
      cockpitUrl: buildCockpitUrl(requestHost),
      webUiUrl: buildWebUiUrl(requestHost),
    });
    return;
  }

  if (parsedUrl.pathname === '/' || parsedUrl.pathname === '/index.html') {
    serveFile(response, path.join(STATIC_DIR, 'index.html'), CONTENT_TYPES['.html']);
    return;
  }

  if (parsedUrl.pathname === '/po.js') {
    const asset = resolveTranslationAsset(request.headers['accept-language'] || '');
    if (!asset) {
      jsonResponse(response, 404, { message: 'Static asset not found.' });
      return;
    }

    serveFile(response, asset, 'application/javascript; charset=utf-8');
    return;
  }

  if (parsedUrl.pathname.startsWith('/po.') && parsedUrl.pathname.endsWith('.js')) {
    serveFile(response, path.join(STATIC_DIR, parsedUrl.pathname.slice(1)), 'application/javascript; charset=utf-8');
    return;
  }

  const filePath = path.join(STATIC_DIR, parsedUrl.pathname.slice(1));
  const extension = path.extname(filePath);
  if (CONTENT_TYPES[extension]) {
    serveFile(response, filePath, CONTENT_TYPES[extension]);
    return;
  }

  jsonResponse(response, 404, { message: 'Not found.' });
}

async function handlePost(request, response, parsedUrl) {
  if (parsedUrl.pathname !== '/api/complete') {
    jsonResponse(response, 404, { message: 'Not found.' });
    return;
  }

  const contentLength = Number(request.headers['content-length'] || '0');
  if (!Number.isFinite(contentLength) || contentLength <= 0 || contentLength > MAX_BODY_SIZE) {
    jsonResponse(response, 400, { message: 'Invalid request size.' });
    return;
  }

  let rawPayload;
  try {
    rawPayload = await readRequestBody(request);
  } catch (error) {
    jsonResponse(response, 400, { message: error.message || 'Invalid request size.' });
    return;
  }

  let payload;
  try {
    payload = JSON.parse(rawPayload);
  } catch (error) {
    jsonResponse(response, 400, { message: 'Invalid JSON payload.' });
    return;
  }

  const fieldErrors = validatePayload(payload);
  if (Object.keys(fieldErrors).length > 0) {
    jsonResponse(response, 422, {
      message: 'Please correct the highlighted fields.',
      fieldErrors,
    });
    return;
  }

  const helperResponse = applyOnboarding(payload);
  if (helperResponse.status !== 'ok') {
    jsonResponse(response, helperResponse.fieldErrors ? 422 : 500, {
      message: helperResponse.message || 'The onboarding helper rejected the request.',
      fieldErrors: helperResponse.fieldErrors || {},
    });
    return;
  }

  const completedPayload = {
    ...payload,
    username: helperResponse.username || payload.username,
    deviceName: helperResponse.deviceName || payload.deviceName,
  };

  const runtimeTransition = await switchToRuntime(completedPayload);
  if (!runtimeTransition.ok) {
    jsonResponse(response, 500, {
      message: runtimeTransition.message || 'The system could not make the Cockpit login page available automatically.',
    });
    return;
  }

  const requestHost = extractRequestHost(request.headers.host || '');
  scheduleShutdownAfterResponse(response);
  jsonResponse(response, 200, {
    message: runtimeTransition.message || helperResponse.message || 'Onboarding helper completed successfully.',
    redirectUrl: buildCockpitUrl(requestHost),
    adminGroups: helperResponse.adminGroups || [],
  });
}

async function requestHandler(request, response) {
  const parsedUrl = new URL(request.url, 'http://127.0.0.1');

  try {
    if (request.method === 'GET') {
      await handleGet(request, response, parsedUrl);
      return;
    }

    if (request.method === 'POST') {
      await handlePost(request, response, parsedUrl);
      return;
    }

    jsonResponse(response, 405, { message: 'Method not allowed.' });
  } catch (error) {
    console.error(error);
    if (!response.headersSent) {
      jsonResponse(response, 500, { message: 'Internal server error.' });
    } else {
      response.destroy();
    }
  }
}

function shutdownServers() {
  if (isShuttingDown) {
    return;
  }

  isShuttingDown = true;
  if (!server) {
    process.exit(0);
    return;
  }

  server.close(() => process.exit(0));
  setTimeout(() => process.exit(0), 1000).unref();
}

function main() {
  ensureStateDir();

  process.on('SIGINT', shutdownServers);
  process.on('SIGTERM', shutdownServers);

  server = http.createServer((request, response) => {
    void requestHandler(request, response);
  });

  server.listen(LISTEN_PORT, LISTEN_HOST, () => {
    console.log(`IOT2050 onboarding listening on ${LISTEN_HOST}:${LISTEN_PORT}`);
  });
}

main();
