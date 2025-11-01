# Cost Guardian Backend

A comprehensive cloud cost monitoring and analysis platform built with Flask, featuring intelligent cost analytics, agentic AI-driven insights, and automated cost optimization recommendations.

## Overview

Cost Guardian is an enterprise-grade backend system designed to help organizations monitor, analyze, and optimize their cloud infrastructure costs. The platform aggregates cost data from multiple cloud providers, performs advanced analytics using machine learning and AI, and provides actionable insights through a RESTful API.

## Features

### Core Capabilities

- **Multi-Cloud Cost Aggregation**: Collect and aggregate cost data from AWS and other cloud providers
- **Day-wise Data Processing**: Efficiently processes raw cost data into daily summaries with advanced aggregation
- **Agentic AI Analysis**: LLM-powered cost analysis with intelligent query understanding and automated insights
- **Vector Database Integration**: Semantic search capabilities using Qdrant for intelligent data retrieval
- **RAG Pipeline**: Retrieval-Augmented Generation for context-aware cost analysis
- **Automated Scheduling**: Background jobs for data collection, analysis, and reporting
- **Intelligent Caching**: Multi-layer caching system for performance optimization

### Analytics & Insights

- **Cost Trend Analysis**: Historical cost tracking with predictive forecasting
- **Anomaly Detection**: Automated identification of unusual cost patterns
- **Cost Allocation**: Service and account-level cost breakdown
- **Utilization Metrics**: Resource utilization tracking and optimization
- **Client Prioritization**: Intelligent ranking based on value and engagement
- **Savings Recommendations**: AI-generated actionable cost optimization suggestions

### API & Integration

- **RESTful API**: Comprehensive REST API with versioning (`/api/v1`)
- **JWT Authentication**: Secure token-based authentication
- **Rate Limiting**: Configurable rate limits to prevent API abuse
- **CORS Support**: Cross-origin resource sharing for frontend integration
- **Error Handling**: Comprehensive error handling with structured responses
- **Request Validation**: Input validation and sanitization

### Data Management

- **Database Support**: SQLite (development) and PostgreSQL (production)
- **Connection Pooling**: Efficient database connection management
- **Schema Management**: Automated database migrations and schema updates
- **Data Quality Checks**: Validation and quality assurance for ingested data
- **Data Cleaning**: Automated data normalization and cleaning

## Project Structure

