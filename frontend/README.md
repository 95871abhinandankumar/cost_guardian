# Cost Guardian Frontend

A modern, responsive React application for visualizing and managing cloud cost analytics with AI-powered insights and interactive dashboards.

## Overview

Cost Guardian Frontend is a sophisticated web application built with React and Material-UI that provides comprehensive cloud cost monitoring, analysis, and optimization tools. The application features multiple role-based dashboards, advanced data visualization, and real-time cost analytics.

## Features

### Dashboard Views

- **IT Dashboard**: Technical metrics, utilization tracking, and infrastructure insights
- **Finance Dashboard**: Financial analytics, cost trends, and budget management
- **MSP Dashboard**: Multi-tenant view with client prioritization and service metrics

### Data Visualization

- **Cost Trend Charts**: Historical cost tracking with interactive line charts
- **Cost Allocation**: Service and account-level breakdown with donut charts
- **Anomaly Detection**: Scatter plots for identifying unusual cost patterns
- **Utilization Metrics**: Resource utilization tracking over time
- **Client Value Analysis**: Line charts for client engagement and value metrics
- **Governance Metrics**: Compliance and governance visualization

### User Experience

- **Modern UI**: Material-UI (MUI) components with professional design
- **Dark/Light Theme**: User-selectable color scheme with system preference detection
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Interactive Charts**: Nivo charts with hover interactions and tooltips
- **Real-time Updates**: React Query for efficient data fetching and caching
- **Navigation**: React Router with smooth page transitions

### Advanced Features

- **Action Queue**: Queue and manage cost optimization actions
- **Client Prioritization**: Intelligent ranking tables with sorting and filtering
- **Savings Prioritization**: Tables for tracking and prioritizing cost savings opportunities
- **Dynamic Filtering**: Date range filters and account selection
- **Export Capabilities**: Data export for reporting and analysis

## Technology Stack

- **React 18.2**: Modern React with hooks and functional components
- **TypeScript**: Type-safe development (partial migration)
- **Material-UI (MUI) 5.15**: Professional component library
- **React Router 6.21**: Client-side routing
- **React Query 3.39**: Data fetching and state management
- **Nivo Charts**: Beautiful, responsive data visualization
- **Emotion**: CSS-in-JS styling solution

## Project Structure

```
frontend/
├── public/
│   ├── index.html                # HTML template
│   └── manifest.json             # PWA manifest
│
├── src/
│   ├── App.js                    # Main application component
│   ├── App.css                   # Application styles
│   ├── index.js                  # Application entry point
│   ├── index.css                 # Global styles
│   │
│   ├── components/               # Reusable UI components
│   │   ├── Header.js             # Application header
│   │   ├── ActionQueue/          # Action queue components
│   │   │   ├── ActionButton.tsx
│   │   │   └── ActionQueueList.tsx
│   │   ├── NivoCharts/           # Chart components
│   │   │   ├── CostTrendChart.tsx
│   │   │   ├── CostAllocationChart.tsx
│   │   │   ├── AnomalyScatterPlot.tsx
│   │   │   ├── UtilizationLineChart.tsx
│   │   │   ├── ClientValueLineChart.tsx
│   │   │   └── GovernanceDonutChart.tsx
│   │   ├── ClientPrioritizationTable.tsx
│   │   └── SavingsPrioritizationTable.tsx
│   │
│   ├── pages/                    # Page components
│   │   ├── ITDashboard.tsx       # IT-focused dashboard
│   │   ├── FinanceDashboard.tsx  # Finance-focused dashboard
│   │   ├── MSPDashboard.tsx      # MSP-focused dashboard
│   │   └── Dashboard.js          # Legacy dashboard (if present)
│   │
│   ├── services/                 # API service layer
│   │   ├── api.js                # API client configuration
│   │   ├── metricsService.js     # Metrics API calls
│   │   └── ...                   # Other service modules
│   │
│   ├── hooks/                    # Custom React hooks
│   │   └── index.js              # Hook exports
│   │
│   ├── context/                  # React Context providers
│   │                           # Theme and state management
│   │
│   ├── utils/                    # Utility functions
│   │   └── index.js              # Helper utilities
│   │
│   ├── assets/                   # Static assets
│   │   ├── images/               # Image files
│   │   └── icons/                # Icon files
│   │
│   ├── styles/                   # Global style definitions
│   │
│   └── ThemeWrapper.js           # Theme provider wrapper
│
├── package.json                  # Dependencies and scripts
├── tsconfig.json                 # TypeScript configuration
└── README.md                     # This file
```

## Prerequisites

- **Node.js**: Version 14.0 or higher (recommended: 16.x or 18.x)
- **npm**: Version 6.0 or higher (comes with Node.js)
- **Backend API**: Cost Guardian backend running on `http://localhost:5002`

## Installation

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Dependencies

```bash
npm install
```

This will install all required packages including:
- React and React DOM
- Material-UI and related packages
- Nivo charting libraries
- React Router and React Query
- TypeScript (for TypeScript files)

### 3. Configure API Endpoint

Update the API base URL if your backend is running on a different port:

```javascript
// src/services/api.js
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5002/api/v1';
```

Create a `.env` file in the `frontend` directory:

```bash
REACT_APP_API_URL=http://localhost:5002/api/v1
```

### 4. Start Development Server

```bash
npm start
```

The application will open automatically at `http://localhost:3000`.

## Available Scripts

### Development

- **`npm start`** - Starts the development server
  - Opens browser at `http://localhost:3000`
  - Hot reloading enabled
  - Displays lint errors in console

### Testing

- **`npm test`** - Launches the test runner in interactive watch mode
  - Runs tests using Jest and React Testing Library
  - Supports watch mode for continuous testing

