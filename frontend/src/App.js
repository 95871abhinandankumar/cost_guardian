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
import ITDashboard from "./pages/ITDashboard";
import { ColorModeContext } from "./ThemeWrapper";


// Placeholder components
const PlaceholderDashboard = ({ name }) => (
    <Box sx={{ p: 5, textAlign: 'center', bgcolor: 'background.paper', borderRadius: '12px' }}>
        <Typography variant="h4" color="primary">
            {name} Dashboard
        </Typography>
        <Typography color="text.secondary">
            Content coming soon. Currently focused on IT Dashboard development.
        </Typography>
    </Box>
);

function App() {
  const [open, setOpen] = useState(false);
  const location = useLocation();
  const theme = useTheme();
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
          <Route path="/" element={<ITDashboard />} />
          <Route path="/it" element={<ITDashboard />} />
          <Route path="/finance" element={<PlaceholderDashboard name="Finance" />} />
          <Route path="/msp" element={<PlaceholderDashboard name="MSP" />} />
        </Routes>
      </Box>
    </Box>
  );
}

const AppWrapper = () => (
    <Router>
        <App />
    </Router>
)

export default AppWrapper;