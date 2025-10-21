"""
常量定义文件
集中管理所有常量
"""

# API相关常量
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2  # 重试延迟基数（秒）

# 数据库相关常量
DEFAULT_PAGE_SIZE = 20
MAX_MESSAGE_COUNT = 1000

# 会话相关常量
DEFAULT_SESSION_TITLE_LENGTH = 30
MAX_CONTEXT_MESSAGES = 10

# 日志相关常量
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 错误消息常量
ERROR_MESSAGES = {
    'SESSION_NOT_FOUND': '会话不存在',
    'INVALID_INPUT': '输入数据无效',
    'DATABASE_ERROR': '数据库操作失败',
    'RAGFLOW_ERROR': 'RAGFlow服务错误',
    'NETWORK_ERROR': '网络连接失败',
    'UNKNOWN_ERROR': '未知错误'
}

# 成功消息常量
SUCCESS_MESSAGES = {
    'SESSION_CREATED': '会话创建成功',
    'SESSION_DELETED': '会话删除成功',
    'SESSION_UPDATED': '会话更新成功',
    'MESSAGE_SAVED': '消息保存成功'
}
