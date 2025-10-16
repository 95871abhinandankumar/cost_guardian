"""
Insights API routes for Cost Guardian application
Provides cost analysis and insights endpoints
"""

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

insights_bp = Blueprint('insights', __name__)

# Rate limiting for insights endpoints
limiter = Limiter(
    key_func=get_jwt_identity,
    default_limits=["100 per hour"]
)

def load_cost_data() -> List[Dict[str, Any]]:
    """Load cost data from the JSON file"""
    try:
        data_path = os.path.join(current_app.root_path, 'data', 'raw_data.json')
        with open(data_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        current_app.logger.error(f"Error loading cost data: {e}")
        return []

@insights_bp.route('/', methods=['GET'])
def get_insights():
    return {'message': 'Insights endpoint ready'}, 200

@insights_bp.route('/cost-summary', methods=['GET'])
@jwt_required()
@limiter.limit("20 per minute")
def get_cost_summary():
    """
    Get overall cost summary and trends
    """
    try:
        data = load_cost_data()
        if not data:
            return jsonify({'error': 'No cost data available'}), 404
        
        # Calculate summary statistics
        total_cost = sum(item['cost'] for item in data)
        total_records = len(data)
        
        # Group by service
        service_costs = {}
        for item in data:
            service = item['service_name']
            if service not in service_costs:
                service_costs[service] = {'cost': 0, 'count': 0}
            service_costs[service]['cost'] += item['cost']
            service_costs[service]['count'] += 1
        
        # Group by account
        account_costs = {}
        for item in data:
            account = item['account_id']
            if account not in account_costs:
                account_costs[account] = {'cost': 0, 'count': 0}
            account_costs[account]['cost'] += item['cost']
            account_costs[account]['count'] += 1
        
        # Group by region
        region_costs = {}
        for item in data:
            region = item['region']
            if region not in region_costs:
                region_costs[region] = {'cost': 0, 'count': 0}
            region_costs[region]['cost'] += item['cost']
            region_costs[region]['count'] += 1
        
        # Find anomalies
        anomalies = [item for item in data if item.get('anomaly_flag', False)]
        
        summary = {
            'total_cost': round(total_cost, 2),
            'total_records': total_records,
            'average_cost_per_record': round(total_cost / total_records, 4),
            'anomalies_detected': len(anomalies),
            'breakdown': {
                'by_service': service_costs,
                'by_account': account_costs,
                'by_region': region_costs
            },
            'currency': 'USD',
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return jsonify(summary), 200
        
    except Exception as e:
        current_app.logger.error(f"Error generating cost summary: {e}")
        return jsonify({'error': 'Failed to generate cost summary'}), 500