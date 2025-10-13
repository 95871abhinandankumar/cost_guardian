// frontend/src/components/ClientPrioritizationTable.tsx (FINAL, ERROR-FREE VERSION)

import React from 'react';
import {
    Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
    Paper, Typography, Box, useTheme, Chip,
    // Removed unused ThemeProvider/createTheme imports
} from '@mui/material';
// CRITICAL FIX: Import the core Theme type from MUI's styles, and SxProps from system
import { Theme } from '@mui/material/styles';
import { SxProps } from '@mui/system';


// Interfaces remain the same
interface ClientSummary {
    client_name: string;
    total_spend: number;
    total_potential_savings: number;
    tagging_compliance: number;
}

interface ClientPrioritizationTableProps {
    data: ClientSummary[];
}

// Function to generate the header styles with correct typing
const getHeaderStyles = (theme: Theme): SxProps<Theme> => ({
    // FIX: Using theme properties ensures correct type assignment
    color: theme.palette.text.secondary,
    fontWeight: theme.typography.fontWeightBold,
    textTransform: 'uppercase',
    fontSize: '0.75rem',
    borderBottom: `2px solid ${theme.palette.divider}`,
});


const ClientPrioritizationTable: React.FC<ClientPrioritizationTableProps> = ({ data }) => {
    const theme = useTheme();

    // FIX: Call the function to generate the correctly typed style object
    const headerStyle = getHeaderStyles(theme);

    return (
        <Paper
            elevation={6}
            sx={{
                p: 2,
                bgcolor: theme.palette.background.paper,
                borderRadius: '12px',
                overflowX: 'auto'
            }}
        >
            <Typography variant="h5" sx={{ mb: 2, color: theme.palette.text.primary }}>
                Client Prioritization Table (Top Waste)
            </Typography>

            <TableContainer component={Box}>
                <Table size="small" sx={{ borderCollapse: 'separate', borderSpacing: '0 4px' }}>
                    <TableHead>
                        <TableRow>
                            {/* Apply styling using the correctly generated object */}
                            <TableCell sx={headerStyle}>Client</TableCell>
                            <TableCell sx={headerStyle} align="right">Total Spend ($)</TableCell>
                            <TableCell sx={headerStyle} align="right">Savings Potential ($)</TableCell>
                            <TableCell sx={headerStyle} align="right">Tagging Compliance %</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {data.map((row, index) => (
                            <TableRow
                                key={row.client_name}
                                // Apply subtle background color for the highest ROI row
                                sx={{
                                    bgcolor: index === 0 ? theme.palette.action.selected : theme.palette.background.paper,
                                    '&:hover': { bgcolor: theme.palette.action.hover }
                                }}
                            >
                                <TableCell sx={{ color: theme.palette.text.primary, borderBottom: 'none' }}>{row.client_name}</TableCell>

                                {/* Numeric data alignment */}
                                <TableCell sx={{ color: theme.palette.text.primary, borderBottom: 'none' }} align="right">${row.total_spend.toFixed(0)}</TableCell>

                                <TableCell sx={{ color: theme.palette.success.main, fontWeight: 'bold', borderBottom: 'none' }} align="right">
                                    ${row.total_potential_savings.toFixed(0)}
                                </TableCell>

                                <TableCell sx={{ borderBottom: 'none' }} align="right">
                                    {/* Use Warning/Primary colors for aesthetic compliance flag */}
                                    <Chip
                                        label={`${row.tagging_compliance.toFixed(0)}%`}
                                        color={row.tagging_compliance < 85 ? 'warning' : 'primary'}
                                        size="small"
                                    />
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </Paper>
    );
};

export default ClientPrioritizationTable;