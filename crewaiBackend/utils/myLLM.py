import os
from langchain_google_genai import ChatGoogleGenerativeAI

# 导入配置
try:
    from ..config import config
    GOOGLE_CHAT_MODEL = config.LLM_MODEL
    GOOGLE_CHAT_API_KEY = config.GOOGLE_API_KEY
    LLM_TEMPERATURE = config.LLM_TEMPERATURE
    LLM_MAX_TOKENS = config.LLM_MAX_TOKENS
    LLM_TIMEOUT = config.LLM_TIMEOUT
except ImportError:
    GOOGLE_CHAT_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    GOOGLE_CHAT_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4000"))
    LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "60"))

# 模型初始化函数
def my_llm(llmType):
    """初始化LLM模型，使用Google Chat API"""
    print(f"正在初始化Google Chat模型: {GOOGLE_CHAT_MODEL}")
    print(f"Google API密钥: {GOOGLE_CHAT_API_KEY[:20]}...")
    print(f"模型参数: temperature={LLM_TEMPERATURE}, max_tokens={LLM_MAX_TOKENS}, timeout={LLM_TIMEOUT}")
    
    # 验证API密钥
    if not GOOGLE_CHAT_API_KEY:
        raise ValueError("Google API密钥未配置，请在config.py中设置GOOGLE_API_KEY")
    
    # 使用Google Chat API
    llm = ChatGoogleGenerativeAI(
        model=GOOGLE_CHAT_MODEL,
        google_api_key=GOOGLE_CHAT_API_KEY,
        temperature=LLM_TEMPERATURE,
        max_output_tokens=LLM_MAX_TOKENS,
        timeout=LLM_TIMEOUT,
    )
    return llm
