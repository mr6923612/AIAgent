#!/bin/bash
# AI Agent 快速启动脚本
# 一键启动所有服务（包括RAGFlow和AI Agent）

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}AI Agent + RAGFlow 快速启动脚本${NC}"
echo "========================================"

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}错误: Docker未运行，请先启动Docker${NC}"
    exit 1
fi
echo -e "${GREEN}Docker运行正常${NC}"

# 检查环境变量文件
if [ ! -f "crewaiBackend/.env" ]; then
    echo -e "${YELLOW}环境变量文件不存在，正在创建...${NC}"
    if [ -f "crewaiBackend/env.template" ]; then
        cp crewaiBackend/env.template crewaiBackend/.env
        echo -e "${GREEN}环境变量文件已创建${NC}"
        echo -e "${YELLOW}请编辑 crewaiBackend/.env 文件，填入必要的配置${NC}"
        echo -e "${YELLOW}特别是 GOOGLE_API_KEY 和 RAGFLOW_API_KEY${NC}"
        echo ""
        echo -e "${YELLOW}按任意键继续（确保已配置好环境变量）...${NC}"
        read -n 1 -s
    else
        echo -e "${RED}env.template 文件不存在${NC}"
        exit 1
    fi
fi

# 创建必要的目录
echo -e "${BLUE}创建必要的目录...${NC}"
mkdir -p data/aiagent/mysql
mkdir -p data/ragflow/mysql
mkdir -p data/ragflow/minio
mkdir -p data/ragflow/elasticsearch
mkdir -p data/ragflow/redis
mkdir -p data/ollama
echo -e "${GREEN}目录创建完成${NC}"

# 停止现有服务
echo -e "${BLUE}停止现有服务...${NC}"
docker-compose down 2>/dev/null || true
docker-compose --profile aiagent down 2>/dev/null || true
cd ragflow/docker
docker-compose down 2>/dev/null || true
cd ../..
echo -e "${GREEN}服务已停止${NC}"

# 启动RAGFlow服务
echo -e "${BLUE}启动RAGFlow服务...${NC}"
cd ragflow/docker
docker-compose up -d
if [ $? -ne 0 ]; then
    echo -e "${RED}RAGFlow启动失败${NC}"
    exit 1
fi
cd ../..
echo -e "${GREEN}RAGFlow服务启动成功${NC}"

# 启动Ollama服务
echo -e "${BLUE}启动Ollama服务...${NC}"
docker-compose up -d
if [ $? -ne 0 ]; then
    echo -e "${RED}Ollama服务启动失败${NC}"
    exit 1
fi
echo -e "${GREEN}Ollama服务启动成功${NC}"

# 启动AI Agent前后端服务
echo -e "${BLUE}启动AI Agent前后端服务...${NC}"
docker-compose --profile aiagent up -d --build
if [ $? -ne 0 ]; then
    echo -e "${RED}AI Agent前后端服务启动失败${NC}"
    exit 1
fi
echo -e "${GREEN}AI Agent前后端服务启动成功${NC}"

# 等待服务启动
echo -e "${BLUE}等待服务启动（约60秒）...${NC}"
sleep 60

# 显示服务状态
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  AI Agent服务状态${NC}"
echo -e "${BLUE}========================================${NC}"
docker-compose ps

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  RAGFlow服务状态${NC}"
echo -e "${BLUE}========================================${NC}"
cd ragflow/docker
docker-compose ps
cd ../..

# 健康检查
echo ""
echo -e "${BLUE}执行健康检查...${NC}"

# 检查AI Agent前端
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}AI Agent前端服务正常${NC}"
else
    echo -e "${YELLOW}AI Agent前端服务可能还在启动中${NC}"
fi

# 检查AI Agent后端
if curl -f http://localhost:8012/health > /dev/null 2>&1; then
    echo -e "${GREEN}AI Agent后端服务正常${NC}"
else
    echo -e "${YELLOW}AI Agent后端服务可能还在启动中${NC}"
fi

# 检查Ollama服务
if curl -f http://localhost:11434 > /dev/null 2>&1; then
    echo -e "${GREEN}Ollama服务正常${NC}"
else
    echo -e "${YELLOW}Ollama服务可能还在启动中${NC}"
fi

# 检查RAGFlow服务
if curl -f http://localhost:80 > /dev/null 2>&1; then
    echo -e "${GREEN}RAGFlow服务正常${NC}"
else
    echo -e "${YELLOW}RAGFlow服务可能还在启动中${NC}"
fi

echo ""
echo -e "${GREEN}所有服务启动完成！${NC}"
echo ""
echo -e "${YELLOW}访问地址：${NC}"
echo -e "  AI Agent前端: http://localhost:3000"
echo -e "  AI Agent后端: http://localhost:8012"
echo -e "  RAGFlow管理: http://localhost:80"
echo -e "  RAGFlow API: http://localhost:9380"
echo -e "  Ollama服务: http://localhost:11434"
echo -e "  MinIO控制台: http://localhost:9001 (rag_flow/infini_rag_flow)"
echo -e "  Elasticsearch: http://localhost:1200"
echo ""
echo -e "${YELLOW}常用命令：${NC}"
echo -e "  查看AI Agent状态: docker-compose ps"
echo -e "  查看RAGFlow状态: cd ragflow/docker && docker-compose ps"
echo -e "  查看AI Agent日志: docker-compose logs -f"
echo -e "  查看RAGFlow日志: cd ragflow/docker && docker-compose logs -f"
echo -e "  停止所有服务: ./stop-all.sh"
echo ""
echo -e "${YELLOW}数据存储位置：${NC}"
echo -e "  AI Agent数据: ./data/aiagent/"
echo -e "  RAGFlow数据: ./data/ragflow/"
echo -e "  Ollama模型: ./data/ollama/"
echo ""
echo -e "${GREEN}开始使用 AI Agent 吧！${NC}"
