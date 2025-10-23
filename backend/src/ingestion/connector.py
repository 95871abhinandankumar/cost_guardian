# backend/src/ingestion/connector.py
"""AWS Connector for S3, EC2, CloudWatch, and Cost Explorer."""

import boto3
import json
import logging
from datetime import datetime, timedelta
import os
from typing import List, Dict, Any, Optional

class AWSConnector:
    """AWS Service Connector."""
    
    def __init__(self, profile_name: Optional[str] = None, region_name: Optional[str] = None):
        """Initialize AWS Connector with optional profile and region."""
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
            self.ce = self.session.client("ce")
            
            self.logger = logging.getLogger(__name__)
            self._validate_credentials()
            
        except Exception as e:
            self.logger = logging.getLogger(__name__)
            self.logger.error(f"Failed to initialize AWS Connector: {e}")
            raise ValueError(f"Invalid AWS configuration: {e}")
    
    def _validate_credentials(self) -> None:
        """Validate AWS credentials."""
        try:
            self.s3.list_buckets()
            self.logger.info("AWS credentials validated")
        except Exception as e:
            self.logger.warning(f"AWS credential validation failed: {e}")

    # ---------------- S3 Operations ----------------
    def upload_file_to_s3(self, local_file: str, bucket: str, key: str) -> bool:
        """Upload file to S3."""
        try:
            if not os.path.exists(local_file):
                raise FileNotFoundError(f"Local file not found: {local_file}")
                
            self.s3.upload_file(local_file, bucket, key)
            self.logger.info(f"Uploaded {local_file} to s3://{bucket}/{key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to upload {local_file} to S3: {e}")
            return False

    # ---------------- Mock Data Operations ----------------
    def load_mock_file(self, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Load mock data from JSON/JSONL file."""
        if file_path is None:
            file_path = os.path.join(os.path.dirname(__file__), "../data/raw_data.json")

        if not os.path.exists(file_path):
            self.logger.warning(f"Mock data file not found: {file_path}")
            return []

        try:
            if file_path.endswith(".jsonl"):
                with open(file_path, "r", encoding="utf-8") as f:
                    data = [json.loads(line.strip()) for line in f if line.strip()]
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
            self.logger.info(f"Loaded {len(data)} records from {file_path}")
            return data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error in {file_path}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error reading {file_path}: {e}")
            return []

    def get_mock_data_for_tenant(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Get tenant-specific mock data."""
        all_data = self.load_mock_file()
        tenant_data = [row for row in all_data if row.get("account_id") == tenant_id]
        
        if not tenant_data:
            self.logger.warning(f"No data for tenant {tenant_id}, using all data")
            tenant_data = all_data
        else:
            self.logger.info(f"Found {len(tenant_data)} records for tenant {tenant_id}")
            
        return tenant_data

    # ---------------- EC2 Operations ----------------
    def list_instances(self) -> List[Dict[str, Any]]:
        """Get all EC2 instances."""
        try:
            response = self.ec2.describe_instances()
            instances = []
            
            for reservation in response.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    name = None
                    if "Tags" in instance:
                        for tag in instance["Tags"]:
                            if tag["Key"] == "Name":
                                name = tag["Value"]
                                break
                    
                    instance_info = {
                        "InstanceId": instance["InstanceId"],
                        "Name": name,
                        "State": instance["State"]["Name"],
                        "InstanceType": instance.get("InstanceType"),
                        "LaunchTime": instance.get("LaunchTime").isoformat() if instance.get("LaunchTime") else None,
                        "Architecture": instance.get("Architecture")
                    }
                    instances.append(instance_info)
            
            if not instances:
                self.logger.warning("No EC2 instances found")
            else:
                self.logger.info(f"Retrieved {len(instances)} EC2 instances")
                
            return instances
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve EC2 instances: {e}")
            return []

    # ---------------- CloudWatch Operations ----------------
    def get_ec2_metrics(self, instance_id: str, metric_names: Optional[List[str]] = None, 
                       period: int = 300) -> Dict[str, List[Dict[str, Any]]]:
        """Get EC2 metrics from CloudWatch."""
        if metric_names is None:
            metric_names = ["CPUUtilization", "NetworkIn", "NetworkOut", "DiskReadOps", "DiskWriteOps"]

        metrics_data = {}
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=1)
        
        for metric_name in metric_names:
            try:
                response = self.cloudwatch.get_metric_statistics(
                    Namespace="AWS/EC2",
                    MetricName=metric_name,
                    Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=period,
                    Statistics=["Average"]
                )
                
                datapoints = []
                for datapoint in response.get("Datapoints", []):
                    processed_datapoint = {
                        "Timestamp": datapoint["Timestamp"].isoformat(),
                        "Average": datapoint.get("Average"),
                        "Unit": datapoint.get("Unit")
                    }
                    datapoints.append(processed_datapoint)
                
                metrics_data[metric_name] = datapoints
                
                if datapoints:
                    self.logger.info(f"Retrieved {len(datapoints)} datapoints for {metric_name}")
                else:
                    self.logger.warning(f"No data for metric {metric_name}")
                    
            except Exception as e:
                self.logger.error(f"Failed to retrieve metric {metric_name}: {e}")
                metrics_data[metric_name] = []
        
        return metrics_data

    # ---------------- Cost Explorer Operations ----------------
    def get_cost(self, start_date: str, end_date: str, 
                granularity: str = "DAILY", 
                metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get cost data from Cost Explorer."""
        if metrics is None:
            metrics = ["UnblendedCost", "UsageQuantity", "BlendedCost", "AmortizedCost", "NetAmortizedCost"]

        try:
            response = self.ce.get_cost_and_usage(
                TimePeriod={"Start": start_date, "End": end_date},
                Granularity=granularity,
                Metrics=metrics
            )
            
            results_count = len(response.get("ResultsByTime", []))
            if results_count > 0:
                self.logger.info(f"Retrieved {results_count} cost data points")
            else:
                self.logger.warning("No cost data returned")
                
            return response
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve cost data: {e}")
            return {}
