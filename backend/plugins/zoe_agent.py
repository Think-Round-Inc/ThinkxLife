"""
Zoe's Plugin - Lightweight connector
All domain logic (personality, prompts, conversation) stays in agents/zoe/
"""

import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from brain.specs import (
    IAgent, AgentMetadata, AgentConfig, AgentResponse, BrainRequest,
    AgentCapability, AgentExecutionSpec, DataSourceSpec, ProviderSpec, 
    ProcessingSpec, DataSourceType
)
from brain.cortex import CortexFlow
from agents.zoe import ZoeCore

logger = logging.getLogger(__name__)


class ZoeAgent(IAgent):
    """Zoe Agent - Connector to CortexFlow"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.initialized = False
        self.zoe_core = None
        self.cortex = None
    
    @property
    def metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="Zoe",
            version="0.7.0",
            description="Empathetic AI companion",
            capabilities=[AgentCapability.CONVERSATIONAL, AgentCapability.ANALYTICAL],
            supported_applications=["chatbot", "general"],
            requires_auth=False,
            author="ThinkLife"
        )
    
    async def initialize(self, config: AgentConfig) -> bool:
        try:
            self.config = config
            self.zoe_core = ZoeCore()
            self.cortex = CortexFlow()
            await self.cortex.initialize()
            
            self.initialized = True
            logger.info("ZoeAgent initialized")
            return True
        except Exception:
            logger.exception("Failed to initialize ZoeAgent")
            return False
    
    async def create_execution_specs(self, request: BrainRequest) -> AgentExecutionSpec:
        # 1. Context
        user_context = {
            "user_id": request.user_context.user_id,
            "ace_score": getattr(request.user_context.user_profile, 'ace_score', None) if request.user_context.user_profile else None
        }
        
        context = self.zoe_core.prepare_context(
            message=request.message,
            user_context=user_context,
            session_id=request.user_context.session_id
        )
        
        # 2. History & Prompt
        history = self.zoe_core.get_conversation_history(request.user_context.session_id)
        prompt = self.zoe_core.build_system_prompt(context)
        
        msg_ctx = {
            "system_prompt": prompt,
            "conversation_history": history[-10:],
            "current_message": request.message
        }
        
        default_db = Path(__file__).resolve().parent.parent / "agents" / "zoe" / "chroma_db"
        db_path = os.getenv("ZOE_VECTOR_DB_PATH", str(default_db))
        
        return AgentExecutionSpec(
            data_sources=[
                DataSourceSpec(
                    source_type=DataSourceType.VECTOR_DB,
                    query=request.message,
                    limit=5,
                    enabled=True,
                    config={"collection_name": "zoe_knowledge", "db_path": db_path}
                ),
            ],
            provider=ProviderSpec(
                provider_type="openai",
                model="gpt-4o-mini",
                temperature=0.7,
                max_tokens=1500,
                custom_params={"presence_penalty": 0.1, "frequency_penalty": 0.1}
            ),
            tools=[],
            processing=ProcessingSpec(
                max_iterations=2,
                timeout_seconds=30.0,
                enable_safety_checks=True,
                enable_conversation_memory=True,
                execution_strategy="direct",
                eval=True
            ),
            agent_metadata={
                "agent_type": "zoe",
                "messages_context": msg_ctx
            }
        )
    
    async def process_request(self, request: BrainRequest) -> AgentResponse:
        if not self.initialized:
            await self.initialize(self.config)
        
        session_id = request.user_context.session_id
        start_time = 0.0

        debug = False
        try:
            # If your BrainRequest.user_context has metadata/custom fields, adjust accordingly
            debug = bool(getattr(request, "metadata", {}).get("debug", False))
        except Exception:
            debug = False

        try:
            import time
            start_time = time.time()
            
            agent_specs = await self.create_execution_specs(request)
            
            logger.info(f"Zoe processing for session: {session_id}")
            cortex_res = await self.cortex.process_agent_request(agent_specs, request)

            retrieved_docs = []
            if debug:
               # try common keys where Cortex might return retrieved context
               retrieved_docs = (
                  cortex_res.get("retrieved_docs")
                  or cortex_res.get("context_docs")
                  or cortex_res.get("documents")
                  or []
                )

            
            if cortex_res.get("success"):
                llm_res = cortex_res.get("content", "")
                
                # Context for post-processing
                u_ctx = {
                    "user_id": request.user_context.user_id,
                    "ace_score": getattr(request.user_context, 'ace_score', None)
                }
                ctx = self.zoe_core.prepare_context(request.message, u_ctx, session_id)
                
                final_res = self.zoe_core.post_process_response(llm_res, ctx)
                
                self.zoe_core.update_conversation(session_id, request.message, final_res)
                
                # Prepare metadata
                metadata = {
                    **cortex_res.get("metadata", {}),
                    "agent": "zoe",
                    "session_id": session_id
                }
                
                if debug:
                   debug_items = []
                   for d in retrieved_docs[:5]:
                       # If it's a LangChain Document
                       if hasattr(d, "page_content"):
                          debug_items.append({
                            "source": (getattr(d, "metadata", {}) or {}).get("source"),
                            "category": (getattr(d, "metadata", {}) or {}).get("category"),
                            "text": (d.page_content or "")[:200],
                          })
                        # If it's already a dict
                       elif isinstance(d, dict):
                            md = d.get("metadata", {}) if isinstance(d.get("metadata"), dict) else {}
                            text = d.get("page_content") or d.get("content") or d.get("text") or ""
                            debug_items.append({
                               "source": md.get("source") or d.get("source"),
                               "category": md.get("category") or d.get("category"),
                               "text": (text or "")[:200],
                            })

                   metadata["debug"] = {
                       "retrieved": debug_items
                   }


                # Include execution plan and estimates if available
                if "execution_plan" in cortex_res:
                    metadata["execution_plan"] = cortex_res["execution_plan"]
                    # Hoist estimates to top-level metadata for visibility
                    if "estimated_cost" in cortex_res["execution_plan"]:
                        metadata["estimated_cost"] = cortex_res["execution_plan"]["estimated_cost"]
                    if "estimated_latency" in cortex_res["execution_plan"]:
                        metadata["estimated_latency"] = cortex_res["execution_plan"]["estimated_latency"]
                
                return AgentResponse(
                    success=True,
                    content=final_res,
                    metadata=metadata,
                    confidence=0.9,
                    processing_time=time.time() - start_time,
                    session_id=session_id
                )
            else:
                logger.error(f"Cortex failed: {cortex_res.get('content')}")
                fallback = self.zoe_core.get_fallback_response()
                return AgentResponse(
                    success=False,
                    content=fallback,
                    metadata={"error": cortex_res.get("content"), "agent": "zoe"},
                    processing_time=time.time() - start_time,
                    session_id=session_id
                )
        
        except Exception as e:
            logger.exception("ZoeAgent process error")
            error_res = self.zoe_core.get_error_response() if self.zoe_core else "Technical error."
            return AgentResponse(
                success=False,
                content=error_res,
                metadata={"error": str(e), "agent": "zoe"},
                processing_time=time.time() - start_time if start_time else 0,
                session_id=session_id
            )
    
    async def health_check(self) -> Dict[str, Any]:
        health = {
            "agent": "zoe",
            "status": "healthy" if self.initialized else "not_initialized",
            "initialized": self.initialized
        }
        if self.zoe_core:
            health["zoe_core"] = self.zoe_core.health_check()
        return health
    
    async def shutdown(self) -> None:
        if self.zoe_core: self.zoe_core.shutdown()
        if self.cortex: await self.cortex.shutdown()
        logger.info("ZoeAgent shutdown")


def create_zoe_agent(config: AgentConfig) -> ZoeAgent:
    return ZoeAgent(config)
