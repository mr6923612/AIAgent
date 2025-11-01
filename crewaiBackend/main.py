"""
Flask-based customer service bot API backend service
Main functions:
1. Receive customer requests (text + images)
2. Process requests asynchronously
3. Return processing results
"""

import os
import json
import logging
import sys
from datetime import datetime
from threading import Thread
from uuid import uuid4

from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import base64

# Force set standard output to unbuffered mode to ensure Docker logs display immediately
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# Configure logging - simplified version, ensure console output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Ensure print can output normally
sys.stdout.reconfigure(encoding='utf-8')

logger.info("=== AI Agent Backend Service Started ===")
logger.info(f"Python version: {sys.version}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info("=" * 40)

# Import configuration file
try:
    from config import config
    logger.info("Configuration file loaded successfully")
    LLM_TYPE = config.LLM_TYPE
    PORT = config.PORT
except ImportError:
    logger.warning("Config.py file not found, please copy config.py.template to config.py and configure API keys")
    # Use default values
    os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")
    os.environ["RAGFLOW_BASE_URL"] = os.getenv("RAGFLOW_BASE_URL", "http://localhost:80")
    os.environ["RAGFLOW_API_KEY"] = os.getenv("RAGFLOW_API_KEY", "")
    os.environ["RAGFLOW_CHAT_ID"] = os.getenv("RAGFLOW_CHAT_ID", "63854abaabb511f0bf790ec84fa37cec")
    os.environ["FLASK_ENV"] = os.getenv("FLASK_ENV", "development")
    os.environ["FLASK_DEBUG"] = os.getenv("FLASK_DEBUG", "True")
    os.environ["PORT"] = os.getenv("PORT", "8012")
    LLM_TYPE = "google"
    PORT = 8012

from .crew import CrewtestprojectCrew
from .utils.jobManager import append_event, jobs, jobs_lock, Event
from .utils.myLLM import my_llm
from .utils.sessionManager import SessionManager
from .utils.session_agent_manager import session_agent_manager


# Create Flask application instance
app = Flask(__name__)
# Enable CORS to handle cross-origin resource sharing so requests from any origin can access /api/* endpoints
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize session manager
session_manager = SessionManager()

# Start periodic cleanup task
import threading
import time

def periodic_cleanup():
    """Periodically clean up inactive sessions"""
    while True:
        try:
            time.sleep(300)  # Clean up every 5 minutes
            session_agent_manager.cleanup_inactive_sessions(max_age_seconds=1800)  # 30 minute timeout
            print(f"[Cleanup] Session cleanup completed, current status: {session_agent_manager.get_session_status()}")
        except Exception as e:
            print(f"[Cleanup] Session cleanup failed: {e}")

# Start background cleanup thread
cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
cleanup_thread.start()


def handle_api_error(error_msg: str, status_code: int = 500):
    """Unified API error handling"""
    logger.error(error_msg)
    return jsonify({"error": error_msg}), status_code


def process_file_upload(request):
    """Handle file upload request"""
    customer_input = request.form.get('customer_input', '')
    input_type = request.form.get('input_type', 'text')
    additional_context = request.form.get('additional_context', '')
    customer_domain = request.form.get('customer_domain', '')
    project_description = request.form.get('project_description', '')
    session_id = request.form.get('session_id')
    
    image_data = None
    audio_data = None
    
    # Handle image files
    if 'image' in request.files:
        image_file = request.files['image']
        if image_file and image_file.filename:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
            input_type = 'text+image' if customer_input.strip() else 'image'
            customer_input = f"{customer_input} [Uploaded image]"
    
    # Handle audio files (speech-to-text feature removed)
    if 'audio' in request.files:
        raise ValueError("Speech-to-text feature has been removed, please input text directly")
    
    return {
        "customer_input": customer_input,
        "input_type": input_type,
        "additional_context": additional_context,
        "customer_domain": customer_domain,
        "project_description": project_description,
        "image_data": image_data,
        "audio_data": audio_data,
        "session_id": session_id
    }


def process_json_request(request):
    """Handle JSON request"""
    data = request.json
    if not data or 'customer_input' not in data:
        abort(400, description="Invalid input data provided. Required: customer_input")
    
    return {
        "customer_input": data['customer_input'],
        "input_type": data.get('input_type', 'text'),
        "additional_context": data.get('additional_context', ''),
        "customer_domain": data.get('customer_domain', ''),
        "project_description": data.get('project_description', ''),
        "image_data": None,
        "audio_data": None,
        "session_id": data.get('session_id')
    }


def kickoff_crew(job_id, inputs):
    """Execute customer service bot analysis asynchronously"""
    session_id = inputs.get('session_id', 'unknown')
    session_prefix = f"[Session:{session_id[:8]}]" if session_id != 'unknown' else "[Session:unknown]"
    
    logger.info(f"{session_prefix} Starting to process task {job_id}")
    
    try:
        # Validate input data
        if not inputs.get("customer_input", "").strip():
            raise ValueError("Customer input cannot be empty")
        
        # Use session Agent manager (reuse Agent)
        session_agent = session_agent_manager.get_or_create_agent(session_id)
        
        # Execute analysis
        results = session_agent.kickoff(inputs)
        logger.info(f"{session_prefix} Task {job_id} analysis completed")
        
        # Update task status to complete
        with jobs_lock:
            jobs[job_id].status = 'COMPLETE'
            jobs[job_id].result = results
            jobs[job_id].events.append(
                Event(timestamp=datetime.now(), data="Customer service bot analysis completed"))
                
    except Exception as e:
        error_msg = f"{session_prefix} Task {job_id} analysis error: {e}"
        print(error_msg)
        
        append_event(job_id, f"Error occurred during customer service bot analysis: {e}")
        with jobs_lock:
            jobs[job_id].status = 'ERROR'
            jobs[job_id].result = str(e)


@app.route('/api/crew', methods=['POST'])
def run_crew():
    """Handle customer service bot request"""
    try:
        # Handle different types of requests
        if request.files:
            inputs = process_file_upload(request)
        else:
            inputs = process_json_request(request)
        
        session_id = inputs.get('session_id')
        session_prefix = f"[Session:{session_id[:8]}]" if session_id else "[Session:unknown]"
        
        print(f"{session_prefix} Received customer service bot request")
        
        # Create task and execute asynchronously
        job_id = str(uuid4())
        append_event(job_id, "Customer service bot starting to analyze customer needs...")
        
        thread = Thread(target=kickoff_crew, args=(job_id, inputs))
        thread.start()
        
        logger.info(f"{session_prefix} Task {job_id} started asynchronous processing")
        return jsonify({"job_id": job_id}), 202
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return handle_api_error(f"Failed to process request: {str(e)}", 500)




@app.route('/api/crew/<job_id>', methods=['GET'])
def get_status(job_id):
    """Get task status"""
    with jobs_lock:
        job = jobs.get(job_id)
        if job is None:
            abort(404, description="Job not found")
    
    # Try to parse result as JSON, keep as string if parsing fails
    try:
        result_json = json.loads(str(job.result))
    except json.JSONDecodeError:
        result_json = str(job.result)
    
    return jsonify({
        "job_id": job_id,
        "status": job.status,
        "result": result_json,
        "events": [{"timestamp": event.timestamp.isoformat(), "data": event.data} for event in job.events]
    })


@app.route('/api/sessions/status', methods=['GET'])
def get_sessions_status():
    """Get all session status"""
    try:
        status = session_agent_manager.get_session_status()
        return jsonify(status), 200
    except Exception as e:
        return handle_api_error(f"Failed to get session status: {str(e)}", 500)

@app.route('/api/sessions/cleanup', methods=['POST'])
def cleanup_sessions():
    """Clean up inactive sessions"""
    try:
        data = request.json or {}
        max_age = data.get('max_age_seconds', 1800)  # Default 30 minutes
        
        session_agent_manager.cleanup_inactive_sessions(max_age)
        status = session_agent_manager.get_session_status()
        
        return jsonify({
            "message": f"Cleanup completed, maximum inactive time: {max_age} seconds",
            "status": status
        }), 200
    except Exception as e:
        return handle_api_error(f"Failed to clean up sessions: {str(e)}", 500)

@app.route('/api/sessions', methods=['POST'])
def create_session():
    """Create new chat session"""
    try:
        data = request.json or {}
        user_id = data.get('user_id', 'anonymous')
        title = data.get('title')
        
        # Create session (only create database record, RAGFlow session created on first conversation)
        session = session_manager.create_session(
            user_id=user_id, 
            title=title
        )
        
        return jsonify({
            "session_id": session.session_id,
            "title": session.title,
            "created_at": session.created_at.isoformat(),
            "ragflow_session_id": None  # RAGFlow session created on first conversation
        }), 201
        
    except Exception as e:
        return handle_api_error(f"Failed to create session: {str(e)}", 500)


@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session details"""
    session = session_manager.get_session(session_id)
    if not session:
        abort(404, description="Session not found")
    
    return jsonify(session.to_dict())


@app.route('/api/sessions/<session_id>/messages', methods=['POST'])
def add_message(session_id):
    """Add message to session"""
    data = request.json
    if not data or 'role' not in data or 'content' not in data:
        abort(400, description="Missing role or content")
    
    message = session_manager.add_message(session_id, data['role'], data['content'])
    if not message:
        abort(404, description="Session not found")
    
    return jsonify(message.to_dict()), 201


@app.route('/api/sessions/<session_id>', methods=['PUT'])
def update_session(session_id):
    """Update session title"""
    data = request.json
    if not data or 'title' not in data:
        abort(400, description="Missing title")
    
    session_manager.update_session_title(session_id, data['title'])
    return jsonify({"message": "Session updated successfully"})


@app.route('/api/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete session"""
    try:
        # 1. First release session Agent (will automatically delete corresponding RAGFlow session)
        session_agent_manager.release_agent(session_id)
        
        # 2. Delete session record in database
        success = session_manager.delete_session(session_id)
        if not success:
            return handle_api_error("Session not found", 404)
        
        return jsonify({"message": "Session deleted successfully"})
        
    except Exception as e:
        return handle_api_error(f"Failed to delete session: {str(e)}", 500)


@app.route('/api/users/<user_id>/sessions', methods=['GET'])
def get_user_sessions(user_id):
    """Get all sessions for a user"""
    sessions = session_manager.get_user_sessions(user_id)
    return jsonify([session.to_dict() for session in sessions])


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        from utils.database import db_manager
        db_status = db_manager._check_connection()
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected" if db_status else "disconnected",
            "service": "aiagent-backend"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "service": "aiagent-backend"
        }), 503


if __name__ == '__main__':
    logger.info(f"Starting server on port {PORT}")
    debug_mode = config.FLASK_DEBUG == "True" or config.FLASK_DEBUG is True
    logger.info(f"Debug mode: {debug_mode}")
    app.run(debug=debug_mode, port=PORT, host='0.0.0.0')
