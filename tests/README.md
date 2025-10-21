# 测试配置和指南

## 🧪 测试结构

```
tests/
├── integration/           # 集成测试
│   ├── test_backend_api.py        # 后端API测试
│   └── test_backend_api_optimized.py  # 优化版API测试
├── unit/                 # 单元测试
│   ├── test_speech_to_text.py     # 语音转文字测试
│   └── test_fuzzy_matching.py     # 模糊匹配测试
├── llm_tests/            # LLM测试
│   └── test_integration.py        # LLM集成测试
├── run_all_tests.py      # 运行所有测试
└── run_tests_by_category.py  # 按类别运行测试
```

## 🚀 运行测试

### 运行所有测试
```bash
cd tests
python run_all_tests.py
```

### 按类别运行测试
```bash
# 集成测试
python run_tests_by_category.py integration

# 单元测试
python run_tests_by_category.py unit

# LLM测试
python run_tests_by_category.py llm_tests
```

### 运行特定测试
```bash
# 后端API测试
python integration/test_backend_api.py

# 语音转文字测试
python unit/test_speech_to_text.py
```

## 📋 测试覆盖

### 集成测试
- **API端点测试**: 验证所有API接口
- **端到端测试**: 完整用户流程测试
- **多模态测试**: 文本、图片、语音输入测试
- **错误处理测试**: 异常情况处理测试

### 单元测试
- **核心功能测试**: 关键业务逻辑测试
- **工具函数测试**: 工具模块功能测试
- **数据处理测试**: 数据转换和处理测试

### LLM测试
- **模型连接测试**: LLM服务连接测试
- **响应质量测试**: AI回复质量测试
- **多语言测试**: 中英文处理测试

## 🔧 测试配置

### 环境变量
```bash
# 测试环境配置
export TEST_MODE=true
export GOOGLE_API_KEY="test_api_key"
export RAGFLOW_BASE_URL="http://localhost:80"
export RAGFLOW_API_KEY="test_ragflow_key"
```

### 测试数据
- **测试用户**: 预定义的测试用户账号
- **测试文件**: 用于测试的图片和音频文件
- **测试消息**: 标准化的测试消息模板

## 📝 编写测试

### 测试模板
```python
import unittest
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestExample(unittest.TestCase):
    """测试示例"""
    
    def setUp(self):
        """测试前准备"""
        self.test_data = "test_data"
    
    def test_function(self):
        """测试函数"""
        result = function_to_test(self.test_data)
        self.assertEqual(result, expected_result)
    
    def tearDown(self):
        """测试后清理"""
        pass

if __name__ == '__main__':
    unittest.main()
```

### 测试最佳实践
- 使用描述性的测试名称
- 每个测试只测试一个功能
- 使用断言验证结果
- 清理测试数据
- 添加测试文档

## 🐛 故障排除

### 常见问题

1. **导入错误**
   - 检查Python路径设置
   - 验证模块安装
   - 确认文件结构

2. **API连接失败**
   - 检查后端服务状态
   - 验证API配置
   - 确认网络连接

3. **测试数据问题**
   - 检查测试文件存在
   - 验证数据格式
   - 确认权限设置

## 📊 测试报告

### 生成测试报告
```bash
# 生成HTML报告
python -m pytest --html=report.html

# 生成覆盖率报告
python -m pytest --cov=crewaiBackend --cov-report=html
```

### 报告内容
- 测试执行结果
- 覆盖率统计
- 失败测试详情
- 性能指标

## 🔄 持续集成

### GitHub Actions配置
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: pip install -r crewaiBackend/requirements.txt
      - name: Run tests
        run: python tests/run_all_tests.py
```

## 📄 许可证

MIT License