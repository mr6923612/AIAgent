#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的Word文档处理脚本
直接处理rag_documents目录中的Word文档，提取文字和图片内容
"""

import os
import sys
import json
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.word_processor import word_processor
from utils.rag_retriever import rag_retriever

def main():
    """主函数"""
    print("=" * 60)
    print("Word文档处理工具")
    print("=" * 60)
    
    # 1. 检查rag_documents目录
    rag_docs_path = "rag_documents"
    if not os.path.exists(rag_docs_path):
        print(f"❌ 目录不存在: {rag_docs_path}")
        print("请确保在正确的目录下运行此脚本")
        return
    
    # 2. 查找Word文档
    word_files = []
    for filename in os.listdir(rag_docs_path):
        if filename.lower().endswith(('.docx', '.doc')):
            word_files.append(filename)
    
    print(f"找到 {len(word_files)} 个Word文档:")
    for i, file in enumerate(word_files, 1):
        file_path = os.path.join(rag_docs_path, file)
        file_size = os.path.getsize(file_path)
        print(f"  {i}. {file} ({file_size:,} bytes)")
    
    if not word_files:
        print("没有找到Word文档")
        print("请将.docx文件放入rag_documents目录")
        print("示例: 已提供sample_product.docx作为参考")
        return
    
    # 3. 处理Word文档
    print(f"\n开始处理Word文档...")
    results = word_processor.process_word_documents()
    
    if not results:
        print("没有需要处理的文档（可能已经处理过）")
    else:
        print(f"处理完成！")
        for filename, result in results.items():
            status = result.get('status', 'unknown')
            if status == 'success':
                content_count = result.get('content_count', 0)
                image_count = result.get('image_count', 0)
                print(f"  {os.path.basename(filename)}: {content_count} 个内容项, {image_count} 张图片")
            else:
                error = result.get('error', '未知错误')
                print(f"  {os.path.basename(filename)}: 处理失败 - {error}")
    
    # 4. 显示处理状态
    print(f"\n处理状态统计:")
    processed_content = word_processor.get_processed_content()
    total_docs = len(processed_content)
    total_items = sum(len(content) for content in processed_content.values())
    
    print(f"  已处理文档: {total_docs} 个")
    print(f"  总内容项: {total_items} 个")
    
    if processed_content:
        print(f"  文档列表:")
        for filename in processed_content.keys():
            print(f"    - {filename}")
    
    # 5. 测试RAG检索
    print(f"\n测试RAG检索功能...")
    test_queries = ["产品", "价格", "功能", "图片"]
    
    for query in test_queries:
        print(f"\n  搜索: '{query}'")
        results = rag_retriever.search(query, max_results=3)
        
        if results:
            print(f"    找到 {len(results)} 个结果:")
            for i, result in enumerate(results, 1):
                result_type = result.get('type', 'unknown')
                content = result.get('content', '')[:80]
                relevance = result.get('relevance', 0)
                source = result.get('source', 'unknown')
                print(f"      {i}. [{result_type}] {content}...")
                print(f"         相关度: {relevance:.2f} | 来源: {source}")
        else:
            print(f"    没有找到相关结果")
    
    # 6. 显示文件结构
    print(f"\n生成的文件:")
    if os.path.exists(rag_docs_path):
        for filename in os.listdir(rag_docs_path):
            if filename.endswith('_content.json') or filename == 'processed_docs.json':
                file_path = os.path.join(rag_docs_path, filename)
                file_size = os.path.getsize(file_path)
                print(f"  {filename} ({file_size:,} bytes)")
    
    images_dir = os.path.join(rag_docs_path, "images")
    if os.path.exists(images_dir):
        image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        if image_files:
            print(f"  images/ 目录: {len(image_files)} 张图片")
            for img_file in image_files[:5]:  # 只显示前5个
                print(f"    - {img_file}")
            if len(image_files) > 5:
                print(f"    ... 还有 {len(image_files) - 5} 张图片")
    
    print(f"\n" + "=" * 60)
    print("Word文档处理完成！")
    print("现在可以启动主服务器进行客服机器人测试了")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n用户中断操作")
    except Exception as e:
        print(f"\n\n发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
