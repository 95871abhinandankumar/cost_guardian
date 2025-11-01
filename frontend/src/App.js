// src/App.js (FINAL VERSION)

import React, { useState, useContext } from "react";
import {
  Box,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  AppBar,
  Toolbar,
  Typography,
  useTheme,
  alpha,
  Divider,
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import Brightness4Icon from "@mui/icons-material/Brightness4";
import Brightness7Icon from "@mui/icons-material/Brightness7";
import DashboardIcon from "@mui/icons-material/Dashboard";
import AccountBalanceIcon from "@mui/icons-material/AccountBalance";
import BusinessIcon from "@mui/icons-material/Business";
import CloseIcon from "@mui/icons-material/Close";

import { BrowserRouter as Router, Routes, Route, Link as RouterLink, useLocation } from "react-router-dom";

// Import all three final dashboard components
import ITDashboard from "./pages/ITDashboard";
import FinanceDashboard from "./pages/FinanceDashboard";
import MSPDashboard from "./pages/MSPDashboard";

// CRITICAL IMPORT: The context that holds the toggle function
import { ColorModeContext } from "./ThemeWrapper";


function App() {
  const [open, setOpen] = useState(false);
  const location = useLocation();
  const theme = useTheme();
  // Access the color mode toggle function from the context
  const colorMode = useContext(ColorModeContext);

  const toggleDrawer = (openState) => () => setOpen(openState);

  const dashboardLinks = [
    { text: "IT Dashboard", path: "/it", icon: DashboardIcon },
    { text: "Finance Dashboard", path: "/finance", icon: AccountBalanceIcon },
    { text: "MSP Dashboard", path: "/msp", icon: BusinessIcon },
  ];

  return (
    <Box
        sx={{
            display: 'flex',
            flexDirection: 'column',
            minHeight: '100vh',
            width: '100%',
            bgcolor: theme.palette.background.default,
        }}
    >
      {/* Modern AppBar */}
      <AppBar 
        position="fixed" 
        sx={{ 
          zIndex: (theme) => theme.zIndex.drawer + 1,
          backdropFilter: 'blur(20px)',
          backgroundColor: alpha(theme.palette.primary.main, 0.95),
        }}
      >
        <Toolbar sx={{ px: { xs: 2, sm: 3 } }}>
          <IconButton
            size="large"
            edge="start"
            color="inherit"
            onClick={toggleDrawer(true)}
            sx={{ 
              mr: 2,
              '&:hover': {
                bgcolor: alpha('#ffffff', 0.1),
              }
            }}
          >
            <MenuIcon />
          </IconButton>

          <Typography 
            variant="h6" 
            sx={{ 
              flexGrow: 1,
              fontWeight: 700,
              fontSize: { xs: '1.1rem', sm: '1.25rem' },
              letterSpacing: 0.5,
            }}
          >
            Cost Guardian
          </Typography>

          {/* Dark Mode Toggle Button */}
          <IconButton
            onClick={colorMode.toggleColorMode}
            color="inherit"
            sx={{ 
              '&:hover': {
                bgcolor: alpha('#ffffff', 0.1),
              }
            }}
            title={theme.palette.mode === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {theme.palette.mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Modern Sidebar Drawer */}
      <Drawer 
        anchor="left" 
        open={open} 
        onClose={toggleDrawer(false)}
        PaperProps={{
          sx: {
            width: 280,
            bgcolor: theme.palette.mode === 'light' 
              ? alpha(theme.palette.background.paper, 0.95)
              : alpha(theme.palette.background.paper, 0.98),
            backdropFilter: 'blur(20px)',
            borderRight: `1px solid ${alpha(theme.palette.divider, 0.5)}`,
          }
        }}
      >
        <Box sx={{ pt: 8 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', px: 2, pb: 2 }}>
            <Typography variant="h6" sx={{ fontWeight: 700, color: theme.palette.primary.main }}>
              Dashboards
            </Typography>
            <IconButton
              size="small"
              onClick={toggleDrawer(false)}
              sx={{
                color: theme.palette.text.secondary,
                '&:hover': {
                  bgcolor: alpha(theme.palette.error.main, 0.1),
                }
              }}
            >
              <CloseIcon />
            </IconButton>
          </Box>
          <Divider sx={{ mb: 1 }} />
          <List>
            {dashboardLinks.map((item) => {
              const Icon = item.icon;
              const isSelected = location.pathname === item.path || (item.path === '/it' && location.pathname === '/');
              return (
                <ListItem
                  key={item.text}
                  disablePadding
                  sx={{ mb: 0.5, px: 1 }}
                >
                  <ListItemButton
                    component={RouterLink}
                    to={item.path}
                    onClick={toggleDrawer(false)}
                    selected={isSelected}
                    sx={{
                      borderRadius: 2,
                      '&.Mui-selected': {
                        bgcolor: alpha(theme.palette.primary.main, 0.15),
                        color: theme.palette.primary.main,
                        '&:hover': {
                          bgcolor: alpha(theme.palette.primary.main, 0.2),
                        },
                        '& .MuiListItemIcon-root': {
                          color: theme.palette.primary.main,
                        },
                      },
                      '&:hover': {
                        bgcolor: alpha(theme.palette.primary.main, 0.08),
                      },
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      <Icon />
                    </ListItemIcon>
                    <ListItemText 
                      primary={item.text}
                      primaryTypographyProps={{
                        fontWeight: isSelected ? 600 : 500,
                        fontSize: '0.95rem',
                      }}
                    />
                  </ListItemButton>
                </ListItem>
              );
            })}
          </List>
        </Box>
      </Drawer>

      {/* Dashboard content with top padding for fixed AppBar */}
      <Box 
        component="main"
        sx={{ 
          flexGrow: 1,
          pt: '64px', // AppBar height
          width: '100%',
          minHeight: 'calc(100vh - 64px)',
        }}
      >
        <Routes>
          <Route path="/" element={<ITDashboard />} />
          <Route path="/it" element={<ITDashboard />} />
          <Route path="/finance" element={<FinanceDashboard />} />
          <Route path="/msp" element={<MSPDashboard />} />
        </Routes>
      </Box>
    </Box>
  );
}

// AppWrapper handles the routing setup and is exported for index.js
const AppWrapper = () => (
    <Router>
        <App />
    </Router>
)

export default AppWrapper;