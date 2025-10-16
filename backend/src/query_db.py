#!/usr/bin/env python3
"""
Database Query Script for Cost Guardian
Simple script to query the aggregated data from SQLite database
"""

import sqlite3
import json
from datetime import datetime

def query_database():
    """Query the aggregated data from SQLite database"""
    try:
        # Connect to database
        conn = sqlite3.connect('cost_guardian.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("Querying Cost Guardian Database...")
        
        # Get total records
        cursor.execute("SELECT COUNT(*) as count FROM daily_usage")
        total_records = cursor.fetchone()['count']
        print(f"Total aggregated records: {total_records}")
        
        # Get cost summary
        cursor.execute("""
            SELECT 
                SUM(cost) as total_cost,
                AVG(cost) as avg_cost,
                COUNT(DISTINCT account_id) as unique_accounts,
                COUNT(DISTINCT service_name) as unique_services,
                COUNT(CASE WHEN anomaly_flag = 1 THEN 1 END) as anomalies
            FROM daily_usage
        """)
        summary = cursor.fetchone()
        
        print(f"Total cost: ${summary['total_cost']:.2f}")
        print(f"Average daily cost: ${summary['avg_cost']:.2f}")
        print(f"Unique accounts: {summary['unique_accounts']}")
        print(f"Unique services: {summary['unique_services']}")
        print(f"Anomalies detected: {summary['anomalies']}")
        
        # Get service breakdown
        print("\nService Breakdown:")
        cursor.execute("""
            SELECT 
                service_name,
                SUM(cost) as total_cost,
                COUNT(*) as record_count,
                COUNT(CASE WHEN anomaly_flag = 1 THEN 1 END) as anomalies
            FROM daily_usage
            GROUP BY service_name
            ORDER BY total_cost DESC
        """)
        
        services = cursor.fetchall()
        for service in services:
            print(f"   {service['service_name']}: ${service['total_cost']:.2f} ({service['record_count']} records, {service['anomalies']} anomalies)")
        
        # Get account breakdown
        print("\nAccount Breakdown:")
        cursor.execute("""
            SELECT 
                account_id,
                SUM(cost) as total_cost,
                COUNT(*) as record_count
            FROM daily_usage
            GROUP BY account_id
            ORDER BY total_cost DESC
        """)
        
        accounts = cursor.fetchall()
        for account in accounts:
            print(f"   {account['account_id']}: ${account['total_cost']:.2f} ({account['record_count']} records)")
        
        # Get recent daily trends
        print("\nRecent Daily Trends (Last 5 days):")
        cursor.execute("""
            SELECT 
                usage_date,
                SUM(cost) as daily_cost,
                COUNT(*) as record_count,
                COUNT(CASE WHEN anomaly_flag = 1 THEN 1 END) as anomalies
            FROM daily_usage
            GROUP BY usage_date
            ORDER BY usage_date DESC
            LIMIT 5
        """)
        
        trends = cursor.fetchall()
        for trend in trends:
            print(f"   {trend['usage_date']}: ${trend['daily_cost']:.2f} ({trend['record_count']} records, {trend['anomalies']} anomalies)")
        
        conn.close()
        print("\nDatabase query completed successfully!")
        
    except Exception as e:
        print(f"Database query failed: {e}")

if __name__ == '__main__':
    query_database()
