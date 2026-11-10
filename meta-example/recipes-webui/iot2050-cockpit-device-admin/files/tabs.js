// Copyright (c) Siemens AG, 2026
// SPDX-License-Identifier: MIT
'use strict';

const deviceAdminTabs = (() => {
  const tabs = ['certificate', 'node-red'].map(name => document.getElementById(`${name}-tab`));

  function select (tab, focus = false) {
    if (tab.hidden) return;
    for (const candidate of tabs) {
      const selected = candidate === tab;
      candidate.setAttribute('aria-selected', String(selected));
      candidate.tabIndex = selected ? 0 : -1;
      document.getElementById(candidate.getAttribute('aria-controls')).hidden = !selected;
    }
    if (focus) tab.focus();
  }

  for (const tab of tabs) {
    tab.addEventListener('click', () => select(tab));
    tab.addEventListener('keydown', event => {
      const available = tabs.filter(candidate => !candidate.hidden);
      let index = available.indexOf(tab);
      if (event.key === 'ArrowRight') index = (index + 1) % available.length;
      else if (event.key === 'ArrowLeft') index = (index + available.length - 1) % available.length;
      else if (event.key === 'Home') index = 0;
      else if (event.key === 'End') index = available.length - 1;
      else return;
      event.preventDefault();
      select(available[index], true);
    });
  }

  return {
    setNodeRedAvailable (available) {
      const tab = tabs[1];
      const selected = tab.getAttribute('aria-selected') === 'true';
      const focused = tab.contains(document.activeElement) ||
        document.getElementById('node-red-panel').contains(document.activeElement);
      tab.hidden = !available;
      if (!available && selected) select(tabs[0], focused);
    },
  };
})();
