// frontend/src/ThemeWrapper.js (FINAL, LIGHT MODE DEFAULT)

import React, { useMemo, useState, createContext } from 'react';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import createCache from '@emotion/cache';
import { CacheProvider } from '@emotion/react';

const muiCache = createCache({
  key: 'mui',
  stylisPlugins: [],
});

export const ColorModeContext = createContext({ toggleColorMode: () => {} });

const getAppTheme = (mode) => createTheme({
    palette: {
        mode,
        // --- CALM GRAY & TEAL PALETTE (Aesthetic Colors) ---
        primary: {
            main: mode === 'light' ? '#5C6BC0' : '#A1C4FD',
        },
        secondary: {
            main: mode === 'light' ? '#9AA4AE' : '#B8C1CD',
        },
        error: {
            main: mode === 'light' ? '#E53E33' : '#FF7E75',
            dark: mode === 'light' ? '#B02F28' : '#CC635D',
        },
        success: {
            main: mode === 'light' ? '#38B249' : '#74D97D',
        },
        warning: {
            main: mode === 'light' ? '#FFC107' : '#FFD54F',
        },
        info: {
            main: mode === 'light' ? '#2196F3' : '#64B5F6',
        },
        background: {
            default: mode === 'light' ? '#F0F3F7' : '#1C2025',
            paper: mode === 'light' ? '#FFFFFF' : '#282C34',
        },
        text: {
             primary: mode === 'light' ? '#212B36' : '#E0E5EB',
             secondary: mode === 'light' ? '#6C757D' : '#9FA7B3',
        },
        divider: mode === 'light' ? '#D1D9E0' : '#39404B',
    },
    components: {
        MuiCssBaseline: {
            styleOverrides: (theme) => ({
                body: {
                    backgroundColor: theme.palette.background.default,
                },
                html: {
                    backgroundColor: theme.palette.background.default,
                    minHeight: '100vh',
                },
                '#root': {
                    minHeight: '100vh',
                },
            }),
        },
        MuiAppBar: { styleOverrides: { root: { boxShadow: 'none' } } },
        MuiCard: { styleOverrides: { root: { borderRadius: '12px', transition: 'background-color 0.3s ease-in-out', border: 'none' } } },
        MuiTypography: { styleOverrides: { root: { color: mode === 'light' ? '#212B36' : '#E0E5EB' } } },
        MuiPaper: { styleOverrides: { root: { backgroundColor: mode === 'light' ? '#FFFFFF' : '#282C34' } } }
    }
});

const ThemeWrapper = ({ children }) => {
    // CRITICAL FIX: Initial state changed to 'light'
    const [mode, setMode] = useState('light');

    const colorMode = useMemo(
        () => ({
            toggleColorMode: () => {
                setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
            },
        }),
        [],
    );

    const theme = useMemo(() => getAppTheme(mode), [mode]);

    return (
        <ColorModeContext.Provider value={colorMode}>
            <CacheProvider value={muiCache}>
                <ThemeProvider theme={theme}>
                    <CssBaseline />
                    {children}
                </ThemeProvider>
            </CacheProvider>
        </ColorModeContext.Provider>
    );
};

export default ThemeWrapper;