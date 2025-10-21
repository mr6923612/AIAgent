#!/bin/bash
# RAGFlow 安装脚本

set -e  # 遇到错误立即退出

echo "🚀 RAGFlow 安装脚本"
echo "=================="

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
if [ -d "ragflow" ]; then
    echo "⚠️  RAGFlow已存在，是否重新安装？"
    read -p "输入 y 重新安装，其他键跳过: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  删除现有RAGFlow..."
        rm -rf ragflow
    else
        echo "✅ 跳过RAGFlow安装"
        exit 0
    fi
fi

# 克隆RAGFlow仓库
echo "📦 克隆RAGFlow仓库..."
git clone https://github.com/infiniflow/ragflow.git

# 进入RAGFlow目录
cd ragflow/docker

# 启动RAGFlow服务
echo "🚀 启动RAGFlow服务..."
docker compose -f docker-compose.yml up -d

# 等待RAGFlow启动
echo "⏳ 等待RAGFlow启动（这可能需要几分钟）..."
echo "📋 查看RAGFlow启动日志..."

# 显示启动日志
timeout 60 docker logs -f ragflow-server 2>/dev/null || true

# 检查RAGFlow是否启动成功
echo "🔍 检查RAGFlow服务状态..."
sleep 10

if docker ps | grep -q ragflow-server; then
    echo "✅ RAGFlow服务已启动"
else
    echo "❌ RAGFlow服务启动失败"
    echo "📋 查看错误日志:"
    docker logs ragflow-server --tail 20
    exit 1
fi

# 检查RAGFlow是否可访问
echo "🌐 检查RAGFlow Web界面..."
for i in {1..30}; do
    if curl -f http://localhost:9380 >/dev/null 2>&1; then
        echo "✅ RAGFlow Web界面可访问"
        break
    else
        echo "⏳ 等待RAGFlow Web界面启动... ($i/30)"
        sleep 10
    fi
done

# 返回原目录
cd ../..

echo ""
echo "🎉 RAGFlow安装完成！"
echo "=================="
echo "RAGFlow Web界面: http://localhost:9380"
echo "默认管理员账号: admin"
echo "默认密码: admin"
echo ""
echo "📝 下一步:"
echo "1. 访问 http://localhost:9380"
echo "2. 使用 admin/admin 登录"
echo "3. 修改默认密码"
echo "4. 在设置中生成API密钥"
echo "5. 将API密钥填入 crewaiBackend/.env 文件"
echo ""
echo "💡 常用命令:"
echo "  查看RAGFlow日志: docker logs -f ragflow-server"
echo "  停止RAGFlow: cd ragflow/docker && docker compose down"
echo "  重启RAGFlow: cd ragflow/docker && docker compose restart"
echo "=================="
