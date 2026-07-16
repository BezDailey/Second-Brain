"""CLI entry point for SecondBrain (``python -m secondbrain``).

Currently exposes a single ``ingest`` subcommand that reads an Obsidian vault
and embeds it into ChromaDB.
"""

import argparse

from app.config import settings
from secondbrain.indexer import ingest_documents
from secondbrain.vault_reader import read_vault


def ingest(vault_path: str) -> None:
    """Read a vault and ingest it, printing add/update/skip counts.

    Args:
        vault_path: Path to the Obsidian vault to ingest.
    """
    documents = read_vault(vault_path)
    stats = ingest_documents(documents)
    print(f"{stats['added']} added, {stats['updated']} updated, {stats['skipped']} skipped")


def main() -> None:
    """Parse command-line arguments and dispatch the chosen subcommand."""
    parser = argparse.ArgumentParser(prog="secondbrain")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Ingest an Obsidian vault")
    ingest_parser.add_argument("--vault-path", default=settings.vault_path)

    args = parser.parse_args()
    if args.command == "ingest":
        ingest(args.vault_path)


if __name__ == "__main__":
    main()
