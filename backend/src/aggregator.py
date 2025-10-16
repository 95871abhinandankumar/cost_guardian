"""
Data Aggregator Script
Simple script to process raw data and store aggregated results
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.data_aggregator import DataAggregationService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main aggregation process"""
    try:
        logger.info("Starting data aggregation process...")
        
        # Initialize service
        service = DataAggregationService()
        
        # Process and store data
        result = service.process_and_store_data()
        
        if result['success']:
            logger.info("Data aggregation completed successfully!")
            logger.info(f"Processed {result['raw_records']} raw records into {result['aggregated_records']} daily records")
            logger.info(f"Total cost: ${result['total_cost']}")
            logger.info(f"Processing time: {result['processing_timestamp']}")
        else:
            logger.error(f"Data aggregation failed: {result['message']}")
            return 1
            
    except Exception as e:
        logger.error(f"Unexpected error during aggregation: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
