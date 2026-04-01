"""
Data Sources Package
Provides pluggable data sources for ThinkLife Brain with central registry and management
"""

from .base_data_source import DataSourceConfig
from .vector_db import VectorDataSource, create_vector_data_source
from .data_source_registry import (
    DataSourceRegistry, 
    get_data_source_registry
)

__all__ = [
    # Configuration
    "DataSourceConfig",
    
    # Data Source Types
    "VectorDataSource",
    
    # Factory Functions
    "create_vector_data_source",
    
    # Registry
    "DataSourceRegistry",
    "get_data_source_registry",
]

