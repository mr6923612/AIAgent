# -*- coding: utf-8 -*-
"""
RAGFlow Session Manager

Specifically responsible for managing RAGFlow session creation, mapping, and deletion
- Maintains one-to-one mapping from application session_id to RAGFlow session_id
- Provides RAGFlow session creation, retrieval, and deletion interfaces
- Loads existing mappings from database to ensure mappings are not lost after restart
"""

import logging
from typing import Dict, Optional
from .ragflow_client import create_ragflow_client, DEFAULT_CHAT_ID

logger = logging.getLogger(__name__)


class RAGFlowSessionManager:
    """RAGFlow Session Manager (Singleton Pattern)"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern: ensure only one global instance"""
        if cls._instance is None:
            cls._instance = super(RAGFlowSessionManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize manager"""
        # Avoid duplicate initialization
        if self._initialized:
            logger.info("[RAGFlow] Using existing RAGFlow session manager instance")
            return
        
        # RAGFlow session ID mapping: {app_session_id: RAGFlow session_id}
        self.session_mapping: Dict[str, str] = {}
        
        # Globally shared RAGFlow client
        self.ragflow_client = create_ragflow_client()
        
        # Load existing mappings from database
        self._load_mappings_from_database()
        
        logger.info(f"RAGFlow session manager initialized, loaded {len(self.session_mapping)} session mappings")
        
        # Clean up invalid RAGFlow sessions on startup
        self._cleanup_invalid_sessions()
        
        # Mark as initialized
        self._initialized = True
    
    def _load_mappings_from_database(self):
        """Load existing RAGFlow session mappings from database"""
        try:
            from .database import db_manager
            
            # Query all sessions with RAGFlow session ID
            query = """
                SELECT session_id, ragflow_session_id 
                FROM chat_sessions 
                WHERE ragflow_session_id IS NOT NULL
            """
            logger.info(f"[RAGFlow] Loading session mappings from database, SQL query: {query}")
            results = db_manager.execute_query(query)
            
            logger.info(f"[RAGFlow] Database query result type: {type(results)}, length: {len(results) if results else 'None'}")
            
            if results:
                for row in results:
                    app_session_id = row[0]
                    ragflow_session_id = row[1]
                    self.session_mapping[app_session_id] = ragflow_session_id
                    logger.info(f"[RAGFlow] Loaded mapping: {app_session_id[:8]} -> {ragflow_session_id[:8] if ragflow_session_id else 'None'}")
                
                logger.info(f"[RAGFlow] Loaded {len(results)} session mappings from database")
            else:
                logger.info("[RAGFlow] No existing session mappings in database")
                
        except Exception as e:
            logger.warning(f"[RAGFlow] Failed to load mappings from database (database may not be connected): {e}")
            import traceback
            logger.warning(f"[RAGFlow] Error stack: {traceback.format_exc()}")
    
    def get_or_create_session(self, app_session_id: str, session_name: str = None) -> Optional[str]:
        """
        Get or create RAGFlow session ID
        
        Args:
            app_session_id: Application session ID
            session_name: Session name (optional)
            
        Returns:
            RAGFlow session ID, returns None on failure
        """
        # 1. First check memory mapping
        if app_session_id in self.session_mapping:
            ragflow_session_id = self.session_mapping[app_session_id]
            logger.info(f"[RAGFlow] Reusing existing session from memory: {app_session_id[:8]} -> {ragflow_session_id[:8]}")
            return ragflow_session_id
        
        # 2. If not in memory, query database (handle post-restart scenario)
        try:
            from .database import db_manager
            query = "SELECT ragflow_session_id FROM chat_sessions WHERE session_id = %s AND ragflow_session_id IS NOT NULL"
            results = db_manager.execute_query(query, (app_session_id,))
            
            if results and len(results) > 0:
                ragflow_session_id = results[0][0]
                # Load mapping from database into memory
                self.session_mapping[app_session_id] = ragflow_session_id
                logger.info(f"[RAGFlow] Restored session mapping from database: {app_session_id[:8]} -> {ragflow_session_id[:8]}")
                return ragflow_session_id
        except Exception as e:
            logger.warning(f"[RAGFlow] Failed to query session mapping from database: {e}")
        
        # 3. If not in database either, create new RAGFlow session
        try:
            name = session_name or f"Session_{app_session_id[:8]}"
            logger.info(f"[RAGFlow] Creating new session: {app_session_id[:8]}")
            
            session_data = self.ragflow_client.create_session(
                chat_id=DEFAULT_CHAT_ID,
                name=name,
                user_id=f"user_{app_session_id}"
            )
            
            ragflow_session_id = session_data.get('id', '')
            
            if ragflow_session_id:
                # Establish mapping relationship
                self.session_mapping[app_session_id] = ragflow_session_id
                logger.info(f"[RAGFlow] Session created successfully: {app_session_id[:8]} -> {ragflow_session_id[:8]}")
                return ragflow_session_id
            else:
                logger.error(f"[RAGFlow] Session creation failed: no id in returned data")
                return None
                
        except Exception as e:
            logger.error(f"[RAGFlow] Session creation failed: {e}")
            return None
    
    def get_session_id(self, app_session_id: str) -> Optional[str]:
        """
        Get RAGFlow session ID (without creating new one)
        
        Args:
            app_session_id: Application session ID
            
        Returns:
            RAGFlow session ID, returns None if not found
        """
        return self.session_mapping.get(app_session_id)
    
    def delete_session(self, app_session_id: str) -> bool:
        """
        Delete RAGFlow session
        
        Args:
            app_session_id: Application session ID
            
        Returns:
            Whether deletion was successful
        """
        # Get RAGFlow session ID
        ragflow_session_id = self.session_mapping.get(app_session_id)
        
        if not ragflow_session_id:
            logger.warning(f"[RAGFlow] Session does not exist, no need to delete: {app_session_id[:8]}")
            return True  # Non-existence is considered success
        
        try:
            logger.info(f"[RAGFlow] Deleting session: {app_session_id[:8]} -> {ragflow_session_id[:8]}")
            
            self.ragflow_client.delete_session(
                chat_id=DEFAULT_CHAT_ID,
                session_id=ragflow_session_id
            )
            
            # Remove mapping relationship
            del self.session_mapping[app_session_id]
            
            logger.info(f"[RAGFlow] Session deleted successfully: {app_session_id[:8]}")
            return True
            
        except Exception as e:
            logger.error(f"[RAGFlow] Session deletion failed: {e}")
            # Even if deletion fails, remove mapping relationship
            if app_session_id in self.session_mapping:
                del self.session_mapping[app_session_id]
            return False
    
    def cleanup_all_sessions(self) -> int:
        """
        Clean up all RAGFlow sessions
        
        Returns:
            Number of sessions cleaned up
        """
        count = 0
        session_ids = list(self.session_mapping.keys())
        
        for app_session_id in session_ids:
            if self.delete_session(app_session_id):
                count += 1
        
        logger.info(f"[RAGFlow] Cleanup completed, deleted {count} sessions")
        return count
    
    def get_mapping_count(self) -> int:
        """Get current number of mapped sessions"""
        return len(self.session_mapping)
    
    def get_mappings(self) -> Dict[str, str]:
        """Get all mapping relationships"""
        return self.session_mapping.copy()
    
    def _cleanup_invalid_sessions(self):
        """
        Clean up invalid RAGFlow sessions on startup
        
        Cleanup strategy (bidirectional cleanup):
        1. Get all sessions from RAGFlow
        2. Get all session mappings from database
        3. Bidirectional cleanup:
           a) If ragflow_session_id in database doesn't exist in RAGFlow, clear database field
           b) If session_id in RAGFlow is not in database mappings, delete RAGFlow session
        """
        try:
            logger.info("[RAGFlow] Starting to clean up invalid sessions...")
            
            # Get all sessions from RAGFlow
            ragflow_sessions = self._get_all_ragflow_sessions()
            if ragflow_sessions is None:
                logger.warning("[RAGFlow] Unable to get RAGFlow session list, skipping cleanup")
                return
            
            ragflow_session_ids = set(ragflow_sessions.keys())
            logger.info(f"[RAGFlow] RAGFlow has {len(ragflow_session_ids)} sessions")
            
            from .database import db_manager
            
            # === Step 1: Get all ragflow_session_id from database ===
            query = """
                SELECT session_id, ragflow_session_id 
                FROM chat_sessions 
                WHERE ragflow_session_id IS NOT NULL
            """
            db_results = db_manager.execute_query(query)
            
            # Build database mapping: {ragflow_session_id: app_session_id}
            db_mapping = {}
            if db_results:
                for row in db_results:
                    app_session_id = row[0]
                    db_ragflow_session_id = row[1]
                    db_mapping[db_ragflow_session_id] = app_session_id
            
            db_ragflow_session_ids = set(db_mapping.keys())
            logger.info(f"[RAGFlow] Database has {len(db_ragflow_session_ids)} session mappings")
            
            # === Step 2: Clean up invalid mappings in database ===
            # If ragflow_session_id in database doesn't exist in RAGFlow, clear database field
            db_invalid_count = 0
            for db_ragflow_session_id, app_session_id in list(db_mapping.items()):
                if db_ragflow_session_id not in ragflow_session_ids:
                    # Clear ragflow_session_id in database
                    update_query = "UPDATE chat_sessions SET ragflow_session_id = NULL WHERE session_id = %s"
                    db_manager.execute_update(update_query, (app_session_id,))
                    
                    # Remove from memory mapping
                    if app_session_id in self.session_mapping:
                        del self.session_mapping[app_session_id]
                    
                    # Remove from db_ragflow_session_ids so this invalid session won't be protected
                    db_ragflow_session_ids.discard(db_ragflow_session_id)
                    
                    db_invalid_count += 1
                    logger.info(f"[RAGFlow] Cleaned invalid database mapping: {app_session_id[:8]} -> {db_ragflow_session_id[:8]}")
            
            # === Step 3: Clean up orphaned sessions in RAGFlow ===
            # Find sessions that exist in RAGFlow but have no database records (orphaned sessions)
            orphaned_sessions = ragflow_session_ids - db_ragflow_session_ids
            ragflow_deleted_count = 0
            
            if orphaned_sessions:
                logger.info(f"[RAGFlow] Found {len(orphaned_sessions)} orphaned sessions, preparing to delete...")
                for orphaned_session_id in orphaned_sessions:
                    try:
                        self.ragflow_client.delete_session(
                            chat_id=DEFAULT_CHAT_ID,
                            session_id=orphaned_session_id
                        )
                        ragflow_deleted_count += 1
                        logger.info(f"[RAGFlow] Deleted orphaned session: {orphaned_session_id[:8]}")
                    except Exception as e:
                        logger.warning(f"[RAGFlow] Failed to delete orphaned session {orphaned_session_id[:8]}: {e}")
            
            # === Summary ===
            total_cleaned = db_invalid_count + ragflow_deleted_count
            if total_cleaned > 0:
                logger.info(f"[RAGFlow] Cleanup completed, cleaned {total_cleaned} sessions (invalid database mappings:{db_invalid_count}, RAGFlow orphaned sessions:{ragflow_deleted_count})")
            else:
                logger.info(f"[RAGFlow] All sessions are valid, no cleanup needed (database:{len(db_ragflow_session_ids)}, RAGFlow:{len(ragflow_session_ids)})")
                
        except Exception as e:
            logger.warning(f"[RAGFlow] Failed to clean up invalid sessions: {e}")
    
    def _get_all_ragflow_sessions(self) -> Optional[Dict[str, dict]]:
        """
        Get all sessions from RAGFlow
        
        Returns:
            {session_id: session_data} dictionary, returns None on failure
        """
        try:
            # Call RAGFlow API to get sessions
            # Note: RAGFlow's list_sessions API requires chat_id
            response = self.ragflow_client.list_sessions(chat_id=DEFAULT_CHAT_ID)
            
            if not response:
                return {}
            
            # Build mapping from session_id to session_data
            session_dict = {}
            for session in response:
                session_id = session.get('id')
                if session_id:
                    session_dict[session_id] = session
            
            return session_dict
            
        except Exception as e:
            logger.error(f"[RAGFlow] Failed to get RAGFlow session list: {e}")
            return None


# Global RAGFlow session manager instance
ragflow_session_manager = RAGFlowSessionManager()
