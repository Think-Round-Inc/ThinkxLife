"""
Workflow Engine - LangGraph-based orchestrator
Executes agent requests using providers, tools, and data sources in a generalized state-based workflow
"""

import asyncio
import logging
import time
import uuid
import os
from typing import Dict, Any, List, Optional, TypedDict
from functools import reduce

logger = logging.getLogger(__name__)

# Conditional Langfuse import for tracing
try:
    from langfuse import observe
except ImportError:
    def observe(name=None, **kwargs):
        def decorator(func):
            return func
        return decorator

from ..specs import WorkflowStatus

class WorkflowState(TypedDict):
    """State for LangGraph workflow"""
    # Input
    execution_id: str
    request: Any  # BrainRequest
    specs: Any  # AgentExecutionSpec
    
    # Intermediate
    data_source_results: List[Dict[str, Any]]
    tool_results: List[Dict[str, Any]]
    messages: List[Dict[str, str]]
    context: Dict[str, Any]
    
    # Output
    llm_response: Optional[Dict[str, Any]]
    final_content: Optional[str]
    
    # Metadata
    errors: List[str]
    execution_steps: List[str]
    status: str
    start_time: float
    end_time: Optional[float]
    
    # Validation tracking
    validation_attempts: int
    max_validation_runs: int
    validation_feedback: Optional[str]
    is_validated: bool
    confidence_score: float


