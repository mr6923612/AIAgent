# 🚀 AI Agent 部署指南

## 📋 目录
- [系统架构](#系统架构)
- [环境要求](#环境要求)
- [快速部署](#快速部署)
- [详细部署步骤](#详细部署步骤)
- [配置说明](#配置说明)
- [服务管理](#服务管理)
- [故障排除](#故障排除)
- [更新维护](#更新维护)

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

## 🔧 环境要求

### 系统要求
- **操作系统**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **内存**: 最少 8GB RAM (推荐 16GB+)
- **存储**: 最少 10GB 可用空间
- **网络**: 稳定的互联网连接

### 软件依赖
- **Docker**: 20.10+ 
- **Docker Compose**: 2.0+
- **Python**: 3.9+ (本地开发)
- **Node.js**: 16+ (前端开发)
- **Git**: 2.0+

## ⚡ 快速部署

### 1. 克隆项目
```bash
git clone <repository-url>
cd AIAgent
```

### 2. 安装RAGFlow
```bash
# 克隆RAGFlow仓库
git clone https://github.com/infiniflow/ragflow.git
cd ragflow/docker

# 启动RAGFlow服务
docker compose -f docker-compose.yml up -d

# 查看RAGFlow启动日志
docker logs -f ragflow-server

# 等待RAGFlow完全启动（通常需要2-3分钟）
# 当看到 "RAGFlow server started successfully" 时表示启动完成
```

### 3. 配置环境变量
```bash
# 回到AI Agent项目目录
cd ../../AIAgent

# 复制环境变量模板
cp crewaiBackend/env.template crewaiBackend/.env

# 编辑配置文件，填入您的API密钥
# 注意：RAGFlow的API密钥需要在RAGFlow界面中生成
```

### 4. 启动AI Agent服务
```bash
# 启动AI Agent服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 5. 访问应用
- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:5000
- **RAGFlow**: http://localhost:9380

## 📝 详细部署步骤

### 第一步：环境准备

#### 1.1 安装 Docker

**Windows:**
```bash
# 方法1: 下载 Docker Desktop for Windows
# 访问: https://www.docker.com/products/docker-desktop
# 下载并安装 Docker Desktop

# 方法2: 使用 Chocolatey
choco install docker-desktop

# 方法3: 使用 Winget
winget install Docker.DockerDesktop
```

**macOS:**
```bash
# 方法1: 使用 Homebrew
brew install --cask docker

# 方法2: 下载 Docker Desktop for Mac
# 访问: https://www.docker.com/products/docker-desktop
# 下载并安装 Docker Desktop

# 启动 Docker Desktop
open /Applications/Docker.app
```

**Ubuntu/Debian:**
```bash
# 更新包索引
sudo apt update

# 安装依赖
sudo apt install apt-transport-https ca-certificates curl gnupg lsb-release

# 添加Docker官方GPG密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加Docker仓库
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装Docker
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 将用户添加到docker组
sudo usermod -aG docker $USER

# 重新登录或运行以下命令使组权限生效
newgrp docker
```

**CentOS/RHEL:**
```bash
# 安装依赖
sudo yum install -y yum-utils

# 添加Docker仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装Docker
sudo yum install docker-ce docker-ce-cli containerd.io

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 将用户添加到docker组
sudo usermod -aG docker $USER
```

**验证Docker安装:**
```bash
# 检查Docker版本
docker --version

# 检查Docker服务状态
docker info

# 运行测试容器
docker run hello-world
```

#### 1.2 安装 Docker Compose
```bash
# 下载Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

#### 1.3 安装 RAGFlow
```bash
# 克隆RAGFlow仓库
git clone https://github.com/infiniflow/ragflow.git
cd ragflow/docker

# 启动RAGFlow服务
docker compose -f docker-compose.yml up -d

# 查看RAGFlow启动日志
docker logs -f ragflow-server

# 等待RAGFlow完全启动（通常需要2-3分钟）
# 当看到 "RAGFlow server started successfully" 时表示启动完成
```

**RAGFlow安装验证:**
```bash
# 检查RAGFlow容器状态
docker ps | grep ragflow

# 检查RAGFlow服务是否可访问
curl -f http://localhost:9380 || echo "RAGFlow正在启动中..."

# 访问RAGFlow Web界面
# 浏览器打开: http://localhost:9380
```

**RAGFlow配置说明:**
- **默认端口**: 9380
- **默认管理员账号**: admin
- **默认密码**: admin
- **首次登录**: 需要修改默认密码
- **API密钥**: 在RAGFlow界面中生成

### 第二步：项目配置

#### 2.1 克隆项目
```bash
git clone <repository-url>
cd AIAgent
```

#### 2.2 配置环境变量
```bash
# 进入后端目录
cd crewaiBackend

# 复制环境变量模板
cp env.template .env

# 编辑配置文件
nano .env  # 或使用您喜欢的编辑器
```

#### 2.3 填写API密钥
编辑 `crewaiBackend/.env` 文件，填入以下信息：

```env
# Google AI API
GOOGLE_API_KEY=your_google_api_key_here

# RAGFlow 配置
RAGFLOW_BASE_URL=http://ragflow:9380
RAGFLOW_API_KEY=your_ragflow_api_key_here
RAGFLOW_CHAT_ID=your_ragflow_chat_id_here

# MySQL 数据库配置
MYSQL_HOST=backend-mysql
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root123
MYSQL_DATABASE=backend_db

# Flask 配置
FLASK_ENV=production
FLASK_DEBUG=False
PORT=5000
```

### 第三步：启动服务

#### 3.1 启动所有服务
```bash
# 回到项目根目录
cd ..

# 启动所有服务
docker-compose up -d

# 查看启动日志
docker-compose logs -f
```

#### 3.2 验证服务状态
```bash
# 查看服务状态
docker-compose ps

# 检查服务健康状态
docker-compose exec aiagent-backend python -c "import requests; print('Backend OK')"
docker-compose exec aiagent-frontend curl -f http://localhost:3000 || echo "Frontend OK"
```

### 第四步：初始化数据库

#### 4.1 创建数据库表
```bash
# 进入后端容器
docker-compose exec aiagent-backend bash

# 初始化数据库
python init_database.py

# 退出容器
exit
```

#### 4.2 验证数据库
```bash
# 检查数据库连接
docker-compose exec aiagent-backend python -c "
from utils.database import db_manager
print('数据库连接成功:', db_manager.test_connection())
"
```

## ⚙️ 配置说明

### 环境变量配置

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `GOOGLE_API_KEY` | Google AI API密钥 | `AIzaSy...` |
| `RAGFLOW_BASE_URL` | RAGFlow服务地址 | `http://ragflow:9380` |
| `RAGFLOW_API_KEY` | RAGFlow API密钥 | `ragflow_api_key` |
| `RAGFLOW_CHAT_ID` | RAGFlow聊天ID | `chat_123` |
| `MYSQL_HOST` | MySQL主机地址 | `backend-mysql` |
| `MYSQL_PORT` | MySQL端口 | `3306` |
| `MYSQL_USER` | MySQL用户名 | `root` |
| `MYSQL_PASSWORD` | MySQL密码 | `root123` |
| `MYSQL_DATABASE` | 数据库名 | `backend_db` |
| `FLASK_ENV` | Flask环境 | `production` |
| `FLASK_DEBUG` | 调试模式 | `False` |
| `PORT` | 服务端口 | `5000` |

### 端口配置

| 服务 | 端口 | 说明 |
|------|------|------|
| 前端 | 3000 | React开发服务器 |
| 后端 | 5000 | Flask API服务 |
| RAGFlow | 9380 | RAGFlow Web界面 |
| MySQL | 3307 | 后端数据库 |
| Qdrant | 6333 | 向量数据库 |
| Ollama | 11434 | 本地LLM服务 |

## 🔧 服务管理

### 启动服务
```bash
# 启动所有服务
docker-compose up -d

# 启动特定服务
docker-compose up -d aiagent-backend
docker-compose up -d aiagent-frontend
```

### 停止服务
```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

### 重启服务
```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart aiagent-backend
```

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f aiagent-backend
docker-compose logs -f aiagent-frontend
```

### 进入容器
```bash
# 进入后端容器
docker-compose exec aiagent-backend bash

# 进入前端容器
docker-compose exec aiagent-frontend sh
```

## 🛠️ 故障排除

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

# 检查数据库连接
docker-compose exec aiagent-backend python -c "
from utils.database import db_manager
print('数据库连接测试:', db_manager.test_connection())
"

# 重启数据库服务
docker-compose restart backend-mysql
```

#### 3. API密钥错误
```bash
# 检查环境变量
docker-compose exec aiagent-backend env | grep API

# 重新加载配置
docker-compose down
docker-compose up -d
```

#### 4. 前端无法访问
```bash
# 检查前端服务状态
docker-compose ps aiagent-frontend

# 检查前端日志
docker-compose logs aiagent-frontend

# 重启前端服务
docker-compose restart aiagent-frontend
```

### 日志分析

#### 后端日志
```bash
# 查看实时日志
docker-compose logs -f aiagent-backend

# 查看错误日志
docker-compose logs aiagent-backend 2>&1 | grep ERROR

# 查看特定时间段的日志
docker-compose logs --since="2024-01-01T00:00:00" aiagent-backend
```

#### 前端日志
```bash
# 查看前端构建日志
docker-compose logs aiagent-frontend

# 查看前端运行时日志
docker-compose exec aiagent-frontend cat /app/logs/app.log
```

### 性能优化

#### 1. 内存优化
```bash
# 检查内存使用
docker stats

# 限制容器内存使用
# 在docker-compose.yml中添加：
# deploy:
#   resources:
#     limits:
#       memory: 2G
```

#### 2. 数据库优化
```bash
# 检查数据库性能
docker-compose exec backend-mysql mysql -u root -p -e "SHOW PROCESSLIST;"

# 优化MySQL配置
# 在docker-compose.yml中添加MySQL配置
```

## 🔄 更新维护

### 更新代码
```bash
# 拉取最新代码
git pull origin main

# 重新构建并启动
docker-compose down
docker-compose up -d --build
```

### 备份数据
```bash
# 备份数据库
docker-compose exec backend-mysql mysqldump -u root -p backend_db > backup.sql

# 备份配置文件
cp crewaiBackend/.env backup.env
```

### 清理资源
```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的容器
docker container prune

# 清理未使用的网络
docker network prune

# 清理未使用的数据卷
docker volume prune
```

### 监控服务
```bash
# 创建监控脚本
cat > monitor.sh << 'EOF'
#!/bin/bash
while true; do
    echo "=== $(date) ==="
    docker-compose ps
    echo "Memory usage:"
    docker stats --no-stream
    echo "=================="
    sleep 60
done
EOF

chmod +x monitor.sh
./monitor.sh
```

## 📞 技术支持

### 获取帮助
- **文档**: 查看项目README.md
- **问题报告**: 在GitHub Issues中提交
- **社区支持**: 加入项目讨论群

### 常用命令速查
```bash
# 快速启动
docker-compose up -d

# 快速停止
docker-compose down

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 清理资源
docker system prune -a
```

---

## 🎯 部署检查清单

- [ ] Docker和Docker Compose已安装
- [ ] 项目代码已克隆
- [ ] 环境变量已配置
- [ ] API密钥已填入
- [ ] 所有服务已启动
- [ ] 数据库已初始化
- [ ] 前端可正常访问
- [ ] 后端API可正常调用
- [ ] RAGFlow服务正常
- [ ] 测试功能正常

**🎉 恭喜！您的AI Agent已成功部署！**
