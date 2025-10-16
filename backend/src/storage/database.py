"""
Database Layer for Cost Guardian
Simple SQLite database management with proper error handling
"""

import os
import logging
from typing import Dict, List, Any, Optional
from contextlib import contextmanager
from datetime import datetime
import json
import sqlite3

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database manager for SQLite"""
    
    def __init__(self, database_url: str = None):
        """Initialize database manager"""
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///cost_guardian.db')
        self.db_path = self.database_url.replace('sqlite:///', '')
        logger.info(f"Initialized SQLite database: {self.db_path}")
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper cleanup"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = None, fetch: str = 'all') -> Optional[List[Dict]]:
        """Execute a SELECT query and return results"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                
                if fetch == 'all':
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
                elif fetch == 'one':
                    result = cursor.fetchone()
                    return dict(result) if result else None
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise DatabaseError(f"Query execution failed: {e}")
    
    def execute_insert(self, query: str, params: tuple = None) -> bool:
        """Execute an INSERT query"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Insert execution failed: {e}")
            raise DatabaseError(f"Insert execution failed: {e}")
    
    def execute_batch_insert(self, query: str, params_list: List[tuple]) -> bool:
        """Execute batch INSERT operations"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Batch insert execution failed: {e}")
            raise DatabaseError(f"Batch insert execution failed: {e}")
    
    def initialize_schema(self):
        """Initialize database with schema"""
        try:
            schema_sql = """
                CREATE TABLE IF NOT EXISTS daily_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id TEXT NOT NULL,
                    service_name TEXT NOT NULL,
                    usage_date TEXT NOT NULL,
                    usage_quantity REAL,
                    cost REAL,
                    currency TEXT DEFAULT 'USD',
                    region TEXT,
                    resource_id TEXT,
                    tags TEXT,
                    billing_period TEXT,
                    anomaly_flag BOOLEAN DEFAULT FALSE,
                    anomaly_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(account_id, service_name, usage_date)
                );
                
                CREATE INDEX IF NOT EXISTS idx_daily_usage_date ON daily_usage(usage_date);
                CREATE INDEX IF NOT EXISTS idx_daily_usage_account ON daily_usage(account_id);
                CREATE INDEX IF NOT EXISTS idx_daily_usage_service ON daily_usage(service_name);
            """
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executescript(schema_sql)
                conn.commit()
            
            logger.info("Database schema initialized successfully")
            
        except Exception as e:
            logger.error(f"Schema initialization failed: {e}")
            raise DatabaseError(f"Schema initialization failed: {e}")

class DatabaseError(Exception):
    """Custom database exception"""
    pass

# Global database manager instance
db_manager = None

def get_db_manager() -> DatabaseManager:
    """Get global database manager instance"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager

def init_database():
    """Initialize database with schema"""
    db = get_db_manager()
    db.initialize_schema()
    logger.info("Database initialization completed")
