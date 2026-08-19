/* eslint-disable react/prop-types */
import * as React from 'react';
import Stack from '@mui/material/Stack';
import Paper from '@mui/material/Paper';
import FormGroup from '@mui/material/FormGroup';
import FormControl from '@mui/material/FormControl';
import ModuleInfo from '@/components/ModuleInfo';
import SelectionConfig from '@/components/ConfigEntry/SelectionConfig';
import CheckConfig from '@/components/ConfigEntry/CheckConfig';
import SliderConfig from '@/components/ConfigEntry/SliderConfig';
import ConfigGroupLabel from '@/components/ConfigEntry/ConfigGroupLabel';
import ConfTextConverter from '@/lib/smConfig/ConfTextConverter';
import uiString from '@/lib/uiString/SM1238EM480VAC.json';
import { range } from 'lodash';

const yamlUIMapping = [
  {
    keys: [/module_version/],
    rules: [
      {
        scenario: 'all',
        mapping: [
          { ui: uiString.MOD_VER_32, yaml: 32 },
          { ui: uiString.MOD_VER_112, yaml: 112 },
          { ui: uiString.MOD_VER_224, yaml: 224 },
          { ui: uiString.MOD_VER_225, yaml: 225 },
          { ui: uiString.MOD_VER_226, yaml: 226 },
          { ui: uiString.MOD_VER_227, yaml: 227 }
        ]
      }
    ]
  },
  {
    keys: [/con_type/],
    rules: [
      {
        scenario: 'all',
        mapping: [
          { ui: uiString.CON_TYPE_00, yaml: 0x00 },
          { ui: uiString.CON_TYPE_0B, yaml: 0x0B },
          { ui: uiString.CON_TYPE_0C, yaml: 0x0C },
          { ui: uiString.CON_TYPE_0E, yaml: 0x0E },
          { ui: uiString.CON_TYPE_10, yaml: 0x10 },
          { ui: uiString.CON_TYPE_0F, yaml: 0x0F }
        ]
      }
    ]
  },
  {
    keys: [/range/],
    rules: [
      {
        scenario: 'all',
        mapping: [
          { ui: uiString.RANGE_01, yaml: 0x01 },
          { ui: uiString.RANGE_02, yaml: 0x02 },
          { ui: uiString.RANGE_03, yaml: 0x03 },
          { ui: uiString.RANGE_04, yaml: 0x04 },
          { ui: uiString.RANGE_05, yaml: 0x05 },
          { ui: uiString.RANGE_06, yaml: 0x06 },
          { ui: uiString.RANGE_07, yaml: 0x07 },
          { ui: uiString.RANGE_08, yaml: 0x08 },
          { ui: uiString.RANGE_09, yaml: 0x09 },
          { ui: uiString.RANGE_0A, yaml: 0x0A },
          { ui: uiString.RANGE_0B, yaml: 0x0B },
          { ui: uiString.RANGE_0C, yaml: 0x0C }
        ]
      }
    ]
  },
  {
    keys: [/line_freq/],
    rules: [
      {
        scenario: 'all',
        mapping: [
          { ui: uiString.LINE_FREQ_1, yaml: 1 },
          { ui: uiString.LINE_FREQ_2, yaml: 2 }
        ]
      }
    ]
  },
  {
    keys: [/data_variant/],
    rules: [
      {
        scenario: 'all',
        mapping: [
          { ui: uiString.DATA_VARIANT_FE, yaml: 0xFE },
          { ui: uiString.DATA_VARIANT_FD, yaml: 0xFD },
          { ui: uiString.DATA_VARIANT_FC, yaml: 0xFC },
          { ui: uiString.DATA_VARIANT_FB, yaml: 0xFB },
          { ui: uiString.DATA_VARIANT_FA, yaml: 0xFA },
          { ui: uiString.DATA_VARIANT_F9, yaml: 0xF9 },
          { ui: uiString.DATA_VARIANT_F8, yaml: 0xF8 },
          { ui: uiString.DATA_VARIANT_F7, yaml: 0xF7 },
          { ui: uiString.DATA_VARIANT_F6, yaml: 0xF6 },
          { ui: uiString.DATA_VARIANT_F5, yaml: 0xF5 },
          { ui: uiString.DATA_VARIANT_F0, yaml: 0xF0 },
          { ui: uiString.DATA_VARIANT_EF, yaml: 0xEF },
          { ui: uiString.DATA_VARIANT_E3, yaml: 0xE3 },
          { ui: uiString.DATA_VARIANT_E2, yaml: 0xE2 },
          { ui: uiString.DATA_VARIANT_E1, yaml: 0xE1 },
          { ui: uiString.DATA_VARIANT_E0, yaml: 0xE0 },
          { ui: uiString.DATA_VARIANT_9F, yaml: 0x9F },
          { ui: uiString.DATA_VARIANT_9E, yaml: 0x9E },
          { ui: uiString.DATA_VARIANT_9D, yaml: 0x9D },
          { ui: uiString.DATA_VARIANT_9C, yaml: 0x9C },
          { ui: uiString.DATA_VARIANT_9B, yaml: 0x9B },
          { ui: uiString.DATA_VARIANT_9A, yaml: 0x9A }
        ]
      }
    ]
  },
  {
    keys: [/period_meters/],
    rules: [
      {
        scenario: 'all',
        mapping: [
          { ui: uiString.PERIOD_METERS_0, yaml: 0 },
          { ui: uiString.PERIOD_METERS_1, yaml: 1 },
          { ui: uiString.PERIOD_METERS_2, yaml: 2 },
          { ui: uiString.PERIOD_METERS_3, yaml: 3 },
          { ui: uiString.PERIOD_METERS_4, yaml: 4 },
          { ui: uiString.PERIOD_METERS_5, yaml: 5 }
        ]
      }
    ]
  },
  {
    keys: [/ch[0-2]\.ct_second_cur/],
    rules: [
      {
        scenario: 'all',
        mapping: [
          { ui: uiString.CT_SND_CUR_0, yaml: 0 },
          { ui: uiString.CT_SND_CUR_2, yaml: 2 }
        ]
      }
    ]
  }
];

