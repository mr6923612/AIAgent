# AI Agent 项目 Makefile
# 提供便捷的部署、测试和管理命令

.PHONY: help install test build deploy clean monitor status logs

# 默认目标
.DEFAULT_GOAL := help

# 颜色定义
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[1;33m
BLUE=\033[0;34m
PURPLE=\033[0;35m
NC=\033[0m

# 项目配置
PROJECT_NAME=aiagent
DOCKER_COMPOSE_FILE=docker-compose.yml
BACKEND_DIR=crewaiBackend
FRONTEND_DIR=crewaiFrontend

# 帮助信息
help: ## 显示帮助信息
	@echo "$(BLUE)AI Agent 项目管理命令$(NC)"
	@echo ""
	@echo "$(YELLOW)安装和设置:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*install|setup|init/ {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)开发和测试:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*test|dev|run/ {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)构建和部署:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*build|deploy|push/ {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)监控和维护:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## .*monitor|backup|clean|logs/ {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""

# 安装和设置
install: ## 安装项目依赖
	@echo "$(BLUE)安装项目依赖...$(NC)"
	@cd $(BACKEND_DIR) && pip install -r requirements.txt
	@cd $(FRONTEND_DIR) && npm install
	@echo "$(GREEN)依赖安装完成$(NC)"

install-dev: ## 安装开发依赖
	@echo "$(BLUE)安装开发依赖...$(NC)"
	@cd $(BACKEND_DIR) && pip install -r requirements.txt
	@cd $(BACKEND_DIR) && pip install pytest pytest-cov black flake8 isort mypy
	@cd $(FRONTEND_DIR) && npm install
	@echo "$(GREEN)开发依赖安装完成$(NC)"

setup-env: ## 设置环境变量
	@echo "$(BLUE)设置环境变量...$(NC)"
	@cd $(BACKEND_DIR) && cp env.template .env
	@echo "$(YELLOW)请编辑 $(BACKEND_DIR)/.env 文件，填入必要的配置$(NC)"

init-db: ## 初始化数据库
	@echo "$(BLUE)初始化数据库...$(NC)"
	@docker-compose exec aiagent-backend python init_database.py
	@echo "$(GREEN)数据库初始化完成$(NC)"

# 开发和测试
dev: ## 启动开发环境
	@echo "$(BLUE)启动开发环境...$(NC)"
	@docker-compose up -d
	@echo "$(GREEN)开发环境已启动$(NC)"
	@echo "$(YELLOW)前端: http://localhost:3000$(NC)"
	@echo "$(YELLOW)后端: http://localhost:8012$(NC)"

dev-backend: ## 仅启动后端开发服务
	@echo "$(BLUE)启动后端开发服务...$(NC)"
	@cd $(BACKEND_DIR) && python main.py

dev-frontend: ## 仅启动前端开发服务
	@echo "$(BLUE)启动前端开发服务...$(NC)"
	@cd $(FRONTEND_DIR) && npm run dev

test: ## 运行所有测试
	@echo "$(BLUE)运行测试...$(NC)"
	@cd $(BACKEND_DIR) && python -m pytest tests/ -v --tb=short
	@echo "$(GREEN)测试完成$(NC)"

test-unit: ## 运行单元测试
	@echo "$(BLUE)运行单元测试...$(NC)"
	@cd $(BACKEND_DIR) && python -m pytest tests/unit/ -v --tb=short
	@echo "$(GREEN)单元测试完成$(NC)"

test-integration: ## 运行集成测试
	@echo "$(BLUE)运行集成测试...$(NC)"
	@cd $(BACKEND_DIR) && python -m pytest tests/integration/ -v --tb=short
	@echo "$(GREEN)集成测试完成$(NC)"

test-api: ## 运行API测试
	@echo "$(BLUE)运行API测试...$(NC)"
	@cd $(BACKEND_DIR) && python -m pytest tests/api/ -v --tb=short
	@echo "$(GREEN)API测试完成$(NC)"

test-coverage: ## 运行测试并生成覆盖率报告
	@echo "$(BLUE)运行测试覆盖率分析...$(NC)"
	@cd $(BACKEND_DIR) && python -m pytest tests/ --cov=crewaiBackend --cov-report=html --cov-report=term
	@echo "$(GREEN)覆盖率报告已生成: $(BACKEND_DIR)/htmlcov/index.html$(NC)"

lint: ## 运行代码检查
	@echo "$(BLUE)运行代码检查...$(NC)"
	@cd $(BACKEND_DIR) && black --check . --line-length=120
	@cd $(BACKEND_DIR) && flake8 . --max-line-length=120 --ignore=E501,W503
	@cd $(BACKEND_DIR) && isort --check-only .
	@cd $(FRONTEND_DIR) && npm run lint
	@echo "$(GREEN)代码检查完成$(NC)"

lint-fix: ## 自动修复代码格式问题
	@echo "$(BLUE)自动修复代码格式...$(NC)"
	@cd $(BACKEND_DIR) && black . --line-length=120
	@cd $(BACKEND_DIR) && isort .
	@cd $(FRONTEND_DIR) && npm run lint -- --fix
	@echo "$(GREEN)代码格式修复完成$(NC)"

# 构建和部署
build: ## 构建Docker镜像
	@echo "$(BLUE)构建Docker镜像...$(NC)"
	@docker-compose build
	@echo "$(GREEN)Docker镜像构建完成$(NC)"

build-no-cache: ## 强制重建Docker镜像（不使用缓存）
	@echo "$(BLUE)强制重建Docker镜像...$(NC)"
	@docker-compose build --no-cache
	@echo "$(GREEN)Docker镜像重建完成$(NC)"

deploy: ## 本地Docker部署
	@echo "$(BLUE)本地Docker部署...$(NC)"
	@docker-compose down
	@docker-compose build
	@docker-compose up -d
	@echo "$(GREEN)本地Docker部署完成$(NC)"
	@echo "$(YELLOW)前端: http://localhost:3000$(NC)"
	@echo "$(YELLOW)后端: http://localhost:8012$(NC)"

# 监控和维护
start: ## 启动所有服务
	@echo "$(BLUE)启动所有服务...$(NC)"
	@docker-compose up -d
	@echo "$(GREEN)所有服务已启动$(NC)"

stop: ## 停止所有服务
	@echo "$(BLUE)停止所有服务...$(NC)"
	@docker-compose down
	@echo "$(GREEN)所有服务已停止$(NC)"

restart: ## 重启所有服务
	@echo "$(BLUE)重启所有服务...$(NC)"
	@docker-compose restart
	@echo "$(GREEN)所有服务已重启$(NC)"

status: ## 查看服务状态
	@echo "$(BLUE)服务状态:$(NC)"
	@docker-compose ps
	@echo ""
	@echo "$(BLUE)容器资源使用:$(NC)"
	@docker stats --no-stream

logs: ## 查看所有服务日志
	@echo "$(BLUE)查看服务日志...$(NC)"
	@docker-compose logs -f

logs-backend: ## 查看后端日志
	@echo "$(BLUE)查看后端日志...$(NC)"
	@docker-compose logs -f aiagent-backend

logs-frontend: ## 查看前端日志
	@echo "$(BLUE)查看前端日志...$(NC)"
	@docker-compose logs -f aiagent-frontend

logs-mysql: ## 查看MySQL日志
	@echo "$(BLUE)查看MySQL日志...$(NC)"
	@docker-compose logs -f backend-mysql

# 简化的监控命令
monitor: ## 查看服务状态和日志
	@echo "$(BLUE)查看服务状态...$(NC)"
	@docker-compose ps
	@echo "$(BLUE)查看最近日志...$(NC)"
	@docker-compose logs --tail=20

# 清理和维护
clean: ## 清理Docker资源
	@echo "$(BLUE)清理Docker资源...$(NC)"
	@docker-compose down -v
	@docker system prune -f
	@echo "$(GREEN)清理完成$(NC)"

clean-all: ## 清理所有Docker资源（包括镜像）
	@echo "$(BLUE)清理所有Docker资源...$(NC)"
	@docker-compose down -v
	@docker system prune -a -f
	@echo "$(GREEN)完全清理完成$(NC)"

clean-logs: ## 清理日志文件
	@echo "$(BLUE)清理日志文件...$(NC)"
	@find . -name "*.log" -type f -delete
	@docker-compose logs --tail=0 -f > /dev/null 2>&1 || true
	@echo "$(GREEN)日志清理完成$(NC)"

# 数据库操作
db-shell: ## 进入数据库Shell
	@echo "$(BLUE)进入数据库Shell...$(NC)"
	@docker-compose exec backend-mysql mysql -u root -proot123 aiagent_chat

# 健康检查
health: ## 检查服务健康状态
	@echo "$(BLUE)检查服务健康状态...$(NC)"
	@curl -f http://localhost:3000 > /dev/null 2>&1 && echo "$(GREEN)✅ 前端服务正常$(NC)" || echo "$(RED)❌ 前端服务异常$(NC)"
	@curl -f http://localhost:8012/health > /dev/null 2>&1 && echo "$(GREEN)✅ 后端服务正常$(NC)" || echo "$(RED)❌ 后端服务异常$(NC)"
	@curl -f http://localhost:80 > /dev/null 2>&1 && echo "$(GREEN)✅ RAGFlow服务正常$(NC)" || echo "$(RED)❌ RAGFlow服务异常$(NC)"
	@docker-compose exec -T backend-mysql mysql -u root -proot123 -e "SELECT 1;" > /dev/null 2>&1 && echo "$(GREEN)✅ AI Agent数据库正常$(NC)" || echo "$(RED)❌ AI Agent数据库异常$(NC)"
	@docker-compose exec -T ragflow-mysql mysql -u root -proot -e "SELECT 1;" > /dev/null 2>&1 && echo "$(GREEN)✅ RAGFlow数据库正常$(NC)" || echo "$(RED)❌ RAGFlow数据库异常$(NC)"

health-detailed: ## 详细健康检查
	@echo "$(BLUE)详细健康检查...$(NC)"
	@echo "$(YELLOW)=== 容器状态 ===$(NC)"
	@docker-compose ps
	@echo ""
	@echo "$(YELLOW)=== 服务响应 ===$(NC)"
	@echo -n "前端服务 (3000): "
	@curl -f http://localhost:3000 > /dev/null 2>&1 && echo "$(GREEN)正常$(NC)" || echo "$(RED)异常$(NC)"
	@echo -n "后端API (8012): "
	@curl -f http://localhost:8012/health > /dev/null 2>&1 && echo "$(GREEN)正常$(NC)" || echo "$(RED)异常$(NC)"
	@echo -n "RAGFlow Web (80): "
	@curl -f http://localhost:80 > /dev/null 2>&1 && echo "$(GREEN)正常$(NC)" || echo "$(RED)异常$(NC)"
	@echo -n "RAGFlow API (9380): "
	@curl -f http://localhost:9380 > /dev/null 2>&1 && echo "$(GREEN)正常$(NC)" || echo "$(RED)异常$(NC)"
	@echo -n "MinIO控制台 (9001): "
	@curl -f http://localhost:9001 > /dev/null 2>&1 && echo "$(GREEN)正常$(NC)" || echo "$(RED)异常$(NC)"
	@echo -n "Elasticsearch (1200): "
	@curl -f http://localhost:1200 > /dev/null 2>&1 && echo "$(GREEN)正常$(NC)" || echo "$(RED)异常$(NC)"

# 更新代码
update: ## 更新项目代码
	@echo "$(BLUE)更新项目代码...$(NC)"
	@git pull origin main
	@echo "$(GREEN)代码更新完成$(NC)"

# 版本管理
version: ## 显示版本信息
	@echo "$(BLUE)版本信息:$(NC)"
	@echo "项目: $(PROJECT_NAME)"
	@echo "Git版本: $(shell git describe --tags --always --dirty)"
	@echo "Docker Compose版本: $(shell docker-compose --version)"
	@echo "Python版本: $(shell python --version)"
	@echo "Node.js版本: $(shell node --version)"

# 快速命令组合
quick-start: setup-env install dev ## 快速启动（设置环境+安装依赖+启动服务）
	@echo "$(GREEN)快速启动完成！$(NC)"

quick-test: test lint health ## 快速测试（运行测试+代码检查+健康检查）
	@echo "$(GREEN)快速测试完成！$(NC)"

quick-deploy: test build deploy ## 快速部署（测试+构建+本地Docker部署）
	@echo "$(GREEN)快速部署完成！$(NC)"

# 显示项目信息
info: ## 显示项目信息
	@echo "$(PURPLE)=== AI Agent 项目信息 ===$(NC)"
	@echo "项目名称: $(PROJECT_NAME)"
	@echo "后端目录: $(BACKEND_DIR)"
	@echo "前端目录: $(FRONTEND_DIR)"
	@echo "Docker Compose文件: $(DOCKER_COMPOSE_FILE)"
	@echo ""
	@echo "$(YELLOW)服务端口:$(NC)"
	@echo "  前端应用: http://localhost:3000"
	@echo "  后端API: http://localhost:8012"
	@echo "  RAGFlow Web: http://localhost:80"
	@echo "  RAGFlow API: http://localhost:9380"
	@echo "  MinIO控制台: http://localhost:9001"
	@echo "  Elasticsearch: http://localhost:1200"
	@echo "  AI Agent MySQL: localhost:3307"
	@echo "  RAGFlow MySQL: localhost:5455"
	@echo ""
	@echo "$(YELLOW)常用命令:$(NC)"
	@echo "  make dev          - 启动开发环境"
	@echo "  make test         - 运行测试"
	@echo "  make deploy       - 本地Docker部署"
	@echo "  make monitor      - 查看服务状态"
	@echo "  make health       - 健康检查"
	@echo "  make help         - 显示所有命令"