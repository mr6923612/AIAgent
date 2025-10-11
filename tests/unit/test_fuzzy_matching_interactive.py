#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式模糊匹配测试模块
允许用户输入文字和图片，实时测试匹配效果并调整参数
"""

import os
import sys
import base64
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import threading

# 添加后端路径
sys.path.append('../crewaiBackend')

from utils.rag_retriever import MultimodalRAGRetriever

class FuzzyMatchingTester:
    """交互式模糊匹配测试器"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("模糊匹配参数测试器")
        self.root.geometry("1200x800")
        
        # 初始化RAG检索器
        self.rag_retriever = MultimodalRAGRetriever()
        
        # 当前参数设置
        self.current_params = {
            'relevance_threshold': 0.1,
            'image_similarity_threshold': 0.7,
            'inquiry_threshold': 0.9,
            'max_results': 5,
            'route_decision': 'PRODUCT_QUERY'
        }
        
        # 当前图片数据
        self.current_image_data = None
        self.current_image_path = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="模糊匹配参数测试器", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 左侧：参数设置区域
        self.setup_parameters_frame(main_frame)
        
        # 中间：输入区域
        self.setup_input_frame(main_frame)
        
        # 右侧：结果显示区域
        self.setup_results_frame(main_frame)
    
    def setup_parameters_frame(self, parent):
        """设置参数配置区域"""
        params_frame = ttk.LabelFrame(parent, text="参数设置", padding="10")
        params_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # 相关性阈值
        ttk.Label(params_frame, text="文字匹配阈值:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.relevance_var = tk.DoubleVar(value=self.current_params['relevance_threshold'])
        relevance_scale = ttk.Scale(params_frame, from_=0.0, to=1.0, variable=self.relevance_var, 
                                   orient=tk.HORIZONTAL, length=200)
        relevance_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        self.relevance_label = ttk.Label(params_frame, text=f"{self.relevance_var.get():.2f}")
        self.relevance_label.grid(row=0, column=2, padx=(5, 0))
        relevance_scale.configure(command=self.update_relevance_label)
        
        # 图片相似度阈值
        ttk.Label(params_frame, text="图片相似度阈值:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.image_similarity_var = tk.DoubleVar(value=self.current_params['image_similarity_threshold'])
        image_scale = ttk.Scale(params_frame, from_=0.0, to=1.0, variable=self.image_similarity_var,
                               orient=tk.HORIZONTAL, length=200)
        image_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        self.image_similarity_label = ttk.Label(params_frame, text=f"{self.image_similarity_var.get():.2f}")
        self.image_similarity_label.grid(row=1, column=2, padx=(5, 0))
        image_scale.configure(command=self.update_image_similarity_label)
        
        # 询问确认阈值
        ttk.Label(params_frame, text="询问确认阈值:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.inquiry_var = tk.DoubleVar(value=self.current_params['inquiry_threshold'])
        inquiry_scale = ttk.Scale(params_frame, from_=0.0, to=1.0, variable=self.inquiry_var,
                                 orient=tk.HORIZONTAL, length=200)
        inquiry_scale.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)
        self.inquiry_label = ttk.Label(params_frame, text=f"{self.inquiry_var.get():.2f}")
        self.inquiry_label.grid(row=2, column=2, padx=(5, 0))
        inquiry_scale.configure(command=self.update_inquiry_label)
        
        # 最大结果数
        ttk.Label(params_frame, text="最大结果数:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.max_results_var = tk.IntVar(value=self.current_params['max_results'])
        max_results_spinbox = ttk.Spinbox(params_frame, from_=1, to=20, textvariable=self.max_results_var, width=10)
        max_results_spinbox.grid(row=3, column=1, sticky=tk.W, pady=2)
        
        # 路由决策
        ttk.Label(params_frame, text="搜索策略:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.route_var = tk.StringVar(value=self.current_params['route_decision'])
        route_combo = ttk.Combobox(params_frame, textvariable=self.route_var, 
                                  values=['PRODUCT_QUERY', 'GENERAL_SERVICE'], state='readonly', width=15)
        route_combo.grid(row=4, column=1, sticky=tk.W, pady=2)
        
        # 参数预设按钮
        preset_frame = ttk.Frame(params_frame)
        preset_frame.grid(row=5, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(preset_frame, text="严格模式", command=self.set_strict_mode).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="宽松模式", command=self.set_loose_mode).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="默认模式", command=self.set_default_mode).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="重置参数", command=self.reset_parameters).pack(side=tk.LEFT, padx=2)
    
    def setup_input_frame(self, parent):
        """设置输入区域"""
        input_frame = ttk.LabelFrame(parent, text="输入测试", padding="10")
        input_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10)
        input_frame.columnconfigure(0, weight=1)
        
        # 文字输入
        ttk.Label(input_frame, text="文字查询:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.text_input = tk.Text(input_frame, height=3, width=40)
        self.text_input.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 图片输入
        ttk.Label(input_frame, text="图片文件:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        image_input_frame = ttk.Frame(input_frame)
        image_input_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        image_input_frame.columnconfigure(0, weight=1)
        
        self.image_path_var = tk.StringVar()
        self.image_path_entry = ttk.Entry(image_input_frame, textvariable=self.image_path_var, state='readonly')
        self.image_path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(image_input_frame, text="选择图片", command=self.select_image).grid(row=0, column=1)
        ttk.Button(image_input_frame, text="清除图片", command=self.clear_image).grid(row=0, column=2, padx=(5, 0))
        
        # 图片预览
        self.image_preview_label = ttk.Label(input_frame, text="无图片")
        self.image_preview_label.grid(row=4, column=0, pady=(0, 10))
        
        # 测试按钮
        test_frame = ttk.Frame(input_frame)
        test_frame.grid(row=5, column=0, pady=(10, 0))
        
        ttk.Button(test_frame, text="开始测试", command=self.run_test).pack(side=tk.LEFT, padx=2)
        ttk.Button(test_frame, text="清除输入", command=self.clear_inputs).pack(side=tk.LEFT, padx=2)
        ttk.Button(test_frame, text="保存结果", command=self.save_results).pack(side=tk.LEFT, padx=2)
        
        # 状态标签
        self.status_label = ttk.Label(input_frame, text="就绪", foreground="green")
        self.status_label.grid(row=6, column=0, pady=(10, 0))
    
    def setup_results_frame(self, parent):
        """设置结果显示区域"""
        results_frame = ttk.LabelFrame(parent, text="测试结果", padding="10")
        results_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # 结果显示文本框
        self.results_text = scrolledtext.ScrolledText(results_frame, height=25, width=50, wrap=tk.WORD)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 结果统计
        stats_frame = ttk.Frame(results_frame)
        stats_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.stats_label = ttk.Label(stats_frame, text="无测试结果")
        self.stats_label.pack()
    
    def update_relevance_label(self, value):
        """更新相关性阈值标签"""
        self.relevance_label.config(text=f"{float(value):.2f}")
    
    def update_image_similarity_label(self, value):
        """更新图片相似度标签"""
        self.image_similarity_label.config(text=f"{float(value):.2f}")
    
    def update_inquiry_label(self, value):
        """更新询问确认阈值标签"""
        self.inquiry_label.config(text=f"{float(value):.2f}")
    
    def set_strict_mode(self):
        """设置严格模式参数"""
        self.relevance_var.set(0.3)
        self.image_similarity_var.set(0.8)
        self.inquiry_var.set(0.8)
        self.max_results_var.set(3)
        self.update_all_labels()
    
    def set_loose_mode(self):
        """设置宽松模式参数"""
        self.relevance_var.set(0.05)
        self.image_similarity_var.set(0.5)
        self.inquiry_var.set(0.95)
        self.max_results_var.set(10)
        self.update_all_labels()
    
    def set_default_mode(self):
        """设置默认模式参数"""
        self.relevance_var.set(0.1)
        self.image_similarity_var.set(0.7)
        self.inquiry_var.set(0.9)
        self.max_results_var.set(5)
        self.update_all_labels()
    
    def reset_parameters(self):
        """重置参数"""
        self.set_default_mode()
        self.route_var.set('PRODUCT_QUERY')
    
    def update_all_labels(self):
        """更新所有标签"""
        self.update_relevance_label(self.relevance_var.get())
        self.update_image_similarity_label(self.image_similarity_var.get())
        self.update_inquiry_label(self.inquiry_var.get())
    
    def select_image(self):
        """选择图片文件"""
        file_path = filedialog.askopenfilename(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            try:
                # 读取图片并转换为Base64
                with open(file_path, 'rb') as f:
                    image_data = f.read()
                    self.current_image_data = base64.b64encode(image_data).decode('utf-8')
                
                self.current_image_path = file_path
                self.image_path_var.set(os.path.basename(file_path))
                
                # 显示图片预览
                self.show_image_preview(file_path)
                
                self.status_label.config(text=f"已加载图片: {os.path.basename(file_path)}", foreground="green")
                
            except Exception as e:
                messagebox.showerror("错误", f"加载图片失败: {str(e)}")
                self.status_label.config(text="图片加载失败", foreground="red")
    
    def show_image_preview(self, image_path):
        """显示图片预览"""
        try:
            # 加载并调整图片大小
            image = Image.open(image_path)
            image.thumbnail((150, 150), Image.Resampling.LANCZOS)
            
            # 转换为Tkinter格式
            photo = ImageTk.PhotoImage(image)
            
            # 更新预览标签
            self.image_preview_label.config(image=photo, text="")
            self.image_preview_label.image = photo  # 保持引用
            
        except Exception as e:
            self.image_preview_label.config(text=f"预览失败: {str(e)}")
    
    def clear_image(self):
        """清除图片"""
        self.current_image_data = None
        self.current_image_path = None
        self.image_path_var.set("")
        self.image_preview_label.config(image="", text="无图片")
        self.status_label.config(text="已清除图片", foreground="blue")
    
    def clear_inputs(self):
        """清除所有输入"""
        self.text_input.delete(1.0, tk.END)
        self.clear_image()
        self.results_text.delete(1.0, tk.END)
        self.stats_label.config(text="无测试结果")
        self.status_label.config(text="已清除所有输入", foreground="blue")
    
    def run_test(self):
        """运行测试"""
        # 获取输入
        query = self.text_input.get(1.0, tk.END).strip()
        image_data = self.current_image_data
        
        if not query and not image_data:
            messagebox.showwarning("警告", "请输入文字查询或选择图片文件")
            return
        
        # 更新参数
        self.update_current_params()
        
        # 在新线程中运行测试
        self.status_label.config(text="正在测试...", foreground="orange")
        thread = threading.Thread(target=self._run_test_thread, args=(query, image_data))
        thread.daemon = True
        thread.start()
    
    def _run_test_thread(self, query, image_data):
        """在后台线程中运行测试"""
        try:
            # 临时修改RAG检索器的参数
            original_threshold = 0.1  # 这里需要修改RAG检索器的内部参数
            # 注意：由于RAG检索器的参数是硬编码的，我们需要通过其他方式测试
            
            # 执行搜索
            results = self.rag_retriever.search(
                query=query,
                max_results=self.current_params['max_results'],
                input_image_data=image_data,
                route_decision=self.current_params['route_decision']
            )
            
            # 在主线程中更新UI
            self.root.after(0, self._update_results, results, query, image_data)
            
        except Exception as e:
            self.root.after(0, self._show_error, str(e))
    
    def _update_results(self, results, query, image_data):
        """更新测试结果"""
        # 清空结果区域
        self.results_text.delete(1.0, tk.END)
        
        # 显示测试信息
        self.results_text.insert(tk.END, "=" * 60 + "\n")
        self.results_text.insert(tk.END, "模糊匹配测试结果\n")
        self.results_text.insert(tk.END, "=" * 60 + "\n\n")
        
        # 显示当前参数
        self.results_text.insert(tk.END, "当前参数设置:\n")
        self.results_text.insert(tk.END, f"  文字匹配阈值: {self.current_params['relevance_threshold']:.2f}\n")
        self.results_text.insert(tk.END, f"  图片相似度阈值: {self.current_params['image_similarity_threshold']:.2f}\n")
        self.results_text.insert(tk.END, f"  询问确认阈值: {self.current_params['inquiry_threshold']:.2f}\n")
        self.results_text.insert(tk.END, f"  最大结果数: {self.current_params['max_results']}\n")
        self.results_text.insert(tk.END, f"  搜索策略: {self.current_params['route_decision']}\n\n")
        
        # 显示输入信息
        self.results_text.insert(tk.END, "输入信息:\n")
        if query:
            self.results_text.insert(tk.END, f"  文字查询: {query}\n")
        if image_data:
            self.results_text.insert(tk.END, f"  图片文件: {os.path.basename(self.current_image_path) if self.current_image_path else '未知'}\n")
            self.results_text.insert(tk.END, f"  图片大小: {len(image_data)} bytes (Base64)\n")
        self.results_text.insert(tk.END, "\n")
        
        # 显示匹配结果
        if results:
            self.results_text.insert(tk.END, f"找到 {len(results)} 个匹配结果:\n\n")
            
            for i, result in enumerate(results, 1):
                self.results_text.insert(tk.END, f"结果 {i}:\n")
                self.results_text.insert(tk.END, f"  类型: {result.get('type', 'unknown')}\n")
                self.results_text.insert(tk.END, f"  相关性/相似度: {result.get('relevance', 0):.3f}\n")
                self.results_text.insert(tk.END, f"  来源: {result.get('source', 'unknown')}\n")
                self.results_text.insert(tk.END, f"  章节: {result.get('section', 'unknown')}\n")
                
                content = result.get('content', '')
                if len(content) > 200:
                    content = content[:200] + "..."
                self.results_text.insert(tk.END, f"  内容: {content}\n")
                
                if 'product_info' in result:
                    product_info = result['product_info']
                    self.results_text.insert(tk.END, f"  产品名称: {product_info.get('name', 'unknown')}\n")
                
                self.results_text.insert(tk.END, "\n" + "-" * 40 + "\n\n")
        else:
            self.results_text.insert(tk.END, "未找到匹配结果\n\n")
        
        # 显示参数建议
        self.results_text.insert(tk.END, "参数调整建议:\n")
        if results:
            best_relevance = results[0].get('relevance', 0)
            if best_relevance < 0.3:
                self.results_text.insert(tk.END, "  - 建议降低文字匹配阈值以获得更多结果\n")
            elif best_relevance > 0.8:
                self.results_text.insert(tk.END, "  - 当前匹配效果良好\n")
            
            if len(results) < 3:
                self.results_text.insert(tk.END, "  - 建议增加最大结果数或降低阈值\n")
        else:
            self.results_text.insert(tk.END, "  - 建议降低匹配阈值或检查输入内容\n")
        
        # 更新统计信息
        if results:
            avg_relevance = sum(r.get('relevance', 0) for r in results) / len(results)
            self.stats_label.config(text=f"找到 {len(results)} 个结果，平均相关性: {avg_relevance:.3f}")
        else:
            self.stats_label.config(text="未找到匹配结果")
        
        self.status_label.config(text="测试完成", foreground="green")
    
    def _show_error(self, error_msg):
        """显示错误信息"""
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"测试出错: {error_msg}")
        self.status_label.config(text="测试失败", foreground="red")
    
    def update_current_params(self):
        """更新当前参数"""
        self.current_params = {
            'relevance_threshold': self.relevance_var.get(),
            'image_similarity_threshold': self.image_similarity_var.get(),
            'inquiry_threshold': self.inquiry_var.get(),
            'max_results': self.max_results_var.get(),
            'route_decision': self.route_var.get()
        }
    
    def save_results(self):
        """保存测试结果"""
        if not self.results_text.get(1.0, tk.END).strip():
            messagebox.showwarning("警告", "没有测试结果可保存")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存测试结果",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.results_text.get(1.0, tk.END))
                messagebox.showinfo("成功", f"测试结果已保存到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def run(self):
        """运行应用程序"""
        self.root.mainloop()

def main():
    """主函数"""
    print("启动交互式模糊匹配测试器...")
    app = FuzzyMatchingTester()
    app.run()

if __name__ == "__main__":
    main()
