"""
日志配置模块
提供统一的日志配置和管理
"""

import logging
import os
from datetime import datetime

# 导入配置
try:
    from config import config
    LOG_LEVEL = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    LOG_FORMAT = config.LOG_FORMAT
except ImportError:
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def setup_logging():
    """设置日志配置"""
    # 创建logs目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 生成日志文件名
    log_filename = f"{log_dir}/app_{datetime.now().strftime('%Y%m%d')}.log"
    
    # 配置日志
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # 同时输出到控制台
        ]
    )
    
    # 设置第三方库的日志级别
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('langchain').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)


def get_logger(name: str = None):
    """获取日志记录器"""
    return logging.getLogger(name or __name__)
