/* eslint-disable react/prop-types */
import * as React from 'react';
import localFont from 'next/font/local';
import './globals.css';

const siemensSans = localFont({
  src: [
    {
      path: '../components/ThemeRegistry/fonts/SiemensSans_Prof_Roman.woff2',
      weight: '400',
      style: 'normal'
    },
    {
      path: '../components/ThemeRegistry/fonts/SiemensSans_Prof_Italic.woff2',
      weight: '400',
      style: 'italic'
    },
    {
      path: '../components/ThemeRegistry/fonts/SiemensSans_Prof_Bold.woff2',
      weight: '700',
      style: 'normal'
    },
    {
      path: '../components/ThemeRegistry/fonts/SiemensSans_Prof_BoldItalic.woff2',
      weight: '700',
      style: 'italic'
    }
  ],
  display: 'swap'
});

export const metadata = {
  title: 'IOT2050 Extended IO',
  description: 'IOT2050 Extended IO Cockpit plugin'
};

export default function RootLayout ({ children }) {
  return (
    <html lang="en" className={siemensSans.className}>
      <head>
        <script src="../base1/cockpit.js"></script>
      </head>
      <body>{children}</body>
    </html>
  );
}
