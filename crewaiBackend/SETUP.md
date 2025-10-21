# 环境配置说明

## 1. 创建环境变量文件

在 `crewaiBackend` 目录下创建 `.env` 文件：

```bash
cd crewaiBackend
cp env.template .env
```

## 2. 配置API密钥

编辑 `.env` 文件，填入您的实际API密钥：

```bash
# Google API配置
GOOGLE_API_KEY=your_actual_google_api_key_here

# RAGFlow配置
RAGFLOW_BASE_URL=http://localhost:80
RAGFLOW_API_KEY=your_actual_ragflow_api_key_here
RAGFLOW_CHAT_ID=your_actual_ragflow_chat_id_here

# MySQL配置
MYSQL_HOST=localhost
MYSQL_PORT=3307
MYSQL_USER=root
MYSQL_PASSWORD=your_actual_mysql_password_here
MYSQL_DATABASE=aiagent_chat

# Flask配置
FLASK_DEBUG=True
FLASK_ENV=development
```

## 3. 获取API密钥

### Google API密钥
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 Gemini API
4. 创建API密钥

### RAGFlow配置
1. 启动RAGFlow服务
2. 在RAGFlow界面中获取API密钥和Chat ID
3. 确保RAGFlow服务运行在指定端口

### MySQL配置
1. 确保MySQL服务正在运行
2. 创建数据库：`CREATE DATABASE aiagent_chat;`
3. 确保用户有相应权限

## 4. 验证配置

运行以下命令验证配置：

```bash
python -c "from config import config; print('配置加载成功')"
```

## 5. 安全注意事项

- **永远不要**将 `.env` 文件提交到Git仓库
- 确保 `.env` 文件在 `.gitignore` 中
- 定期轮换API密钥
- 使用最小权限原则配置数据库用户

## 6. 生产环境配置

在生产环境中，建议：

1. 使用环境变量而不是文件：
   ```bash
   export GOOGLE_API_KEY="your_key"
   export RAGFLOW_API_KEY="your_key"
   ```

2. 使用密钥管理服务（如AWS Secrets Manager、Azure Key Vault等）

3. 定期更新和轮换密钥

## 7. 故障排除

### 常见问题

1. **环境变量未加载**：
   - 确保 `.env` 文件在正确位置
   - 检查文件格式（无空格，正确换行）

2. **API密钥无效**：
   - 验证密钥格式
   - 检查API服务状态
   - 确认权限设置

3. **数据库连接失败**：
   - 检查MySQL服务状态
   - 验证连接参数
   - 确认数据库存在
