"""
Google Gemini Provider - Integration with Google's Gemini models
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


from ..specs import ProviderSpec
from .provider_registry import get_provider_registry

try:
    from google import genai
    from google.genai.types import GenerateContentConfig
    GEMINI_AVAILABLE = True
except ImportError:
    logger.warning("Google Genai library not available. Install with: pip install google-genai")
    GEMINI_AVAILABLE = False
    genai = None
    GenerateContentConfig = None


class GeminiProvider:
    """Google Gemini provider"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = "gemini"
        self._initialized = False
        self.client = None
    
    async def initialize(self) -> bool:
        """Validate config and initialize Gemini client"""
        if not GEMINI_AVAILABLE:
            logger.error("Gemini library not available")
            return False
        
        # Validate with registry
        if not self._validate_config():
            return False
        
        # Initialize client
        try:
            api_key = self.config.get("api_key")
            self.client = genai.Client(api_key=api_key)
            model_name = self.config.get("model", "gemini-1.5-flash")
            self._initialized = True
            logger.info(f"Gemini initialized: {model_name}")
            return True
        except Exception as e:
            logger.error(f"Gemini initialization failed: {e}")
            return False
    
    def _validate_config(self) -> bool:
        """Validate configuration using provider registry"""
        registry = get_provider_registry()
        provider_type = "gemini"
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
        """Generate response from Gemini"""
        if not self._initialized:
            raise RuntimeError("Provider not initialized")
        
        try:
            # Get last user message
            user_message = next(
                (msg["content"] for msg in reversed(messages) if msg.get("role") == "user"),
                None
            )
            
            if not user_message:
                return self._error_response("No user message found")
            
            # Build generation config
            gen_config = self._build_request_params(kwargs)
            model = self.config.get("model", "gemini-1.5-flash")
            
            # Make Gemini API call
            try:
                response = await self.client.aio.models.generate_content(
                    model=model,
                    contents=user_message,
                    config=GenerateContentConfig(**gen_config)
                )
                content = response.text if hasattr(response, 'text') else ""
            except Exception as api_error:
                logger.error(f"Gemini API call failed: {api_error}")
                raise
            
            return {
                "content": content,
                "metadata": {
                    "model": model,
                    "provider": "gemini"
                },
                "success": True
            }
        except Exception as e:
            logger.error(f"Gemini request failed: {e}")
            return self._error_response(str(e))
    
    def _build_request_params(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Build request parameters from config and kwargs"""
        gen_config = {
            "temperature": kwargs.get("temperature", self.config.get("temperature", 0.7)),
            "max_output_tokens": kwargs.get("max_tokens", self.config.get("max_tokens", 2000)),
        }
        
        # Add optional params
        for key in ["top_p", "top_k"]:
            if key in kwargs:
                gen_config[key] = kwargs[key]
            elif key in self.config:
                gen_config[key] = self.config[key]
        
        # Remove None values
        return {k: v for k, v in gen_config.items() if v is not None}
    
    def _error_response(self, error: str) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "content": "",
            "metadata": {"error": error, "provider": "gemini"},
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
        logger.info("Gemini provider closed")


def create_gemini_provider(config: Optional[Dict[str, Any]] = None) -> GeminiProvider:
    """Create Gemini provider instance"""
    return GeminiProvider(config or {})
