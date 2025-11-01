# -*- coding: utf-8 -*-
# Customer service bot CrewAI configuration
# Using RAGFlow to replace CrewAI built-in RagTool

from crewai import Agent, Crew, Process
from .utils.jobManager import append_event
from .utils.ragflow_client import create_ragflow_client, DEFAULT_CHAT_ID
import json
import os
import requests
from datetime import datetime

# Import configuration
try:
    from config import config
except ImportError:
    config = None


class CrewtestprojectCrew:
    """Customer service bot CrewAI class - Using RAGFlow to replace CrewAI RagTool"""
    
    def __init__(self, job_id, llm):
        self.job_id = job_id
        self.llm = llm
        # Initialize RAGFlow client
        self.ragflow_client = create_ragflow_client()
        self.session_id = None  # Store session ID

    def append_event_callback(self, task_output):
        """Task completion callback function"""
        print("Callback called:", task_output)
        append_event(self.job_id, task_output.raw if hasattr(task_output, "raw") else str(task_output))

    def create_agents(self):
        """Create customer service bot related Agents"""

        # 1. Intelligent customer service Agent
        customer_service_agent = Agent(
            role="Casual Trading Customer Service Representative",
            goal="Chat like friends, naturally and easily answer buyers' questions, with authentic tone and personality",
            backstory="""You are a relaxed and friendly customer service representative who often deals with buyers on second-hand trading platforms.
            Your style characteristics:
            - Natural conversational language, like real human dialogue
            - Short, direct, and opinionated replies
            - Can use natural expressions like "bro, mate, nah, yup, sure, can't go that low"
            - Don't use overly polite or formal tone, don't say "Hello" or "Thank you for your inquiry"
            - If there's no relevant information, directly say "Not too sure mate" or "not sure about that bro"
            - Always keep it relaxed, friendly, with personality but not offensive
            - Answers should be as natural as real trading chat
            - Use this Q&A style:
            Buyer: Can you do 500$?
            Seller: Sry mate, that's too low. Best I can do is $650.
            Buyer: Bro 550 cash today?
            Seller: Can't go that low bro, $630 and it's yours today.""",
            verbose=False,
            llm=self.llm,
        )

        return {
            "customer_service_agent": customer_service_agent
        }

    def call_ragflow(self, customer_input, route_decision="PRODUCT_QUERY", ragflow_session_id=None):
        """Call RAGFlow for knowledge retrieval and return summary"""
        try:
            append_event(self.job_id, f"Starting RAGFlow knowledge retrieval...")
            
            # Use the provided RAGFlow session ID
            session_id_to_use = ragflow_session_id
            
            if not session_id_to_use:
                append_event(self.job_id, "Warning: No RAGFlow session ID, creating new session")
                # Only create new session when there's no session ID
                session_data = self.ragflow_client.create_session(
                    chat_id=DEFAULT_CHAT_ID,
                    name=f"Customer Service Session_{self.job_id}",
                    user_id=f"user_{self.job_id}"
                )
                session_id_to_use = session_data.get('id')
                append_event(self.job_id, f"RAGFlow session created successfully: {session_id_to_use}")
            else:
                append_event(self.job_id, f"Using existing RAGFlow session: {session_id_to_use}")
            
            # Use RAGFlow for conversation
            append_event(self.job_id, f"Sending question to RAGFlow: {customer_input}")
            answer_data = self.ragflow_client.converse(
                chat_id=DEFAULT_CHAT_ID,
                question=customer_input,
                session_id=session_id_to_use
            )
            
            # Extract answer and reference information
            answer = answer_data.get('answer', '')
            reference = answer_data.get('reference', {})
            
            # Build summary information
            summary_parts = []
            if answer:
                summary_parts.append(f"Answer: {answer}")
            
            if reference and reference.get('chunks'):
                chunks = reference['chunks']
                summary_parts.append(f"Relevant document chunks: {len(chunks)}")
                for i, chunk in enumerate(chunks[:3]):  # Only show first 3 chunks
                    content = chunk.get('content', '')[:200] + '...' if len(chunk.get('content', '')) > 200 else chunk.get('content', '')
                    summary_parts.append(f"Chunk {i+1}: {content}")
            
            summary = "\n".join(summary_parts) if summary_parts else "No relevant information found"
            
            append_event(self.job_id, f"RAGFlow retrieval completed, obtained {len(answer)} character answer")
            return summary
            
        except Exception as e:
            append_event(self.job_id, f"RAGFlow call failed: {str(e)}")
            import traceback
            append_event(self.job_id, f"Error details: {traceback.format_exc()}")
            # Return empty summary on error
            return ""

    def create_tasks(self, agents, inputs, route_decision="PRODUCT_QUERY"):
        """Create customer service bot task flow (no longer using CrewAI Task for knowledge retrieval)"""
        from crewai import Task

        customer_input = inputs.get("customer_input", "")
        session_id = inputs.get("session_id")
        
        # Priority: get ragflow_session_id from inputs (passed by session_agent_manager)
        ragflow_session_id = inputs.get("ragflow_session_id")
        
        # Get context information
        context_info = ""
        if session_id:
            try:
                from utils.sessionManager import SessionManager
                session_manager = SessionManager()
                session = session_manager.get_session(session_id)
                if session:
                    context_info = session.get_context_summary(max_messages=5)
                    append_event(self.job_id, f"Retrieved session context, containing {len(session.messages)} messages")
                    
                    # If ragflow_session_id is not in inputs, get it from database (fallback)
                    if not ragflow_session_id and session.ragflow_session_id:
                        ragflow_session_id = session.ragflow_session_id
                        append_event(self.job_id, f"Retrieved RAGFlow session ID from database: {ragflow_session_id}")
            except Exception as e:
                append_event(self.job_id, f"Failed to get context: {str(e)}")
        
        if ragflow_session_id:
            append_event(self.job_id, f"Using RAGFlow session ID: {ragflow_session_id}")

        # Directly call RAGFlow, passing session ID
        retrieved_summary = self.call_ragflow(customer_input, route_decision, ragflow_session_id)

        # Intelligent customer service reply task (based on RAGFlow results)
        customer_service_task = Task(
            description=f"""
                You are a relaxed and natural trading customer service representative, chatting with buyers like friends.
                
                Buyer question: {customer_input}
                
                Knowledge base information: {retrieved_summary}
                
                Conversation history: {context_info}
                
                Reply style requirements:
                - Language must be naturally conversational (English or the language the buyer uses)
                - Replies should be short and direct, with a touch of life
                - Can use words like mate, bro, nah, yup, sure, can't go that low
                - Don't use formal customer service language like "Hello" or "Thank you for your inquiry"
                - Don't mention words like "system", "knowledge base", "AI"
                - Don't say "Please visit the official website" or "Please contact..."
                - Answers must be as natural as real trading dialogue
                - If there's no information, casually say you don't know, like:
                "Not too sure about that mate" or "No idea bro"
                - Keep the tone friendly, straightforward, and down-to-earth
            """,
            expected_output="Natural conversational reply like real trading chat, with personality, relaxed and authentic tone",
            agent=agents["customer_service_agent"]
        )

        return [customer_service_task]

    def create_crew(self, agents, tasks):
        """Create customer service bot Crew (original Crew structure can be kept)"""
        return Crew(
            agents=list(agents.values()),
            tasks=tasks,
            process=Process.sequential,
            verbose=False
        )

    def kickoff(self, inputs):
        """Start customer service bot analysis flow"""
        try:
            append_event(self.job_id, "Initializing intelligent customer service bot...")
            agents = self.create_agents()
            append_event(self.job_id, "Intelligent customer service bot initialization completed")
            
            append_event(self.job_id, "Starting customer service bot task flow...")
            tasks = self.create_tasks(agents, inputs)
            crew = self.create_crew(agents, tasks)
            
            try:
                results = crew.kickoff()
                append_event(self.job_id, "Customer service bot task flow completed")
            except (StopIteration, Exception) as e:
                append_event(self.job_id, f"Customer service bot task execution exception: {str(e)}")
                results = "Sorry, the system is temporarily unable to process your request. Please try again later or contact customer service."
                append_event(self.job_id, "Using fallback reply")
            
            final_result = self.format_final_result(results, inputs)
            return final_result
        except Exception as e:
            append_event(self.job_id, f"Failed to start customer service bot analysis flow: {str(e)}")
            return f"Failed to start customer service bot analysis flow: {str(e)}"

    def format_final_result(self, results, inputs):
        """Format final result, return only concise natural answer"""
        # Extract CrewAI's original answer
        if hasattr(results, 'raw'):
            response_text = results.raw
        elif hasattr(results, 'tasks_output') and results.tasks_output:
            # Extract answer from task output
            response_text = results.tasks_output[0].raw
        else:
            response_text = str(results)
        
        # Return only concise answer
        return response_text
