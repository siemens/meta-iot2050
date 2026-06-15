/* eslint-disable react/prop-types */
import * as React from 'react';
import FormLabel from '@mui/material/FormLabel';
import Typography from '@mui/material/Typography';

export default function ConfigGroupLabel ({ label }) {
  return (
    <FormLabel>
      <Typography
        sx={{ fontWeight: 'bold', lineHeight: 2, textTransform: 'uppercase' }}
        variant="h6"
      >
        {label}
      </Typography>
    </FormLabel>
  );
}
