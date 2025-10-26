# 🤖 AI Agent

[![CI/CD Pipeline](https://github.com/mr6923612/AIAgent/workflows/AI%20Agent%20CI/CD%20Pipeline/badge.svg)](https://github.com/mr6923612/AIAgent/actions)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Enabled-brightgreen)](https://github.com/mr6923612/AIAgent/actions)

基于 CrewAI 的智能 AI 代理系统，集成 RAGFlow 知识检索，支持本地 Docker 一键部署。

## ✨ 核心特性

### 🤖 智能对话
- 基于 Google AI (Gemini) 的智能对话
- 自然语言理解和生成
- 多轮对话上下文管理

### 📚 知识检索 (RAGFlow)
- 集成 RAGFlow 进行知识检索
- 向量化文档存储和检索
- 精准的问答支持

### 💾 高可用会话管理
- ✅ **一对一映射**: 前端 session ↔ RAGFlow session
- ✅ **自动恢复**: 服务重启后从数据库恢复映射
- ✅ **智能清理**: 启动时自动清理无效会话
- ✅ **数据库重连**: 网络故障自动恢复
- ✅ **三层查找**: 内存 → 数据库 → 创建

### 🛠️ 开发特性
- 🎨 React 现代化前端界面
- 🐳 完整的 Docker 容器化
- 🔄 GitHub Actions CI/CD
- 🎛️ YAML 配置化 Prompt
- 📊 MySQL 数据持久化

## 📑 目录

### 📘 部署与配置
- [🚀 快速开始](#-快速开始) - 环境要求、部署步骤
- [🔧 配置说明](#-配置说明) - API 密钥、环境变量
- [🤖 自定义 Prompt](#-自定义ai-agent-prompt) - Agent 配置指南
- [🛠️ 故障排除](#️-故障排除) - 常见问题、性能优化

### 📚 技术文档
- [🌐 服务架构](#-服务架构) - 组件关系、数据流
- [🏗️ 代码架构](#️-代码架构) - 核心类、设计模式
- [🆘 获取帮助](#-获取帮助) - 联系方式

---

## 🚀 快速开始

### 📋 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- Git 2.0+
- 4GB+ 内存
- 2GB+ 可用磁盘空间

---

### 🎯 部署步骤

#### 步骤 1：克隆项目
```bash
git clone <your-repo-url>
cd AIAgent
```

#### 步骤 2：启动 RAGFlow 服务
```bash
cd ragflow/docker
docker-compose up -d
cd ../..
```

等待约 30-60 秒让 RAGFlow 完全启动。

#### 步骤 3：注册 RAGFlow 并获取 API Key
1. 访问 http://localhost:80
2. 首次访问需要注册账号（推荐使用：`rag@flow.io` / `infiniflow1`）
3. 登录后，进入 **设置 (Settings)** → **API密钥 (API Keys)**
4. 点击 **创建 API Key**，复制生成的密钥

#### 步骤 4：创建并配置 .env 文件
```bash
cd crewaiBackend
# 复制模板文件
cp env.template .env
```

编辑 `.env` 文件，填入以下 API 密钥：
```bash
# Google AI API Key（从 https://aistudio.google.com/app/apikey 获取）
GOOGLE_API_KEY=your_google_api_key_here

# RAGFlow API Key（从上一步获取）
RAGFLOW_API_KEY=ragflow-xxxxxxxxxxxxx
```

#### 步骤 5：配置 Agent Prompt（可选）
```bash
# 编辑 agent_config.yaml 自定义 AI Agent 的行为和回复风格
nano agent_config.yaml
```

#### 步骤 6：运行配置脚本
```bash
# 自动获取 RAGFlow Chat ID 并更新配置
python crewaiBackend/scripts/update_agent_prompt.py --yes
```

> **💡 说明**：此脚本会自动：
> - 验证 `.env` 文件配置
> - 从 RAGFlow 获取 Chat ID 并更新到 `.env`
> - 根据 `agent_config.yaml` 更新 Agent prompt

#### 步骤 7：启动 AI Agent 服务
```bash
cd ..  # 返回项目根目录
chmod +x quick-start.sh
./quick-start.sh
```

> **注意**：`quick-start.sh` 会重启所有服务，包括 RAGFlow

#### 步骤 8：访问应用
- 🌐 **AI Agent 前端**: http://localhost:3000
- 🔧 **AI Agent 后端**: http://localhost:8012
- 📚 **RAGFlow 管理**: http://localhost:80

---

### 🛠️ 部署脚本说明

| 脚本 | 功能 | 说明 |
|------|------|------|
| `quick-start.sh` | 一键部署 | 启动所有服务并自动构建最新镜像 |
| `stop-all.sh` | 停止服务 | 停止所有运行的服务 |

**脚本功能**：
- ✅ 自动更新 `.env` 文件中的 Docker 环境配置
- ✅ 自动构建最新代码镜像
- ✅ 检测 API 密钥配置状态
- ✅ 执行健康检查并显示服务状态

**常用命令**：
```bash
./quick-start.sh    # 启动所有服务
./stop-all.sh       # 停止所有服务
```
---

## 🔧 配置说明

### ⚙️ 环境配置文件 (.env)

`.env` 文件包含所有服务配置和 API 密钥，**必须正确配置**才能运行系统。

#### 📝 关键配置项

| 配置项 | 说明 | 获取方式 |
|--------|------|----------|
| `GOOGLE_API_KEY` | Google AI API 密钥 | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `RAGFLOW_API_KEY` | RAGFlow API 密钥 | RAGFlow 管理界面 → 设置 → API密钥 |
| `RAGFLOW_CHAT_ID` | RAGFlow 聊天 ID | 运行 `update_agent_prompt.py` 自动获取 |
| `RAGFLOW_BASE_URL` | RAGFlow 服务地址 | Docker 环境: `http://ragflow-server:80` |
| `MYSQL_HOST` | MySQL 主机地址 | Docker 环境: `aiagent-mysql` |
| `MYSQL_PORT` | MySQL 端口 | `3306` |
| `MYSQL_DATABASE` | 数据库名称 | `aiagent` |
| `MYSQL_USER` | 数据库用户名 | `aiagent` |
| `MYSQL_PASSWORD` | 数据库密码 | `aiagent123` |

#### 🔑 API 密钥获取

**Google AI API Key**:
1. 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 登录 Google 账号
3. 点击 "Create API Key"
4. 复制生成的 API Key

**RAGFlow API Key**:
1. 访问 http://localhost:80
2. 登录 RAGFlow 账号
3. 进入 **设置** → **API密钥**
4. 点击 **创建 API Key**
5. 复制生成的密钥

---

## 🌐 服务架构

### 📋 服务概览

| 服务 | 端口 | 功能 | 依赖 |
|------|------|------|------|
| **aiagent-frontend** | 3000 | React 前端界面 | aiagent-backend |
| **aiagent-backend** | 8012 | Flask API 服务 | MySQL, RAGFlow |
| **aiagent-mysql** | 3306 | MySQL 数据库 | - |
| **ragflow-server** | 80 | RAGFlow 知识检索 | Ollama, MySQL, Redis |
| **ollama** | 11434 | LLM 模型服务 | - |

### 🗄️ 数据库和存储服务

- **MySQL**: 存储聊天会话、消息记录
- **Redis**: RAGFlow 缓存服务
- **Elasticsearch**: RAGFlow 文档索引
- **MinIO**: RAGFlow 文件存储

### 🔌 API接口

**AI Agent 后端 API**:
- `GET /api/health` - 健康检查
- `POST /api/crew/{session_id}` - 创建 AI 任务
- `GET /api/crew/{session_id}` - 获取任务状态

**RAGFlow API**:
- `POST /api/v1/chats/{chat_id}/sessions` - 创建会话
- `POST /api/v1/chats/{chat_id}/sessions/{session_id}/completions` - 发送消息

### 📊 服务依赖关系

```
aiagent-frontend → aiagent-backend → aiagent-mysql
                ↓
              ragflow-server → ollama
                ↓
              MySQL + Redis + Elasticsearch + MinIO
```

### 🧹 清理RAGFlow会话

系统启动时会自动清理无效的 RAGFlow 会话：

1. **数据库 → RAGFlow**: 清除数据库中不存在的 RAGFlow 会话 ID
2. **RAGFlow → 数据库**: 删除没有对应数据库记录的 RAGFlow 会话

---

## 📊 项目结构

```
AIAgent/
├── crewaiBackend/           # 后端服务
│   ├── main.py             # Flask 应用入口
│   ├── crew.py             # CrewAI Agent 定义
│   ├── config.py           # 配置管理
│   ├── agent_config.yaml   # Agent 配置文件
│   ├── .env                # 环境变量（需要创建）
│   ├── env.template        # 环境变量模板
│   ├── requirements.txt    # Python 依赖
│   ├── utils/              # 工具模块
│   │   ├── database.py     # 数据库操作
│   │   ├── ragflow_client.py # RAGFlow API 客户端
│   │   ├── sessionManager.py # 会话管理
│   │   ├── ragflow_session_manager.py # RAGFlow 会话管理
│   │   ├── session_agent_manager.py # 会话 Agent 管理
│   │   ├── jobManager.py  # 任务管理
│   │   ├── myLLM.py       # LLM 配置
│   │   └── speech_to_text.py # 语音转文字
│   ├── scripts/            # 脚本工具
│   │   └── update_agent_prompt.py # 更新 Agent 配置
│   └── tests/              # 测试文件
├── crewaiFrontend/         # 前端服务
│   ├── src/               # React 源码
│   ├── package.json       # Node.js 依赖
│   └── Dockerfile         # 前端 Docker 配置
├── ragflow/               # RAGFlow 服务
│   ├── docker/           # RAGFlow Docker 配置
│   └── docker-compose.yml # RAGFlow 服务配置
├── data/                  # 数据存储目录
│   ├── aiagent/mysql/    # AI Agent 数据库文件
│   ├── ragflow/          # RAGFlow 数据文件
│   └── ollama/models/    # Ollama 模型文件
├── docker-compose.yml     # 主 Docker Compose 配置
├── quick-start.sh         # 一键启动脚本
├── stop-all.sh           # 停止所有服务脚本
├── Makefile              # 构建和测试命令
└── README.md             # 项目文档
```

---

## 🏗️ 代码架构

### 核心类与数据结构

#### 1. 会话管理架构

**RAGFlowSessionManager (单例模式)**
```python
class RAGFlowSessionManager:
    def __init__(self):
        self.session_mapping = {}  # 内存映射: app_session_id -> ragflow_session_id
        self.db_manager = DatabaseManager()
        self.ragflow_client = RAGFlowClient()
    
    def get_or_create_session(self, app_session_id: str) -> str:
        # 三层查找: 内存 -> 数据库 -> 创建新会话
        # 1. 检查内存映射
        # 2. 查询数据库
        # 3. 创建新 RAGFlow 会话
```

**SessionAgentManager**
```python
class SessionAgentManager:
    def __init__(self):
        self.session_agents = {}  # session_id -> SessionAgent
    
    def get_or_create_agent(self, session_id: str) -> SessionAgent:
        # 获取或创建会话 Agent
        # 传递 ragflow_session_id 到 CrewAI
```

#### 2. 数据库架构

**DatabaseManager**
```python
class DatabaseManager:
    def __init__(self):
        self.connection = None
        self._connect()
    
    def _check_connection(self):
        # 自动重连机制
        # 网络故障后自动恢复连接
```

**数据表结构**
```sql
-- 聊天会话表
CREATE TABLE chat_sessions (
    id VARCHAR(36) PRIMARY KEY,
    ragflow_session_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 聊天消息表
CREATE TABLE chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(36),
    message TEXT,
    is_user BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);
```

#### 3. CrewAI 集成架构

**CrewtestprojectCrew**
```python
class CrewtestprojectCrew:
    def __init__(self):
        self.ragflow_client = RAGFlowClient()
        self.session_manager = SessionManager()
    
    def create_tasks(self, inputs: dict) -> List[Task]:
        # 优先使用传入的 ragflow_session_id
        # 如果没有，则查询数据库
        ragflow_session_id = inputs.get('ragflow_session_id')
        if not ragflow_session_id:
            ragflow_session_id = self.session_manager.get_ragflow_session_id(inputs['session_id'])
        
        # 创建 RAGFlow 任务
        return [Task(description=..., inputs={'ragflow_session_id': ragflow_session_id})]
```

### 数据流程

#### 1. 用户消息处理流程

```
用户发送消息
    ↓
前端 → aiagent-backend API
    ↓
SessionAgentManager.get_or_create_agent()
    ↓
RAGFlowSessionManager.get_or_create_session()
    ↓
CrewAI Agent 执行任务
    ↓
调用 RAGFlow API
    ↓
返回 AI 回复
    ↓
前端显示回复
```

#### 2. 会话恢复流程

```
服务重启
    ↓
RAGFlowSessionManager 初始化
    ↓
_cleanup_invalid_sessions()
    ↓
数据库 → RAGFlow 清理
    ↓
RAGFlow → 数据库清理
    ↓
加载有效会话到内存
    ↓
服务就绪
```

#### 3. 三层查找机制

```
get_or_create_session(app_session_id)
    ↓
1. 检查内存映射 session_mapping[app_session_id]
    ↓ (如果找到)
    返回 ragflow_session_id
    ↓ (如果未找到)
2. 查询数据库 SELECT ragflow_session_id FROM chat_sessions WHERE id = app_session_id
    ↓ (如果找到)
    加载到内存映射，返回 ragflow_session_id
    ↓ (如果未找到)
3. 创建新 RAGFlow 会话
    ↓
    保存到数据库和内存映射
    ↓
    返回新的 ragflow_session_id
```

### 架构层级

#### 1. 表现层 (Presentation Layer)
- **React 前端**: 用户界面和交互
- **Flask API**: RESTful API 接口

#### 2. 业务逻辑层 (Business Logic Layer)
- **SessionAgentManager**: 会话 Agent 管理
- **RAGFlowSessionManager**: RAGFlow 会话管理
- **CrewAI Agents**: AI 任务执行

#### 3. 数据访问层 (Data Access Layer)
- **DatabaseManager**: MySQL 数据库操作
- **RAGFlowClient**: RAGFlow API 客户端
- **SessionManager**: 会话数据管理

#### 4. 基础设施层 (Infrastructure Layer)
- **Docker 容器**: 服务容器化
- **MySQL**: 数据持久化
- **RAGFlow**: 知识检索服务
- **Ollama**: LLM 模型服务

### 模块职责划分

#### 1. 核心模块
- **main.py**: Flask 应用入口，API 路由
- **crew.py**: CrewAI Agent 定义和任务创建
- **config.py**: 配置管理和环境变量加载

#### 2. 工具模块
- **database.py**: 数据库连接和操作
- **ragflow_client.py**: RAGFlow API 交互
- **sessionManager.py**: 会话数据管理
- **ragflow_session_manager.py**: RAGFlow 会话映射管理
- **session_agent_manager.py**: 会话 Agent 生命周期管理
- **jobManager.py**: 异步任务管理
- **myLLM.py**: LLM 配置和调用
- **speech_to_text.py**: 语音转文字功能

#### 3. 配置模块
- **agent_config.yaml**: Agent 行为配置
- **.env**: 环境变量配置
- **docker-compose.yml**: 服务编排配置



### 设计原则

#### 1. 单一职责原则
- 每个模块只负责一个特定功能
- 数据库操作、API 调用、会话管理分离

#### 2. 依赖注入
- 通过构造函数注入依赖
- 便于测试和模块替换

#### 3. 错误处理
- 统一的异常处理机制
- 自动重试和恢复机制

#### 4. 配置驱动
- 通过配置文件控制行为
- 支持环境变量覆盖

### 核心优化

#### 1. 会话管理优化
```python
# 单例模式确保唯一实例
class RAGFlowSessionManager:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

#### 2. 三层查找机制
```python
def get_or_create_session(self, app_session_id: str) -> str:
    # 1. 内存查找
    if app_session_id in self.session_mapping:
        return self.session_mapping[app_session_id]
    
    # 2. 数据库查找
    ragflow_session_id = self.db_manager.get_ragflow_session_id(app_session_id)
    if ragflow_session_id:
        self.session_mapping[app_session_id] = ragflow_session_id
        return ragflow_session_id
    
    # 3. 创建新会话
    return self._create_new_session(app_session_id)
```

#### 3. 双向清理机制
```python
def _cleanup_invalid_sessions(self):
    # 数据库 → RAGFlow 清理
    self._cleanup_database_to_ragflow()
    
    # RAGFlow → 数据库清理
    self._cleanup_ragflow_to_database()
```

#### 4. 自动重连机制
```python
def _check_connection(self):
    try:
        self.connection.ping(reconnect=True)
    except Exception:
        self._connect()  # 自动重连
```

#### 5. 对象复用优化
```python
class SessionAgent:
    def __init__(self):
        self._crew_helper = CrewtestprojectCrew()  # 创建一次，重复使用
    
    def _create_agents(self):
        return self._crew_helper.create_agents()
    
    def _create_crew(self):
        return self._crew_helper.create_crew()
```

**效果**: ✅ 减少资源消耗，提高性能

---

## 🧪 测试与 CI/CD

### 运行测试
```bash
# 运行所有测试
make test

# 运行特定测试
pytest tests/unit/
pytest tests/integration/
```

### CI/CD 流程
- **GitHub Actions**: 自动测试、构建、部署
- **状态**: [查看流水线](https://github.com/mr6923612/AIAgent/actions)
- **本地开发**: `make dev` → `make test` → `make deploy`

## 📁 数据管理

项目使用统一的数据文件夹结构：

```
data/
├── aiagent/mysql/     # AI Agent 数据库
├── ragflow/          # RAGFlow 服务数据
└── ollama/models/    # Ollama 模型文件
```

**优势**: 数据隔离、易于备份、支持 Docker 卷挂载

## 🛠️ 故障排除

### 端口冲突
如果遇到端口冲突，可以修改 `docker-compose.yml` 中的端口映射：

```yaml
services:
  aiagent-frontend:
    ports:
      - "3001:3000"  # 改为 3001 端口
```

### 服务无法访问
1. 检查服务是否正在运行：
   ```bash
   docker-compose --profile aiagent ps
   ```

2. 查看服务日志：
   ```bash
   docker-compose --profile aiagent logs aiagent-backend
   ```

### 数据库连接问题
```bash
# 检查 MySQL 服务状态
docker-compose --profile aiagent logs aiagent-mysql

# 重启数据库服务
docker-compose --profile aiagent restart aiagent-mysql
```

### 常见问题解决

#### 1. Docker 构建失败
**问题**: `failed to prepare extraction snapshot: parent snapshot does not exist`

**解决方案**:
```bash
# 清理 Docker 构建缓存
docker builder prune -af
docker image prune -af

# 重新构建（不使用缓存）
docker-compose --profile aiagent up -d --build --no-cache
```

#### 2. RAGFlow API 认证失败
**问题**: `RAGFlow API error: Authentication error: API key is invalid!`

**解决方案**:
1. 访问 http://localhost:80
2. 进入 **设置** → **API密钥**
3. 创建新的 API Key
4. 更新 `crewaiBackend/.env` 文件中的 `RAGFLOW_API_KEY`

#### 3. 会话管理问题
**问题**: 每次请求都创建新的 RAGFlow 会话

**解决方案**:
1. 检查数据库连接是否正常
2. 确保 `ragflow_session_manager` 正确初始化
3. 查看后端日志确认会话映射是否正常

#### 4. 服务启动顺序问题
**解决方案**:
1. 先启动 RAGFlow: `cd ragflow/docker && docker-compose up -d`
2. 等待 30-60 秒让 RAGFlow 完全启动
3. 再启动 AI Agent: `./quick-start.sh`

### 性能优化建议

1. **资源要求**: 至少 4GB 内存、2GB 可用磁盘
2. **端口管理**: 确保 3000-12000 端口段可用
3. **网络隔离**: 所有服务在 `aiagent-net` 网络中通信
4. **防火墙**: 允许必要端口访问

### Ollama 和 RAGFlow 配置

#### 1. Ollama 模型管理
系统自动下载 **bge-m3** 模型用于文本嵌入。

```bash
# 查看已安装的模型
docker exec ollama ollama list

# 手动下载模型（如果需要）
docker exec ollama ollama pull bge-m3
```

#### 2. RAGFlow 配置 Ollama
访问 http://localhost:80，进入 **设置** → **模型管理**：

| 配置项 | 值 | 说明 |
|--------|-----|------|
| API地址 | `http://ollama:11434` | ⚠️ 必须用容器名而非 localhost |
| 模型名称 | `bge-m3:latest` | embedding 模型 |

**验证连接**:
```bash
docker exec ragflow-server curl http://ollama:11434
```

**常见问题**:
- **连接失败**: 确保使用 `http://ollama:11434` 而非 `localhost`
- **模型不存在**: 运行 `docker exec ollama ollama pull bge-m3`

## 🤖 自定义 AI Agent Prompt

### 快速配置

1. **编辑配置**: 修改 `crewaiBackend/agent_config.yaml`
2. **应用配置**: 运行 `python crewaiBackend/scripts/update_agent_prompt.py --yes`
3. **重启服务**: `docker-compose --profile aiagent restart aiagent-backend`

### 配置项说明

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `agent_name` | Agent 名称 | "智能客服" |
| `role` | Agent 角色 | "专业的客服代表" |
| `goal` | Agent 目标 | "提供准确、友好的客户服务" |
| `backstory` | Agent 背景 | "我是一名经验丰富的客服专家..." |
| `verbose` | 详细日志 | `true` / `false` |
| `max_iter` | 最大迭代次数 | `3` |
| `max_execution_time` | 最大执行时间(秒) | `300` |

### 故障排除

**问题**: "API key is invalid"
- **解决**: 确保 `.env` 文件中的 `RAGFLOW_API_KEY` 正确

**问题**: "You do not own the assistant"
- **解决**: 重新运行配置脚本获取正确的 `CHAT_ID`

**问题**: "Connection refused"
- **解决**: 确保 RAGFlow 服务正在运行

## 🆘 获取帮助

- **GitHub Issues**: [提交问题](https://github.com/mr6923612/AIAgent/issues)
- **文档**: 查看项目文档和配置说明
- **社区**: 参与讨论和贡献代码

---

**🎉 感谢使用 AI Agent！**