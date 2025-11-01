#!/bin/bash
# Stop All Services Script

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Stopping All Services${NC}"
echo "========================================"

# Stop AI Agent and Ollama services
echo -e "${BLUE}Stopping AI Agent and Ollama services...${NC}"
docker-compose down
docker-compose --profile aiagent down
echo -e "${GREEN}AI Agent services stopped${NC}"

# Stop RAGFlow service
echo -e "${BLUE}Stopping RAGFlow service...${NC}"
cd ragflow/docker
docker-compose down
cd ../..
echo -e "${GREEN}RAGFlow service stopped${NC}"

echo ""
echo -e "${GREEN}All services stopped${NC}"