class WorkflowEngine:
    """LangGraph-based workflow orchestrator"""
    
    def __init__(self):
        self.executions: Dict[str, Dict[str, Any]] = {}
        self._initialized = False
        self.graph = None
    
    async def initialize(self):
        self._initialized = True
        self._build_graph()
        logger.info("Workflow Engine initialized")
    
    def _build_graph(self):
        try:
            from langgraph.graph import StateGraph, END
            
            workflow = StateGraph(WorkflowState)
            
            # Add nodes (processing steps)
            workflow.add_node("initialize", self._initialize_node)
            workflow.add_node("query_data_sources", self._query_data_sources_node)
            workflow.add_node("execute_tools", self._execute_tools_node)
            workflow.add_node("build_messages", self._build_messages_node)
            workflow.add_node("call_provider", self._call_provider_node)
            workflow.add_node("validate_response", self._validate_response_node)
            workflow.add_node("finalize", self._finalize_node)
            
            # Set entry point
            workflow.set_entry_point("initialize")
            
            # Add conditional edges (routing logic)
            workflow.add_conditional_edges(
                "initialize",
                self._route_after_initialize,
                {
                    "data_sources": "query_data_sources",
                    "tools": "execute_tools",
                    "messages": "build_messages"
                }
            )
            
            workflow.add_conditional_edges(
                "query_data_sources",
                self._route_after_data_sources,
                {
                    "tools": "execute_tools",
                    "messages": "build_messages"
                }
            )
            
            workflow.add_edge("execute_tools", "build_messages")
            workflow.add_edge("build_messages", "call_provider")
            workflow.add_edge("call_provider", "validate_response")
            
            # Validation loop: retry if validation fails, else finalize
            workflow.add_conditional_edges(
                "validate_response",
                self._route_after_validation,
                {
                    "retry": "build_messages",  # Loop back to rebuild messages with feedback
                    "finalize": "finalize"
                }
            )
            
            workflow.add_edge("finalize", END)
            
            self.graph = workflow.compile()
            
        except ImportError:
            logger.warning("LangGraph not available, using fallback execution")
            self.graph = None
    
    @observe(name="workflow_execute_plan")
    async def execute_plan(
        self,
        plan: Any,
        request: Any
    ) -> Dict[str, Any]:
        execution_id = str(uuid.uuid4())
        specs = plan.optimized_specs
        start_time = time.time()
        
        try:
            initial_state: WorkflowState = {
                "execution_id": execution_id,
                "request": request,
                "specs": specs,
                "data_source_results": [],
                "tool_results": [],
                "messages": [],
                "context": {
                    "plan_metadata": plan.to_dict() if hasattr(plan, 'to_dict') else {},
                    "session_id": getattr(request.user_context, 'session_id', None)
                },
                "llm_response": None,
                "final_content": None,
                "errors": [],
                "execution_steps": [],
                "status": "running",
                "start_time": start_time,
                "end_time": None,
                "validation_attempts": 0,
                "max_validation_runs": 5,
                "validation_feedback": None,
                "is_validated": False,
                "confidence_score": 0.0
            }
            
            if self.graph:
                final_state = await self._execute_graph(initial_state)
            else:
                final_state = await self._execute_sequential(initial_state)
            
            self.executions[execution_id] = final_state
            
            # Determine outcome
            final_content = final_state.get("final_content")
            if final_content is None:
                llm_response = final_state.get("llm_response")
                if llm_response and isinstance(llm_response, dict):
                    final_content = llm_response.get("content", "")
                else:
                    final_content = "No response generated"
                    logger.warning(f"[{execution_id}] No final content produced")
            
            # Success check logic
            llm_success = False
            if final_state.get("llm_response") and isinstance(final_state["llm_response"], dict):
                llm_success = final_state["llm_response"].get("success", False)
            
            has_valid_content = final_content and final_content != "No response generated" and not final_content.startswith("Error:")
            is_successful = (llm_success and has_valid_content) or (has_valid_content and final_state["status"] in ["completed", "completed_with_errors"])
            
            return {
                "success": is_successful,
                "content": final_content or "",
                "execution_id": execution_id,
                "status": final_state["status"],
                "confidence": final_state.get("confidence_score", 0.0),
                "metadata": {
                    "execution_steps": final_state["execution_steps"],
                    "errors": final_state["errors"],
                    "duration_seconds": (final_state["end_time"] or time.time()) - final_state["start_time"],
                    "confidence_score": final_state.get("confidence_score", 0.0),
                    "validation_attempts": final_state.get("validation_attempts", 0)
                }
            }
            
        except Exception as e:
            logger.exception(f"Workflow execution failed for {execution_id}")
            return {
                "success": False,
                "content": f"Workflow execution failed: {str(e)}",
                "execution_id": execution_id,
                "status": "failed",
                "metadata": {"error": str(e)}
            }
    
    @observe(name="workflow_execute_graph")
    async def _execute_graph(self, initial_state: WorkflowState) -> WorkflowState:
        try:
            return await self.graph.ainvoke(initial_state)
        except Exception as e:
            logger.exception("Graph execution error")
            initial_state["status"] = "failed"
            initial_state["errors"].append(f"Graph error: {str(e)}")
            initial_state["end_time"] = time.time()
            return initial_state
    
    @observe(name="workflow_execute_sequential")
    async def _execute_sequential(self, state: WorkflowState) -> WorkflowState:
        """Fallback sequential execution with validation loop"""
        try:
            state = await self._initialize_node(state)
            
            if state["specs"].data_sources:
                state = await self._query_data_sources_node(state)
            
            if state["specs"].tools:
                state = await self._execute_tools_node(state)
            
            # Agentic loop: retry until validated or max attempts reached
            while True:
                state = await self._build_messages_node(state)
                state = await self._call_provider_node(state)
                state = await self._validate_response_node(state)
                
                # Check if we should continue or break
                route = self._route_after_validation(state)
                if route == "finalize":
                    break
                # else route == "retry", continue loop
            
            state = await self._finalize_node(state)
            
        except Exception as e:
            logger.exception("Sequential execution error")
            state["status"] = "failed"
            state["errors"].append(str(e))
            state["end_time"] = time.time()
        
        return state

    # Nodes
    
    @observe(name="workflow_node_initialize")
    async def _initialize_node(self, state: WorkflowState) -> WorkflowState:
        state["execution_steps"].append("initialize")
        return state
    
    @observe(name="workflow_node_query_data_sources")
    async def _query_data_sources_node(self, state: WorkflowState) -> WorkflowState:
        state["execution_steps"].append("query_data_sources")
        
        try:
            from ..data_sources import get_data_source_registry, create_vector_data_source, DataSourceConfig
            from ..specs import DataSourceType
            
            registry = get_data_source_registry()
            request = state["request"]
            specs = state["specs"]
            results = []
            
            for ds_spec in specs.data_sources:
                if not ds_spec.enabled: continue
                
                try:
                    # Logic simplified for readability
                    source_name = str(ds_spec.source_type.value if hasattr(ds_spec.source_type, 'value') else ds_spec.source_type)
                    
                    if source_name == "vector_db":
                        if registry.check_data_source_available("vector_db"):
                            config = DataSourceConfig(
                                source_id="vector_db",
                                source_type=DataSourceType.VECTOR_DB,
                                config=ds_spec.config or {}
                            )
                            # Assuming proper initialization params
                            vector_source = create_vector_data_source(config)
                            init_config = ds_spec.config or {}
                            
                            if await vector_source.initialize(init_config):
                                query_res = await vector_source.query(
                                    query=ds_spec.query or request.message,
                                    context={"filter": ds_spec.config.get("filter")},
                                    k=ds_spec.limit or 5
                                )
                                results.append({
                                    "source": source_name,
                                    "results": query_res,
                                    "count": len(query_res)
                                })
                                await vector_source.close()
                            else:
                                results.append({"source": source_name, "error": "Initialization failed"})
                        else:
                            results.append({"source": source_name, "error": "Not available"})
                            
                except Exception as e:
                    logger.warning(f"Data source query failed for {ds_spec.source_type}: {e}")
                    state["errors"].append(f"DS Error: {str(e)}")
            
            state["data_source_results"] = results
            
        except Exception as e:
            logger.exception("Data source node error")
            state["errors"].append(str(e))
        
        return state
    
    @observe(name="workflow_node_execute_tools")
    async def _execute_tools_node(self, state: WorkflowState) -> WorkflowState:
        state["execution_steps"].append("execute_tools")
        
        try:
            from ..tools import get_tool_registry
            registry = get_tool_registry()
            results = []
            
            for tool in state["specs"].tools:
                if not tool.enabled: continue
                
                if registry.check_tool_available(tool.name):
                    # In a real implementation, we'd execute the tool here
                    results.append({
                        "tool": tool.name,
                        "status": "executed",
                        "result": "Tool execution placeholder" 
                    })
                else:
                    results.append({"tool": tool.name, "error": "Not available"})
            
            state["tool_results"] = results
            
        except Exception as e:
            logger.exception("Tool execution node error")
            state["errors"].append(str(e))
        
        return state
    
    @observe(name="workflow_node_build_messages")
    async def _build_messages_node(self, state: WorkflowState) -> WorkflowState:
        state["execution_steps"].append("build_messages")
        
        try:
            request = state["request"]
            specs = state["specs"]
            messages = []
            
            # Check if this is a retry with validation feedback
            is_retry = state.get("validation_attempts", 0) > 0 and state.get("validation_feedback")
            
            # User Context
            user_info = self._extract_user_info_for_llm(request.user_context)
            
            # Agent Metadata
            agent_meta = getattr(specs, 'agent_metadata', {})
            msg_context = agent_meta.get("messages_context", {})
            
            if msg_context:
                # Use agent provided context
                sys_prompt = msg_context.get("system_prompt", "")
                if user_info and not self._has_user_context_in_prompt(sys_prompt):
                    sys_prompt = self._enhance_prompt_with_user_info(sys_prompt, user_info)
                
                if sys_prompt:
                    messages.append({"role": "system", "content": sys_prompt})
                
                # History
                for msg in msg_context.get("conversation_history", []):
                    messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
                
                # Context injection
                self._inject_context_messages(messages, state)
                
                # Current message
                messages.append({
                    "role": "user", 
                    "content": msg_context.get("current_message") or request.message
                })
            else:
                # Generic build
                sys_parts = []
                if user_info:
                    sys_parts.append(self._build_user_context_prompt(user_info))
                
                # Context injection into system prompt
                ds_ctx = self._format_data_source_context(state)
                if ds_ctx: sys_parts.append(f"Context from data sources:\n{ds_ctx}")
                
                tool_ctx = self._format_tool_context(state)
                if tool_ctx: sys_parts.append(f"Tool results:\n{tool_ctx}")
                
                # Add validation feedback for retry attempts
                if is_retry:
                    prev_response = state.get("final_content", "")
                    feedback = state.get("validation_feedback", "")
                    retry_guidance = f"""IMPORTANT - Response Improvement Required:
Your previous response was not satisfactory. 

Previous response: {prev_response[:500]}{'...' if len(prev_response) > 500 else ''}

Feedback: {feedback}

Please generate a better, more helpful, and complete response that addresses the user's question properly."""
                    sys_parts.append(retry_guidance)
                
                if sys_parts:
                    messages.append({"role": "system", "content": "\n\n".join(sys_parts)})
                
                messages.append({"role": "user", "content": request.message})
            
            state["messages"] = messages
            
        except Exception as e:
            logger.exception("Build messages node error")
            state["errors"].append(str(e))
            # Fallback
            if not state.get("messages"):
                state["messages"] = [{"role": "user", "content": state["request"].message or "Hello"}]
        
        return state
    
    def _inject_context_messages(self, messages: List[Dict], state: WorkflowState):
        """Helper to inject DS/Tool results into messages"""
        ds_ctx = self._format_data_source_context(state)
        if ds_ctx:
            messages.append({"role": "system", "content": f"Context:\n{ds_ctx}"})
            
        tool_ctx = self._format_tool_context(state)
        if tool_ctx:
            messages.append({"role": "system", "content": f"Tool Results:\n{tool_ctx}"})

    def _format_data_source_context(self, state: WorkflowState) -> str:
        if not state["data_source_results"]: return ""
        return "\n".join([
            f"Data from {r['source']}: {r.get('message', r.get('results', ''))}"
            for r in state["data_source_results"]
        ])

    def _format_tool_context(self, state: WorkflowState) -> str:
        if not state["tool_results"]: return ""
        return "\n".join([
            f"Tool {r['tool']}: {r.get('result', r.get('error', ''))}"
            for r in state["tool_results"]
        ])

    @observe(name="workflow_node_call_provider", as_type="generation")
    async def _call_provider_node(self, state: WorkflowState) -> WorkflowState:
        state["execution_steps"].append("call_provider")
        
        try:
            from ..providers import create_provider
            
            specs = state["specs"]
            if not specs.provider:
                raise ValueError("No provider specified")
                
            config = specs.provider.to_dict() if hasattr(specs.provider, 'to_dict') else {}
            p_type = specs.provider.provider_type
            config.pop("provider_type", None)
            
            # Auto-inject API keys
            key_map = {
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY", 
                "gemini": "GEMINI_API_KEY"
            }
            if p_type in key_map and "api_key" not in config:
                config["api_key"] = os.getenv(key_map[p_type])
            
            provider = create_provider(p_type, config)
            if not await provider.initialize():
                raise RuntimeError(f"Failed to initialize provider {p_type}")
            
            try:
                # Prepare params
                kwargs = {}
                if specs.provider.model: kwargs["model"] = specs.provider.model
                if specs.provider.temperature is not None: kwargs["temperature"] = specs.provider.temperature
                if specs.provider.max_tokens: kwargs["max_tokens"] = specs.provider.max_tokens
                if specs.provider.custom_params: kwargs.update(specs.provider.custom_params)
                
                response = await provider.generate_response(messages=state["messages"], **kwargs)
                state["llm_response"] = response
                
                if response.get("success"):
                    state["final_content"] = response.get("content", "")
                else:
                    err = response.get("metadata", {}).get("error", "Unknown provider error")
                    state["errors"].append(err)
                    state["final_content"] = f"Error: {err}"
                    
            finally:
                await provider.close()
                
        except Exception as e:
            logger.exception("Provider call failed")
            state["errors"].append(str(e))
            state["final_content"] = f"Error calling provider: {str(e)}"
        
        return state
    
    @observe(name="workflow_node_validate_response")
    async def _validate_response_node(self, state: WorkflowState) -> WorkflowState:
        """Validate the LLM response for quality and sensibility with confidence scoring"""
        state["execution_steps"].append("validate_response")
        state["validation_attempts"] += 1
        
        try:
            # Get response content
            response_content = state.get("final_content", "")
            if not response_content or response_content.startswith("Error:"):
                state["validation_feedback"] = "Response generation failed or returned error"
                state["confidence_score"] = 0.0
                return state
            
            # Validate response quality and get confidence score
            validation_result = await self._validate_response_quality(
                response=response_content,
                user_message=state["request"].message,
                state=state
            )
            
            # Update confidence score
            confidence = validation_result.get("confidence", 0.0)
            state["confidence_score"] = confidence
            
            # Threshold check: >= 0.75 is acceptable
            if confidence >= 0.75:
                state["is_validated"] = True
                logger.info(f"Response validated successfully (attempt {state['validation_attempts']}, confidence: {confidence:.2f})")
            else:
                state["is_validated"] = False
                state["validation_feedback"] = validation_result.get("feedback", f"Confidence too low: {confidence:.2f}")
                logger.warning(f"Response validation failed (attempt {state['validation_attempts']}, confidence: {confidence:.2f}): {state['validation_feedback']}")
                
        except Exception as e:
            logger.exception("Validation node error")
            state["errors"].append(f"Validation error: {str(e)}")
            # If validation itself fails, use low confidence
            state["confidence_score"] = 0.5
            state["is_validated"] = True
        
        return state
    
    async def _validate_response_quality(
        self,
        response: str,
        user_message: str,
        state: WorkflowState
    ) -> Dict[str, Any]:
        """
        Validate response quality using rule-based checks and LLM validation
        Returns confidence score (0.0 - 1.0) along with validation result
        """
        confidence_score = 0.0
        
        # Rule-based checks with confidence scoring
        if len(response.strip()) < 10:
            return {"is_valid": False, "feedback": "Response is too short", "confidence": 0.1}
        
        if response.count(" ") < 3:
            return {"is_valid": False, "feedback": "Response lacks substance", "confidence": 0.2}
        
        # Check for common error patterns
        error_patterns = [
            "i cannot", "i can't", "i don't have", "i'm unable",
            "as an ai", "i apologize, but", "i'm sorry, but"
        ]
        response_lower = response.lower()
        if any(pattern in response_lower for pattern in error_patterns) and len(response) < 100:
            return {"is_valid": False, "feedback": "Response appears to be a refusal or error message", "confidence": 0.3}
        
        # Base confidence from rule-based checks
        confidence_score = 0.5  # Passed basic checks
        
        # LLM-based validation for semantic quality with confidence scoring
        try:
            from ..providers import create_provider
            specs = state["specs"]
            
            if not specs.provider:
                # No provider, skip LLM validation - return base confidence
                return {"is_valid": True, "confidence": confidence_score}
            
            # Use same provider for validation
            config = specs.provider.to_dict() if hasattr(specs.provider, 'to_dict') else {}
            p_type = specs.provider.provider_type
            config.pop("provider_type", None)
            
            # Auto-inject API keys
            key_map = {
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
                "gemini": "GEMINI_API_KEY"
            }
            if p_type in key_map and "api_key" not in config:
                config["api_key"] = os.getenv(key_map[p_type])
            
            provider = create_provider(p_type, config)
            if not await provider.initialize():
                # Provider init failed, skip LLM validation
                return {"is_valid": True, "confidence": confidence_score}
            
            try:
                validation_prompt = f"""Evaluate this AI response and provide a confidence score.

User Message: {user_message}

AI Response: {response}

Evaluate:
1. Relevance to the user's question (0-25 points)
2. Helpfulness and informativeness (0-25 points)
3. Accuracy and correctness (0-25 points)
4. Completeness (not cut off, addresses the question) (0-25 points)

Respond in this EXACT format:
SCORE: <number 0-100>
REASONING: <brief explanation>

If score >= 75, the response is acceptable. Below 75, it needs improvement."""

                validation_response = await provider.generate_response(
                    messages=[{"role": "user", "content": validation_prompt}],
                    max_tokens=200,
                    temperature=0.3
                )
                
                validation_text = validation_response.get("content", "").strip()
                
                # Parse confidence score
                import re
                score_match = re.search(r'SCORE:\s*(\d+)', validation_text)
                
                if score_match:
                    llm_score = int(score_match.group(1))
                    # Normalize to 0-1 scale
                    llm_confidence = min(llm_score / 100.0, 1.0)
                    
                    # Combine base confidence with LLM confidence (weighted average)
                    final_confidence = (confidence_score * 0.3) + (llm_confidence * 0.7)
                    
                    # Extract reasoning
                    reasoning_match = re.search(r'REASONING:\s*(.+)', validation_text, re.IGNORECASE | re.DOTALL)
                    reasoning = reasoning_match.group(1).strip() if reasoning_match else "No reasoning provided"
                    
                    is_valid = final_confidence >= 0.75
                    
                    if is_valid:
                        return {"is_valid": True, "confidence": final_confidence, "reasoning": reasoning}
                    else:
                        return {
                            "is_valid": False, 
                            "confidence": final_confidence,
                            "feedback": f"Confidence too low ({final_confidence:.2f}): {reasoning}"
                        }
                else:
                    # Couldn't parse score, fall back to keyword check
                    logger.warning("Could not parse confidence score from validation response")
                    if "acceptable" in validation_text.lower() or "good" in validation_text.lower():
                        return {"is_valid": True, "confidence": 0.75}
                    else:
                        return {"is_valid": False, "confidence": 0.5, "feedback": validation_text}
                    
            finally:
                await provider.close()
                
        except Exception as e:
            logger.warning(f"LLM validation error, accepting response with base confidence: {e}")
            return {"is_valid": True, "confidence": confidence_score}
    
    @observe(name="workflow_node_finalize")
    async def _finalize_node(self, state: WorkflowState) -> WorkflowState:
        state["execution_steps"].append("finalize")
        
        # Check if confidence is below threshold after all attempts
        confidence = state.get("confidence_score", 0.0)
        
        if confidence < 0.75:
            # Replace with fallback response for low confidence
            logger.warning(f"Final confidence {confidence:.2f} below threshold 0.75, using fallback response")
            
            # Generate appropriate fallback message
            fallback_messages = [
                "I'm not confident I can provide an accurate answer to that question right now.",
                "I don't have enough information to give you a reliable response at this time.",
                "I'm uncertain about the best way to answer that. Could you rephrase or provide more context?",
                "I don't know enough about this topic to provide a helpful response."
            ]
            
            # Use the first fallback as default
            state["final_content"] = fallback_messages[0]
            state["errors"].append(f"Low confidence response ({confidence:.2f}) replaced with fallback")
        
        state["status"] = "completed_with_errors" if state["errors"] else "completed"
        state["end_time"] = time.time()
        logger.info(f"Workflow {state['execution_id']} finished: {state['status']} (confidence: {confidence:.2f}, attempts: {state.get('validation_attempts', 0)})")
        return state

    # Routing
    
    @observe(name="workflow_route_after_initialize")
    def _route_after_initialize(self, state: WorkflowState) -> str:
        specs = state["specs"]
        if specs.data_sources and any(d.enabled for d in specs.data_sources): return "data_sources"
        if specs.tools and any(t.enabled for t in specs.tools): return "tools"
        return "messages"
    
    @observe(name="workflow_route_after_data_sources")
    def _route_after_data_sources(self, state: WorkflowState) -> str:
        specs = state["specs"]
        if specs.tools and any(t.enabled for t in specs.tools): return "tools"
        return "messages"
    
    @observe(name="workflow_route_after_validation")
    def _route_after_validation(self, state: WorkflowState) -> str:
        """Route after validation: retry if failed and under max attempts, else finalize"""
        if state["is_validated"]:
            return "finalize"
        
        if state["validation_attempts"] >= state["max_validation_runs"]:
            logger.warning(f"Max validation attempts ({state['max_validation_runs']}) reached, finalizing anyway")
            state["is_validated"] = True  # Force accept after max attempts
            state["errors"].append(f"Response validation failed after {state['validation_attempts']} attempts")
            return "finalize"
        
        logger.info(f"Retrying response generation (attempt {state['validation_attempts'] + 1}/{state['max_validation_runs']})")
        return "retry"

    # User Context Utilities
    
    def _extract_user_info_for_llm(self, user_context) -> Optional[Dict[str, Any]]:
        if not user_context: return None
        
        from dataclasses import asdict
        ctx = asdict(user_context) if hasattr(user_context, '__dataclass_fields__') else dict(user_context or {})
        
        if not ctx.get("is_authenticated") and not ctx.get("authenticated"):
            return None
            
        info = {k: ctx.get(k) for k in ["user_id", "session_id", "name", "email", "roles"] if ctx.get(k)}
        
        profile = ctx.get("user_profile")
        if profile:
            ace = profile.get("ace_score") if isinstance(profile, dict) else getattr(profile, "ace_score", None)
            if ace is not None: info["ace_score"] = ace
            
        return info if len(info) > 1 else None # >1 because user_id/session_id almost always exist

    def _has_user_context_in_prompt(self, prompt: str) -> bool:
        if not prompt: return False
        indicators = ["user_id", "session_id", "user context", "user information", "authenticated user"]
        prompt_lower = prompt.lower()
        return any(i in prompt_lower for i in indicators)

    def _enhance_prompt_with_user_info(self, prompt: str, user_info: Dict[str, Any]) -> str:
        ctx_str = self._build_user_context_prompt(user_info)
        return f"{ctx_str}\n\n{prompt}" if ctx_str else prompt

    def _build_user_context_prompt(self, info: Dict[str, Any]) -> str:
        if not info: return ""
        lines = []
        if info.get("name"): lines.append(f"User name: {info['name']}")
        if info.get("email"): lines.append(f"User email: {info['email']}")
        if info.get("roles"): lines.append(f"User roles: {', '.join(info['roles'])}")
        if info.get("ace_score") is not None: lines.append(f"User ACE score: {info['ace_score']}")
        
        return "User Context:\n" + "\n".join(f"- {l}" for l in lines) if lines else ""

    async def shutdown(self):
        logger.info("Workflow Engine shutdown")

# Singleton
_workflow_engine_instance: Optional[WorkflowEngine] = None

def get_workflow_engine() -> WorkflowEngine:
    global _workflow_engine_instance
    if _workflow_engine_instance is None:
        _workflow_engine_instance = WorkflowEngine()
    return _workflow_engine_instance
