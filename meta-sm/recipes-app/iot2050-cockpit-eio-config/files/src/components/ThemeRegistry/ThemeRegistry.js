/* eslint-disable react/prop-types */
'use client';

import * as React from 'react';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import GlobalStyles from '@mui/material/GlobalStyles';
import createAppTheme from './theme';
import siemensSansRoman from './fonts/SiemensSans_Prof_Roman.woff2';
import siemensSansItalic from './fonts/SiemensSans_Prof_Italic.woff2';
import siemensSansBold from './fonts/SiemensSans_Prof_Bold.woff2';
import siemensSansBoldItalic from './fonts/SiemensSans_Prof_BoldItalic.woff2';

function getAssetUrl (asset) {
  const url = typeof asset === 'string' ? asset : asset.src;

  if (url.startsWith('/')) {
    return `.${url}`;
  }

  return url;
}

export default function ThemeRegistry ({ children }) {
  const [mode, setMode] = React.useState('light');

  React.useEffect(() => {
    const media = window.matchMedia('(prefers-color-scheme: dark)');
    const apply = (style) => {
      const selected = style || window.localStorage.getItem('shell:style') || 'auto';
      const dark = selected === 'dark' || (selected === 'auto' && media.matches);
      document.documentElement.classList.toggle('pf-v6-theme-dark', dark);
      document.documentElement.dataset.cockpitTheme = dark ? 'dark' : 'light';
      document.documentElement.style.colorScheme = dark ? 'dark' : 'light';
      setMode(dark ? 'dark' : 'light');
    };
    const onStorage = (event) => {
      if (event.key === 'shell:style') apply(event.newValue);
    };
    const onCockpitStyle = (event) => apply(event.detail?.style);
    const onMedia = () => apply();
    apply();
    window.addEventListener('storage', onStorage);
    window.addEventListener('cockpit-style', onCockpitStyle);
    media.addEventListener('change', onMedia);
    return () => {
      window.removeEventListener('storage', onStorage);
      window.removeEventListener('cockpit-style', onCockpitStyle);
      media.removeEventListener('change', onMedia);
    };
  }, []);

  const theme = React.useMemo(() => createAppTheme(mode), [mode]);
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <GlobalStyles styles={`
        @font-face {
          font-family: 'Siemens Sans';
          src: url('${getAssetUrl(siemensSansRoman)}') format('woff2');
          font-weight: 400;
          font-style: normal;
        }

        @font-face {
          font-family: 'Siemens Sans';
          src: url('${getAssetUrl(siemensSansItalic)}') format('woff2');
          font-weight: 400;
          font-style: italic;
        }

        @font-face {
          font-family: 'Siemens Sans';
          src: url('${getAssetUrl(siemensSansBold)}') format('woff2');
          font-weight: 700;
          font-style: normal;
        }

        @font-face {
          font-family: 'Siemens Sans';
          src: url('${getAssetUrl(siemensSansBoldItalic)}') format('woff2');
          font-weight: 700;
          font-style: italic;
        }
      `} />
      {children}
    </ThemeProvider>
  );
}
