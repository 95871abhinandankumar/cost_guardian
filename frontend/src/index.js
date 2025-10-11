// frontend/src/index.js 

import React from 'react';
import ReactDOM from 'react-dom/client';
// ❌ CONFLICT FIX: Removed the import of './index.css' as styles are now in public/index.html
// import './index.css';

// Import AppWrapper (which contains the Router and App components)
import AppWrapper from './App';
import ThemeWrapper from "./ThemeWrapper";
import { QueryClient, QueryClientProvider } from 'react-query';

const queryClient = new QueryClient();

const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    {/* 1. QUERY CLIENT: Essential for data fetching and Continuous Monitoring */}
    <QueryClientProvider client={queryClient}>

      {/* 2. THEME WRAPPER: Essential for MUI styling and aesthetic control */}
      <ThemeWrapper>
        {/* FIX: Use the component exported from App.js */}
        <AppWrapper />
      </ThemeWrapper>

    </QueryClientProvider>
  </React.StrictMode>
);