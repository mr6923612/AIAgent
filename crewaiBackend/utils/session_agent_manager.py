# -*- coding: utf-8 -*-
"""
Session Agent Manager

Architecture:
- RAGFlow and SQL are started at program startup, globally shared
- Agent is created on first conversation of session, released when session is deleted
- Reuse Agent when session exists to avoid duplicate creation

Session ID mapping:
- One application session_id corresponds to one RAGFlow session_id (one-to-one mapping)
- RAGFlow session is automatically created by SessionAgent on first conversation
- When application session is deleted, corresponding RAGFlow session is automatically deleted

Lifecycle management:
1. Create session: Only create database record, do not create RAGFlow session
2. First conversation: Create SessionAgent, automatically create RAGFlow session
3. Subsequent conversations: Reuse existing SessionAgent and RAGFlow session
4. Delete session: First release Agent (delete RAGFlow session), then delete database record
5. Clean up inactive sessions: Automatically release Agent and delete RAGFlow session
"""

import threading
from typing import Dict, Optional
from datetime import datetime
import logging

from crewai import Agent, Crew, Process
from .myLLM import my_llm
from .ragflow_session_manager import ragflow_session_manager

logger = logging.getLogger(__name__)

class SessionAgentManager:
    """Session Agent Manager"""
    
    def __init__(self):
        """Initialize manager"""
        self.session_agents: Dict[str, 'SessionAgent'] = {}
        self.lock = threading.Lock()
        
        # Globally shared resources (created at program startup)
        self.shared_llm = None
        self._init_shared_resources()
    
    def _init_shared_resources(self):
        """Initialize globally shared resources"""
        try:
            # Create shared LLM instance
            self.shared_llm = my_llm("google")
            logger.info("Global LLM instance created successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize global resources: {e}")
            raise
    
    def get_or_create_agent(self, session_id: str) -> 'SessionAgent':
        """
        Get or create session Agent
        
        Args:
            session_id: Session ID
            
        Returns:
            SessionAgent instance
        """
        with self.lock:
            # Check if Agent already exists for this session
            if session_id in self.session_agents:
                agent = self.session_agents[session_id]
                agent.update_last_used()
                logger.info(f"🔄 Reusing Agent for session {session_id}")
                return agent
            
            # Create new Agent
            agent = SessionAgent(
                session_id=session_id,
                llm=self.shared_llm
            )
            
            self.session_agents[session_id] = agent
            logger.info(f"🆕 Created new Agent for session {session_id}, current session count: {len(self.session_agents)}")
            return agent
    
    def release_agent(self, session_id: str):
        """
        Release session Agent, simultaneously delete corresponding RAGFlow session
        
        Args:
            session_id: Session ID
        """
        with self.lock:
            if session_id in self.session_agents:
                agent = self.session_agents[session_id]
                
                # Clean up resources (including deleting RAGFlow session)
                agent.cleanup()
                
                # Remove from dictionary
                del self.session_agents[session_id]
                logger.info(f"Released Agent for session {session_id}, current session count: {len(self.session_agents)}")
            else:
                logger.warning(f"Attempting to release non-existent session {session_id}")
    
    def get_session_status(self) -> Dict:
        """Get all session status"""
        with self.lock:
            return {
                'total_sessions': len(self.session_agents),
                'sessions': list(self.session_agents.keys()),
                'session_details': {
                    session_id: {
                        'created_at': agent.created_at.isoformat(),
                        'last_used': agent.last_used.isoformat(),
                        'age_seconds': (datetime.now() - agent.created_at).total_seconds()
                    }
                    for session_id, agent in self.session_agents.items()
                }
            }
    
    def cleanup_inactive_sessions(self, max_age_seconds: int = 1800):
        """
        Clean up inactive sessions, simultaneously delete corresponding RAGFlow sessions
        
        Args:
            max_age_seconds: Maximum inactive time (seconds)
        """
        with self.lock:
            now = datetime.now()
            inactive_sessions = [
                (session_id, agent) for session_id, agent in self.session_agents.items()
                if (now - agent.last_used).total_seconds() > max_age_seconds
            ]
            
            for session_id, agent in inactive_sessions:
                # Clean up resources (including deleting RAGFlow session)
                agent.cleanup()
                
                # Remove from dictionary
                del self.session_agents[session_id]
                logger.info(f"Cleaned up inactive session {session_id}")
            
            if inactive_sessions:
                logger.info(f"Cleanup completed, released {len(inactive_sessions)} inactive sessions")


