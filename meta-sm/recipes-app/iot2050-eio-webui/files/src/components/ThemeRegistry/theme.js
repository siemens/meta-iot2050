import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      light: '#d8ffef',
      main: '#007993',
      dark: '#0cc',
      contrastText: '#fff'
    },
    secondary: {
      light: '#ff7961',
      main: '#fff',
      dark: '#000028',
      contrastText: '#000'
    }
  },
  typography: {
    fontFamily: 'Siemens Sans, Arial, sans-serif'
  },
  components: {
    MuiAlert: {
      styleOverrides: {
        root: ({ ownerState }) => ({
          ...(ownerState.severity === 'info' && {
            backgroundColor: '#00ffb9'
          })
        })
      }
    }
  }
});

export default theme;
