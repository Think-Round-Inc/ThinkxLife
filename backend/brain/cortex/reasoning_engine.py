"""
Reasoning Engine
Uses LLMs to decide next steps, choose tools/data sources, refine plans
"""

import logging
from typing import Dict, Any, List, Optional

from ..specs import BrainRequest, ProviderSpec, ToolSpec, DataSourceSpec
from ..providers import create_provider, get_provider_registry
from ..tools import get_tool_registry
from ..data_sources import get_data_source_registry
from evaluation import CostEstimator, LatencyEstimator, get_latency_statistics

logger = logging.getLogger(__name__)


class ReasoningEngine:
    """
    LLM-powered reasoning engine that decides:
    - What tools to use
    - What data sources to query
    - How to refine plans
    - Next steps in execution
    """
    
    def __init__(self):
        self.tool_registry = get_tool_registry()
        self.data_source_registry = get_data_source_registry()
        self.provider_registry = get_provider_registry()
    
    async def initialize(self):
        logger.info("Reasoning Engine initialized")
    
    async def decide_next_step(
        self,
        request: BrainRequest,
        provider_spec: ProviderSpec,
        context: Dict[str, Any],
        execution_history: List[str]
    ) -> Dict[str, Any]:
        """Use LLM to decide next step"""
        reasoning_prompt = self._build_reasoning_prompt(request, context, execution_history)
        
        user_info = self._extract_user_info_for_reasoning(request.user_context)
        if user_info:
            ctx_section = self._build_user_context_for_reasoning(user_info)
            if ctx_section:
                reasoning_prompt = f"{ctx_section}\n\n{reasoning_prompt}"
        
        provider = await self._create_provider(provider_spec)
        if not provider:
            return {"action": "error", "reason": "Provider unavailable"}
        
        try:
            response = await provider.generate_response(
                messages=[{"role": "user", "content": reasoning_prompt}]
            )
            return self._parse_decision(response.get("content", ""))
            
        except Exception as e:
            logger.error(f"Reasoning failed: {e}")
            return {"action": "error", "reason": str(e)}
    
    async def select_tools(
        self,
        request: BrainRequest,
        provider_spec: ProviderSpec,
        available_tools: List[str]
    ) -> List[ToolSpec]:
        """Use LLM to select relevant tools"""
        tool_desc = self.tool_registry.get_tool_descriptions()
        
        prompt = f"""
Given the user request: "{request.message}"

Available tools:
{self._format_tools(tool_desc)}

Select the most relevant tools to use. Reply with tool names only, one per line.
"""
        
        provider = await self._create_provider(provider_spec)
        if not provider:
            return []
        
        try:
            response = await provider.generate_response(
                messages=[{"role": "user", "content": prompt}]
            )
            selected = self._parse_tool_selection(response.get("content", ""))
            return [ToolSpec(name=tool) for tool in selected if tool in available_tools]
            
        except Exception as e:
            logger.error(f"Tool selection failed: {e}")
            return []
    
    async def refine_plan(
        self,
        original_request: BrainRequest,
        provider_spec: ProviderSpec,
        results_so_far: Dict[str, Any],
        remaining_iterations: int
    ) -> Dict[str, Any]:
        """Use LLM to refine execution plan"""
        prompt = f"""
Original request: "{original_request.message}"

Results so far:
{self._format_results(results_so_far)}

Remaining iterations: {remaining_iterations}

Should we:
1. Continue with current approach
2. Try different tools/data sources
3. Conclude with current results

Provide reasoning and recommendation.
"""
        
        provider = await self._create_provider(provider_spec)
        if not provider:
            return {"action": "continue", "reason": "Provider unavailable"}
        
        try:
            response = await provider.generate_response(
                messages=[{"role": "user", "content": prompt}]
            )
            return self._parse_plan_refinement(response.get("content", ""))
            
        except Exception as e:
            logger.error(f"Plan refinement failed: {e}")
            return {"action": "continue", "reason": str(e)}
    
    def _build_reasoning_prompt(self, request, context, history) -> str:
        return f"""
Task: {request.message}
Context: {context}
Execution History:
{chr(10).join(history) if history else "None"}
Based on the above, what should be the next action?
"""
    
    def _parse_decision(self, llm_response: str) -> Dict[str, Any]:
        resp = llm_response.lower()
        if "tool" in resp: return {"action": "use_tool", "reason": llm_response}
        if "data" in resp or "search" in resp: return {"action": "query_data", "reason": llm_response}
        if "complete" in resp or "done" in resp: return {"action": "complete", "reason": llm_response}
        return {"action": "continue", "reason": llm_response}
    
    def _parse_tool_selection(self, llm_response: str) -> List[str]:
        tools = []
        for line in llm_response.strip().split("\n"):
            tool = line.strip().strip("-*•").strip()
            if tool and not tool.startswith("#"):
                tools.append(tool)
        return tools
    
    def _parse_plan_refinement(self, llm_response: str) -> Dict[str, Any]:
        resp = llm_response.lower()
        if "different" in resp or "try" in resp: return {"action": "adjust", "reason": llm_response}
        if "conclude" in resp or "finish" in resp: return {"action": "conclude", "reason": llm_response}
        return {"action": "continue", "reason": llm_response}
    
    def _format_tools(self, tool_desc: Dict[str, str]) -> str:
        return "\n".join(f"- {name}: {desc}" for name, desc in tool_desc.items())
    
    def _format_results(self, results: Dict[str, Any]) -> str:
        return str(results)
    
    def _extract_user_info_for_reasoning(self, user_context) -> Optional[Dict[str, Any]]:
        if not user_context: return None
        from dataclasses import asdict
        ctx = asdict(user_context) if hasattr(user_context, '__dataclass_fields__') else dict(user_context or {})
        
        if not ctx.get("is_authenticated") or ctx.get("auth_provider") != "keycloak":
            return None
        
        info = {k: ctx.get(k) for k in ["user_id", "session_id", "roles"] if ctx.get(k)}
        
        profile = ctx.get("user_profile")
        if profile:
            ace = profile.get("ace_score") if isinstance(profile, dict) else getattr(profile, "ace_score", None)
            if ace is not None: info["ace_score"] = ace
        
        return info if len(info) > 2 else None
    
    def _build_user_context_for_reasoning(self, user_info: Dict[str, Any]) -> str:
        parts = []
        if user_info.get("roles"): parts.append(f"User roles: {', '.join(user_info['roles'])}")
        if user_info.get("ace_score") is not None: parts.append(f"User ACE score: {user_info['ace_score']}")
        return "User Context (for decision-making):\n" + "\n".join(f"- {p}" for p in parts) if parts else ""
    
    async def _create_provider(self, provider_spec: ProviderSpec):
        is_valid, errors, _ = self.provider_registry.check_provider_and_model(
            provider_spec.provider_type, provider_spec.model
        )
        if not is_valid:
            logger.error(f"Provider spec invalid: {errors}")
            return None
        
        try:
            config = {
                    "model": provider_spec.model,
                    "temperature": provider_spec.temperature,
                    "max_tokens": provider_spec.max_tokens,
                    **provider_spec.custom_params
                }
            provider = create_provider(provider_spec.provider_type, config)
            await provider.initialize()
            return provider
        except Exception as e:
            logger.error(f"Provider creation failed: {e}")
            return None
    
    async def optimize_execution_specs(
        self,
        original_specs: Any,
        request: Any,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize execution specs using LLM reasoning"""
        logger.info("Reasoning engine optimizing execution specs")
        
        try:
            optimized_specs = original_specs
            confidence = 0.75
            notes = {}
            
            # Simple heuristics placeholder for full LLM logic
            if original_specs.provider:
                notes["provider"] = await self._analyze_provider(original_specs.provider, request, context)
            
            if original_specs.data_sources:
                notes["data_sources"] = await self._analyze_data_sources(original_specs.data_sources, request)
            
            if original_specs.tools:
                notes["tools"] = await self._analyze_tools(original_specs.tools, request)
            
            # Use centralized estimators
            estimated_cost = CostEstimator.estimate(optimized_specs)
            
            # Get history stats for better latency estimation
            try:
                stats = get_latency_statistics()
            except Exception:
                stats = None
            
            estimated_latency = LatencyEstimator.estimate(optimized_specs, stats)
            
            return {
                "optimized_specs": optimized_specs,
                "confidence": confidence,
                "notes": notes,
                "estimated_cost": estimated_cost,
                "estimated_latency": estimated_latency
            }
        
        except Exception as e:
            logger.error(f"Error optimizing specs: {e}")
            return {
                "optimized_specs": original_specs,
                "confidence": 0.0,
                "notes": {"error": str(e)},
                "estimated_cost": 0.0,
                "estimated_latency": 0.0
            }
    
    async def _analyze_provider(self, provider_spec, request, context) -> Dict[str, Any]:
        return {
            "original_provider": provider_spec.provider_type,
            "can_use_cheaper": len(request.message.split()) < 50
        }
    
    async def _analyze_data_sources(self, data_sources, request) -> Dict[str, Any]:
        return {"count": len(data_sources)}
    
    async def _analyze_tools(self, tools, request) -> Dict[str, Any]:
        return {"count": len(tools)}
    
    async def shutdown(self):
        logger.info("Reasoning Engine shutdown")


# Singleton
_reasoning_engine_instance: Optional[ReasoningEngine] = None

def get_reasoning_engine() -> ReasoningEngine:
    global _reasoning_engine_instance
    if _reasoning_engine_instance is None:
        _reasoning_engine_instance = ReasoningEngine()
    return _reasoning_engine_instance
