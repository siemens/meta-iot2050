/* eslint-disable react/prop-types */
import * as React from 'react';
import Stack from '@mui/material/Stack';
import ModuleInfo from '@/components/ModuleInfo';
import SelectionConfig from '@/components/ConfigEntry/SelectionConfig';
import ConfTextConverter from '@/lib/smConfig/ConfTextConverter';
import uiString from '@/lib/uiString/SM1221_8DI.json';

const yamlUIMapping = [
  {
    keys: [/di\.ch0_3_delay_time/, /di\.ch4_7_delay_time/],
    rules: [
      {
        scenario: 'all',
        mapping: [
          { ui: uiString.TIME_2, yaml: 2 },
          { ui: uiString.TIME_3, yaml: 3 },
          { ui: uiString.TIME_4, yaml: 4 },
          { ui: uiString.TIME_5, yaml: 5 },
          { ui: uiString.TIME_6, yaml: 6 },
          { ui: uiString.TIME_7, yaml: 7 },
          { ui: uiString.TIME_9, yaml: 9 }
        ]
      }
    ]
  }
];

const converter = new ConfTextConverter(yamlUIMapping);

const inputFiltersSelection = [
  uiString.TIME_2,
  uiString.TIME_3,
  uiString.TIME_4,
  uiString.TIME_5,
  uiString.TIME_6,
  uiString.TIME_7,
  uiString.TIME_9
];

export const SM1221with8DIConfDefault = {
  mlfb: '6ES7221-1BF32-0XB0',
  di: {
    ch0_3_delay_time: {
      label: uiString.LABEL_DI_INPUT_FILTER_TIME_CH0_3,
      selection: inputFiltersSelection,
      value: uiString.TIME_3
    },
    ch4_7_delay_time: {
      label: uiString.LABEL_DI_INPUT_FILTER_TIME_CH4_7,
      selection: inputFiltersSelection,
      value: uiString.TIME_3
    }
  }
};

export function convertToUIFormat (config) {
  const ret = JSON.parse(JSON.stringify(SM1221with8DIConfDefault));
  ret.di.ch0_3_delay_time.value = converter.yamlToUi('di.ch0_3_delay_time', config.di.ch0_3_delay_time);
  ret.di.ch4_7_delay_time.value = converter.yamlToUi('di.ch4_7_delay_time', config.di.ch4_7_delay_time);
  return ret;
};

export function convertToDeviceFormat (config) {
  const ret = {
    description: uiString.DESC_MOD,
    mlfb: config.mlfb,
    di: {
      ch0_3_delay_time: converter.uiToYaml('di.ch0_3_delay_time', config.di.ch0_3_delay_time.value),
      ch4_7_delay_time: converter.uiToYaml('di.ch4_7_delay_time', config.di.ch4_7_delay_time.value)
    }
  };
  return ret;
};

export default function SM1221with8DIConf ({ slotNum, configData, updateConfig }) {
  const updateSlotConfig = () => {
    updateConfig(slotNum, configData);
  };

  return (
    <Stack
      direction="column"
      justifyContent="flex-start"
      alignItems="stretch"
      spacing={2}
    >
      <ModuleInfo
        description={uiString.DESC_MOD}
        artNumber="6ES7 221-1BF32-0XB0"
        fwVersion="NA"
      />

      <SelectionConfig
        id="input-filter-time-ch0-3"
        data={configData.di.ch0_3_delay_time}
        updateConfig={updateSlotConfig}
      />

      <SelectionConfig
        id="input-filter-time-ch4-7"
        data={configData.di.ch4_7_delay_time}
        updateConfig={updateSlotConfig}
      />
    </Stack>
  );
}
