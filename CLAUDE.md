# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

SecondBrain — RAG-powered knowledge system over an Obsidian vault. Ingests markdown notes to make concepts, daily logs, and learning plans searchable and conversational. Includes an annotation evaluation pipeline that measures retrieval precision and answer quality.

## Tech Stack

- **Backend:** Python · FastAPI · LlamaIndex
- **Vector Store:** ChromaDB
- **Frontend:** React · Vite · TypeScript

## Architecture

```
Obsidian Vault → Ingestion Pipeline → ChromaDB
                                          ↓
React Chat UI ↔ FastAPI (LlamaIndex RAG Query Engine)
```

- **Ingestion:** Reads Obsidian markdown, parses frontmatter/wikilinks, chunks via LlamaIndex node parsers, stores embeddings + metadata in ChromaDB
- **Query:** FastAPI exposes `/api/query` — LlamaIndex retrieves relevant chunks from ChromaDB, synthesizes a grounded answer with source citations
- **Evaluation:** CLI pipeline scores retrieval precision@k, recall@k, MRR, faithfulness, and relevance against annotated Q&A datasets

## Project Structure

```
├── server/               # FastAPI backend (uv-managed, Python 3.12)
│   ├── app/              # ✅ main.py (routes), config.py (pydantic-settings)
│   ├── ingestion/        # (planned) Vault reader, chunking, embedding
│   ├── engine/           # (planned) LlamaIndex query engine config
│   ├── eval/             # (planned) Evaluation pipeline
│   ├── pyproject.toml    # ✅ deps (uv) + ruff config
│   └── .env.example      # ✅ config template (no API keys)
├── client/               # ✅ React frontend (Vite + TS, ESLint + Prettier)
├── data/                 # Chroma persistence + evaluation datasets
├── docker-compose.yml    # ✅ local ChromaDB service
└── Makefile              # ✅ make dev / backend / frontend
```

## Local Models (no API keys)

The stack runs entirely on local models: [Ollama](https://ollama.com) for the LLM
(`ollama pull llama3.1`) and a local HuggingFace embedding model
(`BAAI/bge-small-en-v1.5`, downloads on first use). All config lives in `server/.env`
(see `server/.env.example`).

## Commands

- `make dev` — run backend + frontend concurrently (backend :8000, frontend :5173)
- `make backend` / `make frontend` — run one half
- `docker compose up -d chroma` — start local ChromaDB (:8001)
- `cd server && uv run ruff check . && uv run ruff format .` — lint/format backend
- `cd client && npm run format` — format frontend (Prettier)
- `python -m secondbrain ingest --vault-path <path>` — (planned) ingest Obsidian vault
- `python -m secondbrain evaluate --dataset <path>` — (planned) run evaluation pipeline

## Repository

- **Remote:** https://github.com/BezDailey/Second-Brain
- **Branch:** main
- **Project board:** https://github.com/users/BezDailey/projects/3
