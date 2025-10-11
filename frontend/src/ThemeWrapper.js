// frontend/src/ThemeWrapper.js (FINAL AESTHETIC: Calm Gray & Teal Palette)

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
        // --- CALM GRAY & TEAL PALETTE ---
        primary: {
            // Teal Accent for Lines, App Bar, and Primary Data
            main: mode === 'light' ? '#00A389' : '#2DE6CA',
        },
        secondary: {
            // Subtle grey for secondary actions
            main: mode === 'light' ? '#9AA4AE' : '#B0B0B0',
        },
        error: {
            // Soft Salmon Red/Pink for Critical (Low Luminosity Red)
            main: mode === 'light' ? '#E53E33' : '#FF7E75',
            dark: mode === 'light' ? '#B02F28' : '#CC635D',
        },
        success: {
            // Bright Mint Green for Savings/ROI
            main: mode === 'light' ? '#38B249' : '#74D97D',
        },
        warning: {
            // Amber for Utilization Thresholds
            main: mode === 'light' ? '#FFC107' : '#FFD54F',
        },
        info: {
            // Standard light blue for general info/subtle dots
            main: mode === 'light' ? '#2196F3' : '#64B5F6',
        },
        background: {
            // Soft Charcoal/Blue Base (Canvas background)
            default: mode === 'light' ? '#F0F3F7' : '#1C2025',
            // Card/Chart backgrounds: Slightly lighter for layering
            paper: mode === 'light' ? '#FFFFFF' : '#282C34',
        },
        text: {
             primary: mode === 'light' ? '#212B36' : '#E0E5EB', // Deep Charcoal vs Soft White
             secondary: mode === 'light' ? '#6C757D' : '#9FA7B3',
        },
        divider: mode === 'light' ? '#D1D9E0' : '#39404B', // Subtle, dark grid line
    },
    components: {
        // --- CRITICAL FIX: FORCES THEME BACKGROUND ONTO THE HTML BODY ---
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
        // --- End of CRITICAL FIX ---
        MuiAppBar: { styleOverrides: { root: { boxShadow: 'none' } } },
        MuiCard: { styleOverrides: { root: { borderRadius: '12px', transition: 'background-color 0.3s ease-in-out', border: 'none' } } },
        MuiTypography: { styleOverrides: { root: { color: mode === 'light' ? '#1A1A1A' : '#EAEAEA' } } },
        MuiPaper: { styleOverrides: { root: { backgroundColor: mode === 'light' ? '#FFFFFF' : '#282C34' } } }
    }
});

const ThemeWrapper = ({ children }) => {
    const [mode, setMode] = useState('dark');

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