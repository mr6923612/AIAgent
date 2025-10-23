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
| `quick-start.sh` | 快速启动 | 一键启动所有服务，自动创建环境变量文件 |

**使用方法**：
```bash
# 克隆项目并快速启动
git clone <your-repo-url>
cd AIAgent
./quick-start.sh
```

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
python cleanup_ragflow_sessions.py
```

**注意**: 需要先设置环境变量 `RAGFLOW_API_KEY`

## 🆘 获取帮助

- 查看所有可用命令: `make help`
- 查看项目信息: `make info`
- 查看版本信息: `make version`
- 详细健康检查: `make health-detailed`
