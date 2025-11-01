"""Metrics API endpoints for cost monitoring dashboard."""

import os
import sqlite3
import json
import logging
from datetime import datetime
from flask import Blueprint, jsonify, request
from typing import List, Dict, Any, Optional

# Agentic AI imports
from agentic_ai import LLMEvaluator, QueryAnalyzer

logger = logging.getLogger(__name__)
metrics_bp = Blueprint('metrics', __name__)

# Initialize agentic AI components (singleton pattern)
_llm_engine = None
_query_analyzer = None

def get_llm_engine():
    """Lazy initialization of LLM engine."""
    global _llm_engine
    if _llm_engine is None:
        _llm_engine = LLMEvaluator(tenant_id="default")
    return _llm_engine

def get_query_analyzer():
    """Lazy initialization of Query Analyzer."""
    global _query_analyzer
    if _query_analyzer is None:
        _query_analyzer = QueryAnalyzer()
    return _query_analyzer


def get_db_path() -> str:
    """Get database path."""
    return os.path.join(os.path.dirname(__file__), '..', '..', 'cost_guardian.db')


def transform_to_metrics_format(record: Dict[str, Any]) -> Dict[str, Any]:
    """Transform database record to frontend metrics format."""
    # Extract tags if available
    tags = {}
    if record.get('tags'):
        try:
            import json
            tags = json.loads(record['tags']) if isinstance(record['tags'], str) else record['tags']
        except Exception:
            tags = {}
    
    # Determine resource type from service name
    service_name = record.get('service_name', '').lower()
    resource_type = 'compute'
    if 's3' in service_name or 'storage' in service_name:
        resource_type = 'storage'
    elif 'rds' in service_name or 'database' in service_name:
        resource_type = 'db'
    elif 'slack' in service_name or 'license' in service_name:
        resource_type = 'saas_seat'
    
    # Extract billing tag owner or default to account
    billing_tag_owner = tags.get('Team', tags.get('Owner', record.get('account_id', 'unknown')))
    if billing_tag_owner and not billing_tag_owner.startswith(('team:', 'owner:')):
        billing_tag_owner = f"team:{billing_tag_owner.lower().replace(' ', '_')}"
    
    # Calculate utilization score (placeholder logic - can be enhanced)
    utilization_score = 0.5  # Default
    if record.get('anomaly_flag') and record.get('anomaly_score'):
        utilization_score = max(0.0, min(1.0, 1.0 - float(record.get('anomaly_score', 0.5))))
    elif record.get('usage_quantity'):
        # Simple heuristic: normalize usage quantity (assuming max usage around 1000)
        usage_qty = float(record.get('usage_quantity', 0))
        utilization_score = min(1.0, usage_qty / 1000.0)
    
    # Simplify service name
    service_name_simplified = service_name.replace('Amazon ', '').replace('AWS ', '').upper()
    
    return {
        'timestamp_day': record.get('usage_date', ''),
        'resource_id': record.get('resource_id', f"{service_name}-{record.get('account_id', 'unknown')}"),
        'service_name_simplified': service_name_simplified,
        'billing_tag_owner': billing_tag_owner,
        'unblended_cost_usd': float(record.get('cost', 0.0)),
        'utilization_score': round(utilization_score, 2),
        'resource_type': resource_type
    }