const converter = new ConfTextConverter(yamlUIMapping);

const modVerSelection = [
  uiString.MOD_VER_32,
  uiString.MOD_VER_112
];

const conTypeSelection = [
  uiString.CON_TYPE_00,
  uiString.CON_TYPE_0B,
  uiString.CON_TYPE_0C,
  uiString.CON_TYPE_0E,
  uiString.CON_TYPE_10,
  uiString.CON_TYPE_0F
];

const rangeSelection = [
  uiString.RANGE_01,
  uiString.RANGE_02,
  uiString.RANGE_03,
  uiString.RANGE_04,
  uiString.RANGE_05,
  uiString.RANGE_06,
  uiString.RANGE_07,
  uiString.RANGE_08,
  uiString.RANGE_09,
  uiString.RANGE_0A,
  uiString.RANGE_0B,
  uiString.RANGE_0C
];

const lineFreqSelection = [
  uiString.LINE_FREQ_2,
  uiString.LINE_FREQ_1
];

const periodMetersSelection = [
  uiString.PERIOD_METERS_0,
  uiString.PERIOD_METERS_1,
  uiString.PERIOD_METERS_2,
  uiString.PERIOD_METERS_3,
  uiString.PERIOD_METERS_4,
  uiString.PERIOD_METERS_5
];

const dataVariantSelectionDefault = [
  uiString.DATA_VARIANT_FE,
  uiString.DATA_VARIANT_FD,
  uiString.DATA_VARIANT_FC,
  uiString.DATA_VARIANT_FB,
  uiString.DATA_VARIANT_FA,
  uiString.DATA_VARIANT_F9,
  uiString.DATA_VARIANT_F8,
  uiString.DATA_VARIANT_F7,
  uiString.DATA_VARIANT_F6,
  uiString.DATA_VARIANT_F5,
  uiString.DATA_VARIANT_F0,
  uiString.DATA_VARIANT_EF,
  uiString.DATA_VARIANT_E3,
  uiString.DATA_VARIANT_E2,
  uiString.DATA_VARIANT_E1,
  uiString.DATA_VARIANT_E0,
  uiString.DATA_VARIANT_9F,
  uiString.DATA_VARIANT_9E,
  uiString.DATA_VARIANT_9D,
  uiString.DATA_VARIANT_9C,
  uiString.DATA_VARIANT_9B,
  uiString.DATA_VARIANT_9A
];

const ctSndCurSelection = [
  uiString.CT_SND_CUR_0,
  uiString.CT_SND_CUR_2
];

