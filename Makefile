# AI Agent Project Makefile
# Provides convenient deployment, testing, and management commands

.PHONY: help install test build deploy clean monitor status logs

# Default target
.DEFAULT_GOAL := help

# Color definitions
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
BLUE=\033[0;34m
PURPLE=\033[0;35m
NC=\033[0m

# Project configuration
PROJECT_NAME=aiagent
DOCKER_COMPOSE_FILE=docker-compose.yml
BACKEND_DIR=crewaiBackend
FRONTEND_DIR=crewaiFrontend

# Help information
help: ## Display help information
	@echo "$(BLUE)AI Agent Project Management Commands$(NC)"
	@echo ""
	@echo "$(YELLOW)Installation and Setup:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*install|setup|init/ {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Development and Testing:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*test|dev|run/ {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Build and Deploy:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*build|deploy|push/ {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Monitoring and Maintenance:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*monitor|backup|clean|logs/ {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""

# Installation and Setup
install: ## Install project dependencies
	@echo "$(BLUE)Installing project dependencies...$(NC)"
	@cd $(BACKEND_DIR) && pip install -r requirements.txt
	@cd $(FRONTEND_DIR) && npm install
	@echo "$(GREEN)Dependencies installed$(NC)"

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	@cd $(BACKEND_DIR) && pip install -r requirements.txt
	@cd $(BACKEND_DIR) && pip install pytest pytest-cov black flake8 isort mypy
	@cd $(FRONTEND_DIR) && npm install
	@echo "$(GREEN)Development dependencies installed$(NC)"

setup-env: ## Set up environment variables
	@echo "$(BLUE)Setting up environment variables...$(NC)"
	@cd $(BACKEND_DIR) && cp env.template .env
	@echo "$(YELLOW)Please edit $(BACKEND_DIR)/.env file and fill in necessary configuration$(NC)"

init-db: ## Initialize database
	@echo "$(BLUE)Initializing database...$(NC)"
	@docker-compose exec aiagent-backend python init_database.py
	@echo "$(GREEN)Database initialized$(NC)"

# Development and Testing
dev: ## Start development environment
	@echo "$(BLUE)Starting development environment...$(NC)"
	@docker-compose up -d
	@echo "$(GREEN)Development environment started$(NC)"
	@echo "$(YELLOW)Frontend: http://localhost:3000$(NC)"
	@echo "$(YELLOW)Backend: http://localhost:8012$(NC)"

dev-backend: ## Start backend development service only
	@echo "$(BLUE)Starting backend development service...$(NC)"
	@cd $(BACKEND_DIR) && python main.py

dev-frontend: ## Start frontend development service only
	@echo "$(BLUE)Starting frontend development service...$(NC)"
	@cd $(FRONTEND_DIR) && npm run dev

test: ## Run all tests
	@echo "$(BLUE)Running tests...$(NC)"
	@cd $(BACKEND_DIR) && python -m pytest tests/ -v --tb=short
	@echo "$(GREEN)Tests completed$(NC)"

test-unit: ## Run unit tests
	@echo "$(BLUE)Running unit tests...$(NC)"
	@cd $(BACKEND_DIR) && python -m pytest tests/unit/ -v --tb=short
	@echo "$(GREEN)Unit tests completed$(NC)"

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	@cd $(BACKEND_DIR) && python -m pytest tests/integration/ -v --tb=short
	@echo "$(GREEN)Integration tests completed$(NC)"

test-api: ## Run API tests
	@echo "$(BLUE)Running API tests...$(NC)"
	@cd $(BACKEND_DIR) && python -m pytest tests/api/ -v --tb=short
	@echo "$(GREEN)API tests completed$(NC)"

test-coverage: ## Run tests and generate coverage report
	@echo "$(BLUE)Running test coverage analysis...$(NC)"
	@cd $(BACKEND_DIR) && python -m pytest tests/ --cov=crewaiBackend --cov-report=html --cov-report=term
	@echo "$(GREEN)Coverage report generated: $(BACKEND_DIR)/htmlcov/index.html$(NC)"

lint: ## Run code check
	@echo "$(BLUE)Running code check...$(NC)"
	@cd $(BACKEND_DIR) && black --check . --line-length=120
	@cd $(BACKEND_DIR) && flake8 . --max-line-length=120 --ignore=E501,W503
	@cd $(BACKEND_DIR) && isort --check-only .
	@cd $(FRONTEND_DIR) && npm run lint
	@echo "$(GREEN)Code check completed$(NC)"

lint-fix: ## Automatically fix code formatting issues
	@echo "$(BLUE)Automatically fixing code formatting...$(NC)"
	@cd $(BACKEND_DIR) && black . --line-length=120
	@cd $(BACKEND_DIR) && isort .
	@cd $(FRONTEND_DIR) && npm run lint -- --fix
	@echo "$(GREEN)Code formatting fixed$(NC)"

# Build and Deploy
build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	@docker-compose build
	@echo "$(GREEN)Docker images built$(NC)"

build-no-cache: ## Force rebuild Docker images (without cache)
	@echo "$(BLUE)Force rebuilding Docker images...$(NC)"
	@docker-compose build --no-cache
	@echo "$(GREEN)Docker images rebuilt$(NC)"

deploy: ## Local Docker deployment
	@echo "$(BLUE)Local Docker deployment...$(NC)"
	@docker-compose down
	@docker-compose build
	@docker-compose up -d
	@echo "$(GREEN)Local Docker deployment completed$(NC)"
	@echo "$(YELLOW)Frontend: http://localhost:3000$(NC)"
	@echo "$(YELLOW)Backend: http://localhost:8012$(NC)"

# Monitoring and Maintenance
start: ## Start all services
	@echo "$(BLUE)Starting all services...$(NC)"
	@docker-compose up -d
	@echo "$(GREEN)All services started$(NC)"

stop: ## Stop all services
	@echo "$(BLUE)Stopping all services...$(NC)"
	@docker-compose down
	@echo "$(GREEN)All services stopped$(NC)"

restart: ## Restart all services
	@echo "$(BLUE)Restarting all services...$(NC)"
	@docker-compose restart
	@echo "$(GREEN)All services restarted$(NC)"

status: ## View service status
	@echo "$(BLUE)Service status:$(NC)"
	@docker-compose ps
	@echo ""
	@echo "$(BLUE)Container resource usage:$(NC)"
	@docker stats --no-stream

logs: ## View all service logs
	@echo "$(BLUE)Viewing service logs...$(NC)"
	@docker-compose logs -f

logs-backend: ## View backend logs
	@echo "$(BLUE)Viewing backend logs...$(NC)"
	@docker-compose logs -f aiagent-backend

logs-frontend: ## View frontend logs
	@echo "$(BLUE)Viewing frontend logs...$(NC)"
	@docker-compose logs -f aiagent-frontend

logs-mysql: ## View MySQL logs
	@echo "$(BLUE)Viewing MySQL logs...$(NC)"
	@docker-compose logs -f backend-mysql

# Simplified monitoring commands
monitor: ## View service status and logs
	@echo "$(BLUE)Viewing service status...$(NC)"
	@docker-compose ps
	@echo "$(BLUE)Viewing recent logs...$(NC)"
	@docker-compose logs --tail=20

# Cleanup and Maintenance
clean: ## Clean Docker resources
	@echo "$(BLUE)Cleaning Docker resources...$(NC)"
	@docker-compose down -v
	@docker system prune -f
	@echo "$(GREEN)Cleanup completed$(NC)"

clean-all: ## Clean all Docker resources (including images)
	@echo "$(BLUE)Cleaning all Docker resources...$(NC)"
	@docker-compose down -v
	@docker system prune -a -f
	@echo "$(GREEN)Full cleanup completed$(NC)"

clean-logs: ## Clean log files
	@echo "$(BLUE)Cleaning log files...$(NC)"
	@find . -name "*.log" -type f -delete
	@docker-compose logs --tail=0 -f > /dev/null 2>&1 || true
	@echo "$(GREEN)Log cleanup completed$(NC)"

# Database operations
db-shell: ## Enter database Shell
	@echo "$(BLUE)Entering database Shell...$(NC)"
	@docker-compose exec backend-mysql mysql -u root -proot123 aiagent_chat

# Health check
health: ## Check service health status
	@echo "$(BLUE)Checking service health status...$(NC)"
	@curl -f http://localhost:3000 > /dev/null 2>&1 && echo "$(GREEN)✅ Frontend service normal$(NC)" || echo "$(RED)❌ Frontend service abnormal$(NC)"
	@curl -f http://localhost:8012/health > /dev/null 2>&1 && echo "$(GREEN)✅ Backend service normal$(NC)" || echo "$(RED)❌ Backend service abnormal$(NC)"
	@curl -f http://localhost:80 > /dev/null 2>&1 && echo "$(GREEN)✅ RAGFlow service normal$(NC)" || echo "$(RED)❌ RAGFlow service abnormal$(NC)"
	@docker-compose exec -T backend-mysql mysql -u root -proot123 -e "SELECT 1;" > /dev/null 2>&1 && echo "$(GREEN)✅ AI Agent database normal$(NC)" || echo "$(RED)❌ AI Agent database abnormal$(NC)"
	@docker-compose exec -T ragflow-mysql mysql -u root -proot -e "SELECT 1;" > /dev/null 2>&1 && echo "$(GREEN)✅ RAGFlow database normal$(NC)" || echo "$(RED)❌ RAGFlow database abnormal$(NC)"

health-detailed: ## Detailed health check
	@echo "$(BLUE)Detailed health check...$(NC)"
	@echo "$(YELLOW)=== Container Status ===$(NC)"
	@docker-compose ps
	@echo ""
	@echo "$(YELLOW)=== Service Response ===$(NC)"
	@echo -n "Frontend service (3000): "
	@curl -f http://localhost:3000 > /dev/null 2>&1 && echo "$(GREEN)Normal$(NC)" || echo "$(RED)Abnormal$(NC)"
	@echo -n "Backend API (8012): "
	@curl -f http://localhost:8012/health > /dev/null 2>&1 && echo "$(GREEN)Normal$(NC)" || echo "$(RED)Abnormal$(NC)"
	@echo -n "RAGFlow Web (80): "
	@curl -f http://localhost:80 > /dev/null 2>&1 && echo "$(GREEN)Normal$(NC)" || echo "$(RED)Abnormal$(NC)"
	@echo -n "RAGFlow API (9380): "
	@curl -f http://localhost:9380 > /dev/null 2>&1 && echo "$(GREEN)Normal$(NC)" || echo "$(RED)Abnormal$(NC)"
	@echo -n "MinIO Console (9001): "
	@curl -f http://localhost:9001 > /dev/null 2>&1 && echo "$(GREEN)Normal$(NC)" || echo "$(RED)Abnormal$(NC)"
	@echo -n "Elasticsearch (1200): "
	@curl -f http://localhost:1200 > /dev/null 2>&1 && echo "$(GREEN)Normal$(NC)" || echo "$(RED)Abnormal$(NC)"

# Update code
update: ## Update project code
	@echo "$(BLUE)Updating project code...$(NC)"
	@git pull origin main
	@echo "$(GREEN)Code update completed$(NC)"

# Version management
version: ## Display version information
	@echo "$(BLUE)Version information:$(NC)"
	@echo "Project: $(PROJECT_NAME)"
	@echo "Git version: $(shell git describe --tags --always --dirty)"
	@echo "Docker Compose version: $(shell docker-compose --version)"
	@echo "Python version: $(shell python --version)"
	@echo "Node.js version: $(shell node --version)"

# Quick command combinations
quick-start: setup-env install dev ## Quick start (setup environment + install dependencies + start services)
	@echo "$(GREEN)Quick start completed!$(NC)"

quick-test: test lint health ## Quick test (run tests + code check + health check)
	@echo "$(GREEN)Quick test completed!$(NC)"

quick-deploy: test build deploy ## Quick deploy (test + build + local Docker deployment)
	@echo "$(GREEN)Quick deploy completed!$(NC)"

# Display project information
info: ## Display project information
	@echo "$(PURPLE)=== AI Agent Project Information ===$(NC)"
	@echo "Project name: $(PROJECT_NAME)"
	@echo "Backend directory: $(BACKEND_DIR)"
	@echo "Frontend directory: $(FRONTEND_DIR)"
	@echo "Docker Compose file: $(DOCKER_COMPOSE_FILE)"
	@echo ""
	@echo "$(YELLOW)Service Ports:$(NC)"
	@echo "  Frontend app: http://localhost:3000"
	@echo "  Backend API: http://localhost:8012"
	@echo "  RAGFlow Web: http://localhost:80"
	@echo "  RAGFlow API: http://localhost:9380"
	@echo "  MinIO Console: http://localhost:9001"
	@echo "  Elasticsearch: http://localhost:1200"
	@echo "  AI Agent MySQL: localhost:3307"
	@echo "  RAGFlow MySQL: localhost:5455"
	@echo ""
	@echo "$(YELLOW)Common Commands:$(NC)"
	@echo "  make dev          - Start development environment"
	@echo "  make test         - Run tests"
	@echo "  make deploy       - Local Docker deployment"
	@echo "  make monitor      - View service status"
	@echo "  make health       - Health check"
	@echo "  make help         - Display all commands"