### Production

- **`npm run build`** - Builds the app for production
  - Creates optimized production build in `build/` directory
  - Minifies code and optimizes assets
  - Ready for deployment to static hosting

### Advanced

- **`npm run eject`** - Ejects from Create React App (irreversible)
  - Provides full control over webpack configuration
  - ⚠️ **Warning**: This is a one-way operation

## Configuration

### Environment Variables

Create a `.env` file in the `frontend` directory:

```bash
# API Configuration
REACT_APP_API_URL=http://localhost:5002/api/v1

# Feature Flags (if applicable)
REACT_APP_ENABLE_ANALYTICS=true
```

### API Integration

The frontend communicates with the backend API through service modules:

- **Metrics Service**: Fetches dashboard metrics and analytics
- **API Client**: Handles HTTP requests and error handling
- **React Query**: Manages data fetching, caching, and synchronization

## Usage

### Navigation

The application features a responsive sidebar navigation:

1. **IT Dashboard** (`/it`): Technical infrastructure metrics
2. **Finance Dashboard** (`/finance`): Financial analytics and trends
3. **MSP Dashboard** (`/msp`): Multi-tenant management view

### Theme Toggle

Click the theme toggle button in the header to switch between:
- **Light Mode**: Bright theme for daytime use
- **Dark Mode**: Dark theme for reduced eye strain

### Dashboard Features

#### Date Filtering

- Select date ranges using the date picker controls
- Filter data by specific accounts or services
- Real-time chart updates based on filters

#### Chart Interactions

- **Hover**: View detailed tooltips with exact values
- **Click**: Interact with chart elements for detailed views
- **Zoom**: Pan and zoom on time-series charts
- **Legend**: Toggle data series visibility

#### Tables

- **Sorting**: Click column headers to sort
- **Filtering**: Use filter inputs to narrow results
- **Pagination**: Navigate through large datasets

## Development Guide

### Adding New Components

1. Create component file in appropriate directory:
   ```bash
   # For reusable components
   src/components/MyComponent.tsx
   
   # For page components
   src/pages/MyPage.tsx
   ```

2. Follow existing patterns:
   - Use functional components with hooks
   - Include TypeScript types (for .tsx files)
   - Use Material-UI components
   - Follow naming conventions

### Styling Guidelines

- Use Material-UI `sx` prop for component-specific styles
- Use `theme` object for consistent spacing and colors
- Leverage Emotion for advanced styling needs
- Follow Material-UI design principles

### API Integration

1. Add service method in `src/services/`:
   ```javascript
   export const fetchMyData = async (params) => {
     const response = await api.get('/my-endpoint', { params });
     return response.data;
   };
   ```

2. Use React Query hook:
   ```javascript
   const { data, isLoading, error } = useQuery(
     'myData',
     () => fetchMyData(params)
   );
   ```

### Chart Development

Charts use Nivo library:

1. Import Nivo chart component
2. Format data according to Nivo requirements
3. Configure responsive wrapper
4. Add appropriate props and styling

Example:
```jsx
import { ResponsiveLine } from '@nivo/line';

<ResponsiveLine
  data={formattedData}
  margin={{ top: 50, right: 110, bottom: 50, left: 60 }}
  // ... other props
/>
```

## Building for Production

### Create Production Build

```bash
npm run build
```

This creates an optimized build in the `build/` directory.

### Deploy Static Build

The `build/` folder contains static files that can be served by:

- **Nginx**: Configure as static file server
- **Apache**: Serve from web root
- **AWS S3**: Upload to S3 bucket with static hosting
- **Netlify/Vercel**: Deploy directly from Git

### Example Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/frontend/build;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## Browser Support

The application supports:

- **Chrome**: Latest 2 versions
- **Firefox**: Latest 2 versions
- **Safari**: Latest 2 versions
- **Edge**: Latest 2 versions

Note: Some features may require modern browser capabilities.

## Performance Optimization

### Built-in Optimizations

- Code splitting and lazy loading
- Optimized bundle size
- Memoization of expensive computations
- React Query caching for API calls

### Best Practices

- Use React.memo for expensive components
- Implement lazy loading for routes
- Optimize images and assets
- Monitor bundle size

## Troubleshooting

### Common Issues

#### Port 3000 Already in Use

```bash
# Find process using port 3000
lsof -ti:3000

# Kill process (macOS/Linux)
lsof -ti:3000 | xargs kill -9

# Or use different port
PORT=3001 npm start
```

#### API Connection Errors

1. Verify backend is running:
   ```bash
   curl http://localhost:5002/api/v1/status/health
   ```

2. Check CORS configuration in backend
3. Verify API URL in `.env` file

#### Module Not Found Errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### Build Failures

```bash
# Clear build cache
rm -rf build node_modules/.cache
npm run build
```

### Development Tools

- **React Developer Tools**: Browser extension for React debugging
- **Redux DevTools**: (If using Redux) For state inspection
- **Browser Console**: Check for errors and warnings

## Testing

### Running Tests

```bash
npm test
```

### Test Structure

- Unit tests for utility functions
- Component tests using React Testing Library
- Integration tests for API services

### Writing Tests

```javascript
import { render, screen } from '@testing-library/react';
import MyComponent from './MyComponent';

test('renders component', () => {
  render(<MyComponent />);
  const element = screen.getByText(/expected text/i);
  expect(element).toBeInTheDocument();
});
```

## Contributing

1. Follow existing code style and patterns
2. Write tests for new features
3. Update documentation
4. Ensure responsive design
5. Test across browsers
6. Follow accessibility guidelines

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions:
- Check existing documentation
- Review code comments
- Contact the development team
- Submit issues to the repository
