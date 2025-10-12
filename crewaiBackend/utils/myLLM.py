import os
from langchain_google_genai import ChatGoogleGenerativeAI


GOOGLE_CHAT_MODEL = "gemini-2.5-flash"
GOOGLE_CHAT_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# 模型初始化函数
def my_llm(llmType):
    """初始化LLM模型，使用Google Chat API"""
    print(f"正在初始化Google Chat模型: {GOOGLE_CHAT_MODEL}")
    print(f"Google API密钥: {GOOGLE_CHAT_API_KEY[:20]}...")
    
    # 使用Google Chat API
    llm = ChatGoogleGenerativeAI(
        model=GOOGLE_CHAT_MODEL,
        google_api_key=GOOGLE_CHAT_API_KEY,
        temperature=0.7,
        max_output_tokens=4000,
        timeout=60,
    )
    return llm
