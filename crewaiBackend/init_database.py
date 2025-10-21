#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建MySQL数据库和表结构
"""

import pymysql
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config


def create_database():
    """创建数据库"""
    try:
        # 连接到MySQL服务器（不指定数据库）
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"数据库 {Config.MYSQL_DATABASE} 创建成功")
            
        connection.close()
        
    except Exception as e:
        print(f"创建数据库失败: {e}")
        sys.exit(1)


def create_tables():
    """创建表结构"""
    try:
        # 连接到指定数据库
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 创建会话表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    session_id VARCHAR(36) PRIMARY KEY,
                    user_id VARCHAR(100) NOT NULL DEFAULT 'anonymous',
                    title VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    context JSON,
                    INDEX idx_user_id (user_id),
                    INDEX idx_updated_at (updated_at)
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
            
            print("数据库表创建成功")
            
        connection.close()
        
    except Exception as e:
        print(f"创建表失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    print("开始初始化MySQL数据库...")
    
    # 检查配置
    if Config.MYSQL_PASSWORD == "your_mysql_password_here":
        print("错误: 请在config.py中设置正确的MySQL密码")
        sys.exit(1)
    
    # 创建数据库
    create_database()
    
    # 创建表
    create_tables()
    
    print("数据库初始化完成！")


if __name__ == "__main__":
    main()
