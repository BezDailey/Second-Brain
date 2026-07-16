"""Build the LlamaIndex RAG query engine over the Chroma vault collection.

Wires the Ollama LLM and the embedding model to a vector index, exposing a
query engine with optional metadata filtering.
"""

from functools import lru_cache

from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters
from llama_index.llms.ollama import Ollama

from app.config import settings
from secondbrain.indexer import configure, get_vector_store


@lru_cache(maxsize=1)
def _get_index() -> VectorStoreIndex:
    """Return the vault index, configuring the LLM once and caching it.

    The index is cached for the process lifetime, so notes ingested after the
    first call are not visible until the process restarts.

    Returns:
        A ``VectorStoreIndex`` backed by the Chroma vault collection.
    """
    configure()
    Settings.llm = Ollama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        request_timeout=300.0,
        context_window=8192,
    )
    return VectorStoreIndex.from_vector_store(get_vector_store())


def _build_filters(filters: dict | None) -> MetadataFilters | None:
    """Convert a plain dict into LlamaIndex ``MetadataFilters``.

    Args:
        filters: Metadata key/value pairs to match, e.g. ``{"tags": "python"}``.
            Empty or ``None`` disables filtering.

    Returns:
        A ``MetadataFilters`` combining each pair, or ``None`` if no filters.
    """
    if not filters:
        return None
    return MetadataFilters(
        filters=[MetadataFilter(key=key, value=value) for key, value in filters.items()]
    )


def get_query_engine(filters: dict | None = None):
    """Build a query engine over the vault, optionally metadata-filtered.

    Args:
        filters: Optional metadata key/value pairs to restrict retrieval to
            matching notes (e.g. ``{"title": "..."}``).

    Returns:
        A LlamaIndex query engine retrieving the top 5 chunks and synthesizing
        a compact, grounded answer.
    """
    index = _get_index()
    return index.as_query_engine(
        similarity_top_k=5,
        response_mode="compact",
        filters=_build_filters(filters),
    )
