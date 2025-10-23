# 📊 会话持久化机制说明

## 概述

本系统采用**双层存储架构**：
- **内存层**：Agent实例（临时，用于性能优化）
- **持久层**：MySQL数据库（永久，用于数据持久化）

## 资源生命周期

### 1. 程序启动时
```
程序启动 → 创建全局LLM实例 → 创建全局RAGFlow客户端
```

### 2. 会话创建时
```
创建会话 → 保存到MySQL → 创建Agent实例（内存）
```

### 3. 请求处理时
```
接收请求 → 复用现有Agent → 处理请求 → 保存消息到MySQL
```

### 4. 会话清理时
```
清理触发 → 释放Agent实例（内存） → 保留MySQL数据
```

### 5. 重新访问时
```
重新访问 → 从MySQL加载会话 → 重新创建Agent实例
```

## 清理机制详解

### Agent清理（内存层）
```python
# 清理非活跃Agent（不影响SQL数据）
session_agent_manager.cleanup_inactive_sessions(max_age_seconds=1800)
```

**清理内容**：
- ✅ 释放Agent实例（内存）
- ✅ 释放Crew实例（内存）
- ❌ **不影响SQL数据**

**触发条件**：
- Agent超过30分钟未使用
- 定时清理（每5分钟检查一次）
- 手动清理API调用

### 会话删除（持久层）
```python
# 完全删除会话（包括SQL数据）
session_manager.delete_session(session_id, ragflow_client)
```

**删除内容**：
- ✅ 删除Agent实例（内存）
- ✅ 删除SQL中的会话数据
- ✅ 删除SQL中的消息数据
- ✅ 删除RAGFlow会话

## 数据持久化保证

### SQL数据保留
```sql
-- 会话表
CREATE TABLE chat_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    title VARCHAR(500),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    context JSON,
    ragflow_session_id VARCHAR(255)
);

-- 消息表
CREATE TABLE chat_messages (
    id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255),
    role VARCHAR(50),
    content TEXT,
    timestamp TIMESTAMP
);
```

### 数据恢复流程
1. **用户重新登录**
2. **调用获取会话API**：`GET /api/sessions/{session_id}`
3. **从MySQL加载数据**：会话信息 + 消息历史
4. **重新创建Agent**：基于加载的数据创建新的Agent实例

## 测试验证

### 运行持久化测试
```bash
python scripts/test_session_persistence.py
```

### 测试步骤
1. 创建测试会话
2. 添加测试消息
3. 等待Agent清理
4. 验证SQL数据保留
5. 测试会话恢复
6. 验证Agent重新创建

### 预期结果
- ✅ SQL数据完整保留
- ✅ 会话可以重新加载
- ✅ Agent可以重新创建
- ✅ 消息历史完整

## 使用场景

### 场景1：正常使用
```
用户登录 → 创建会话 → 发送消息 → 关闭浏览器
↓
用户重新登录 → 加载历史会话 → 继续对话
```

### 场景2：长时间未使用
```
用户登录 → 创建会话 → 发送消息 → 长时间未使用
↓
系统清理Agent → 保留SQL数据
↓
用户重新登录 → 从SQL加载会话 → 重新创建Agent → 继续对话
```

### 场景3：主动删除
```
用户登录 → 创建会话 → 发送消息 → 主动删除会话
↓
完全删除 → SQL数据删除 → Agent释放
```

## 配置参数

### Agent清理配置
```python
# 最大非活跃时间（秒）
max_age_seconds = 1800  # 30分钟

# 清理检查间隔（秒）
cleanup_interval = 300  # 5分钟
```

### 数据库配置
```python
# MySQL连接配置
MYSQL_HOST = "backend-mysql"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "root123"
MYSQL_DATABASE = "backend_db"
```

## 监控和调试

### 查看会话状态
```bash
# 查看所有会话状态
curl http://localhost:5000/api/sessions/status

# 查看特定会话
curl http://localhost:5000/api/sessions/{session_id}
```

### 手动清理
```bash
# 清理非活跃Agent
curl -X POST http://localhost:5000/api/sessions/cleanup

# 完全删除会话
curl -X DELETE http://localhost:5000/api/sessions/{session_id}
```

### 日志监控
```bash
# 查看Agent清理日志
grep "清理" logs/app.log

# 查看会话创建日志
grep "创建会话" logs/app.log
```

## 最佳实践

### 1. 会话管理
- 定期清理非活跃Agent，释放内存
- 保留SQL数据，确保数据持久化
- 支持会话恢复，提升用户体验

### 2. 性能优化
- 使用Agent复用，减少创建开销
- 全局共享LLM和RAGFlow客户端
- 定时清理，避免内存泄漏

### 3. 数据安全
- 重要数据存储在MySQL中
- 支持数据备份和恢复
- 提供完整的审计日志

## 故障排除

### 问题1：会话数据丢失
**原因**：调用了删除会话API
**解决**：检查是否误调用了`DELETE /api/sessions/{session_id}`

### 问题2：Agent无法恢复
**原因**：SQL数据损坏或Agent创建失败
**解决**：检查数据库连接和Agent创建日志

### 问题3：内存使用过高
**原因**：Agent清理不及时
**解决**：调整清理参数或手动清理

## 总结

✅ **SQL数据永久保留**：会话清理后，SQL中的会话信息仍然存在
✅ **支持重新登录**：下次登录可以从SQL重新加载会话
✅ **Agent自动重建**：重新访问时会自动创建新的Agent实例
✅ **性能优化**：通过Agent复用和定时清理优化内存使用
✅ **数据完整性**：确保用户数据不丢失，提供良好的用户体验
