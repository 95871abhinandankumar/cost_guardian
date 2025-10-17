# backend/src/ingestion/aws_data_collector.py

import os
from .connector import AWSConnector
from datetime import datetime, timedelta

# Environment variables
RAW_DATA_BUCKET = os.environ.get("RAW_DATA_BUCKET", "cost-guardian-data-lake")

# Initialize connector
connector = AWSConnector(profile_name="cost-guardian")  # ensure profile is used

def fetch_raw_data_for_tenant(tenant_id, date_str=None, use_mock=True, mock_file_path=None):
    """
    Fetch raw data for a tenant.
    - use_mock=True: fetch data from local mock file (default: raw_data.json)
    - date_str: YYYY-MM-DD format. Defaults to 2 days ago.
    - mock_file_path: optional, custom path to mock file.
    Returns a list of data rows for the tenant.
    """
    if date_str is None:
        date_str = (datetime.utcnow() - timedelta(days=2)).strftime('%Y-%m-%d')

    if use_mock:
        print(f"Fetching mock data locally for tenant: {tenant_id}")

        # Load mock data using connector (supports raw_data.json or any JSONL)
        mock_data = connector.load_mock_file(file_path=mock_file_path)
        tenant_data = [row for row in mock_data if row.get("account_id") == tenant_id]

        if not tenant_data:
            print(f"⚠️ No tenant-specific mock data found for {tenant_id}, using all mock data")
            tenant_data = mock_data

        # Filter by usage_date
        date_filtered_data = [row for row in tenant_data if row.get("usage_date") == date_str]
        if not date_filtered_data:
            print(f"⚠️ No mock data for tenant {tenant_id} on {date_str}, using all available dates")
            date_filtered_data = tenant_data

        return date_filtered_data

    else:
        # TODO: implement real AWS data fetching via connector (Cost Explorer, EC2, etc.)
        print(f"Fetching real AWS data for tenant: {tenant_id} (not implemented yet)")
        return []
