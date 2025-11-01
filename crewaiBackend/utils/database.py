"""
MySQL database connection and operations
For managing persistent storage of chat sessions and messages
"""

import pymysql
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from ..config import Config

logger = logging.getLogger(__name__)


class DatabaseManager:
    """MySQL Database Manager"""
    
    def __init__(self):
        self.connection = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Connect to MySQL database"""
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
            logger.info("MySQL database connection successful")
        except Exception as e:
            logger.error(f"MySQL database connection failed: {e}")
            logger.warning("System will run in memory mode, session data will not be persisted")
            self.connection = None
    
    def _check_connection(self):
        """Check if database connection is valid, attempt reconnection if disconnected"""
        if not self.connection:
            logger.info("Database connection does not exist, attempting to reconnect...")
            self._connect()
            return self.connection is not None
        
        try:
            self.connection.ping(reconnect=True)
            return True
        except Exception as e:
            logger.warning(f"Database connection check failed: {e}, attempting to reconnect...")
            self._connect()
            return self.connection is not None
    
    def _create_tables(self):
        """Create database tables"""
        if not self.connection:
            logger.warning("Database connection unavailable, skipping table creation")
            return
            
        try:
            with self.connection.cursor() as cursor:
                # Create sessions table
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
                
                # Create messages table
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
                
                logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = None) -> Any:
        """Execute SQL query"""
        if not self._check_connection():
            logger.warning("Database connection unavailable, unable to execute query")
            return []
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            # Attempt reconnection
            self._connect()
            return []
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute SQL update operation"""
        if not self._check_connection():
            logger.warning("Database connection unavailable, unable to execute update")
            return 0
        try:
            with self.connection.cursor() as cursor:
                affected_rows = cursor.execute(query, params)
                return affected_rows
        except Exception as e:
            logger.error(f"Update execution failed: {e}")
            # Attempt reconnection
            self._connect()
            return 0
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("MySQL database connection closed")


# Global database manager instance
db_manager = DatabaseManager()
