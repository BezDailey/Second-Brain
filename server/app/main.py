from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import settings
from secondbrain.engine import get_query_engine
from secondbrain.indexer import get_collection

app = FastAPI(title="SecondBrain")


class QueryRequest(BaseModel):
    question: str
    filters: dict | None = None


class Source(BaseModel):
    title: str
    content_snippet: str
    metadata: dict


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/config")
async def config():
    return {"ollama_model": settings.ollama_model, "chroma_port": settings.chroma_port}


@app.post("/api/query", response_model=QueryResponse)
def query(req: QueryRequest):
    engine = get_query_engine(req.filters)
    response = engine.query(req.question)
    sources = [
        Source(
            title=node.metadata.get("title", "Untitled"),
            content_snippet=node.get_content()[:200],
            metadata=node.metadata,
        )
        for node in response.source_nodes
    ]
    return QueryResponse(answer=str(response), sources=sources)


@app.get("/api/sources/{source_id}")
def get_source(source_id: str):
    collection = get_collection()
    result = collection.get(where={"title": source_id}, include=["documents", "metadatas"])
    documents = result.get("documents") or []
    if not documents:
        raise HTTPException(status_code=404, detail=f"No source titled '{source_id}'")
    metadata = (result.get("metadatas") or [{}])[0]
    return {
        "title": source_id,
        "content": "\n\n".join(documents),
        "metadata": metadata,
        "chunk_count": len(documents),
    }
