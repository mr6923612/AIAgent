# Scripts 目录说明

这个目录包含了项目的实用脚本，用于各种维护和操作任务。

## 📋 可用脚本

### 1. `process_word_docs.py`
**用途**: 处理RAG文档目录中的Word文档
**功能**:
- 自动扫描Word文档
- 提取文字和图片内容
- 按产品分组处理
- 生成JSON格式的内容文件
- 测试RAG检索功能

**使用方法**:
```bash
python scripts/process_word_docs.py
```

### 2. `check_status.py`
**用途**: 检查项目状态和配置
**功能**:
- 检查Python版本
- 检查依赖包安装
- 检查项目结构完整性
- 检查RAG文档状态
- 检查配置设置
- 检查网络连接

**使用方法**:
```bash
python scripts/check_status.py
```

### 3. `cleanup.py`
**用途**: 清理项目临时文件和缓存
**功能**:
- 清理Python缓存文件 (`__pycache__`, `*.pyc`)
- 清理临时文件 (`*.tmp`, `*.log`, `*.bak`)
- 清理Word临时文件 (`~$*.docx`)
- 清理IDE文件 (`.vscode`, `.idea`)
- 清理系统文件 (`.DS_Store`, `Thumbs.db`)

**使用方法**:
```bash
python scripts/cleanup.py
```

## 🚀 快速使用

### 日常开发流程
```bash
# 1. 检查项目状态
python scripts/check_status.py

# 2. 处理新的Word文档（如果需要）
python scripts/process_word_docs.py

# 3. 启动服务器
python main.py

# 4. 清理临时文件（定期执行）
python scripts/cleanup.py
```

### 故障排除
```bash
# 检查项目是否有问题
python scripts/check_status.py

# 清理可能损坏的缓存文件
python scripts/cleanup.py

# 重新处理Word文档
python scripts/process_word_docs.py
```

## 📝 注意事项

1. **运行环境**: 所有脚本都需要在项目根目录下运行
2. **Python版本**: 需要Python 3.10或更高版本
3. **依赖包**: 确保已安装所有必需的依赖包
4. **权限**: 确保有读写项目文件的权限

## 🔧 自定义

如果需要修改脚本行为，可以：
1. 直接编辑对应的Python文件
2. 修改配置参数
3. 添加新的检查项目或清理规则

所有脚本都包含详细的注释，便于理解和修改。
