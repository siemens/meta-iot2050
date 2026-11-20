/* global cockpit, deviceAdminTabs */
// Copyright (c) Siemens AG, 2026
// SPDX-License-Identifier: MIT
'use strict';

const nodeRedName = 'com.siemens.iot2050.NodeRed';
// Always use the original user bridge. Administrative authorization happens
// in Polkit, not by replacing the caller with a root D-Bus connection.
const nodeRedBus = cockpit.dbus(nodeRedName, { bus: 'system', superuser: null });
const nodeRedSuperuser = cockpit.dbus(null, { bus: 'internal' }).proxy('cockpit.Superuser', '/superuser');
let nodeRedStatus = null;
let nodeRedBusy = false;
let nodeRedAccessGeneration = 0;
let nodeRedAccessAllowed = false;
let nodeRedPendingOperation = null;
let nodeRedStatusRequest = null;
let nodeRedRuntimeRequest = null;
let nodeRedPollTimer = null;
const nodeRedTransitions = new Set(['activating', 'deactivating', 'reloading']);

function nodeRedAdministrative () {
  return nodeRedSuperuser.valid && typeof nodeRedSuperuser.Current === 'string' &&
    nodeRedSuperuser.Current !== '' && nodeRedSuperuser.Current !== 'init' && nodeRedSuperuser.Current !== 'none';
}

function nodeRedCurrent (generation) {
  return generation === nodeRedAccessGeneration && nodeRedAdministrative();
}

function nodeRedNeedsPolling () {
  return nodeRedStatus === null || nodeRedTransitions.has(nodeRedStatus.active_state);
}

async function nodeRedCall (request) {
  if (!nodeRedAdministrative()) throw new Error('Administrative access is required.');
  let raw;
  if (request.operation === 'status') {
    [raw] = await nodeRedBus.call('/com/siemens/iot2050/NodeRed', nodeRedName,
      'Call', [JSON.stringify(request)], { type: 's', timeout: 240000 });
  } else {
    // Cockpit's existing administrative bridge performs authorization. The
    // service independently resolves the original connection's actual UID.
    const administrative = cockpit.dbus(nodeRedName, { bus: 'system', superuser: 'require' });
    try {
      [raw] = await administrative.call('/com/siemens/iot2050/NodeRed', nodeRedName,
        'CallFor', [nodeRedStatus.caller_connection, JSON.stringify(request)], { type: 'ss', timeout: 240000 });
    } finally {
      administrative.close();
    }
  }
  const response = JSON.parse(raw);
  if (!response.ok) throw new Error(response.error.message);
  return response.data;
}

function nodeRedSetState (label) {
  const state = document.getElementById('node-red-state');
  const key = label.replace(/…$/, '');
  const colors = {
    Running: 'good', Starting: 'warn', Stopping: 'warn', Reloading: 'warn', Applying: 'warn',
    Failed: 'bad', 'Status unavailable': 'bad', Unknown: 'warn',
  };
  state.textContent = label;
  state.className = `status ${colors[key] || 'neutral'}`;
}

function nodeRedSetMessage (text, kind = '') {
  const message = document.getElementById('node-red-message');
  message.textContent = text;
  message.className = text && kind ? `node-red-feedback ${kind}` : '';
}

function nodeRedServiceLabel (state) {
  const labels = { activating: 'Starting', deactivating: 'Stopping', active: 'Running', inactive: 'Stopped', failed: 'Failed', reloading: 'Reloading' };
  return labels[state] || 'Unknown';
}

