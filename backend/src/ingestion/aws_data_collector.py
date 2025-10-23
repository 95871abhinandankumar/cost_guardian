# backend/src/ingestion/aws_data_collector.py
"""AWS Data Collector for fetching raw data for tenants."""

import os
import logging
from .connector import AWSConnector
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Environment variables
RAW_DATA_BUCKET = os.environ.get("RAW_DATA_BUCKET", "cost-guardian-data-lake")

# Initialize connector
connector = AWSConnector(profile_name=os.environ.get("AWS_PROFILE"))
logger = logging.getLogger(__name__)

def fetch_raw_data_for_tenant(tenant_id: str, date_str: Optional[str] = None, 
                           use_mock: bool = True, mock_file_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch raw data for a tenant.
    
    Args:
        tenant_id: Tenant identifier
        date_str: Date in YYYY-MM-DD format (defaults to 2 days ago)
        use_mock: Use mock data if True, real AWS data if False
        mock_file_path: Custom path to mock file
    
    Returns:
        List of data rows for the tenant
    """
    if date_str is None:
        date_str = (datetime.utcnow() - timedelta(days=2)).strftime('%Y-%m-%d')

    if use_mock:
        logger.info(f"Fetching mock data for tenant: {tenant_id}")
        
        mock_data = connector.load_mock_file(file_path=mock_file_path)
        tenant_data = [row for row in mock_data if row.get("account_id") == tenant_id]

        if not tenant_data:
            logger.warning(f"No tenant-specific data for {tenant_id}, using all data")
            tenant_data = mock_data

        # Filter by usage_date
        date_filtered_data = [row for row in tenant_data if row.get("usage_date") == date_str]
        if not date_filtered_data:
            logger.warning(f"No data for {tenant_id} on {date_str}, using all dates")
            date_filtered_data = tenant_data

        return date_filtered_data

    else:
        logger.info(f"Fetching real AWS data for tenant: {tenant_id} (not implemented)")
        return []
