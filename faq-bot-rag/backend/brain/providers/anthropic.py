"""
Anthropic Provider - Integration with Anthropic Claude models
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


from ..specs import ProviderSpec
from .provider_registry import get_provider_registry

try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    logger.warning("Anthropic library not available. Install with: pip install anthropic")
    ANTHROPIC_AVAILABLE = False
    AsyncAnthropic = None


class AnthropicProvider:
    """Anthropic provider for Claude models"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = "anthropic"
        self._initialized = False
        self.client = None
    
    async def initialize(self) -> bool:
        """Validate config and initialize Anthropic client"""
        if not ANTHROPIC_AVAILABLE:
            logger.error("Anthropic library not available")
            return False
        
        # Validate with registry
        if not self._validate_config():
            return False
        
        # Initialize client
        try:
            self.client = AsyncAnthropic(
                api_key=self.config["api_key"],
                timeout=self.config.get("timeout", 30.0),
                max_retries=self.config.get("max_retries", 3),
            )
            self._initialized = True
            logger.info(f"Anthropic initialized: {self.config.get('model')}")
            return True
        except Exception as e:
            logger.error(f"Anthropic initialization failed: {e}")
            return False
    
    def _validate_config(self) -> bool:
        """Validate configuration using provider registry"""
        registry = get_provider_registry()
        provider_type = "anthropic"
        model = self.config.get("model")
        
        is_valid, errors, _ = registry.check_provider_and_model(provider_type, model)
        if not is_valid:
            logger.error(f"Validation failed: {'; '.join(errors)}")
            return False
        return True
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs: Any) -> Dict[str, Any]:
        """Generate response from Anthropic"""
        if not self._initialized:
            raise RuntimeError("Provider not initialized")
        
        try:
            # Extract system message
            system = kwargs.get("system") or self.config.get("system")
            user_messages = [msg for msg in messages if msg.get("role") != "system"]
            
            # Get system from messages if not in config
            if not system:
                for msg in messages:
                    if msg.get("role") == "system":
                        system = msg["content"]
                        break
            
            params = self._build_request_params(kwargs)
            model = params.get("model", self.config.get("model", "unknown"))
            params["messages"] = user_messages
            if system:
                params["system"] = system
            
            # Make Anthropic API call
            try:
                response = await self.client.messages.create(**params)
            except Exception as api_error:
                logger.error(f"Anthropic API call failed: {api_error}")
                raise
            
            content = "".join(
                block.text for block in response.content 
                if block.type == "text"
            ) if response.content else ""
            
            if not response.content:
                return self._error_response("No response content")
            
            # Extract text content
            content = "".join(
                block.text for block in response.content 
                if block.type == "text"
            )
            
            # Extract tool uses
            tool_uses = [
                {"id": block.id, "name": block.name, "input": block.input}
                for block in response.content
                if block.type == "tool_use"
            ]
            
            metadata = {
                "model": response.model,
                "usage": response.usage.dict() if response.usage else {},
                "stop_reason": response.stop_reason,
                "provider": "anthropic"
            }
            if tool_uses:
                metadata["tool_uses"] = tool_uses
            
            return {
                "content": content,
                "metadata": metadata,
                "success": True
            }
        except Exception as e:
            logger.error(f"Anthropic request failed: {e}")
            return self._error_response(str(e))
    
    def _build_request_params(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Build request parameters from config and kwargs"""
        params = {
            "model": kwargs.get("model", self.config.get("model")),
            "max_tokens": kwargs.get("max_tokens", self.config.get("max_tokens")),
            "temperature": kwargs.get("temperature", self.config.get("temperature")),
            "top_p": kwargs.get("top_p", self.config.get("top_p")),
            "stream": kwargs.get("stream", self.config.get("stream", False)),
        }
        
        # Add optional params
        optional = ["top_k", "stop_sequences", "metadata", "tools", "tool_choice"]
        for key in optional:
            if key in kwargs:
                params[key] = kwargs[key]
            elif key in self.config:
                params[key] = self.config[key]
        
        # Remove None values
        return {k: v for k, v in params.items() if v is not None}
    
    def _error_response(self, error: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "content": "",
            "metadata": {"error": error, "provider": "anthropic"},
            "success": False
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check provider health"""
        try:
            import time
            start = time.time()
            response = await self.generate_response(
                [{"role": "user", "content": "Test"}], 
                max_tokens=1
            )
            return {
                "healthy": response.get("success", False),
                "response_time": time.time() - start,
                "provider": self.name,
                "model": self.config.get("model", "unknown")
            }
        except Exception as e:
            return {"healthy": False, "error": str(e), "provider": self.name}
    
    async def close(self) -> None:
        """Close provider"""
        self._initialized = False
        self.client = None
        logger.info("Anthropic provider closed")
    
    
def create_anthropic_provider(config: Optional[Dict[str, Any]] = None) -> AnthropicProvider:
    """Create Anthropic provider instance"""
    return AnthropicProvider(config or {})
