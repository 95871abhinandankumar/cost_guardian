# backend/src/ingestion/data_scheduler.py
"""Data ingestion scheduler for automated AWS data collection."""

import os
import json
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import boto3
from typing import List

# Configuration
RAW_DATA_BUCKET = os.environ.get("RAW_DATA_BUCKET", "cost-guardian-data-lake")
PROCESSOR_LAMBDA_NAME = os.environ.get("PROCESSOR_LAMBDA_NAME", "CostGuardianProcessorAgent")
S3_PREFIX = "raw/aws/"

# Tenant list
TENANTS = [
    "client-test-01",
    "client-test-02", 
    "client-test-03",
    "client-test-04",
    "client-test-05"
]

# Mock data file path
MOCK_DATA_FILE = os.path.join(os.path.dirname(__file__), "../data/raw_data.json")

# Initialize S3 client
s3_client = boto3.Session(profile_name=os.environ.get("AWS_PROFILE")).client("s3", region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"))
logger = logging.getLogger(__name__)

def run_ingestion_for_tenant(tenant_id: str) -> None:
    """Run data ingestion for a specific tenant."""
    if not os.path.exists(MOCK_DATA_FILE):
        logger.error(f"Mock data file not found: {MOCK_DATA_FILE}")
        return

    with open(MOCK_DATA_FILE, "r") as f:
        mock_data = json.load(f)

    # Determine earliest usage_date in mock data
    if mock_data:
        earliest_date = min(row.get("usage_date") for row in mock_data if row.get("usage_date"))
        date_str = earliest_date
    else:
        date_str = (datetime.utcnow() - timedelta(days=2)).strftime('%Y-%m-%d')

    logger.info(f"Starting ingestion for tenant: {tenant_id}, date: {date_str}")

    try:
        # Filter data by tenant
        tenant_data = [row for row in mock_data if row.get("account_id") == tenant_id]

        if not tenant_data:
            logger.warning(f"No tenant-specific data for {tenant_id}, using all data")
            tenant_data = mock_data

        # Filter by usage_date
        tenant_data_for_date = [row for row in tenant_data if row.get("usage_date") == date_str]

        if not tenant_data_for_date:
            logger.warning(f"No data for date {date_str}, using all dates")
            tenant_data_for_date = tenant_data

        # Save tenant data locally
        local_file = f"{tenant_id}_{date_str}_mock_raw.json"
        with open(local_file, "w") as f:
            json.dump(tenant_data_for_date, f, indent=2)

        # Upload to S3
        s3_key = f"{S3_PREFIX}{tenant_id}/{date_str}/raw.json"
        s3_client.upload_file(local_file, RAW_DATA_BUCKET, s3_key)
        logger.info(f"Ingestion successful for {tenant_id}: s3://{RAW_DATA_BUCKET}/{s3_key}")

        # Simulate processor agent invocation
        logger.info(f"Simulating invocation of {PROCESSOR_LAMBDA_NAME}")

    except Exception as e:
        logger.error(f"Ingestion failed for {tenant_id}: {e}")

def schedule_daily_mock_ingestion() -> None:
    """Schedule daily data ingestion at 02:00 UTC for all tenants."""
    scheduler = BackgroundScheduler(timezone="UTC")
    
    for tenant in TENANTS:
        scheduler.add_job(
            run_ingestion_for_tenant,
            'cron',
            hour=2,
            minute=0,
            args=[tenant],
            id=f"mock_ingestion_{tenant}",
            replace_existing=True
        )
    
    scheduler.start()
    logger.info("Scheduler started: Daily ingestion at 02:00 UTC")

    try:
        while True:
            pass  # Keep scheduler running
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler stopped")

if __name__ == "__main__":
    # Run ingestion for all tenants
    for tenant in TENANTS:
        run_ingestion_for_tenant(tenant)

    # Start daily scheduler
    schedule_daily_mock_ingestion()
