"""
Zoe Conversation Manager

Simple conversation history storage.
Uses unified session_id from brain's session management.
No session lifecycle management - sessions are managed by brain.
"""

import uuid
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ConversationMessage:
    """Represents a single message in a conversation"""
    id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class ZoeConversationManager:
    """
    Simple conversation history manager for Zoe AI Companion
    
    Features:
    - Conversation history storage by session_id
    - Message history tracking
    - No session lifecycle management (handled by brain)
    
    Uses unified session_id from brain's session management system.
    """
    
    def __init__(self):
        # Simple storage: session_id -> list of messages
        self.conversations: Dict[str, List[ConversationMessage]] = {}
        
        # Configuration
        self.max_message_history = 50
        
        logger.info("Zoe Conversation Manager initialized")
    
    def add_message(
        self, 
        session_id: str, 
        role: str, 
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a message to the conversation history
        
        Args:
            session_id: Session identifier (from brain's unified session)
            role: 'user' or 'assistant'
            content: Message content
            metadata: Optional message metadata
            
        Returns:
            bool: Success status
        """
        if not session_id:
            logger.warning("No session_id provided, cannot store message")
            return False
        
        # Initialize conversation if needed
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        # Create message
        message = ConversationMessage(
            id=str(uuid.uuid4()),
            role=role,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        # Add to conversation
        self.conversations[session_id].append(message)
        
        # Limit message history
        if len(self.conversations[session_id]) > self.max_message_history:
            # Keep only the most recent messages
            self.conversations[session_id] = self.conversations[session_id][-self.max_message_history:]
        
        logger.debug(f"Added {role} message to conversation {session_id}")
        return True
    
    def get_conversation_history(
        self, 
        session_id: str, 
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages to return
            
        Returns:
            List of message dictionaries
        """
        if not session_id or session_id not in self.conversations:
            return []
        
        messages = self.conversations[session_id]
        if limit:
            messages = messages[-limit:]
        
        return [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "metadata": msg.metadata
            }
            for msg in messages
        ]
    
    def clear_conversation(self, session_id: str) -> bool:
        """
        Clear conversation history for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: Success status
        """
        if session_id in self.conversations:
            del self.conversations[session_id]
            logger.info(f"Cleared conversation history for session {session_id}")
            return True
        return False
    
    def get_context_for_ai(self, session_id: str) -> Dict[str, Any]:
        """
        Get formatted context for AI processing
        
        Returns context suitable for Brain/OpenAI processing
        """
        if not session_id or session_id not in self.conversations:
            return {}
        
        # Get recent conversation history (last 10 messages for AI context)
        messages = self.conversations[session_id]
        recent_messages = messages[-10:] if messages else []
        
        conversation_history = [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in recent_messages
        ]
        
        return {
            "conversation_history": conversation_history,
            "session_id": session_id,
            "conversation_length": len(messages),
        }
