#!/bin/bash
# AI Agent Quick Start Script
# One-click startup for all services (including RAGFlow and AI Agent)

set -e  # Exit immediately on error

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}AI Agent + RAGFlow Quick Start Script${NC}"
echo "========================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running, please start Docker first${NC}"
    exit 1
fi
echo -e "${GREEN}Docker is running normally${NC}"

# Check and configure environment variable file
echo -e "${BLUE}Checking environment variable configuration...${NC}"
if [ ! -f "crewaiBackend/.env" ]; then
    echo -e "${YELLOW}Environment variable file does not exist, creating...${NC}"
    if [ -f "crewaiBackend/env.template" ]; then
        cp crewaiBackend/env.template crewaiBackend/.env
        echo -e "${GREEN}Environment variable file created${NC}"
    else
        echo -e "${RED}env.template file does not exist${NC}"
        exit 1
    fi
fi

# Update Docker environment configuration in .env file
echo -e "${BLUE}Updating Docker environment configuration...${NC}"
sed -i.bak 's|RAGFLOW_BASE_URL=http://localhost:80|RAGFLOW_BASE_URL=http://ragflow-server:80|g' crewaiBackend/.env
sed -i.bak 's|MYSQL_HOST=localhost|MYSQL_HOST=backend-mysql|g' crewaiBackend/.env
sed -i.bak 's|MYSQL_PORT=3307|MYSQL_PORT=3306|g' crewaiBackend/.env
echo -e "${GREEN}Docker environment configuration updated${NC}"

# Check API key configuration
if grep -q "your_google_api_key_here" crewaiBackend/.env || grep -q "your_ragflow_api_key_here" crewaiBackend/.env; then
    echo ""
    echo -e "${YELLOW}⚠️  Warning: Unconfigured API keys detected!${NC}"
    echo -e "${YELLOW}Please edit crewaiBackend/.env file and fill in the following configuration:${NC}"
    echo -e "${YELLOW}  - GOOGLE_API_KEY: Visit https://aistudio.google.com/app/apikey to get${NC}"
    echo -e "${YELLOW}  - RAGFLOW_API_KEY: Get from RAGFlow Web interface${NC}"
    echo ""
    echo -e "${YELLOW}Or run the configuration script after service startup:${NC}"
    echo -e "${YELLOW}  cd crewaiBackend && python scripts/update_agent_prompt.py --yes${NC}"
    echo ""
    echo -e "${YELLOW}Press any key to continue starting services...${NC}"
    read -n 1 -s
fi

# Create necessary directories
echo -e "${BLUE}Creating necessary directories...${NC}"
mkdir -p data/aiagent/mysql
mkdir -p data/ragflow/mysql
mkdir -p data/ragflow/minio
mkdir -p data/ragflow/elasticsearch
mkdir -p data/ragflow/redis
mkdir -p data/ollama
echo -e "${GREEN}Directories created${NC}"

# Stop existing services
echo -e "${BLUE}Stopping existing services...${NC}"
docker-compose down 2>/dev/null || true
docker-compose --profile aiagent down 2>/dev/null || true
cd ragflow/docker
docker-compose down 2>/dev/null || true
cd ../..
echo -e "${GREEN}Services stopped${NC}"

# Start RAGFlow service
echo -e "${BLUE}Starting RAGFlow service...${NC}"
cd ragflow/docker
docker-compose up -d
if [ $? -ne 0 ]; then
    echo -e "${RED}RAGFlow startup failed${NC}"
    exit 1
fi
cd ../..
echo -e "${GREEN}RAGFlow service started successfully${NC}"

# Start Ollama service
echo -e "${BLUE}Starting Ollama service...${NC}"
docker-compose up -d
if [ $? -ne 0 ]; then
    echo -e "${RED}Ollama service startup failed${NC}"
    exit 1
fi
echo -e "${GREEN}Ollama service started successfully${NC}"

# Start AI Agent frontend and backend services
echo -e "${BLUE}Starting AI Agent frontend and backend services...${NC}"
docker-compose --profile aiagent up -d --build
if [ $? -ne 0 ]; then
    echo -e "${RED}AI Agent frontend and backend services startup failed${NC}"
    exit 1
fi
echo -e "${GREEN}AI Agent frontend and backend services started successfully${NC}"

# Wait for services to start
echo -e "${BLUE}Waiting for services to start (approximately 60 seconds)...${NC}"
sleep 60

# Display service status
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  AI Agent Service Status${NC}"
echo -e "${BLUE}========================================${NC}"
docker-compose ps

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  RAGFlow Service Status${NC}"
echo -e "${BLUE}========================================${NC}"
cd ragflow/docker
docker-compose ps
cd ../..

# Health check
echo ""
echo -e "${BLUE}Performing health check...${NC}"

# Check AI Agent frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}AI Agent frontend service is normal${NC}"
else
    echo -e "${YELLOW}AI Agent frontend service may still be starting${NC}"
fi

# Check AI Agent backend
if curl -f http://localhost:8012/health > /dev/null 2>&1; then
    echo -e "${GREEN}AI Agent backend service is normal${NC}"
else
    echo -e "${YELLOW}AI Agent backend service may still be starting${NC}"
fi

# Check Ollama service
if curl -f http://localhost:11434 > /dev/null 2>&1; then
    echo -e "${GREEN}Ollama service is normal${NC}"
else
    echo -e "${YELLOW}Ollama service may still be starting${NC}"
fi

# Check RAGFlow service
if curl -f http://localhost:80 > /dev/null 2>&1; then
    echo -e "${GREEN}RAGFlow service is normal${NC}"
else
    echo -e "${YELLOW}RAGFlow service may still be starting${NC}"
fi

echo ""
echo -e "${GREEN}All services started successfully!${NC}"
echo ""
echo -e "${YELLOW}Access URLs:${NC}"
echo -e "  AI Agent Frontend: http://localhost:3000"
echo -e "  AI Agent Backend: http://localhost:8012"
echo -e "  RAGFlow Admin: http://localhost:80"
echo -e "  RAGFlow API: http://localhost:9380"
echo -e "  Ollama Service: http://localhost:11434"
echo -e "  MinIO Console: http://localhost:9001 (rag_flow/infini_rag_flow)"
echo -e "  Elasticsearch: http://localhost:1200"
echo ""
echo -e "${YELLOW}Common Commands:${NC}"
echo -e "  Check AI Agent status: docker-compose ps"
echo -e "  Check RAGFlow status: cd ragflow/docker && docker-compose ps"
echo -e "  View AI Agent logs: docker-compose logs -f"
echo -e "  View RAGFlow logs: cd ragflow/docker && docker-compose logs -f"
echo -e "  Stop all services: ./stop-all.sh"
echo ""
echo -e "${YELLOW}Data Storage Locations:${NC}"
echo -e "  AI Agent data: ./data/aiagent/"
echo -e "  RAGFlow data: ./data/ragflow/"
echo -e "  Ollama models: ./data/ollama/"
echo ""
echo -e "${GREEN}Start using AI Agent now!${NC}"
