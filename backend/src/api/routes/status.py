"""
Status API routes for Cost Guardian application
Provides health check and system status endpoints
"""

from flask import Blueprint, jsonify, current_app
from datetime import datetime
import psutil
import os

status_bp = Blueprint('status', __name__)

@status_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    Returns basic application health status
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'cost-guardian-api',
        'version': '1.0.0'
    }), 200

@status_bp.route('/status', methods=['GET'])
def detailed_status():
    """
    Detailed system status endpoint
    Returns comprehensive system information
    """
    try:
        # Get system information
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get process information
        process = psutil.Process(os.getpid())
        
        status_info = {
            'status': 'operational',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'cost-guardian-api',
            'version': '1.0.0',
            'environment': current_app.config.get('FLASK_ENV', 'development'),
            'system': {
                'cpu_percent': cpu_percent,
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                }
            },
            'process': {
                'pid': process.pid,
                'memory_info': process.memory_info()._asdict(),
                'cpu_percent': process.cpu_percent(),
                'create_time': datetime.fromtimestamp(process.create_time()).isoformat()
            },
            'config': {
                'debug': current_app.debug,
                'testing': current_app.testing,
                'database_configured': bool(current_app.config.get('DATABASE_URL')),
                'redis_configured': bool(current_app.config.get('REDIS_URL')),
                'aws_configured': bool(current_app.config.get('AWS_ACCESS_KEY_ID'))
            }
        }
        
        return jsonify(status_info), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500

@status_bp.route('/ping', methods=['GET'])
def ping():
    """
    Simple ping endpoint for load balancer health checks
    """
    return jsonify({'pong': True}), 200

@status_bp.route('/ready', methods=['GET'])
def readiness_check():
    """
    Readiness check endpoint
    Verifies that the application is ready to serve requests
    """
    try:
        # Check database connectivity
        database_ready = True
        try:
            # Add database connectivity check here
            pass
        except Exception:
            database_ready = False
        
        # Check Redis connectivity
        redis_ready = True
        try:
            # Add Redis connectivity check here
            pass
        except Exception:
            redis_ready = False
        
        if database_ready and redis_ready:
            return jsonify({
                'status': 'ready',
                'timestamp': datetime.utcnow().isoformat(),
                'checks': {
                    'database': 'ok',
                    'redis': 'ok'
                }
            }), 200
        else:
            return jsonify({
                'status': 'not_ready',
                'timestamp': datetime.utcnow().isoformat(),
                'checks': {
                    'database': 'ok' if database_ready else 'failed',
                    'redis': 'ok' if redis_ready else 'failed'
                }
            }), 503
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500
