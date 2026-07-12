# Second Brain

RAG-powered knowledge system over an Obsidian vault. Ingests markdown notes to make concepts, daily logs, and learning plans searchable and conversational. Includes an annotation evaluation pipeline that measures retrieval precision and answer quality.

## Tech Stack

- **Backend:** Python, FastAPI, LlamaIndex
- **Vector Store:** ChromaDB
- **Frontend:** React (Vite + TypeScript)

## Architecture

```
┌────────────┐       ┌───────────────┐       ┌──────────┐
│  Obsidian  │──────▶│  Ingestion    │──────▶│ ChromaDB │
│   Vault    │       │  Pipeline     │       │          │
└────────────┘       └───────────────┘       └────┬─────┘
                                                  │
┌────────────┐       ┌───────────────┐            │
│   React    │◀─────▶│   FastAPI     │◀───────────┘
│   Chat UI  │       │  Query Engine │
└────────────┘       └───────────────┘
                            │
                     ┌──────┴──────┐
                     │  LlamaIndex │
                     │     RAG     │
                     └─────────────┘
```

## Features

- **Vault ingestion** — parses Obsidian markdown (frontmatter, wikilinks, callouts), chunks documents, and stores embeddings with metadata
- **Conversational search** — ask natural language questions and get answers grounded in your notes with source citations
- **Metadata filtering** — narrow queries by tags, date range, or note type
- **Evaluation pipeline** — measures retrieval precision@k, recall@k, MRR, faithfulness, and answer relevance against annotated Q&A pairs

## Getting Started

SecondBrain runs entirely on **local models — no API keys required**. The LLM is served by [Ollama](https://ollama.com) and embeddings run locally via a HuggingFace model.

### Prerequisites

- **[uv](https://docs.astral.sh/uv/)** — Python package manager (it fetches the pinned Python 3.12 automatically)
- **Node.js 20+** — for the React frontend
- **Docker** — runs the local ChromaDB instance
- **[Ollama](https://ollama.com)** — local LLM runtime

Install Ollama, then pull the model used for generation:

```bash
ollama pull llama3.1
```

Ollama must be **running** to answer RAG queries (it is not needed just to boot the app). The embedding model (`BAAI/bge-small-en-v1.5`) downloads automatically from HuggingFace on first use — no manual step.

### Setup

1. **Configure environment** — copy the example env file (no secrets or API keys required):

   ```bash
   cp server/.env.example server/.env
   ```

2. **Start ChromaDB** (local vector store):

   ```bash
   docker compose up -d chroma
   ```

3. **Run the app** — starts the FastAPI backend and React frontend together:

   ```bash
   make dev
   ```

   - Backend (API + docs): http://localhost:8000 · http://localhost:8000/docs
   - Frontend: http://localhost:5173

   Run either half on its own with `make backend` or `make frontend`.

### Configuration

All settings live in `server/.env` (see `server/.env.example` for defaults). No API keys are needed:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.1` | Local LLM used for generation |
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | Local HuggingFace embedding model |
| `CHROMA_HOST` | `localhost` | ChromaDB host |
| `CHROMA_PORT` | `8001` | ChromaDB port (host-mapped in `docker-compose.yml`) |
| `VAULT_PATH` | — | Path to the Obsidian vault to ingest |

## Project Board

Track progress: [Second Brain Project Board](https://github.com/users/BezDailey/projects/3)

## License

MIT
