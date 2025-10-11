# CrewAI Backend 项目结构

## 📁 目录结构

```
crewaiBackend/
├── 📄 main.py                    # 主服务器入口
├── 📄 crew.py                    # CrewAI核心逻辑
├── 📄 requirements.txt           # Python依赖
├── 📄 README.md                  # 项目说明
├── 📄 PROJECT_STRUCTURE.md       # 项目结构说明（本文件）
│
├── 📁 utils/                     # 工具模块
│   ├── 📄 __init__.py
│   ├── 📄 jobManager.py          # 任务管理器
│   ├── 📄 myLLM.py              # LLM配置
│   ├── 📄 rag_retriever.py      # RAG检索器
│   └── 📄 word_processor.py     # Word文档处理器
│
├── 📁 config/                    # 配置文件
│   ├── 📄 agents.yaml           # Agent配置
│   └── 📄 tasks.yaml            # Task配置
│
├── 📁 scripts/                   # 脚本文件
│   ├── 📄 process_word_docs.py  # Word文档处理脚本
│   ├── 📄 check_status.py       # 项目状态检查脚本
│   └── 📄 cleanup.py            # 项目清理脚本
│
├── 📁 tests/                     # 测试文件
│   ├── 📄 test_google_api.py    # Google API测试
│   ├── 📄 fix_google_api.py     # Google API修复
│   └── 📄 install_google_deps.py # Google依赖安装
│
├── 📁 docs/                      # 文档
│   ├── 📄 GOOGLE_API_SETUP.md   # Google API设置说明
│   ├── 📄 README.md             # RAG文档说明
│   └── 📄 WORD_DOCS_USAGE.md    # Word文档使用说明
│
└── 📁 rag_documents/             # RAG文档存储
    ├── 📄 sample_product.docx   # 示例产品Word文档
    ├── 📄 sample_product_content.json # 提取的内容
    ├── 📄 taobao_customer_service.md # 淘宝客服问答库
    ├── 📄 processed_docs.json   # 处理记录
    ├── 📁 images/               # 提取的图片
    │   ├── 📄 extracted_1.png
    │   └── 📄 README.md
    └── 📁 uploads/              # 上传文件目录
```

## 🚀 快速开始

### 1. 启动主服务器
```bash
# 直接运行主服务器
python main.py
```

### 2. 处理Word文档
```bash
# 直接运行Word文档处理脚本
python scripts/process_word_docs.py
```

## 📋 核心功能

### 1. 主服务器 (main.py)
- **端口**: 8012
- **功能**: CrewAI客服机器人API服务
- **接口**:
  - `POST /api/crew` - 运行客服机器人
  - `GET /api/crew/<job_id>` - 获取任务状态

### 2. Word文档处理 (scripts/process_word_docs.py)
- **功能**: 处理RAG文档目录中的Word文档
- **特性**:
  - 自动提取文字和图片
  - 按产品分组处理
  - 智能关联内容
  - 避免重复处理

### 3. RAG检索系统 (utils/rag_retriever.py)
- **功能**: 多模态RAG检索
- **特性**:
  - 文字检索
  - 图片检索
  - 产品信息检索
  - 客服问答检索
  - 多模态融合

## 🔧 工具模块

### utils/jobManager.py
- 任务状态管理
- 事件记录
- 线程安全操作

### utils/myLLM.py
- LLM配置管理
- 支持多种LLM提供商
- 统一接口

### utils/word_processor.py
- Word文档解析
- 产品信息提取
- 图片提取和关联

### utils/rag_retriever.py
- 多模态检索
- 相关性计算
- 结果排序

## 📚 文档说明

### docs/GOOGLE_API_SETUP.md
- Google API配置指南
- API密钥设置
- 依赖安装说明

### docs/WORD_DOCS_USAGE.md
- Word文档处理使用说明
- 产品格式要求
- 处理流程说明

### docs/README.md
- RAG文档系统说明
- 多模态检索原理
- 使用指南

## 🧪 测试文件

### tests/test_google_api.py
- Google API功能测试
- API连接验证
- 错误处理测试

### tests/fix_google_api.py
- Google API问题修复
- 依赖更新
- 配置修复

### tests/install_google_deps.py
- Google依赖安装
- 环境配置
- 版本检查

## 📁 数据存储

### rag_documents/
- **docs.docx**: 原始Word文档
- **docs_content.json**: 提取的结构化内容
- **processed_docs.json**: 处理记录和状态
- **images/**: 提取的图片文件
- **uploads/**: 用户上传的文件

## 🔄 工作流程

1. **准备文档**: 将Word文档放入 `rag_documents/` 目录
2. **处理文档**: 运行 `scripts/process_word_docs.py`
3. **启动服务**: 运行 `scripts/start_server.bat/sh`
4. **测试功能**: 通过API或前端测试客服机器人

## ⚙️ 配置说明

### config/agents.yaml
- Agent角色定义
- 技能配置
- 行为设置

### config/tasks.yaml
- 任务流程定义
- 输入输出规范
- 执行顺序

## 🛠️ 开发指南

### 添加新功能
1. 在 `utils/` 目录添加工具模块
2. 在 `scripts/` 目录添加脚本文件
3. 在 `tests/` 目录添加测试文件
4. 更新相关文档

### 调试和测试
1. 使用 `tests/` 目录中的测试文件
2. 检查日志输出
3. 验证API响应
4. 测试RAG检索功能

## 📝 注意事项

1. **环境要求**: Python 3.10+, 相关依赖包
2. **文件权限**: 确保有读写 `rag_documents/` 的权限
3. **端口占用**: 确保8012端口未被占用
4. **依赖管理**: 定期更新 `requirements.txt`
5. **数据备份**: 定期备份 `rag_documents/` 目录
