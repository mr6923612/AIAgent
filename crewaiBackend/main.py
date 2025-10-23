"""
基于Flask的客服机器人API后端服务
主要功能：
1. 接收客户请求（文本+图片）
2. 异步处理请求
3. 返回处理结果
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

# 强制设置标准输出为无缓冲模式，确保Docker日志能立即显示
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

# 配置日志 - 简化版本，确保控制台输出
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# 确保print也能正常输出
import sys
sys.stdout.reconfigure(encoding='utf-8')

print("=== AI Agent 后端服务启动 ===")
print(f"Python版本: {sys.version}")
print(f"当前工作目录: {os.getcwd()}")
print("=" * 40)

# 导入配置文件
try:
    from config import config
    logger.info("成功加载配置文件")
    LLM_TYPE = config.LLM_TYPE
    PORT = config.PORT
except ImportError:
    print("警告: 未找到config.py文件，请复制config.py.template为config.py并配置API密钥")
    # 使用默认值
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


# 创建Flask应用实例
app = Flask(__name__)
# 启用CORS，处理跨域资源共享以便任何来源的请求可以访问以/api/开头的接口
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 初始化会话管理器
session_manager = SessionManager()

# 启动定时清理任务
import threading
import time

def periodic_cleanup():
    """定期清理非活跃会话"""
    while True:
        try:
            time.sleep(300)  # 每5分钟清理一次
            session_agent_manager.cleanup_inactive_sessions(max_age_seconds=1800)  # 30分钟超时
            print(f"[清理] 会话清理完成，当前状态: {session_agent_manager.get_session_status()}")
        except Exception as e:
            print(f"[清理] 会话清理失败: {e}")

# 启动后台清理线程
cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
cleanup_thread.start()


def create_ragflow_client():
    """创建RAGFlow客户端"""
    try:
        from utils.ragflow_client import create_ragflow_client
        return create_ragflow_client()
    except Exception as e:
        logger.error(f"创建RAGFlow客户端失败: {e}")
        return None


def handle_api_error(error_msg: str, status_code: int = 500):
    """统一处理API错误"""
    logger.error(error_msg)
    return jsonify({"error": error_msg}), status_code


def process_file_upload(request):
    """处理文件上传请求"""
    customer_input = request.form.get('customer_input', '')
    input_type = request.form.get('input_type', 'text')
    additional_context = request.form.get('additional_context', '')
    customer_domain = request.form.get('customer_domain', '')
    project_description = request.form.get('project_description', '')
    session_id = request.form.get('session_id')
    
    image_data = None
    audio_data = None
    
    # 处理图片文件
    if 'image' in request.files:
        image_file = request.files['image']
        if image_file and image_file.filename:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
            input_type = 'text+image' if customer_input.strip() else 'image'
            customer_input = f"{customer_input} [上传了图片]"
    
    # 处理音频文件（已移除语音转文字功能）
    if 'audio' in request.files:
        raise ValueError("语音转文字功能已移除，请直接输入文字")
    
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
    """处理JSON请求"""
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
    """异步执行客服机器人分析"""
    session_id = inputs.get('session_id', 'unknown')
    session_prefix = f"[会话:{session_id[:8]}]" if session_id != 'unknown' else "[会话:unknown]"
    
    print(f"{session_prefix} 开始处理任务 {job_id}")
    
    try:
        # 验证输入数据
        if not inputs.get("customer_input", "").strip():
            raise ValueError("客户输入不能为空")
        
        # 使用会话Agent管理器（复用Agent）
        session_agent = session_agent_manager.get_or_create_agent(session_id)
        
        # 执行分析
        results = session_agent.kickoff(inputs)
        print(f"{session_prefix} 任务 {job_id} 分析完成")
        
        # 更新任务状态为完成
        with jobs_lock:
            jobs[job_id].status = 'COMPLETE'
            jobs[job_id].result = results
            jobs[job_id].events.append(
                Event(timestamp=datetime.now(), data="客服机器人分析完成"))
                
    except Exception as e:
        error_msg = f"{session_prefix} 任务 {job_id} 分析错误: {e}"
        print(error_msg)
        
        append_event(job_id, f"客服机器人分析过程中出现错误: {e}")
        with jobs_lock:
            jobs[job_id].status = 'ERROR'
            jobs[job_id].result = str(e)


@app.route('/api/crew', methods=['POST'])
def run_crew():
    """处理客服机器人请求"""
    try:
        # 处理不同类型的请求
        if request.files:
            inputs = process_file_upload(request)
        else:
            inputs = process_json_request(request)
        
        session_id = inputs.get('session_id')
        session_prefix = f"[会话:{session_id[:8]}]" if session_id else "[会话:unknown]"
        
        print(f"{session_prefix} 收到客服机器人请求")
        
        # 创建任务并异步执行
        job_id = str(uuid4())
        append_event(job_id, "客服机器人开始分析客户需求...")
        
        thread = Thread(target=kickoff_crew, args=(job_id, inputs))
        thread.start()
        
        print(f"{session_prefix} 任务 {job_id} 已启动异步处理")
        return jsonify({"job_id": job_id}), 202
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return handle_api_error(f"处理请求失败: {str(e)}", 500)




@app.route('/api/crew/<job_id>', methods=['GET'])
def get_status(job_id):
    """获取任务状态"""
    with jobs_lock:
        job = jobs.get(job_id)
        if job is None:
            abort(404, description="Job not found")
    
    # 尝试解析结果为JSON，失败则保持字符串
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
    """获取所有会话状态"""
    try:
        status = session_agent_manager.get_session_status()
        return jsonify(status), 200
    except Exception as e:
        return handle_api_error(f"获取会话状态失败: {str(e)}", 500)

@app.route('/api/sessions/cleanup', methods=['POST'])
def cleanup_sessions():
    """清理非活跃会话"""
    try:
        data = request.json or {}
        max_age = data.get('max_age_seconds', 1800)  # 默认30分钟
        
        session_agent_manager.cleanup_inactive_sessions(max_age)
        status = session_agent_manager.get_session_status()
        
        return jsonify({
            "message": f"清理完成，最大非活跃时间: {max_age}秒",
            "status": status
        }), 200
    except Exception as e:
        return handle_api_error(f"清理会话失败: {str(e)}", 500)

@app.route('/api/sessions', methods=['POST'])
def create_session():
    """创建新的聊天会话"""
    try:
        data = request.json or {}
        user_id = data.get('user_id', 'anonymous')
        title = data.get('title')
        
        # 创建RAGFlow客户端
        ragflow_client = create_ragflow_client()
        
        # 创建会话（包含RAGFlow会话）
        session = session_manager.create_session(
            user_id=user_id, 
            title=title, 
            ragflow_client=ragflow_client
        )
        
        return jsonify({
            "session_id": session.session_id,
            "title": session.title,
            "created_at": session.created_at.isoformat(),
            "ragflow_session_id": session.ragflow_session_id
        }), 201
        
    except Exception as e:
        return handle_api_error(f"创建会话失败: {str(e)}", 500)


@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """获取会话详情"""
    session = session_manager.get_session(session_id)
    if not session:
        abort(404, description="Session not found")
    
    return jsonify(session.to_dict())


@app.route('/api/sessions/<session_id>/messages', methods=['POST'])
def add_message(session_id):
    """添加消息到会话"""
    data = request.json
    if not data or 'role' not in data or 'content' not in data:
        abort(400, description="Missing role or content")
    
    message = session_manager.add_message(session_id, data['role'], data['content'])
    if not message:
        abort(404, description="Session not found")
    
    return jsonify(message.to_dict()), 201


@app.route('/api/sessions/<session_id>', methods=['PUT'])
def update_session(session_id):
    """更新会话标题"""
    data = request.json
    if not data or 'title' not in data:
        abort(400, description="Missing title")
    
    session_manager.update_session_title(session_id, data['title'])
    return jsonify({"message": "Session updated successfully"})


@app.route('/api/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """删除会话"""
    try:
        # 创建RAGFlow客户端
        ragflow_client = create_ragflow_client()
        
        # 删除会话（包含RAGFlow会话）
        success = session_manager.delete_session(session_id, ragflow_client)
        if not success:
            return handle_api_error("Session not found", 404)
        
        # 释放会话Agent
        session_agent_manager.release_agent(session_id)
        
        return jsonify({"message": "Session deleted successfully"})
        
    except Exception as e:
        return handle_api_error(f"删除会话失败: {str(e)}", 500)


@app.route('/api/users/<user_id>/sessions', methods=['GET'])
def get_user_sessions(user_id):
    """获取用户的所有会话"""
    sessions = session_manager.get_user_sessions(user_id)
    return jsonify([session.to_dict() for session in sessions])


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    try:
        # 检查数据库连接
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
    logger.info(f"在端口 {PORT} 上启动服务器")
    debug_mode = config.FLASK_DEBUG == "True" or config.FLASK_DEBUG is True
    logger.info(f"Debug模式: {debug_mode}")
    app.run(debug=debug_mode, port=PORT, host='0.0.0.0')
