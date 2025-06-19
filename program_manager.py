import os
import subprocess
import threading
import time
import logging
from datetime import datetime
from collections import deque
import signal
import psutil

class ProgramManager:
    def __init__(self):
        self.programs = {
            1: {
                'name': 'Program 1',
                'path': 'programs/program1',
                'script': 'main.py',
                'process': None,
                'logs': deque(maxlen=1000),  # Keep last 1000 log lines
                'status': 'stopped'
            },
            2: {
                'name': 'Program 2', 
                'path': 'programs/program2',
                'script': 'main.py',
                'process': None,
                'logs': deque(maxlen=1000),
                'status': 'stopped'
            },
            3: {
                'name': 'Program 3',
                'path': 'programs/program3', 
                'script': 'main.py',
                'process': None,
                'logs': deque(maxlen=1000),
                'status': 'stopped'
            },
            4: {
                'name': 'Program 4',
                'path': 'programs/program4',
                'script': 'main.py', 
                'process': None,
                'logs': deque(maxlen=1000),
                'status': 'stopped'
            }
        }
        self.logger = logging.getLogger(__name__)
        
        # Start monitoring thread
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_programs, daemon=True)
        self.monitor_thread.start()

    def get_programs_status(self):
        """Get current status of all programs"""
        status = {}
        for program_id, program in self.programs.items():
            status[program_id] = {
                'name': program['name'],
                'status': program['status'],
                'pid': program['process'].pid if program['process'] and program['process'].poll() is None else None
            }
        return status

    def start_program(self, program_id):
        """Start a specific program"""
        if program_id not in self.programs:
            self.logger.error(f"Program {program_id} not found")
            return False
            
        program = self.programs[program_id]
        
        if program['process'] and program['process'].poll() is None:
            self.logger.warning(f"Program {program_id} is already running")
            return False
            
        try:
            # Change to program directory
            program_dir = os.path.abspath(program['path'])
            script_path = os.path.join(program_dir, program['script'])
            
            if not os.path.exists(script_path):
                self.logger.error(f"Script not found: {script_path}")
                return False
            
            # Start the process
            process = subprocess.Popen(
                ['python', script_path],
                cwd=program_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            program['process'] = process
            program['status'] = 'running'
            
            # Start log monitoring thread for this program
            log_thread = threading.Thread(
                target=self._monitor_program_output,
                args=(program_id,),
                daemon=True
            )
            log_thread.start()
            
            self.logger.info(f"Started program {program_id} (PID: {process.pid})")
            self._add_log(program_id, f"Program started (PID: {process.pid})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start program {program_id}: {str(e)}")
            program['status'] = 'error'
            self._add_log(program_id, f"Failed to start: {str(e)}")
            return False

    def stop_program(self, program_id):
        """Stop a specific program"""
        if program_id not in self.programs:
            self.logger.error(f"Program {program_id} not found")
            return False
            
        program = self.programs[program_id]
        
        if not program['process'] or program['process'].poll() is not None:
            self.logger.warning(f"Program {program_id} is not running")
            program['status'] = 'stopped'
            return True
            
        try:
            process = program['process']
            pid = process.pid
            
            # Try graceful termination first
            process.terminate()
            
            # Wait for process to terminate
            try:
                process.wait(timeout=5)
                self.logger.info(f"Program {program_id} terminated gracefully")
            except subprocess.TimeoutExpired:
                # Force kill if graceful termination failed
                process.kill()
                process.wait()
                self.logger.warning(f"Program {program_id} was force killed")
            
            program['status'] = 'stopped'
            self._add_log(program_id, f"Program stopped (PID: {pid})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop program {program_id}: {str(e)}")
            self._add_log(program_id, f"Failed to stop: {str(e)}")
            return False

    def get_program_logs(self, program_id):
        """Get logs for a specific program"""
        if program_id not in self.programs:
            return []
        return list(self.programs[program_id]['logs'])

    def stream_program_logs(self, program_id):
        """Generator that yields new log lines for a program"""
        if program_id not in self.programs:
            return
            
        # Yield existing logs first
        existing_logs = list(self.programs[program_id]['logs'])
        for log in existing_logs[-50:]:  # Send last 50 logs
            yield log
        
        # Monitor for new logs
        last_count = len(self.programs[program_id]['logs'])
        while True:
            current_logs = self.programs[program_id]['logs']
            current_count = len(current_logs)
            
            if current_count > last_count:
                # Yield new logs
                new_logs = list(current_logs)[last_count:]
                for log in new_logs:
                    yield log
                last_count = current_count
            
            time.sleep(0.5)  # Poll every 500ms

    def clear_program_logs(self, program_id):
        """Clear logs for a specific program"""
        if program_id in self.programs:
            self.programs[program_id]['logs'].clear()
            self._add_log(program_id, "Logs cleared")

    def _add_log(self, program_id, message):
        """Add a log entry for a program"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.programs[program_id]['logs'].append(log_entry)

    def _monitor_program_output(self, program_id):
        """Monitor output from a specific program"""
        program = self.programs[program_id]
        process = program['process']
        
        try:
            while process.poll() is None:
                line = process.stdout.readline()
                if line:
                    self._add_log(program_id, line.strip())
                else:
                    time.sleep(0.1)
        except Exception as e:
            self.logger.error(f"Error monitoring program {program_id} output: {str(e)}")
        finally:
            # Process has ended
            if process.poll() is not None:
                program['status'] = 'stopped'
                self._add_log(program_id, f"Program ended with exit code {process.returncode}")

    def _monitor_programs(self):
        """Background thread to monitor program status"""
        while self.monitoring:
            try:
                for program_id, program in self.programs.items():
                    process = program['process']
                    if process and process.poll() is not None:
                        # Process has ended
                        if program['status'] == 'running':
                            program['status'] = 'stopped'
                            self._add_log(program_id, f"Program ended unexpectedly with exit code {process.returncode}")
                
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                self.logger.error(f"Error in program monitoring: {str(e)}")
                time.sleep(5)
