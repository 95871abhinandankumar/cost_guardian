"""
Data Aggregation Service for Cost Guardian
Simple day-wise aggregation of raw cost data
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any
from storage.database import get_db_manager, DatabaseError

logger = logging.getLogger(__name__)

class DataAggregationService:
    """Service for aggregating raw cost data into daily summaries"""

    def __init__(self):
        """Initialize the data aggregation service"""
        self.db_manager = get_db_manager()
        self.data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw_data.json')

    def load_raw_data(self) -> List[Dict[str, Any]]:
        """Load raw data from JSON file"""
        try:
            if not os.path.exists(self.data_path):
                raise FileNotFoundError(f"Data file not found: {self.data_path}")

            with open(self.data_path, 'r') as f:
                data = json.load(f)

            logger.info(f"Loaded {len(data)} raw data records")
            return data

        except Exception as e:
            logger.error(f"Failed to load raw data: {e}")
            raise

    def aggregate_daily_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Aggregate raw data into daily usage records"""
        try:
            # Group data by account_id, service_name, and usage_date
            grouped_data = {}

            for record in raw_data:
                key = (
                    record['account_id'],
                    record['service_name'],
                    record['usage_date']
                )

                if key not in grouped_data:
                    grouped_data[key] = {
                        'account_id': record['account_id'],
                        'service_name': record['service_name'],
                        'usage_date': record['usage_date'],
                        'total_cost': 0,
                        'total_usage': 0,
                        'regions': set(),
                        'resource_count': 0,
                        'tags': {},
                        'billing_period': record.get('billing_period', ''),
                        'anomaly_flags': [],
                        'anomaly_scores': [],
                        'currency': record.get('currency', 'USD')
                    }

                # Aggregate values
                grouped_data[key]['total_cost'] += record['cost']
                grouped_data[key]['total_usage'] += record['usage_quantity']
                grouped_data[key]['regions'].add(record['region'])
                grouped_data[key]['resource_count'] += 1

                # Merge tags
                if 'tags' in record and record['tags']:
                    for tag_key, tag_value in record['tags'].items():
                        grouped_data[key]['tags'][tag_key] = tag_value

                # Collect anomaly data
                if record.get('anomaly_flag', False):
                    grouped_data[key]['anomaly_flags'].append(True)
                    grouped_data[key]['anomaly_scores'].append(record.get('anomaly_score', 0))

            # Convert to final format
            aggregated_records = []
            for key, data in grouped_data.items():
                # Calculate anomaly metrics
                has_anomaly = len(data['anomaly_flags']) > 0
                avg_anomaly_score = (
                    sum(data['anomaly_scores']) / len(data['anomaly_scores'])
                    if data['anomaly_scores'] else 0
                )

                aggregated_record = {
                    'account_id': data['account_id'],
                    'service_name': data['service_name'],
                    'usage_date': data['usage_date'],
                    'usage_quantity': round(data['total_usage'], 4),
                    'cost': round(data['total_cost'], 4),
                    'currency': data['currency'],
                    'region': ', '.join(sorted(data['regions'])),
                    'resource_id': f"aggregated-{data['resource_count']}-resources",
                    'tags': json.dumps(data['tags']),
                    'billing_period': data['billing_period'],
                    'anomaly_flag': has_anomaly,
                    'anomaly_score': round(avg_anomaly_score, 2)
                }

                aggregated_records.append(aggregated_record)

            logger.info(f"Aggregated {len(raw_data)} records into {len(aggregated_records)} daily records")
            return aggregated_records

        except Exception as e:
            logger.error(f"Daily aggregation failed: {e}")
            raise

    def store_daily_usage(self, aggregated_data: List[Dict[str, Any]]) -> bool:
        """Store aggregated daily usage data in database"""
        try:
            insert_query = """
                INSERT OR REPLACE INTO daily_usage (
                    account_id, service_name, usage_date, usage_quantity, 
                    cost, currency, region, resource_id, tags, 
                    billing_period, anomaly_flag, anomaly_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            params_list = []
            for record in aggregated_data:
                params = (
                    record['account_id'],
                    record['service_name'],
                    record['usage_date'],
                    record['usage_quantity'],
                    record['cost'],
                    record['currency'],
                    record['region'],
                    record['resource_id'],
                    record['tags'],
                    record['billing_period'],
                    record['anomaly_flag'],
                    record['anomaly_score']
                )
                params_list.append(params)

            success = self.db_manager.execute_batch_insert(insert_query, params_list)

            if success:
                logger.info(f"Successfully stored {len(aggregated_data)} daily usage records")

            return success

        except DatabaseError as e:
            logger.error(f"Database error during storage: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to store daily usage data: {e}")
            raise

    def process_and_store_data(self) -> Dict[str, Any]:
        """Process raw data and store aggregated results"""
        try:
            # Load data
            raw_data = self.load_raw_data()

            if not raw_data:
                return {'success': False, 'message': 'No data to process'}

            # Initialize database schema if needed
            self.db_manager.initialize_schema()

            # Aggregate data
            aggregated_data = self.aggregate_daily_data(raw_data)

            if not aggregated_data:
                return {'success': False, 'message': 'Failed to aggregate data'}

            # Store aggregated data
            store_success = self.store_daily_usage(aggregated_data)

            # Generate summary
            summary = {
                'success': store_success,
                'message': 'Data processed successfully' if store_success else 'Failed to store data',
                'raw_records': len(raw_data),
                'aggregated_records': len(aggregated_data),
                'total_cost': round(sum(record['cost'] for record in aggregated_data), 2),
                'processing_timestamp': datetime.utcnow().isoformat()
            }

            return summary

        except Exception as e:
            logger.error(f"Data processing failed: {e}")
            return {'success': False, 'message': f'Processing failed: {str(e)}'}
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        service = DataAggregationService()
        result = service.process_and_store_data()
        print(f"Processing result: {result}")
    except Exception as e:
        logger.error(f"Failed to process data: {e}")
        print(f"Error: {e}")
