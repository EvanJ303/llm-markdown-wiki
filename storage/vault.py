import os
import sqlite3

from pathlib import Path

class Vault:
    def __init__(self, path: str) -> None:
        self.path = Path(path)

        wiki_path = self.path / 'wiki'
        db_path = self.path / '.llmwiki/index.db'
        cache_path = self.path / '.llmwiki/cache'

        wiki_path.mkdir(parents=True, exist_ok=True)
        db_path.mkdir(parents=True, exist_ok=True)
        cache_path.mkdir(exist_ok=True)

        




