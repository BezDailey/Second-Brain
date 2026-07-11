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

## Project Structure (planned)

```
├── server/          # FastAPI backend
│   ├── app/         # API routes, dependencies
│   ├── ingestion/   # Vault reader, chunking, embedding
│   ├── engine/      # LlamaIndex query engine config
│   └── eval/        # Evaluation pipeline
├── client/          # React frontend (Vite)
└── data/            # Evaluation datasets
```

## Commands (once scaffolded)

- `make dev` — run backend + frontend concurrently
- `python -m secondbrain ingest --vault-path <path>` — ingest Obsidian vault
- `python -m secondbrain evaluate --dataset <path>` — run evaluation pipeline

## Repository

- **Remote:** https://github.com/BezDailey/SecondBrain
- **Branch:** main
- **Project board:** https://github.com/users/BezDailey/projects/3
