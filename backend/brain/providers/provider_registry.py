"""
Provider Registry - Checks if provider files are available and validates specs
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

logger = logging.getLogger(__name__)


# Provider configurations with models
PROVIDER_CONFIGS = {
    "openai": {
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
        "default_model": "gpt-4o-mini",
    },
    "anthropic": {
        "models": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
        "default_model": "claude-3-5-sonnet-20241022",
    },
    "gemini": {
        "models": ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro", "gemini-1.5-flash-8b", "gemini-1.5-pro-002"],
        "default_model": "gemini-1.5-flash",
    }
}


class ProviderRegistry:
    """
    Registry for providers
    
    Checks if provider files exist and validates provider specs
    """
    
    def check_provider_and_model(self, provider_type: str, model: str = None) -> Tuple[bool, List[str], Optional[Dict[str, Any]]]:
        """
        Check provider and model in one function
        
        Validates:
        1. Provider exists in PROVIDER_CONFIGS
        2. Provider file exists
        3. Model is valid for the provider
        4. Detects if model belongs to a different provider (logical check)
        
        Args:
            provider_type: Name of the provider (e.g., "openai")
            model: Name of the model (e.g., "gpt-4o-mini") - optional
        
        Returns:
            Tuple of (is_valid, errors, info)
            - is_valid: True if provider and model are valid
            - errors: List of error messages
            - info: Dictionary with validated info if valid, None otherwise
        """
        errors = []
        
        # Check if provider exists in PROVIDER_CONFIGS
        if provider_type not in PROVIDER_CONFIGS:
            available = list(PROVIDER_CONFIGS.keys())
            errors.append(f"Provider '{provider_type}' not found. Available: {available}")
            return False, errors, None
        
        # Check if provider file exists
        file_path = Path(__file__).parent / f"{provider_type}.py"
        if not file_path.exists():
            errors.append(f"Provider file not found: {provider_type}.py")
            return False, errors, None
        
        # Get provider config
        provider_config = PROVIDER_CONFIGS[provider_type]
        available_models = provider_config.get("models", [])
        
        # If model is specified, validate it
        if model:
            if model not in available_models:
                model_owner = None
                for other_provider, other_config in PROVIDER_CONFIGS.items():
                    if model in other_config.get("models", []):
                        model_owner = other_provider
                        break
                
                if model_owner:
                    errors.append(f"Model '{model}' belongs to provider '{model_owner}', not '{provider_type}'. Use provider '{model_owner}' or choose a model from {available_models}")
                else:
                    errors.append(f"Model '{model}' not found in any provider. Available models for '{provider_type}': {available_models}")
        else:
            # Use default model if not specified
            model = provider_config.get("default_model")
            if not model:
                errors.append(f"No model specified and no default_model for provider '{provider_type}'")
        
        if errors:
            return False, errors, None
        
        # Return validated info
        info = {
            "provider_type": provider_type,
            "model": model,
            "available": True
        }
        
        return True, [], info
    

# Singleton
_provider_registry_instance = None


def get_provider_registry() -> ProviderRegistry:
    """Get singleton ProviderRegistry instance"""
    global _provider_registry_instance
    if _provider_registry_instance is None:
        _provider_registry_instance = ProviderRegistry()
    return _provider_registry_instance
