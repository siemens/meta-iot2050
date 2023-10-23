/* eslint-disable react/prop-types */
import * as React from 'react';
import Checkbox from '@mui/material/Checkbox';
import FormControlLabel from '@mui/material/FormControlLabel';

export default function CheckConfig ({ id, data, updateConfig, disabled = false }) {
  const onChange = (event) => {
    data.value = event.target.checked;
    updateConfig();
  };

  return (
    <FormControlLabel
      disabled={disabled}
      label={data.label}
      control={<Checkbox
        checked={data.value}
        onChange={onChange}
        id={id}
        name={id}
      />}
    />
  );
}
