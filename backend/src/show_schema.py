#!/usr/bin/env python3
"""
Database Schema Viewer for Cost Guardian
Displays comprehensive database structure and statistics
"""

import sqlite3
import json
from datetime import datetime

def show_database_schema():
    """Display all tables and their structure"""
    try:
        # Connect to database
        conn = sqlite3.connect('cost_guardian.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("Cost Guardian Database Schema")
        print("=" * 50)
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"Total Tables: {len(tables)}")
        print()
        
        for table in tables:
            table_name = table['name']
            print(f"Table: {table_name}")
            print("-" * 30)
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print("Columns:")
            for col in columns:
                nullable = "NULL" if col['notnull'] == 0 else "NOT NULL"
                default = f" DEFAULT {col['dflt_value']}" if col['dflt_value'] is not None else ""
                print(f"  - {col['name']} ({col['type']}) {nullable}{default}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            row_count = cursor.fetchone()['count']
            print(f"  Rows: {row_count}")
            
            # Get indexes
            cursor.execute(f"PRAGMA index_list({table_name})")
            indexes = cursor.fetchall()
            if indexes:
                print("  Indexes:")
                for idx in indexes:
                    print(f"    - {idx['name']} ({'UNIQUE' if idx['unique'] else 'NON-UNIQUE'})")
            
            print()
        
        # Show sample data from daily_usage table
        print("Sample Data from daily_usage table:")
        print("-" * 40)
        cursor.execute("""
            SELECT 
                account_id, service_name, usage_date, 
                cost, usage_quantity, anomaly_flag, anomaly_score
            FROM daily_usage 
            ORDER BY usage_date DESC, cost DESC 
            LIMIT 5
        """)
        
        sample_data = cursor.fetchall()
        for row in sample_data:
            anomaly_text = f"ANOMALY (Score: {row['anomaly_score']})" if row['anomaly_flag'] else "NORMAL"
            print(f"  {row['usage_date']} | {row['account_id']} | {row['service_name']} | ${row['cost']:.2f} | {row['usage_quantity']} | {anomaly_text}")
        
        print()
        
        # Show table statistics
        print("Table Statistics:")
        print("-" * 20)
        cursor.execute("""
            SELECT 
                'daily_usage' as table_name,
                COUNT(*) as total_records,
                COUNT(DISTINCT account_id) as unique_accounts,
                COUNT(DISTINCT service_name) as unique_services,
                COUNT(DISTINCT usage_date) as unique_dates,
                SUM(cost) as total_cost,
                COUNT(CASE WHEN anomaly_flag = 1 THEN 1 END) as anomaly_records
            FROM daily_usage
        """)
        
        stats = cursor.fetchone()
        print(f"  Total Records: {stats['total_records']}")
        print(f"  Unique Accounts: {stats['unique_accounts']}")
        print(f"  Unique Services: {stats['unique_services']}")
        print(f"  Unique Dates: {stats['unique_dates']}")
        print(f"  Total Cost: ${stats['total_cost']:.2f}")
        print(f"  Anomaly Records: {stats['anomaly_records']}")
        
        conn.close()
        print("\nDatabase schema displayed successfully!")
        
    except Exception as e:
        print(f"Failed to display database schema: {e}")

if __name__ == '__main__':
    show_database_schema()
