"""Background scheduler for daily LLM cost analysis."""

import os
import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from agentic_ai import LLMEvaluator

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")


def get_db_path() -> str:
    """Get database path."""
    return os.path.join(os.path.dirname(__file__), '..', 'cost_guardian.db')


def initialize_analysis_table():
    """Create table for storing LLM analysis results."""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS llm_analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_date TEXT NOT NULL,
                query_text TEXT,
                intent TEXT,
                dashboard_type TEXT,
                analysis_result TEXT NOT NULL,
                engine_used TEXT,
                recommendations_count INTEGER,
                anomalies_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(analysis_date, query_text)
            );
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_analysis_date ON llm_analysis_results(analysis_date DESC);
        """)
        
        conn.commit()
        conn.close()
        logger.info("Analysis results table initialized")
    except Exception as e:
        logger.error(f"Failed to initialize analysis table: {e}")


def run_daily_analysis():
    """Run LLM analysis and store results in database."""
    try:
        logger.info("Starting daily LLM cost analysis...")
        
        # Initialize components
        llm_engine = LLMEvaluator(tenant_id="default")
        
        # Analysis queries - clear instructions for LLM analysis
        queries = [
            "Analyze cost data and provide specific optimization recommendations with resource details, cost savings, and actionable steps for reducing cloud spend",
            "Identify cost anomalies, unexpected spending spikes, low utilization resources, and unusual patterns that require attention",
            "Forecast cost trends and predict spending for the next 30 days based on historical patterns and current usage"
        ]
        
        # Load ALL records from SQLite database once for all analyses
        logger.info("Loading all records from database...")
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM daily_usage ORDER BY usage_date DESC")
        rows = cursor.fetchall()
        all_records = [dict(row) for row in rows]
        conn.close()
        
        if not all_records:
            logger.error("No records found in database. Cannot run analysis.")
            return
        
        logger.info(f"Loaded {len(all_records)} records from database")
        
        analysis_date = datetime.utcnow().date().isoformat()
        
        for query_text in queries:
            try:
                logger.info(f"Analyzing query: {query_text[:50]}...")
                
                # Run LLM analysis on ALL records from database
                analysis_result = llm_engine.analyze(
                    query=query_text,
                    raw_data=all_records,  # Use ALL records from database
                    context=None,  # No vector DB context needed
                    horizon_days=30,
                    force_refresh=True  # Get fresh analysis
                )
                
                # Store in database
                db_path_store = get_db_path()
                conn = sqlite3.connect(db_path_store)
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
                
                logger.info(f"Analysis stored for query: {query_text[:50]}...")
                
            except Exception as e:
                logger.error(f"Failed to analyze query '{query_text[:30]}...': {e}")
        
        logger.info("Daily LLM analysis completed")
        
    except Exception as e:
        logger.error(f"Daily analysis job failed: {e}", exc_info=True)


def start_analysis_scheduler():
    """Start background scheduler for daily analysis."""
    scheduler = BackgroundScheduler(timezone="UTC")
    
    # Run daily at 3:00 AM UTC (after data ingestion)
    scheduler.add_job(
        run_daily_analysis,
        trigger=CronTrigger(hour=3, minute=0),
        id="daily_llm_analysis",
        replace_existing=True,
        misfire_grace_time=3600  # Allow running up to 1 hour late
    )
    
    scheduler.start()
    logger.info("Analysis scheduler started - will run daily at 03:00 UTC")
    return scheduler


if __name__ == "__main__":
    # Initialize table
    initialize_analysis_table()
    
    # Run immediately for testing
    logger.info("Running immediate analysis test...")
    run_daily_analysis()
    
    # Start scheduler
    scheduler = start_analysis_scheduler()
    
    try:
        import time
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        scheduler.shutdown()
        logger.info("Scheduler stopped")

