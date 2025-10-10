/* eslint-disable camelcase */
/* eslint-disable react/prop-types */
import * as React from 'react';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import MenuItem from '@mui/material/MenuItem';
import Typography from '@mui/material/Typography';
import { SM1223ConfDefault } from '@/components/ExtendedModules/SM1223/SM1223Conf';
import SM1223_AC_DI8_DQ8RLY_Conf from '@/components/ExtendedModules/SM1223/SM1223_AC_DI8_DQ8RLY_Conf';
import SM1231_4RTDConf, { SM1231_4RTDConfDefault } from '@/components/ExtendedModules/SM1231_RTD/SM1231_4RTDConf';
import SM1231_8RTDConf, { SM1231_8RTDConfDefault } from '@/components/ExtendedModules/SM1231_RTD/SM1231_8RTDConf';
import SM1231with8AIConf, { SM1231with8AIConfDefault } from '@/components/ExtendedModules/SM1231_AI/SM1231with8AIConf';
import SMSensDIConf, { SMSensDIConfDefault } from '@/components/ExtendedModules/SMSensDI/SMSensDIConf';
import SM1238EM480VACConf, { SM1238EM480VACConfDefault } from '@/components/ExtendedModules/SM1238_EM480VAC/SM1238EM480VACConf';
import SM1231with4AIConf, { SM1231with4AIConfDefault } from '@/components/ExtendedModules/SM1231_AI/SM1231with4AIConf';
import SM1221with8DIConf, { SM1221with8DIConfDefault } from '@/components/ExtendedModules/SM1221_8DI/SM1221with8DIConf';
import SM1223_DC_DI16_DQ16RLY_Conf from '@/components/ExtendedModules/SM1223/SM1223_DC_DI16_DQ16RLY_Conf';

function Mod ({ modType, slotNum, config, updateConfig }) {
  switch (modType) {
    case '6ES7223-1QH32-0XB0':
      return <SM1223_AC_DI8_DQ8RLY_Conf
        slotNum={slotNum}
        configData={config}
        updateConfig={updateConfig}
      />;
    case '6ES7223-1PL32-0XB0':
      return <SM1223_DC_DI16_DQ16RLY_Conf
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
    case '6ES7231-4HD32-0XB0':
      return <SM1231with4AIConf
        slotNum={slotNum}
        configData={config}
        updateConfig={updateConfig}
      />;
    case '6ES7221-1BF32-0XB0':
      return <SM1221with8DIConf
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
      case '6ES7223-1PL32-0XB0':
        updateSlot(slotNum, JSON.parse(JSON.stringify(SM1223ConfDefault(event.target.value))));
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
      case '6ES7231-4HD32-0XB0':
        updateSlot(slotNum, JSON.parse(JSON.stringify(SM1231with4AIConfDefault)));
        break;
      case '6ES7221-1BF32-0XB0':
        updateSlot(slotNum, JSON.parse(JSON.stringify(SM1221with8DIConfDefault)));
        break;
      default:
        updateSlot(slotNum, { mlfb: 'None' });
    }
  };

  const moduleTypes = [
    'None',
    '6ES7223-1QH32-0XB0', // SM1223-AC-DI8-DQ8
    '6ES7223-1PL32-0XB0', // SM1223-DC-DI16-DQ16
    '6ES7231-5PD32-0XB0', // SM1231-4RTD
    '6ES7231-5PF32-0XB0', // SM1231-8RTD
    '6ES7231-4HF32-0XB0', // SM1231-8AI
    '6ES7238-5XA32-0XB0', // SM1238 Energy Meter 480VAC
    '6ES7647-0CM00-1AA2', // SM SENS DI
    '6ES7231-4HD32-0XB0', // SM1231-4AI
    '6ES7221-1BF32-0XB0' // SM1221-8DI
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
