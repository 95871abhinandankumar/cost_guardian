"""
AWSConnector Utility
--------------------
Provides wrapper functions for interacting with AWS services (S3, EC2, CloudWatch, Cost Explorer),
and loading mock data for local testing.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import boto3
from botocore.exceptions import BotoCoreError, ClientError

# --------------------------- Logging Configuration --------------------------- #
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class AWSConnector:
    """AWS Service Connector."""

    def __init__(self, profile_name: Optional[str] = None, region_name: str = "us-east-2") -> None:
        """Initialize AWS session and clients."""
        session_args = {}

        profile = profile_name or os.environ.get("AWS_PROFILE")
        region = region_name or os.environ.get("AWS_DEFAULT_REGION", "us-east-2")

        if profile:
            session_args["profile_name"] = profile
        if region:
            session_args["region_name"] = region

        try:
            self.session = boto3.Session(**session_args)
            self.s3 = self.session.client("s3")
            self.ec2 = self.session.client("ec2")
            self.cloudwatch = self.session.client("cloudwatch")
            self.ce = self.session.client("ce")  # Cost Explorer
            logger.info("AWSConnector initialized successfully with profile '%s', region '%s'", profile_name, region_name)
        except Exception as e:
            logger.critical("Failed to initialize AWSConnector: %s", e, exc_info=True)
            raise

    # ---------------- S3 ----------------
    def upload_file_to_s3(self, local_file: str, bucket: str, key: str) -> None:
        """Upload a local file to S3."""
        try:
            if not os.path.exists(local_file):
                raise FileNotFoundError(f"Local file not found: {local_file}")
            self.s3.upload_file(local_file, bucket, key)
            logger.info("Uploaded %s → s3://%s/%s", local_file, bucket, key)
        except (BotoCoreError, ClientError, FileNotFoundError) as e:
            logger.error("Failed to upload file to S3: %s", e, exc_info=True)

    # ---------------- Mock Loader ----------------
    def load_mock_file(self, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Load mock data from JSON or JSONL file.
        Defaults to ../data/raw_data.json if no path provided.
        """
        if file_path is None:
            file_path = os.path.join(os.path.dirname(__file__), "../data/raw_data.json")

        if not os.path.exists(file_path):
            logger.error("Mock file not found: %s", file_path)
            return []

        try:
            if file_path.endswith(".jsonl"):
                with open(file_path, "r", encoding="utf-8") as f:
                    data = [json.loads(line.strip()) for line in f if line.strip()]
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            logger.info("Loaded %d rows from mock file: %s", len(data), file_path)
            return data
        except json.JSONDecodeError as e:
            logger.error("JSON parsing error in %s: %s", file_path, e)
            return []
        except Exception as e:
            logger.error("Error reading mock file %s: %s", file_path, e, exc_info=True)
            return []

    def get_mock_data_for_tenant(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Return tenant-specific mock data (or all mock data if none match)."""
        all_data = self.load_mock_file()
        tenant_data = [row for row in all_data if row.get("account_id") == tenant_id] or all_data
        if not tenant_data:
            logger.warning("No tenant-specific mock data found for %s; using all mock data", tenant_id)
        return tenant_data

    # ---------------- EC2 ----------------
    def list_instances(self) -> List[Dict[str, Any]]:
        """Return all EC2 instances with InstanceId, Name tag, and State."""
        try:
            response = self.ec2.describe_instances()
            instances = []
            for reservation in response.get("Reservations", []):
                for inst in reservation.get("Instances", []):
                    name = next((tag["Value"] for tag in inst.get("Tags", []) if tag["Key"] == "Name"), None)
                    instances.append({
                        "InstanceId": inst["InstanceId"],
                        "Name": name,
                        "State": inst["State"]["Name"],
                        "InstanceType": inst.get("InstanceType"),
                        "LaunchTime": inst.get("LaunchTime").isoformat() if inst.get("LaunchTime") else None,
                        "Architecture": inst.get("Architecture")
                    })
            if not instances:
                logger.warning("No EC2 instances found.")
            return instances
        except Exception as e:
            logger.error("Error fetching EC2 instances: %s", e, exc_info=True)
            return []

    # ---------------- CloudWatch ----------------
    def get_ec2_metrics(
        self,
        instance_id: str,
        metric_names: Optional[List[str]] = None,
        period: int = 300
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch multiple EC2 metrics from CloudWatch."""
        if metric_names is None:
            metric_names = ["CPUUtilization", "NetworkIn", "NetworkOut", "DiskReadOps", "DiskWriteOps"]

        metrics_data = {}
        try:
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
                datapoints = [
                    {**dp, "Timestamp": dp["Timestamp"].isoformat()} for dp in response.get("Datapoints", [])
                ]
                metrics_data[metric_name] = datapoints
            return metrics_data
        except Exception as e:
            logger.error("Error fetching CloudWatch metrics for %s: %s", instance_id, e, exc_info=True)
            return {}

    # ---------------- Cost Explorer ----------------
    def get_cost(
        self,
        start_date: str,
        end_date: str,
        granularity: str = "DAILY",
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Fetch cost & usage metrics from AWS Cost Explorer."""
        if metrics is None:
            metrics = ["UnblendedCost", "UsageQuantity", "BlendedCost", "AmortizedCost", "NetAmortizedCost"]

        try:
            response = self.ce.get_cost_and_usage(
                TimePeriod={"Start": start_date, "End": end_date},
                Granularity=granularity,
                Metrics=metrics
            )
            if not response.get("ResultsByTime"):
                logger.warning("Cost Explorer returned empty; fallback to mock data may be required.")
            return response
        except Exception as e:
            logger.error("Error fetching Cost Explorer data: %s", e, exc_info=True)
            return {}
