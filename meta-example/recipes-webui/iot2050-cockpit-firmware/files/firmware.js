/* global cockpit */
'use strict';

const command = '/usr/sbin/iot2050-fwmgr';
let activeTask = window.sessionStorage.getItem('iot2050FirmwareTask');
let taskRunning = false;
let backendAvailability = {};
let defaultSystemPackage = '';
let deviceIdentity = {};

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
    const style = event.detail && event.detail.style;
    applyShellStyle(style);
  });
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if ((window.localStorage.getItem('shell:style') || 'auto') === 'auto') applyShellStyle();
  });
}

installShellStyleSync();

function runManager (args) {
  return cockpit.spawn([command, ...args], { superuser: 'require', err: 'message' })
    .then(output => {
      const response = JSON.parse(output);
      if (!response.ok) throw new Error(response.error.message);
      return response.data;
    });
}

function stageFile (file) {
  let tmpPath = '';
  const reader = file.stream().getReader();

  const createTempPath = () => cockpit.spawn(
    ['/usr/bin/mktemp', '/tmp/iot2050-fwmgr-upload-XXXXXX'],
    { superuser: 'require', err: 'message' }
  ).then(path => {
    tmpPath = path.trim();
    return tmpPath;
  });

  const uploadTempFile = () => {
    const sink = cockpit.spawn(
      ['/usr/bin/dd', `of=${tmpPath}`, 'status=none'],
      { superuser: 'require', err: 'message', binary: true }
    );
    const pump = () => reader.read().then(({ done, value }) => {
      if (done) {
        sink.input(null);
        return sink;
      }
      sink.input(value);
      return pump();
    });
    return pump();
  };

  const removeTempPath = () => {
    if (!tmpPath) return Promise.resolve();
    return cockpit.spawn(
      ['/usr/bin/rm', '-f', tmpPath],
      { superuser: 'require', err: 'ignore' }
    ).catch(() => {});
  };

  return createTempPath()
    .then(uploadTempFile)
    .then(() => runManager(['stage', tmpPath, '--name', file.name]))
    .finally(removeTempPath);
}

function detail (label, value) {
  const row = document.createElement('div');
  const term = document.createElement('dt');
  const description = document.createElement('dd');
  term.textContent = label;
  description.textContent = value == null ? 'Unavailable' : value;
  row.append(term, description);
  return row;
}

const PHASE_LABELS = {
  'starting': 'Starting',
  'checking-compatibility-and-signature': 'Checking compatibility and signature',
  'preparing-backup': 'Creating rollback backup',
  'flashing-system': 'Flashing system firmware',
  'retrying-flash': 'Flashing failed, retrying',
  'preparing-rollback': 'Preparing rollback',
  'flashing-module': 'Flashing module firmware',
  'flashing-controller': 'Flashing controller firmware',
  'completed': 'Completed',
  'succeeded': 'Completed',
  'failed': 'Failed',
  'interrupted': 'Interrupted',
};

function phaseLabel (phase) {
  if (!phase) return '';
  return PHASE_LABELS[phase] || phase.replace(/-/g, ' ');
}

function setMatchStatus (element, current, expected) {
  const matched = Boolean(current && expected && current === expected);
  element.textContent = matched ? 'Matched' : 'Not Matched';
  element.className = `status ${matched ? 'good' : 'bad'}`;
}

function showError (error) {
  const alert = document.getElementById('error');
  alert.textContent = error && error.problem === 'access-denied'
    ? 'You don\'t have permission to access this page. If your account has administrator privileges, switch to Administrative access using the lock menu, authenticate if prompted, and refresh the page.'
    : error.message || String(error);
  alert.classList.remove('hidden');
}

function clearError () {
  const alert = document.getElementById('error');
  alert.textContent = '';
  alert.classList.add('hidden');
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
  setMatchStatus(
    document.getElementById('controller-status'),
    data.current_version,
    data.bundled_version,
  );
}

function renderDeviceInfo (info) {
  ['name', 'mlfb', 'serial'].forEach(key => {
    if (info[key] !== undefined && info[key] !== null && String(info[key]).trim()) {
      deviceIdentity[key] = info[key];
    }
  });
  document.getElementById('device-details').replaceChildren(
    detail('Name:', deviceIdentity.name),
    detail('MLFB:', deviceIdentity.mlfb),
    detail('SN:', deviceIdentity.serial),
  );
  document.getElementById('device-summary').classList.remove('hidden');
}

