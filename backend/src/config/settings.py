"""
Configuration Management for Cost Guardian
Professional configuration handling with environment-based settings
"""

import os
from datetime import timedelta
from typing import List, Dict, Any

class BaseConfig:
    """Base configuration class with common settings"""
    
    # Basic Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database settings
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///cost_guardian.db'
    DATABASE_POOL_SIZE = int(os.environ.get('DATABASE_POOL_SIZE', 10))
    DATABASE_POOL_TIMEOUT = int(os.environ.get('DATABASE_POOL_TIMEOUT', 30))
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get('JWT_ACCESS_EXPIRES_HOURS', 1)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.environ.get('JWT_REFRESH_EXPIRES_DAYS', 30)))
    JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_HEADERS = ['Content-Type', 'Authorization']
    
    # Rate limiting (using in-memory for now)
    RATE_LIMITS = ["1000 per day", "100 per hour"]
    
    # External services (add when needed)
    # AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    # AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    # OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'cost_guardian.log')
    LOG_MAX_SIZE = int(os.environ.get('LOG_MAX_SIZE', 10485760))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 5))
    
    # Data processing settings
    MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', 16 * 1024 * 1024))  # 16MB
    ALLOWED_EXTENSIONS = {'json', 'csv', 'xlsx', 'parquet'}
    DATA_RETENTION_DAYS = int(os.environ.get('DATA_RETENTION_DAYS', 365))
    
    # Pagination
    DEFAULT_PAGE_SIZE = int(os.environ.get('DEFAULT_PAGE_SIZE', 20))
    MAX_PAGE_SIZE = int(os.environ.get('MAX_PAGE_SIZE', 100))
    
    # Security
    PASSWORD_MIN_LENGTH = int(os.environ.get('PASSWORD_MIN_LENGTH', 8))
    SESSION_TIMEOUT_MINUTES = int(os.environ.get('SESSION_TIMEOUT_MINUTES', 30))
    
    # API settings
    API_VERSION = 'v1'
    API_PREFIX = f'/api/{API_VERSION}'
    
    # Feature flags (simplified)
    ENABLE_ANOMALY_DETECTION = True
    ENABLE_DATA_EXPORT = True

class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    
    DEBUG = True
    TESTING = False
    
    # Use SQLite for development
    SQLALCHEMY_DATABASE_URI = 'sqlite:///cost_guardian_dev.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Relaxed CORS for development - allow all localhost ports
    CORS_ORIGINS = ['*']  # Allow all origins in development
    
    # Development-specific settings
    LOG_LEVEL = 'DEBUG'
    RATE_LIMITS = ["10000 per day", "1000 per hour"]  # More lenient for development

class ProductionConfig(BaseConfig):
    """Production configuration"""
    
    DEBUG = False
    TESTING = False
    
    # Use PostgreSQL for production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Production-specific settings
    LOG_LEVEL = 'WARNING'
    
    # Validate required environment variables
    @classmethod
    def validate_config(cls):
        """Validate that all required production settings are present"""
        required_vars = [
            'SECRET_KEY',
            'JWT_SECRET_KEY',
            'DATABASE_URL'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

class TestingConfig(BaseConfig):
    """Testing configuration"""
    
    TESTING = True
    DEBUG = True
    
    # Use in-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Mock services for testing (add when needed)
    # AWS_ACCESS_KEY_ID = 'test-key'
    # AWS_SECRET_ACCESS_KEY = 'test-secret'
    # OPENAI_API_KEY = 'test-openai-key'
    
    # Fast token expiration for testing
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=1)

class StagingConfig(ProductionConfig):
    """Staging configuration (inherits from Production)"""
    
    DEBUG = True
    LOG_LEVEL = 'INFO'
    
    # Staging-specific overrides
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'https://staging.costguardian.com').split(',')

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name: str = None) -> BaseConfig:
    """
    Get configuration class by name
    
    Args:
        config_name: Configuration environment name
        
    Returns:
        Configuration class
    """
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    
    if config_name not in config:
        raise ValueError(f"Unknown configuration: {config_name}")
    
    config_class = config[config_name]
    
    # Validate production config
    if config_name == 'production':
        config_class.validate_config()
    
    return config_class