# 🔍 模糊匹配参数配置指南

## ⚙️ 可调节参数

### 1. 相关性阈值参数

#### 文字匹配最低阈值
**位置**: `crewaiBackend/utils/rag_retriever.py` 第189行
```python
if relevance > 0.1:  # 当前设置：0.1
```

#### 询问确认阈值
**位置**: `crewaiBackend/utils/rag_retriever.py` 第150行
```python
if best_result["relevance"] < 0.9:  # 当前设置：0.9
```

#### 图片相似度阈值
**位置**: `crewaiBackend/utils/rag_retriever.py` 第274行
```python
if similarity > 0.7:  # 当前设置：0.7
```

### 2. 匹配算法分数权重

#### 匹配分数设置
**位置**: `crewaiBackend/utils/rag_retriever.py` 第337-390行
```python
# 完全匹配分数
return 1.0  # 第346行

# 部分匹配分数
return 0.8  # 第353行

# 词汇匹配分数范围
return max(0.2, min(relevance, 1.0))  # 第368行

# 相似词汇匹配分数
return 0.3  # 第377行

# 字符级匹配分数
return 0.2  # 第388行
```

## 🔧 参数调节指南

### 场景1: 提高匹配精度（更严格）

```python
# 1. 提高文字匹配阈值
if relevance > 0.3:  # 从0.1提高到0.3

# 2. 提高图片相似度阈值
if similarity > 0.8:  # 从0.7提高到0.8

# 3. 降低询问确认阈值
if best_result["relevance"] < 0.8:  # 从0.9降低到0.8
```

### 场景2: 降低匹配精度（更宽松）

```python
# 1. 降低文字匹配阈值
if relevance > 0.05:  # 从0.1降低到0.05

# 2. 降低图片相似度阈值
if similarity > 0.5:  # 从0.7降低到0.5

# 3. 提高询问确认阈值
if best_result["relevance"] < 0.95:  # 从0.9提高到0.95
```

## 🧪 测试参数效果

### 使用测试用例验证参数

```bash
# 运行模糊匹配测试
cd tests
python -m unit.test_fuzzy_matching

# 或使用交互式测试器
python run_tests_by_category.py
# 选择 5 - 交互式测试器
```

## 📊 参数优化建议

### 根据业务需求调整

#### 电商产品搜索
```python
relevance_threshold = 0.1  # 宽松匹配，避免遗漏
image_similarity = 0.7     # 中等图片匹配
```

#### 客服问答系统
```python
relevance_threshold = 0.2  # 稍严格的匹配
image_similarity = 0.8     # 严格的图片匹配
```

#### 内容推荐系统
```python
relevance_threshold = 0.05 # 非常宽松的匹配
image_similarity = 0.6     # 宽松的图片匹配
```

## 🔄 参数调优流程

### 1. 基准测试
- 使用当前参数运行测试
- 记录匹配准确率和性能指标

### 2. 参数调整
- 根据需求调整参数
- 逐步调整，观察效果

### 3. 效果验证
- 运行测试用例
- 对比调整前后的结果

### 4. 生产部署
- 确认参数效果后部署
- 监控生产环境表现

## 🚨 注意事项

### 参数调整风险
1. **过度宽松**: 可能返回不相关结果
2. **过度严格**: 可能遗漏相关结果
3. **性能影响**: 低阈值可能影响响应速度

### 最佳实践
1. **渐进调整**: 逐步调整参数，观察效果
2. **A/B测试**: 对比不同参数的效果
3. **监控指标**: 持续监控匹配质量和性能
4. **用户反馈**: 收集用户对匹配结果的反馈