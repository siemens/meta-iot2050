/* eslint-disable react/prop-types */
import * as React from 'react';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormControl from '@mui/material/FormControl';
import FormLabel from '@mui/material/FormLabel';
import Checkbox from '@mui/material/Checkbox';
import ModuleInfo from '@/components/ModuleInfo';
import SelectionConfig from '@/components/ConfigEntry/SelectionConfig';
import ConfTextConverter from '@/lib/smConfig/ConfTextConverter';
import uiString from '@/lib/uiString/SM1223.json';
import { range } from 'lodash';

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
  },
  {
    keys: [/dq\.behavior_with_OD/],
    rules: [
      {
        scenario: 'all',
        mapping: [
          { ui: uiString.DISCONN_2, yaml: 2 },
          { ui: uiString.DISCONN_3, yaml: 3 }
        ]
      }
    ]
  },
  {
    keys: [/dq\.ch[0-7]\.substitute/],
    rules: [
      {
        scenario: 'all',
        mapping: [
          { ui: true, yaml: 1 },
          { ui: false, yaml: 0 }
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

export const SM1223ConfDefault = {
  mlfb: '6ES7223-1QH32-0XB0',
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
  },
  dq: {
    behavior_with_OD: {
      label: uiString.LABEL_DQ_LOST_CONNECTION,
      selection: [
        uiString.DISCONN_2,
        uiString.DISCONN_3
      ],
      value: uiString.DISCONN_2
    },
    ch0: { substitute: true },
    ch1: { substitute: true },
    ch2: { substitute: true },
    ch3: { substitute: true },
    ch4: { substitute: true },
    ch5: { substitute: true },
    ch6: { substitute: true },
    ch7: { substitute: true }
  }
};

export function convertToUIFormat (config) {
  const ret = JSON.parse(JSON.stringify(SM1223ConfDefault));
  ret.di.ch0_3_delay_time.value = converter.yamlToUi('di.ch0_3_delay_time', config.di.ch0_3_delay_time);
  ret.di.ch4_7_delay_time.value = converter.yamlToUi('di.ch4_7_delay_time', config.di.ch4_7_delay_time);
  ret.dq.behavior_with_OD.value = converter.yamlToUi('dq.behavior_with_OD', config.dq.behavior_with_OD);
  ret.dq.ch0.substitute = converter.yamlToUi('dq.ch0.substitute', config.dq.ch0.substitute);
  ret.dq.ch1.substitute = converter.yamlToUi('dq.ch1.substitute', config.dq.ch1.substitute);
  ret.dq.ch2.substitute = converter.yamlToUi('dq.ch2.substitute', config.dq.ch2.substitute);
  ret.dq.ch3.substitute = converter.yamlToUi('dq.ch3.substitute', config.dq.ch3.substitute);
  ret.dq.ch4.substitute = converter.yamlToUi('dq.ch4.substitute', config.dq.ch4.substitute);
  ret.dq.ch5.substitute = converter.yamlToUi('dq.ch5.substitute', config.dq.ch5.substitute);
  ret.dq.ch6.substitute = converter.yamlToUi('dq.ch6.substitute', config.dq.ch6.substitute);
  ret.dq.ch7.substitute = converter.yamlToUi('dq.ch7.substitute', config.dq.ch7.substitute);
  return ret;
};

export function convertToDeviceFormat (config) {
  const ret = {
    description: uiString.DESC_MOD,
    mlfb: config.mlfb,
    di: {
      ch0_3_delay_time: converter.uiToYaml('di.ch0_3_delay_time', config.di.ch0_3_delay_time.value),
      ch4_7_delay_time: converter.uiToYaml('di.ch4_7_delay_time', config.di.ch4_7_delay_time.value)
    },
    dq: {
      behavior_with_OD: converter.uiToYaml('dq.behavior_with_OD', config.dq.behavior_with_OD.value),
      ch0: { substitute: converter.uiToYaml('dq.ch0.substitute', config.dq.ch0.substitute) },
      ch1: { substitute: converter.uiToYaml('dq.ch1.substitute', config.dq.ch1.substitute) },
      ch2: { substitute: converter.uiToYaml('dq.ch2.substitute', config.dq.ch2.substitute) },
      ch3: { substitute: converter.uiToYaml('dq.ch3.substitute', config.dq.ch3.substitute) },
      ch4: { substitute: converter.uiToYaml('dq.ch4.substitute', config.dq.ch4.substitute) },
      ch5: { substitute: converter.uiToYaml('dq.ch5.substitute', config.dq.ch5.substitute) },
      ch6: { substitute: converter.uiToYaml('dq.ch6.substitute', config.dq.ch6.substitute) },
      ch7: { substitute: converter.uiToYaml('dq.ch7.substitute', config.dq.ch7.substitute) }
    }
  };
  return ret;
};

export default function SM1223Conf ({ slotNum, configData, updateConfig }) {
  const onChangeBehaviorWithOD = (event, value) => {
    const newConf = configData;
    newConf.dq.behavior_with_OD.value = value;
    updateConfig(slotNum, newConf);
  };

  const onChangeChSubstitute = (event) => {
    const newConf = configData;
    newConf.dq[event.target.name].substitute = event.target.checked;
    updateConfig(slotNum, newConf);
  };

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
        artNumber="6ES7 223-1QH32-0XB0"
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

      <FormControl>
        <FormLabel id="do-discon-config-label">{configData.dq.behavior_with_OD.label}</FormLabel>
        <RadioGroup
          aria-labelledby="do-discon-config-label"
          value={configData.dq.behavior_with_OD.value}
          name="do-discon-config-group"
          onChange={onChangeBehaviorWithOD}
        >
          {configData.dq.behavior_with_OD.selection.map((option) => (
            <FormControlLabel value={option} control={<Radio />} label={option} key={option}/>
          ))}

          <Box sx={{
            display: configData.dq.behavior_with_OD.value === uiString.DISCONN_3 ? 'flex' : 'none',
            flexDirection: 'column',
            ml: 3
          }}
          >
            {range(0, 8).map((index) => (
              <FormControlLabel key={index}
                label={'Channel ' + index}
                control={<Checkbox
                  checked={configData.dq['ch' + index].substitute}
                  onChange={onChangeChSubstitute}
                  id={'checkbox-ch-' + index}
                  name={'ch' + index}
                />}
              />
            ))
            }
          </Box>
        </RadioGroup>
      </FormControl>
    </Stack>
  );
}