function renderSystemInfo (data) {
  const info = data.device_info || {};
  renderDeviceInfo(info);
  document.getElementById('system-details').replaceChildren(
    detail('OS image version', info.os_image_version),
    detail('Firmware version', info.firmware_version),
    detail('Expected version', data.target_version),
    detail('Source', 'Signed update package'),
    detail('Protection', 'Signature, compatibility, backup'),
  );
  setMatchStatus(
    document.querySelector('#system-card .status'),
    info.firmware_version,
    data.target_version,
  );
}

async function inspectSystem () {
  const data = await runManager([
    'inspect', 'system', '--payload', JSON.stringify({
      source: 'image-default',
      device_info: true,
    }),
  ]);
  renderSystemInfo(data);
}

async function inspectModule () {
  const slot = Number(document.getElementById('module-slot').value);
  if (!slot) throw new Error('No EIO module slot is available.');
  const data = await runManager(['inspect', 'module', '--payload', JSON.stringify({ slot })]);
  document.getElementById('module-details').replaceChildren(
    detail('Slot', data.slot),
    detail('Slot available', data.available ? 'Yes' : 'No'),
    detail('Chip A node', data.chip_a_node ? 'Available' : 'Unavailable'),
    detail('Chip B node', data.chip_b_node ? 'Available' : 'Unavailable')
  );
  applyModuleInspection(data);
}

function setModuleFilePickerDisabled (inputId, buttonId, disabled) {
  document.getElementById(inputId).disabled = disabled;
  document.getElementById(buttonId).classList.toggle('disabled', disabled);
  document.getElementById(buttonId).setAttribute('aria-disabled', String(disabled));
}

function updateModuleFileName (inputId, nameId) {
  const file = document.getElementById(inputId).files[0];
  const fileName = file ? `Selected: ${file.name}` : 'No file selected';
  const element = document.getElementById(nameId);
  element.textContent = fileName;
  element.title = fileName;
  element.setAttribute('aria-label', fileName);
  element.classList.toggle('placeholder', !file);
}

function applyModuleInspection (inspection) {
  setModuleFilePickerDisabled('firmware-a', 'choose-firmware-a', !inspection.chip_a_node);
  setModuleFilePickerDisabled('firmware-b', 'choose-firmware-b', !inspection.chip_b_node);
  document.getElementById('update-module').disabled =
    !inspection.chip_a_node && !inspection.chip_b_node;
}

async function scanModuleSlots () {
  const select = document.getElementById('module-slot');
  const slotLabel = document.getElementById('module-slot-label');
  const scan = await runManager(['inspect', 'module', '--payload', JSON.stringify({ scan: true })]);
  const slots = scan.slots.filter(slot => slot.chip_a_node || slot.chip_b_node);
  document.getElementById('module-card').classList.toggle('hidden', !slots.length);
  select.replaceChildren();
  slots.forEach(slot => {
    const option = document.createElement('option');
    option.value = String(slot.slot);
    option.textContent = `Slot ${slot.slot}`;
    select.append(option);
  });
  if (!slots.length) {
    select.append(new Option('No module slots detected', ''));
    setModuleControlsDisabled(true);
    select.hidden = false;
    slotLabel.hidden = true;
    document.getElementById('module-status').textContent = 'Unavailable';
    document.getElementById('module-status').className = 'status bad';
    document.getElementById('module-details').replaceChildren(
      detail('Reason', 'No EIO module slots were detected.'),
    );
    return;
  }
  select.value = String(slots[0].slot);
  if (slots.length === 1) {
    slotLabel.textContent = `Slot ${slots[0].slot}`;
    slotLabel.hidden = false;
    select.hidden = true;
  } else {
    slotLabel.hidden = true;
    select.hidden = false;
  }
  setModuleControlsDisabled(false);
  await inspectModule();
}

function setWriteControlsDisabled (disabled) {
  setSystemUpdateDisabled(disabled);
  document.getElementById('update-controller').disabled = disabled || backendAvailability.controller === false;
  document.getElementById('update-module').disabled = disabled || backendAvailability.module === false;
}

function setSystemUpdateDisabled (disabled) {
  document.getElementById('update-system').disabled = disabled || backendAvailability.system === false;
  document.getElementById('system-firmware').disabled = disabled;
  document.getElementById('choose-system-firmware').classList.toggle('disabled', disabled);
  document.getElementById('choose-system-firmware').setAttribute('aria-disabled', String(disabled));
  document.getElementById('rollback-system').disabled = disabled;
}

function setControllerControlsDisabled (disabled) {
  document.getElementById('update-controller').disabled = disabled;
}

