/* eslint-disable react/prop-types */
import * as React from 'react';
import Box from '@mui/material/Box';
import InputAdornment from '@mui/material/InputAdornment';
import { styled } from '@mui/material/styles';
import Typography from '@mui/material/Typography';
import Grid from '@mui/material/Grid';
import Slider from '@mui/material/Slider';
import MuiInput from '@mui/material/Input';

const Input = styled(MuiInput)`
  width: 100px;
`;

const doNothing = (id) => {};

export default function SliderConfig ({ id, data, unit, updateConfig, disabled = false, postChange = doNothing }) {
  const onChangeSlider = (event, newValue) => {
    data.value = newValue;
    postChange(id);
    updateConfig();
  };

  const onChangeInput = (event) => {
    data.value = event.target.value === '' ? 0 : Number(event.target.value);
    postChange(id);
    updateConfig();
  };

  const onBlurInput = () => {
    if (data.value < data.min) {
      data.value = data.min;
    } else if (data.value > data.max) {
      data.value = data.max;
    }
    postChange(id);
    updateConfig();
  };

  return (
    <Box sx={{ width: 300 }}>
    <Typography id={id + '-slider'} gutterBottom>
      {data.label}
    </Typography>
    <Grid container spacing={2} alignItems="center">
      <Grid item xs>
        <Slider
          step={1}
          disabled={disabled}
          min={data.min}
          max={data.max}
          value={typeof data.value === 'number' ? data.value : 0}
          onChange={onChangeSlider}
          aria-labelledby="line-vol-tol-slider"
        />
      </Grid>
      <Grid item>
        <Input
          endAdornment={<InputAdornment position="end">{unit}</InputAdornment>}
          disabled={disabled}
          value={data.value}
          size="small"
          onChange={onChangeInput}
          onBlur={onBlurInput}
          inputProps={{
            min: data.min,
            max: data.max,
            type: 'number',
            'aria-labelledby': 'line-vol-tol-slider'
          }}
        />
      </Grid>
    </Grid>
  </Box>
  );
}
