"""
基于Flask的客服机器人API后端服务
主要功能：
1. 接收客户请求（文本+图片）
2. 异步处理请求
3. 返回处理结果
"""

import os
import json
from datetime import datetime
from threading import Thread
from uuid import uuid4

from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import base64

from crew_with_crewai_rag import CrewtestprojectCrew
from utils.jobManager import append_event, jobs, jobs_lock, Event
from utils.myLLM import my_llm
from utils.speech_to_text import speech_converter


# 服务访问的端口
PORT = 8012
# 设置SERPER_API_KEY环境变量，用于Google搜索引擎的API
os.environ["SERPER_API_KEY"] = "9d2aa95f5a0831110a3ec837996ff37b906e99dd"
LLM_TYPE = "google"


# 创建Flask应用实例
app = Flask(__name__)
# 启用CORS，处理跨域资源共享以便任何来源的请求可以访问以/api/开头的接口
CORS(app, resources={r"/api/*": {"origins": "*"}})


def kickoff_crew(job_id, inputs):
    """异步执行客服机器人分析"""
    global LLM_TYPE
    print(f"开始处理任务 {job_id}")
    
    try:
        # 创建客服机器人实例并执行分析
        results = CrewtestprojectCrew(job_id, my_llm(LLM_TYPE)).kickoff(inputs)
        print(f"任务 {job_id} 分析完成")
        
        # 更新任务状态为完成
        with jobs_lock:
            jobs[job_id].status = 'COMPLETE'
            jobs[job_id].result = results
            jobs[job_id].events.append(
                Event(timestamp=datetime.now(), data="客服机器人分析完成"))
                
    except Exception as e:
        # 处理异常
        print(f"任务 {job_id} 分析错误: {e}")
        append_event(job_id, f"客服机器人分析过程中出现错误: {e}")
        with jobs_lock:
            jobs[job_id].status = 'ERROR'
            jobs[job_id].result = str(e)


@app.route('/api/crew', methods=['POST'])
def run_crew():
    """处理客服机器人请求"""
    print("收到客服机器人请求")
    
    # 处理文件上传请求
    if request.files:
        print("检测到文件上传请求")
        customer_input = request.form.get('customer_input', '')
        input_type = request.form.get('input_type', 'text')
        additional_context = request.form.get('additional_context', '')
        customer_domain = request.form.get('customer_domain', '')
        project_description = request.form.get('project_description', '')
        
        # 处理图片文件
        image_data = None
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file and image_file.filename:
                print(f"接收到图片文件: {image_file.filename}")
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
                input_type = 'text+image' if customer_input.strip() else 'image'
                customer_input = f"{customer_input} [上传了图片]"
        
        # 处理音频文件（语音转文字）
        if 'audio' in request.files:
            audio_file = request.files['audio']
            if audio_file and audio_file.filename:
                print(f"接收到音频文件: {audio_file.filename}")
                audio_data = base64.b64encode(audio_file.read()).decode('utf-8')
                
                # 语音转文字
                print("开始语音转文字...")
                transcribed_text = speech_converter.convert_audio_to_text(audio_data)
                
                if transcribed_text:
                    print(f"语音转文字成功: {transcribed_text}")
                    customer_input = transcribed_text
                    input_type = 'voice'
                    # 语音转文字成功后，不再需要传递音频数据给LLM
                    audio_data = None
                else:
                    print("语音转文字失败，直接返回错误信息")
                    # 语音转文字失败时，直接返回错误信息，不调用LLM
                    return jsonify({
                        "error": "抱歉，我无法听清楚您刚才说的话。请您：\n\n1. 在安静的环境中重新录音\n2. 说话时声音稍微大一些，语速慢一些\n3. 或者您也可以直接输入文字，我会立即为您处理\n\n感谢您的理解，期待为您提供更好的服务！"
                    }), 400
        
        inputs = {
            "customer_input": customer_input,
            "input_type": input_type,
            "additional_context": additional_context,
            "customer_domain": customer_domain,
            "project_description": project_description,
            "image_data": image_data,
            "audio_data": audio_data
        }
    else:
        # 处理JSON请求
        data = request.json
        if not data or 'customer_input' not in data:
            abort(400, description="Invalid input data provided. Required: customer_input")
        
        print(f"接收到的客户输入: {data['customer_input']}")
        
        inputs = {
            "customer_input": data['customer_input'],
            "input_type": data.get('input_type', 'text'),
            "additional_context": data.get('additional_context', ''),
            "customer_domain": data.get('customer_domain', ''),
            "project_description": data.get('project_description', ''),
            "image_data": None,
            "audio_data": None
        }
    
    # 创建任务并异步执行
    job_id = str(uuid4())
    
    # 初始化任务状态
    append_event(job_id, "客服机器人开始分析客户需求...")
    
    thread = Thread(target=kickoff_crew, args=(job_id, inputs))
    thread.start()
    
    return jsonify({"job_id": job_id}), 202




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


if __name__ == '__main__':
    print(f"在端口 {PORT} 上启动服务器")
    app.run(debug=True, port=PORT)
