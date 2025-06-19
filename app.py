import os
import logging
from flask import Flask, render_template, request, jsonify, Response
from program_manager import ProgramManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

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
            return jsonify({'status': 'success', 'message': f'Program {program_id} started'})
        else:
            return jsonify({'status': 'error', 'message': f'Failed to start program {program_id}'}), 400
    except Exception as e:
        app.logger.error(f"Error starting program {program_id}: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/programs/<int:program_id>/stop', methods=['POST'])
def stop_program(program_id):
    """Stop a specific program"""
    try:
        success = program_manager.stop_program(program_id)
        if success:
            return jsonify({'status': 'success', 'message': f'Program {program_id} stopped'})
        else:
            return jsonify({'status': 'error', 'message': f'Failed to stop program {program_id}'}), 400
    except Exception as e:
        app.logger.error(f"Error stopping program {program_id}: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/programs/<int:program_id>/logs')
def get_program_logs(program_id):
    """Get logs for a specific program"""
    try:
        logs = program_manager.get_program_logs(program_id)
        return jsonify({'logs': logs})
    except Exception as e:
        app.logger.error(f"Error getting logs for program {program_id}: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/programs/<int:program_id>/logs/stream')
def stream_program_logs(program_id):
    """Stream logs for a specific program using Server-Sent Events"""
    def generate():
        try:
            for log_line in program_manager.stream_program_logs(program_id):
                yield f"data: {log_line}\n\n"
        except Exception as e:
            app.logger.error(f"Error streaming logs for program {program_id}: {str(e)}")
            yield f"data: Error: {str(e)}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/programs/<int:program_id>/clear_logs', methods=['POST'])
def clear_program_logs(program_id):
    """Clear logs for a specific program"""
    try:
        program_manager.clear_program_logs(program_id)
        return jsonify({'status': 'success', 'message': f'Logs cleared for program {program_id}'})
    except Exception as e:
        app.logger.error(f"Error clearing logs for program {program_id}: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
