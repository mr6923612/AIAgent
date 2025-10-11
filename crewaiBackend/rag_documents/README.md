# RAG文档目录说明

这个目录用于存储RAG（检索增强生成）系统的文档和内容。

## 📁 目录结构

```
rag_documents/
├── sample_product.docx           # 示例产品Word文档
├── sample_product_content.json   # 提取的产品内容
├── taobao_customer_service.md   # 淘宝客服问答库
├── processed_docs.json          # 处理记录
├── SAMPLE_PRODUCT_INFO.md       # 示例产品说明
├── images/                      # 提取的图片
│   ├── extracted_1.png         # 产品图片
│   └── README.md               # 图片说明
└── uploads/                     # 上传文件目录
```

## 🚀 快速开始

### 1. 查看示例产品
- **文件**: `sample_product.docx`
- **说明**: `SAMPLE_PRODUCT_INFO.md`
- **内容**: 新西兰dermatix舒痕祛疤膏产品介绍

### 2. 处理Word文档
```bash
# 运行处理脚本
python scripts/process_word_docs.py
```

### 3. 查看处理结果
- **内容文件**: `sample_product_content.json`
- **图片文件**: `images/extracted_1.png`
- **处理记录**: `processed_docs.json`

## 📋 添加新文档

### 1. 准备Word文档
按照以下格式组织您的产品文档：

```
产品名称
产品图片
产品介绍
(空行)
下一个产品名称
下一个产品图片
下一个产品介绍
(空行)
...
```

### 2. 放入目录
将.docx文件放入 `rag_documents/` 目录

### 3. 运行处理
```bash
python scripts/process_word_docs.py
```

## 🔍 RAG检索

处理后的文档会自动集成到RAG检索系统中：

- **产品检索**: 支持产品名称、描述、特性搜索
- **客服问答**: 支持常见客服问题的智能回答
- **图片检索**: 支持图片相似度搜索
- **多模态检索**: 同时搜索文字和图片内容

### 客服问答库包含：
- 产品咨询类问题
- 价格优惠类问题
- 物流配送类问题
- 退换货类问题
- 售后服务类问题
- 支付方式类问题
- 会员服务类问题
- 常见问题类问题
- 产品使用类问题
- 投诉建议类问题

## 📝 注意事项

1. **文件格式**: 只支持.docx格式
2. **产品分割**: 用空行分隔不同产品
3. **图片要求**: 图片会自动提取，建议使用清晰图片
4. **文件大小**: 建议单个文档不超过50MB
5. **重复处理**: 系统会自动跳过已处理的文档

## 🛠️ 维护

### 清理文件
```bash
# 清理临时文件
python scripts/cleanup.py
```

### 检查状态
```bash
# 检查项目状态
python scripts/check_status.py
```

## 📚 更多信息

- [Word文档使用说明](../docs/WORD_DOCS_USAGE.md)
- [项目结构说明](../PROJECT_STRUCTURE.md)
- [示例产品说明](SAMPLE_PRODUCT_INFO.md)