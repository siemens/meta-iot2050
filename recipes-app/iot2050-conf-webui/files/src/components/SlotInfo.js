/* eslint-disable camelcase */
/* eslint-disable react/prop-types */
import * as React from 'react';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import MenuItem from '@mui/material/MenuItem';
import Typography from '@mui/material/Typography';
import SM1223Conf, { SM1223ConfDefault } from '@/components/ExtendedModules/SM1223/SM1223Conf';
import SM1231_4RTDConf, { SM1231_4RTDConfDefault } from '@/components/ExtendedModules/SM1231_RTD/SM1231_4RTDConf';
import SM1231_8RTDConf, { SM1231_8RTDConfDefault } from '@/components/ExtendedModules/SM1231_RTD/SM1231_8RTDConf';
import SM1231with8AIConf, { SM1231with8AIConfDefault } from '@/components/ExtendedModules/SM1231_8AI/SM1231with8AIConf';
import SMSensDIConf, { SMSensDIConfDefault } from '@/components/ExtendedModules/SMSensDI/SMSensDIConf';
import SM1238EM480VACConf, { SM1238EM480VACConfDefault } from '@/components/ExtendedModules/SM1238_EM480VAC/SM1238EM480VACConf';

function Mod ({ modType, slotNum, config, updateConfig }) {
  switch (modType) {
    case '6ES7223-1QH32-0XB0':
      return <SM1223Conf
        slotNum={slotNum}
        configData={config}
        updateConfig={updateConfig}
      />;
    case '6ES7231-5PD32-0XB0':
      return <SM1231_4RTDConf
        slotNum={slotNum}
        configData={config}
        updateConfig={updateConfig}
      />;
    case '6ES7231-5PF32-0XB0':
      return <SM1231_8RTDConf
        slotNum={slotNum}
        configData={config}
        updateConfig={updateConfig}
      />;
    case '6ES7231-4HF32-0XB0':
      return <SM1231with8AIConf
        slotNum={slotNum}
        configData={config}
        updateConfig={updateConfig}
      />;
    case '6ES7647-0CM00-1AA2':
      return <SMSensDIConf
        slotNum={slotNum}
        configData={config}
        updateConfig={updateConfig}
      />;
    case '6ES7238-5XA32-0XB0':
      return <SM1238EM480VACConf
        slotNum={slotNum}
        configData={config}
        updateConfig={updateConfig}
      />;
    default:
      return <Typography>No module in this slot!!!</Typography>;
  }
}

export default function SlotInfo ({ slotNum, configData, updateSlot }) {
  const onChangeModSelect = (event) => {
    switch (event.target.value) {
      case '6ES7223-1QH32-0XB0':
        updateSlot(slotNum, JSON.parse(JSON.stringify(SM1223ConfDefault)));
        break;
      case '6ES7231-5PD32-0XB0':
        updateSlot(slotNum, JSON.parse(JSON.stringify(SM1231_4RTDConfDefault)));
        break;
      case '6ES7231-5PF32-0XB0':
        updateSlot(slotNum, JSON.parse(JSON.stringify(SM1231_8RTDConfDefault)));
        break;
      case '6ES7231-4HF32-0XB0':
        updateSlot(slotNum, JSON.parse(JSON.stringify(SM1231with8AIConfDefault)));
        break;
      case '6ES7647-0CM00-1AA2':
        updateSlot(slotNum, JSON.parse(JSON.stringify(SMSensDIConfDefault)));
        break;
      case '6ES7238-5XA32-0XB0':
        updateSlot(slotNum, JSON.parse(JSON.stringify(SM1238EM480VACConfDefault)));
        break;
      default:
        updateSlot(slotNum, { mlfb: 'None' });
    }
  };

  const moduleTypes = [
    'None',
    '6ES7223-1QH32-0XB0', // SM1223
    '6ES7231-5PD32-0XB0', // SM1231-4RTD
    '6ES7231-5PF32-0XB0', // SM1231-8RTD
    '6ES7231-4HF32-0XB0', // SM1231-8AI
    '6ES7647-0CM00-1AA2', // SM SENS DI
    '6ES7238-5XA32-0XB0' // SM1238 Energy Meter 480VAC
  ];

  return (
    <Stack
      direction="column"
      justifyContent="flex-start"
      alignItems="stretch"
      spacing={2}
    >

      <TextField
        id="add-new-module-list"
        select
        label="Select a module"
        value={configData.mlfb}
        onChange={onChangeModSelect}
      >
        {moduleTypes.map((option) => (
          <MenuItem key={option} value={option}>
            {option}
          </MenuItem>
        ))}
      </TextField>

      <Mod
        slotNum={slotNum}
        modType={configData.mlfb}
        config={configData}
        updateConfig={updateSlot}
      ></Mod>

    </Stack>
  );
}