const channelConfigDefault = {
  diag_over_cur: {
    label: uiString.LABEL_DIAG_OVER_CUR,
    value: false
  },
  diag_over_cal: {
    label: uiString.LABEL_DIAG_OVER_CAL,
    value: false
  },
  diag_ll_vol: {
    label: uiString.LABEL_DIAG_LL_VOL,
    value: false
  },
  diag_under_vol: {
    label: uiString.LABEL_DIAG_UNDER_VOL,
    value: false
  },
  diag_over_vol: {
    label: uiString.LABEL_DIAG_OVER_VOL,
    value: false
  },
  over_cur_tol_val: {
    label: uiString.LABEL_SND_OVER_CUR_TOL_VAL,
    value: 100,
    min: 10,
    max: 100
  },
  over_cur_tol_time: {
    label: uiString.LABEL_OVER_CUR_TOL_TIME,
    value: 40000,
    min: 0,
    max: 60000
  },
  ct_primary_cur: {
    label: uiString.LABEL_CT_PRIMARY_CUR,
    value: 1,
    min: 1,
    max: 99999
  },
  en_gate_cir_hour_meter: {
    label: uiString.LABEL_EN_GATE_CIR_HOUR_METER,
    value: false
  },
  ct_second_cur: {
    label: uiString.LABEL_CT_SND_CUR,
    value: uiString.CT_SND_CUR_0,
    selection: ctSndCurSelection
  },
  act_hour_meter: {
    label: uiString.LABEL_ACT_HOUR_METER,
    value: false
  },
  re_cur_dir: {
    label: uiString.LABEL_RE_CUR_DIR,
    value: false
  },
  ll_cur_measure: {
    label: uiString.LABEL_LL_CUR_MEASURE,
    value: 50,
    min: 2,
    max: 250
  },
  vt_second_vol: {
    label: uiString.LABEL_VT_SND_VOL,
    value: 230,
    min: 1,
    max: 500
  },
  vt_prim_vol: {
    label: uiString.LABEL_VT_PRIM_VOL,
    value: 230,
    min: 1,
    max: 999999
  }
};

export const SM1238EM480VACConfDefault = {
  mlfb: '6ES7238-5XA32-0XB0',
  module_version: {
    label: uiString.LABEL_MOD_VER,
    selection: modVerSelection,
    value: uiString.MOD_VER_112
  },
  con_type: {
    label: uiString.LABEL_CON_TYPE,
    selection: conTypeSelection,
    value: uiString.CON_TYPE_0C
  },
  range: {
    label: uiString.LABEL_RANGE,
    selection: rangeSelection,
    value: uiString.RANGE_0A
  },
  line_freq: {
    label: uiString.LABEL_LINE_FREQ,
    selection: lineFreqSelection,
    value: uiString.LINE_FREQ_2
  },
  period_meters: {
    label: uiString.LABEL_PERIOD_METERS,
    selection: periodMetersSelection,
    value: uiString.PERIOD_METERS_0
  },
  meter_gate: {
    label: uiString.LABEL_METER_GATE,
    value: false
  },
  min_max_cal: {
    label: uiString.LABEL_MIN_MAX_CAL,
    value: false
  },
  line_vol_tol: {
    label: uiString.LABEL_LINE_VOL_TOL,
    value: 10,
    min: 1,
    max: 50
  },
  diag_line_vol: {
    label: uiString.LABEL_LINE_VOL_DIAG,
    value: false
  },
  data_variant: {
    label: uiString.LABEL_DATA_VARIANT,
    selection: dataVariantSelectionDefault,
    value: uiString.DATA_VARIANT_FE
  },
  channels: [
    JSON.parse(JSON.stringify(channelConfigDefault)),
    JSON.parse(JSON.stringify(channelConfigDefault)),
    JSON.parse(JSON.stringify(channelConfigDefault))
  ]
};

