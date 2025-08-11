import * as React from 'react';
import Box from '@mui/material/Box';
import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';

export default function HomePage () {
  return (
    <Box
      sx={{
        display: 'flex'
      }}
    >
      <Box>
        <Alert severity="info" sx={{ mt: 2, mb: 5 }}>
          <AlertTitle>IOT2050 SETUP 👋</AlertTitle>
          https://github.com/siemens/meta-iot2050
        </Alert>
      </Box>
    </Box>
  );
}