function nodeRedRender (status) {
  if (!nodeRedAdministrative()) return;
  const firstStatus = nodeRedStatus === null;
  nodeRedStatus = status;
  const healthError = status.configuration_error || status.account_error || '';
  const transitioning = nodeRedTransitions.has(status.active_state);
  const ready = status.configured && status.account_exists && !healthError;
  const canStop = status.running || ['activating', 'reloading'].includes(status.active_state);
  deviceAdminTabs.setNodeRedAvailable(status.installed);
  document.getElementById('node-red-card').classList.toggle('hidden', !status.installed);
  document.getElementById('node-red-actor').textContent = status.actor;
  nodeRedSetState(nodeRedBusy
    ? ({ start: 'Starting…', stop: 'Stopping…' }[nodeRedPendingOperation] || 'Applying…')
    : status.active_state ? nodeRedServiceLabel(status.active_state) : status.running ? 'Running' : 'Stopped');
  if (!nodeRedBusy || nodeRedPendingOperation !== 'set-autostart') {
    document.getElementById('node-red-autostart').checked = status.autostart;
  }
  document.getElementById('node-red-health-error').textContent = healthError;
  document.getElementById('node-red-health-error').classList.toggle('hidden', !healthError);
  document.getElementById('node-red-autostart').disabled = nodeRedBusy || transitioning || !ready;
  document.getElementById('node-red-password-state').textContent = status.account_error ? 'Unavailable' : status.account_exists ? 'Set' : 'Not set';
  document.getElementById('node-red-password-required').classList.toggle('hidden', ready || !!healthError);
  if (firstStatus) document.getElementById('node-red-credentials').open = !status.account_exists;
  for (const operation of ['start', 'stop', 'save-password']) {
    const button = document.getElementById(`node-red-${operation}`);
    button.disabled = nodeRedBusy || (operation === 'start' && (!ready || transitioning || status.running)) ||
      (operation === 'stop' && !canStop) || (operation === 'save-password' && transitioning);
  }
  document.getElementById('node-red-password').disabled = nodeRedBusy || transitioning;
  document.getElementById('node-red-password-confirm').disabled = nodeRedBusy || transitioning;
  const url = new URL(window.location.href);
  url.protocol = 'https:';
  url.port = '1880';
  url.pathname = status.admin_path;
  url.search = '';
  url.hash = '';
  const link = document.getElementById('node-red-open');
  link.href = url.href;
  link.classList.toggle('hidden', nodeRedBusy || !status.running || !status.gateway);
}

async function nodeRedRefresh () {
  if (!nodeRedAdministrative()) return;
  const generation = nodeRedAccessGeneration;
  if (nodeRedStatusRequest?.generation === generation) return nodeRedStatusRequest.promise;
  const request = { generation };
  nodeRedStatusRequest = request;
  request.promise = (async () => {
    try {
      const status = await nodeRedCall({ operation: 'status' });
      if (nodeRedCurrent(generation)) nodeRedRender(status);
    } catch (error) {
      if (nodeRedCurrent(generation)) nodeRedSetMessage('Unable to read Node-RED status. Refresh to retry.', 'error');
    } finally {
      if (nodeRedStatusRequest === request) nodeRedStatusRequest = null;
      nodeRedSchedulePoll(generation);
    }
  })();
  return request.promise;
}

function nodeRedSchedulePoll (generation) {
  if (!nodeRedCurrent(generation)) return;
  if (!nodeRedNeedsPolling()) {
    window.clearTimeout(nodeRedPollTimer);
    nodeRedPollTimer = null;
    return;
  }
  if (nodeRedPollTimer !== null || nodeRedRuntimeRequest === generation) return;
  nodeRedPollTimer = window.setTimeout(() => {
    nodeRedPollTimer = null;
    nodeRedReadRuntime(generation);
  }, 1000);
}

async function nodeRedOperation (operation) {
  if (!nodeRedAdministrative() || !nodeRedStatus || nodeRedBusy) return;
  if ((operation === 'start' || operation === 'set-autostart') &&
      (!nodeRedStatus.configured || !nodeRedStatus.account_exists)) return;
  const input = document.getElementById('node-red-password');
  const confirm = document.getElementById('node-red-password-confirm');
  const request = { operation };
  nodeRedSetMessage('');
  if (operation === 'save-password') {
    if (input.value !== confirm.value) {
      nodeRedSetMessage('The Node-RED passwords do not match.', 'error');
      return;
    }
    if (!input.value) {
      nodeRedSetMessage('Enter a new access password.', 'error');
      return;
    }
    request.password = input.value;
  }
  if (operation === 'set-autostart') request.autostart = document.getElementById('node-red-autostart').checked;
  const generation = nodeRedAccessGeneration;
  nodeRedBusy = true;
  nodeRedPendingOperation = operation;
  nodeRedRender(nodeRedStatus);
  try {
    const status = await nodeRedCall(request);
    if (generation !== nodeRedAccessGeneration) return;
    nodeRedRender(status);
    nodeRedSetMessage(operation === 'save-password' ? 'Password saved.' : operation === 'set-autostart' ? 'Startup setting saved.' : '', 'success');
    if (operation === 'save-password') document.getElementById('node-red-credentials').open = false;
  } catch (error) {
    if (nodeRedCurrent(generation)) {
      nodeRedSetMessage(error.problem === 'access-denied'
        ? 'Enable Administrative access using the Cockpit lock menu, then retry. Your original login account remains the Node-RED identity.'
        : error.message || String(error), 'error');
    }
  } finally {
    input.value = '';
    confirm.value = '';
    delete request.password;
    nodeRedBusy = false;
    nodeRedPendingOperation = null;
    if (nodeRedStatus) nodeRedRender(nodeRedStatus);
    await nodeRedRefresh();
  }
}

