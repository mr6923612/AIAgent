# AI Agent 智能客服系统

一个基于CrewAI和RAGFlow的智能客服系统，支持多模态输入和会话管理。

## ✨ 功能特性

### 🤖 智能客服系统
- **CrewAI框架**：基于CrewAI构建的智能客服系统
- **多Agent协作**：支持多个AI Agent协同工作
- **上下文理解**：智能理解用户意图和上下文
- **个性化响应**：根据用户历史提供个性化服务

### 📚 知识库集成
- **RAGFlow集成**：集成RAGFlow进行知识检索和问答
- **向量搜索**：支持语义搜索和相似度匹配
- **知识更新**：支持动态更新知识库内容
- **多源数据**：支持多种数据源的知识整合

### 💬 会话管理
- **多会话支持**：支持同时管理多个对话会话
- **会话持久化**：使用MySQL数据库持久化存储
- **会话同步**：本地会话与RAGFlow会话同步
- **会话删除**：支持删除本地和RAGFlow会话

### 🎤 多模态输入
- **文本输入**：支持自然语言文本输入
- **语音输入**：支持语音转文字功能
- **图片输入**：支持图片上传和分析
- **文件上传**：支持多种文件格式上传

### 🔄 实时交互
- **流式对话**：支持流式对话和实时响应
- **任务状态**：实时显示任务执行状态
- **进度跟踪**：可视化任务执行进度
- **错误处理**：智能错误处理和用户提示

### 🛠️ 开发工具
- **健康检查**：自动检查服务状态
- **测试框架**：完整的测试用例和工具
- **清理工具**：自动清理测试数据和会话
- **监控脚本**：实时监控系统运行状态

## 🛠️ 技术栈

### 后端技术
- **Python 3.9+** - 主要编程语言
- **Flask 3.0+** - Web框架和API服务
- **CrewAI 0.1.32** - AI Agent框架
- **LangChain** - LLM应用开发框架
- **Google Generative AI** - 大语言模型服务
- **RAGFlow** - 知识库和RAG服务
- **MySQL 8.0+** - 关系型数据库
- **PyMySQL** - MySQL数据库连接器
- **python-dotenv** - 环境变量管理

### 前端技术
- **React 18+** - 用户界面框架
- **Vite** - 构建工具和开发服务器
- **Lucide React** - 图标库
- **Axios** - HTTP客户端
- **CSS3** - 样式设计

### 部署技术
- **Docker** - 容器化部署
- **Docker Compose** - 多容器编排
- **MySQL** - 数据持久化
- **Qdrant** - 向量数据库
- **Ollama** - 本地LLM服务

### 开发工具
- **Git** - 版本控制
- **Python-dotenv** - 环境变量管理
- **pytest** - 测试框架
- **requests** - HTTP请求库
- **SpeechRecognition** - 语音识别
- **pydub** - 音频处理

## 🏗️ 系统架构

### LLM调用架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端界面      │    │   后端API       │    │   RAGFlow       │
│   (React)       │───►│   (Flask)       │───►│   (知识检索)    │
│   Port: 3000    │    │   Port: 5000    │    │   Port: 9380    │
│   用户输入      │    │   接收请求      │    │   获取知识      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Google AI     │
                       │   (Gemini API)  │
                       │   生成响应      │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   后端API       │
                       │   (Flask)       │
                       │   Port: 5000    │
                       │   流式输出      │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   前端界面      │
                       │   (React)       │
                       │   Port: 3000    │
                       │   展示响应      │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   MySQL数据库   │
                       │   Port: 3307    │
                       │   会话存储      │
                       └─────────────────┘
```

### 详细调用流程
```
前端用户输入 → 发送到后端API
    ↓
后端接收请求 → 调用RAGFlow知识检索
    ↓
RAGFlow返回相关知识 → 后端整合上下文
    ↓
后端调用Google AI (Gemini) → 生成响应
    ↓
Gemini流式输出 → 后端接收并转发
    ↓
