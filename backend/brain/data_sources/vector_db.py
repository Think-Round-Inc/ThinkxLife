"""
Vector Database Data Source - Integration with vector databases for semantic search
"""

import logging
import os
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..specs import IDataSource, DataSourceType
from .base_data_source import DataSourceConfig
from .data_source_registry import get_data_source_registry

logger = logging.getLogger(__name__)

try:
    import chromadb
    from chromadb.config import Settings
    from langchain_chroma import Chroma
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    chromadb = None
    Chroma = None


class VectorDataSource(IDataSource):
    """Vector database data source for semantic search"""
    
    def __init__(self, config: DataSourceConfig):
        self.config = config
        self.vectorstore = None
        self._initialized = False
        self._is_external = False
    
    async def initialize(self, init_config: Dict[str, Any] = None) -> bool:
        if not CHROMA_AVAILABLE:
            logger.error("ChromaDB library not available")
            return False
        
        if not self._validate_config():
            return False
        
        try:
            init_config = init_config or {}
            db_path = self.config.config.get("db_path") or init_config.get("db_path")
            
            if not db_path:
                db_path = self._find_sqlite_db()
                if db_path:
                    logger.info(f"Discovered vector DB at {db_path}")
            
            if init_config.get("vectorstore"):
                self.vectorstore = init_config.get("vectorstore")
            elif db_path:
                self.vectorstore = await self._create_from_path(db_path)
                self._is_external = True
            else:
                self.vectorstore = await self._create_default()
            
            if not self.vectorstore:
                return False
            
            self._initialized = True
            logger.info(f"Vector data source {self.config.source_id} initialized")
            return True
            
        except Exception:
            logger.exception("Vector data source initialization failed")
            return False
    
    def _validate_config(self) -> bool:
        registry = get_data_source_registry()
        if not registry.check_data_source_available("vector_db"):
            logger.error("vector_db data source not available")
            return False
        return True
    
    async def _create_default(self):
        return await self._create_client(None)
    
    async def _create_from_path(self, db_path: str):
        return await self._create_client(db_path)

    async def _create_client(self, db_path: Optional[str]):
        """Unified client creation logic"""
        try:
            embeddings = self._load_embeddings()
            if not embeddings:
                logger.warning("No embeddings found, functionality limited")
            
            if db_path:
                persist_dir = os.path.abspath(os.path.dirname(db_path) if db_path.endswith('.sqlite3') else db_path)
            else:
                persist_dir = Path(__file__).parent / "data" / "chroma_db"
                persist_dir.mkdir(parents=True, exist_ok=True)
                persist_dir = str(persist_dir)
            
            if not os.path.exists(persist_dir) and db_path:
                try:
                    os.makedirs(persist_dir, exist_ok=True)
                except Exception:
                    logger.exception(f"Failed to create directory {persist_dir}")
                return None
            
            client = chromadb.PersistentClient(
                path=str(persist_dir),
                settings=Settings(anonymized_telemetry=False)
            )
            
            coll_name = self.config.config.get("collection_name", "default_collection")
            if db_path:
                try:
                    colls = client.list_collections()
                    if colls: coll_name = colls[0].name
                except Exception:
                    pass
            
            return Chroma(
                client=client,
                collection_name=coll_name,
                embedding_function=embeddings
            )
        except Exception:
            logger.exception(f"Failed to create vectorstore (path={db_path})")
            return None
    
    def _load_embeddings(self):
        try:
            from langchain_openai import OpenAIEmbeddings
            if os.getenv("OPENAI_API_KEY"):
                model = self.config.config.get("embedding_model") or "text-embedding-3-small"
                return OpenAIEmbeddings(model=model)
            logger.warning("OPENAI_API_KEY missing")
            return None
        except ImportError:
            logger.warning("OpenAI embeddings library missing")
            return None
        except Exception:
            logger.exception("Failed to load embeddings")
            return None
    
    async def query(self, query: str, context: Dict[str, Any] = None, **kwargs) -> List[Dict[str, Any]]:
        if not self._initialized or not self.vectorstore:
            logger.error("Vectorstore not initialized")
            return []
        
        try:
            k = kwargs.get("k", self.config.config.get("k", 5))
            filter_crit = kwargs.get("filter") or (context.get("filter") if context else None)
            
            docs = self.vectorstore.similarity_search(query, k=k, filter=filter_crit)
            
            return [{
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "source": "vector_db",
                    "score": getattr(doc, 'score', None)
            } for doc in docs]
            
        except Exception:
            logger.exception("Vector query failed")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        try:
            if not self._initialized:
                return {"status": "not_initialized", "initialized": False}
            
            count = self.vectorstore._collection.count() if self.vectorstore and hasattr(self.vectorstore, '_collection') else 0
            return {
                "status": "healthy",
                "document_count": count,
                "initialized": True,
                "is_external": self._is_external
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "initialized": self._initialized}
    
    async def close(self) -> None:
        self._initialized = False
        self.vectorstore = None
        logger.info("Vector data source closed")
    
    @property
    def source_type(self) -> DataSourceType:
        return DataSourceType.VECTOR_DB

    def _find_sqlite_db(self) -> Optional[str]:
        try:
            data_dir = Path(__file__).parent / "data"
            if not data_dir.exists(): return None
            candidates = sorted(data_dir.rglob("*.sqlite*"))
            for path in candidates:
                if path.is_file(): return str(path.resolve())
            return None
        except Exception:
            logger.warning("Auto-discovery failed", exc_info=True)
            return None


def create_vector_data_source(config: Optional[DataSourceConfig] = None) -> VectorDataSource:
    if config is None:
        config = DataSourceConfig(
            source_id="vector_db",
            source_type=DataSourceType.VECTOR_DB,
            priority=10
        )
    return VectorDataSource(config)
