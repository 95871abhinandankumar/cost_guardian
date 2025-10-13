// src/App.js (FINAL VERSION)

import React, { useState, useContext } from "react";
import {
  Box,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  AppBar,
  Toolbar,
  Typography,
  useTheme,
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import Brightness4Icon from "@mui/icons-material/Brightness4";
import Brightness7Icon from "@mui/icons-material/Brightness7";

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
    { text: "IT Dashboard", path: "/it" },
    { text: "Finance Dashboard", path: "/finance" },
    { text: "MSP Dashboard", path: "/msp" },
  ];

  return (
    // FINAL FIX: Apply dynamic background and full height to the main wrapper
    <Box
        sx={{
            flexGrow: 1,
            minHeight: '100vh',
            bgcolor: theme.palette.background.default // Applies aesthetic theme background color
        }}
    >
      <AppBar position="static" sx={{ background: theme.palette.primary.main }}>
        <Toolbar>
          <IconButton
            size="large"
            edge="start"
            color="inherit"
            onClick={toggleDrawer(true)}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>

          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Cost Guardian
          </Typography>

          {/* Dark Mode Toggle Button */}
          <IconButton
            sx={{ ml: 1 }}
            onClick={colorMode.toggleColorMode}
            color="inherit"
            title={theme.palette.mode === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {theme.palette.mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
          </IconButton>
        </Toolbar>
      </AppBar>

      {/* Sidebar Drawer */}
      <Drawer anchor="left" open={open} onClose={toggleDrawer(false)}>
        <Box sx={{ width: 250 }} onClick={toggleDrawer(false)} role="presentation">
          <List>
            {dashboardLinks.map((item) => (
              <ListItem
                key={item.text}
                disablePadding
                component={RouterLink}
                to={item.path}
                // Highlight the selected dashboard in the menu
                selected={location.pathname === item.path}
              >
                <ListItemButton>
                  <ListItemText primary={item.text} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>

      {/* Dashboard content controlled by React Router */}
      <Box sx={{ p: 3 }}>
        <Routes>
          {/* Default path (/) and IT Dashboard */}
          <Route path="/" element={<ITDashboard />} />
          <Route path="/it" element={<ITDashboard />} />

          {/* INTEGRATED: Finance Dashboard */}
          <Route path="/finance" element={<FinanceDashboard />} />

          {/* FINAL INTEGRATION: MSP Dashboard */}
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