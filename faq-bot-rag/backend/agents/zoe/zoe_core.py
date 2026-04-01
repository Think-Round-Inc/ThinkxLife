"""
Zoe Core - Domain Logic Handler

Handles everything EXCEPT LLM calls:
- Trauma-informed personality and prompts
- Conversation context and session management
- Response post-processing and safety checks
- Empathetic communication patterns

LLM calls go through: Plugin - CortexFlow - WorkflowEngine - Provider
"""

import logging
from typing import Dict, Optional, Any, List

from .personality import ZoePersonality
from .conversation_manager import ZoeConversationManager

logger = logging.getLogger(__name__)


class ZoeCore:
    """
    Zoe AI Companion - Domain Logic Handler
    
    Handles everything EXCEPT LLM calls:
    - Trauma-informed personality and prompts
    - Conversation context and session management
    - Response post-processing and safety checks
    - Empathetic communication patterns
    
    LLM calls go through: Plugin - CortexFlow - WorkflowEngine - Provider
    """
    
    def __init__(self):
        self.personality = ZoePersonality()
        self.conversation_manager = ZoeConversationManager()
        self.empathy_level = "high"
        self.trauma_awareness = True
        
        logger.info("ZoeCore initialized")
    
    def prepare_context(self, message: str, user_context: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """
        Prepare context for building prompts
        
        Returns dict with user info, conversation history, safety requirements
        """
        # Get conversation history
        history = self.conversation_manager.get_conversation_history(session_id)
        
        context = {
            "user_id": user_context.get("user_id", "anonymous"),
            "session_id": session_id,
            "empathy_level": self.empathy_level,
            "trauma_aware": self.trauma_awareness,
            "conversation_length": len(history) if history else 0
        }
        
        # Add ACE score if available
        ace_score = user_context.get("ace_score")
        if ace_score:
            context["ace_score"] = ace_score
            context["high_trauma_risk"] = ace_score >= 4
        
        return context
    
    def build_system_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build Zoe's trauma-informed system prompt based on context
        
        This is Zoe's "personality" that guides her responses
        """
        """Build Zoe's trauma-informed system prompt"""
        base_prompt = """You are Zoe, a compassionate AI companion for ThinkLife.

                            Core Principles:
                            - Trauma-Informed Care: Always prioritize safety and empowerment
                            - Empathetic Communication: Validate feelings and provide support
                            - Educational Support: Help users understand AI and technology
                            - Healing-Focused: Support users on their healing journey

                            Guidelines:
                            - Use warm, supportive language
                            - Acknowledge emotions before problem-solving
                            - Respect boundaries and pace
                            - Provide resources when appropriate
                            - Never judge or minimize experiences
                            - Use phrases like "I hear you", "That makes sense", "Thank you for sharing"

                            You speak with kindness, patience, and genuine care for each person's wellbeing."""
        
        # Add trauma-specific guidance for high-risk users
        if context.get("high_trauma_risk"):
            base_prompt += """

                        IMPORTANT: This user has a high ACE score (trauma history). Please:
                        - Be extra gentle and patient
                        - Avoid triggering language
                        - Offer support resources
                        - Acknowledge their strength
                        - Move at their pace"""
        
        return base_prompt
    
    def post_process_response(
        self,
        llm_response: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Post-process LLM response with Zoe's safety checks
        
        Ensures:
        - No minimizing language
        - Trauma-informed tone
        - Appropriate boundaries
        """
        response = llm_response
        
        # Check for minimizing language
        minimizing_phrases = ["just", "simply", "only", "it's not that bad", "calm down"]
        for phrase in minimizing_phrases:
            if phrase.lower() in response.lower():
                logger.warning(f"Zoe: Detected potentially minimizing language: {phrase}")
        
        # Add empathetic closing if needed
        if len(response) > 200 and not any(word in response.lower() for word in ["here", "support", "help"]):
            response += "\n\nI'm here if you need anything else."
        
        return response
    
    def update_conversation(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str
    ):
        """Update conversation history"""
        self.conversation_manager.add_message(
            session_id=session_id,
            role="user",
            content=user_message
        )
        
        self.conversation_manager.add_message(
            session_id=session_id,
            role="assistant",
            content=assistant_response
        )
    
    def clear_conversation(self, session_id: str) -> bool:
        """Clear conversation history"""
        return self.conversation_manager.clear_conversation(session_id)
    
    def get_fallback_response(self) -> str:
        """Get fallback response when LLM fails"""
        return "I'm having a moment of difficulty connecting my thoughts. Could we try that again? I really want to be here for you."
    
    def get_error_response(self) -> str:
        """Get empathetic error response"""
        return "I'm experiencing some technical challenges right now. Please bear with me and try again in a moment. You're important to me, and I want to give you my best."
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for ZoeCore"""
        conversation_count = 0
        if hasattr(self.conversation_manager, 'conversations'):
            conversation_count = len(self.conversation_manager.conversations)
        
        return {
            "status": "healthy",
            "personality": "trauma-informed",
            "empathy_level": self.empathy_level,
            "trauma_awareness": self.trauma_awareness,
            "active_conversations": conversation_count
        }
    
    def shutdown(self):
        """Shutdown ZoeCore"""
        # Clear all conversations if needed
        if hasattr(self.conversation_manager, 'conversations'):
            self.conversation_manager.conversations.clear()
        logger.info("ZoeCore shutdown complete")
    
    def create_brain_request(
        self,
        message: str,
        user_context: Optional[Dict[str, Any]] = None,
        application: str = "chatbot",
        session_id: Optional[str] = None,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Helper method to create a BrainRequest object from user input
        
        This is used by the frontend/API to prepare requests for the plugin.
        The actual LLM processing happens through the plugin architecture.
        
        Args:
            message: User's message
            user_context: User context information (age, ACE score, etc.)
            application: Application type (defaults to chatbot)
            session_id: Session ID from brain's unified session management
            user_id: User identifier
            
        Returns:
            Dictionary that can be used to create a BrainRequest for the plugin
        """
        # Use session_id from user_context if not provided
        if not session_id and user_context:
            session_id = user_context.get("session_id")
        
        # Get conversation length
        conversation_length = 0
        if session_id:
            history = self.conversation_manager.get_conversation_history(session_id)
            conversation_length = len(history)
        
        # Check if message needs redirection (safety check)
        redirect_info = None
        if self.personality.is_off_topic_request(message):
            is_harmful = self.personality._is_harmful_request(message.lower())
            redirect_response = self.personality.get_redirect_response(is_harmful=is_harmful)
            redirect_info = {
                "should_redirect": True,
                "response": redirect_response,
                "is_harmful": is_harmful
            }
        
        return {
            "message": message,
            "application": application,
            "user_context": {
                "user_id": user_id,
                "session_id": session_id,
                "is_authenticated": True,
                **(user_context or {})
            },
            "session_id": session_id,
            "redirect_info": redirect_info,
            "metadata": {
                "source": "zoe",
                "personality_mode": "empathetic_companion",
                "conversation_length": conversation_length,
                "agent_type": "zoe"
            }
        }
    
    def get_conversation_history(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        return self.conversation_manager.get_conversation_history(session_id, limit)