/* eslint-disable camelcase */
/* eslint-disable react/prop-types */
import * as React from 'react';
import SM1231AIConf, { channelConfigDefault } from './SM1231AIConf';
import uiString from '@/lib/uiString/SM1231_AI.json';

export const SM1231with4AIConfDefault = {
  mlfb: '6ES7231-4HD32-0XB0',
  power_alarm: {
    label: uiString.LABEL_POWER_ALARM,
    value: true
  },
  integ_time: {
    label: uiString.LABEL_INT_TIME,
    selection: [
      uiString.INT_TIME_0,
      uiString.INT_TIME_1,
      uiString.INT_TIME_2,
      uiString.INT_TIME_3
    ],
    value: uiString.INT_TIME_2
  },
  channels: [
    JSON.parse(JSON.stringify(channelConfigDefault)),
    JSON.parse(JSON.stringify(channelConfigDefault)),
    JSON.parse(JSON.stringify(channelConfigDefault)),
    JSON.parse(JSON.stringify(channelConfigDefault))
  ]
};

export default function SM1231with4AIConf ({ slotNum, configData, updateConfig }) {
  return (
    <SM1231AIConf
      slotNum={slotNum}
      configData={configData}
      updateConfig={updateConfig}
      chTotal={4}
    />
  );
}