class SessionAgent:
    """Session Agent instance"""
    
    def __init__(self, session_id: str, llm):
        self.session_id = session_id
        self.llm = llm
        self.created_at = datetime.now()
        self.last_used = datetime.now()
        
        # Create a shared Crew helper instance (for reusing definitions from crew.py)
        from ..crew import CrewtestprojectCrew
        self._crew_helper = CrewtestprojectCrew(job_id="temp", llm=self.llm)
        
        # Create Agent (only create once)
        self.agents = self._create_agents()
        self.crew = self._create_crew()
    
    def update_last_used(self):
        """Update last used time"""
        self.last_used = datetime.now()
    
    def _create_agents(self):
        """Create Agent (reuse definitions from crew.py)"""
        # Use shared crew helper instance
        agents_dict = self._crew_helper.create_agents()
        return agents_dict
    
    def _create_crew(self):
        """Create Crew (reuse definitions from crew.py)"""
        # Use create_crew method from crew.py
        return self._crew_helper.create_crew(
            agents=self.agents,
            tasks=[]  # Tasks are dynamically created at kickoff
        )
    
    def kickoff(self, inputs):
        """Execute task"""
        # Update usage time
        self.update_last_used()
        
        # Dynamically create tasks
        tasks = self._create_tasks(inputs)
        
        # Update Crew's tasks
        self.crew.tasks = tasks
        
        # Execute task
        return self.crew.kickoff()
    
    def _create_tasks(self, inputs):
        """Dynamically create tasks based on inputs (reuse definitions from crew.py)"""
        from crewai import Task
        
        # Import class from crew.py
        from ..crew import CrewtestprojectCrew
        
        # Ensure RAGFlow session_id is created and updated to database
        session_id = inputs.get('session_id', '')
        ragflow_session_id = None
        
        if session_id:
            # Use ragflow_session_manager to get or create RAGFlow session ID
            ragflow_session_id = ragflow_session_manager.get_or_create_session(session_id)
            
            # Update ragflow_session_id in database
            if ragflow_session_id:
                try:
                    from ..utils.sessionManager import SessionManager
                    session_manager = SessionManager()
                    session = session_manager.get_session(session_id)
                    
                    # Check if ragflow_session_id in database matches the one in memory
                    db_ragflow_session_id = session.ragflow_session_id if session else None
                    
                    if db_ragflow_session_id != ragflow_session_id:
                        # Update database record (update whether new or inconsistent)
                        from ..utils.database import db_manager
                        query = "UPDATE chat_sessions SET ragflow_session_id = %s WHERE session_id = %s"
                        db_manager.execute_update(query, (ragflow_session_id, session_id))
                        logger.info(f"[Session:{session_id[:8]}] Updated RAGFlow session_id to database: {ragflow_session_id[:8]}")
                    
                    # Pass ragflow_session_id directly to inputs to avoid import issues in crew.py
                    inputs = inputs.copy()  # Avoid modifying original inputs
                    inputs['ragflow_session_id'] = ragflow_session_id
                    logger.info(f"[Session:{session_id[:8]}] Passing RAGFlow session_id to task: {ragflow_session_id[:8]}")
                    
                except Exception as e:
                    logger.warning(f"[Session:{session_id[:8]}] Failed to update RAGFlow session_id to database: {e}")
        
        # Use shared crew helper to create tasks
        tasks = self._crew_helper.create_tasks(self.agents, inputs)
        
        return tasks
    
    def cleanup(self):
        """
        Clean up session resources, including deleting corresponding RAGFlow session
        """
        try:
            # Use ragflow_session_manager to delete RAGFlow session
            ragflow_session_manager.delete_session(self.session_id)
        except Exception as e:
            logger.error(f"[Session:{self.session_id[:8]}] Failed to clean up RAGFlow session: {e}")


# Global session Agent manager instance
session_agent_manager = SessionAgentManager()
