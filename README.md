# Cost Guardian

An enterprise-grade cloud cost monitoring and optimization platform powered by AI, providing intelligent cost analytics, automated insights, and role-based dashboards for IT, Finance, and MSP teams.

## Overview

Cost Guardian is a full-stack application that helps organizations monitor, analyze, and optimize cloud infrastructure costs across multiple providers. The platform combines advanced analytics with AI-powered insights to deliver actionable recommendations for cost reduction.

## Architecture

```
cost_guardian/
├── backend/          # Flask REST API with AI/ML capabilities
└── frontend/         # React dashboard application
```

**Backend**: Flask-based REST API featuring agentic AI analysis, vector database integration, RAG pipeline, and automated cost analytics.

**Frontend**: React application with Material-UI, featuring role-based dashboards (IT, Finance, MSP) with interactive data visualization.

## Key Features

- **Multi-Cloud Cost Aggregation**: Collect and analyze costs from AWS and other providers
- **AI-Powered Insights**: LLM-driven analysis with Google Gemini integration
- **Anomaly Detection**: Automated identification of unusual cost patterns
- **Predictive Forecasting**: Machine learning models for cost trend prediction
- **Role-Based Dashboards**: Specialized views for IT, Finance, and MSP teams
- **Interactive Visualizations**: Advanced charts and analytics with Nivo
- **Intelligent Recommendations**: AI-generated cost optimization suggestions

## Quick Start

### Prerequisites

- **Backend**: Python 3.9+, PostgreSQL (optional for production)
- **Frontend**: Node.js 14+, npm

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd src
flask init-db
python aggregator.py
python main.py
```

Backend runs on `http://localhost:5002`

See [backend/README.md](backend/README.md) for detailed documentation.

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend runs on `http://localhost:3000`

See [frontend/README.md](frontend/README.md) for detailed documentation.

## Technology Stack

**Backend**
- Flask (Python)
- Google Gemini API
- Qdrant (Vector Database)
- PostgreSQL/SQLite
- Redis
- Celery

**Frontend**
- React 18.2 + TypeScript
- Material-UI
- Nivo Charts
- React Query
- React Router

## Project Structure

- `backend/` - Flask API server with AI/ML components
- `frontend/` - React dashboard application

## Documentation

- [Backend Documentation](backend/README.md) - API, installation, and backend details
- [Frontend Documentation](frontend/README.md) - Frontend setup and usage

## License

This project is licensed under the MIT License.

