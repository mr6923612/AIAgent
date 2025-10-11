# Google Chat API 配置说明

## 🔧 配置更改

系统已从智谱AI BigModel切换到Google Chat API (Gemini 2.5 Flash)。

### 主要更改：

1. **LLM模型**: `glm-4.6` → `gemini-2.5-flash`
2. **API提供商**: 智谱AI → Google
3. **API密钥**: 使用 `GOOGLE_API_KEY` 环境变量

## 🚀 快速开始

### 1. 获取Google API密钥

1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 登录Google账户
3. 创建新的API密钥
4. 复制生成的API密钥

### 2. 设置环境变量

```bash
# Windows (PowerShell)
$env:GOOGLE_API_KEY="your-google-api-key-here"

# Windows (CMD)
set GOOGLE_API_KEY=your-google-api-key-here

# Linux/Mac
export GOOGLE_API_KEY="your-google-api-key-here"
```

### 3. 安装依赖

```bash
cd crewaiBackend
pip install -r requirements.txt
```

### 4. 测试配置

```bash
python test_google_api.py
```

### 5. 启动服务

```bash
python main.py
```

## 📋 配置详情

### API配置 (utils/myLLM.py)

```python
GOOGLE_CHAT_MODEL = "gemini-2.5-flash"
GOOGLE_CHAT_API_KEY = os.getenv("GOOGLE_API_KEY", "your-default-key")
```

### 服务配置 (main.py)

```python
LLM_TYPE = "google"  # 已从 "bigmodel" 更改
```

## 🧪 测试功能

### 1. API连接测试
```bash
python test_google_api.py
```

### 2. 完整系统测试
```bash
python test_text_input.py
```

### 3. 多模态测试
```bash
python test_multimodal.py
```

## ⚠️ 注意事项

1. **API限制**: Google Gemini API有使用限制，请查看官方文档
2. **网络连接**: 确保能够访问Google API服务
3. **API密钥安全**: 不要将API密钥提交到版本控制系统
4. **模型性能**: Gemini 2.5 Flash是Google的最新模型，性能优秀

## 🔍 故障排除

### 常见问题：

1. **API密钥无效**
   - 检查密钥是否正确
   - 确认密钥有足够的权限

2. **网络连接问题**
   - 检查防火墙设置
   - 确认网络可以访问Google服务

3. **模型不可用**
   - 检查模型名称是否正确
   - 确认API密钥支持该模型

### 调试命令：

```bash
# 检查环境变量
echo $GOOGLE_API_KEY

# 测试网络连接
curl -I https://generativelanguage.googleapis.com

# 运行详细测试
python test_google_api.py
```

## 📚 相关文档

- [Google AI Studio](https://makersuite.google.com/)
- [Gemini API文档](https://ai.google.dev/docs)
- [LangChain Google集成](https://python.langchain.com/docs/integrations/llms/google_vertex_ai)
