#!/bin/bash
# AI Agent GitHub部署脚本

set -e

echo "🚀 开始部署AI Agent项目到GitHub..."

# 检查Git状态
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ 工作目录有未提交的更改，请先提交或暂存"
    git status
    exit 1
fi

# 检查是否在Git仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ 当前目录不是Git仓库，正在初始化..."
    git init
fi

# 添加所有文件
echo "📁 添加文件到Git..."
git add .

# 提交更改
echo "💾 提交更改..."
git commit -m "🚀 添加AI Agent项目配置" || echo "没有新的更改需要提交"

# 检查远程仓库
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "❌ 没有配置远程仓库，请先添加远程仓库："
    echo "git remote add origin <your-repo-url>"
    exit 1
fi

# 推送到GitHub
echo "📤 推送到GitHub..."
git push origin main || git push origin master

echo "✅ 部署完成！"
echo "🔗 请访问您的GitHub仓库查看CI/CD状态"
echo "📊 在Actions标签页中查看构建和测试结果"