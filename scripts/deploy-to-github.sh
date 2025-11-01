#!/bin/bash
# AI Agent GitHub Deployment Script

set -e

echo "🚀 Starting deployment of AI Agent project to GitHub..."

# Check Git status
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Working directory has uncommitted changes, please commit or stash first"
    git status
    exit 1
fi

# Check if in Git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Current directory is not a Git repository, initializing..."
    git init
fi

# Add all files
echo "📁 Adding files to Git..."
git add .

# Commit changes
echo "💾 Committing changes..."
git commit -m "🚀 Add AI Agent project configuration" || echo "No new changes to commit"

# Check remote repository
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "❌ No remote repository configured, please add remote repository first:"
    echo "git remote add origin <your-repo-url>"
    exit 1
fi

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push origin main || git push origin master

echo "✅ Deployment completed!"
echo "🔗 Please visit your GitHub repository to check CI/CD status"
echo "📊 View build and test results in the Actions tab"