#!/bin/bash
# AI Agent 快速启动脚本
# 一键启动所有服务

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 AI Agent 快速启动脚本${NC}"
echo "================================"

# 检查环境变量文件
if [ ! -f "crewaiBackend/.env" ]; then
    echo -e "${YELLOW}⚠️  环境变量文件不存在，正在创建...${NC}"
    if [ -f "crewaiBackend/env.template" ]; then
        cp crewaiBackend/env.template crewaiBackend/.env
        echo -e "${GREEN}✅ 环境变量文件已创建${NC}"
        echo -e "${YELLOW}⚠️  请编辑 crewaiBackend/.env 文件，填入必要的配置${NC}"
        echo -e "${YELLOW}   特别是 GOOGLE_API_KEY 和 RAGFLOW_API_KEY${NC}"
        echo ""
        echo -e "${YELLOW}按任意键继续（确保已配置好环境变量）...${NC}"
        read -n 1 -s
    else
        echo -e "${RED}❌ env.template 文件不存在${NC}"
        exit 1
    fi
fi

# 创建必要的目录
echo -e "${BLUE}📁 创建必要的目录...${NC}"
mkdir -p data/aiagent/mysql
mkdir -p data/ragflow/mysql
mkdir -p data/ragflow/minio
mkdir -p data/ragflow/elasticsearch
mkdir -p data/ragflow/redis
mkdir -p data/ragflow/app
mkdir -p data/ollama
echo -e "${GREEN}✅ 目录创建完成${NC}"

# 停止现有服务
echo -e "${BLUE}🛑 停止现有服务...${NC}"
docker-compose down || true
echo -e "${GREEN}✅ 服务已停止${NC}"

# 构建并启动所有服务
echo -e "${BLUE}🔨 构建并启动所有服务...${NC}"
docker-compose up -d --build
echo -e "${GREEN}✅ 服务启动完成${NC}"

# 等待服务启动
echo -e "${BLUE}⏳ 等待服务启动...${NC}"
sleep 30

# 健康检查
echo -e "${BLUE}🔍 执行健康检查...${NC}"

# 检查服务状态
echo -e "${BLUE}检查服务状态...${NC}"
docker-compose ps

# 等待更长时间让服务完全启动
echo -e "${BLUE}⏳ 等待服务完全启动...${NC}"
sleep 30

# 检查各个服务
echo -e "${BLUE}检查各个服务...${NC}"

# 检查前端服务
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 前端服务正常${NC}"
else
    echo -e "${YELLOW}⚠️  前端服务可能还在启动中${NC}"
fi

# 检查后端服务
if curl -f http://localhost:8012/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 后端服务正常${NC}"
else
    echo -e "${YELLOW}⚠️  后端服务可能还在启动中${NC}"
fi

# 检查RAGFlow服务
if curl -f http://localhost:80 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ RAGFlow服务正常${NC}"
else
    echo -e "${YELLOW}⚠️  RAGFlow服务可能还在启动中${NC}"
fi

# 检查数据库服务
if docker-compose exec -T backend-mysql mysql -u root -proot123 -e "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ AI Agent数据库正常${NC}"
else
    echo -e "${YELLOW}⚠️  AI Agent数据库可能还在启动中${NC}"
fi

if docker-compose exec -T ragflow-mysql mysql -u root -proot -e "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ RAGFlow数据库正常${NC}"
else
    echo -e "${YELLOW}⚠️  RAGFlow数据库可能还在启动中${NC}"
fi

echo ""
echo -e "${GREEN}🎉 AI Agent 启动完成！${NC}"
echo ""
echo -e "${YELLOW}🌐 访问地址：${NC}"
echo -e "  前端界面: http://localhost:3000"
echo -e "  后端API: http://localhost:8012"
echo -e "  RAGFlow管理: http://localhost:80"
echo -e "  MinIO控制台: http://localhost:9001 (root/password)"
echo -e "  Elasticsearch: http://localhost:1200"
echo -e "  Ollama: http://localhost:11434"
echo ""
echo -e "${YELLOW}📚 常用命令：${NC}"
echo -e "  查看状态: docker-compose ps"
echo -e "  查看日志: docker-compose logs -f"
echo -e "  停止服务: docker-compose down"
echo -e "  重启服务: docker-compose restart"
echo ""
echo -e "${YELLOW}🔍 健康检查：${NC}"
echo -e "  后端健康检查: curl http://localhost:8012/health"
echo -e "  前端健康检查: curl http://localhost:3000/health"
echo ""
echo -e "${GREEN}✨ 开始使用 AI Agent 吧！${NC}"
