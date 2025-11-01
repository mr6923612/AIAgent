"""
Session Manager
For managing chat sessions and context records
Uses MySQL database for persistent storage
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import uuid4
from .database import db_manager

logger = logging.getLogger(__name__)


class ChatMessage:
    """Chat message class"""
    
    def __init__(self, role: str, content: str, timestamp: datetime = None):
        self.role = role  # 'user' or 'assistant'
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.id = str(uuid4())
    
    def to_dict(self):
        return {
            'id': self.id,
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        message = cls(
            role=data['role'],
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )
        message.id = data['id']
        return message


class ChatSession:
    """Chat session class"""
    
    def __init__(self, session_id: str = None, user_id: str = None, title: str = None, ragflow_session_id: str = None):
        self.session_id = session_id or str(uuid4())
        self.user_id = user_id or "anonymous"
        self.title = title or f"Chat Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.messages: List[ChatMessage] = []
        self.context = {}  # Store context information
        self.ragflow_session_id = ragflow_session_id  # RAGFlow session ID
    
    def add_message(self, role: str, content: str):
        """Add message to session"""
        message = ChatMessage(role, content)
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
    
    def get_context_summary(self, max_messages: int = 10) -> str:
        """Get context summary"""
        if not self.messages:
            return ""
        
        recent_messages = self.messages[-max_messages:]
        context_parts = []
        
        for msg in recent_messages:
            role_name = "User" if msg.role == "user" else "Assistant"
            context_parts.append(f"{role_name}: {msg.content}")
        
        return "\n".join(context_parts)
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'title': self.title,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'messages': [msg.to_dict() for msg in self.messages],
            'message_count': len(self.messages),
            'context': self.context,
            'ragflow_session_id': self.ragflow_session_id
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        session = cls(
            session_id=data['session_id'],
            user_id=data['user_id'],
            title=data['title'],
            ragflow_session_id=data.get('ragflow_session_id')
        )
        session.created_at = datetime.fromisoformat(data['created_at'])
        session.updated_at = datetime.fromisoformat(data['updated_at'])
        session.messages = [ChatMessage.from_dict(msg) for msg in data['messages']]
        session.context = data.get('context', {})
        return session


class SessionManager:
    """Session Manager"""

    def __init__(self):
        self.db = db_manager
        logger.info("Session manager initialized")

    def create_session(self, user_id: str = None, title: str = None) -> ChatSession:
        """
        Create new session (only create database record)
        Note: RAGFlow session creation is automatically handled by session_agent_manager on first conversation
        """
        session_id = str(uuid4())
        user_id = user_id or "anonymous"
        title = title or f"Chat Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        try:
            # Insert session into database (ragflow_session_id is NULL initially, managed by agent later)
            query = """
                INSERT INTO chat_sessions (session_id, user_id, title, context, ragflow_session_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (session_id, user_id, title, json.dumps({}), None)
            self.db.execute_update(query, params)
            
            # Create session object
            session = ChatSession(session_id=session_id, user_id=user_id, title=title, ragflow_session_id=None)
            logger.info(f"Created new session: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get session"""
        try:
            # Query session information
            session_query = "SELECT * FROM chat_sessions WHERE session_id = %s"
            session_data = self.db.execute_query(session_query, (session_id,))
            
            if not session_data:
                return None
            
            session_row = session_data[0]
            session = ChatSession(
                session_id=session_row[0],
                user_id=session_row[1],
                title=session_row[2],
                ragflow_session_id=session_row[6] if len(session_row) > 6 else None
            )
            session.created_at = session_row[3]
            session.updated_at = session_row[4]
            session.context = json.loads(session_row[5]) if session_row[5] else {}
            
            # Query messages
            messages_query = """
                SELECT id, role, content, timestamp 
                FROM chat_messages 
                WHERE session_id = %s 
                ORDER BY timestamp ASC
            """
            messages_data = self.db.execute_query(messages_query, (session_id,))
            
            for msg_row in messages_data:
                message = ChatMessage(
                    role=msg_row[1],
                    content=msg_row[2],
                    timestamp=msg_row[3]
                )
                message.id = msg_row[0]
                session.messages.append(message)
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to get session: {e}")
            return None

    def get_user_sessions(self, user_id: str) -> List[ChatSession]:
        """Get all sessions for a user"""
        try:
            query = """
                SELECT session_id FROM chat_sessions 
                WHERE user_id = %s 
                ORDER BY updated_at DESC
            """
            sessions_data = self.db.execute_query(query, (user_id,))
            
            sessions = []
            for row in sessions_data:
                session = self.get_session(row[0])
                if session:
                    sessions.append(session)
            
            return sessions
            
        except Exception as e:
            logger.error(f"Failed to get user sessions: {e}")
            return []

    def add_message(self, session_id: str, role: str, content: str) -> Optional[ChatMessage]:
        """Add message to session"""
        try:
            message_id = str(uuid4())
            
            # Insert message into database
            query = """
                INSERT INTO chat_messages (id, session_id, role, content)
                VALUES (%s, %s, %s, %s)
            """
            params = (message_id, session_id, role, content)
            self.db.execute_update(query, params)
            
            # If it's the first user message, automatically update session title
            if role == 'user':
                # Check if it's the first user message
                count_query = """
                    SELECT COUNT(*) FROM chat_messages 
                    WHERE session_id = %s AND role = 'user'
                """
                count_result = self.db.execute_query(count_query, (session_id,))
                if count_result and count_result[0][0] == 1:  # First user message
                    # Generate title based on content (truncate to first 30 characters)
                    new_title = content[:30] + ('...' if len(content) > 30 else '')
                    title_update_query = "UPDATE chat_sessions SET title = %s WHERE session_id = %s"
                    self.db.execute_update(title_update_query, (new_title, session_id))
            
            # Update session's update time
            update_query = "UPDATE chat_sessions SET updated_at = NOW() WHERE session_id = %s"
            self.db.execute_update(update_query, (session_id,))
            
            # Create message object
            message = ChatMessage(role, content)
            message.id = message_id
            
            logger.info(f"Added message to session {session_id}: {role}")
            return message
            
        except Exception as e:
            logger.error(f"Failed to add message: {e}")
            return None

    def update_session_title(self, session_id: str, title: str):
        """Update session title"""
        try:
            query = "UPDATE chat_sessions SET title = %s, updated_at = NOW() WHERE session_id = %s"
            self.db.execute_update(query, (title, session_id))
            logger.info(f"Updated session title: {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to update session title: {e}")

    def delete_session(self, session_id: str) -> bool:
        """
        Delete session (only delete database record)
        Note: RAGFlow session deletion is handled by session_agent_manager
        """
        try:
            # Delete local session (due to foreign key constraints, deleting session will automatically delete related messages)
            query = "DELETE FROM chat_sessions WHERE session_id = %s"
            affected_rows = self.db.execute_update(query, (session_id,))
            
            if affected_rows > 0:
                logger.info(f"Deleted local session: {session_id}")
                return True
            else:
                logger.warning(f"Session does not exist: {session_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return False

    def get_all_sessions(self) -> List[ChatSession]:
        """Get all sessions"""
        try:
            query = "SELECT session_id FROM chat_sessions ORDER BY updated_at DESC"
            sessions_data = self.db.execute_query(query)
            
            sessions = []
            for row in sessions_data:
                session = self.get_session(row[0])
                if session:
                    sessions.append(session)
            
            return sessions
            
        except Exception as e:
            logger.error(f"Failed to get all sessions: {e}")
            return []

    def cleanup_old_sessions(self, days: int = 30):
        """
        Clean up old sessions
        Note: This method only cleans up database records, not Agents
        To clean up Agents, call session_agent_manager.cleanup_inactive_sessions()
        """
        try:
            # First get session IDs to delete
            select_query = "SELECT session_id FROM chat_sessions WHERE updated_at < DATE_SUB(NOW(), INTERVAL %s DAY)"
            old_sessions = self.db.execute_query(select_query, (days,))
            
            if not old_sessions:
                logger.info("No old sessions to clean up")
                return
            
            # Delete database records
            delete_query = "DELETE FROM chat_sessions WHERE updated_at < DATE_SUB(NOW(), INTERVAL %s DAY)"
            affected_rows = self.db.execute_update(delete_query, (days,))
            logger.info(f"Cleaned up {affected_rows} old sessions (database records)")
            
        except Exception as e:
            logger.error(f"Failed to clean up old sessions: {e}")
