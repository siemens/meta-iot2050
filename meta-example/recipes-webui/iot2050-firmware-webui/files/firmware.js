/* global cockpit */
'use strict';

const command = '/usr/sbin/iot2050-fwmgr';
let activeTask = window.sessionStorage.getItem('iot2050FirmwareTask');
let taskRunning = false;

function runManager (args) {
  return cockpit.spawn([command, ...args], { superuser: 'require', err: 'message' })
    .then(output => {
      const response = JSON.parse(output);
      if (!response.ok) throw new Error(response.error.message);
      return response.data;
    });
}

function stageFile (file) {
  const process = cockpit.spawn(
    [command, 'stage', '--name', file.name],
    { superuser: 'require', err: 'message', binary: true }
  );
  const reader = file.stream().getReader();
  const pump = () => reader.read().then(({ done, value }) => {
    if (done) {
      process.input(null);
      return process;
    }
    process.input(value);
    return pump();
  });
  return pump().then(output => {
    const text = typeof output === 'string' ? output : new TextDecoder().decode(output);
    const response = JSON.parse(text);
    if (!response.ok) throw new Error(response.error.message);
    return response.data;
  });
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
  alert.textContent = error.message || String(error);
  alert.classList.remove('hidden');
}

async function inspectController () {
  const data = await runManager(['inspect', 'controller']);
  const details = document.getElementById('controller-details');
  details.replaceChildren(
    detail('Current version', data.current_version),
    detail('Bundled version', data.bundled_version),
    detail('Metadata SHA-1', data.metadata_sha1),
    detail('Actual SHA-256', data.actual_sha256),
    detail('Update needed', data.update_needed ? 'Yes' : 'No')
  );
  const status = document.getElementById('controller-status');
  status.textContent = data.status;
  status.className = `status ${data.integrity === false ? 'bad' : data.update_needed ? 'warn' : 'good'}`;
}

async function inspectModule () {
  const slot = Number(document.getElementById('module-slot').value);
  const data = await runManager(['inspect', 'module', '--payload', JSON.stringify({ slot })]);
  document.getElementById('module-details').replaceChildren(
    detail('Slot', data.slot),
    detail('Slot available', data.available ? 'Yes' : 'No'),
    detail('Chip A node', data.chip_a_node ? 'Available' : 'Unavailable'),
    detail('Chip B node', data.chip_b_node ? 'Available' : 'Unavailable')
  );
}

function setWriteControlsDisabled (disabled) {
  document.getElementById('update-system').disabled = disabled;
  document.getElementById('update-controller').disabled = disabled;
  document.getElementById('update-module').disabled = disabled;
}

async function startSystemUpdate () {
  const file = document.getElementById('system-firmware').files[0];
  if (!file) throw new Error('Select a signed system firmware update package.');
  setWriteControlsDisabled(true);
  try {
    const staged = await stageFile(file);
    // Inspection is intentionally performed by the privileged backend. The
    // browser never decides whether a package is signed or board-compatible.
    const details = await runManager(['inspect', 'system', '--payload', JSON.stringify({ token: staged.token })]);
    document.getElementById('system-details').replaceChildren(
      detail('Target version', details.target_version),
      detail('Firmware image', details.firmware_name),
      detail('Target board', details.target_board),
      detail('Firmware SHA-256', details.firmware_sha256),
      detail('Signature', details.signature_verified ? 'Verified' : 'Not verified')
    );
    const warning = `Install signed System Firmware ${details.target_version || details.firmware_name}?\n\nSHA-256: ${details.firmware_sha256}\n\nThe current firmware will be backed up. Do not power off the device during this operation.`;
    if (!window.confirm(warning)) return;
    const task = await runManager(['start', 'system', '--payload', JSON.stringify({ token: staged.token })]);
    await pollTask(task.id);
  } finally {
    if (!taskRunning) setWriteControlsDisabled(false);
  }
}

