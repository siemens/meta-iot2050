/* eslint-disable react/prop-types */
import * as React from 'react';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';

export default function ModuleInfo ({ description, artNumber, fwVersion }) {
  return (
    <Stack
      direction="column"
      justifyContent="flex-start"
      alignItems="stretch"
      spacing={2}
    >
      <TextField
        disabled={true}
        id="description-sm1223"
        label="Description"
        defaultValue={description}
        InputProps={{
          readOnly: true
        }}
      />
      <TextField
        disabled={true}
        id="artnumber-sm1223"
        label="Article number"
        defaultValue={artNumber}
        InputProps={{
          readOnly: true
        }}
      />
      <TextField
        sx={{ display: 'none' }}
        disabled={true}
        id="fwver-sm1223"
        label="Firmware version"
        defaultValue={fwVersion}
        InputProps={{
          readOnly: true
        }}
      />
    </Stack>
  );
}