export function convertToUIFormat (config) {
  const ret = JSON.parse(JSON.stringify(SM1238EM480VACConfDefault));

  ret.module_version.value = converter.yamlToUi('module_version', config.module_version);
  ret.con_type.value = converter.yamlToUi('con_type', config.con_type);
  ret.range.value = converter.yamlToUi('range', config.range);
  ret.line_freq.value = converter.yamlToUi('line_freq', config.line_freq);
  ret.period_meters.value = converter.yamlToUi('period_meters', config.period_meters);
  ret.meter_gate.value = config.meter_gate;
  ret.min_max_cal.value = config.min_max_cal;
  ret.line_vol_tol.value = config.line_vol_tol;
  ret.diag_line_vol.value = config.diag_line_vol;
  ret.data_variant.value = converter.yamlToUi('data_variant', config.data_variant);

  for (let i = 0; i < 3; i++) {
    ret.channels[i].diag_over_cur.value = config[`ch${i}`].diag_over_cur;
    ret.channels[i].diag_over_cal.value = config[`ch${i}`].diag_over_cal;
    ret.channels[i].diag_ll_vol.value = config[`ch${i}`].diag_ll_vol;
    ret.channels[i].diag_under_vol.value = config[`ch${i}`].diag_under_vol;
    ret.channels[i].diag_over_vol.value = config[`ch${i}`].diag_over_vol;
    ret.channels[i].over_cur_tol_val.value = config[`ch${i}`].over_cur_tol_val;
    ret.channels[i].over_cur_tol_time.value = config[`ch${i}`].over_cur_tol_time;
    ret.channels[i].ct_primary_cur.value = config[`ch${i}`].ct_primary_cur;
    ret.channels[i].en_gate_cir_hour_meter.value = config[`ch${i}`].en_gate_cir_hour_meter;
    ret.channels[i].ct_second_cur.value = converter.yamlToUi(`ch${i}.ct_second_cur`, config[`ch${i}`].ct_second_cur);
    ret.channels[i].act_hour_meter.value = config[`ch${i}`].act_hour_meter;
    ret.channels[i].re_cur_dir.value = config[`ch${i}`].re_cur_dir;
    ret.channels[i].ll_cur_measure.value = config[`ch${i}`].ll_cur_measure;
    ret.channels[i].vt_second_vol.value = config[`ch${i}`].vt_second_vol;
    ret.channels[i].vt_prim_vol.value = config[`ch${i}`].vt_prim_vol;
  }
  return ret;
};

export function convertToDeviceFormat (config) {
  const ret = {
    description: uiString.DESC_MOD,
    mlfb: config.mlfb,
    module_version: converter.uiToYaml('module_version', config.module_version.value),
    con_type: converter.uiToYaml('con_type', config.con_type.value),
    range: converter.uiToYaml('range', config.range.value),
    line_freq: converter.uiToYaml('line_freq', config.line_freq.value),
    period_meters: converter.uiToYaml('period_meters', config.period_meters.value),
    meter_gate: config.meter_gate.value,
    min_max_cal: config.min_max_cal.value,
    line_vol_tol: config.line_vol_tol.value,
    diag_line_vol: config.diag_line_vol.value,
    data_variant: converter.uiToYaml('data_variant', config.data_variant.value)
  };

  for (let i = 0; i < 3; i++) {
    ret['ch' + i] = {
      diag_over_cur: config.channels[i].diag_over_cur.value,
      diag_over_cal: config.channels[i].diag_over_cal.value,
      diag_ll_vol: config.channels[i].diag_ll_vol.value,
      diag_under_vol: config.channels[i].diag_under_vol.value,
      diag_over_vol: config.channels[i].diag_over_vol.value,
      over_cur_tol_val: config.channels[i].over_cur_tol_val.value,
      over_cur_tol_time: config.channels[i].over_cur_tol_time.value,
      ct_primary_cur: config.channels[i].ct_primary_cur.value,
      en_gate_cir_hour_meter: config.channels[i].en_gate_cir_hour_meter.value,
      ct_second_cur: converter.uiToYaml(`ch${i}.ct_second_cur`, config.channels[i].ct_second_cur.value),
      act_hour_meter: config.channels[i].act_hour_meter.value,
      re_cur_dir: config.channels[i].re_cur_dir.value,
      ll_cur_measure: config.channels[i].ll_cur_measure.value,
      vt_second_vol: config.channels[i].vt_second_vol.value,
      vt_prim_vol: config.channels[i].vt_prim_vol.value
    };
  }
  return ret;
};