@metrics_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """Get metrics data for dashboard."""
    try:
        db_path = get_db_path()
        if not os.path.exists(db_path):
            return jsonify({'error': 'Database not found'}), 404
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get query parameters
        limit = request.args.get('limit', type=int, default=100)
        offset = request.args.get('offset', type=int, default=0)
        resource_type = request.args.get('resource_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = """
            SELECT 
                usage_date, account_id, service_name, cost, 
                usage_quantity, region, anomaly_flag, anomaly_score,
                resource_id, tags
            FROM daily_usage
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND usage_date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND usage_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY usage_date DESC, cost DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to dicts and transform
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        records = [dict(zip(columns, row)) for row in rows]
        
        # Filter by resource_type if specified
        if resource_type:
            # We'll filter after transformation since resource_type is computed
            metrics = [transform_to_metrics_format(r) for r in records]
            metrics = [m for m in metrics if m['resource_type'] == resource_type]
        else:
            metrics = [transform_to_metrics_format(r) for r in records]
        
        return jsonify(metrics), 200
        
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@metrics_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """Get AI-powered recommendations - reads from DB cache first, then runs on-demand if needed."""
    try:
        # Get query parameters
        status = request.args.get('status')
        resource_type = request.args.get('resource_type')
        query_text = request.args.get('query', 'Analyze cost data and provide specific optimization recommendations with resource details, cost savings, and action items')
        force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
        
        analysis_result = None
        analysis_date = datetime.utcnow().date().isoformat()
        
        # Step 1: Try to get from database cache (if not forcing refresh)
        if not force_refresh:
            try:
                db_path = get_db_path()
                if os.path.exists(db_path):
                    conn = sqlite3.connect(db_path)
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    
                    # Get most recent analysis for this query or default query
                    cursor.execute("""
                        SELECT analysis_result, created_at, engine_used
                        FROM llm_analysis_results
                        WHERE analysis_date = ? AND query_text LIKE ?
                        ORDER BY created_at DESC
                        LIMIT 1
                    """, (analysis_date, f"%{query_text[:50]}%"))
                    
                    row = cursor.fetchone()
                    if row:
                        analysis_result = json.loads(row['analysis_result'])
                        logger.info(f"Using cached analysis from DB (created: {row['created_at']})")
                    conn.close()
            except Exception as e:
                logger.warning(f"Failed to load from DB cache: {e}")
        
        # Step 2: If no cached result, run LLM analysis on-demand
        if not analysis_result or force_refresh:
            try:
                logger.info(f"Running on-demand LLM analysis (force_refresh={force_refresh})...")
                llm_engine = get_llm_engine()
                query_analyzer = get_query_analyzer()
                
                # Get semantic context from vector DB
                query_analysis = query_analyzer.analyze(query_text, top_k=15)
                context_items = query_analysis.get('context', [])
                
                # Run LLM analysis
                analysis_result = llm_engine.analyze(
                    query=query_text,
                    raw_data=None,
                    context=[str(ctx) for ctx in context_items],
                    horizon_days=30,
                    force_refresh=True
                )
                
                logger.info(f"On-demand analysis complete. Engine: {analysis_result.get('engine_used', 'unknown')}")
                
                # Optionally store in DB for future use
                try:
                    db_path = get_db_path()
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT OR REPLACE INTO llm_analysis_results 
                        (analysis_date, query_text, intent, dashboard_type, analysis_result, 
                         engine_used, recommendations_count, anomalies_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        analysis_date,
                        query_text,
                        analysis_result.get('intent', 'insight'),
                        analysis_result.get('dashboard', 'finance'),
                        json.dumps(analysis_result, default=str),
                        analysis_result.get('engine_used', 'unknown'),
                        len(analysis_result.get('recommendations', [])),
                        len(analysis_result.get('anomalies', []))
                    ))
                    conn.commit()
                    conn.close()
                except Exception as e:
                    logger.warning(f"Failed to store analysis in DB: {e}")
                    
            except Exception as ai_error:
                logger.error(f"On-demand LLM analysis failed: {ai_error}", exc_info=True)
                return jsonify({
                    'error': 'AI recommendation service unavailable',
                    'message': str(ai_error)
                }), 503
        
        # Step 3: Transform LLM recommendations to frontend format
        if analysis_result:
            llm_recommendations = analysis_result.get('recommendations', [])
            anomalies = analysis_result.get('anomalies', [])
            summary = analysis_result.get('summary', {})
            
            # Use RecommendationEngine to format for dashboard if needed
            # dashboard_payload = _recommendation_engine.to_dashboard_payload(
            #     analysis_result,
            #     dashboard_type="msp"
            # )
            
            # Convert LLM recommendations to frontend format
            recommendations = []
            for idx, rec in enumerate(llm_recommendations[:50]):
                # Handle both string and dict recommendations from LLM
                if isinstance(rec, str):
                    rec_text = rec
                    # Match recommendation with anomaly data if available
                    if idx < len(anomalies):
                        anomaly = anomalies[idx]
                        resource_id = anomaly.get('resource_id') or anomaly.get('service_name', f"resource-{idx}")
                        cost = float(anomaly.get('cost', 0.0))
                        anomaly_score = float(anomaly.get('anomaly_score', 0.0))
                        # Extract owner and service from anomaly tags/metadata
                        anomaly_tags = anomaly.get('tags', {})
                        anomaly_owner = anomaly_tags.get('Owner') or anomaly_tags.get('owner') or anomaly_tags.get('Team') or anomaly_tags.get('team') or 'Unknown'
                        anomaly_service = anomaly.get('service_name') or 'Unknown'
                    else:
                        resource_id = f"resource-{idx}"
                        cost = 0.0
                        anomaly_score = 0.0
                        anomaly_owner = 'Unknown'
                        anomaly_service = 'Unknown'
                else:
                    rec_text = rec.get('action', rec.get('text', rec.get('recommendation', str(rec))))
                    resource_id = rec.get('resource_id') or rec.get('service_name', f"resource-{idx}")
                    cost = float(rec.get('cost', rec.get('monthly_cost', 0.0)) / 30 if 'monthly_cost' in rec else 0.0)
                    anomaly_score = float(rec.get('anomaly_score', 0.0))
                    # Extract from dict if available - LLM should provide these fields
                    if isinstance(rec, dict):
                        anomaly_owner = rec.get('owner') or rec.get('team') or 'Unknown'
                        anomaly_service = rec.get('service_name') or rec.get('service') or 'Unknown'
                        if 'tags' in rec:
                            rec_tags = rec.get('tags', {})
                            anomaly_owner = rec_tags.get('Owner') or rec_tags.get('owner') or rec_tags.get('Team') or rec_tags.get('team') or anomaly_owner or 'Unknown'
                    else:
                        anomaly_owner = 'Unknown'
                        anomaly_service = 'Unknown'
                
                # Extract service info from resource_id or service_name
                service_name = str(resource_id).lower()
                if 'ec2' in service_name or 'compute' in service_name:
                    resource_type_val = 'compute'
                elif 's3' in service_name or 'storage' in service_name:
                    resource_type_val = 'storage'
                elif 'rds' in service_name or 'database' in service_name or 'db' in service_name:
                    resource_type_val = 'db'
                elif 'slack' in service_name or 'license' in service_name:
                    resource_type_val = 'saas_seat'
                else:
                    resource_type_val = 'compute'
                
                # Determine severity from anomaly score and cost
                monthly_cost = cost * 30 if cost > 0 else summary.get('avg_cost_per_day', 0) * 30
                
                if anomaly_score > 0.8 or monthly_cost > 300:
                    severity = "Critical"
                    savings_percent = 0.30
                elif anomaly_score > 0.5 or monthly_cost > 150:
                    severity = "High"
                    savings_percent = 0.20
                else:
                    severity = "Low"
                    savings_percent = 0.10
                
                # Determine recommendation type from LLM text
                rec_text_lower = rec_text.lower()
                if any(word in rec_text_lower for word in ['resize', 'downsize', 'right-size', 'rightsize']):
                    rec_type = "resize"
                elif any(word in rec_text_lower for word in ['terminate', 'delete', 'remove', 'shut down']):
                    rec_type = "terminate"
                elif any(word in rec_text_lower for word in ['reconfigure', 'configure', 'policy', 'lifecycle']):
                    rec_type = "reconfigure"
                else:
                    rec_type = "optimize"
                
                # Get client/account info from summary
                service_breakdown = summary.get('service_breakdown', {})
                top_services = summary.get('top_services', [])
                client_name = f"Client {summary.get('top_account', idx + 1)}" if top_services else f"Client {idx + 1}"
                
                # Calculate savings from LLM recommendation if available
                if isinstance(rec, dict) and 'savings' in rec:
                    projected_savings = float(rec.get('savings', monthly_cost * savings_percent))
                else:
                    projected_savings = monthly_cost * savings_percent
                
                recommendations.append({
                    'recommendation_id': f"REC-LLM{idx:04d}",
                    'resource_id_impacted': str(resource_id),
                    'resource_type': resource_type_val,
                    'flag_severity': severity,
                    'recommendation_type': rec_type,
                    'current_monthly_cost': round(monthly_cost, 2),
                    'projected_savings_monthly': round(projected_savings, 2),
                    'recommended_action': rec_text[:200],  # Limit length for frontend
                    'action_status': 'pending',
                    'client_name': client_name,
                    # Add owner and service info from anomaly data for frontend matching
                    'owner': anomaly_owner,
                    'service_name_simplified': anomaly_service
                })
            
            # Filter by status if provided
            if status:
                recommendations = [r for r in recommendations if r['action_status'] == status]
            
            # Filter by resource_type if provided
            if resource_type:
                recommendations = [r for r in recommendations if r['resource_type'] == resource_type]
            
            logger.info(f"Returning {len(recommendations)} LLM-generated recommendations")
            return jsonify(recommendations), 200
        else:
            return jsonify({'error': 'No analysis result available'}), 404
        
    except Exception as e:
        logger.error(f"Error fetching recommendations: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500



