"""
Cortex - Generalized AI orchestration system
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, Union
from dotenv import load_dotenv

from ..specs import (
    BrainRequest, BrainConfig, BrainAnalytics, WorkflowExecution, 
    AgentExecutionSpec, ExecutionPlan, IAgent
)
from .workflow_engine import WorkflowEngine, get_workflow_engine
from .reasoning_engine import ReasoningEngine, get_reasoning_engine
from ..data_sources import get_data_source_registry
from ..tools import get_tool_registry
from ..providers import get_provider_registry
from ..guardrails import SecurityManager
from evaluation import (
    get_evaluation_manager, CostEstimator, LatencyEstimator,
    initialize_langfuse_client, is_langfuse_enabled, LANGFUSE_AVAILABLE
)

load_dotenv()

logger = logging.getLogger(__name__)

# Conditional Langfuse import for tracing
try:
    from langfuse import observe
except ImportError:
    # No-op decorator if Langfuse not available
    def observe(name=None, **kwargs):
        def decorator(func):
            return func
        return decorator


class CortexFlow:
    """
    CortexFlow - Two-Phase Execution System
    
    Phase 1: Planning - Agent specs - Optional reasoning
    Phase 2: Execution - Workflow engine executes the plan
    
    Key Features:
    - Two-phase execution (planning - execution)
    - Optional reasoning engine for optimization
    - Plugin-based agent system
    - Workflow engine for standardized execution
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls, config=None):
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config: Optional[Union[BrainConfig, Dict[str, Any]]] = None):
        """Initialize the Cortex"""
        if self._initialized:
            return
        
        # Store config
        if isinstance(config, BrainConfig):
            self.config = config
        elif isinstance(config, dict):
            self.config = BrainConfig(**config)
        else:
            self.config = BrainConfig()

        # Core components  
        self.reasoning_engine: Optional[ReasoningEngine] = None
        self.workflow_engine: Optional[WorkflowEngine] = None
        self.provider_registry = get_provider_registry()
        self.tool_registry = get_tool_registry()
        self.data_source_registry = get_data_source_registry()
        self.security_manager: SecurityManager = SecurityManager(self.config.security)
        
        # Analytics and monitoring
        self.analytics = BrainAnalytics()
        self.start_time = datetime.now()
        self.active_executions: Dict[str, WorkflowExecution] = {}
        
        logger.info("Cortex instance created")

    
    async def initialize(self) -> None:
        """Initialize all Cortex components"""
        if self._initialized:
            return
        
        logger.info("Initializing Cortex components...")
        
        try:
            # Initialize reasoning engine
            self.reasoning_engine = get_reasoning_engine()
            await self.reasoning_engine.initialize()
            
            # Initialize workflow engine 
            self.workflow_engine = get_workflow_engine()
            await self.workflow_engine.initialize()
            
            # Initialize guardrails
            self.security_manager = SecurityManager(self.config.security)
            
            self._initialized = True
            logger.info("Cortex initialized successfully")
            
        except Exception as e:
            logger.critical(f"Failed to initialize Cortex: {e}", exc_info=True)
            raise
    
    
    async def _ensure_initialized(self):
        if not self._initialized:
            await self.initialize()
    
    @observe(name="cortex_process_agent_request")
    async def process_agent_request(
        self,
        agent_specs: AgentExecutionSpec,
        request: BrainRequest
    ) -> Dict[str, Any]:
        """
        Process agent request with agent specs and LLM request
        
        Flow:
        1. Check availability of providers, tools, and data sources via registries
        2. Apply guardrails (rate limiting, content filtering)
        3. Check if reasoning is enabled
        4. If reasoning enabled - invoke reasoning engine (create_execution_plan)
        5. If reasoning not enabled - invoke execute_agent_request (workflow engine)
        6. Return response from workflow engine
        """
        start_time = time.time()
        
        # Initialize Langfuse if needed
        if agent_specs.processing and agent_specs.processing.eval:
            if LANGFUSE_AVAILABLE:
                if not is_langfuse_enabled():
                    if initialize_langfuse_client():
                        logger.info("Langfuse tracing enabled")
                    else:
                        logger.warning("Langfuse initialization failed")
            else:
                logger.warning("Evaluation enabled but Langfuse not installed")
        
        try:
            await self._ensure_initialized()
            
            # 1. Validation
            if agent_specs.provider:
                is_valid, errors, _ = self.provider_registry.check_provider_and_model(
                    agent_specs.provider.provider_type, 
                    agent_specs.provider.model
                )
                if not is_valid:
                    return self._create_error_response(f"Provider validation failed: {', '.join(errors)}", start_time)
            
            for tool in agent_specs.tools:
                if tool.enabled and not self.tool_registry.check_tool_available(tool.name):
                    return self._create_error_response(f"Tool '{tool.name}' not available", start_time)
            
            for ds in agent_specs.data_sources:
                if ds.enabled and str(ds.source_type) == "vector_db":
                    if not self.data_source_registry.check_data_source_available("vector_db"):
                        return self._create_error_response("Data source 'vector_db' not available", start_time)
            
            # 2. Guardrails
            # Convert context safely
            from dataclasses import asdict
            ctx_dict = asdict(request.user_context) if hasattr(request.user_context, '__dataclass_fields__') else dict(request.user_context)
            token = ctx_dict.get("token") or (request.metadata.dict().get("token") if request.metadata else None)
            
            auth_result = self.security_manager.validate_user(ctx_dict, token=token)
            if not auth_result["valid"]:
                return self._create_error_response(f"Authentication failed: {auth_result.get('error')}", start_time)
            
            if not self.security_manager.check_rate_limit(request.user_context.user_id, ctx_dict):
                return self._create_error_response("Rate limit exceeded", start_time)
            
            # 3. Planning
            strategy = agent_specs.processing.execution_strategy if agent_specs.processing else "direct"
            
            if strategy in ["reasoned", "adaptive"]:
                logger.info(f"Creating execution plan using strategy: {strategy}")
                plan = await self.create_execution_plan(agent_specs, request)
                
                # Validate reasoning output before execution
                validation = self._validate_reasoning_output(plan, request)
                if not validation["valid"]:
                    logger.error(f"Reasoning validation failed: {validation['issues']}")
                    return self._create_error_response(
                        f"Reasoning validation failed: {'; '.join(validation['issues'])}",
                        start_time
                    )
                
                result = await self.execute_plan(plan, request)
            else:
                logger.info("Executing directly (no reasoning)")
                estimates = self._get_estimates(agent_specs)
                plan = ExecutionPlan(
                    original_specs=agent_specs,
                    optimized_specs=agent_specs,
                    reasoning_applied=False,
                    confidence=1.0,
                    reasoning_notes={"strategy": "direct"},
                    estimated_cost=estimates["cost"],
                    estimated_latency=estimates["latency"]
                )
                result = await self.execute_agent_request(plan, request)
            
            result["processing_time"] = time.time() - start_time
            return result
            
        except Exception as e:
            logger.exception("Error processing agent request")
            return self._create_error_response(f"Internal error: {str(e)}", start_time)

    def _create_error_response(self, message: str, start_time: float) -> Dict[str, Any]:
        """Helper to create consistent error responses"""
        return {
            "success": False,
            "content": message,
            "metadata": {"error": message},
            "processing_time": time.time() - start_time
        }

    @observe(name="cortex_create_execution_plan")
    async def create_execution_plan(
        self,
        agent_specs: AgentExecutionSpec,
        request: BrainRequest
    ) -> ExecutionPlan:
        """Create execution plan based on strategy"""
        strategy = agent_specs.processing.execution_strategy
        
        if strategy == "reasoned":
            return await self._create_reasoned_plan(agent_specs, request)
        
        elif strategy == "adaptive":
            # Use reasoning, but fallback to agent specs if confidence low
            return await self._create_adaptive_plan(agent_specs, request)
        
        else:
            logger.warning(f"Unknown execution strategy: {strategy}, using direct")
            return self._create_direct_plan(agent_specs)
    
    @observe(name="cortex_create_direct_plan")
    def _create_direct_plan(self, agent_specs: AgentExecutionSpec) -> ExecutionPlan:
        estimates = self._get_estimates(agent_specs)
        return ExecutionPlan(
            original_specs=agent_specs,
            optimized_specs=agent_specs,
            reasoning_applied=False,
            confidence=1.0,
            reasoning_notes={"strategy": "direct", "message": "Skipped reasoning as requested"},
            estimated_cost=estimates["cost"],
            estimated_latency=estimates["latency"]
        )
    
    @observe(name="cortex_create_reasoned_plan")
    async def _create_reasoned_plan(
        self,
        agent_specs: AgentExecutionSpec,
        request: BrainRequest
    ) -> ExecutionPlan:
        try:
            reasoning_result = await self.reasoning_engine.optimize_execution_specs(
                original_specs=agent_specs,
                request=request,
                context=self._get_execution_context()
            )
            
            return ExecutionPlan(
                original_specs=agent_specs,
                optimized_specs=reasoning_result.get("optimized_specs", agent_specs),
                reasoning_applied=True,
                confidence=reasoning_result.get("confidence", 0.8),
                reasoning_notes=reasoning_result.get("notes", {}),
                estimated_cost=reasoning_result.get("estimated_cost", 0.0),
                estimated_latency=reasoning_result.get("estimated_latency", 0.0)
            )
        except Exception as e:
            logger.warning(f"Reasoning failed, falling back to direct: {e}")
            return self._create_direct_plan(agent_specs)
    
    @observe(name="cortex_create_adaptive_plan")
    async def _create_adaptive_plan(
        self,
        agent_specs: AgentExecutionSpec,
        request: BrainRequest
    ) -> ExecutionPlan:
        try:
            reasoning_result = await self.reasoning_engine.optimize_execution_specs(
                original_specs=agent_specs,
                request=request,
                context=self._get_execution_context()
            )
            
            confidence = reasoning_result.get("confidence", 0.0)
            threshold = agent_specs.processing.reasoning_threshold
            
            if confidence >= threshold:
                # High confidence - use reasoning suggestions
                logger.info(f"Using reasoning suggestions (confidence: {confidence} >= {threshold})")
                
                return ExecutionPlan(
                    original_specs=agent_specs,
                    optimized_specs=reasoning_result["optimized_specs"],
                    reasoning_applied=True,
                    confidence=confidence,
                    reasoning_notes=reasoning_result.get("notes", {}),
                    estimated_cost=reasoning_result.get("estimated_cost", 0.0),
                    estimated_latency=reasoning_result.get("estimated_latency", 0.0)
                )
            else:
                # Low confidence - stick with agent specs
                logger.info(f"Reasoning confidence too low ({confidence} < {threshold}), using agent specs")
                
                estimates = self._get_estimates(agent_specs)
                return ExecutionPlan(
                    original_specs=agent_specs,
                    optimized_specs=agent_specs,
                    reasoning_applied=False,
                    confidence=1.0,
                    reasoning_notes={
                        "skipped": f"confidence {confidence} < {threshold}",
                        "suggestion": reasoning_result.get("notes", {})
                    },
                    estimated_cost=estimates["cost"],
                    estimated_latency=estimates["latency"]
                )
        except Exception as e:
            logger.warning(f"Adaptive planning failed, falling back to direct: {e}")
            return self._create_direct_plan(agent_specs)
    
    def _get_execution_context(self) -> Dict[str, Any]:
        """Gather context for reasoning engine"""
        from ..providers.provider_registry import PROVIDER_CONFIGS
        from ..tools.tool_registry import TOOLS
        from ..data_sources.data_source_registry import DATA_SOURCES
        
        return {
            "available_providers": list(PROVIDER_CONFIGS.keys()),
            "available_tools": TOOLS,
            "data_sources": DATA_SOURCES,
            "system_load": {
                "total_requests": self.analytics.total_requests,
                "average_response_time": self.analytics.average_response_time
            }
        }
    
    def _get_estimates(self, specs: AgentExecutionSpec) -> Dict[str, float]:
        try:
            eval_manager = get_evaluation_manager()
            stats = eval_manager.get_latency_statistics() if hasattr(eval_manager, 'get_latency_statistics') else None
            
            return {
                "cost": CostEstimator.estimate(specs),
                "latency": LatencyEstimator.estimate(specs, stats)
            }
        except Exception as e:
            logger.warning(f"Estimation failed: {e}")
            return {"cost": 0.0, "latency": 1.0}
    
    def _validate_reasoning_output(self, plan: ExecutionPlan, request: BrainRequest) -> Dict[str, Any]:
        """
        Validate reasoning engine output before workflow execution
        
        Checks:
        1. Plan has valid specs
        2. Provider is specified and valid
        3. Reasoning confidence is reasonable
        4. Optimized specs are different from original (if reasoning was applied)
        """
        issues = []
        
        try:
            # Check if plan exists
            if not plan:
                return {"valid": False, "issues": ["No execution plan generated"]}
            
            # Check if optimized specs exist
            if not plan.optimized_specs:
                issues.append("No optimized specs in plan")
            
            # Check provider
            if plan.optimized_specs and not plan.optimized_specs.provider:
                issues.append("No provider specified in optimized specs")
            
            # Check reasoning confidence if reasoning was applied
            if plan.reasoning_applied:
                if plan.confidence < 0.3:
                    issues.append(f"Reasoning confidence too low: {plan.confidence}")
                    logger.warning(f"Low reasoning confidence: {plan.confidence}")
                
                # Verify reasoning made meaningful changes
                if plan.optimized_specs and plan.original_specs:
                    original_dict = plan.original_specs.to_dict() if hasattr(plan.original_specs, 'to_dict') else {}
                    optimized_dict = plan.optimized_specs.to_dict() if hasattr(plan.optimized_specs, 'to_dict') else {}
                    
                    # Check if specs are identical (reasoning didn't do anything)
                    if original_dict == optimized_dict:
                        logger.info("Reasoning applied but specs unchanged - this may be intentional")
                        # Not necessarily an issue, reasoning might have validated the original specs
            
            # Check if estimated cost/latency are reasonable
            if plan.estimated_cost and plan.estimated_cost < 0:
                issues.append(f"Invalid estimated cost: {plan.estimated_cost}")
            
            if plan.estimated_latency and plan.estimated_latency < 0:
                issues.append(f"Invalid estimated latency: {plan.estimated_latency}")
            
            # Validate specs have necessary components
            if plan.optimized_specs:
                specs = plan.optimized_specs
                
                # Check provider details
                if specs.provider:
                    if not specs.provider.provider_type:
                        issues.append("Provider type not specified")
                    if not specs.provider.model:
                        issues.append("Provider model not specified")
            
            if issues:
                logger.warning(f"Reasoning validation found {len(issues)} issue(s): {', '.join(issues)}")
                return {"valid": False, "issues": issues}
            
            logger.info("Reasoning output validated successfully")
            return {"valid": True, "issues": []}
            
        except Exception as e:
            logger.error(f"Reasoning validation error: {e}")
            return {"valid": False, "issues": [f"Validation error: {str(e)}"]}
    
    @observe(name="cortex_execute_plan")
    async def execute_plan(
        self,
        plan: ExecutionPlan,
        request: BrainRequest,
        agent: Optional[IAgent] = None
    ) -> Dict[str, Any]:
        """Execute plan via workflow engine"""
        try:
            result = await self.workflow_engine.execute_plan(plan=plan, request=request)
            result["execution_plan"] = plan.to_dict()
            return result
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            raise
    
    @observe(name="cortex_execute_agent_request")
    async def execute_agent_request(
        self,
        plan: ExecutionPlan,
        request: BrainRequest
    ) -> Dict[str, Any]:
        return await self.execute_plan(plan, request, None)
    
    async def shutdown(self):
        logger.info("Shutting down CortexFlow...")
        try:
            if self.workflow_engine:
                await self.workflow_engine.shutdown()
            
            if self.reasoning_engine and hasattr(self.reasoning_engine, 'shutdown'):
                await self.reasoning_engine.shutdown()
            
            self._initialized = False
            logger.info("CortexFlow shutdown complete")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
