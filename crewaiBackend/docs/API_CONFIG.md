# API配置说明

## 🔐 安全配置

为了保护您的API密钥安全，项目使用了以下配置方式：

### 1. 配置文件方式（推荐）

1. **复制配置模板**
   ```bash
   cp config.py.template config.py
   ```

2. **编辑配置文件**
   ```python
   # 编辑 crewaiBackend/config.py 文件中的Config类
   class Config:
       GOOGLE_API_KEY = "your_actual_google_api_key"
       RAGFLOW_API_KEY = "your_actual_ragflow_api_key"
   ```

3. **配置文件已被Git忽略**
   - `config.py` 文件不会被提交到Git仓库
   - 只有 `config.py.template` 模板文件会被跟踪
   - 所有配置都通过Config类统一管理

### 2. 环境变量方式

```bash
# 设置环境变量
export GOOGLE_API_KEY="your_google_api_key"
export RAGFLOW_BASE_URL="http://localhost:80"
export RAGFLOW_API_KEY="your_ragflow_api_key"
export RAGFLOW_CHAT_ID="63854abaabb511f0bf790ec84fa37cec"
```

### 3. .env文件方式

1. **复制环境变量模板**
   ```bash
   cp env.template .env
   ```

2. **编辑.env文件**
   ```bash
   GOOGLE_API_KEY=your_actual_google_api_key
   RAGFLOW_API_KEY=your_actual_ragflow_api_key
   ```

## 📋 必需的API密钥

### Google API Key
- **用途**: 用于Google Gemini大语言模型
- **获取方式**: 
  1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
  2. 创建新的API密钥
  3. 复制密钥到配置文件

### RAGFlow API Key
- **用途**: 用于RAGFlow知识检索服务
- **获取方式**:
  1. 部署RAGFlow服务
  2. 在RAGFlow界面中获取API密钥
  3. 复制密钥到配置文件

## 🔧 配置优先级

系统按以下优先级加载配置：

1. **配置文件** (`config.py`) - 最高优先级
2. **环境变量** - 中等优先级
3. **默认值** - 最低优先级

## ⚠️ 安全注意事项

1. **永远不要提交API密钥到Git仓库**
2. **使用配置文件时，确保config.py在.gitignore中**
3. **定期轮换API密钥**
4. **不要在日志中输出API密钥**
5. **在生产环境中使用环境变量**

## 🐛 故障排除

### 配置文件未找到
```
警告: 未找到config.py文件，请复制config.py.template为config.py并配置API密钥
```
**解决方案**: 复制模板文件并配置API密钥

### API密钥无效
```
ValueError: RAGFlow API key is required
```
**解决方案**: 检查API密钥是否正确配置

### 服务连接失败
```
ConnectionError: Failed to connect to RAGFlow
```
**解决方案**: 检查RAGFlow服务是否运行，URL是否正确

## 📝 配置示例

### 开发环境配置
```python
# config.py
GOOGLE_API_KEY = "AIzaSyBvQZ8QZ8QZ8QZ8QZ8QZ8QZ8QZ8QZ8QZ8Q"
RAGFLOW_BASE_URL = "http://localhost:80"
RAGFLOW_API_KEY = "ragflow-ZkMzMwODc2YWM1YzExZjBhNGM1MGVjOD"
RAGFLOW_CHAT_ID = "63854abaabb511f0bf790ec84fa37cec"
FLASK_ENV = "development"
FLASK_DEBUG = True
PORT = 8012
```

### 生产环境配置
```python
# config.py
GOOGLE_API_KEY = "your_production_google_api_key"
RAGFLOW_BASE_URL = "https://your-ragflow-domain.com"
RAGFLOW_API_KEY = "your_production_ragflow_api_key"
RAGFLOW_CHAT_ID = "your_production_chat_id"
FLASK_ENV = "production"
FLASK_DEBUG = False
PORT = 8012
```