export default function SM1238EM480VACConf ({ slotNum, configData, updateConfig }) {
  const setDataVariantSelection = (event) => {
    switch (configData.module_version.value) {
      case uiString.MOD_VER_224:
        configData.data_variant.selection = [uiString.DATA_VARIANT_E0];
        configData.data_variant.value = uiString.DATA_VARIANT_E0;
        break;
      case uiString.MOD_VER_225:
        configData.data_variant.selection = [uiString.DATA_VARIANT_E1];
        configData.data_variant.value = uiString.DATA_VARIANT_E1;
        break;
      case uiString.MOD_VER_226:
        configData.data_variant.selection = [uiString.DATA_VARIANT_E2];
        configData.data_variant.value = uiString.DATA_VARIANT_E2;
        break;
      case uiString.MOD_VER_227:
        configData.data_variant.selection = [uiString.DATA_VARIANT_E3];
        configData.data_variant.value = uiString.DATA_VARIANT_E3;
        break;
      case uiString.MOD_VER_112:
        switch (configData.con_type.value) {
          case uiString.CON_TYPE_00:
          case uiString.CON_TYPE_0C:
          case uiString.CON_TYPE_0E:
          case uiString.CON_TYPE_0F:
            configData.data_variant.selection = dataVariantSelectionDefault;
            if (!configData.data_variant.selection.includes(configData.data_variant.value)) {
              configData.data_variant.value = uiString.DATA_VARIANT_FE;
            }
            break;
          case uiString.CON_TYPE_0B:
            configData.data_variant.selection = dataVariantSelectionDefault.filter(
              (variant) => ![
                uiString.DATA_VARIANT_F7,
                uiString.DATA_VARIANT_F6,
                uiString.DATA_VARIANT_F5,
                uiString.DATA_VARIANT_9D,
                uiString.DATA_VARIANT_9C,
                uiString.DATA_VARIANT_9B,
                uiString.DATA_VARIANT_9A
              ].includes(variant)
            );
            if (!configData.data_variant.selection.includes(configData.data_variant.value)) {
              configData.data_variant.value = uiString.DATA_VARIANT_FE;
            }
            break;
          case uiString.CON_TYPE_10:
            configData.data_variant.selection = dataVariantSelectionDefault.filter(
              (variant) => ![
                uiString.DATA_VARIANT_F6,
                uiString.DATA_VARIANT_9B,
                uiString.DATA_VARIANT_9A
              ].includes(variant)
            );
            if (!configData.data_variant.selection.includes(configData.data_variant.value)) {
              configData.data_variant.value = uiString.DATA_VARIANT_FE;
            }
            break;
        }
        break;
      case uiString.MOD_VER_32:
        switch (configData.con_type.value) {
          case uiString.CON_TYPE_00:
          case uiString.CON_TYPE_0C:
          case uiString.CON_TYPE_0E:
          case uiString.CON_TYPE_0F:
            configData.data_variant.selection = dataVariantSelectionDefault.filter(
              (variant) => ![uiString.DATA_VARIANT_E3].includes(variant)
            );
            if (!configData.data_variant.selection.includes(configData.data_variant.value)) {
              configData.data_variant.value = uiString.DATA_VARIANT_FE;
            }
            break;
          case uiString.CON_TYPE_0B:
            configData.data_variant.selection = dataVariantSelectionDefault.filter(
              (variant) => ![
                uiString.DATA_VARIANT_E3,
                uiString.DATA_VARIANT_F7,
                uiString.DATA_VARIANT_F6,
                uiString.DATA_VARIANT_F5,
                uiString.DATA_VARIANT_9D,
                uiString.DATA_VARIANT_9C,
                uiString.DATA_VARIANT_9B,
                uiString.DATA_VARIANT_9A
              ].includes(variant)
            );
            if (!configData.data_variant.selection.includes(configData.data_variant.value)) {
              configData.data_variant.value = uiString.DATA_VARIANT_FE;
            }
            break;
          case uiString.CON_TYPE_10:
            configData.data_variant.selection = dataVariantSelectionDefault.filter(
              (variant) => ![
                uiString.DATA_VARIANT_E3,
                uiString.DATA_VARIANT_F6,
                uiString.DATA_VARIANT_9B,
                uiString.DATA_VARIANT_9A
              ].includes(variant)
            );
            if (!configData.data_variant.selection.includes(configData.data_variant.value)) {
              configData.data_variant.value = uiString.DATA_VARIANT_FE;
            }
            break;
        }
        break;
    }
  };

  const setCtSndCurSelection = (event) => {
    switch (configData.con_type.value) {
      case uiString.CON_TYPE_0F:
        for (let i = 0; i < 3; i++) {
          configData.channels[i].ct_second_cur.selection = [uiString.CT_SND_CUR_0];
          configData.channels[i].ct_second_cur.value = uiString.CT_SND_CUR_0;
        }
        break;
      default:
        for (let i = 0; i < 3; i++) {
          configData.channels[i].ct_second_cur.selection = ctSndCurSelection;
        }
        break;
    };
  };

  const updateSelectionOnChangeConType = (event) => {
    setDataVariantSelection(event);
    setCtSndCurSelection(event);
    if (configData.con_type.value === uiString.CON_TYPE_0E) {
      configData.channels[1].ct_primary_cur.value = configData.channels[0].ct_primary_cur.value;
      configData.channels[2].ct_primary_cur.value = configData.channels[0].ct_primary_cur.value;

      configData.channels[1].ct_second_cur.value = configData.channels[0].ct_second_cur.value;
      configData.channels[2].ct_second_cur.value = configData.channels[0].ct_second_cur.value;

      configData.channels[1].vt_prim_vol.value = configData.channels[0].vt_prim_vol.value;
      configData.channels[2].vt_prim_vol.value = configData.channels[0].vt_prim_vol.value;

      configData.channels[1].vt_second_vol.value = configData.channels[0].vt_second_vol.value;
      configData.channels[2].vt_second_vol.value = configData.channels[0].vt_second_vol.value;

      configData.channels[1].ll_cur_measure.value = configData.channels[0].ll_cur_measure.value;
      configData.channels[2].ll_cur_measure.value = configData.channels[0].ll_cur_measure.value;

      configData.channels[1].re_cur_dir.value = configData.channels[0].re_cur_dir.value;
      configData.channels[2].re_cur_dir.value = configData.channels[0].re_cur_dir.value;
    }
  };

  const updateCtPrimaryCur = (id) => {
    const chIndex = parseInt(id.slice(-1), 10);
    if (configData.con_type.value === uiString.CON_TYPE_0E && chIndex === 0) {
      const newValue = configData.channels[chIndex].ct_primary_cur.value;
      configData.channels[1].ct_primary_cur.value = newValue;
      configData.channels[2].ct_primary_cur.value = newValue;
    }
  };

  const updateCtSecondCur = (event) => {
    const chIndex = parseInt(event.target.name.slice(-1), 10);
    if (configData.con_type.value === uiString.CON_TYPE_0E && chIndex === 0) {
      const newValue = configData.channels[chIndex].ct_second_cur.value;
      configData.channels[1].ct_second_cur.value = newValue;
      configData.channels[2].ct_second_cur.value = newValue;
    }
  };

  const updateVtPrimVol = (id) => {
    const chIndex = parseInt(id.slice(-1), 10);
    if (configData.con_type.value === uiString.CON_TYPE_0E && chIndex === 0) {
      const newValue = configData.channels[chIndex].vt_prim_vol.value;
      configData.channels[1].vt_prim_vol.value = newValue;
      configData.channels[2].vt_prim_vol.value = newValue;
    }
  };

  const updateVtSecondVol = (id) => {
    const chIndex = parseInt(id.slice(-1), 10);
    if (configData.con_type.value === uiString.CON_TYPE_0E && chIndex === 0) {
      const newValue = configData.channels[chIndex].vt_second_vol.value;
      configData.channels[1].vt_second_vol.value = newValue;
      configData.channels[2].vt_second_vol.value = newValue;
    }
  };

  const updateLlCurMeasure = (id) => {
    const chIndex = parseInt(id.slice(-1), 10);
    if (configData.con_type.value === uiString.CON_TYPE_0E && chIndex === 0) {
      const newValue = configData.channels[chIndex].ll_cur_measure.value;
      configData.channels[1].ll_cur_measure.value = newValue;
      configData.channels[2].ll_cur_measure.value = newValue;
    }
  };

  const updateReCurDir = (id) => {
    const chIndex = parseInt(id.slice(-1), 10);
    if (configData.con_type.value === uiString.CON_TYPE_0E && chIndex === 0) {
      const newValue = configData.channels[chIndex].re_cur_dir.value;
      configData.channels[1].re_cur_dir.value = newValue;
      configData.channels[2].re_cur_dir.value = newValue;
    }
  };

  const updateSlotConfig = () => {
    updateConfig(slotNum, configData);
  };

  const isChannelDisabled = (index) => {
    return configData.con_type.value === uiString.CON_TYPE_00 ||
      (index === 1 && configData.con_type.value === uiString.CON_TYPE_0B) ||
      (index === 2 && (configData.con_type.value === uiString.CON_TYPE_0B ||
                       configData.con_type.value === uiString.CON_TYPE_10));
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
        artNumber="6ES7 238-5XA32-0XB0"
        fwVersion="NA"
      />

      <Paper elevation={3}>
        <FormControl sx={{ m: 2 }} component="fieldset" variant="standard">
          <ConfigGroupLabel label='Diagnostics' />
          <FormGroup>
            <Stack
              direction="column"
              justifyContent="flex-start"
              alignItems="stretch"
              spacing={2}
            >

              <CheckConfig
                id='diag-line-vol'
                data={configData.diag_line_vol}
                updateConfig={updateSlotConfig}
                disabled={configData.con_type.value === uiString.CON_TYPE_00}
              />

              <SliderConfig
                id="line-vol-tol-slider"
                data={configData.line_vol_tol}
                unit='%'
                updateConfig={updateSlotConfig}
                disabled={configData.con_type.value === uiString.CON_TYPE_00}
              />

            </Stack>
          </FormGroup>
        </FormControl>
      </Paper>

      <Paper elevation={3}>
        <FormControl sx={{ m: 2 }} component="fieldset" variant="standard">
          <ConfigGroupLabel label='Measurement' />
          <FormGroup>
            <Stack
              direction="column"
              justifyContent="flex-start"
              alignItems="stretch"
              spacing={2}
            >
              <SelectionConfig
                id='con-type'
                data={configData.con_type}
                updateConfig={updateSlotConfig}
                postChange={updateSelectionOnChangeConType}
              />

              <SelectionConfig
                id='range'
                data={configData.range}
                updateConfig={updateSlotConfig}
                disabled={configData.con_type.value === uiString.CON_TYPE_00}
              />

              <SelectionConfig
                id='line-freq'
                data={configData.line_freq}
                updateConfig={updateSlotConfig}
                disabled={configData.con_type.value === uiString.CON_TYPE_00}
              />

              <SelectionConfig
                id='period-meters'
                data={configData.period_meters}
                updateConfig={updateSlotConfig}
                disabled={configData.con_type.value === uiString.CON_TYPE_00}
              />

              <CheckConfig
                id='meter-gate'
                data={configData.meter_gate}
                updateConfig={updateSlotConfig}
                disabled={configData.con_type.value === uiString.CON_TYPE_00}
              />

              <CheckConfig
                id='min-max-cal'
                data={configData.min_max_cal}
                updateConfig={updateSlotConfig}
                disabled={configData.con_type.value === uiString.CON_TYPE_00}
              />
            </Stack>
          </FormGroup>
        </FormControl>
      </Paper>

      <Paper elevation={3}>
        <FormControl sx={{ m: 2 }} component="fieldset" variant="standard">
          <ConfigGroupLabel label='Operating mode' />
          <FormGroup>
            <Stack
              direction="column"
              justifyContent="flex-start"
              alignItems="stretch"
              spacing={2}
            >
              <SelectionConfig
                id='module-version'
                data={configData.module_version}
                updateConfig={updateSlotConfig}
                disabled={configData.con_type.value === uiString.CON_TYPE_00}
                postChange={setDataVariantSelection}
              />

              <SelectionConfig
                id='data-variant'
                data={configData.data_variant}
                updateConfig={updateSlotConfig}
                disabled={configData.con_type.value === uiString.CON_TYPE_00}
              />

            </Stack>
          </FormGroup>
        </FormControl>
      </Paper>

      {range(0, 3).map((index) => (
        <Paper elevation={3} key={'ch-' + index}>
          <FormControl sx={{ m: 2 }} component="fieldset" variant="standard">
            <ConfigGroupLabel label={'Channel ' + index} />
            <FormGroup disabled={true}>
              <Stack
                direction="column"
                justifyContent="flex-start"
                alignItems="stretch"
                spacing={2}
              >
              </Stack>

                <CheckConfig
                  id={'diag-over-cur-ch' + index}
                  data={configData.channels[index].diag_over_cur}
                  updateConfig={updateSlotConfig}
                  disabled={isChannelDisabled(index)}
                />

                <CheckConfig
                  id={'diag-over-vol-ch' + index}
                  data={configData.channels[index].diag_over_vol}
                  updateConfig={updateSlotConfig}
                  disabled={isChannelDisabled(index)}
                />

                <CheckConfig
                  id={'diag-under-vol-ch' + index}
                  data={configData.channels[index].diag_under_vol}
                  updateConfig={updateSlotConfig}
                  disabled={isChannelDisabled(index)}
                />

                <CheckConfig
                  id={'diag-ll-vol-ch' + index}
                  data={configData.channels[index].diag_ll_vol}
                  updateConfig={updateSlotConfig}
                  disabled={isChannelDisabled(index)}
                />

                <CheckConfig
                  id={'diag-over-cal-ch' + index}
                  data={configData.channels[index].diag_over_cal}
                  updateConfig={updateSlotConfig}
                  disabled={isChannelDisabled(index)}
                />

                <SliderConfig
                  id={'second-over-cur-tol-val-ch' + index}
                  data={configData.channels[index].over_cur_tol_val}
                  unit='0.1 A'
                  updateConfig={updateSlotConfig}
                  disabled={isChannelDisabled(index)}
                />

                <SliderConfig
                  id={'over-cur-tol-time-ch' + index}
                  data={configData.channels[index].over_cur_tol_time}
                  unit='ms'
                  updateConfig={updateSlotConfig}
                  disabled={isChannelDisabled(index)}
                />

                <CheckConfig
                  id={'act-hour-meter-ch' + index}
                  data={configData.channels[index].act_hour_meter}
                  updateConfig={updateSlotConfig}
                  disabled={isChannelDisabled(index)}
                />

                <CheckConfig
                  id={'en-gate-cir-hour-meter-ch' + index}
                  data={configData.channels[index].en_gate_cir_hour_meter}
                  updateConfig={updateSlotConfig}
                  disabled={isChannelDisabled(index)}
                />

                <SliderConfig
                  id={'ct-primary-cur-ch' + index}
                  data={configData.channels[index].ct_primary_cur}
                  unit='A'
                  updateConfig={updateSlotConfig}
                  postChange={updateCtPrimaryCur}
                  disabled={isChannelDisabled(index) || (
                    configData.con_type.value === uiString.CON_TYPE_0E && index > 0)
                  }

                />

                <SelectionConfig
                  id={'ct-second-cur-ch' + index}
                  data={configData.channels[index].ct_second_cur}
                  updateConfig={updateSlotConfig}
                  postChange={updateCtSecondCur}
                  disabled={isChannelDisabled(index) ||
                    configData.con_type.value === uiString.CON_TYPE_0F || (
                    configData.con_type.value === uiString.CON_TYPE_0E && index > 0)
                  }
                />

                <SliderConfig
                  id={'vt-prim-vol-ch' + index}
                  data={configData.channels[index].vt_prim_vol}
                  unit='V'
                  updateConfig={updateSlotConfig}
                  postChange={updateVtPrimVol}
                  disabled={isChannelDisabled(index) || (
                    configData.con_type.value === uiString.CON_TYPE_0E && index > 0)}
                />

                <SliderConfig
                  id={'vt-second-vol-ch' + index}
                  data={configData.channels[index].vt_second_vol}
                  unit='V'
                  updateConfig={updateSlotConfig}
                  postChange={updateVtSecondVol}
                  disabled={isChannelDisabled(index) || (
                    configData.con_type.value === uiString.CON_TYPE_0E && index > 0)}
                />

                <SliderConfig
                  id={'ll-cur-measure-ch' + index}
                  data={configData.channels[index].ll_cur_measure}
                  unit='mA'
                  updateConfig={updateSlotConfig}
                  postChange={updateLlCurMeasure}
                  disabled={isChannelDisabled(index) || (
                    configData.con_type.value === uiString.CON_TYPE_0E && index > 0)}
                />

                <CheckConfig
                  id={'re-cur-dir-ch' + index}
                  data={configData.channels[index].re_cur_dir}
                  updateConfig={updateSlotConfig}
                  postChange={updateReCurDir}
                  disabled={isChannelDisabled(index) || (
                    configData.con_type.value === uiString.CON_TYPE_0E && index > 0)}
                />

            </FormGroup>
          </FormControl>
        </Paper>
      ))}
    </Stack>
  );
}