后端流式返回 → 前端实时展示
```

## 📁 项目结构

```
AIAgent/
├── 📂 crewaiBackend/                    # 后端服务
│   ├── 📂 utils/                        # 工具模块
│   │   ├── database.py                  # 数据库管理
│   │   ├── sessionManager.py            # 会话管理
│   │   ├── ragflow_client.py            # RAGFlow客户端
│   │   ├── myLLM.py                     # LLM配置
│   │   ├── speech_to_text.py            # 语音转文字
│   │   └── jobManager.py                # 任务管理
│   ├── 📂 scripts/                      # 脚本工具
│   │   ├── check_requirements.py        # 依赖检查
│   │   ├── cleanup_sessions.py          # 会话清理
│   │   ├── quick_cleanup.py             # 快速清理
│   │   ├── run_tests.py                 # 测试运行
│   │   └── test_cleanup.py              # 测试清理
│   ├── 📂 tests/                        # 测试用例
│   │   ├── test_session_management.py   # 会话管理测试
│   │   └── README.md                    # 测试文档
│   ├── 📂 docs/                         # 文档
│   │   ├── API_CONFIG.md                # API配置
│   │   └── GOOGLE_API_SETUP.md          # Google API设置
│   ├── main.py                          # Flask应用入口
│   ├── crew.py                          # CrewAI配置
│   ├── config.py                        # 配置文件
│   ├── init_database.py                 # 数据库初始化
│   ├── env.template                     # 环境变量模板
│   ├── requirements.txt                 # Python依赖
│   └── SETUP.md                         # 后端设置指南
├── 📂 crewaiFrontend/                   # 前端应用
│   ├── 📂 src/
│   │   ├── 📂 components/               # React组件
│   │   │   ├── ChatInterface.jsx        # 聊天界面
│   │   │   ├── Login.jsx                # 登录组件
│   │   │   └── Register.jsx             # 注册组件
│   │   ├── 📂 utils/                    # 工具函数
│   │   │   └── api.js                   # API调用
│   │   ├── App.jsx                      # 主应用组件
│   │   └── main.jsx                     # 应用入口
│   ├── package.json                     # Node.js依赖
│   └── vite.config.js                   # Vite配置
├── 📂 tests/                            # 集成测试
│   ├── 📂 integration/                  # 集成测试
│   ├── 📂 unit/                         # 单元测试
│   ├── 📂 llm_tests/                    # LLM测试
│   └── run_all_tests.py                 # 测试运行器
├── 🐳 部署文件
│   ├── docker-compose.yml               # Docker编排
│   ├── deploy.sh                        # Linux/macOS部署脚本
│   ├── deploy.bat                       # Windows部署脚本
│   ├── install_ragflow.sh               # RAGFlow安装脚本(Linux/macOS)
│   ├── install_ragflow.bat              # RAGFlow安装脚本(Windows)
│   └── health_check.py                  # 健康检查脚本
├── 📚 文档
│   ├── README.md                        # 项目说明
│   ├── DEPLOYMENT.md                    # 部署指南
│   └── .gitignore                       # Git忽略文件
└── 📂 mysql_data/                       # MySQL数据目录(Docker)
```

## 🚀 快速开始

### 环境要求
- **Docker 20.10+** 和 **Docker Compose 2.0+**
- **Python 3.9+** (本地开发)
- **Node.js 16+** (前端开发)
- **MySQL 8.0+** (数据库)

### 一键部署 (推荐)

#### 方法一：使用部署脚本

**Linux/macOS:**
```bash
# 克隆项目
git clone <repository-url>
cd AIAgent

# 运行部署脚本（包含RAGFlow安装）
chmod +x deploy.sh
./deploy.sh
```

**Windows:**
```cmd
# 克隆项目
git clone <repository-url>
cd AIAgent

# 运行部署脚本（包含RAGFlow安装）
deploy.bat
```

#### 方法二：分步安装

**1. 安装RAGFlow:**
```bash
# Linux/macOS
chmod +x install_ragflow.sh
./install_ragflow.sh

# Windows
install_ragflow.bat
```

**2. 安装AI Agent:**
```bash
# 配置环境变量
cp crewaiBackend/env.template crewaiBackend/.env
# 编辑 .env 文件，填入API密钥

# 启动AI Agent服务
docker-compose up -d
```

#### 方法二：手动部署

1. **克隆项目**
```bash
git clone <repository-url>
cd AIAgent
```

2. **配置环境变量**
```bash
# 复制环境变量模板
cp crewaiBackend/env.template crewaiBackend/.env

# 编辑配置文件，填入您的API密钥
nano crewaiBackend/.env  # 或使用您喜欢的编辑器
```

3. **启动服务**
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

4. **初始化数据库**
```bash
# 初始化数据库表
docker-compose exec aiagent-backend python init_database.py
```

5. **访问应用**
- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:5000
- **RAGFlow**: http://localhost:9380

### 健康检查
```bash
# 检查所有服务状态
python health_check.py

# 持续监控模式
python health_check.py --continuous 30

# 保存检查报告
python health_check.py --save-report
```

### 常用命令

#### 服务管理
```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启服务
docker-compose restart

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 测试和清理
```bash
# 运行所有测试
python crewaiBackend/scripts/run_tests.py

# 清理所有会话
python crewaiBackend/scripts/quick_cleanup.py

# 检查依赖包
python crewaiBackend/scripts/check_requirements.py
```

#### RAGFlow管理
```bash
# 安装RAGFlow
./install_ragflow.sh  # Linux/macOS
install_ragflow.bat   # Windows

# 查看RAGFlow日志
docker logs -f ragflow-server

# 重启RAGFlow
cd ragflow/docker && docker compose restart
```

### 本地开发

#### 后端开发
```bash
# 进入后端目录
cd crewaiBackend

# 安装Python依赖
pip install -r requirements.txt

# 配置环境变量
cp env.template .env
# 编辑.env文件，填入您的API密钥

# 初始化数据库
python init_database.py

# 启动后端服务
python main.py
```

#### 前端开发
```bash
# 进入前端目录
cd crewaiFrontend

# 安装Node.js依赖
npm install

# 启动开发服务器
npm start
```

