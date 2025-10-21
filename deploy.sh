#!/bin/bash
# AI Agent 快速部署脚本

set -e  # 遇到错误立即退出

echo "🚀 AI Agent 快速部署脚本"
echo "=========================="

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

echo "✅ Docker 环境检查通过"

# 检查RAGFlow是否已安装
if [ ! -d "ragflow" ]; then
    echo "📦 安装RAGFlow..."
    git clone https://github.com/infiniflow/ragflow.git
    cd ragflow/docker
    echo "🚀 启动RAGFlow服务..."
    docker compose -f docker-compose.yml up -d
    echo "⏳ 等待RAGFlow启动..."
    sleep 30
    echo "📋 查看RAGFlow启动日志..."
    docker logs ragflow-server --tail 20
    cd ../..
    echo "✅ RAGFlow安装完成"
else
    echo "✅ RAGFlow已安装"
    # 检查RAGFlow是否运行
    if ! docker ps | grep -q ragflow; then
        echo "🔄 启动RAGFlow服务..."
        cd ragflow/docker
        docker compose -f docker-compose.yml up -d
        cd ../..
    fi
fi

# 检查环境变量文件
if [ ! -f "crewaiBackend/.env" ]; then
    echo "📝 创建环境变量文件..."
    cp crewaiBackend/env.template crewaiBackend/.env
    echo "⚠️  请编辑 crewaiBackend/.env 文件，填入您的API密钥"
    echo "   注意：RAGFlow的API密钥需要在RAGFlow界面中生成"
    echo "   然后重新运行此脚本"
    exit 1
fi

echo "✅ 环境变量文件已存在"

# 停止现有服务
echo "🛑 停止现有服务..."
docker-compose down 2>/dev/null || true

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 初始化数据库
echo "🗄️  初始化数据库..."
docker-compose exec -T aiagent-backend python init_database.py

# 检查服务健康状态
echo "🏥 检查服务健康状态..."

# 检查后端
if docker-compose exec -T aiagent-backend python -c "import requests; print('Backend OK')" 2>/dev/null; then
    echo "✅ 后端服务正常"
else
    echo "❌ 后端服务异常"
fi

# 检查前端
if curl -f http://localhost:3000 >/dev/null 2>&1; then
    echo "✅ 前端服务正常"
else
    echo "❌ 前端服务异常"
fi

# 检查RAGFlow
if curl -f http://localhost:9380 >/dev/null 2>&1; then
    echo "✅ RAGFlow服务正常"
else
    echo "❌ RAGFlow服务异常"
fi

echo ""
echo "🎉 部署完成！"
echo "=========================="
echo "前端界面: http://localhost:3000"
echo "后端API: http://localhost:5000"
echo "RAGFlow: http://localhost:9380"
echo ""
echo "📝 常用命令:"
echo "  查看日志: docker-compose logs -f"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
echo "=========================="
