# Cost Guardian - Flask Application

A comprehensive cost monitoring and analysis platform for cloud infrastructure.

## Features

- **Day-wise Data Aggregation**: Efficiently processes raw cost data into daily summaries
- **Flask API**: RESTful API with proper error handling and logging
- **Database Management**: SQLite/PostgreSQL support with connection pooling
- **Web Data Viewer**: Interactive web interface for data exploration
- **Configuration Management**: Environment-based configuration system
- **Rate Limiting**: Built-in API rate limiting
- **JWT Authentication**: Secure API access (ready for implementation)

## Project Structure

```
backend/src/
├── app.py                     # Main Flask application factory
├── main.py                    # Application entry point
├── config/
│   └── settings.py           # Configuration management
├── api/
│   └── routes/               # API route blueprints
│       ├── status.py         # Health check endpoints
│       ├── insights.py       # Cost analysis endpoints
│       ├── feedback.py       # Feedback endpoints
│       └── data_viewer.py    # Web data viewer
├── services/
│   └── data_aggregator.py    # Data aggregation service
├── storage/
│   ├── database.py           # Database management layer
│   └── schema.sql            # Database schema
└── data/
    └── raw_data.json         # Raw cost data
```

## Quick Start

### Prerequisites
- Python 3.9 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone the repository and navigate to backend**:
   ```bash
   git clone <repository-url>
   cd cost_guardian/backend
   ```

2. **Create and activate virtual environment**:
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Process the data**:
   ```bash
   cd src
   python aggregator.py
   ```

5. **Start the application**:
   ```bash
   python main.py
   ```

6. **Access the application**:
   - API: http://localhost:5002/api/v1/status/health
   - Data Viewer: http://localhost:5002/api/v1/data-viewer

### Expected Output

When everything is working correctly, you should see:

- **Aggregator output**: "Data aggregation completed successfully!" with statistics
- **API response**: JSON with service status "healthy"
- **Data viewer**: Interactive web page with cost data tables
- **Database**: 602 aggregated records from 713 raw records

## API Endpoints

### Status Endpoints
- `GET /api/v1/status/health` - Health check
- `GET /api/v1/status/ping` - Simple ping
- `GET /api/v1/status/status` - Detailed system status

### Insights Endpoints
- `GET /api/v1/insights/cost-summary` - Cost summary analysis

### Data Viewer
- `GET /api/v1/data-viewer` - Interactive web interface

## Configuration

The application uses environment-based configuration:

### Development (Default)
- SQLite database
- Debug mode enabled
- In-memory rate limiting
- Detailed logging

### Production
- PostgreSQL database
- Security headers enabled
- Redis rate limiting (when configured)
- Optimized logging

### Environment Variables
```bash
# Required for production
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=postgresql://user:pass@host:port/db

# Optional
FLASK_ENV=development
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000
```

## Data Aggregation

The system processes raw cost data into daily summaries:

1. **Load raw data** from JSON files
2. **Group by** account_id, service_name, usage_date
3. **Aggregate** costs, usage quantities, and metadata
4. **Store** in optimized database format
5. **Generate** summary statistics and anomaly detection

## Database

### SQLite (Development)
- File-based database
- No external dependencies
- Perfect for development and testing

### PostgreSQL (Production)
- Connection pooling
- Advanced query optimization
- Production-ready scalability

## Security Features

- **JWT Authentication**: Ready for implementation
- **Rate Limiting**: Prevents API abuse
- **CORS Configuration**: Controlled cross-origin access
- **Input Validation**: Built-in validation framework
- **Error Handling**: Secure error responses

## Monitoring

- **Structured Logging**: JSON-formatted logs
- **Health Checks**: Built-in monitoring endpoints
- **Performance Metrics**: Request timing and statistics
- **Error Tracking**: Comprehensive error logging

## Deployment

### Development
```bash
python main.py
```

### Production
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## CLI Commands

```bash
# Initialize database
flask init-db

# Run data aggregation
flask aggregate-data
```

## Contributing

1. Follow the existing code structure
2. Add proper error handling and logging
3. Include type hints and docstrings
4. Test all new features
5. Update documentation

## Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # If port 5002 is busy, the app will show an error
   # Kill the process or change the port in main.py
   lsof -ti:5002 | xargs kill -9  # macOS/Linux
   ```

2. **Database not found**:
   ```bash
   # Make sure you've run the aggregator first
   cd src
   python aggregator.py
   ```

3. **Module not found errors**:
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate    # Windows
   
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

4. **Permission errors on Windows**:
   ```bash
   # Run as administrator or use PowerShell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

### Verification Steps

After installation, verify everything works:

1. **Check API health**:
   ```bash
   curl http://localhost:5002/api/v1/status/health
   ```

2. **View data in browser**:
   - Open: http://localhost:5002/api/v1/data-viewer

3. **Check database**:
   ```bash
   cd src
   python show_schema.py
   ```

## License

This project is licensed under the MIT License.