```
backend/
├── src/
│   ├── app.py                    # Flask application factory
│   ├── main.py                   # Application entry point
│   ├── aggregator.py             # Data aggregation service
│   ├── query_db.py               # Database query utilities
│   │
│   ├── api/                      # API layer
│   │   ├── routes/               # Route blueprints
│   │   │   ├── status.py         # Health check endpoints
│   │   │   ├── insights.py      # Cost analysis endpoints
│   │   │   ├── metrics.py        # Metrics and analytics endpoints
│   │   │   ├── feedback.py       # User feedback endpoints
│   │   │   └── data_viewer.py   # Web data viewer
│   │   ├── utils/
│   │   │   ├── auth.py           # Authentication utilities
│   │   │   └── response_builder.py
│   │   └── handler.py            # Request handlers
│   │
│   ├── agentic_ai/               # AI and ML components
│   │   ├── llm_engine.py         # LLM evaluation engine
│   │   ├── query_analysis.py     # Query analysis and understanding
│   │   ├── insight_generator.py  # AI-powered insight generation
│   │   ├── recommendation.py    # Cost optimization recommendations
│   │   ├── enhanced_analysis.py  # Advanced analytics
│   │   ├── cache_manager.py      # Caching layer
│   │   ├── analysis_scheduler.py # Scheduled analysis jobs
│   │   └── gemini_provider.py   # Google Gemini integration
│   │
│   ├── ingestion/                # Data ingestion layer
│   │   ├── aws_data_collector.py # AWS cost data collection
│   │   ├── connector.py          # Cloud provider connectors
│   │   ├── data_cleaner.py       # Data cleaning utilities
│   │   └── data_scheduler.py     # Data collection scheduling
│   │
│   ├── processing/               # Data processing
│   │   ├── etl_lambda.py      # ETL pipelines
│   │   ├── embedding_lambda.py  # Vector embeddings generation
│   │   ├── summarizer_lambda.py # Data summarization
│   │   └── data_quality_checks.py
│   │
│   ├── storage/                   # Data storage layer
│   │   ├── database.py           # Database management
│   │   ├── schema.sql            # Database schema
│   │   ├── mongodb_client.py     # MongoDB integration
│   │   ├── vector_db_client.py   # Vector database client
│   │   └── embedding_utils.py    # Embedding utilities
│   │
│   ├── vector_db/                # Vector database integration
│   │   ├── qdrant_client_connector.py
│   │   ├── embedding_model.py    # Embedding models
│   │   ├── semantic_search.py    # Semantic search
│   │   └── ingest_to_qdrant.py   # Data ingestion
│   │
│   ├── rag/                      # RAG pipeline
│   │   ├── rag_pipeline.py       # Main RAG pipeline
│   │   ├── retriever.py          # Document retrieval
│   │   ├── llm_client.py         # LLM client
│   │   └── prompt_templates.py   # Prompt templates
│   │
│   ├── services/                 # Business logic services
│   │   └── data_aggregator.py    # Data aggregation service
│   │
│   ├── monitoring/               # Monitoring and logging
│   │   ├── logger.py             # Logging configuration
│   │   ├── error_handler.py      # Error handling
│   │   └── metrics_collector.py  # Metrics collection
│   │
│   ├── config/                   # Configuration management
│   │   ├── settings.py           # Application settings
│   │   └── secrets_manager.py    # Secrets management
│   │
│   └── data/                     # Data files
│       └── raw_data.json         # Raw cost data
│
├── tests/                         # Test suite
│   ├── test_api_routes.py
│   ├── test_ingestion.py
│   ├── test_rag_pipeline.py
│   └── test_storage.py
│
├── requirements.txt               # Python dependencies
├── template.yaml                  # SAM/CloudFormation template
├── ENV_README.md                  # Environment variables documentation
└── README.md                      # This file
```

## Prerequisites

- **Python**: 3.9 or higher
- **pip**: Python package installer
- **PostgreSQL**: (Optional, for production) PostgreSQL 12+
- **Redis**: (Optional, for production rate limiting)
- **AWS CLI**: (Optional, for AWS data collection)

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd cost_guardian/backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the environment template and configure:

```bash
cp ENV_README.md .env
```

Set required environment variables (see [ENV_README.md](ENV_README.md) for details):

```bash
# Required
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key

# Optional (for production)
DATABASE_URL=postgresql://user:password@localhost:5432/cost_guardian
REDIS_URL=redis://localhost:6379/0
GEMINI_API_KEY=your-gemini-api-key
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
```

### 5. Initialize Database

```bash
cd src
flask init-db
```

### 6. Process Initial Data

```bash
python aggregator.py
```

This will:
- Load raw cost data from JSON files
- Aggregate data by account, service, and date
- Store aggregated data in the database
- Generate summary statistics

### 7. Start the Application

```bash
python main.py
```

The application will start on `http://localhost:5002` by default.

## API Documentation

### Base URL

```
http://localhost:5002/api/v1
```

### Endpoints

#### Status Endpoints

- **`GET /status/health`** - Health check endpoint
  - Returns: Service health status
  - Response: `{"status": "healthy", "timestamp": "..."}`

- **`GET /status/ping`** - Simple ping endpoint
  - Returns: Basic connectivity test
  - Response: `{"message": "pong"}`

- **`GET /status/status`** - Detailed system status
  - Returns: Comprehensive system information
  - Response: Includes database status, cache status, etc.

#### Metrics Endpoints

- **`GET /metrics/dashboard`** - Dashboard metrics
  - Query Parameters:
    - `start_date` (optional): Start date filter
    - `end_date` (optional): End date filter
    - `account_id` (optional): Filter by account
  - Returns: Aggregated metrics for dashboard visualization

- **`GET /metrics/cost-trend`** - Cost trend analysis
  - Returns: Historical cost trends with forecasting

- **`GET /metrics/anomalies`** - Anomaly detection results
  - Returns: Detected cost anomalies

- **`GET /metrics/client-prioritization`** - Client prioritization data
  - Returns: Ranked client list based on value metrics

#### Insights Endpoints

