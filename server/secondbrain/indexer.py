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
    Settings.embed_model = HuggingFaceEmbedding(model_name=settings.embedding_model)
    Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)


def get_collection():
    client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
    return client.get_or_create_collection(COLLECTION_NAME)


def get_vector_store() -> ChromaVectorStore:
    return ChromaVectorStore(chroma_collection=get_collection())


def _content_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def _load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text())
    return {}


def _save_manifest(manifest: dict) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2))


def ingest_documents(documents) -> dict:
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
