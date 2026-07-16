"""Read an Obsidian vault into LlamaIndex Documents.

Walks a vault directory for markdown notes, parsing YAML frontmatter and
`[[wikilinks]]` into per-note metadata.
"""

import re
from pathlib import Path

import frontmatter
from llama_index.core import Document

EXCLUDED_DIRS = {".obsidian", ".trash"}
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def read_vault(vault_path: str) -> list[Document]:
    """Read every markdown note in a vault into LlamaIndex Documents.

    Recursively scans ``vault_path`` for ``*.md`` files, skipping Obsidian's
    internal directories (see ``EXCLUDED_DIRS``). Each note's frontmatter and
    wikilinks are parsed into metadata.

    Args:
        vault_path: Path to the vault root; subdirectories are searched.

    Returns:
        One Document per markdown file, carrying ``title``, ``file_name``,
        ``file_path`` and any parsed note metadata.
    """
    documents = []
    for path in Path(vault_path).rglob("*.md"):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        raw = path.read_text(encoding="utf-8", errors="ignore")
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
    """Split a raw note into body content and metadata.

    Extracts ``tags``, ``aliases`` and ``date`` from YAML frontmatter (list
    values are flattened to comma-separated strings) and collects any
    ``[[wikilinks]]`` found in the body. Malformed frontmatter is tolerated:
    the note is treated as plain text with no metadata.

    Args:
        text: The full raw contents of a markdown note, frontmatter included.

    Returns:
        A ``(content, metadata)`` tuple where ``content`` is the note body
        without frontmatter and ``metadata`` holds the parsed fields.
    """
    try:
        post = frontmatter.loads(text)
        content = post.content
        fm = post.metadata
    except Exception:
        # Malformed YAML frontmatter: treat the note as plain text, no metadata.
        content = text
        fm = {}
    metadata: dict = {}

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
