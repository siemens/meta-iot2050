/* eslint-disable react/prop-types */
import * as React from 'react';
import Stack from '@mui/material/Stack';
import Paper from '@mui/material/Paper';
import FormGroup from '@mui/material/FormGroup';
import FormControl from '@mui/material/FormControl';
import ModuleInfo from '@/components/ModuleInfo';
import SelectionConfig from '@/components/ConfigEntry/SelectionConfig';
import CheckConfig from '@/components/ConfigEntry/CheckConfig';
import ConfigGroupLabel from '@/components/ConfigEntry/ConfigGroupLabel';
import ConfTextConverter from '@/lib/smConfig/ConfTextConverter';
import uiString from '@/lib/uiString/SM1231_AI.json';
import { range } from 'lodash';

const yamlUIMapping = [
  {
    keys: [/ch[0-7]\.type/],
    rules: [
      {
        scenario: 'all',
        mapping: [
          { ui: uiString.TYPE_1, yaml: 1 },
          { ui: uiString.TYPE_3, yaml: 3 }
        ]
      }
    ]
  },
  {
    keys: [/ch[0-7]\.range/],
    rules: [
      {
        scenario: 'all',
        mapping: [
          { ui: uiString.RANGE_2, yaml: 2 },
          { ui: uiString.RANGE_3, yaml: 3 },
          { ui: uiString.RANGE_7, yaml: 7 },
          { ui: uiString.RANGE_8, yaml: 8 },
          { ui: uiString.RANGE_9, yaml: 9 }
        ]
      }
    ]
  },
  {
    keys: [/integ_time/],
    rules: [
      {
        scenario: 'all',
        mapping: [
          { ui: uiString.INT_TIME_0, yaml: 0 },
          { ui: uiString.INT_TIME_1, yaml: 1 },
          { ui: uiString.INT_TIME_2, yaml: 2 },
          { ui: uiString.INT_TIME_3, yaml: 3 }
        ]
      }
    ]
  },
  {
    keys: [/ch[0-7]\.smooth/],
    rules: [
      {
        scenario: 'all',
        mapping: [
          { ui: uiString.SMOOTH_0, yaml: 0 },
          { ui: uiString.SMOOTH_1, yaml: 1 },
          { ui: uiString.SMOOTH_2, yaml: 2 },
          { ui: uiString.SMOOTH_3, yaml: 3 }
        ]
      }
    ]
  }
];

const converter = new ConfTextConverter(yamlUIMapping);

const rangeSelectionOfCurrent = [
  uiString.RANGE_2,
  uiString.RANGE_3
];

const rangeSelectionOfVoltage = [
  uiString.RANGE_7,
  uiString.RANGE_8,
  uiString.RANGE_9
];

export const channelConfigDefault = {
  type: {
    label: uiString.LABEL_TYPE,
    selection: [
      uiString.TYPE_1,
      uiString.TYPE_3
    ],
    value: uiString.TYPE_1
  },
  range: {
    label: uiString.LABEL_RANGE_VOL,
    selection: rangeSelectionOfVoltage,
    value: uiString.RANGE_9
  },
  smooth: {
    label: uiString.LABEL_SMOOTH,
    selection: [
      uiString.SMOOTH_0,
      uiString.SMOOTH_1,
      uiString.SMOOTH_2,
      uiString.SMOOTH_3
    ],
    value: uiString.SMOOTH_1
  },
  open_wire_alarm: {
    label: uiString.LABEL_OPEN_WIRE_ALARM,
    value: false
  },
  overflow_alarm: {
    label: uiString.LABEL_OVER_FLOW_ALARM,
    value: true
  },
  underflow_alarm: {
    label: uiString.LABEL_UNDER_FLOW_ALARM,
    value: true
  }
};

export function convertToUIFormat (config) {
  const ret = {
    mlfb: config.mlfb,
    power_alarm: {
      label: uiString.LABEL_POWER_ALARM,
      value: config.power_alarm
    },
    integ_time: {
      label: uiString.LABEL_INT_TIME,
      selection: [
        uiString.INT_TIME_0,
        uiString.INT_TIME_1,
        uiString.INT_TIME_2,
        uiString.INT_TIME_3
      ],
      value: converter.yamlToUi('integ_time', config.integ_time)
    },
    channels: []
  };

  const channelNums = config.mlfb === '6ES7231-4HD32-0XB0' ? 4 : 8;

  for (let i = 0; i < channelNums; i++) {
    ret.channels[i] = JSON.parse(JSON.stringify(channelConfigDefault));
    ret.channels[i].type.value = converter.yamlToUi(`ch${i}.type`, config[`ch${i}`].type);
    ret.channels[i].range.value = converter.yamlToUi(`ch${i}.range`, config[`ch${i}`].range);
    if (ret.channels[i].type.value === uiString.TYPE_1) {
      ret.channels[i].range.selection = rangeSelectionOfVoltage;
      ret.channels[i].range.label = uiString.LABEL_RANGE_VOL;
    } else {
      ret.channels[i].range.selection = rangeSelectionOfCurrent;
      ret.channels[i].range.label = uiString.LABEL_RANGE_CUR;
    }

    ret.channels[i].smooth.value = converter.yamlToUi(`ch${i}.smooth`, config[`ch${i}`].smooth);
    ret.channels[i].open_wire_alarm.value = config[`ch${i}`].open_wire_alarm;
    ret.channels[i].overflow_alarm.value = config[`ch${i}`].overflow_alarm;
    ret.channels[i].underflow_alarm.value = config[`ch${i}`].underflow_alarm;
  }
  return ret;
};

