# AI Agent 测试框架

## 概述

本项目使用 pytest 作为主要测试框架，提供了完整的测试覆盖，包括单元测试、集成测试、API测试、数据库测试和外部服务测试。

## 测试结构

```
tests/
├── conftest.py              # 测试配置和共享夹具
├── unit/                    # 单元测试
│   ├── test_config.py
│   └── test_session_manager.py
├── integration/             # 集成测试
│   └── test_session_flow.py
├── api/                     # API测试
│   ├── test_session_api.py
│   └── test_crew_api.py
├── database/                # 数据库测试
│   └── test_mysql_operations.py
└── external/                # 外部服务测试
    └── test_ragflow_integration.py
```

## 快速开始

### 1. 安装测试依赖

```bash
cd crewaiBackend
pip install -r requirements.txt
```

### 2. 运行测试

#### 使用测试脚本（推荐）

```bash
# 交互式选择测试类型
python scripts/test_runner.py

# 直接运行特定测试
python scripts/test_runner.py 1  # 快速测试
python scripts/test_runner.py 6  # 所有测试
```

#### 使用pytest命令

```bash
# 运行所有测试
pytest

# 运行特定类型的测试
pytest tests/unit/              # 单元测试
pytest tests/integration/       # 集成测试
pytest tests/api/               # API测试
pytest tests/database/          # 数据库测试
pytest tests/external/          # 外部服务测试

# 运行带标记的测试
pytest -m smoke                 # 冒烟测试
pytest -m unit                  # 单元测试
pytest -m integration           # 集成测试

# 运行特定测试文件
pytest tests/unit/test_config.py
```

## 测试类型说明

### 1. 单元测试 (Unit Tests)
- **位置**: `tests/unit/`
- **目的**: 测试各个模块的独立功能
- **特点**: 快速、隔离、Mock外部依赖
- **运行时间**: < 30秒

### 2. 集成测试 (Integration Tests)
- **位置**: `tests/integration/`
- **目的**: 测试模块间的交互
- **特点**: 测试完整的业务流程
- **运行时间**: 30秒 - 2分钟

### 3. API测试 (API Tests)
- **位置**: `tests/api/`
- **目的**: 测试Flask API接口
- **特点**: 使用测试客户端，Mock外部服务
- **运行时间**: 1-3分钟

### 4. 数据库测试 (Database Tests)
- **位置**: `tests/database/`
- **目的**: 测试MySQL数据库操作
- **特点**: 使用测试数据库，事务回滚
- **运行时间**: 30秒 - 1分钟

### 5. 外部服务测试 (External Service Tests)
- **位置**: `tests/external/`
- **目的**: 测试RAGFlow、Gemini等外部服务集成
- **特点**: Mock外部API调用
- **运行时间**: 1-2分钟

## 测试标记

- `@pytest.mark.unit`: 单元测试
- `@pytest.mark.integration`: 集成测试
- `@pytest.mark.api`: API测试
- `@pytest.mark.database`: 数据库测试
- `@pytest.mark.external`: 外部服务测试
- `@pytest.mark.slow`: 慢速测试
- `@pytest.mark.smoke`: 冒烟测试

## 测试配置

### pytest.ini
```ini
[tool:pytest]
testpaths = crewaiBackend/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --cov=crewaiBackend
    --cov-report=html:htmlcov
    --cov-report=term-missing
    --cov-fail-under=70
    --html=reports/report.html
    --self-contained-html
    --timeout=300
    --maxfail=5
```

### 环境变量
测试使用独立的环境变量配置：
- `MYSQL_DATABASE=test_backend_db`
- `MYSQL_HOST=localhost`
- `MYSQL_PORT=3306`

## 测试报告

### 1. 控制台报告
- 实时显示测试进度
- 显示失败测试的详细信息
- 显示覆盖率统计

### 2. HTML报告
- 位置: `reports/report.html`
- 包含详细的测试结果
- 支持测试历史对比

### 3. 覆盖率报告
- 位置: `htmlcov/index.html`
- 显示代码覆盖率
- 高亮未覆盖的代码行

## CI/CD集成

### GitHub Actions
- 自动运行测试
- 生成测试报告
- 代码覆盖率检查
- 安全扫描

### 测试流程
1. 代码提交触发CI
2. 安装依赖和环境
3. 运行单元测试
4. 运行集成测试
5. 运行API测试
6. 运行数据库测试
7. 生成测试报告
8. 检查覆盖率阈值

## 最佳实践

### 1. 测试编写
- 使用描述性的测试名称
- 每个测试只验证一个功能点
- 使用Mock隔离外部依赖
- 保持测试的独立性

### 2. 测试数据
- 使用夹具管理测试数据
- 避免硬编码的测试数据
- 使用工厂模式生成测试数据

### 3. 测试维护
- 定期更新测试用例
- 删除过时的测试
- 保持测试的简洁性

### 4. 性能考虑
- 快速测试优先
- 使用并行测试加速
- 避免不必要的等待

## 故障排除

### 常见问题

1. **测试失败**: 检查测试数据和Mock配置
2. **数据库连接失败**: 确保测试数据库已启动
3. **外部服务超时**: 检查网络连接和Mock配置
4. **覆盖率不足**: 添加更多测试用例

### 调试技巧

1. 使用 `-v` 参数查看详细输出
2. 使用 `--tb=long` 查看完整错误信息
3. 使用 `--pdb` 进入调试模式
4. 使用 `--lf` 只运行上次失败的测试

## 贡献指南

1. 为新功能添加测试
2. 确保测试覆盖率 > 70%
3. 遵循测试命名规范
4. 更新测试文档