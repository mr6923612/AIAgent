# 🧪 测试用例文档

## 📋 快速开始

```bash
cd tests
python run_tests_by_category.py
```

**推荐选择**:
- 1. 单元测试 (不需要LLM) - **日常开发**
- 2. 集成测试 (需要后端API，避免LLM) - **功能验证**
- 3. LLM测试 (需要调用LLM) - **完整测试**
- 5. 交互式测试器 - **参数调优**

## 📁 测试结构

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
└── run_tests_by_category.py # 分类测试运行器
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

## 🚀 使用方法

### 单独运行测试
```bash
# 单元测试
python -m unit.test_speech_to_text
python -m unit.test_fuzzy_matching

# 集成测试
python -m integration.test_backend_api_optimized

# LLM测试
python -m llm_tests.test_integration
```

### 交互式测试器
```bash
# 启动交互式测试器
python -m unit.start_fuzzy_matching_test
```

## 📊 测试数据

### 测试音频文件
- `../test_audios/Recording.m4a` - 英语语音 "other thing is"
- `../test_audios/Recording (2).m4a` - 英语语音 "hello hello"

### 测试文本输入
- 简单问候: "你好，我想了解你们的产品"
- 产品咨询: "这个产品怎么样？价格是多少？"
- 订单查询: "我的订单还没有发货，请帮我查询一下"

## ⚙️ 模糊匹配参数调节

### 主要参数位置 (`crewaiBackend/utils/rag_retriever.py`)
- **第189行**: `if relevance > 0.1` - 文字匹配最低阈值
- **第150行**: `if best_result["relevance"] < 0.9` - 询问确认阈值  
- **第274行**: `if similarity > 0.7` - 图片相似度阈值
- **第337-390行**: `_calculate_relevance` 方法中的各种匹配分数权重

### 参数调节建议
- **提高匹配精度**: 将阈值从0.1提高到0.3
- **降低匹配精度**: 将阈值从0.1降低到0.05
- **使用交互式测试器**: 实时调整参数查看效果

## 🐛 故障排除

### 常见问题
1. **ImportError**: 确保从项目根目录运行测试
2. **ConnectionError**: 确保后端服务正在运行 (端口8012)
3. **语音识别失败**: 检查网络连接和音频文件质量
4. **测试超时**: 单元测试和集成测试应该很快完成

### 调试技巧
1. **查看详细日志**: 后端控制台显示处理日志
2. **分类测试**: 先单元测试，再集成测试，最后LLM测试
3. **检查测试数据**: 验证音频文件存在且可读

## 💡 最佳实践

### 测试策略
1. **分层测试**: 单元测试 → 集成测试 → LLM测试
2. **成本控制**: 优先使用低成本测试
3. **按需运行**: 根据开发阶段选择测试
4. **质量保证**: 重要节点必须运行完整测试

### 开发流程
1. **编码阶段**: 频繁运行单元测试
2. **功能完成**: 运行集成测试
3. **集成阶段**: 运行所有测试
4. **发布前**: 运行完整LLM测试

## 📞 支持

如有问题，请参考：
- [测试结构说明](TEST_STRUCTURE.md)
- [交互式测试指南](INTERACTIVE_TESTING_GUIDE.md)
- [模糊匹配配置指南](FUZZY_MATCHING_CONFIG.md)