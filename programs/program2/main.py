#!/usr/bin/env python3
"""
Sample Python Program 2 - System Monitor
This program simulates a system monitoring application that tracks various metrics.
"""

import time
import random
import logging
import psutil
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

def get_system_metrics():
    """Get current system metrics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu': cpu_percent,
            'memory_percent': memory.percent,
            'memory_used_gb': memory.used / (1024**3),
            'disk_percent': disk.percent,
            'disk_free_gb': disk.free / (1024**3)
        }
    except Exception as e:
        logger.error(f"Error getting system metrics: {str(e)}")
        # Return simulated metrics if psutil fails
        return {
            'cpu': random.uniform(10, 80),
            'memory_percent': random.uniform(30, 70),
            'memory_used_gb': random.uniform(2, 8),
            'disk_percent': random.uniform(20, 60),
            'disk_free_gb': random.uniform(10, 100)
        }

def check_system_health(metrics):
    """Check system health and log warnings if necessary"""
    warnings = []
    
    if metrics['cpu'] > 80:
        warnings.append(f"High CPU usage: {metrics['cpu']:.1f}%")
    
    if metrics['memory_percent'] > 85:
        warnings.append(f"High memory usage: {metrics['memory_percent']:.1f}%")
    
    if metrics['disk_percent'] > 90:
        warnings.append(f"Low disk space: {metrics['disk_percent']:.1f}% used")
    
    return warnings

def main():
    """Main program loop"""
    logger.info("System Monitor started")
    logger.info("Starting system monitoring...")
    
    monitoring_cycles = 0
    
    try:
        while True:
            monitoring_cycles += 1
            logger.info(f"=== Monitoring Cycle {monitoring_cycles} ===")
            
            # Get system metrics
            metrics = get_system_metrics()
            
            # Log current metrics
            logger.info(f"CPU: {metrics['cpu']:.1f}%")
            logger.info(f"Memory: {metrics['memory_percent']:.1f}% ({metrics['memory_used_gb']:.2f} GB used)")
            logger.info(f"Disk: {metrics['disk_percent']:.1f}% ({metrics['disk_free_gb']:.2f} GB free)")
            
            # Check for warnings
            warnings = check_system_health(metrics)
            for warning in warnings:
                logger.warning(warning)
            
            if not warnings:
                logger.info("System health: OK")
            
            # Simulate additional monitoring events
            if random.random() < 0.2:  # 20% chance
                logger.info(f"Network activity detected: {random.randint(10, 100)} MB/s")
            
            if random.random() < 0.1:  # 10% chance
                logger.info(f"Process count: {random.randint(50, 200)} active processes")
            
            # Wait for next monitoring cycle
            time.sleep(8)
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise
    finally:
        logger.info("System Monitor shutting down...")
        logger.info(f"Total monitoring cycles completed: {monitoring_cycles}")

if __name__ == "__main__":
    main()
