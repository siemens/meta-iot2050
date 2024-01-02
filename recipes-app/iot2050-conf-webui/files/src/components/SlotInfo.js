/* eslint-disable camelcase */
/* eslint-disable react/prop-types */
import * as React from 'react';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import MenuItem from '@mui/material/MenuItem';
import Typography from '@mui/material/Typography';

function Mod ({ modType, slotNum, config, updateConfig }) {
  switch (modType) {
    default:
      return <Typography>No module in this slot!!!</Typography>;
  }
}

export default function SlotInfo ({ slotNum, configData, updateSlot }) {
  const onChangeModSelect = (event) => {
    switch (event.target.value) {
      default:
        updateSlot(slotNum, { mlfb: 'None' });
    }
  };

  const moduleTypes = [
    'None',
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
