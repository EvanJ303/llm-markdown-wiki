import json
from dataclasses import dataclass
import sqlite3
from pathlib import Path
from typing import List

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

        config_path = Path(__file__).resolve().parent.parent / 'config.json'
        with open(config_path, 'r', encoding='utf-8') as f:
            self.chunk_size = f['chunk_size']
            self.chunk_overlap = f['chunk_overlap']
            self.min_chunk_tokens = f['min_chunk_tokens']
            self.max_chunk_chars = f['max_chunk_chars']

        self.conn = sqlite3.connect(self.db_path)
        
        schema_path = Path(__file__).resolve().parent / 'schema.sql'
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()

        self.conn.executescript(schema)

    def _extract_text(self, path: Path) -> str:
        suffix = path.suffix.lower()
        try:
            if suffix == '.pdf':
                from pypdf import PdfReader

                reader = PdfReader(str(path))
                parts: List[str] = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        parts.append(text)
                return '\n'.join(parts)

            if suffix == '.docx':
                from docx import Document as DocxDocument

                doc = DocxDocument(path)
                return '\n'.join(p.text for p in doc.paragraphs if p.text)

            if suffix in ('.xlsx', '.xlsm', '.xltx', '.xltm'):
                from openpyxl import load_workbook

                wb = load_workbook(filename=path, read_only=True, data_only=True)
                parts: List[str] = []
                for sheet in wb.worksheets:
                    parts.append(f'=== Sheet: {sheet.title} ===')
                    for row in sheet.iter_rows(values_only=True):
                        row_vals = [str(cell) if cell is not None else '' for cell in row]
                        parts.append('\t'.join(row_vals))
                return '\n'.join(parts)

            # fallback: try to read as plain text
            try:
                return path.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                return ''
        except Exception:
            return ''

    def _read_and_chunk_text(self, path: Path) -> list[Chunk]:
        text = self._extract_text(path)

        paragraphs = [p.strip() for p in text.split('\n\n')]
        chunks = []
        current = ''

        for paragraph in paragraphs:
            if len(current + paragraphs) // 4 <= self.max_chunk_tokens:
                current += paragraph
            else:
                if len(current) // 4 >= self.min_chunk_tokens:
                    chunks.append(Chunk, current, page)

                current = ''

                

    def _upsert_document_row(self, document: Document) -> int:
        self.conn.execute(
            '''
            INSERT INTO documents (path, type, size, created, modified, hash, processed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
                type = excluded.type,
                size = excluded.size,
                created = excluded.created,
                modified = excluded.modified,
                hash = excluded.hash,
                processed = excluded.processed
            ''',
            (
                str(document.path),
                document.type,
                document.size,
                document.created,
                document.modified,
                document.hash,
                document.processed,
            ),
        )
        self.conn.commit()

        row = self.conn.execute(
            'SELECT id FROM documents WHERE path = ?',
            (str(document.path),),
        ).fetchone()
        
        return int(row[0])

    def _insert_chunk_row(self, chunk: Chunk) -> None:
        self.conn.execute(
            '''
            INSERT INTO chunks (content, page)
            VALUES (?, ?)
            ''',
            (
                chunk.content,
                chunk.page,
            ),
        )
        self.conn.commit()

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