async function pollTask (taskId) {
  activeTask = taskId;
  taskRunning = true;
  window.sessionStorage.setItem('iot2050FirmwareTask', taskId);
  document.getElementById('task-panel').classList.remove('hidden');
  setWriteControlsDisabled(true);
  const task = await runManager(['task', taskId]);
  document.getElementById('task-title').textContent = `${task.provider} firmware update`;
  document.getElementById('task-message').textContent = task.error?.message || task.phase;
  const state = document.getElementById('task-state');
  state.textContent = task.state;
  state.className = `status ${task.state === 'succeeded' ? 'good' : task.state === 'failed' ? 'bad' : 'warn'}`;
  if (task.state === 'queued' || task.state === 'running') {
    window.setTimeout(() => pollTask(taskId).catch(showError), 1000);
  } else {
    taskRunning = false;
    window.sessionStorage.removeItem('iot2050FirmwareTask');
    setWriteControlsDisabled(false);
    if (task.result?.reboot_required) {
      document.getElementById('task-message').textContent += ' — Reboot is required to activate the firmware.';
    }
  }
}

async function startControllerUpdate () {
  const details = await runManager(['inspect', 'controller']);
  const warning = `Update the EIO controller from ${details.current_version || 'unknown'} to ${details.bundled_version || 'unknown'}?\n\nSHA-256: ${details.actual_sha256}\n\nDo not power off the device during this operation.`;
  if (!window.confirm(warning)) return;
  const task = await runManager(['start', 'controller', '--payload', JSON.stringify({ source: 'image-default' })]);
  await pollTask(task.id);
}

async function startModuleUpdate () {
  const slot = Number(document.getElementById('module-slot').value);
  const fileA = document.getElementById('firmware-a').files[0];
  const fileB = document.getElementById('firmware-b').files[0];
  if (!fileA && !fileB) throw new Error('Select firmware for chip A or chip B.');
  setWriteControlsDisabled(true);
  try {
    const stagedA = fileA ? await stageFile(fileA) : null;
    const stagedB = fileB ? await stageFile(fileB) : null;
    const lines = [`Update module in slot ${slot}?`];
    if (stagedA) lines.push(`Chip A: ${stagedA.name} (${stagedA.size} bytes)\nSHA-256: ${stagedA.sha256}`);
    if (stagedB) lines.push(`Chip B: ${stagedB.name} (${stagedB.size} bytes)\nSHA-256: ${stagedB.sha256}`);
    lines.push('Do not power off the module during this operation.');
    if (!window.confirm(lines.join('\n\n'))) return;
    const task = await runManager(['start', 'module', '--payload', JSON.stringify({
      slot,
      firmware_a: stagedA?.token,
      firmware_b: stagedB?.token
    })]);
    await pollTask(task.id);
  } finally {
    if (!taskRunning) setWriteControlsDisabled(false);
  }
}

async function loadCapabilities () {
  document.getElementById('error').classList.add('hidden');
  document.getElementById('loading').classList.remove('hidden');
  document.getElementById('providers').classList.add('hidden');
  try {
    const capabilities = await runManager(['capabilities']);
    const names = new Set(capabilities.map(capability => capability.provider));
    document.getElementById('system-card').classList.toggle('hidden', !names.has('system'));
    document.getElementById('controller-card').classList.toggle('hidden', !names.has('controller'));
    document.getElementById('module-card').classList.toggle('hidden', !names.has('module'));
    document.getElementById('providers').classList.remove('hidden');
    if (names.has('controller')) await inspectController();
  } catch (error) {
    showError(error);
  } finally {
    document.getElementById('loading').classList.add('hidden');
  }
}

document.getElementById('refresh').addEventListener('click', loadCapabilities);
document.getElementById('update-system').addEventListener('click', () => startSystemUpdate().catch(showError));
document.getElementById('inspect-module').addEventListener('click', () => inspectModule().catch(showError));
document.getElementById('update-controller').addEventListener('click', () => startControllerUpdate().catch(showError));
document.getElementById('update-module').addEventListener('click', () => startModuleUpdate().catch(showError));
window.addEventListener('beforeunload', event => {
  if (!taskRunning) return;
  event.preventDefault();
  event.returnValue = '';
});
loadCapabilities().then(() => {
  if (activeTask) pollTask(activeTask).catch(error => {
    window.sessionStorage.removeItem('iot2050FirmwareTask');
    showError(error);
  });
});
