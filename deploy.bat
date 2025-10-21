@echo off
REM AI Agent 快速部署脚本 (Windows)

echo 🚀 AI Agent 快速部署脚本
echo ==========================

REM 检查Docker是否安装
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker 未安装，请先安装 Docker Desktop
    pause
    exit /b 1
)

REM 检查Docker Compose是否安装
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose 未安装，请先安装 Docker Compose
    pause
    exit /b 1
)

echo ✅ Docker 环境检查通过

REM 检查RAGFlow是否已安装
if not exist "ragflow" (
    echo 📦 安装RAGFlow...
    git clone https://github.com/infiniflow/ragflow.git
    cd ragflow\docker
    echo 🚀 启动RAGFlow服务...
    docker compose -f docker-compose.yml up -d
    echo ⏳ 等待RAGFlow启动...
    timeout /t 30 /nobreak >nul
    echo 📋 查看RAGFlow启动日志...
    docker logs ragflow-server --tail 20
    cd ..\..
    echo ✅ RAGFlow安装完成
) else (
    echo ✅ RAGFlow已安装
    REM 检查RAGFlow是否运行
    docker ps | findstr ragflow >nul
    if %errorlevel% neq 0 (
        echo 🔄 启动RAGFlow服务...
        cd ragflow\docker
        docker compose -f docker-compose.yml up -d
        cd ..\..
    )
)

REM 检查环境变量文件
if not exist "crewaiBackend\.env" (
    echo 📝 创建环境变量文件...
    copy "crewaiBackend\env.template" "crewaiBackend\.env" >nul
    echo ⚠️  请编辑 crewaiBackend\.env 文件，填入您的API密钥
    echo    注意：RAGFlow的API密钥需要在RAGFlow界面中生成
    echo    然后重新运行此脚本
    pause
    exit /b 1
)

echo ✅ 环境变量文件已存在

REM 停止现有服务
echo 🛑 停止现有服务...
docker-compose down >nul 2>&1

REM 启动服务
echo 🚀 启动服务...
docker-compose up -d

REM 等待服务启动
echo ⏳ 等待服务启动...
timeout /t 10 /nobreak >nul

REM 检查服务状态
echo 🔍 检查服务状态...
docker-compose ps

REM 初始化数据库
echo 🗄️  初始化数据库...
docker-compose exec -T aiagent-backend python init_database.py

REM 检查服务健康状态
echo 🏥 检查服务健康状态...

REM 检查后端
docker-compose exec -T aiagent-backend python -c "import requests; print('Backend OK')" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 后端服务正常
) else (
    echo ❌ 后端服务异常
)

REM 检查前端
curl -f http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 前端服务正常
) else (
    echo ❌ 前端服务异常
)

REM 检查RAGFlow
curl -f http://localhost:9380 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ RAGFlow服务正常
) else (
    echo ❌ RAGFlow服务异常
)

echo.
echo 🎉 部署完成！
echo ==========================
echo 前端界面: http://localhost:3000
echo 后端API: http://localhost:5000
echo RAGFlow: http://localhost:9380
echo.
echo 📝 常用命令:
echo   查看日志: docker-compose logs -f
echo   停止服务: docker-compose down
echo   重启服务: docker-compose restart
echo ==========================
pause