for (const operation of ['start', 'stop']) {
  document.getElementById(`node-red-${operation}`).addEventListener('click', () => nodeRedOperation(operation));
}
document.getElementById('node-red-password-form').addEventListener('submit', event => {
  event.preventDefault();
  nodeRedOperation('save-password');
});
document.getElementById('node-red-autostart').addEventListener('change', () => nodeRedOperation('set-autostart'));
document.getElementById('refresh').addEventListener('click', nodeRedRefresh);

function nodeRedAccessChanged () {
  const allowed = nodeRedAdministrative();
  // Superuser proxy properties can change without an access-mode transition,
  // including when an operation opens or closes an administrative bridge.
  if (allowed === nodeRedAccessAllowed) return;
  nodeRedAccessAllowed = allowed;
  nodeRedAccessGeneration++;
  window.clearTimeout(nodeRedPollTimer);
  nodeRedPollTimer = null;
  nodeRedStatus = null;
  deviceAdminTabs.setNodeRedAvailable(false);
  document.getElementById('node-red-card').classList.add('hidden');
  document.getElementById('node-red-password').value = '';
  document.getElementById('node-red-password-confirm').value = '';
  nodeRedSetMessage('');
  document.getElementById('node-red-health-error').textContent = '';
  document.getElementById('node-red-health-error').classList.add('hidden');
  document.getElementById('node-red-credentials').open = false;
  if (allowed) nodeRedDiscover(nodeRedAccessGeneration);
}

async function nodeRedDiscover (generation) {
  try {
    // The management service serializes long-running start/stop calls. Detect
    // installation independently so a fresh page need not wait for that queue.
    await cockpit.spawn(['/usr/bin/test', '-x', '/usr/bin/node-red'], { superuser: null, err: 'message' });
    if (!nodeRedCurrent(generation)) return;
    deviceAdminTabs.setNodeRedAvailable(true);
    document.getElementById('node-red-card').classList.remove('hidden');
    nodeRedSetState('Checking service…');
    document.getElementById('node-red-actor').textContent = '';
    document.getElementById('node-red-open').classList.add('hidden');
    nodeRedSetMessage('');
    for (const operation of ['start', 'stop', 'save-password']) {
      document.getElementById(`node-red-${operation}`).disabled = true;
    }
    document.getElementById('node-red-autostart').disabled = true;
    document.getElementById('node-red-password').disabled = true;
    document.getElementById('node-red-password-confirm').disabled = true;
    nodeRedReadRuntime(generation);
    await nodeRedRefresh();
  } catch (error) {
    // Images without Node-RED keep its tab hidden.
  }
}

async function nodeRedReadRuntime (generation) {
  if (!nodeRedCurrent(generation) || !nodeRedNeedsPolling() || nodeRedRuntimeRequest === generation) return;
  nodeRedRuntimeRequest = generation;
  try {
    // systemd remains responsive while the management service waits for its
    // start/stop job. Read the actual unit state, never infer it from a reload.
    const output = await cockpit.spawn([
      '/usr/bin/systemctl', 'show', 'node-red.service', '--property=ActiveState', '--value',
    ], { superuser: null, err: 'message' });
    if (!nodeRedCurrent(generation) || !nodeRedNeedsPolling()) return;
    nodeRedSetState(nodeRedServiceLabel(output.trim()));
    if (!nodeRedBusy) nodeRedRefresh();
  } catch (error) {
    if (nodeRedCurrent(generation) && nodeRedNeedsPolling()) nodeRedSetState('Status unavailable');
  } finally {
    if (nodeRedRuntimeRequest === generation) nodeRedRuntimeRequest = null;
    nodeRedSchedulePoll(generation);
  }
}

nodeRedSuperuser.addEventListener('changed', nodeRedAccessChanged);
nodeRedSuperuser.wait(nodeRedAccessChanged);
