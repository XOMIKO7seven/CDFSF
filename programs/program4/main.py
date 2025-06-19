#!/usr/bin/env python3
"""
Sample Python Program 4 - API Service Monitor
This program simulates monitoring of external API services and web endpoints.
"""

import time
import random
import logging
import json
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

class APIMonitor:
    def __init__(self):
        self.endpoints = [
            {"name": "User Service", "url": "https://api.example.com/users", "timeout": 5},
            {"name": "Payment Gateway", "url": "https://pay.example.com/status", "timeout": 10},
            {"name": "Database Health", "url": "https://db.example.com/health", "timeout": 3},
            {"name": "File Storage", "url": "https://storage.example.com/ping", "timeout": 7}
        ]
        self.stats = {endpoint["name"]: {"success": 0, "failures": 0, "avg_response_time": 0} 
                     for endpoint in self.endpoints}
    
    def simulate_api_check(self, endpoint):
        """Simulate checking an API endpoint"""
        name = endpoint["name"]
        url = endpoint["url"]
        timeout = endpoint["timeout"]
        
        # Simulate response time
        response_time = random.uniform(0.1, timeout * 0.8)
        
        # Simulate success/failure (90% success rate)
        success = random.random() > 0.1
        
        if success:
            status_code = random.choice([200, 200, 200, 201, 204])  # Mostly 200
            self.stats[name]["success"] += 1
            
            if status_code == 200:
                logger.info(f"{name}: OK ({response_time:.3f}s) - {url}")
            else:
                logger.info(f"{name}: OK ({response_time:.3f}s) - Status {status_code} - {url}")
                
        else:
            error_type = random.choice(["timeout", "connection_error", "server_error", "dns_error"])
            self.stats[name]["failures"] += 1
            
            if error_type == "timeout":
                logger.error(f"{name}: TIMEOUT ({timeout}s exceeded) - {url}")
            elif error_type == "connection_error":
                logger.error(f"{name}: CONNECTION ERROR - {url}")
            elif error_type == "server_error":
                status_code = random.choice([500, 502, 503, 504])
                logger.error(f"{name}: SERVER ERROR (HTTP {status_code}) - {url}")
            else:
                logger.error(f"{name}: DNS RESOLUTION FAILED - {url}")
        
        # Update average response time
        total_checks = self.stats[name]["success"] + self.stats[name]["failures"]
        if total_checks > 0:
            current_avg = self.stats[name]["avg_response_time"]
            self.stats[name]["avg_response_time"] = (current_avg * (total_checks - 1) + response_time) / total_checks
        
        return success, response_time
    
    def generate_summary_report(self):
        """Generate a summary report of all endpoint statistics"""
        logger.info("=== API Monitoring Summary ===")
        
        for endpoint_name, stats in self.stats.items():
            total_checks = stats["success"] + stats["failures"]
            if total_checks > 0:
                success_rate = (stats["success"] / total_checks) * 100
                logger.info(f"{endpoint_name}: {success_rate:.1f}% uptime ({stats['success']}/{total_checks}) - Avg: {stats['avg_response_time']:.3f}s")
            else:
                logger.info(f"{endpoint_name}: No data available")

def simulate_alert_system():
    """Simulate alert system notifications"""
    alert_types = [
        "High response time detected",
        "Multiple failures in sequence", 
        "Service degradation warning",
        "All systems operational",
        "Scheduled maintenance window",
        "Performance threshold exceeded"
    ]
    
    if random.random() < 0.2:  # 20% chance of alert
        alert = random.choice(alert_types)
        if "operational" in alert.lower() or "maintenance" in alert.lower():
            logger.info(f"ALERT: {alert}")
        else:
            logger.warning(f"ALERT: {alert}")
        return True
    return False

def main():
    """Main program loop"""
    logger.info("API Service Monitor started")
    logger.info("Initializing endpoint monitoring...")
    
    monitor = APIMonitor()
    
    # Log endpoints being monitored
    for endpoint in monitor.endpoints:
        logger.info(f"Monitoring endpoint: {endpoint['name']} - {endpoint['url']}")
    
    check_cycle = 0
    
    try:
        while True:
            check_cycle += 1
            logger.info(f"=== Monitoring Cycle {check_cycle} ===")
            
            # Check all endpoints
            cycle_results = []
            for endpoint in monitor.endpoints:
                success, response_time = monitor.simulate_api_check(endpoint)
                cycle_results.append((endpoint["name"], success, response_time))
            
            # Log cycle summary
            successful_checks = sum(1 for _, success, _ in cycle_results if success)
            logger.info(f"Cycle {check_cycle} completed: {successful_checks}/{len(cycle_results)} endpoints healthy")
            
            # Check alert system
            simulate_alert_system()
            
            # Generate detailed report every 10 cycles
            if check_cycle % 10 == 0:
                monitor.generate_summary_report()
            
            # Simulate load balancer status
            if random.random() < 0.3:  # 30% chance
                logger.info(f"Load balancer: {random.randint(15, 45)} active connections")
            
            # Wait for next monitoring cycle
            time.sleep(7)
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise
    finally:
        logger.info("API Service Monitor shutting down...")
        logger.info(f"Total monitoring cycles completed: {check_cycle}")
        
        # Final summary report
        if check_cycle > 0:
            monitor.generate_summary_report()

if __name__ == "__main__":
    main()
