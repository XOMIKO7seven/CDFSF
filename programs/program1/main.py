#!/usr/bin/env python3
"""
Sample Python Program 1 - Data Processor
This program simulates a data processing application that generates logs periodically.
"""

import time
import random
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def process_data_batch(batch_id):
    """Simulate processing a batch of data"""
    logger.info(f"Starting data batch {batch_id}")
    
    # Simulate processing time
    processing_time = random.uniform(1, 3)
    time.sleep(processing_time)
    
    # Simulate random success/warning scenarios
    if random.random() < 0.1:  # 10% chance of warning
        logger.warning(f"Batch {batch_id} processed with warnings (took {processing_time:.2f}s)")
    else:
        logger.info(f"Batch {batch_id} processed successfully (took {processing_time:.2f}s)")
    
    # Simulate random metrics
    records_processed = random.randint(100, 1000)
    logger.info(f"Processed {records_processed} records in batch {batch_id}")

def main():
    """Main program loop"""
    logger.info("Data Processor started")
    logger.info("Initializing data processing pipeline...")
    
    batch_counter = 1
    
    try:
        while True:
            process_data_batch(batch_counter)
            batch_counter += 1
            
            # Wait between batches
            wait_time = random.uniform(2, 5)
            logger.debug(f"Waiting {wait_time:.1f}s before next batch...")
            time.sleep(wait_time)
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise
    finally:
        logger.info("Data Processor shutting down...")
        logger.info(f"Total batches processed: {batch_counter - 1}")

if __name__ == "__main__":
    main()
