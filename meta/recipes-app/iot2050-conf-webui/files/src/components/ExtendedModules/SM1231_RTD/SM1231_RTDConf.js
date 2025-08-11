/* eslint-disable camelcase */
/* eslint-disable lines-between-class-members */
/* eslint-disable react/prop-types */
import * as React from 'react';
import Stack from '@mui/material/Stack';
import FormControl from '@mui/material/FormControl';
import FormGroup from '@mui/material/FormGroup';
import Paper from '@mui/material/Paper';
import ModuleInfo from '@/components/ModuleInfo';
import SelectionConfig from '@/components/ConfigEntry/SelectionConfig';
import CheckConfig from '@/components/ConfigEntry/CheckConfig';
import ConfigGroupLabel from '@/components/ConfigEntry/ConfigGroupLabel';
import ConfTextConverter from '@/lib/smConfig/ConfTextConverter';
import uiString from '@/lib/uiString/SM1231_RTD.json';
import { range } from 'lodash';

const yamlUIMapping = [
  {
    keys: [/ch[0-7]\.type/],
    rules: [
      {
        scenario: 'all',
        mapping: [
          { ui: uiString.TYPE_0, yaml: 0 },
          { ui: uiString.TYPE_4, yaml: 4 },
          { ui: uiString.TYPE_5, yaml: 5 },
          { ui: uiString.TYPE_6, yaml: 6 },
          { ui: uiString.TYPE_7, yaml: 7 },
          { ui: uiString.TYPE_8, yaml: 8 },
          { ui: uiString.TYPE_9, yaml: 9 }
        ]
      }
    ]
  },
  {
    keys: [/ch[0-7]\.range/],
    rules: [
      {
        scenario: 'resistance',
        mapping: [
          { ui: uiString.Resistance_RANGE_1, yaml: 1 },
          { ui: uiString.Resistance_RANGE_2, yaml: 2 },
          { ui: uiString.Resistance_RANGE_3, yaml: 3 }
        ]
      },
      {
        scenario: 'thermal',
        mapping: [
          { ui: uiString.Thermal_RANGE_0, yaml: 0 },
          { ui: uiString.Thermal_RANGE_2, yaml: 2 },
          { ui: uiString.Thermal_RANGE_3, yaml: 3 },
          { ui: uiString.Thermal_RANGE_4, yaml: 4 },
          { ui: uiString.Thermal_RANGE_5, yaml: 5 },
          { ui: uiString.Thermal_RANGE_6, yaml: 6 },
          { ui: uiString.Thermal_RANGE_11, yaml: 11 },
          { ui: uiString.Thermal_RANGE_12, yaml: 12 },
          { ui: uiString.Thermal_RANGE_15, yaml: 15 },
          { ui: uiString.Thermal_RANGE_16, yaml: 16 },
          { ui: uiString.Thermal_RANGE_18, yaml: 18 },
          { ui: uiString.Thermal_RANGE_20, yaml: 20 },
          { ui: uiString.Thermal_RANGE_22, yaml: 22 },
          { ui: uiString.Thermal_RANGE_24, yaml: 24 },
          { ui: uiString.Thermal_RANGE_26, yaml: 26 },
          { ui: uiString.Thermal_RANGE_28, yaml: 28 }
        ]
      },
      {
        scenario: 'deactivated',
        mapping: [
          { ui: uiString.Resistance_RANGE_1, yaml: 1 },
          { ui: uiString.Resistance_RANGE_2, yaml: 2 },
          { ui: uiString.Resistance_RANGE_3, yaml: 3 },
          { ui: uiString.Thermal_RANGE_0, yaml: 0 },
          { ui: uiString.Thermal_RANGE_2, yaml: 2 },
          { ui: uiString.Thermal_RANGE_3, yaml: 3 },
          { ui: uiString.Thermal_RANGE_4, yaml: 4 },
          { ui: uiString.Thermal_RANGE_5, yaml: 5 },
          { ui: uiString.Thermal_RANGE_6, yaml: 6 },
          { ui: uiString.Thermal_RANGE_11, yaml: 11 },
          { ui: uiString.Thermal_RANGE_12, yaml: 12 },
          { ui: uiString.Thermal_RANGE_15, yaml: 15 },
          { ui: uiString.Thermal_RANGE_16, yaml: 16 },
          { ui: uiString.Thermal_RANGE_18, yaml: 18 },
          { ui: uiString.Thermal_RANGE_20, yaml: 20 },
          { ui: uiString.Thermal_RANGE_22, yaml: 22 },
          { ui: uiString.Thermal_RANGE_24, yaml: 24 },
          { ui: uiString.Thermal_RANGE_26, yaml: 26 },
          { ui: uiString.Thermal_RANGE_28, yaml: 28 }
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
  },
  {
    keys: [/ch[0-7]\.temper_coeff/],
    rules: [
      {
        scenario: 'all',
        mapping: [
          { ui: uiString.TEMP_COEFF_0, yaml: 0 },
          { ui: uiString.TEMP_COEFF_1, yaml: 1 },
          { ui: uiString.TEMP_COEFF_2, yaml: 2 },
          { ui: uiString.TEMP_COEFF_3, yaml: 3 },
          { ui: uiString.TEMP_COEFF_5, yaml: 5 },
          { ui: uiString.TEMP_COEFF_7, yaml: 7 },
          { ui: uiString.TEMP_COEFF_8, yaml: 8 },
          { ui: uiString.TEMP_COEFF_9, yaml: 9 },
          { ui: uiString.TEMP_COEFF_10, yaml: 10 },
          { ui: uiString.TEMP_COEFF_11, yaml: 11 },
          { ui: uiString.TEMP_COEFF_12, yaml: 12 },
          { ui: uiString.TEMP_COEFF_13, yaml: 13 }
        ]
      }
    ]
  },
  {
    keys: [/ch[0-7]\.temper_unit/],
    rules: [
      {
        scenario: 'all',
        mapping: [
          { ui: uiString.TEMP_UNIT_0, yaml: 0 },
          { ui: uiString.TEMP_UNIT_1, yaml: 1 }
        ]
      }
    ]
  }
];

const converter = new ConfTextConverter(yamlUIMapping);

const typeSelectionOfResistance = [
  uiString.TYPE_4,
  uiString.TYPE_5,
  uiString.TYPE_6
];
const typeSelectionOfThermal = [
  uiString.TYPE_7,
  uiString.TYPE_8,
  uiString.TYPE_9
];

const rangeSelectionOfResistance = [
  uiString.Resistance_RANGE_1,
  uiString.Resistance_RANGE_2,
  uiString.Resistance_RANGE_3
];

const rangeSelectionOfThermal = [
  uiString.Thermal_RANGE_0,
  uiString.Thermal_RANGE_2,
  uiString.Thermal_RANGE_3,
  uiString.Thermal_RANGE_4,
  uiString.Thermal_RANGE_5,
  uiString.Thermal_RANGE_6,
  uiString.Thermal_RANGE_11,
  uiString.Thermal_RANGE_12,
  uiString.Thermal_RANGE_15,
  uiString.Thermal_RANGE_16,
  uiString.Thermal_RANGE_18,
  uiString.Thermal_RANGE_20,
  uiString.Thermal_RANGE_22,
  uiString.Thermal_RANGE_24,
  uiString.Thermal_RANGE_26,
  uiString.Thermal_RANGE_28
];

function decideTempCoeffSelection (range) {
  let selection;
  let defaultValue;

  switch (range) {
    case uiString.Thermal_RANGE_0:
      selection = [uiString.TEMP_COEFF_0];
      defaultValue = uiString.TEMP_COEFF_0;
      break;
    case uiString.Thermal_RANGE_2:
    case uiString.Thermal_RANGE_4:
      selection = [
        uiString.TEMP_COEFF_0,
        uiString.TEMP_COEFF_1,
        uiString.TEMP_COEFF_2,
        uiString.TEMP_COEFF_3,
        uiString.TEMP_COEFF_5
      ];
      defaultValue = uiString.TEMP_COEFF_0;
      break;
    case uiString.Thermal_RANGE_3:
      selection = [
        uiString.TEMP_COEFF_7,
        uiString.TEMP_COEFF_8,
        uiString.TEMP_COEFF_9
      ];
      defaultValue = uiString.TEMP_COEFF_9;
      break;
    case uiString.Thermal_RANGE_5:
    case uiString.Thermal_RANGE_11:
      selection = [
        uiString.TEMP_COEFF_0,
        uiString.TEMP_COEFF_1,
        uiString.TEMP_COEFF_2,
        uiString.TEMP_COEFF_3
      ];
      defaultValue = uiString.TEMP_COEFF_0;
      break;
    case uiString.Thermal_RANGE_6:
    case uiString.Thermal_RANGE_12:
    case uiString.Thermal_RANGE_16:
    case uiString.Thermal_RANGE_18:
      selection = [
        uiString.TEMP_COEFF_8,
        uiString.TEMP_COEFF_9
      ];
      defaultValue = uiString.TEMP_COEFF_9;
      break;
    case uiString.Thermal_RANGE_15:
      selection = [
        uiString.TEMP_COEFF_11,
        uiString.TEMP_COEFF_12,
        uiString.TEMP_COEFF_13
      ];
      defaultValue = uiString.TEMP_COEFF_12;
      break;
    case uiString.Thermal_RANGE_20:
    case uiString.Thermal_RANGE_22:
      selection = [
        uiString.TEMP_COEFF_0,
        uiString.TEMP_COEFF_5
      ];
      defaultValue = uiString.TEMP_COEFF_5;
      break;
    case uiString.Thermal_RANGE_24:
    case uiString.Thermal_RANGE_26:
      selection = [
        uiString.TEMP_COEFF_11,
        uiString.TEMP_COEFF_13
      ];
      defaultValue = uiString.TEMP_COEFF_11;
      break;

    case uiString.Thermal_RANGE_28:
      selection = [uiString.TEMP_COEFF_10];
      defaultValue = uiString.TEMP_COEFF_10;
      break;
  }

  return { selection, defaultValue };
}

export const channelConfigDefault = {
  type: {
    label: uiString.LABEL_TYPE,
    selection: [
      uiString.TYPE_0,
      ...typeSelectionOfResistance,
      ...typeSelectionOfThermal
    ],
    value: uiString.TYPE_7
  },
  range: {
    label: uiString.LABEL_RANGE_THERMAL,
    selection: rangeSelectionOfThermal,
    value: uiString.Thermal_RANGE_0
  },
  temper_coeff: {
    label: uiString.LABEL_TEMP_COEFF,
    selection: [uiString.TEMP_COEFF_0],
    value: uiString.TEMP_COEFF_0
  },
  temper_unit: {
    label: uiString.LABEL_TEMP_UNIT,
    selection: [
      uiString.TEMP_UNIT_0,
      uiString.TEMP_UNIT_1
    ],
    value: uiString.TEMP_UNIT_0
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
  overflow_alarm: {
    label: uiString.LABEL_OVER_FLOW_ALARM,
    value: true
  },
  underflow_alarm: {
    label: uiString.LABEL_UNDER_FLOW_ALARM,
    value: true
  },
  open_wire_alarm: {
    label: uiString.LABEL_OPEN_WIRE_ALARM,
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

  const channelNums = config.mlfb === '6ES7231-5PD32-0XB0' ? 4 : 8;

  for (let i = 0; i < channelNums; i++) {
    let rangeScenario = 'thermal';
    if ([4, 5, 6].includes(config[`ch${i}`].type)) {
      rangeScenario = 'resistance';
    } else if (config[`ch${i}`].type === 0) {
      rangeScenario = 'deactivated';
    }
    const chConfig = JSON.parse(JSON.stringify(channelConfigDefault));
    chConfig.type.value = converter.yamlToUi(`ch${i}.type`, config[`ch${i}`].type);
    chConfig.range.value = converter.yamlToUi(`ch${i}.range`, config[`ch${i}`].range, rangeScenario);
    chConfig.temper_coeff.value = converter.yamlToUi(`ch${i}.temper_coeff`, config[`ch${i}`].temper_coeff);
    chConfig.temper_unit.value = converter.yamlToUi(`ch${i}.temper_unit`, config[`ch${i}`].temper_unit);
    chConfig.smooth.value = converter.yamlToUi(`ch${i}.smooth`, config[`ch${i}`].smooth);
    chConfig.overflow_alarm.value = config[`ch${i}`].overflow_alarm;
    chConfig.underflow_alarm.value = config[`ch${i}`].underflow_alarm;
    chConfig.open_wire_alarm.value = config[`ch${i}`].open_wire_alarm;

    if (typeSelectionOfResistance.includes(chConfig.type.value)) {
      chConfig.range.label = uiString.LABEL_RANGE_RESISTOR;
      chConfig.range.selection = rangeSelectionOfResistance;
    } else if (typeSelectionOfThermal.includes(chConfig.type.value)) {
      chConfig.range.label = uiString.LABEL_RANGE_THERMAL;
      chConfig.range.selection = rangeSelectionOfThermal;
      const newSelection = decideTempCoeffSelection(chConfig.range.value);
      chConfig.temper_coeff.selection = newSelection.selection;
    } else {
      /* Do nothing */
    }

    ret.channels.push(chConfig);
  }

  return ret;
};

export function convertToDeviceFormat (config) {
  const ret = {
    description: 'TBD',
    mlfb: config.mlfb,
    power_alarm: config.power_alarm.value,
    integ_time: converter.uiToYaml('integ_time', config.integ_time.value)
  };

  const channelNums = config.mlfb === '6ES7231-5PD32-0XB0' ? 4 : 8;

  if (channelNums === 4) {
    ret.description = uiString.DESC_MOD_4CH;
  } else {
    ret.description = uiString.DESC_MOD_8CH;
  }

  for (let i = 0; i < channelNums; i++) {
    let rangeScenario = 'thermal';
    if ([
      uiString.TYPE_4,
      uiString.TYPE_5,
      uiString.TYPE_6
    ].includes(config.channels[i].type.value)) {
      rangeScenario = 'resistance';
    } else if (config.channels[i].type.value === uiString.TYPE_0) {
      rangeScenario = 'deactivated';
    }

    ret['ch' + i] = {
      type: converter.uiToYaml(`ch${i}.type`, config.channels[i].type.value),
      range: converter.uiToYaml(`ch${i}.range`, config.channels[i].range.value, rangeScenario),
      temper_coeff: converter.uiToYaml(`ch${i}.temper_coeff`, config.channels[i].temper_coeff.value),
      smooth: converter.uiToYaml(`ch${i}.smooth`, config.channels[i].smooth.value),
      temper_unit: converter.uiToYaml(`ch${i}.temper_unit`, config.channels[i].temper_unit.value),
      overflow_alarm: config.channels[i].overflow_alarm.value,
      underflow_alarm: config.channels[i].underflow_alarm.value,
      open_wire_alarm: config.channels[i].open_wire_alarm.value
    };
  }

  return ret;
};

export default function SM1231_RTDConf ({ slotNum, configData, updateConfig, chTotal }) {
  const postChangeChannelType = (event) => {
    updateChannelRange(event);
  };

  const updateChannelRange = (event) => {
    const chIndex = parseInt(event.target.name.slice(-1), 10);
    const newType = configData.channels[chIndex].type.value;

    if (typeSelectionOfResistance.includes(newType)) {
      configData.channels[chIndex].range.label = uiString.LABEL_RANGE_RESISTOR;
      configData.channels[chIndex].range.selection = rangeSelectionOfResistance;
      if (!configData.channels[chIndex].range.selection.includes(configData.channels[chIndex].range.value)) {
        configData.channels[chIndex].range.value = uiString.Resistance_RANGE_1;
      }
    } else if (typeSelectionOfThermal.includes(newType)) {
      configData.channels[chIndex].range.label = uiString.LABEL_RANGE_THERMAL;
      configData.channels[chIndex].range.selection = rangeSelectionOfThermal;
      if (!configData.channels[chIndex].range.selection.includes(configData.channels[chIndex].range.value)) {
        configData.channels[chIndex].range.value = uiString.Thermal_RANGE_0;
        updateChannelTempCoeff(event);
      }
    } else {
      /* Do nothing */
    }
  };

  const updateChannelTempCoeff = (event) => {
    const chIndex = parseInt(event.target.name.slice(-1), 10);
    const newRange = configData.channels[chIndex].range.value;

    if (!typeSelectionOfThermal.includes(configData.channels[chIndex].type.value)) {
      return;
    }

    const newSelection = decideTempCoeffSelection(newRange);

    configData.channels[chIndex].temper_coeff.selection = newSelection.selection;
    if (!newSelection.selection.includes(configData.channels[chIndex].temper_coeff.value)) {
      configData.channels[chIndex].temper_coeff.value = newSelection.defaultValue;
    }
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
        artNumber={configData.mlfb === '6ES7231-5PD32-0XB0' ? '6ES7 231-5PD32-0XB0' : '6ES7 231-5PF32-0XB0'}
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
                  postChange={postChangeChannelType}
                />

                <SelectionConfig
                  id={'range-ch' + index}
                  data={configData.channels[index].range}
                  updateConfig={updateSlotConfig}
                  postChange={updateChannelTempCoeff}
                  disabled={configData.channels[index].type.value === uiString.TYPE_0}
                />

                <SelectionConfig
                  id={'temp-coeff-ch' + index}
                  data={configData.channels[index].temper_coeff}
                  updateConfig={updateSlotConfig}
                  disabled={
                    typeSelectionOfResistance.includes(configData.channels[index].type.value) ||
                    configData.channels[index].type.value === uiString.TYPE_0
                  }
                />

                <SelectionConfig
                  id={'tempunit-ch' + index}
                  data={configData.channels[index].temper_unit}
                  updateConfig={updateSlotConfig}
                  disabled={
                    typeSelectionOfResistance.includes(configData.channels[index].type.value) ||
                    configData.channels[index].type.value === uiString.TYPE_0
                  }
                />

                <SelectionConfig
                  id={'smooth-ch' + index}
                  data={configData.channels[index].smooth}
                  updateConfig={updateSlotConfig}
                  disabled={configData.channels[index].type.value === uiString.TYPE_0}
                />

                <CheckConfig
                  id={'openwire-alarm-ch' + index}
                  data={configData.channels[index].open_wire_alarm}
                  updateConfig={updateSlotConfig}
                  disabled={configData.channels[index].type.value === uiString.TYPE_0}
                />

                <CheckConfig
                  id={'overflow-alarm-ch' + index}
                  data={configData.channels[index].overflow_alarm}
                  updateConfig={updateSlotConfig}
                  disabled={configData.channels[index].type.value === uiString.TYPE_0}
                />

                <CheckConfig
                  id={'underflow-alarm-ch' + index}
                  data={configData.channels[index].underflow_alarm}
                  updateConfig={updateSlotConfig}
                  disabled={
                    typeSelectionOfResistance.includes(configData.channels[index].type.value) ||
                    configData.channels[index].type.value === uiString.TYPE_0
                  }
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
