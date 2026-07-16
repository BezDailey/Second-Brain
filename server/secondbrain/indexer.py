"""Embed vault documents into ChromaDB with incremental, idempotent ingest.

Configures the embedding model and chunker, connects to the Chroma collection,
and upserts documents while skipping unchanged notes via a content-hash
manifest at ``data/ingest_manifest.json``.
"""

import hashlib
import json
from pathlib import Path

import chromadb
from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

from app.config import settings

COLLECTION_NAME = "vault"
MANIFEST_PATH = Path(__file__).resolve().parents[2] / "data" / "ingest_manifest.json"


def configure() -> None:
    """Set the global LlamaIndex embedding model and node parser.

    Idempotent; safe to call before any indexing or querying operation.
    """
    Settings.embed_model = HuggingFaceEmbedding(model_name=settings.embedding_model)
    Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)


def get_collection():
    """Return the Chroma ``vault`` collection, creating it if absent.

    Returns:
        The ChromaDB collection handle for the configured host/port.
    """
    client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
    return client.get_or_create_collection(COLLECTION_NAME)


def get_vector_store() -> ChromaVectorStore:
    """Wrap the Chroma collection in a LlamaIndex vector store.

    Returns:
        A ``ChromaVectorStore`` backed by the ``vault`` collection.
    """
    return ChromaVectorStore(chroma_collection=get_collection())


def _content_hash(text: str) -> str:
    """Return the md5 hex digest of ``text`` for change detection."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def _load_manifest() -> dict:
    """Load the ingest manifest (``{file_path: content_hash}``), or ``{}``."""
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text())
    return {}


def _save_manifest(manifest: dict) -> None:
    """Write the ingest manifest to disk, creating parent dirs as needed."""
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2))


def ingest_documents(documents) -> dict:
    """Upsert documents into Chroma, skipping unchanged notes.

    Compares each document's content hash against the manifest: unchanged notes
    are skipped, changed notes are deleted and re-inserted, and new notes are
    inserted. The manifest is rewritten to reflect the current vault state.

    Args:
        documents: LlamaIndex Documents from :func:`read_vault`. Each must carry
            a ``file_path`` in its metadata, used as the stable document id.

    Returns:
        A stats dict with integer counts: ``{"added", "updated", "skipped"}``.
    """
    configure()
    vector_store = get_vector_store()
    index = VectorStoreIndex.from_vector_store(vector_store)

    manifest = _load_manifest()
    new_manifest = {}
    stats = {"added": 0, "updated": 0, "skipped": 0}

    for doc in documents:
        path = doc.metadata["file_path"]
        doc.id_ = path
        digest = _content_hash(doc.text)
        new_manifest[path] = digest

        if manifest.get(path) == digest:
            stats["skipped"] += 1
            continue
        if path in manifest:
            index.delete_ref_doc(path, delete_from_docstore=False)
            stats["updated"] += 1
        else:
            stats["added"] += 1
        index.insert(doc)

    _save_manifest(new_manifest)
    return stats