export function convertToDeviceFormat (config) {
  const ret = {
    description: '',
    mlfb: config.mlfb,
    power_alarm: config.power_alarm.value,
    integ_time: converter.uiToYaml('integ_time', config.integ_time.value)
  };

  const channelNums = config.mlfb === '6ES7231-4HD32-0XB0' ? 4 : 8;

  if (channelNums === 4) {
    ret.description = uiString.DESC_MOD_4CH;
  } else {
    ret.description = uiString.DESC_MOD_8CH;
  }

  for (let i = 0; i < channelNums; i++) {
    ret['ch' + i] = {
      type: converter.uiToYaml(`ch${i}.type`, config.channels[i].type.value),
      range: converter.uiToYaml(`ch${i}.range`, config.channels[i].range.value),
      smooth: converter.uiToYaml(`ch${i}.smooth`, config.channels[i].smooth.value),
      open_wire_alarm: config.channels[i].open_wire_alarm.value,
      overflow_alarm: config.channels[i].overflow_alarm.value,
      underflow_alarm: config.channels[i].underflow_alarm.value
    };
  }
  return ret;
};

export default function SM1231AIConf ({ slotNum, configData, updateConfig, chTotal }) {
  const setChannelRange = (event) => {
    const chIndex = parseInt(event.target.name.slice(-1), 10);
    const newType = configData.channels[chIndex].type.value;
    let newRangeSelection;
    let newRangeLabel;
    let newRange;

    if (newType === uiString.TYPE_1) {
      newRangeSelection = rangeSelectionOfVoltage;
      newRangeLabel = uiString.LABEL_RANGE_VOL;
      newRange = uiString.RANGE_9;
    } else {
      newRangeSelection = rangeSelectionOfCurrent;
      newRangeLabel = uiString.LABEL_RANGE_CUR;
      newRange = uiString.RANGE_2;
    }

    configData.channels[chIndex].range.selection = newRangeSelection;
    configData.channels[chIndex].range.label = newRangeLabel;
    configData.channels[chIndex].range.value = newRange;
    /* Set the binding channel */
    configData.channels[chIndex + 1].type.value = newType;
    configData.channels[chIndex + 1].range.selection = newRangeSelection;
    configData.channels[chIndex + 1].range.label = newRangeLabel;
    configData.channels[chIndex + 1].range.value = newRange;
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
        description={chTotal === 4 ? uiString.DESC_MOD_4CH : uiString.DESC_MOD_8CH}
        artNumber={configData.mlfb === '6ES7231-4HD32-0XB0' ? '6ES7 231-4HD32-0XB0' : '6ES7 231-4HF32-0XB0'}
        fwVersion="NA"
      />

      <CheckConfig
        id='power-alarm'
        data={configData.power_alarm}
        updateConfig={updateSlotConfig}
      />

      <SelectionConfig
        id={'intime'}
        data={configData.integ_time}
        updateConfig={updateSlotConfig}
      />

      {range(0, chTotal).map((index) => (
        <Paper elevation={3} key={'ch-' + index}>
          <FormControl sx={{ m: 2 }} component="fieldset" variant="standard">
            <ConfigGroupLabel label={'Channel ' + index} />
            <FormGroup>
              <Stack
                direction="column"
                justifyContent="flex-start"
                alignItems="stretch"
                spacing={2}
              >
                <SelectionConfig
                  id={'type-ch' + index}
                  data={configData.channels[index].type}
                  updateConfig={updateSlotConfig}
                  postChange={setChannelRange}
                  disabled={index % 2 !== 0}
                />

                <SelectionConfig
                  id={'range-ch' + index}
                  data={configData.channels[index].range}
                  updateConfig={updateSlotConfig}
                />

                <SelectionConfig
                  id={'smooth-ch' + index}
                  data={configData.channels[index].smooth}
                  updateConfig={updateSlotConfig}
                />

                <CheckConfig
                  id={'open-wire-alarm-ch' + index}
                  data={configData.channels[index].open_wire_alarm}
                  updateConfig={updateSlotConfig}
                  disabled={!(configData.channels[index].type.value === uiString.TYPE_3 &&
                    configData.channels[index].range.value === uiString.RANGE_3)}
                />

                <CheckConfig
                  id={'overflow-alarm-ch' + index}
                  data={configData.channels[index].overflow_alarm}
                  updateConfig={updateSlotConfig}
                />

                <CheckConfig
                  id={'underflow-alarm-ch' + index}
                  data={configData.channels[index].underflow_alarm}
                  updateConfig={updateSlotConfig}
                  disabled={configData.channels[index].type.value === uiString.TYPE_3 &&
                    configData.channels[index].range.value === uiString.RANGE_3}
                />

              </Stack>
            </FormGroup>
          </FormControl>
        </Paper>
      ))
      }
    </Stack>
  );
}