# 仅启动AI Agent相关服务
docker-compose --profile aiagent up -d
```

## 配置说明

### 环境变量配置

所有敏感信息都通过环境变量管理，请创建 `.env` 文件：

```bash
# 复制模板文件
cp crewaiBackend/env.template crewaiBackend/.env

# 编辑配置文件
# 填入您的实际API密钥和配置
```

详细配置说明请参考：[SETUP.md](crewaiBackend/SETUP.md)

### 环境变量列表

```bash
# Google API配置
GOOGLE_API_KEY=your_google_api_key

# RAGFlow配置
RAGFLOW_BASE_URL=http://localhost:80
RAGFLOW_API_KEY=your_ragflow_api_key
RAGFLOW_CHAT_ID=your_chat_id

# MySQL配置
MYSQL_HOST=localhost
MYSQL_PORT=3307
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=aiagent_chat
```

### 安全注意事项

- **永远不要**将 `.env` 文件提交到Git仓库
- 确保 `.env` 文件在 `.gitignore` 中
- 定期轮换API密钥

## API文档

### 会话管理

- `POST /api/sessions` - 创建新会话
- `GET /api/sessions/{session_id}` - 获取会话详情
- `DELETE /api/sessions/{session_id}` - 删除会话
- `PUT /api/sessions/{session_id}` - 更新会话标题
- `GET /api/users/{user_id}/sessions` - 获取用户所有会话

### 消息管理

- `POST /api/sessions/{session_id}/messages` - 添加消息到会话

### 客服机器人

- `POST /api/crew` - 发送消息给客服机器人
- `GET /api/crew/{job_id}` - 获取任务状态

## 开发指南

### 代码结构优化

1. **后端优化**：
   - 统一的错误处理机制
   - 公共API请求方法
   - 模块化的会话管理
   - 完善的日志记录

2. **前端优化**：
   - 统一的API调用工具
   - 组件化的UI设计
   - 错误处理机制
   - 响应式设计

### 测试和清理

1. **测试用例**：
   - 所有测试用例都会自动清理创建的会话
   - 使用 `scripts/test_cleanup.py` 管理测试会话
   - 运行 `python scripts/run_tests.py` 执行所有测试

2. **会话清理**：
   - 使用 `scripts/cleanup_sessions.py` 清理所有会话
   - 支持清理本地会话和RAGFlow会话
   - 支持清理数据库表

3. **测试工具**：
   ```bash
   # 运行所有测试
   python scripts/run_tests.py
   
   # 运行指定测试
   python scripts/run_tests.py --test test_session_management
   
   # 只运行清理
   python scripts/run_tests.py --cleanup-only
   
   # 清理所有会话
   python scripts/cleanup_sessions.py
   ```

### 添加新功能

1. **后端**：在相应的模块中添加新功能
2. **前端**：在`utils/api.js`中添加API调用，在组件中使用
3. **测试**：编写相应的测试用例，确保测试后清理

## 故障排除

### 常见问题

1. **RAGFlow连接失败**：
   - 检查RAGFlow服务是否运行
   - 验证API密钥和URL配置
   - 检查网络连接

2. **数据库连接失败**：
   - 检查MySQL服务状态
   - 验证数据库配置
   - 检查数据库权限

3. **前端API调用失败**：
   - 检查后端服务是否运行
   - 验证API端点URL
   - 检查CORS配置

### 日志查看

```bash
# 查看后端日志
tail -f crewaiBackend/app.log

# 查看Docker日志
docker-compose logs -f aiagent-backend
```

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License

## 🔧 故障排除

### 常见问题

#### 1. 服务启动失败
```bash
# 检查Docker状态
docker --version
docker-compose --version

# 检查端口占用
netstat -tulpn | grep :3000
netstat -tulpn | grep :5000

# 查看详细错误日志
docker-compose logs aiagent-backend
```

#### 2. 数据库连接失败
```bash
# 检查MySQL容器状态
docker-compose ps backend-mysql

# 重启数据库服务
docker-compose restart backend-mysql

# 重新初始化数据库
docker-compose exec aiagent-backend python init_database.py
```

#### 3. RAGFlow连接问题
```bash
# 检查RAGFlow状态
docker ps | grep ragflow

# 重启RAGFlow
cd ragflow/docker && docker compose restart

# 查看RAGFlow日志
docker logs -f ragflow-server
```

#### 4. API密钥错误
```bash
# 检查环境变量
docker-compose exec aiagent-backend env | grep API

# 重新加载配置
docker-compose down && docker-compose up -d
```

### 性能优化

#### 内存优化
```bash
# 检查内存使用
docker stats

# 限制容器内存使用
# 在docker-compose.yml中添加内存限制
```

#### 数据库优化
```bash
# 检查数据库性能
docker-compose exec backend-mysql mysql -u root -p -e "SHOW PROCESSLIST;"
```

## 📚 相关文档

- [🚀 部署指南](DEPLOYMENT.md) - 详细的部署和配置说明
- [🔧 后端设置指南](crewaiBackend/SETUP.md) - 后端环境配置
- [🧪 测试文档](crewaiBackend/tests/README.md) - 测试用例和工具

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

如有问题或建议，请提交Issue或联系开发团队。