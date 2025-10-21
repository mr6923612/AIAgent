# 测试文档

## 测试概述

本目录包含AI Agent系统的所有测试用例，确保系统功能的正确性和稳定性。

## 测试结构

```
tests/
├── README.md                    # 测试文档
├── test_session_management.py   # 会话管理测试
├── integration/                 # 集成测试
│   ├── test_backend_api.py     # 后端API测试
│   └── ...
└── unit/                       # 单元测试
    ├── test_fuzzy_matching.py  # 模糊匹配测试
    └── ...
```

## 测试工具

### 1. 测试运行脚本

```bash
# 运行所有测试
python scripts/run_tests.py

# 运行指定测试
python scripts/run_tests.py --test test_session_management

# 只运行清理
python scripts/run_tests.py --cleanup-only

# 跳过清理
python scripts/run_tests.py --no-cleanup
```

### 2. 会话清理工具

```bash
# 清理所有会话
python scripts/cleanup_sessions.py

# 清理所有会话（包括数据库表）
python scripts/cleanup_sessions.py --database

# 跳过RAGFlow清理
python scripts/cleanup_sessions.py --no-ragflow

# 确认清理（跳过确认提示）
python scripts/cleanup_sessions.py --confirm
```

### 3. 测试会话清理

```bash
# 清理测试会话
python scripts/test_cleanup.py --test-only

# 清理所有会话
python scripts/test_cleanup.py --all
```

## 测试用例说明

### 会话管理测试 (test_session_management.py)

测试会话的创建、获取、删除、消息管理等功能：

- **test_create_session**: 测试本地会话创建
- **test_create_session_via_api**: 测试API会话创建
- **test_get_session**: 测试会话获取
- **test_add_message**: 测试消息添加
- **test_delete_session**: 测试本地会话删除
- **test_delete_session_via_api**: 测试API会话删除
- **test_ragflow_integration**: 测试RAGFlow集成
- **test_multiple_sessions**: 测试多会话管理

### 集成测试 (integration/)

测试系统各组件之间的集成：

- **test_backend_api.py**: 测试后端API接口
- 其他集成测试...

### 单元测试 (unit/)

测试单个组件的功能：

- **test_fuzzy_matching.py**: 测试模糊匹配功能
- 其他单元测试...

## 测试最佳实践

### 1. 测试前准备

```python
def setup(self):
    """测试前准备"""
    print("🔧 测试前准备...")
    # 初始化必要的组件
    # 清理可能存在的测试数据
```

### 2. 测试后清理

```python
def teardown(self):
    """测试后清理"""
    print("🧹 测试后清理...")
    # 清理测试数据
    # 确保不影响其他测试
```

### 3. 会话注册

```python
# 在测试中创建会话后，注册到清理器
register_test_session(session_id, ragflow_session_id)
```

### 4. 异常处理

```python
try:
    # 测试代码
    assert condition, "错误信息"
    print("✅ 测试通过")
except Exception as e:
    print(f"❌ 测试失败: {e}")
    raise
```

## 测试数据管理

### 1. 测试会话

- 所有测试创建的会话都会自动注册到清理器
- 测试完成后自动清理，避免数据污染
- 支持清理本地会话和RAGFlow会话

### 2. 测试用户

- 使用特定的测试用户ID（如 `test_user`, `test_api_user`）
- 避免与真实用户数据冲突
- 测试完成后清理相关数据

### 3. 测试数据隔离

- 每个测试用例独立运行
- 测试间不共享数据
- 确保测试的可重复性

## 运行测试

### 1. 本地开发

```bash
# 进入后端目录
cd crewaiBackend

# 运行所有测试
python scripts/run_tests.py

# 运行特定测试
python tests/test_session_management.py --test create
```

### 2. CI/CD

```bash
# 在CI环境中运行测试
python scripts/run_tests.py --no-cleanup
```

### 3. 调试测试

```bash
# 运行单个测试并查看详细输出
python tests/test_session_management.py --test ragflow -v
```

## 测试报告

测试运行后会生成详细的报告：

- ✅ 通过的测试数量
- ❌ 失败的测试数量
- 📊 测试统计信息
- ⏰ 测试时间信息
- 🧹 清理状态

## 故障排除

### 常见问题

1. **测试失败**：
   - 检查服务是否运行
   - 验证配置是否正确
   - 查看错误日志

2. **清理失败**：
   - 检查数据库连接
   - 验证RAGFlow服务状态
   - 手动运行清理工具

3. **会话残留**：
   - 运行 `python scripts/cleanup_sessions.py`
   - 检查数据库表
   - 验证RAGFlow会话状态

## 贡献指南

### 添加新测试

1. 在相应目录创建测试文件
2. 继承测试基类或使用测试工具
3. 确保测试后清理
4. 更新文档

### 修改现有测试

1. 确保向后兼容
2. 更新相关文档
3. 验证测试通过
4. 提交代码

## 联系方式

如有测试相关问题，请：

1. 查看本文档
2. 检查测试日志
3. 提交Issue
4. 联系开发团队
