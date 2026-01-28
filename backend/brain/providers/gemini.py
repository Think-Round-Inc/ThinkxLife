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
    from google.genai.types import GenerateContentConfig, Content, Part
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
            model = self.config.get("model", "gemini-1.5-flash")
            
            # Extract system instruction and format history
            system_instruction = None
            contents = []
            
            for msg in messages:
                role = msg.get("role")
                content = msg.get("content", "")
                
                if role == "system":
                    # Concatenate multiple system prompts if present
                    if system_instruction:
                        system_instruction += "\n" + content
                    else:
                        system_instruction = content
                elif role == "user":
                    contents.append(Content(role="user", parts=[Part.from_text(text=content)]))
                elif role == "assistant":
                    contents.append(Content(role="model", parts=[Part.from_text(text=content)]))
            
            if not contents:
                return self._error_response("No conversation history found")
            
            # Build generation config
            gen_config_dict = self._build_request_params(kwargs)
            if system_instruction:
                gen_config_dict["system_instruction"] = system_instruction

            # Convert dict to proper Config object if needed, or pass as kwargs depending on SDK version
            # The google-genai SDK v0.1+ usually takes config object
            # We'll pass specific args to the generate_content calls
            
            gen_config = GenerateContentConfig(**gen_config_dict)
            
            # Make Gemini API call
            try:
                response = await self.client.aio.models.generate_content(
                    model=model,
                    contents=contents,
                    config=gen_config
                )
                
                # Handle response
                content = response.text if hasattr(response, 'text') else ""
                
                # Extract usage if available (depends on SDK version structure)
                usage = {}
                if hasattr(response, 'usage_metadata'):
                    usage = {
                        "prompt_tokens": response.usage_metadata.prompt_token_count,
                        "completion_tokens": response.usage_metadata.candidates_token_count,
                        "total_tokens": response.usage_metadata.total_token_count
                    }
                
            except Exception as api_error:
                logger.error(f"Gemini API call failed: {api_error}")
                # Log detailed error for debugging
                if hasattr(api_error, 'response'):
                    logger.error(f"API Response: {api_error.response}")
                raise
            
            return {
                "content": content,
                "metadata": {
                    "model": model,
                    "provider": "gemini",
                    "usage": usage
                },
                "success": True
            }
        except Exception as e:
            logger.error(f"Gemini request failed: {e}")
            return self._error_response(str(e))
    
    def _build_request_params(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Build request parameters from config and kwargs"""
        # Base config
        params = {}
        
        # Temp
        temp = kwargs.get("temperature", self.config.get("temperature"))
        if temp is not None: params["temperature"] = float(temp)
            
        # Max tokens
        max_tokens = kwargs.get("max_tokens", self.config.get("max_tokens"))
        if max_tokens is not None: params["max_output_tokens"] = int(max_tokens)
            
        # Top P/K
        if "top_p" in kwargs: params["top_p"] = float(kwargs["top_p"])
        if "top_k" in kwargs: params["top_k"] = int(kwargs["top_k"])
        
        return params
    
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
