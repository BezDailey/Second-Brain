from functools import lru_cache

from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters
from llama_index.llms.ollama import Ollama

from app.config import settings
from secondbrain.indexer import configure, get_vector_store


@lru_cache(maxsize=1)
def _get_index() -> VectorStoreIndex:
    configure()
    Settings.llm = Ollama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        request_timeout=300.0,
        context_window=8192,
    )
    return VectorStoreIndex.from_vector_store(get_vector_store())


def _build_filters(filters: dict | None) -> MetadataFilters | None:
    if not filters:
        return None
    return MetadataFilters(
        filters=[MetadataFilter(key=key, value=value) for key, value in filters.items()]
    )


def get_query_engine(filters: dict | None = None):
    index = _get_index()
    return index.as_query_engine(
        similarity_top_k=5,
        response_mode="compact",
        filters=_build_filters(filters),
    )
