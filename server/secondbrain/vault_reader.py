import re
from pathlib import Path

import frontmatter
from llama_index.core import Document

EXCLUDED_DIRS = {".obsidian", ".trash"}
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def read_vault(vault_path: str) -> list[Document]:
    documents = []
    for path in Path(vault_path).rglob("*.md"):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        raw = path.read_text(encoding="utf-8")
        content, note_meta = parse_note(raw)
        documents.append(
            Document(
                text=content,
                metadata={
                    "title": path.stem,
                    "file_name": path.name,
                    "file_path": str(path),
                    **note_meta,
                },
            )
        )
    return documents


def parse_note(text: str) -> tuple[str, dict]:
    post = frontmatter.loads(text)
    content = post.content
    metadata: dict = {}

    fm = post.metadata
    for key in ("tags", "aliases"):
        if key in fm:
            value = fm[key]
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            metadata[key] = str(value)

    if "date" in fm:
        metadata["date"] = str(fm["date"])

    # Wikilinks
    links = [m.split("|")[0].strip() for m in WIKILINK_RE.findall(content)]
    if links:
        metadata["links"] = ", ".join(links)

    return content, metadata
