"""
Data Scheduler - Mock Ingestion
--------------------------------
Reads local mock AWS cost data, filters by tenant and date, uploads to S3,
and simulates invocation of a processor agent. Supports daily scheduling.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List
from apscheduler.schedulers.background import BackgroundScheduler
import boto3
from botocore.exceptions import BotoCoreError, ClientError

# --------------------------- Logging Configuration --------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# --------------------------- Environment Config ----------------------------- #
RAW_DATA_BUCKET = os.getenv("RAW_DATA_BUCKET", "cost-guardian-data-lake")
PROCESSOR_LAMBDA_NAME = os.getenv("PROCESSOR_LAMBDA_NAME", "CostGuardianProcessorAgent")
AWS_PROFILE = os.getenv("AWS_PROFILE", "cost-guardian")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
S3_PREFIX = "raw/aws/"
MOCK_DATA_FILE = os.path.join(os.path.dirname(__file__), "../data/raw_data.json")

TENANTS: List[str] = [
    "client-test-01",
    "client-test-02",
    "client-test-03",
    "client-test-04",
    "client-test-05",
]

# --------------------------- AWS S3 Client Setup ---------------------------- #
try:
    s3_client = boto3.Session(profile_name=AWS_PROFILE).client("s3", region_name=AWS_REGION)
    logger.info("Initialized S3 client with profile '%s' and region '%s'", AWS_PROFILE, AWS_REGION)
except Exception as e:
    logger.critical("Failed to initialize S3 client: %s", e, exc_info=True)
    raise

# --------------------------- Core Ingestion Logic --------------------------- #
def run_ingestion_for_tenant(tenant_id: str) -> None:
    """
    Reads local mock data, filters for tenant and date, uploads processed file to S3,
    and simulates the processor agent invocation.
    """
    try:
        if not os.path.exists(MOCK_DATA_FILE):
            logger.error("Mock data file not found: %s", MOCK_DATA_FILE)
            return

        with open(MOCK_DATA_FILE, "r") as f:
            mock_data = json.load(f)

        if not mock_data:
            logger.warning("Mock data file is empty, using default date fallback")
            date_str = (datetime.utcnow() - timedelta(days=2)).strftime("%Y-%m-%d")
        else:
            earliest_date = min(row.get("usage_date") for row in mock_data if row.get("usage_date"))
            date_str = earliest_date or (datetime.utcnow() - timedelta(days=2)).strftime("%Y-%m-%d")

        logger.info("Starting ingestion for Tenant: %s, Date: %s", tenant_id, date_str)

        # Filter tenant-specific data
        tenant_data = [row for row in mock_data if row.get("account_id") == tenant_id] or mock_data

        # Filter by usage_date
        tenant_data_for_date = [row for row in tenant_data if row.get("usage_date") == date_str] or tenant_data

        # Save locally for debugging
        local_file = f"{tenant_id}_{date_str}_mock_raw.json"
        with open(local_file, "w") as f:
            json.dump(tenant_data_for_date, f, indent=2)

        # Upload to S3
        s3_key = f"{S3_PREFIX}{tenant_id}/{date_str}/raw.json"
        s3_client.upload_file(local_file, RAW_DATA_BUCKET, s3_key)
        logger.info("Mock ingestion SUCCESS for %s: s3://%s/%s", tenant_id, RAW_DATA_BUCKET, s3_key)

        # Simulate next processor agent invocation
        logger.info("Simulating Processor Agent: %s", PROCESSOR_LAMBDA_NAME)

    except (BotoCoreError, ClientError) as aws_err:
        logger.error("AWS S3 error for tenant '%s': %s", tenant_id, aws_err, exc_info=True)
    except Exception as e:
        logger.error("Mock ingestion FAILED for tenant '%s': %s", tenant_id, e, exc_info=True)


# --------------------------- Scheduler Setup ------------------------------- #
def schedule_daily_mock_ingestion() -> None:
    """
    Schedule daily mock ingestion at 02:00 UTC for all tenants.
    """
    scheduler = BackgroundScheduler(timezone="UTC")

    for tenant in TENANTS:
        scheduler.add_job(
            run_ingestion_for_tenant,
            trigger="cron",
            hour=2,
            minute=0,
            args=[tenant],
            id=f"mock_ingestion_{tenant}",
            replace_existing=True,
        )

    scheduler.start()
    logger.info("Scheduler started: Daily mock ingestion at 02:00 UTC for all tenants")

    try:
        scheduler._thread.join()  # Keep scheduler running
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler stopped.")


# --------------------------- Direct Run ------------------------------------ #
if __name__ == "__main__":
    # Run ingestion for all tenants immediately
    for tenant in TENANTS:
        run_ingestion_for_tenant(tenant)

    # Start scheduler
    schedule_daily_mock_ingestion()
