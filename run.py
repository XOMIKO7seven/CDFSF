#!/usr/bin/env python3
"""
Main entry point for the Python Program Manager web application.
This replaces the previous Flask app with a more robust architecture.
"""

import os
import sys
import logging
import threading
import time
import subprocess
import signal
from datetime import datetime
from collections import deque
from flask import Flask, render_template, request, jsonify, Response
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

class ProgramManager:
    """Enhanced program manager with better streaming support"""
    
    def __init__(self):
        self.programs = {
            1: {
                'name': 'Обработчик данных',
                'path': 'programs/program1',
                'script': 'main.py',
                'process': None,
                'logs': deque(maxlen=1000),
                'status': 'остановлен',
                'last_update': None
            },
            2: {
                'name': 'Монитор системы', 
                'path': 'programs/program2',
                'script': 'main.py',
                'process': None,
                'logs': deque(maxlen=1000),
                'status': 'остановлен',
                'last_update': None
            },
            3: {
                'name': 'Файловый монитор',
                'path': 'programs/program3', 
                'script': 'main.py',
                'process': None,
                'logs': deque(maxlen=1000),
                'status': 'остановлен',
                'last_update': None
            },
            4: {
                'name': 'API монитор',
                'path': 'programs/program4',
                'script': 'main.py', 
                'process': None,
                'logs': deque(maxlen=1000),
                'status': 'остановлен',
                'last_update': None
            }
        }
        self.logger = logging.getLogger(f"{__name__}.ProgramManager")
        self.lock = threading.Lock()
        
        # Start monitoring thread
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_programs, daemon=True)
        self.monitor_thread.start()

    def get_programs_status(self):
        """Get current status of all programs"""
        with self.lock:
            status = {}
            for program_id, program in self.programs.items():
                status[program_id] = {
                    'name': program['name'],
                    'status': program['status'],
                    'pid': program['process'].pid if program['process'] and program['process'].poll() is None else None,
                    'last_update': program['last_update']
                }
            return status

    def start_program(self, program_id):
        """Start a specific program"""
        if program_id not in self.programs:
            self.logger.error(f"Программа {program_id} не найдена")
            return False
            
        with self.lock:
            program = self.programs[program_id]
            
            if program['process'] and program['process'].poll() is None:
                self.logger.warning(f"Программа {program_id} уже запущена")
                return False
                
            try:
                program_dir = os.path.abspath(program['path'])
                script_path = os.path.join(program_dir, program['script'])
                
                if not os.path.exists(script_path):
                    self.logger.error(f"Скрипт не найден: {script_path}")
                    return False
                
                # Start the process
                process = subprocess.Popen(
                    [sys.executable, script_path],
                    cwd=program_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
                
                program['process'] = process
                program['status'] = 'запущен'
                program['last_update'] = datetime.now().isoformat()
                
                # Start log monitoring thread for this program
                log_thread = threading.Thread(
                    target=self._monitor_program_output,
                    args=(program_id,),
                    daemon=True
                )
                log_thread.start()
                
                self.logger.info(f"Программа {program_id} запущена (PID: {process.pid})")
                self._add_log(program_id, f"Программа запущена (PID: {process.pid})")
                return True
                
            except Exception as e:
                self.logger.error(f"Ошибка запуска программы {program_id}: {str(e)}")
                program['status'] = 'ошибка'
                program['last_update'] = datetime.now().isoformat()
                self._add_log(program_id, f"Ошибка запуска: {str(e)}")
                return False

    def stop_program(self, program_id):
        """Stop a specific program"""
        if program_id not in self.programs:
            self.logger.error(f"Программа {program_id} не найдена")
            return False
            
        with self.lock:
            program = self.programs[program_id]
            
            if not program['process'] or program['process'].poll() is not None:
                self.logger.warning(f"Программа {program_id} не запущена")
                program['status'] = 'остановлен'
                program['last_update'] = datetime.now().isoformat()
                return True
                
            try:
                process = program['process']
                pid = process.pid
                
                # Try graceful termination first
                process.terminate()
                
                # Wait for process to terminate
                try:
                    process.wait(timeout=5)
                    self.logger.info(f"Программа {program_id} остановлена корректно")
                except subprocess.TimeoutExpired:
                    # Force kill if graceful termination failed
                    process.kill()
                    process.wait()
                    self.logger.warning(f"Программа {program_id} принудительно остановлена")
                
                program['status'] = 'остановлен'
                program['last_update'] = datetime.now().isoformat()
                self._add_log(program_id, f"Программа остановлена (PID: {pid})")
                return True
                
            except Exception as e:
                self.logger.error(f"Ошибка остановки программы {program_id}: {str(e)}")
                self._add_log(program_id, f"Ошибка остановки: {str(e)}")
                return False

    def get_program_logs(self, program_id):
        """Get logs for a specific program"""
        if program_id not in self.programs:
            return []
        with self.lock:
            return list(self.programs[program_id]['logs'])

    def get_recent_logs(self, program_id, since_time=None):
        """Get recent logs since a specific time"""
        if program_id not in self.programs:
            return []
        
        with self.lock:
            logs = list(self.programs[program_id]['logs'])
            if since_time:
                # Filter logs newer than since_time
                filtered_logs = []
                for log in logs:
                    if log.startswith('[') and ']' in log:
                        try:
                            log_time_str = log.split(']')[0][1:]
                            log_time = datetime.fromisoformat(log_time_str.replace(' ', 'T'))
                            if log_time > since_time:
                                filtered_logs.append(log)
                        except:
                            # If parsing fails, include the log
                            filtered_logs.append(log)
                return filtered_logs
            return logs[-10:]  # Return last 10 logs

    def clear_program_logs(self, program_id):
        """Clear logs for a specific program"""
        if program_id in self.programs:
            with self.lock:
                self.programs[program_id]['logs'].clear()
                self._add_log(program_id, "Логи очищены")

    def _add_log(self, program_id, message):
        """Add a log entry for a program"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.programs[program_id]['logs'].append(log_entry)
        self.programs[program_id]['last_update'] = datetime.now().isoformat()

    def _monitor_program_output(self, program_id):
        """Monitor output from a specific program"""
        program = self.programs[program_id]
        process = program['process']
        
        try:
            while process.poll() is None:
                line = process.stdout.readline()
                if line:
                    with self.lock:
                        self._add_log(program_id, line.strip())
                else:
                    time.sleep(0.1)
        except Exception as e:
            self.logger.error(f"Ошибка мониторинга программы {program_id}: {str(e)}")
        finally:
            # Process has ended
            if process.poll() is not None:
                with self.lock:
                    program['status'] = 'остановлен'
                    program['last_update'] = datetime.now().isoformat()
                    self._add_log(program_id, f"Программа завершена с кодом {process.returncode}")

    def _monitor_programs(self):
        """Background thread to monitor program status"""
        while self.monitoring:
            try:
                with self.lock:
                    for program_id, program in self.programs.items():
                        process = program['process']
                        if process and process.poll() is not None:
                            # Process has ended
                            if program['status'] == 'запущен':
                                program['status'] = 'остановлен'
                                program['last_update'] = datetime.now().isoformat()
                                self._add_log(program_id, f"Программа неожиданно завершилась с кодом {process.returncode}")
                
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                self.logger.error(f"Ошибка мониторинга программ: {str(e)}")
                time.sleep(5)


# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-12345")

# Initialize program manager
program_manager = ProgramManager()

@app.route('/')
def index():
    """Main dashboard page"""
    programs = program_manager.get_programs_status()
    return render_template('index.html', programs=programs)

@app.route('/api/programs/status')
def get_programs_status():
    """API endpoint to get current status of all programs"""
    return jsonify(program_manager.get_programs_status())

@app.route('/api/programs/<int:program_id>/start', methods=['POST'])
def start_program(program_id):
    """Start a specific program"""
    try:
        success = program_manager.start_program(program_id)
        if success:
            return jsonify({'status': 'success', 'message': f'Программа {program_id} запущена'})
        else:
            return jsonify({'status': 'error', 'message': f'Не удалось запустить программу {program_id}'}), 400
    except Exception as e:
        app.logger.error(f"Ошибка запуска программы {program_id}: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/programs/<int:program_id>/stop', methods=['POST'])
def stop_program(program_id):
    """Stop a specific program"""
    try:
        success = program_manager.stop_program(program_id)
        if success:
            return jsonify({'status': 'success', 'message': f'Программа {program_id} остановлена'})
        else:
            return jsonify({'status': 'error', 'message': f'Не удалось остановить программу {program_id}'}), 400
    except Exception as e:
        app.logger.error(f"Ошибка остановки программы {program_id}: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/programs/<int:program_id>/logs')
def get_program_logs(program_id):
    """Get logs for a specific program"""
    try:
        since_param = request.args.get('since')
        since_time = None
        if since_param:
            try:
                since_time = datetime.fromisoformat(since_param)
            except:
                pass
        
        if since_time:
            logs = program_manager.get_recent_logs(program_id, since_time)
        else:
            logs = program_manager.get_program_logs(program_id)
        
        return jsonify({'logs': logs, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        app.logger.error(f"Ошибка получения логов программы {program_id}: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/programs/<int:program_id>/clear_logs', methods=['POST'])
def clear_program_logs(program_id):
    """Clear logs for a specific program"""
    try:
        program_manager.clear_program_logs(program_id)
        return jsonify({'status': 'success', 'message': f'Логи программы {program_id} очищены'})
    except Exception as e:
        app.logger.error(f"Ошибка очистки логов программы {program_id}: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("Получен сигнал завершения, останавливаем все программы...")
    program_manager.monitoring = False
    
    # Stop all running programs
    for program_id in program_manager.programs:
        program_manager.stop_program(program_id)
    
    logger.info("Все программы остановлены")
    sys.exit(0)

if __name__ == '__main__':
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Запуск Python Program Manager...")
    logger.info("Веб-интерфейс будет доступен по адресу: http://0.0.0.0:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)