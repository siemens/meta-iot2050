/* eslint-disable react/prop-types */
'use client';

import * as React from 'react';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import GlobalStyles from '@mui/material/GlobalStyles';
import theme from './theme';
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
