"""
Cost Guardian - Main Application Entry Point
Flask application for cost monitoring and analysis
"""

from app import create_app

# Create Flask application instance
app = create_app()

if __name__ == '__main__':
    # Run the application
    app.run(
        debug=app.config.get('DEBUG', False),
        host=app.config.get('HOST', '0.0.0.0'),
        port=app.config.get('PORT', 5002)
    )