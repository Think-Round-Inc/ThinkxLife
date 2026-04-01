"""
Data source specifications, types, and interfaces
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class DataSourceType(str, Enum):
    """Types of data sources"""
    VECTOR_DB = "vector_db"
    #FILE_SYSTEM = "file_system"
    #WEB_SEARCH = "web_search"
    #DATABASE = "database"
    #API = "api"
    #MEMORY = "memory"
    CONVERSATION_HISTORY = "conversation_history"


@dataclass
class DataSourceSpec:
    """Specification for a data source that agents want to use"""
    source_type: DataSourceType
    query: Optional[str] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    limit: int = 5
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "source_type": self.source_type.value if isinstance(self.source_type, Enum) else self.source_type,
            "query": self.query,
            "filters": self.filters,
            "limit": self.limit,
            "enabled": self.enabled,
            "config": self.config
        }


@dataclass
class DataSourceInfo:
    """Information about data sources"""
    source_id: str
    source_type: str
    enabled: bool
    priority: int
    health_status: str
    last_query: Optional[datetime] = None
    query_count: int = 0
    error_count: int = 0
    average_response_time: float = 0.0


class IDataSource(ABC):
    """Interface for data sources that Brain can use"""
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the data source"""
        pass
    
    @abstractmethod
    async def query(self, query: str, context: Dict[str, Any] = None, **kwargs) -> List[Dict[str, Any]]:
        """Query the data source"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check data source health"""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Clean up resources"""
        pass
    
    @property
    @abstractmethod
    def source_type(self) -> DataSourceType:
        """Return the type of this data source"""
        pass

