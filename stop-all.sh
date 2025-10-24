#!/bin/bash
# 停止所有服务脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}停止所有服务${NC}"
echo "========================================"

# 停止AI Agent和Ollama服务
echo -e "${BLUE}停止AI Agent和Ollama服务...${NC}"
docker-compose down
docker-compose --profile aiagent down
echo -e "${GREEN}AI Agent服务已停止${NC}"

# 停止RAGFlow服务
echo -e "${BLUE}停止RAGFlow服务...${NC}"
cd ragflow/docker
docker-compose down
cd ../..
echo -e "${GREEN}RAGFlow服务已停止${NC}"

echo ""
echo -e "${GREEN}所有服务已停止${NC}"
