import {
  convertToDeviceFormat as convertToDeviceFmtForSM1223,
  convertToUIFormat as convertToUIFmtForSM1223
} from '@/components/ExtendedModules/SM1223/SM1223Conf';

export function exportYamlConfig (configData) {
  const yamlConfig = {};
  for (let i = 0; i < configData.config.length; i++) {
    const slotIndex = i + 1;
    const confSlot = configData.config[i];
    switch (confSlot.mlfb) {
      case '6ES7223-1QH32-0XB0': // SM1223
        yamlConfig['slot' + slotIndex] = convertToDeviceFmtForSM1223(confSlot);
        break;
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
      case '6ES7223-1QH32-0XB0': // SM1223
        uiConfig.config[i - 1] = convertToUIFmtForSM1223(configData['slot' + i]);
        break;
      case 'None':
      default:
        break;
    };
  }
  return uiConfig;
};
