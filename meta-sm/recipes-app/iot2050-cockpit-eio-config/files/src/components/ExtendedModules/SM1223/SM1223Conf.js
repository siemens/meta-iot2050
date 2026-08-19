/* eslint-disable react/prop-types */
import * as React from 'react';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import ConfigGroupLabel from '@/components/ConfigEntry/ConfigGroupLabel';
import Paper from '@mui/material/Paper';
import FormGroup from '@mui/material/FormGroup';
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
    keys: [/di\.ch0_3_delay_time/, /di\.ch4_7_delay_time/, /di\.ch8_11_delay_time/, /di\.ch12_15_delay_time/],
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
    keys: [/dq\.ch([0-9]|1[0-5])\.substitute/],
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

export function SM1223ConfDefault (mlfb) {
  const ret = {
    mlfb,
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
      }
    }
  };

  let chTotal = 8;
  if (mlfb === '6ES7223-1PL32-0XB0') {
    ret.di.ch8_11_delay_time = {
      label: uiString.LABEL_DI_INPUT_FILTER_TIME_CH8_11,
      selection: inputFiltersSelection,
      value: uiString.TIME_3
    };
    ret.di.ch12_15_delay_time = {
      label: uiString.LABEL_DI_INPUT_FILTER_TIME_CH12_15,
      selection: inputFiltersSelection,
      value: uiString.TIME_3
    };
    chTotal = 16;
  }

  for (let i = 0; i < chTotal; i++) {
    const chX = 'ch' + i;
    ret.dq[chX] = { substitute: true };
  };

  return ret;
};

export function convertToUIFormat (config) {
  const ret = JSON.parse(JSON.stringify(SM1223ConfDefault(config.mlfb)));
  ret.di.ch0_3_delay_time.value = converter.yamlToUi('di.ch0_3_delay_time', config.di.ch0_3_delay_time);
  ret.di.ch4_7_delay_time.value = converter.yamlToUi('di.ch4_7_delay_time', config.di.ch4_7_delay_time);
  ret.dq.behavior_with_OD.value = converter.yamlToUi('dq.behavior_with_OD', config.dq.behavior_with_OD);

  let chTotal = 8;
  if (config.mlfb === '6ES7223-1PL32-0XB0') {
    ret.di.ch8_11_delay_time.value = converter.yamlToUi('di.ch8_11_delay_time', config.di.ch8_11_delay_time);
    ret.di.ch12_15_delay_time.value = converter.yamlToUi('di.ch12_15_delay_time', config.di.ch12_15_delay_time);
    chTotal = 16;
  }

  for (let i = 0; i < chTotal; i++) {
    const chX = 'ch' + i;
    ret.dq[chX].substitute = converter.yamlToUi(`dq.${chX}.substitute`, config.dq[chX].substitute);
  }

  return ret;
};

export function convertToDeviceFormat (config) {
  const ret = {
    description: 'TBD',
    mlfb: config.mlfb,
    di: {
      ch0_3_delay_time: converter.uiToYaml('di.ch0_3_delay_time', config.di.ch0_3_delay_time.value),
      ch4_7_delay_time: converter.uiToYaml('di.ch4_7_delay_time', config.di.ch4_7_delay_time.value)
    },
    dq: {
      behavior_with_OD: converter.uiToYaml('dq.behavior_with_OD', config.dq.behavior_with_OD.value)
    }
  };

  const chTotal = config.mlfb === '6ES7223-1QH32-0XB0' ? 8 : 16;

  if (chTotal === 8) {
    ret.description = uiString.DESC_MOD_AC_DI8_DQ8RLY;
  } else {
    ret.description = uiString.DESC_MOD_DC_DI16_DQ16RLY;
    ret.di.ch8_11_delay_time = converter.uiToYaml('di.ch8_11_delay_time', config.di.ch8_11_delay_time.value);
    ret.di.ch12_15_delay_time = converter.uiToYaml('di.ch12_15_delay_time', config.di.ch12_15_delay_time.value);
  }

  for (let i = 0; i < chTotal; i++) {
    const chX = 'ch' + i;
    ret.dq[chX] = { substitute: converter.uiToYaml(`dq.${chX}.substitute`, config.dq[chX].substitute) };
  }

  return ret;
};

export default function SM1223Conf ({ slotNum, configData, updateConfig, chTotal }) {
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
        description={chTotal === 8 ? uiString.DESC_MOD_AC_DI8_DQ8RLY : uiString.DESC_MOD_DC_DI16_DQ16RLY}
        artNumber={configData.mlfb === '6ES7223-1QH32-0XB0' ? '6ES7 223-1QH32-0XB0' : '6ES7 223-1PL32-0XB0'}
        fwVersion="NA"
      />

      <Paper elevation={3}>
        <FormControl sx={{ m: 2 }} component="fieldset" variant="standard">
          <ConfigGroupLabel label='Digital Inputs' />
          <FormGroup>
            <Stack
              direction="column"
              justifyContent="flex-start"
              alignItems="stretch"
              spacing={2}
            >

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

              {chTotal === 16 && (<>
                <SelectionConfig
                  id="input-filter-time-ch8-11"
                  data={configData.di.ch8_11_delay_time}
                  updateConfig={updateSlotConfig}
                />
                <SelectionConfig
                  id="input-filter-time-ch12-15"
                  data={configData.di.ch12_15_delay_time}
                  updateConfig={updateSlotConfig}
                />
              </>
              )}
            </Stack>
          </FormGroup>
        </FormControl>
      </Paper>

      <Paper elevation={3}>
        <FormControl sx={{ m: 2 }} component="fieldset" variant="standard">
          <ConfigGroupLabel label='Digital Outputs' />
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
              {range(0, chTotal).map((index) => (
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
      </Paper>

    </Stack>
  );
}
