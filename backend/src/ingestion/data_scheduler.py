# backend/src/ingestion/data_scheduler.py

import os
import json
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import boto3

# ---------------- Configuration ----------------
RAW_DATA_BUCKET = os.environ.get("RAW_DATA_BUCKET", "cost-guardian-data-lake")
PROCESSOR_LAMBDA_NAME = os.environ.get("PROCESSOR_LAMBDA_NAME", "CostGuardianProcessorAgent")
S3_PREFIX = "raw/aws/"

# List of tenants
TENANTS = [
    "client-test-01",
    "client-test-02",
    "client-test-03",
    "client-test-04",
    "client-test-05"
]

# Path to local mock data file (JSONL)
MOCK_DATA_FILE = os.path.join(os.path.dirname(__file__), "mock_data.jsonl")

# ---------------- Initialize S3 Client ----------------
# Use your AWS profile instead of environment variables
s3_client = boto3.Session(profile_name="cost-guardian").client("s3", region_name="us-east-1")

# ---------------- Core Ingestion Logic ----------------
def run_ingestion_for_tenant(tenant_id):
    """
    Reads local mock data, filters for tenant, uploads processed file to S3,
    and simulates the processor agent invocation.
    """
    # Load local mock data
    if not os.path.exists(MOCK_DATA_FILE):
        print(f"❌ Mock data file not found: {MOCK_DATA_FILE}")
        return

    with open(MOCK_DATA_FILE, "r") as f:
        mock_data = [json.loads(line) for line in f]

    # Determine earliest usage_date in mock data
    if mock_data:
        earliest_date = min(row.get("usage_date") for row in mock_data if row.get("usage_date"))
        date_str = earliest_date
    else:
        date_str = (datetime.utcnow() - timedelta(days=2)).strftime('%Y-%m-%d')

    print(f"[{datetime.utcnow()}] Starting ingestion for Tenant: {tenant_id}, Date: {date_str}")

    try:
        # Filter data by tenant (account_id)
        tenant_data = [row for row in mock_data if row.get("account_id") == tenant_id]

        if not tenant_data:
            print(f"⚠️ No tenant-specific mock data found for {tenant_id}, using all mock data")
            tenant_data = mock_data

        # Filter by usage_date
        tenant_data_for_date = [row for row in tenant_data if row.get("usage_date") == date_str]

        if not tenant_data_for_date:
            print(f"⚠️ No mock data for date {date_str}, using all available dates")
            tenant_data_for_date = tenant_data

        # Save tenant data locally (optional, for debugging)
        local_file = f"{tenant_id}_{date_str}_mock_raw.json"
        with open(local_file, "w") as f:
            json.dump(tenant_data_for_date, f, indent=2)

        # Upload processed data to S3
        s3_key = f"{S3_PREFIX}{tenant_id}/{date_str}/raw.json"
        s3_client.upload_file(local_file, RAW_DATA_BUCKET, s3_key)
        print(f"✅ Mock ingestion SUCCESS for {tenant_id}: s3://{RAW_DATA_BUCKET}/{s3_key}")

        # Simulate next agent invocation
        print(f"Simulating invocation of Processor Agent: {PROCESSOR_LAMBDA_NAME}")

    except Exception as e:
        print(f"❌ Mock ingestion FAILED for {tenant_id}: {e}")

# ---------------- Scheduler Setup ----------------
def schedule_daily_mock_ingestion():
    """
    Daily scheduler at 02:00 UTC for all tenants (mock data only).
    """
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
    print("🕒 Scheduler started: Daily mock ingestion at 02:00 UTC for all tenants")

    try:
        while True:
            pass  # keep scheduler running
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler stopped.")

# ---------------- Direct Run ----------------
if __name__ == "__main__":
    for tenant in TENANTS:
        run_ingestion_for_tenant(tenant)

    # Start daily scheduler
    schedule_daily_mock_ingestion()
