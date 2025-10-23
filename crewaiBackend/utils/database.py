"""
MySQL数据库连接和操作
用于管理聊天会话和消息的持久化存储
"""

import pymysql
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from ..config import Config

logger = logging.getLogger(__name__)


class DatabaseManager:
    """MySQL数据库管理器"""
    
    def __init__(self):
        self.connection = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """连接到MySQL数据库"""
        try:
            self.connection = pymysql.connect(
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DATABASE,
                charset='utf8mb4',
                autocommit=True,
                connect_timeout=10,
                read_timeout=30,
                write_timeout=30
            )
            logger.info("MySQL数据库连接成功")
        except Exception as e:
            logger.error(f"MySQL数据库连接失败: {e}")
            logger.warning("系统将使用内存模式运行，会话数据不会持久化")
            self.connection = None
    
    def _check_connection(self):
        """检查数据库连接是否有效"""
        if not self.connection:
            return False
        try:
            self.connection.ping(reconnect=True)
            return True
        except Exception as e:
            logger.warning(f"数据库连接检查失败: {e}")
            self.connection = None
            return False
    
    def _create_tables(self):
        """创建数据库表"""
        if not self.connection:
            logger.warning("数据库连接不可用，跳过表创建")
            return
            
        try:
            with self.connection.cursor() as cursor:
                # 创建会话表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chat_sessions (
                        session_id VARCHAR(36) PRIMARY KEY,
                        user_id VARCHAR(100) NOT NULL DEFAULT 'anonymous',
                        title VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        context JSON,
                        ragflow_session_id VARCHAR(100) DEFAULT NULL,
                        INDEX idx_user_id (user_id),
                        INDEX idx_updated_at (updated_at),
                        INDEX idx_ragflow_session_id (ragflow_session_id)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                
                # 创建消息表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chat_messages (
                        id VARCHAR(36) PRIMARY KEY,
                        session_id VARCHAR(36) NOT NULL,
                        role ENUM('user', 'assistant') NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
                        INDEX idx_session_id (session_id),
                        INDEX idx_timestamp (timestamp)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                
                logger.info("数据库表创建成功")
        except Exception as e:
            logger.error(f"创建数据库表失败: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = None) -> Any:
        """执行SQL查询"""
        if not self._check_connection():
            logger.warning("数据库连接不可用，无法执行查询")
            return []
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"执行查询失败: {e}")
            # 尝试重连
            self._connect()
            return []
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """执行SQL更新操作"""
        if not self._check_connection():
            logger.warning("数据库连接不可用，无法执行更新")
            return 0
        try:
            with self.connection.cursor() as cursor:
                affected_rows = cursor.execute(query, params)
                return affected_rows
        except Exception as e:
            logger.error(f"执行更新失败: {e}")
            # 尝试重连
            self._connect()
            return 0
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            logger.info("MySQL数据库连接已关闭")


# 全局数据库管理器实例
db_manager = DatabaseManager()
