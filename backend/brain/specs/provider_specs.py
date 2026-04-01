"""
Provider specifications, types, and configurations
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class ProviderType(str, Enum):
    """Available AI provider types"""
    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"


@dataclass
class ModelInfo:
    """Information about a specific AI model"""
    name: str
    max_tokens: int
    input_cost_per_1k: Optional[float] = None
    output_cost_per_1k: Optional[float] = None
    description: Optional[str] = None
    capabilities: List[str] = field(default_factory=lambda: ["text", "completion"])
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = ["text", "completion"]


@dataclass
class ProviderInfo:
    """Information about an AI provider"""
    name: str
    available: bool
    models: List[ModelInfo]
    required_fields: List[str]
    optional_fields: List[str]
    defaults: Dict[str, Any]
    max_tokens_limit: int
    min_tokens_limit: int
    supports_streaming: bool = True
    supports_functions: bool = False
    supports_tools: bool = False


@dataclass
class ProviderConfig:
    """Base provider configuration"""
    enabled: bool = True
    timeout: float = 30.0


@dataclass
class LocalProviderConfig(ProviderConfig):
    """Local provider configuration"""
    endpoint: str = "http://localhost:8000"
    api_key: Optional[str] = None


@dataclass
class OpenAIProviderConfig(ProviderConfig):
    """OpenAI provider configuration"""
    api_key: str = ""
    model: str = "gpt-4o-mini"
    max_tokens: int = 2000
    temperature: float = 0.7
    organization: Optional[str] = None


@dataclass
class AnthropicProviderConfig(ProviderConfig):
    """Anthropic provider configuration"""
    api_key: str = ""
    model: str = "claude-3-sonnet-20240229"
    max_tokens: int = 2000
    temperature: float = 0.7


@dataclass
class GeminiProviderConfig(ProviderConfig):
    """Google Gemini provider configuration"""
    api_key: str = ""
    model: str = "gemini-1.5-flash"
    max_tokens: int = 2000
    temperature: float = 0.7
    safety_settings: Optional[Dict[str, Any]] = None


@dataclass
class ProviderSpec:
    """Specification for LLM provider configuration that agents want to use"""
    provider_type: str  # "openai", "gemini", "anthropic"
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    stream: bool = False
    custom_params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for provider calls"""
        result = {
            "provider_type": self.provider_type,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": self.stream,
            **self.custom_params
        }
        if self.model:
            result["model"] = self.model
        return result

