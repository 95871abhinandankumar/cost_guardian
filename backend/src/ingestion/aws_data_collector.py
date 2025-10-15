# backend/src/ingestion/aws_data_collector.py

import os
from .connector import AWSConnector
from datetime import datetime, timedelta

# Environment variables
RAW_DATA_BUCKET = os.environ.get("RAW_DATA_BUCKET", "cost-guardian-data-lake")

# Initialize connector
connector = AWSConnector(profile_name="cost-guardian")  # ensure profile is used

def fetch_raw_data_for_tenant(tenant_id, date_str=None, use_mock=True):
    """
    Fetch raw data for a tenant.
    If use_mock=True, fetch data from local mock file.
    date_str: YYYY-MM-DD format. Defaults to 2 days ago.
    Returns a list of data rows for the tenant.
    """
    if date_str is None:
        date_str = (datetime.utcnow() - timedelta(days=2)).strftime('%Y-%m-%d')

    if use_mock:
        # Fetch mock data locally
        print(f"Fetching mock data locally for tenant: {tenant_id}")
        mock_data = connector.get_mock_data_for_tenant(tenant_id)

        # Filter by date
        date_filtered_data = [row for row in mock_data if row.get("usage_date") == date_str]

        if not date_filtered_data:
            date_filtered_data = mock_data  # fallback to all dates
            print(f"⚠️ No mock data for tenant {tenant_id} on {date_str}, using all available dates")

        return date_filtered_data

    else:
        # TODO: implement real AWS data fetching via connector (Cost Explorer, EC2, etc.)
        print(f"Fetching real AWS data for tenant: {tenant_id} (not implemented yet)")
        return []
