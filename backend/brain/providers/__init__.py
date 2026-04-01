"""
Brain Providers - AI provider implementations for ThinkLife Brain
"""

__all__ = []

# Provider registry
try:
    from .provider_registry import (
        ProviderRegistry, 
        get_provider_registry,
        get_provider_registry
    )
    __all__.extend([
        "ProviderRegistry", 
        "get_provider_registry",
        "get_provider_registry"
    ])
except ImportError as e:
    print(f"Warning: Provider registry not available: {e}")


# Core providers
try:
    from .openai import OpenAIProvider, create_openai_provider
    __all__.extend(["OpenAIProvider", "create_openai_provider"])
except ImportError as e:
    print(f"Warning: OpenAI provider not available: {e}")

try:
    from .gemini import GeminiProvider, create_gemini_provider
    __all__.extend(["GeminiProvider", "create_gemini_provider"])
except ImportError as e:
    print(f"Warning: Gemini provider not available: {e}")

try:
    from .anthropic import AnthropicProvider, create_anthropic_provider
    __all__.extend(["AnthropicProvider", "create_anthropic_provider"])
except ImportError as e:
    print(f"Warning: Anthropic provider not available: {e}")

# Provider factory for easy instantiation
def create_provider(provider_type: str, config: dict = None):
    """Factory function to create providers with default settings"""
    if config is None:
        config = {}
    
    provider_map = {
        "openai": (OpenAIProvider, create_openai_provider),
        "gemini": (GeminiProvider, create_gemini_provider), 
        "anthropic": (AnthropicProvider, create_anthropic_provider),
    }
    
    if provider_type not in provider_map:
        raise ValueError(f"Unknown provider type: {provider_type}. Available: {list(provider_map.keys())}")
    
    provider_class, factory_func = provider_map[provider_type]
    
    if provider_class.__name__ not in __all__:
        raise ImportError(f"{provider_type} provider not available. Check dependencies.")
    
    return factory_func(config)

# Get available providers
def get_available_providers():
    """Get list of available provider types"""
    available = []
    provider_map = {
        "OpenAIProvider": "openai",
        "GeminiProvider": "gemini", 
        "AnthropicProvider": "anthropic",
    }
    
    for class_name, provider_type in provider_map.items():
        if class_name in __all__:
            available.append(provider_type)
    
    return available

def get_provider_config_template(provider_type: str) -> dict:
    """Get default configuration template for a provider"""
    try:
        provider = create_provider(provider_type, {})
        return provider.get_default_config()
    except Exception as e:
        raise ValueError(f"Could not get config for {provider_type}: {str(e)}")

def validate_provider_config(provider_type: str, config: dict):
    """Validate provider configuration"""
    try:
        provider = create_provider(provider_type, config)
        is_valid = provider.validate_config()
        error = None if is_valid else "Configuration validation failed"
        return is_valid, error
    except Exception as e:
        return False, str(e) 