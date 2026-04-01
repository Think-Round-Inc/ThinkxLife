"""
Base Data Source Interface and Configuration
Defines the common interface and configuration for all data sources
"""

from dataclasses import dataclass, field
from typing import Dict, Any
from ..specs import DataSourceType


@dataclass
class DataSourceConfig:
    """Configuration for data sources"""
    source_id: str
    source_type: DataSourceType
    config: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    priority: int = 1  # Higher priority sources are preferred
    cache_ttl: int = 300  # Cache TTL in seconds
    max_retries: int = 3
    timeout: float = 30.0

