/* eslint-disable camelcase */
/* eslint-disable react/prop-types */
import * as React from 'react';
import SM1223Conf from './SM1223Conf';

export default function SM1223_DC_DI16_DQ16RLY_Conf ({ slotNum, configData, updateConfig }) {
  return (
    <SM1223Conf
      slotNum={slotNum}
      configData={configData}
      updateConfig={updateConfig}
      chTotal={16}
    />
  );
}
