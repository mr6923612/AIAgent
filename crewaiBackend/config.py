"""
API配置文件
使用环境变量管理敏感信息，请创建.env文件并填入您的实际API密钥
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """应用配置类"""
    
    # Google API配置
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    
    # RAGFlow配置
    RAGFLOW_BASE_URL = os.getenv("RAGFLOW_BASE_URL", "http://localhost:80")
    RAGFLOW_API_KEY = os.getenv("RAGFLOW_API_KEY", "")
    RAGFLOW_CHAT_ID = os.getenv("RAGFLOW_CHAT_ID", "")
    
    # 其他API配置（如需要）
    # OPENAI_API_KEY = "your_openai_api_key_here"
    # ANTHROPIC_API_KEY = "your_anthropic_api_key_here"
    
    # MySQL数据库配置
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3307"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "aiagent_chat")
    
    # 服务配置
    FLASK_ENV = "development"
    FLASK_DEBUG = True  # 重新启用debug mode
    PORT = 8012
    
    # LLM配置
    LLM_TYPE = "google"
    LLM_MODEL = "gemini-2.5-flash"
    LLM_TEMPERATURE = 0.7
    LLM_MAX_TOKENS = 4000
    LLM_TIMEOUT = 60
    
    # 请求配置
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    
    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    


# 创建配置实例
config = Config()
