# backend/src/ingestion/connector.py
import boto3
from datetime import datetime, timedelta

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
        self.s3.upload_file(local_file, bucket, key)
        print(f"Uploaded {local_file} -> s3://{bucket}/{key}")

    # ---------------- EC2 ----------------
    def list_instances(self):
        """Return all EC2 instances with InstanceId, Name tag, and State"""
        response = self.ec2.describe_instances()
        instances = []
        for reservation in response.get("Reservations", []):
            for inst in reservation.get("Instances", []):
                # Extract Name tag if exists
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
        return instances

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
            # Convert timestamps to string
            datapoints = []
            for dp in response.get("Datapoints", []):
                dp["Timestamp"] = dp["Timestamp"].isoformat()
                datapoints.append(dp)
            metrics_data[metric_name] = datapoints
        return metrics_data

    # ---------------- Cost Explorer ----------------
    def get_cost(self, start_date, end_date, granularity="DAILY", metrics=None):
        """Fetch all cost & usage metrics automatically"""
        if metrics is None:
            metrics = ["UnblendedCost", "UsageQuantity", "BlendedCost", "AmortizedCost", "NetAmortizedCost"]

        response = self.ce.get_cost_and_usage(
            TimePeriod={"Start": start_date, "End": end_date},
            Granularity=granularity,
            Metrics=metrics,
        )
        return response
