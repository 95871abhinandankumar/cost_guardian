"""
Data Viewer Extension for Cost Guardian
Simple web interface to view aggregated data
"""

from flask import Blueprint, render_template_string, jsonify, request
import sqlite3
import json
from datetime import datetime

data_viewer_bp = Blueprint('data_viewer', __name__)

# HTML template for data viewer
DATA_VIEWER_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cost Guardian - Data Viewer</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-card h3 {
            margin: 0 0 10px 0;
            font-size: 14px;
            opacity: 0.9;
        }
        .stat-card .value {
            font-size: 24px;
            font-weight: bold;
        }
        .section {
            margin-bottom: 30px;
        }
        .section h2 {
            color: #34495e;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f8f9fa;
            font-weight: 600;
            color: #2c3e50;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .anomaly {
            color: #e74c3c;
            font-weight: bold;
        }
        .normal {
            color: #27ae60;
        }
        .filters {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .filters select, .filters input {
            margin: 5px;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .btn {
            background: #3498db;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin: 5px;
        }
        .btn:hover {
            background: #2980b9;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Cost Guardian Data Viewer</h1>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Records</h3>
                <div class="value">{{ stats.total_records }}</div>
            </div>
            <div class="stat-card">
                <h3>Total Cost</h3>
                <div class="value">${{ "%.2f"|format(stats.total_cost) }}</div>
            </div>
            <div class="stat-card">
                <h3>Unique Accounts</h3>
                <div class="value">{{ stats.unique_accounts }}</div>
            </div>
            <div class="stat-card">
                <h3>Unique Services</h3>
                <div class="value">{{ stats.unique_services }}</div>
            </div>
            <div class="stat-card">
                <h3>Anomalies</h3>
                <div class="value">{{ stats.anomaly_records }}</div>
            </div>
        </div>

        <div class="filters">
            <h3>Filters</h3>
            <select id="accountFilter">
                <option value="">All Accounts</option>
                {% for account in accounts %}
                <option value="{{ account.account_id }}">{{ account.account_id }}</option>
                {% endfor %}
            </select>
            <select id="serviceFilter">
                <option value="">All Services</option>
                {% for service in services %}
                <option value="{{ service.service_name }}">{{ service.service_name }}</option>
                {% endfor %}
            </select>
            <input type="date" id="startDate" placeholder="Start Date">
            <input type="date" id="endDate" placeholder="End Date">
            <button class="btn" onclick="applyFilters()">Apply Filters</button>
            <button class="btn" onclick="clearFilters()">Clear</button>
        </div>

        <div class="section">
            <h2>Daily Usage Data</h2>
            <div id="dataTable">
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Account</th>
                            <th>Service</th>
                            <th>Cost</th>
                            <th>Usage</th>
                            <th>Region</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for record in records %}
                        <tr>
                            <td>{{ record.usage_date }}</td>
                            <td>{{ record.account_id }}</td>
                            <td>{{ record.service_name }}</td>
                            <td>${{ "%.2f"|format(record.cost) }}</td>
                            <td>{{ record.usage_quantity }}</td>
                            <td>{{ record.region }}</td>
                            <td>
                                {% if record.anomaly_flag %}
                                    <span class="anomaly">ANOMALY ({{ record.anomaly_score }})</span>
                                {% else %}
                                    <span class="normal">NORMAL</span>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="section">
            <h2>Service Breakdown</h2>
            <table>
                <thead>
                    <tr>
                        <th>Service</th>
                        <th>Total Cost</th>
                        <th>Records</th>
                        <th>Anomalies</th>
                        <th>Avg Cost/Day</th>
                    </tr>
                </thead>
                <tbody>
                    {% for service in service_breakdown %}
                    <tr>
                        <td>{{ service.service_name }}</td>
                        <td>${{ "%.2f"|format(service.total_cost) }}</td>
                        <td>{{ service.record_count }}</td>
                        <td>{{ service.anomalies }}</td>
                        <td>${{ "%.2f"|format(service.avg_cost) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        function applyFilters() {
            const account = document.getElementById('accountFilter').value;
            const service = document.getElementById('serviceFilter').value;
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;
            
            const params = new URLSearchParams();
            if (account) params.append('account', account);
            if (service) params.append('service', service);
            if (startDate) params.append('start_date', startDate);
            if (endDate) params.append('end_date', endDate);
            
            window.location.href = '/api/v1/data-viewer?' + params.toString();
        }
        
        function clearFilters() {
            document.getElementById('accountFilter').value = '';
            document.getElementById('serviceFilter').value = '';
            document.getElementById('startDate').value = '';
            document.getElementById('endDate').value = '';
            window.location.href = '/api/v1/data-viewer';
        }
    </script>
</body>
</html>
"""

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('cost_guardian.db')
    conn.row_factory = sqlite3.Row
    return conn

@data_viewer_bp.route('/data-viewer', methods=['GET'])
def data_viewer():
    """Main data viewer page"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get filters from request
        account_filter = request.args.get('account', '')
        service_filter = request.args.get('service', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        # Build query with filters
        query = """
            SELECT 
                usage_date, account_id, service_name, cost, 
                usage_quantity, region, anomaly_flag, anomaly_score
            FROM daily_usage
            WHERE 1=1
        """
        params = []
        
        if account_filter:
            query += " AND account_id = ?"
            params.append(account_filter)
        
        if service_filter:
            query += " AND service_name = ?"
            params.append(service_filter)
        
        if start_date:
            query += " AND usage_date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND usage_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY usage_date DESC, cost DESC LIMIT 100"
        
        # Get filtered records
        records = cursor.execute(query, params).fetchall()
        
        # Get statistics
        stats_query = """
            SELECT 
                COUNT(*) as total_records,
                SUM(cost) as total_cost,
                COUNT(DISTINCT account_id) as unique_accounts,
                COUNT(DISTINCT service_name) as unique_services,
                COUNT(CASE WHEN anomaly_flag = 1 THEN 1 END) as anomaly_records
            FROM daily_usage
        """
        stats = cursor.execute(stats_query).fetchone()
        
        # Get unique accounts and services for filters
        accounts = cursor.execute("SELECT DISTINCT account_id FROM daily_usage ORDER BY account_id").fetchall()
        services = cursor.execute("SELECT DISTINCT service_name FROM daily_usage ORDER BY service_name").fetchall()
        
        # Get service breakdown
        service_breakdown_query = """
            SELECT 
                service_name,
                SUM(cost) as total_cost,
                COUNT(*) as record_count,
                COUNT(CASE WHEN anomaly_flag = 1 THEN 1 END) as anomalies,
                AVG(cost) as avg_cost
            FROM daily_usage
            GROUP BY service_name
            ORDER BY total_cost DESC
        """
        service_breakdown = cursor.execute(service_breakdown_query).fetchall()
        
        conn.close()
        
        return render_template_string(
            DATA_VIEWER_TEMPLATE,
            records=records,
            stats=stats,
            accounts=accounts,
            services=services,
            service_breakdown=service_breakdown
        )
        
    except Exception as e:
        return f"Error loading data: {str(e)}", 500

@data_viewer_bp.route('/data-viewer/api/data', methods=['GET'])
def get_data_api():
    """API endpoint for data (for AJAX calls)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get filters
        account_filter = request.args.get('account', '')
        service_filter = request.args.get('service', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        # Build query
        query = """
            SELECT 
                usage_date, account_id, service_name, cost, 
                usage_quantity, region, anomaly_flag, anomaly_score
            FROM daily_usage
            WHERE 1=1
        """
        params = []
        
        if account_filter:
            query += " AND account_id = ?"
            params.append(account_filter)
        
        if service_filter:
            query += " AND service_name = ?"
            params.append(service_filter)
        
        if start_date:
            query += " AND usage_date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND usage_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY usage_date DESC, cost DESC"
        
        records = cursor.execute(query, params).fetchall()
        conn.close()
        
        return jsonify([dict(record) for record in records])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
