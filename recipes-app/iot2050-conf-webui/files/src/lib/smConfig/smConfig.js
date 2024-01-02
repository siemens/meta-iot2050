export function exportYamlConfig (configData) {
  const yamlConfig = {};
  for (let i = 0; i < configData.config.length; i++) {
    const slotIndex = i + 1;
    const confSlot = configData.config[i];
    switch (confSlot.mlfb) {
      case 'None':
      default:
        yamlConfig['slot' + slotIndex] = {
          description: 'No module for this slot',
          mlfb: 'NA'
        };
        break;
    }
  };
  return yamlConfig;
};

export function importYamlConfig (configData) {
  const uiConfig = {
    version: 1,
    config: [
      { mlfb: 'None' },
      { mlfb: 'None' },
      { mlfb: 'None' },
      { mlfb: 'None' },
      { mlfb: 'None' },
      { mlfb: 'None' }
    ]
  };
  for (let i = 1; i < 7; i++) {
    switch (configData['slot' + i].mlfb) {
      case 'None':
      default:
        break;
    };
  }
  return uiConfig;
};
