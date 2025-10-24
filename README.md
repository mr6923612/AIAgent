# 🤖 AI Agent

[![CI/CD Pipeline](https://github.com/mr6923612/AIAgent/workflows/AI%20Agent%20CI/CD%20Pipeline/badge.svg)](https://github.com/mr6923612/AIAgent/actions)
[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Enabled-brightgreen)](https://github.com/mr6923612/AIAgent/actions)

基于CrewAI的智能AI代理系统，支持本地Docker部署。

## ✨ 功能特性

- 🤖 **智能对话** - 基于Google AI (Gemini)的智能对话系统
- 📚 **知识检索** - 集成RAGFlow进行知识检索和问答
- 💾 **会话管理** - 支持多轮对话和会话持久化
- 🎨 **现代UI** - React前端界面，响应式设计
- 🐳 **容器化** - 完整的Docker容器化部署
- 🔄 **CI/CD** - GitHub Actions自动化测试和部署流程

## 🌐 服务架构

### 📋 服务概览
| 服务类型 | 服务名称 | 端口 | 访问地址 | 用途 |
|---------|---------|------|----------|------|
| **前端应用** | aiagent-frontend | 3000 | http://localhost:3000 | React前端界面 |
| **后端API** | aiagent-backend | 8012 | http://localhost:8012 | Flask后端服务 |
| **RAGFlow Web** | ragflow-server | 80 | http://localhost:80 | 知识库管理界面 |
| **RAGFlow API** | ragflow-server | 9380 | http://localhost:9380 | 知识检索API |

### 🗄️ 数据库和存储服务
| 服务名称 | 端口 | 连接信息 | 用途 |
|---------|------|----------|------|
| **AI Agent MySQL** | 3307 | `localhost:3307` | AI Agent专用数据库 |
| **RAGFlow MySQL** | 5455 | `localhost:5455` | RAGFlow专用数据库 |
| **RAGFlow Redis** | 6379 | `localhost:6379` | RAGFlow缓存服务 |
| **MinIO控制台** | 9001 | http://localhost:9001 | 对象存储管理界面 |
| **MinIO API** | 9000 | http://localhost:9000 | 对象存储API |
| **Elasticsearch** | 1200 | http://localhost:1200 | 搜索引擎服务 |
| **Ollama LLM** | 11434 | http://localhost:11434 | 本地LLM服务 |

### 🔌 API接口

#### 后端API (http://localhost:8012)
| 端点 | 方法 | 描述 | 示例 |
|------|------|------|------|
| `/health` | GET | 健康检查 | `curl http://localhost:8012/health` |
| `/api/sessions` | POST | 创建新会话 | `POST /api/sessions` |
| `/api/sessions/{id}` | GET | 获取会话详情 | `GET /api/sessions/123` |
| `/api/users/{id}/sessions` | GET | 获取用户所有会话 | `GET /api/users/1/sessions` |
| `/api/crew` | POST | 发送消息给AI客服 | `POST /api/crew` |
| `/api/crew/{job_id}` | GET | 获取任务状态 | `GET /api/crew/job-123` |

#### RAGFlow API (http://localhost:9380)
| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/chats` | GET | 获取聊天列表 |
| `/api/v1/chats/{id}/sessions` | POST | 创建新会话 |
| `/api/v1/chats/{id}/messages` | POST | 发送消息 |

### 📊 服务依赖关系
```
前端应用 (3000)
    ↓ HTTP请求
后端API (8012)
    ↓ 数据库连接
AI Agent MySQL (3307)
    ↓ RAGFlow集成
RAGFlow服务器 (80/9380)
    ↓ 依赖服务
├── RAGFlow MySQL (5455)
├── RAGFlow Redis (6379)
├── Elasticsearch (1200)
└── MinIO (9000/9001)
```

## 🚀 快速开始

### 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- Git 2.0+
- 4GB+ 内存
- 2GB+ 可用磁盘空间

### 一键部署

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd AIAgent

# 2. 快速启动
./quick-start.sh

# 3. 访问应用
# 前端界面: http://localhost:3000
# 后端API: http://localhost:8012
# RAGFlow管理: http://localhost:80
```

> **注意**：首次运行时会自动创建环境变量文件，请根据提示配置必要的 API 密钥。

### 手动部署

```bash
# 1. 设置环境变量
cp crewaiBackend/env.template crewaiBackend/.env
# 编辑 crewaiBackend/.env 文件，填入必要的配置

# 2. 启动服务
docker-compose up -d

# 3. 访问应用
# 前端界面: http://localhost:3000
# 后端API: http://localhost:8012
# RAGFlow管理: http://localhost:80
```

> **注意**：手动部署需要先配置环境变量文件，建议使用一键部署脚本。

### 部署脚本说明

项目提供了便捷的部署脚本：

| 脚本 | 功能 | 说明 |
|------|------|------|
| `quick-start.sh` | 一键部署 | 同时启动RAGFlow和AI Agent所有服务，并自动构建最新镜像 |
| `stop-all.sh` | 停止所有服务 | 同时停止RAGFlow和AI Agent所有服务 |

**使用方法**：
```bash
# 一键部署所有服务
chmod +x quick-start.sh stop-all.sh
./quick-start.sh

# 停止所有服务
./stop-all.sh
```

> **💡 代码更新说明**: 
> - `quick-start.sh` 会自动使用 `--build` 参数重新构建镜像
> - 这确保每次运行都使用最新的代码
> - 如果只想重启服务而不重新构建，使用 `docker-compose restart`

## 🔍 服务状态检查

### 健康检查
```bash
# 检查后端服务
curl http://localhost:8012/health

# 检查RAGFlow服务
curl http://localhost:80

# 检查所有容器状态
docker-compose ps
```

### 服务日志
```bash
# 查看后端日志
docker-compose logs aiagent-backend

# 查看RAGFlow日志
docker-compose logs ragflow-server

# 查看所有服务日志
docker-compose logs
```

## 🛠️ 常用命令

### 开发环境
```bash
make dev              # 启动开发环境
make test             # 运行测试
make lint             # 代码检查
make health           # 健康检查
```

### 本地部署
```bash
make deploy           # 本地Docker部署
make monitor          # 查看服务状态
make status           # 查看服务状态
```

### 维护操作
```bash
make logs             # 查看日志
make restart          # 重启服务
make clean            # 清理资源
make update           # 更新代码
```

## 📊 项目结构

```
AIAgent/
├── crewaiBackend/          # 后端服务
│   ├── main.py            # 主应用入口
│   ├── crew.py            # CrewAI配置
│   ├── config.py          # 配置管理
│   ├── constants.py       # 常量定义
│   ├── utils/             # 工具模块
│   │   ├── database.py    # 数据库操作
│   │   ├── jobManager.py  # 任务管理
│   │   ├── logger.py      # 日志管理
│   │   ├── myLLM.py       # LLM配置
│   │   ├── ragflow_client.py # RAGFlow客户端
│   │   ├── sessionManager.py # 会话管理
│   │   └── session_agent_manager.py # 会话代理管理
│   ├── scripts/           # 后端脚本
│   │   ├── update_agent_prompt.py  # Agent Prompt更新脚本
│   │   └── PROMPT_CONFIG_GUIDE.md  # Prompt配置指南
│   ├── agent_config.yaml  # Agent Prompt配置文件
│   ├── backups/           # 自动备份目录
│   └── Dockerfile         # 后端Docker配置
├── crewaiFrontend/         # 前端服务
│   ├── src/               # React源码
│   ├── public/            # 静态资源
│   └── Dockerfile         # 前端Docker配置
├── tests/                  # 测试文件
│   ├── conftest.py        # 测试配置
│   ├── unit/              # 单元测试
│   └── database/          # 数据库测试
├── .github/workflows/      # CI/CD配置
│   └── ci.yml            # 主CI/CD流程
├── docker-compose.yml     # Docker Compose配置
├── quick-start.sh         # 一键启动脚本
├── Makefile              # 项目管理命令
└── README.md             # 项目说明
```

## 🔧 配置说明

### 环境变量配置

编辑 `crewaiBackend/.env` 文件：

```env
# Google AI API
GOOGLE_API_KEY=your_google_api_key_here

# RAGFlow 配置
RAGFLOW_BASE_URL=http://localhost:9380
RAGFLOW_API_KEY=your_ragflow_api_key_here
RAGFLOW_CHAT_ID=your_ragflow_chat_id_here

# MySQL 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3307  # 本地开发环境使用3307端口（Docker映射）
MYSQL_USER=root
MYSQL_PASSWORD=root123
MYSQL_DATABASE=aiagent_chat

# Flask 配置
FLASK_ENV=production
FLASK_DEBUG=False
PORT=8012
```

> **注意**：首次运行时会自动创建环境变量文件，请根据提示配置必要的 API 密钥。


## 🔄 CI/CD 流程

项目配置了完整的CI/CD流程，使用GitHub Actions进行自动化测试和部署：

**🔗 GitHub Actions状态**: [查看CI/CD流水线状态](https://github.com/mr6923612/AIAgent/actions)

### 📋 流水线阶段

1. **代码推送** → 触发GitHub Actions
2. **测试阶段** → 运行单元测试、集成测试、API测试
3. **构建阶段** → 构建Docker镜像
4. **安全检查** → 运行安全扫描
5. **代码检查** → 运行代码质量检查
6. **部署测试** → 测试本地Docker部署

### 🚀 自动化流程
   ```bash
# 本地开发
make dev

# 运行测试
make test

# 推送代码（自动触发CI/CD）
git add .
git commit -m "Add new feature"
git push origin main

# 本地部署
make deploy
```

## 🧪 测试框架

项目使用pytest作为测试框架，提供完整的测试覆盖：

### 测试类型
- **单元测试** - 测试各个模块的独立功能
- **数据库测试** - 测试MySQL数据库操作

### 运行测试
```bash
# 使用Makefile（推荐）
make test             # 运行所有基本功能测试
make test-coverage    # 运行测试并生成覆盖率报告

# 直接使用pytest
cd crewaiBackend
python -m pytest tests/ -v                    # 运行所有测试
python -m pytest tests/unit/ -v               # 运行单元测试
python -m pytest tests/database/ -v           # 运行数据库测试
python -m pytest tests/ --cov=. --cov-report=html   # 运行测试并生成覆盖率报告
```

### 测试配置
- **pytest.ini** - pytest配置文件
- **conftest.py** - 测试配置和夹具
- **测试数据** - 使用fixture提供测试数据

### 测试目录结构
```
tests/
├── conftest.py              # 测试配置和共享夹具
├── unit/                    # 单元测试 (44个测试)
│   ├── test_api_connectivity.py      # API连通性测试
│   ├── test_basic_functionality.py   # 基本功能测试
│   ├── test_config.py               # 配置模块测试
│   ├── test_frontend_backend_integration.py # 前后端集成测试
│   └── test_session_manager.py      # 会话管理器测试
└── database/                # 数据库测试 (7个测试)
    └── test_mysql_operations.py # MySQL数据库操作测试
```

### 测试覆盖范围

#### 单元测试 (44个)
- **API连通性测试** - 健康检查、会话状态、路由注册验证
- **基本功能测试** - 配置加载、数据库连接、会话管理、任务管理
- **配置模块测试** - 配置加载、默认值、环境变量加载
- **前后端集成测试** - 会话管理流程、聊天消息流程、AI响应流程
- **会话管理器测试** - 聊天消息、聊天会话、会话管理器

#### 数据库测试 (7个)
- **MySQL操作测试** - 数据库连接、会话CRUD、错误处理、事务回滚

### CI/CD集成
测试已集成到GitHub Actions中，每次代码推送都会自动运行：
- **测试阶段** - 运行所有测试用例 (50个测试)
- **构建阶段** - 构建Docker镜像
- **安全检查** - 运行安全扫描
- **代码检查** - 运行代码质量检查
- **覆盖率检查** - 代码覆盖率阈值30%



## 📁 数据文件夹结构

项目采用统一的数据文件夹结构，便于管理和维护：

```
data/
├── aiagent/              # AI Agent核心服务数据
│   └── mysql/           # AI Agent MySQL数据库文件
├── ragflow/             # RAGFlow服务数据
│   ├── app/             # RAGFlow应用数据
│   ├── elasticsearch/   # Elasticsearch索引数据
│   ├── minio/           # MinIO对象存储数据
│   ├── mysql/           # RAGFlow MySQL数据库文件
│   └── redis/           # Redis缓存数据
└── ollama/              # Ollama LLM模型数据
    ├── models/          # 下载的模型文件
    ├── id_ed25519       # SSH密钥
    └── id_ed25519.pub   # SSH公钥
```

### 数据管理优势

- **统一管理**: 所有数据文件集中存储
- **分类清晰**: 按服务类型组织数据
- **便于备份**: 统一的数据备份策略
- **权限控制**: 更好的数据安全保护
- **易于维护**: 简化的清理和维护流程

## 🛠️ 故障排除

### 端口冲突
如果遇到端口冲突，可以修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "3001:3000"  # 将前端端口改为3001
  - "8013:8012"  # 将后端端口改为8013
```

### 服务无法访问
1. 检查容器状态：`docker-compose ps`
2. 查看服务日志：`docker-compose logs [service-name]`
3. 检查端口占用：`netstat -an | grep :8012`
4. 重启服务：`docker-compose restart [service-name]`

### 数据库连接问题
1. 检查数据库容器：`docker-compose logs backend-mysql`
2. 测试数据库连接：`docker-compose exec backend-mysql mysql -u root -proot123`
3. 检查网络连接：`docker network ls`

### 常见问题解决

#### 1. 前端无法连接后端
```bash
# 检查后端是否运行
curl http://localhost:8012/health

# 检查前端API配置
# 确保 crewaiFrontend/src/utils/api.js 中的 API_BASE_URL 正确
```

#### 2. RAGFlow连接失败
```bash
# 检查RAGFlow服务
curl http://localhost:80

# 检查RAGFlow容器日志
docker-compose logs ragflow-server
```

#### 3. 数据库连接失败
```bash
# 检查MySQL容器
docker-compose logs backend-mysql

# 测试数据库连接
docker-compose exec backend-mysql mysql -u root -proot123 -e "SELECT 1;"
```

### 性能优化建议

1. **端口范围**: 确保端口3000-12000范围内没有其他服务占用
2. **防火墙**: 确保防火墙允许这些端口的访问
3. **资源要求**: 建议至少4GB内存和2GB可用磁盘空间
4. **网络隔离**: 所有服务都在 `aiagent-net` 网络中，确保容器间通信正常



## 🧹 清理RAGFlow会话

```bash
# 清理RAGFlow中的所有会话
python scripts/cleanup_ragflow_sessions.py
```

**注意**: 需要先设置环境变量 `RAGFLOW_API_KEY`

## 🤖 Ollama模型配置

### 自动模型下载
系统会自动下载以下必需的模型：
- **bge-m3** - 用于文本嵌入和向量化

### 验证模型安装
```bash
# 验证Ollama模型是否正确安装（本地开发环境）
python tests/unit/verify_ollama_models.py

# 验证Ollama服务连通性（CI/CD环境）
python tests/unit/test_ollama_connectivity.py
```

### 手动下载模型
```bash
# 查看已安装的模型（推荐）
docker exec ollama ollama list

# 下载bge-m3模型
docker exec ollama ollama pull bge-m3

# 删除不需要的模型
docker exec ollama ollama rm model-name
```

## 🔗 RAGFlow LLM配置

RAGFlow需要配置Ollama作为embedding模型提供者才能正常工作。

### 配置步骤

1. **访问RAGFlow管理界面**
   ```
   http://localhost:80
   ```

2. **首次登录**
   - 创建管理员账户
   - 使用邮箱和密码登录

3. **配置Ollama服务**
   - 进入 **设置 (Settings)** → **模型管理 (Model Management)**
   - 点击 **添加模型提供者 (Add Model Provider)**
   - 选择 **Ollama** 类型

4. **关键配置项**
   ```
   提供者名称: Ollama
   API地址: http://ollama:11434
   模型名称: bge-m3:latest
   用途: Embedding（向量化）
   ```

   > **⚠️ 重要**: 
   > - 必须使用 `http://ollama:11434` 而不是 `http://localhost:11434`
   > - 在Docker网络中，容器之间通过容器名称相互访问
   > - `localhost` 指向容器自己，而 `ollama` 是Ollama容器的hostname

5. **测试连接**
   - 点击 **测试连接 (Test Connection)** 按钮
   - 确保显示 "连接成功" 或 "Connection Successful"

6. **创建知识库**
   - 进入 **知识库 (Knowledge Base)** 页面
   - 创建新的知识库
   - 上传文档并选择刚配置的 `bge-m3` 模型进行向量化

### 验证配置

```bash
# 从RAGFlow容器内测试Ollama连接
docker exec ragflow-server curl http://ollama:11434

# 查看可用模型
docker exec ragflow-server curl http://ollama:11434/api/tags
```

### 常见问题

**问题**: "Connection refused" 或 "[Errno 111]"
- **原因**: 使用了 `localhost` 而不是 `ollama`
- **解决**: 在RAGFlow配置中将地址改为 `http://ollama:11434`

**问题**: "模型不存在"
- **原因**: Ollama中没有下载bge-m3模型
- **解决**: 运行 `docker exec ollama ollama pull bge-m3`

**问题**: RAGFlow无法访问Ollama
- **原因**: 网络配置问题
- **解决**: 确保使用 `quick-start.sh` 启动所有服务

## 🤖 自定义AI Agent Prompt

您可以轻松自定义AI客服代表的行为和回复风格，无需直接修改代码。

### 📂 相关文件

```
crewaiBackend/
├── agent_config.yaml          # ← 编辑这个文件来配置prompt
├── crew.py                    # Agent定义（自动更新）
├── scripts/
│   └── update_agent_prompt.py # ← 运行这个脚本来应用配置
└── backups/                   # 自动备份目录
    └── crew_backup_*.py       # 备份文件
```

### 🚀 快速配置

#### 1. 编辑配置文件

打开 `crewaiBackend/agent_config.yaml`，可以修改以下配置：

**Agent配置（定义客服的身份和性格）**

- **role** - 角色定义（简短描述）
```yaml
role: "智能客服代表"
```

- **goal** - 目标（这个agent要达成什么）
```yaml
goal: "为客户提供友好、专业的服务，像真人客服一样自然回复"
```

- **backstory** - 背景故事（定义agent的性格和行为方式）
```yaml
backstory: |
  你是一位经验丰富的客服代表，具备强大的语言识别和回复能力。
  你的特点：
  - 能够自动识别客户使用的语言（中文、英文、其他语言）
  - 使用相同的语言进行自然、亲切的回复
  ...
```

**Task配置（定义具体的服务要求和行为规范）**

- **description_template** - 任务描述模板（详细的服务要求和注意事项）
```yaml
description_template: |
  作为智能客服代表，请为客户提供专业、友好的服务。
  
  客户问题：{customer_input}
  知识库信息：{retrieved_summary}
  对话历史：{context_info}
  
  重要提醒：
  - 你的回答必须像真人客服一样自然
  - 不要提及"知识库"、"系统"等技术词汇
  ...
```

- **expected_output** - 期望输出（描述理想的回复效果）
```yaml
expected_output: "像真人客服一样的自然回复，使用客户相同的语言"
```

#### 2. 运行更新脚本

保存配置文件后，运行更新脚本：

```bash
# 从项目根目录
python crewaiBackend/scripts/update_agent_prompt.py
```

脚本会：
- ✅ 读取您的配置（Agent + Task）
- 💾 自动备份原始文件
- 📝 更新 `crew.py` 中的 Agent 和 Task 定义
- 🔍 验证更新是否成功
- 🔗 自动从RAGFlow获取chat_id并更新到`.env`文件

#### 3. 重启服务

更新完成后，重启后端服务以应用更改：

```bash
# Docker 环境
docker-compose restart aiagent-backend

# 或重新部署
./stop-all.sh
./quick-start.sh
```

> **💡 自动配置RAGFlow**: 脚本会自动从RAGFlow获取第一个可用的chat（对话助手）ID，并更新到`.env`文件中的`RAGFLOW_CHAT_ID`。这样可以确保Agent使用正确的知识库进行对话。如果您想使用特定的chat，可以在RAGFlow Web界面查看chat列表，然后手动修改`.env`文件中的`RAGFLOW_CHAT_ID`。

### 🔧 故障排除

**问题：脚本运行失败**
```bash
# 确保安装了 PyYAML
pip install pyyaml

# 检查文件路径是否正确
ls crewaiBackend/agent_config.yaml
ls crewaiBackend/crew.py
```

**问题：配置未生效**
```bash
# 1. 检查是否重启了服务
docker-compose restart aiagent-backend

# 2. 查看后端日志
docker logs aiagent-backend -f

# 3. 验证 crew.py 是否更新
cat crewaiBackend/crew.py | grep "customer_service_agent"
```

**问题：需要回滚**
```bash
# 查看备份文件
ls crewaiBackend/backups/

# 恢复备份（替换 TIMESTAMP 为实际时间戳）
cp crewaiBackend/backups/crew_backup_TIMESTAMP.py crewaiBackend/crew.py

# 重启服务
docker-compose restart aiagent-backend
```

### 🎯 最佳实践

1. **先备份**：脚本会自动备份，但重要更改前建议手动备份
2. **小步迭代**：每次只修改一小部分，观察效果
3. **测试验证**：更新后立即测试几个对话场景
4. **版本控制**：将 `agent_config.yaml` 加入Git，记录配置变更
5. **文档记录**：在配置文件中添加注释，说明修改原因

> 💡 **提示**: 好的prompt配置是一个迭代过程，根据实际使用反馈持续优化！

## 🆘 获取帮助

- 查看所有可用命令: `make help`
- 查看项目信息: `make info`
- 查看版本信息: `make version`
- 详细健康检查: `make health-detailed`
