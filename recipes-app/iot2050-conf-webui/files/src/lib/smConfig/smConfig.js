import {
  convertToDeviceFormat as convertToDeviceFmtForSM1223,
  convertToUIFormat as convertToUIFmtForSM1223
} from '@/components/ExtendedModules/SM1223/SM1223Conf';
import {
  convertToDeviceFormat as convertToDeviceFmtForSM1231with8AI,
  convertToUIFormat as convertToUIFmtForSM1231with8AI
} from '@/components/ExtendedModules/SM1231_8AI/SM1231with8AIConf';
import {
  convertToDeviceFormat as convertToDeviceFmtForSM1231RTD,
  convertToUIFormat as convertToUIFmtForSM1231RTD
} from '@/components/ExtendedModules/SM1231_RTD/SM1231_RTDConf';
import {
  convertToDeviceFormat as convertToDeviceFmtForSMSensDI,
  convertToUIFormat as convertToUIFmtForSMSensDI
} from '@/components/ExtendedModules/SMSensDI/SMSensDIConf';
import {
  convertToDeviceFormat as convertToDeviceFmtForSM1238,
  convertToUIFormat as convertToUIFmtForSM1238
} from '@/components/ExtendedModules/SM1238_EM480VAC/SM1238EM480VACConf';

export function exportYamlConfig (configData) {
  const yamlConfig = {};
  for (let i = 0; i < configData.config.length; i++) {
    const slotIndex = i + 1;
    const confSlot = configData.config[i];
    switch (confSlot.mlfb) {
      case '6ES7223-1QH32-0XB0': // SM1223
        yamlConfig['slot' + slotIndex] = convertToDeviceFmtForSM1223(confSlot);
        break;
      case '6ES7231-4HF32-0XB0': // SM1231-8AI
        yamlConfig['slot' + slotIndex] = convertToDeviceFmtForSM1231with8AI(confSlot);
        break;
      case '6ES7231-5PD32-0XB0': // SM1231-4RTD
      case '6ES7231-5PF32-0XB0': // SM1231-8RTD
        yamlConfig['slot' + slotIndex] = convertToDeviceFmtForSM1231RTD(confSlot);
        break;
      case '6ES7647-0CM00-1AA2':
        yamlConfig['slot' + slotIndex] = convertToDeviceFmtForSMSensDI(confSlot);
        break;
      case '6ES7238-5XA32-0XB0':
        yamlConfig['slot' + slotIndex] = convertToDeviceFmtForSM1238(confSlot);
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
      case '6ES7231-4HF32-0XB0': // SM1231-8AI
        uiConfig.config[i - 1] = convertToUIFmtForSM1231with8AI(configData['slot' + i]);
        break;
      case '6ES7231-5PD32-0XB0': // SM1231-4RTD
      case '6ES7231-5PF32-0XB0': // SM1231-8RTD
        uiConfig.config[i - 1] = convertToUIFmtForSM1231RTD(configData['slot' + i]);
        break;
      case '6ES7647-0CM00-1AA2':
        uiConfig.config[i - 1] = convertToUIFmtForSMSensDI(configData['slot' + i]);
        break;
      case '6ES7238-5XA32-0XB0':
        uiConfig.config[i - 1] = convertToUIFmtForSM1238(configData['slot' + i]);
        break;
      case 'None':
      default:
        break;
    };
  }
  return uiConfig;
};
