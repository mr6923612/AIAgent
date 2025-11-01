"""
API Configuration File
Use environment variables to manage sensitive information, please create .env file and fill in your actual API keys
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration class"""
    
    # Google API configuration
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    
    # RAGFlow configuration
    RAGFLOW_BASE_URL = os.getenv("RAGFLOW_BASE_URL", "http://localhost:80")
    RAGFLOW_API_KEY = os.getenv("RAGFLOW_API_KEY", "")
    RAGFLOW_CHAT_ID = os.getenv("RAGFLOW_CHAT_ID", "")
    
    # Other API configuration (if needed)
    # OPENAI_API_KEY = "your_openai_api_key_here"
    # ANTHROPIC_API_KEY = "your_anthropic_api_key_here"
    
    # MySQL database configuration
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3307"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "aiagent_chat")
    
    # Service configuration
    FLASK_ENV = "development"
    FLASK_DEBUG = True  # Re-enable debug mode
    PORT = 8012
    
    # LLM configuration
    LLM_TYPE = "google"
    LLM_MODEL = "gemini-2.5-flash"
    LLM_TEMPERATURE = 0.7
    LLM_MAX_TOKENS = 4000
    LLM_TIMEOUT = 60
    
    # Request configuration
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    
    # Logging configuration
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    


# Create configuration instance
config = Config()
