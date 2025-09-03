import localFont from 'next/font/local';
import { createTheme } from '@mui/material/styles';

const siemensSans = localFont({
  src: [
    {
      path: './fonts/SiemensSans_Prof_Roman.woff2',
      weight: '400',
      style: 'normal'
    },
    {
      path: './fonts/SiemensSans_Prof_Italic.woff2',
      weight: '400',
      style: 'italic'
    },
    {
      path: './fonts/SiemensSans_Prof_Bold.woff2',
      weight: '700',
      style: 'normal'
    },
    {
      path: './fonts/SiemensSans_Prof_BoldItalic.woff2',
      weight: '700',
      style: 'italic'
    }
  ]
});

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
    fontFamily: siemensSans.style.fontFamily
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
