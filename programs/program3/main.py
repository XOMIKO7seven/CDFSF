#!/usr/bin/env python3
"""
Sample Python Program 3 - File Watcher
This program simulates a file monitoring service that watches for file changes.
"""

import time
import random
import logging
import os
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

class FileWatcher:
    def __init__(self, watch_directories):
        self.watch_directories = watch_directories
        self.file_count = {}
        
    def scan_directory(self, directory):
        """Scan directory and return file information"""
        try:
            if not os.path.exists(directory):
                # Create directory if it doesn't exist for demo purposes
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Created watch directory: {directory}")
            
            files = []
            for root, dirs, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(root, filename)
                    try:
                        stat = os.stat(filepath)
                        files.append({
                            'path': filepath,
                            'size': stat.st_size,
                            'modified': stat.st_mtime
                        })
                    except OSError:
                        continue
            return files
        except Exception as e:
            logger.error(f"Error scanning directory {directory}: {str(e)}")
            return []
    
    def check_for_changes(self):
        """Check all watched directories for changes"""
        total_changes = 0
        
        for directory in self.watch_directories:
            current_files = self.scan_directory(directory)
            current_count = len(current_files)
            
            previous_count = self.file_count.get(directory, 0)
            
            if current_count != previous_count:
                change = current_count - previous_count
                if change > 0:
                    logger.info(f"Directory {directory}: {change} new file(s) detected")
                else:
                    logger.info(f"Directory {directory}: {abs(change)} file(s) removed")
                total_changes += abs(change)
            
            self.file_count[directory] = current_count
            
            # Log directory status
            total_size = sum(f['size'] for f in current_files)
            logger.debug(f"Directory {directory}: {current_count} files, {total_size / 1024:.1f} KB total")
        
        return total_changes

def simulate_file_activity():
    """Simulate some file system activity"""
    activities = [
        "Configuration file updated",
        "Log file rotated", 
        "Temporary file created",
        "Cache file cleaned up",
        "Backup file generated",
        "Report file exported"
    ]
    
    if random.random() < 0.3:  # 30% chance of file activity
        activity = random.choice(activities)
        logger.info(f"File activity: {activity}")
        return True
    return False

def main():
    """Main program loop"""
    logger.info("File Watcher started")
    
    # Define directories to watch (create some demo directories)
    watch_dirs = [
        "./watch_data",
        "./watch_logs", 
        "./watch_temp"
    ]
    
    # Create directories if they don't exist
    for directory in watch_dirs:
        os.makedirs(directory, exist_ok=True)
    
    logger.info(f"Watching directories: {', '.join(watch_dirs)}")
    
    watcher = FileWatcher(watch_dirs)
    scan_counter = 0
    
    try:
        while True:
            scan_counter += 1
            logger.info(f"=== File Scan {scan_counter} ===")
            
            # Check for file changes
            changes = watcher.check_for_changes()
            
            if changes == 0:
                logger.info("No file changes detected")
            else:
                logger.info(f"Total changes detected: {changes}")
            
            # Simulate file system activity
            simulate_file_activity()
            
            # Simulate security scan
            if random.random() < 0.15:  # 15% chance
                logger.info("Security scan: All monitored files verified")
            
            # Simulate performance metrics
            if scan_counter % 5 == 0:
                scan_time = random.uniform(0.1, 0.5)
                logger.info(f"Scan performance: {scan_time:.3f}s for {len(watch_dirs)} directories")
            
            # Wait for next scan
            time.sleep(6)
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise
    finally:
        logger.info("File Watcher shutting down...")
        logger.info(f"Total scans completed: {scan_counter}")

if __name__ == "__main__":
    main()
