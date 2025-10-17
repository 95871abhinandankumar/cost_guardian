# backend/src/ingestion/connector.py
import boto3
import json
from datetime import datetime, timedelta
import os

class AWSConnector:
    def __init__(self, profile_name=None, region_name="us-east-2"):
        session_args = {}
        if profile_name:
            session_args["profile_name"] = profile_name
        if region_name:
            session_args["region_name"] = region_name

        self.session = boto3.Session(**session_args)
        self.s3 = self.session.client("s3")
        self.ec2 = self.session.client("ec2")
        self.cloudwatch = self.session.client("cloudwatch")
        self.ce = self.session.client("ce")  # Cost Explorer

    # ---------------- S3 ----------------
    def upload_file_to_s3(self, local_file, bucket, key):
        """Upload a local file to S3"""
        self.s3.upload_file(local_file, bucket, key)
        print(f"✅ Uploaded {local_file} → s3://{bucket}/{key}")

    # ---------------- Mock Loader ----------------
    def load_mock_file(self, file_path=None):
        """
        Load mock data from JSON or JSONL file.
        Defaults to ../data/raw_data.json if no path provided.
        """
        if file_path is None:
            file_path = os.path.join(os.path.dirname(__file__), "../data/raw_data.json")

        if not os.path.exists(file_path):
            print(f"❌ Mock file not found: {file_path}")
            return []

        try:
            if file_path.endswith(".jsonl"):
                # JSON Lines format
                with open(file_path, "r") as f:
                    data = [json.loads(line) for line in f]
            else:
                # Standard JSON array format
                with open(file_path, "r") as f:
                    data = json.load(f)
            print(f"✅ Loaded {len(data)} rows from mock file: {file_path}")
            return data
        except Exception as e:
            print(f"❌ Error reading mock file {file_path}: {e}")
            return []

    def get_mock_data_for_tenant(self, tenant_id):
        """Return tenant-specific mock data (or all mock data if none match)"""
        all_data = self.load_mock_file()
        tenant_data = [row for row in all_data if row.get("account_id") == tenant_id]
        if not tenant_data:
            print(f"⚠️ No tenant-specific mock data found for {tenant_id}, using all mock data")
            tenant_data = all_data
        return tenant_data

    # ---------------- EC2 ----------------
    def list_instances(self):
        """Return all EC2 instances with InstanceId, Name tag, and State"""
        try:
            response = self.ec2.describe_instances()
            instances = []
            for reservation in response.get("Reservations", []):
                for inst in reservation.get("Instances", []):
                    name = None
                    if "Tags" in inst:
                        for tag in inst["Tags"]:
                            if tag["Key"] == "Name":
                                name = tag["Value"]
                                break
                    instances.append({
                        "InstanceId": inst["InstanceId"],
                        "Name": name,
                        "State": inst["State"]["Name"],
                        "InstanceType": inst.get("InstanceType"),
                        "LaunchTime": inst.get("LaunchTime").isoformat() if inst.get("LaunchTime") else None,
                        "Architecture": inst.get("Architecture")
                    })
            if not instances:
                print("⚠️ No EC2 instances found, will fallback to mock data if available.")
            return instances
        except Exception as e:
            print(f"❌ Error fetching EC2 instances: {e}")
            return []

    # ---------------- CloudWatch ----------------
    def get_ec2_metrics(self, instance_id, metric_names=None, period=300):
        """Fetch multiple EC2 metrics from CloudWatch"""
        if metric_names is None:
            metric_names = ["CPUUtilization", "NetworkIn", "NetworkOut", "DiskReadOps", "DiskWriteOps"]

        metrics_data = {}
        for metric_name in metric_names:
            response = self.cloudwatch.get_metric_statistics(
                Namespace="AWS/EC2",
                MetricName=metric_name,
                Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                StartTime=datetime.utcnow() - timedelta(days=1),
                EndTime=datetime.utcnow(),
                Period=period,
                Statistics=["Average"],
            )
            datapoints = []
            for dp in response.get("Datapoints", []):
                dp["Timestamp"] = dp["Timestamp"].isoformat()
                datapoints.append(dp)
            metrics_data[metric_name] = datapoints
        return metrics_data

    # ---------------- Cost Explorer ----------------
    def get_cost(self, start_date, end_date, granularity="DAILY", metrics=None):
        """Fetch cost & usage metrics"""
        if metrics is None:
            metrics = ["UnblendedCost", "UsageQuantity", "BlendedCost", "AmortizedCost", "NetAmortizedCost"]

        try:
            response = self.ce.get_cost_and_usage(
                TimePeriod={"Start": start_date, "End": end_date},
                Granularity=granularity,
                Metrics=metrics,
            )
            if not response.get("ResultsByTime"):
                print("⚠️ Cost Explorer returned empty, fallback to mock data if available.")
            return response
        except Exception as e:
            print(f"❌ Error fetching Cost Explorer data: {e}")
            return {}