- **`GET /insights/cost-summary`** - Cost summary analysis
  - Returns: High-level cost summary with key metrics

- **`POST /insights/analyze`** - AI-powered cost analysis
  - Body: Query or analysis request
  - Returns: AI-generated insights and recommendations

#### Feedback Endpoints

- **`POST /feedback`** - Submit user feedback
  - Body: Feedback data
  - Returns: Confirmation of feedback submission

### Authentication

Protected endpoints require JWT authentication:

```bash
# Get token
POST /api/v1/auth/login
# Returns: { "access_token": "..." }

# Use token
Authorization: Bearer <token>
```

## Configuration

### Development Configuration

The application uses environment-based configuration:

- **Database**: SQLite (file-based, no setup required)
- **Debug Mode**: Enabled
- **Rate Limiting**: In-memory (simple)
- **Logging**: Console and file logging
- **CORS**: Allows all origins

### Production Configuration

Set `FLASK_ENV=production`:

- **Database**: PostgreSQL (connection pooling)
- **Debug Mode**: Disabled
- **Rate Limiting**: Redis-backed
- **Logging**: Structured JSON logging
- **CORS**: Restricted origins
- **Security Headers**: Enabled

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FLASK_ENV` | No | `development` | Environment name |
| `SECRET_KEY` | Yes | - | Flask secret key |
| `JWT_SECRET_KEY` | Yes | - | JWT signing key |
| `DATABASE_URL` | No | SQLite | Database connection string |
| `REDIS_URL` | No | - | Redis connection URL |
| `GEMINI_API_KEY` | No | - | Google Gemini API key |
| `AWS_ACCESS_KEY_ID` | No | - | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | No | - | AWS secret key |
| `LOG_LEVEL` | No | `INFO` | Logging level |
| `CORS_ORIGINS` | No | `*` | Allowed CORS origins |

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code (if using black)
black src/

# Lint code (if using flake8)
flake8 src/
```

### Database Migrations

```bash
# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade
```

## Deployment

### Development Server

```bash
python main.py
```

### Production Server (Gunicorn)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app
```

### Docker Deployment

```bash
# Build image
docker build -t cost-guardian-backend .

# Run container
docker run -p 5002:5002 --env-file .env cost-guardian-backend
```

### AWS Lambda Deployment

The project includes `template.yaml` for AWS SAM deployment:

```bash
sam build
sam deploy --guided
```

## Monitoring & Logging

### Logging

Logs are written to:
- Console (stdout)
- File: `cost_guardian.log`
- Structured JSON format in production

### Health Checks

Monitor application health:

```bash
curl http://localhost:5002/api/v1/status/health
```

### Metrics

Application metrics are collected and exposed via:
- `/api/v1/status/status` endpoint
- Custom metrics collector

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Find process using port 5002
lsof -ti:5002

# Kill process (macOS/Linux)
lsof -ti:5002 | xargs kill -9
```

#### Database Connection Errors

```bash
# Verify database exists
cd src
python show_schema.py

# Reinitialize database
flask init-db
```

#### Module Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### Missing Environment Variables

Ensure all required environment variables are set:

```bash
# Check current environment
printenv | grep -E "SECRET_KEY|JWT_SECRET|DATABASE_URL"
```

## Architecture

### Key Components

1. **Application Factory**: Flask app creation using factory pattern
2. **Blueprint Architecture**: Modular route organization
3. **Service Layer**: Business logic separation
4. **Data Layer**: Database abstraction
5. **AI Engine**: LLM integration for intelligent analysis
6. **Vector Database**: Semantic search capabilities
7. **Caching Layer**: Multi-level caching for performance

### Data Flow

1. **Ingestion**: Cloud provider APIs → Data Collectors
2. **Processing**: Raw Data → Cleaning → Aggregation
3. **Storage**: Aggregated Data → Database
4. **Analysis**: Database → AI Engine → Insights
5. **API**: Insights → REST API → Frontend

## Contributing

1. Follow the existing code structure and patterns
2. Add comprehensive error handling and logging
3. Include type hints and docstrings for all functions
4. Write tests for new features
5. Update documentation as needed
6. Follow PEP 8 style guidelines

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions, please refer to the project repository or contact the development team.
