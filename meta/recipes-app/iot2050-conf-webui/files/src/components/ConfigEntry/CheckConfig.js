/* eslint-disable react/prop-types */
import * as React from 'react';
import Checkbox from '@mui/material/Checkbox';
import FormControlLabel from '@mui/material/FormControlLabel';

const doNothing = (id) => {};

export default function CheckConfig ({ id, data, updateConfig, disabled = false, postChange = doNothing }) {
  const setNewValue = (newValue) => {
    data.value = newValue;
    postChange(id);
    updateConfig();
  };

  const onChange = (event) => {
    setNewValue(event.target.checked);
  };

  /* When disabled, the value should be setting to false */
  React.useEffect(() => {
    if (disabled) {
      setNewValue(false);
    }
  }, [disabled]);

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
