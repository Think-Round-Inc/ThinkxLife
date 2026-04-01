"""
Data Source Registry - Checks if data source files are available
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

DATA_SOURCES = ["vector_db"]


class DataSourceRegistry:
    """Registry for data sources"""
    
    def check_data_source_available(self, source_name: str) -> bool:
        if source_name not in DATA_SOURCES:
            logger.warning(f"Data source '{source_name}' not in allowed list")
            return False
        
        file_path = Path(__file__).parent / f"{source_name}.py"
        if not file_path.exists():
            logger.warning(f"Data source file missing: {source_name}.py")
            return False
        
        return True


_data_source_registry_instance = None

def get_data_source_registry() -> DataSourceRegistry:
    global _data_source_registry_instance
    if _data_source_registry_instance is None:
        _data_source_registry_instance = DataSourceRegistry()
    return _data_source_registry_instance
