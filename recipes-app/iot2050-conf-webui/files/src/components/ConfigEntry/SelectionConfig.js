/* eslint-disable react/prop-types */
import * as React from 'react';
import MenuItem from '@mui/material/MenuItem';
import TextField from '@mui/material/TextField';

const doNothing = (event) => {};

export default function SelectionConfig ({ id, data, updateConfig, disabled = false, postChange = doNothing }) {
  const onChange = (event) => {
    data.value = event.target.value;
    postChange(event);
    updateConfig();
  };

  return (
    <TextField
      sx={{ mt: 1 }}
      id={id}
      select
      disabled={disabled}
      label={data.label}
      value={data.value}
      onChange={onChange}
      name={id}
    >
      {data.selection.map((option) => (
        <MenuItem key={option} value={option}>
          {option}
        </MenuItem>
      ))}
    </TextField>
  );
}
