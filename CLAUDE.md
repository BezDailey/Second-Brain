# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

SecondBrain — RAG over an Obsidian vault: ingest markdown notes, then query them conversationally with cited sources. An annotation-based evaluation pipeline is planned (see Roadmap).

## Tech Stack

- **Backend:** Python 3.12 · FastAPI · LlamaIndex (uv-managed)
- **Vector store:** ChromaDB (runs as a separate service)
- **LLM / embeddings:** Ollama (`llama3.1`) + local HuggingFace embeddings (`BAAI/bge-small-en-v1.5`) — no API keys
- **Frontend:** React 19 · Vite · TypeScript

## Architecture

```
Obsidian Vault → vault_reader → indexer → ChromaDB
                                             ↓
React Chat UI ──/api/query──▶ app.main ──▶ engine (LlamaIndex query)
```

- **Ingestion (CLI):** `vault_reader` reads markdown, parses YAML frontmatter (tags, aliases, date) and `[[wikilinks]]`; `indexer` chunks with `SentenceSplitter` (512/50) and upserts embeddings + metadata into Chroma. Ingestion is **incremental** — a content-hash manifest at `data/ingest_manifest.json` drives add/update/skip.
- **Query (API):** `POST /api/query` → `engine` builds an LRU-cached `VectorStoreIndex` over the Chroma collection, retrieves `similarity_top_k=5`, and synthesizes a grounded answer (`response_mode="compact"`). Optional metadata `filters` (e.g. `{"title": ...}`, `{"tags": ...}`) narrow retrieval.

## Where things live

The backend has **two importable packages under `server/`**, and both are run from the `server/` directory:

- **`app/`** — web layer. `main.py` (FastAPI routes) and `config.py` (`pydantic-settings`, reads `server/.env`).
- **`secondbrain/`** — RAG core. `vault_reader.py`, `indexer.py`, `engine.py`, and `__main__.py` (the `ingest` CLI).

They depend on each other: `app.main` imports from `secondbrain`, and `secondbrain` imports config from `app.config`. Other paths worth knowing: the ingest manifest lives at `data/ingest_manifest.json`, and the frontend chat UI is `client/src/App.tsx` (metadata filter by title/tag).

## API Endpoints (`server/app/main.py`)

- `GET  /api/health` — liveness check
- `GET  /api/config` — active `ollama_model` and `chroma_port`
- `POST /api/query` — `{ question, filters? }` → `{ answer, sources[] }` (each source: `title`, `content_snippet`, `metadata`)
- `GET  /api/sources/{source_id}` — reassemble a note's chunks from Chroma by `title` (404 if none)

CORS allows `http://localhost:5173`. In dev, Vite proxies `/api` → `http://localhost:8000` (`client/vite.config.ts`).

## Local Models (no API keys)

The stack runs entirely on local models: [Ollama](https://ollama.com) for the LLM (`ollama pull llama3.1`, served at `:11434`) and a local HuggingFace embedding model (downloads on first use). All config lives in `server/.env` (copy from `server/.env.example`).

## Commands

- `make dev` — run backend + frontend concurrently (backend :8000, frontend :5173)
- `make backend` / `make frontend` — run one half (each frees its port first)
- `docker compose up -d chroma` — start local ChromaDB (host :8001 → container :8000)
- `python -m secondbrain ingest --vault-path <path>` — ingest a vault (run from `server/`; defaults to `VAULT_PATH` in `.env`)
- `cd server && uv run ruff check . && uv run ruff format .` — lint/format backend
- `cd client && npm run format` — format frontend (Prettier)
- `cd client && npm run lint` — lint frontend (ESLint)
- `cd client && npm run build` — type-check (`tsc -b`) + production build

To serve queries end to end: ChromaDB running, Ollama running with the model pulled, and a vault ingested at least once.

## Conventions

- **Backend:** ruff-formatted, line length 100, lint rules `E,F,I` (import sorting on). Config via `pydantic-settings` — add new settings to `app/config.py` and `.env.example`; never hardcode.
- **Ingestion is idempotent:** re-running `ingest` only re-embeds changed notes (md5 content hash). Delete `data/ingest_manifest.json` to force re-ingest.
- **The query index is LRU-cached** for the process lifetime — restart the backend to pick up newly ingested notes.
- **Frontend:** Prettier-formatted, TypeScript strict; talks to the API only through the `/api` proxy (no hardcoded backend URL).

### Documentation style

- **Python (`server/`):** Google-style docstrings (PEP 257) on public modules, classes, and functions — a summary line plus `Args:` / `Returns:` / `Raises:` as needed. Types live in the signature; don't repeat them in the docstring. FastAPI route docstrings surface in the auto-generated `/docs` (OpenAPI) page, so write them for that audience.
- **TypeScript (`client/`):** TSDoc comments on exported functions and types — a summary plus `@param` / `@returns` / `@throws`. Keep types in the signature, not in the tags (TypeScript already has them).
- **Config files** (`pyproject.toml`, `docker-compose.yml`, `Makefile`, `.env.example`): plain `#` comments only — no doc-comment convention applies. `package.json` is strict JSON and takes no comments.

## Contributing

All code changes to `main` go through pull requests — never commit directly to `main`. Branch, push, and open a PR.

**Authorship:** Commits are authored under the repo owner's git identity (`BezDailey <jabezdailey@icloud.com>`), never an AI/assistant identity. Do not add `Co-Authored-By` trailers, "Generated with …" footers, or similar attribution to commit messages or PR descriptions. Use conventional branch prefixes (`docs/`, `feat/`, `fix/`) — not tool-named prefixes.

**Commit messages:** Follow [Conventional Commits](https://www.conventionalcommits.org) — `type(scope): summary`, with an imperative, lowercase summary kept to ~50 characters. Allowed types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`, `build`, `perf`, `style`. The scope is optional (e.g. `docs(readme):`, `feat(engine):`). Mark a breaking change with `type!:` or a `BREAKING CHANGE:` footer. Example: `fix(indexer): skip notes with unchanged content hash`. (This matches the branch prefixes above and, once tooling lands, is enforced by commitlint and a PR-title check.)

## Roadmap

- **Evaluation pipeline (planned):** score retrieval and answer quality against annotated Q&A datasets. Not yet implemented.

## Repository

- **Remote:** https://github.com/BezDailey/Second-Brain
- **Default branch:** main
- **Project board:** https://github.com/users/BezDailey/projects/3
