from langchain_openai import ChatOpenAI

# OpenRouter API 配置
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"  
OPENROUTER_CHAT_API_KEY = "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"  
OPENROUTER_CHAT_MODEL = "alibaba/tongyi-deepresearch-30b-a3b:free"  

# 模型初始化函数
def my_llm(llmType):
    # 使用OpenRouter API
    llm = ChatOpenAI(
        base_url=OPENROUTER_API_BASE,
        api_key=OPENROUTER_CHAT_API_KEY,
        model=OPENROUTER_CHAT_MODEL,
        temperature=0.7,
    )
    return llm