function setModuleControlsDisabled (disabled) {
  document.getElementById('inspect-module').disabled = disabled;
  document.getElementById('module-slot').disabled = disabled;
  setModuleFilePickerDisabled('firmware-a', 'choose-firmware-a', disabled);
  setModuleFilePickerDisabled('firmware-b', 'choose-firmware-b', disabled);
  document.getElementById('update-module').disabled = disabled;
}

function showUnavailable (statusElement, detailsElement, reason) {
  statusElement.textContent = 'Unavailable';
  statusElement.className = 'status bad';
  detailsElement.replaceChildren(detail('Reason', reason || 'Backend is unavailable'));
}

async function updateSystemFileHint () {
  const file = document.getElementById('system-firmware').files[0];
  const fileName = file
    ? `Selected package: ${file.name}`
    : `Default package: ${defaultSystemPackage || 'unavailable'}`;
  const fileNameElement = document.getElementById('system-file-name');
  fileNameElement.textContent = fileName;
  fileNameElement.title = fileName;
  fileNameElement.setAttribute('aria-label', fileName);
  fileNameElement.classList.toggle('placeholder', !file);
  document.getElementById('system-file-hint').textContent = file
    ? 'The selected package will be used for this update.'
    : defaultSystemPackage
      ? 'Leave empty to use the default package.'
      : 'Choose a custom package because no default package is available.';
}

async function inspectRollback () {
  await runManager(['inspect', 'system', '--rollback']);
  document.getElementById('rollback-system').classList.remove('hidden');
}

async function startRollback () {
  if (taskRunning) return;
  clearError();
  setWriteControlsDisabled(true);
  try {
    const details = await runManager(['inspect', 'system', '--rollback']);
    if (!window.confirm(`Rollback System Firmware from the local backup created at ${details.created_at}?\n\nSHA-256: ${details.sha256}\n\nThis restores the firmware saved before the update. Do not power off or reset the device during rollback.`)) return;
    const task = await runManager(['rollback', 'system']);
    await pollTask(task.id);
  } finally {
    if (!taskRunning) setWriteControlsDisabled(false);
  }
}

async function rebootDevice () {
  if (!window.confirm('Reboot the device now? Firmware activation may require this restart.')) return;
  await cockpit.spawn(['/usr/bin/systemctl', 'reboot'], { superuser: 'require', err: 'message' });
}

async function startSystemUpdate () {
  clearError();
  setSystemUpdateDisabled(true);
  let staged = null;
  try {
    const file = document.getElementById('system-firmware').files[0];
    if (file) staged = await stageFile(file);
    const payload = staged ? { token: staged.token } : { source: 'image-default' };
    const preview = await runManager(['inspect', 'system', '--payload', JSON.stringify(payload)]);
    const summary = [
      `Update System Firmware now?`,
      `Firmware: ${preview.firmware_name || 'unknown'}`,
      `Target board: ${preview.target_board || 'unknown'}`,
      `Target version: ${preview.target_version || 'unknown'}`,
      `SHA-256: ${preview.firmware_sha256 || 'unknown'}`,
      `Signature: ${preview.signature_verified ? 'verified' : 'not verified'}`,
      'WARNING: An interrupted firmware update can leave the device unbootable.',
      'The system will create a rollback backup, flash the firmware, and verify readback. Do not power off or reset the device.'
    ].join('\n\n');
    if (!window.confirm(summary)) {
      if (staged) await runManager(['staging-delete', staged.token]).catch(() => {});
      staged = null;
      return;
    }
    const task = await runManager(['start', 'system', '--payload', JSON.stringify(payload)]);
    staged = null;
    setSystemUpdateDisabled(true);
  await pollTask(task.id);
  } catch (error) {
    if (staged) await runManager(['staging-delete', staged.token]).catch(() => {});
    throw error;
  } finally {
    if (!taskRunning) setSystemUpdateDisabled(false);
  }
}

