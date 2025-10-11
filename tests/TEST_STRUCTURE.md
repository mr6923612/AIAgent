# 🧪 测试结构说明

## 📁 目录结构

```
tests/
├── unit/                    # 单元测试（不需要LLM）
│   ├── test_speech_to_text.py           # 语音转文字功能测试
│   ├── test_fuzzy_matching.py           # 模糊匹配功能测试
│   ├── test_fuzzy_matching_cli.py       # 命令行交互式测试器
│   ├── test_fuzzy_matching_interactive.py # 图形界面交互式测试器
│   └── start_fuzzy_matching_test.py     # 交互式测试器启动脚本
├── integration/             # 集成测试（需要后端API，避免LLM）
│   ├── test_backend_api.py              # 原始后端API测试
│   └── test_backend_api_optimized.py    # 优化的后端API测试
├── llm_tests/              # LLM测试（需要调用LLM）
│   └── test_integration.py              # 完整集成测试
├── run_all_tests.py        # 运行所有测试
├── run_tests_by_category.py # 分类测试运行器
└── 文档文件...
```

## 🎯 测试分类

### 1. 单元测试 (unit/) - 不需要LLM
- **特点**: 快速执行，独立测试，无外部依赖
- **执行时间**: 1-5分钟
- **成本**: 无
- **适用**: 日常开发，频繁运行

### 2. 集成测试 (integration/) - 需要后端API，避免LLM
- **特点**: 测试API接口，优化减少LLM调用
- **执行时间**: 2-10分钟
- **成本**: 极低
- **适用**: 功能验证，定期运行

### 3. LLM测试 (llm_tests/) - 需要调用LLM
- **特点**: 完整功能测试，需要LLM调用
- **执行时间**: 10-30分钟
- **成本**: 高
- **适用**: 发布前验证，按需运行

## 🚀 运行方式

### 分类运行（推荐）
```bash
cd tests
python run_tests_by_category.py
```

### 单独运行
```bash
# 单元测试
python -m unit.test_speech_to_text
python -m unit.test_fuzzy_matching

# 集成测试
python -m integration.test_backend_api_optimized

# LLM测试
python -m llm_tests.test_integration
```

## 💡 使用建议

### 开发阶段
1. **频繁运行单元测试**: 快速验证功能
2. **定期运行集成测试**: 确保API正常
3. **偶尔运行LLM测试**: 验证完整流程

### CI/CD流水线
1. **必运行**: 单元测试
2. **推荐运行**: 集成测试
3. **可选运行**: LLM测试（根据成本考虑）

### 发布前
1. **必须运行**: 所有测试
2. **重点关注**: LLM测试的完整性和准确性

## ⚡ 性能对比

| 测试类型 | 执行时间 | LLM调用 | 成本 | 适用频率 |
|---------|---------|---------|------|---------|
| 单元测试 | 1-5分钟 | 无 | 无 | 高 |
| 集成测试 | 2-10分钟 | 极少 | 极低 | 中 |
| LLM测试 | 10-30分钟 | 多 | 高 | 低 |

## 🔧 优化说明

### 集成测试优化
- **减少LLM调用**: 只测试API响应，不等待LLM完成
- **简化查询**: 使用简单的测试文本
- **快速验证**: 重点测试错误处理和接口健壮性

### 单元测试优化
- **独立运行**: 不依赖外部服务
- **快速执行**: 专注于功能逻辑测试
- **无成本**: 不产生API调用费用

### LLM测试保留
- **完整验证**: 确保端到端功能正常
- **质量保证**: 验证LLM回复质量
- **按需运行**: 在重要节点执行