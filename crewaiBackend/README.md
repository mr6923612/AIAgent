# CrewAI Backend - 智能客服机器人后端

基于CrewAI的多模态智能客服机器人后端服务，支持文字、图片、音频输入和RAG知识库检索。

## ✨ 核心功能

- 🤖 **智能客服机器人**: 基于CrewAI的多Agent协作
- 📝 **多模态输入**: 支持文字、图片、音频输入
- 🎤 **语音转文字**: 支持音频文件上传和实时语音识别
- 🔍 **RAG检索**: 智能知识库检索和问答
- 📄 **Word文档处理**: 自动提取产品信息和图片
- 💬 **客服问答库**: 内置常见客服问题智能回答
- 🔄 **异步任务处理**: 支持长时间运行的任务
- 🌐 **RESTful API**: 标准化的API接口

## 🚀 快速开始

### 1. 环境准备
```bash
# 安装Python依赖
pip install -r requirements.txt

# 配置Google API密钥（可选）
export GOOGLE_API_KEY="your_api_key"
```

### 2. 处理Word文档（可选）
```bash
# 处理RAG文档目录中的Word文档
python scripts/process_word_docs.py
```

### 3. 启动服务器
```bash
# 直接运行主服务器
python main.py
```

### 4. 测试API
```bash
# 测试文字输入
curl -X POST http://localhost:8012/api/crew \
  -H "Content-Type: application/json" \
  -d '{"customer_input": "你好，我想了解你们的产品"}'

# 测试图片输入
curl -X POST http://localhost:8012/api/crew \
  -F "customer_input=这个产品怎么样？" \
  -F "image=@your_image.jpg"

# 测试语音转文字
curl -X POST http://localhost:8012/api/speech-to-text \
  -F "audio=@your_audio.wav" \
  -F "language=zh-CN"
```

## 📋 API接口

### POST /api/crew
运行客服机器人

**请求体 (JSON):**
```json
{
  "customer_input": "用户输入内容",
  "input_type": "text|image|voice",
  "additional_context": "额外上下文信息",
  "customer_domain": "客户所属领域",
  "project_description": "项目描述"
}
```

**请求体 (Form Data - 支持文件上传):**
```
customer_input: 用户输入内容
input_type: text|image|voice
image: 图片文件 (可选)
audio: 音频文件 (可选)
additional_context: 额外上下文
customer_domain: 客户领域
project_description: 项目描述
```

### POST /api/speech-to-text
语音转文字API

**请求体 (Form Data):**
```
audio: 音频文件 (必需)
language: 语言代码 (可选，默认zh-CN)
```

**响应:**
```json
{
  "success": true,
  "text": "识别出的文字内容",
  "language": "zh-CN"
}
```

### GET /api/crew/<job_id>
获取任务执行状态

**响应:**
```json
{
  "job_id": "任务唯一标识",
  "status": "PENDING|COMPLETE|ERROR",
  "result": "处理结果",
  "events": [
    {
      "timestamp": "2024-01-01T00:00:00",
      "data": "事件描述"
    }
  ]
}
```

## 🏗️ 项目结构

详细的项目结构说明请查看 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

```
crewaiBackend/
├── 📄 main.py                    # 主服务器入口
├── 📄 crew.py                    # CrewAI核心逻辑
├── 📁 utils/                     # 工具模块
│   ├── jobManager.py             # 任务管理器
│   ├── myLLM.py                 # LLM配置
│   ├── rag_retriever.py         # RAG检索器
│   └── word_processor.py        # Word文档处理器
├── 📁 scripts/                   # 脚本文件
│   ├── process_word_docs.py     # Word文档处理
│   ├── check_status.py          # 项目状态检查
│   └── cleanup.py               # 项目清理
├── 📁 tests/                     # 测试文件
├── 📁 docs/                      # 文档
└── 📁 rag_documents/             # RAG文档存储
    ├── sample_product.docx       # 示例产品文档
    ├── taobao_customer_service.md # 客服问答库
```

## 🔧 配置说明

### 环境变量
- `SERPER_API_KEY`: Google搜索API密钥
- `GOOGLE_API_KEY`: Google Gemini API密钥

### LLM配置
支持多种LLM提供商：
- **Google Gemini**: 推荐，支持多模态
- **OpenAI GPT**: 需要API密钥
- **本地模型**: 通过Ollama等

### RAG文档配置
- 支持Markdown文档
- 支持Word文档（.docx）
- 自动提取图片和文字
- 按产品分组处理

## 📚 文档指南

- [项目结构说明](PROJECT_STRUCTURE.md)
- [Google API设置](docs/GOOGLE_API_SETUP.md)
- [Word文档使用说明](docs/WORD_DOCS_USAGE.md)
- [RAG文档系统说明](docs/README.md)

## 🧪 测试和调试

### 运行测试
```bash
# 检查项目状态
python scripts/check_status.py

# 测试Word文档处理
python scripts/process_word_docs.py

# 清理项目文件
python scripts/cleanup.py
```

### 调试模式
```bash
# 启用调试模式
python main.py --debug
```

## 🛠️ 开发指南

### 添加新的Agent
1. 在 `crew.py` 中定义新的Agent
2. 配置角色、目标和背景故事
3. 添加到Crew中

### 添加新的Task
1. 在 `crew.py` 中定义新的Task
2. 配置描述、期望输出和Agent
3. 添加到任务流程中

### 扩展RAG功能
1. 在 `utils/rag_retriever.py` 中添加新的检索方法
2. 更新知识库文档
3. 测试检索效果

## 🔍 故障排除

### 常见问题
1. **依赖安装失败**: 检查Python版本（需要3.10+）
2. **API调用失败**: 检查API密钥和网络连接
3. **任务执行失败**: 查看控制台日志输出
4. **Word文档处理失败**: 检查文档格式和权限

### 日志查看
服务器运行时会输出详细的日志信息：
- 任务执行状态
- API调用结果
- 错误信息和堆栈跟踪

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [CrewAI](https://github.com/joaomdmoura/crewAI) - 多Agent协作框架
- [LangChain](https://github.com/langchain-ai/langchain) - LLM应用开发框架
- [Flask](https://flask.palletsprojects.com/) - Web框架