# backend/src/ingestion/aws_data_collector.py

from datetime import datetime, timedelta
from .connector import AWSConnector

def fetch_raw_data_for_tenant(tenant_id, date_str):
    """
    Fetch EC2 instance details, CloudWatch metrics, and Cost Explorer data.
    """
    aws_conn = AWSConnector(profile_name="cost-guardian", region_name="us-east-2")

    # 1️⃣ Fetch EC2 instances
    all_instances = aws_conn.list_instances()
    tenant_instances = [i for i in all_instances if i.get("Tags") and any(t["Value"] == tenant_id for t in i["Tags"])]

    # 2️⃣ Fetch CloudWatch metrics
    metrics_data = []
    for inst in tenant_instances:
        metrics = aws_conn.get_ec2_metrics(inst["InstanceId"])
        metrics_data.append({"InstanceId": inst["InstanceId"], "Metrics": metrics})

    # 3️⃣ Fetch Cost Explorer
    start_date = date_str
    end_date = (datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    cost_data = aws_conn.get_cost(start_date=start_date, end_date=end_date)

    # 4️⃣ Compose final JSON
    raw_data = {
        "tenant_id": tenant_id,
        "data_date": date_str,
        "ec2_instances": tenant_instances,
        "cloudwatch_metrics": metrics_data,
        "cost_data": cost_data,
    }

    return raw_data
