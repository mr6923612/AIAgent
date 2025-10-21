@echo off
REM RAGFlow 安装脚本 (Windows)

echo 🚀 RAGFlow 安装脚本
echo ==================

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
if exist "ragflow" (
    echo ⚠️  RAGFlow已存在，是否重新安装？
    set /p choice="输入 y 重新安装，其他键跳过: "
    if /i "%choice%"=="y" (
        echo 🗑️  删除现有RAGFlow...
        rmdir /s /q ragflow
    ) else (
        echo ✅ 跳过RAGFlow安装
        pause
        exit /b 0
    )
)

REM 克隆RAGFlow仓库
echo 📦 克隆RAGFlow仓库...
git clone https://github.com/infiniflow/ragflow.git

REM 进入RAGFlow目录
cd ragflow\docker

REM 启动RAGFlow服务
echo 🚀 启动RAGFlow服务...
docker compose -f docker-compose.yml up -d

REM 等待RAGFlow启动
echo ⏳ 等待RAGFlow启动（这可能需要几分钟）...
echo 📋 查看RAGFlow启动日志...

REM 显示启动日志
timeout /t 60 /nobreak >nul
docker logs ragflow-server --tail 20

REM 检查RAGFlow是否启动成功
echo 🔍 检查RAGFlow服务状态...
timeout /t 10 /nobreak >nul

docker ps | findstr ragflow-server >nul
if %errorlevel% equ 0 (
    echo ✅ RAGFlow服务已启动
) else (
    echo ❌ RAGFlow服务启动失败
    echo 📋 查看错误日志:
    docker logs ragflow-server --tail 20
    pause
    exit /b 1
)

REM 检查RAGFlow是否可访问
echo 🌐 检查RAGFlow Web界面...
for /l %%i in (1,1,30) do (
    curl -f http://localhost:9380 >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ RAGFlow Web界面可访问
        goto :success
    ) else (
        echo ⏳ 等待RAGFlow Web界面启动... (%%i/30)
        timeout /t 10 /nobreak >nul
    )
)

:success
REM 返回原目录
cd ..\..

echo.
echo 🎉 RAGFlow安装完成！
echo ==================
echo RAGFlow Web界面: http://localhost:9380
echo 默认管理员账号: admin
echo 默认密码: admin
echo.
echo 📝 下一步:
echo 1. 访问 http://localhost:9380
echo 2. 使用 admin/admin 登录
echo 3. 修改默认密码
echo 4. 在设置中生成API密钥
echo 5. 将API密钥填入 crewaiBackend\.env 文件
echo.
echo 💡 常用命令:
echo   查看RAGFlow日志: docker logs -f ragflow-server
echo   停止RAGFlow: cd ragflow\docker ^&^& docker compose down
echo   重启RAGFlow: cd ragflow\docker ^&^& docker compose restart
echo ==================
pause
