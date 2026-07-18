import json
from dataclasses import dataclass
import sqlite3
from pathlib import Path

@dataclass
class Document:
    path: Path
    type: str
    size: int
    created: str
    modified: str
    hash: str
    processed: bool

@dataclass
class Chunk:
    content: str
    page: int | None = None

@dataclass
class SearchHit:
    path: Path
    snippet: str
    page: int | None = None

class Vault:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

        self.wiki_path = self.root / 'wiki'
        self.cache_path = self.root / '.llmwiki/cache'
        self.db_path = self.root / '.llmwiki/index.db'

        self.wiki_path.mkdir(parents=True, exist_ok=True)
        self.cache_path.mkdir(exist_ok=True)

        self.conn = sqlite3.connect(self.db_path)
        
        schema_path = Path(__file__).resolve().parent / 'schema.sql'
        with open(schema_path, 'r') as f:
            schema = f.read()

        self.conn.executescript(schema)

    def _extract_text(self, path: Path) -> str:
        pass

    def _chunk_text(self, text: str) -> list[Chunk]:
        pass

    def _upsert_document_row(self, document: Document) -> int:
        pass

    def _insert_chunk_row(self, chunk: Chunk) -> None:
        pass

    def _cache_document(self, path: Path) -> None:
        pass

    def _delete_cache_entry(self, path: Path) -> None:
        pass

    def _index_document(self, path: Path) -> None:
        pass

    def _remove_document(self, path: Path) -> None:
        pass

    def index_db(self) -> None:
        pass

    def search(self, query: str) -> list[SearchHit]:
        pass

    def read_document(self, path: Path, page_start: int | None = None, page_end: int | None = None) -> str:
        pass

    def write_page(self, path: Path, content: str) -> None:
        pass

    def edit_page(self, path: Path, content: str) -> None:
        pass

    def delete_page(self, path: Path) -> None:
        pass

    def close(self) -> None:
        self.conn.close()