async function pollTask (taskId) {
  activeTask = taskId;
  taskRunning = true;
  window.sessionStorage.setItem('iot2050FirmwareTask', taskId);
  document.getElementById('task-panel').classList.remove('hidden');
  setWriteControlsDisabled(true);
  const task = await runManager(['task', taskId]);
  document.getElementById('task-title').textContent = `${task.backend} firmware update`;
  document.getElementById('task-message').textContent = (task.error && task.error.message) || phaseLabel(task.phase);
  const state = document.getElementById('task-state');
  const safety = document.getElementById('task-safety');
  const rebootButton = document.getElementById('reboot-device');
  rebootButton.classList.add('hidden');
  state.textContent = task.state;
  state.className = `status ${task.state === 'succeeded' ? 'good' : task.state === 'failed' ? 'bad' : 'warn'}`;
  safety.classList.remove('hidden');
  safety.className = `task-safety ${task.state === 'failed' ? 'bad' : task.state === 'succeeded' ? 'good' : 'warn'}`;
  safety.textContent = task.state === 'running'
    ? 'Do not power off or reset the device while firmware is being written. An interrupted update may make the device unbootable.'
    : task.state === 'succeeded'
      ? 'Firmware operation completed. Reboot only when requested by the result.'
      : task.backend === 'controller' || task.backend === 'module'
        ? 'Firmware operation failed. Keep the device powered, reboot manually to reinitialize the external controller, then refresh and inspect before retrying.'
        : 'Firmware operation failed. Keep the device powered and do not retry or reboot until the failure state is reviewed.';
  if (task.state === 'running') {
    await new Promise(resolve => window.setTimeout(resolve, 1000));
    return pollTask(taskId);
  } else {
    taskRunning = false;
    window.sessionStorage.removeItem('iot2050FirmwareTask');
    setWriteControlsDisabled(false);
    setSystemUpdateDisabled(false);
    if (task.state === 'succeeded') {
      clearError();
    }
    if (task.state === 'succeeded' && task.backend === 'system' &&
        task.operation === 'update') {
      // The backup is created during the task. Refresh its capability now so
      // the rollback action becomes available without a page reload.
      await inspectRollback().catch(() => {
        document.getElementById('rollback-system').classList.add('hidden');
      });
    }
    if (task.state === 'failed' && task.backend === 'system' &&
        task.operation === 'update') {
      try {
        await inspectRollback();
        document.getElementById('task-message').textContent += ' A rollback backup is available; use Rollback to restore the previous firmware before rebooting.';
      } catch (error) {
        document.getElementById('task-message').textContent += ' No verified rollback backup is available; keep the device powered and follow the recovery procedure.';
      }
    }
    if (task.result && task.result.reboot_required) {
      document.getElementById('task-message').textContent += ' — Reboot is required to activate the firmware.';
      rebootButton.textContent = 'Reboot now';
      rebootButton.classList.remove('hidden');
    } else if (task.state === 'failed' &&
               (task.backend === 'controller' || task.backend === 'module')) {
      document.getElementById('task-message').textContent += ' Reboot the device manually, then refresh and inspect before retrying.';
      rebootButton.textContent = 'Reboot now';
      rebootButton.classList.remove('hidden');
    }
  }
}

async function startControllerUpdate () {
  clearError();
  const details = await runManager(['inspect', 'controller']);
  const warning = `Update the EIO controller from ${details.current_version || 'unknown'} to ${details.bundled_version || 'unknown'}?\n\nSHA-256: ${details.actual_sha256}\n\nWARNING: An interrupted controller update can leave the device unusable. Do not power off or reset the device during this operation.`;
  if (!window.confirm(warning)) return;
  const task = await runManager(['start', 'controller', '--payload', JSON.stringify({ source: 'image-default' })]);
  await pollTask(task.id);
}

