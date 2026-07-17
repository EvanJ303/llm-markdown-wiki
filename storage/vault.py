import json
from dataclasses import dataclass
import sqlite3
from pathlib import Path

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

        wiki_path = self.root / 'wiki'
        cache_path = self.root / '.llmwiki/cache'
        db_path = self.root / '.llmwiki/index.db'

        wiki_path.mkdir(parents=True, exist_ok=True)
        cache_path.mkdir(exist_ok=True)

        self.conn = sqlite3.connect(db_path)
        
        schema_path = Path(__file__).resolve().parent / 'schema.sql'
        with open(schema_path, 'r') as f:
            schema = f.read()

        self.conn.executescript(schema)

    def _extract_text(self, path: Path) -> str:
        pass

    def _chunk_text(self, text: str) -> list[Chunk]:
        pass

    def search(self, query: str) -> list[SearchHit]:
        pass

    def read_file(self, path: Path, page_start: int | None = None, page_end: int | None = None) -> str:
        pass

    def write_page(self, path: Path) -> None:
        pass

    def index_db(self) -> None:
        pass

    def close(self) -> None:
        self.conn.close()