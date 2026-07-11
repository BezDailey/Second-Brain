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

> Project is in initial development. Setup instructions will be added as scaffolding is completed.

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker (for ChromaDB)

## Project Board

Track progress: [Second Brain Project Board](https://github.com/users/BezDailey/projects/3)

## License

MIT
