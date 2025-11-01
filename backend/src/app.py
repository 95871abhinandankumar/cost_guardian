"""
Cost Guardian - Professional Flask Application
A comprehensive cost monitoring and analysis platform for cloud infrastructure
"""

import os
import logging
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cost_guardian.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_app(config_name=None):
    """
    Application factory pattern for Flask app creation
    
    Args:
        config_name (str): Configuration environment name
        
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    app.config.from_object(f'config.settings.{config_name.title()}Config')
    
    # Initialize extensions
    initialize_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register CLI commands
    register_cli_commands(app)
    
    logger.info(f"Cost Guardian application initialized in {config_name} mode")
    return app

def initialize_extensions(app):
    """Initialize Flask extensions with proper configuration"""
    
    # CORS configuration - allow all origins in development
    cors_origins = app.config.get('CORS_ORIGINS', ['*'])
    if cors_origins == ['*']:
        CORS(app, resources={r"/api/*": {"origins": "*"}})
    else:
        CORS(app, origins=cors_origins)
    
    # Rate limiting (in-memory for development)
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=app.config.get('RATE_LIMITS', ["1000 per day", "100 per hour"])
    )
    limiter.init_app(app)
    
    # JWT configuration
    jwt = JWTManager(app)
    
    # Configure JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'message': 'Token has expired', 'error': 'token_expired'}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {'message': 'Invalid token', 'error': 'invalid_token'}, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {'message': 'Authorization token is required', 'error': 'missing_token'}, 401
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return {'message': 'Fresh token required', 'error': 'token_not_fresh'}, 401

def register_blueprints(app):
    """Register Flask blueprints with proper error handling"""
    
    try:
        # Import blueprints
        from api.routes.status import status_bp
        from api.routes.insights import insights_bp
        from api.routes.feedback import feedback_bp
        from api.routes.data_viewer import data_viewer_bp
        from api.routes.metrics import metrics_bp
        
        # Register blueprints with URL prefixes
        app.register_blueprint(status_bp, url_prefix='/api/v1/status')
        app.register_blueprint(insights_bp, url_prefix='/api/v1/insights')
        app.register_blueprint(feedback_bp, url_prefix='/api/v1/feedback')
        app.register_blueprint(data_viewer_bp, url_prefix='/api/v1')
        app.register_blueprint(metrics_bp, url_prefix='/api/v1')
        
        logger.info("All blueprints registered successfully")
        
    except ImportError as e:
        logger.error(f"Failed to import blueprints: {e}")
        raise

def register_error_handlers(app):
    """Register comprehensive error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return {'message': 'Bad request', 'error': 'bad_request'}, 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return {'message': 'Unauthorized access', 'error': 'unauthorized'}, 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return {'message': 'Forbidden access', 'error': 'forbidden'}, 403
    
    @app.errorhandler(404)
    def not_found(error):
        return {'message': 'Resource not found', 'error': 'not_found'}, 404
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return {'message': 'Unprocessable entity', 'error': 'unprocessable_entity'}, 422
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return {'message': 'Rate limit exceeded', 'error': 'rate_limit_exceeded'}, 429
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return {'message': 'Internal server error', 'error': 'internal_error'}, 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {e}")
        return {'message': 'An unexpected error occurred', 'error': 'unexpected_error'}, 500

def register_cli_commands(app):
    """Register CLI commands for database management"""
    
    @app.cli.command()
    def init_db():
        """Initialize the database with schema"""
        from storage.database import init_database
        init_database()
        print("Database initialized successfully")
    
    @app.cli.command()
    def aggregate_data():
        """Run data aggregation process"""
        from services.data_aggregator import DataAggregationService
        service = DataAggregationService()
        result = service.process_and_store_data()
        if result['success']:
            print(f"Data aggregation completed: {result['summary']}")
        else:
            print(f"Data aggregation failed: {result['message']}")
            return 1
        return 0

if __name__ == '__main__':
    app = create_app()
    app.run(
        debug=app.config.get('DEBUG', False),
        host=app.config.get('HOST', '0.0.0.0'),
        port=app.config.get('PORT', 5000)
    )