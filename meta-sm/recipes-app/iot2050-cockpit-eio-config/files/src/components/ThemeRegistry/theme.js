import { createTheme } from '@mui/material/styles';

const light = {
  background: '#f0f0f0',
  surface: '#ffffff',
  text: '#151515',
  muted: '#6a6e73',
  border: '#d2d2d2',
  primary: '#0066cc',
  primaryDark: '#004d99'
};

const tokenNames = {
  background: '--pf-t--global--background--color--primary--default',
  surface: '--pf-t--global--background--color--secondary--default',
  text: '--pf-t--global--text--color--regular',
  muted: '--pf-t--global--text--color--subtle',
  border: '--pf-t--global--border--color--default',
  primary: '--pf-t--global--color--brand--default',
  primaryDark: '--pf-t--global--color--brand--hover'
};

const dark = {
  background: '#151515',
  surface: '#212121',
  text: '#f5f5f5',
  muted: '#b8bbbe',
  border: '#4f5255',
  primary: '#73bcf7',
  primaryDark: '#bee1f7'
};

function readCockpitColors (mode) {
  const fallback = mode === 'dark' ? dark : light;
  if (typeof window === 'undefined') return fallback;
  const probe = document.createElement('span');
  probe.hidden = true;
  document.body.appendChild(probe);
  const read = (name, fallbackValue) => {
    probe.style.color = `var(${name}, ${fallbackValue})`;
    const value = getComputedStyle(probe).color;
    probe.style.removeProperty('color');
    return value && value !== 'rgba(0, 0, 0, 0)' ? value : fallbackValue;
  };
  const colors = Object.fromEntries(Object.entries(tokenNames).map(([name, token]) => [name, read(token, fallback[name])]));
  probe.remove();
  return colors;
}

export default function createAppTheme (mode = 'light') {
  const colors = readCockpitColors(mode);
  return createTheme({
    palette: {
      mode,
      primary: { light: colors.primary, main: colors.primary, dark: colors.primaryDark, contrastText: mode === 'dark' ? '#151515' : '#fff' },
      background: { default: colors.background, paper: colors.surface },
      text: { primary: colors.text, secondary: colors.muted },
      divider: colors.border
    },
    typography: { fontFamily: 'Siemens Sans, Arial, sans-serif' },
    components: {
      MuiCssBaseline: {
        styleOverrides: { body: { backgroundColor: colors.background, color: colors.text } }
      },
      MuiAlert: {
        styleOverrides: { root: { borderRadius: 6 } }
      },
      MuiButton: {
        styleOverrides: { root: { borderRadius: 6, textTransform: 'none', boxShadow: 'none', fontWeight: 600 } }
      },
      MuiPaper: {
        styleOverrides: { root: { backgroundColor: colors.surface, border: `1px solid ${colors.border}`, borderRadius: 6, boxShadow: '0 4px 16px rgba(20,45,55,.08)' } }
      },
      MuiAppBar: {
        styleOverrides: { root: { backgroundColor: colors.surface, color: colors.text, borderBottom: `1px solid ${colors.border}` } }
      },
      MuiContainer: {
        styleOverrides: { root: { backgroundColor: 'transparent' } }
      }
    }
  });
}
