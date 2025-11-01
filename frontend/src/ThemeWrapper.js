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
        // Modern gradient-inspired color palette
        primary: {
            main: mode === 'light' ? '#6366f1' : '#818cf8', // Indigo
            light: mode === 'light' ? '#818cf8' : '#a5b4fc',
            dark: mode === 'light' ? '#4f46e5' : '#6366f1',
        },
        secondary: {
            main: mode === 'light' ? '#8b5cf6' : '#a78bfa', // Purple
            light: mode === 'light' ? '#a78bfa' : '#c4b5fd',
            dark: mode === 'light' ? '#7c3aed' : '#8b5cf6',
        },
        error: {
            main: mode === 'light' ? '#ef4444' : '#f87171',
            dark: mode === 'light' ? '#dc2626' : '#ef4444',
        },
        success: {
            main: mode === 'light' ? '#10b981' : '#34d399',
        },
        warning: {
            main: mode === 'light' ? '#f59e0b' : '#fbbf24',
        },
        info: {
            main: mode === 'light' ? '#3b82f6' : '#60a5fa',
        },
        background: {
            default: mode === 'light' ? '#f8fafc' : '#0f172a', // Slate
            paper: mode === 'light' ? '#ffffff' : '#1e293b',
        },
        text: {
             primary: mode === 'light' ? '#1e293b' : '#f1f5f9',
             secondary: mode === 'light' ? '#64748b' : '#94a3b8',
        },
        divider: mode === 'light' ? '#e2e8f0' : '#334155',
    },
    components: {
        MuiCssBaseline: {
            styleOverrides: (theme) => ({
                body: {
                    backgroundColor: theme.palette.background.default,
                    margin: 0,
                    padding: 0,
                },
                html: {
                    backgroundColor: theme.palette.background.default,
                    minHeight: '100vh',
                    width: '100%',
                    margin: 0,
                    padding: 0,
                },
                '#root': {
                    minHeight: '100vh',
                    width: '100%',
                    margin: 0,
                    padding: 0,
                },
                '*': {
                    boxSizing: 'border-box',
                },
            }),
        },
        MuiAppBar: { 
            styleOverrides: { 
                root: { 
                    boxShadow: mode === 'light' 
                        ? '0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24)'
                        : '0 1px 3px rgba(0, 0, 0, 0.3), 0 1px 2px rgba(0, 0, 0, 0.4)',
                    background: mode === 'light'
                        ? 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)'
                        : 'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
                } 
            } 
        },
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