async function startModuleUpdate () {
  clearError();
  const slot = Number(document.getElementById('module-slot').value);
  const fileA = document.getElementById('firmware-a').files[0];
  const fileB = document.getElementById('firmware-b').files[0];
  if (!fileA && !fileB) throw new Error('Select firmware for chip A or chip B.');
  setWriteControlsDisabled(true);
  const stagedTokens = [];
  try {
    const inspection = await runManager(['inspect', 'module', '--payload', JSON.stringify({ slot })]);
    if (!inspection.available || (!inspection.chip_a_node && !inspection.chip_b_node)) {
      throw new Error(`Module slot ${slot} is unavailable or has no writable firmware nodes.`);
    }
    if ((fileA && !inspection.chip_a_node) || (fileB && !inspection.chip_b_node)) {
      throw new Error(`Selected firmware targets an unavailable chip in slot ${slot}.`);
    }
    const stagedA = fileA ? await stageFile(fileA) : null;
    const stagedB = fileB ? await stageFile(fileB) : null;
    if (stagedA) stagedTokens.push(stagedA.token);
    if (stagedB) stagedTokens.push(stagedB.token);
    const lines = [
      `Update module in slot ${slot}?`,
      `Chip A node: ${inspection.chip_a_node ? 'available' : 'unavailable'}`,
      `Chip B node: ${inspection.chip_b_node ? 'available' : 'unavailable'}`
    ];
    if (stagedA) lines.push(`Chip A: ${stagedA.name} (${stagedA.size} bytes)\nSHA-256: ${stagedA.sha256}`);
    if (stagedB) lines.push(`Chip B: ${stagedB.name} (${stagedB.size} bytes)\nSHA-256: ${stagedB.sha256}`);
    lines.push('WARNING: An interrupted module update can leave the device unusable. Do not power off or reset the device during this operation.');
    if (!window.confirm(lines.join('\n\n'))) {
      await Promise.all(stagedTokens.map(token => runManager(['staging-delete', token]).catch(() => {})));
      stagedTokens.length = 0;
      return;
    }
    const task = await runManager(['start', 'module', '--payload', JSON.stringify({
      slot,
      firmware_a: stagedA ? stagedA.token : undefined,
      firmware_b: stagedB ? stagedB.token : undefined
    })]);
    stagedTokens.length = 0;
    await pollTask(task.id);
  } finally {
    await Promise.all(stagedTokens.map(token => runManager(['staging-delete', token]).catch(() => {})));
    if (!taskRunning) setWriteControlsDisabled(false);
  }
}

async function loadCapabilities () {
  document.getElementById('error').classList.add('hidden');
  document.getElementById('loading').classList.remove('hidden');
  document.getElementById('backends').classList.add('hidden');
  try {
    const capabilities = await runManager(['capabilities']);
    const capabilityMap = new Map(capabilities.map(capability => [capability.backend, capability]));
    backendAvailability = Object.fromEntries(
      capabilities.map(capability => [capability.backend, capability.available !== false]),
    );
    const systemCapability = capabilities.find(capability => capability.backend === 'system');
    defaultSystemPackage = systemCapability && systemCapability.default_package
      ? systemCapability.default_package
      : '';
    updateSystemFileHint();
    document.getElementById('system-card').classList.toggle('hidden', !capabilityMap.has('system'));
    document.getElementById('controller-card').classList.toggle('hidden', !capabilityMap.has('controller'));
    document.getElementById('module-card').classList.toggle('hidden', !capabilityMap.has('module'));
    document.getElementById('backends').classList.remove('hidden');
    const controllerCapability = capabilityMap.get('controller');
    if (controllerCapability && controllerCapability.available) {
      setControllerControlsDisabled(false);
      await inspectController();
    } else if (controllerCapability) {
      setControllerControlsDisabled(true);
      showUnavailable(
        document.getElementById('controller-status'),
        document.getElementById('controller-details'),
        controllerCapability.availability_reason,
      );
    }
    const moduleCapability = capabilityMap.get('module');
    if (moduleCapability && moduleCapability.available) {
      document.getElementById('module-status').textContent = 'Available';
      document.getElementById('module-status').className = 'status neutral';
      try {
        await scanModuleSlots();
      } catch (error) {
        document.getElementById('module-card').classList.add('hidden');
        setModuleControlsDisabled(true);
        showUnavailable(
          document.getElementById('module-status'),
          document.getElementById('module-details'),
          error.message,
        );
      }
    } else if (moduleCapability) {
      document.getElementById('module-card').classList.add('hidden');
      setModuleControlsDisabled(true);
      showUnavailable(
        document.getElementById('module-status'),
        document.getElementById('module-details'),
        moduleCapability.availability_reason,
      );
    }
    if (systemCapability && systemCapability.available) {
      await inspectSystem();
      try {
        await inspectRollback();
      } catch (error) {
        document.getElementById('rollback-system').classList.add('hidden');
      }
    }
  } catch (error) {
    showError(error);
  } finally {
    document.getElementById('loading').classList.add('hidden');
  }
}

document.getElementById('refresh').addEventListener('click', loadCapabilities);
document.getElementById('system-firmware').addEventListener('change', updateSystemFileHint);
document.getElementById('firmware-a').addEventListener('change', () => updateModuleFileName('firmware-a', 'firmware-a-name'));
document.getElementById('firmware-b').addEventListener('change', () => updateModuleFileName('firmware-b', 'firmware-b-name'));
document.getElementById('update-system').addEventListener('click', () => startSystemUpdate().catch(showError));
document.getElementById('rollback-system').addEventListener('click', () => startRollback().catch(showError));
document.getElementById('reboot-device').addEventListener('click', () => rebootDevice().catch(showError));
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
