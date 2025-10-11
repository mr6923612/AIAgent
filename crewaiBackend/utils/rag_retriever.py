# -*- coding: utf-8 -*-
"""
多模态RAG文档检索工具
支持文字和图片的检索和对比
"""

import os
import re
import base64
import hashlib
from typing import List, Dict, Tuple, Optional
from PIL import Image
import io
import json

class MultimodalRAGRetriever:
    """多模态RAG文档检索器"""
    
    def __init__(self, knowledge_base_path: str = "rag_documents/taobao_customer_service.md", 
                 images_path: str = "rag_documents/images",
                 products_content_path: str = "rag_documents/products_content.json"):
        """
        初始化多模态RAG检索器
        
        Args:
            knowledge_base_path: 知识库文档路径
            images_path: 图片存储路径
            products_content_path: 产品内容JSON文件路径
        """
        self.knowledge_base_path = knowledge_base_path
        self.images_path = images_path
        self.products_content_path = products_content_path
        self.knowledge_content = self._load_knowledge_base()
        self.image_database = self._load_image_database()
        self.products_content = self._load_products_content()
    
    def _load_knowledge_base(self) -> str:
        """加载知识库文档"""
        try:
            if os.path.exists(self.knowledge_base_path):
                with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return "知识库文档不存在"
        except Exception as e:
            return f"加载知识库失败: {str(e)}"
    
    def _load_image_database(self) -> Dict[str, Dict]:
        """加载图片数据库"""
        image_db = {}
        try:
            if os.path.exists(self.images_path):
                for filename in os.listdir(self.images_path):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                        image_path = os.path.join(self.images_path, filename)
                        image_info = self._analyze_image(image_path)
                        image_db[filename] = image_info
        except Exception as e:
            print(f"加载图片数据库失败: {str(e)}")
        return image_db
    
    
    def _load_products_content(self) -> List[Dict]:
        """加载产品内容JSON文件"""
        try:
            if os.path.exists(self.products_content_path):
                with open(self.products_content_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载产品内容失败: {str(e)}")
        return []
    
    def _analyze_image(self, image_path: str) -> Dict:
        """分析图片并提取特征"""
        try:
            with Image.open(image_path) as img:
                # 获取图片基本信息
                width, height = img.size
                mode = img.mode
                
                # 计算图片哈希值用于快速对比
                img_hash = self._calculate_image_hash(img)
                
                return {
                    "path": image_path,
                    "filename": os.path.basename(image_path),
                    "width": width,
                    "height": height,
                    "mode": mode,
                    "hash": img_hash,
                    "size": os.path.getsize(image_path)
                }
        except Exception as e:
            return {"error": f"分析图片失败: {str(e)}"}
    
    def _calculate_image_hash(self, image: Image.Image) -> str:
        """计算图片哈希值"""
        # 将图片转换为灰度并缩放到8x8
        img_gray = image.convert('L').resize((8, 8), Image.Resampling.LANCZOS)
        
        # 计算平均像素值
        pixels = list(img_gray.getdata())
        avg = sum(pixels) / len(pixels)
        
        # 生成哈希值
        hash_bits = []
        for pixel in pixels:
            hash_bits.append('1' if pixel > avg else '0')
        
        return ''.join(hash_bits)
    
    def search(self, query: str, max_results: int = 5, input_image_data: Optional[str] = None, route_decision: str = "PRODUCT_QUERY") -> List[Dict]:
        """
        多模态搜索：支持文字和图片搜索
        
        Args:
            query: 文字搜索查询
            max_results: 最大返回结果数
            input_image_data: 输入的图片数据（base64编码）
            route_decision: 路由决策（GENERAL_SERVICE/PRODUCT_QUERY）
            
        Returns:
            搜索结果列表
        """
        results = []
        
        # 根据路由决策选择搜索策略
        if route_decision == "GENERAL_SERVICE":
            # 通用客服问题：主要搜索客服问答库
            if query:
                text_results = self._search_text(query, max_results, route_decision)
                results.extend(text_results)
        else:
            # 产品问题：搜索所有知识库
            if query:
                text_results = self._search_text(query, max_results, route_decision)
                results.extend(text_results)
        
        # 图片搜索（两种类型都支持）
        if input_image_data:
            image_results = self._search_images(input_image_data, max_results)
            results.extend(image_results)
        
        # 按相关性排序并返回前N个结果
        results.sort(key=lambda x: x["relevance"], reverse=True)
        
        # 检查是否需要询问客户确认（通用策略）
        if results:
            best_result = results[0]
            if best_result["relevance"] < 0.9:  # 如果最佳匹配的相关度低于0.9（更宽松的猜测）
                # 根据路由决策生成不同的询问内容
                if route_decision == "PRODUCT_QUERY":
                    inquiry_content = "我找到了一些可能相关的产品信息，但不确定是否完全匹配您的问题。请问您是想了解以下产品吗？"
                    section_name = "产品确认"
                else:
                    inquiry_content = "我找到了一些可能相关的客服信息，但不确定是否完全匹配您的问题。请问您是想了解以下内容吗？"
                    section_name = "客服确认"
                
                # 添加询问结果
                inquiry_result = {
                    "type": "inquiry",
                    "content": inquiry_content,
                    "relevance": best_result["relevance"],
                    "source": "系统询问",
                    "section": section_name,
                    "best_match": best_result,
                    "all_matches": results[:3]  # 提供前3个可能的匹配
                }
                results.insert(0, inquiry_result)
        
        return results[:max_results]
    
    def _search_text(self, query: str, max_results: int, route_decision: str = "PRODUCT_QUERY") -> List[Dict]:
        """文字搜索"""
        results = []
        query_lower = query.lower()
        
        # 根据路由决策选择搜索内容
        if route_decision == "GENERAL_SERVICE":
            # 通用客服问题：主要搜索客服问答库
            if self.knowledge_content:
                paragraphs = self._split_into_paragraphs(self.knowledge_content)
                for i, paragraph in enumerate(paragraphs):
                    if len(paragraph.strip()) < 10:
                        continue
                        
                    relevance = self._calculate_relevance(query_lower, paragraph.lower())
                    
                    if relevance > 0.1:
                        results.append({
                            "content": paragraph.strip(),
                            "relevance": relevance,
                            "source": f"淘宝客服问答库第{i+1}段",
                            "section": self._get_section_name(paragraph),
                            "type": "text"
                        })
        else:
            # 产品问题：搜索客服问答库和产品内容
            # 1. 搜索客服问答库
            if self.knowledge_content:
                paragraphs = self._split_into_paragraphs(self.knowledge_content)
                for i, paragraph in enumerate(paragraphs):
                    if len(paragraph.strip()) < 10:
                        continue
                        
                    relevance = self._calculate_relevance(query_lower, paragraph.lower())
                    
                    if relevance > 0.1:
                        results.append({
                            "content": paragraph.strip(),
                            "relevance": relevance,
                            "source": f"淘宝客服问答库第{i+1}段",
                            "section": self._get_section_name(paragraph),
                            "type": "text"
                        })
            
            # 2. 搜索产品内容
            for product in self.products_content:
                if "product_info" in product:
                    product_name = product["product_info"].get("name", "")
                    product_desc = product["product_info"].get("description", "")
                    
                    # 搜索产品名称
                    if product_name:
                        relevance = self._calculate_relevance(query_lower, product_name.lower())
                        if relevance > 0.1:
                            results.append({
                                "content": f"产品名称：{product_name}",
                                "relevance": relevance,
                                "source": "产品库",
                                "section": "产品信息",
                                "type": "product"
                            })
                    
                    # 搜索产品描述
                    if product_desc:
                        relevance = self._calculate_relevance(query_lower, product_desc.lower())
                        if relevance > 0.1:
                            results.append({
                                "content": f"产品描述：{product_desc}",
                                "relevance": relevance,
                                "source": "产品库",
                                "section": "产品信息",
                                "type": "product"
                            })
        
        return results[:max_results]
    
    
    def _search_images(self, input_image_data: str, max_results: int) -> List[Dict]:
        """图片搜索"""
        try:
            # 解码输入图片
            input_image = self._decode_base64_image(input_image_data)
            if not input_image:
                return []
            
            # 计算输入图片的哈希值
            input_hash = self._calculate_image_hash(input_image)
            
            results = []
            
            # 搜索产品内容中的图片
            for product in self.products_content:
                if "images" in product and product["images"]:
                    for image_info in product["images"]:
                        image_filename = image_info.get("filename", "")
                        if image_filename and image_filename in self.image_database:
                            stored_image_info = self.image_database[image_filename]
                            if "error" not in stored_image_info:
                                # 计算图片相似度
                                similarity = self._calculate_image_similarity(input_hash, stored_image_info["hash"])
                                
                                if similarity > 0.7:
                                    results.append({
                                        "content": f"找到相似产品图片: {product['product_info']['name']}\n产品描述: {product['product_info']['description'][:200]}...",
                                        "relevance": similarity,
                                        "source": f"产品库: {product['product_info']['name']}",
                                        "section": "产品图片",
                                        "type": "product_image",
                                        "image_info": stored_image_info,
                                        "product_info": product['product_info']
                                    })
            
            return results[:max_results]
        except Exception as e:
            return [{"content": f"图片搜索失败: {str(e)}", "relevance": 0.0, "source": "错误", "type": "error"}]
    
    def _find_associated_product(self, image_filename: str) -> Optional[Dict]:
        """查找与图片关联的产品信息"""
        try:
            # 从产品内容中查找
            for product in self.products_content:
                if "images" in product and product["images"]:
                    for img in product["images"]:
                        if img.get("filename") == image_filename:
                            return product
            
            return None
        except Exception as e:
            print(f"查找关联产品失败: {str(e)}")
            return None
    
    def _decode_base64_image(self, image_data: str) -> Optional[Image.Image]:
        """解码base64图片数据"""
        try:
            # 移除data:image前缀（如果存在）
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            # 解码base64数据
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            return image
        except Exception as e:
            print(f"解码图片失败: {str(e)}")
            return None
    
    def _calculate_image_similarity(self, hash1: str, hash2: str) -> float:
        """计算两张图片的相似度"""
        if len(hash1) != len(hash2):
            return 0.0
        
        # 计算汉明距离
        hamming_distance = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
        
        # 转换为相似度分数（0-1）
        similarity = 1.0 - (hamming_distance / len(hash1))
        return similarity
    
    def _split_into_paragraphs(self, content: str) -> List[str]:
        """将内容分割成段落"""
        # 按双换行符分割
        paragraphs = re.split(r'\n\s*\n', content)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _calculate_relevance(self, query: str, content: str) -> float:
        """计算相关性分数（极宽松的匹配，只要有任何部分匹配就进行猜测）"""
        if not query or not content:
            return 0.0
        
        query_lower = query.lower()
        content_lower = content.lower()
        
        # 直接字符串匹配（最高分）
        if query_lower in content_lower:
            return 1.0
        
        # 部分字符串匹配（更宽松）
        query_words = query_lower.split()
        for word in query_words:
            if len(word) > 1 and word in content_lower:  # 降低到1个字符
                return 0.8
        
        # 词汇匹配（极宽松）
        query_words_set = set(query_lower.split())
        content_words_set = set(content_lower.split())
        
        if not query_words_set:
            return 0.0
        
        # 计算词汇重叠度（极低要求）
        overlap = len(query_words_set.intersection(content_words_set))
        if overlap > 0:
            # 只要有任何一个词匹配就给予基础分数
            relevance = overlap / len(query_words_set)
            # 最低给予0.2的基础分数，最高1.0
            return max(0.2, min(relevance, 1.0))
        
        # 极模糊匹配：检查是否有任何相似词汇
        for query_word in query_words_set:
            if len(query_word) > 1:  # 降低到1个字符
                for content_word in content_words_set:
                    if len(content_word) > 1:  # 降低到1个字符
                        # 简单的相似度检查（包含关系）
                        if query_word in content_word or content_word in query_word:
                            return 0.3
        
        # 字符级匹配：检查是否有任何字符序列匹配
        for query_word in query_words_set:
            if len(query_word) >= 2:
                for content_word in content_words_set:
                    if len(content_word) >= 2:
                        # 检查是否有2个字符以上的子串匹配
                        for i in range(len(query_word) - 1):
                            substring = query_word[i:i+2]
                            if substring in content_word:
                                return 0.2
        
        return 0.0
    
    def _get_section_name(self, paragraph: str) -> str:
        """获取段落所属的章节名称"""
        lines = paragraph.split('\n')
        for line in lines:
            if line.startswith('#'):
                return line.strip('#').strip()
        return "未分类"
    
    def get_all_content(self) -> str:
        """获取所有知识库内容"""
        return self.knowledge_content

# 全局多模态RAG检索器实例
rag_retriever = MultimodalRAGRetriever()
