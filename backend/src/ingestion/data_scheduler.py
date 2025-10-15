# backend/src/ingestion/data_scheduler.py
import os
import json
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from .connector import AWSConnector

RAW_DATA_BUCKET = os.environ.get("RAW_DATA_BUCKET", "cost-guardian-data-lake")
PROCESSOR_LAMBDA_NAME = os.environ.get("PROCESSOR_LAMBDA_NAME", "CostGuardianProcessor")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-2")
S3_PREFIX = "raw/aws/"

def json_converter(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def run_ingestion_logic(event=None, context=None):
    date_str = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
    print(f"[{datetime.utcnow()}] Starting ingestion for Date: {date_str}")

    try:
        aws_conn = AWSConnector(profile_name="cost-guardian", region_name=AWS_REGION)

        # ✅ 1. List all EC2 instances automatically
        instances = aws_conn.list_instances()
        print(f"Found {len(instances)} EC2 instances")

        # ✅ 2. Fetch CloudWatch metrics for all instances
        metrics_data = []
        for inst in instances:
            metrics = aws_conn.get_ec2_metrics(inst["InstanceId"])
            metrics_data.append({
                "InstanceId": inst["InstanceId"],
                "Name": inst.get("Name"),
                "Metrics": metrics,
                "State": inst.get("State"),
                "InstanceType": inst.get("InstanceType"),
                "LaunchTime": inst.get("LaunchTime"),
                "Architecture": inst.get("Architecture")
            })

        # ✅ 3. Fetch Cost Explorer automatically
        start_date = date_str
        end_date = (datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
        cost_data = aws_conn.get_cost(start_date=start_date, end_date=end_date)

        # ✅ 4. Compose final JSON
        raw_data = {
            "data_date": date_str,
            "instances": metrics_data,
            "cost": cost_data
        }

        # ✅ 5. Save locally
        local_file = f"aws_data_{date_str}.json"
        with open(local_file, "w") as f:
            json.dump(raw_data, f, indent=2, default=json_converter)

        # ✅ 6. Upload to S3
        s3_key = f"{S3_PREFIX}all_instances/{date_str}/raw.json"
        aws_conn.upload_file_to_s3(local_file, RAW_DATA_BUCKET, s3_key)

        print(f"Simulating invocation of Processor Agent: {PROCESSOR_LAMBDA_NAME}")

        return {"status": "SUCCESS", "s3_key": s3_key, "bucket": RAW_DATA_BUCKET}

    except Exception as e:
        print(f"❌ Ingestion Agent Failed: {e}")
        return {"status": "FAILED", "error": str(e)}

def start_daily_scheduler():
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(run_ingestion_logic, 'cron', hour=2, minute=0)
    scheduler.start()
    print("✅ Daily ingestion scheduler started (02:00 UTC).")
    return scheduler

if __name__ == "__main__":
    result = run_ingestion_logic()
    print("Manual run result:", result)

    scheduler = start_daily_scheduler()
    print("Scheduler is running. Press Ctrl+C to exit.")
    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler stopped.")
