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
            cfg = json.load(f)
            self.chunk_size = cfg.get('chunk_size', 200)
            self.chunk_overlap = cfg.get('chunk_overlap', 20)
            self.min_chunk_tokens = cfg.get('min_chunk_tokens', 50)
            self.max_chunk_chars = cfg.get('max_chunk_chars', 2000)

        self.conn = sqlite3.connect(self.db_path)
        
        schema_path = Path(__file__).resolve().parent / 'schema.sql'
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()

        self.conn.executescript(schema)

    def _extract_text(self, path: Path) -> List[tuple[str, int | None]]:
        suffix = path.suffix.lower()
        try:
            if suffix == '.pdf':
                from pypdf import PdfReader

                reader = PdfReader(str(path))
                parts: List[tuple[str, int | None]] = []
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text:
                        parts.append((text, i + 1))
                return parts

            if suffix == '.docx':
                from docx import Document as DocxDocument

                doc = DocxDocument(path)
                # docx has no reliable concept of page; return as single segment
                text = '\n'.join(p.text for p in doc.paragraphs if p.text)
                return [(text, None)]

            if suffix in ('.xlsx', '.xlsm', '.xltx', '.xltm'):
                from openpyxl import load_workbook

                wb = load_workbook(filename=path, read_only=True, data_only=True)
                parts_ret: List[tuple[str, int | None]] = []
                for i, sheet in enumerate(wb.worksheets):
                    lines: List[str] = []
                    lines.append(f'=== Sheet: {sheet.title} ===')
                    for row in sheet.iter_rows(values_only=True):
                        row_vals = [str(cell) if cell is not None else '' for cell in row]
                        lines.append('\t'.join(row_vals))
                    parts_ret.append(('\n'.join(lines), i + 1))
                return parts_ret

            # fallback: try to read as plain text and detect form-feed pages
            try:
                raw = path.read_text(encoding='utf-8', errors='ignore')
                if '\f' in raw:
                    pages = [p for p in raw.split('\f') if p.strip()]
                    return [(p, i + 1) for i, p in enumerate(pages)]
                return [(raw, None)]
            except Exception:
                return []
        except Exception:
            return []

    def _read_and_chunk_text(self, path: Path) -> list[Chunk]:
        segments = self._extract_text(path)

        def est_tokens(s: str) -> int:
            return max(1, len(s) // 4)

        def split_long_text(s: str, page: int | None) -> List[Chunk]:
            """Split a very long text block into smaller chunks by char windows with overlap."""
            res: List[Chunk] = []
            maxc = int(self.max_chunk_chars)
            overlap_chars = int(self.chunk_overlap * 4)
            if maxc <= 0:
                maxc = 2000
            start = 0
            length = len(s)
            while start < length:
                end = min(start + maxc, length)
                piece = s[start:end].strip()
                if piece:
                    res.append(Chunk(content=piece, page=page))
                if end >= length:
                    break
                # move start to create overlap
                start = max(0, end - overlap_chars)
            return res

        chunks: List[Chunk] = []

        for (segment_text, page_num) in segments:
            if not segment_text or not segment_text.strip():
                continue

            # split into paragraphs
            import re

            # If this segment originates from a spreadsheet (we add a header '=== Sheet:'),
            # treat each row/line as a paragraph so chunks follow row boundaries.
            if segment_text.lstrip().startswith('=== Sheet:'):
                paragraphs = [l.strip() for l in segment_text.splitlines() if l.strip()]
            else:
                paragraphs = [p.strip() for p in re.split(r'\n\s*\n', segment_text) if p.strip()]

            current = ''

            for paragraph in paragraphs:
                # split paragraph into sentences (simple regex)
                sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', paragraph) if s.strip()]

                # if paragraph is a single very long sentence, treat it as a long block
                if len(sentences) == 1 and (len(sentences[0]) > self.max_chunk_chars or est_tokens(sentences[0]) > self.chunk_size):
                    # flush current if present
                    if current:
                        chunks.append(Chunk(content=current.strip(), page=page_num))
                        current = ''
                    chunks.extend(split_long_text(sentences[0], page_num))
                    continue

                for sent in sentences:
                    if not current:
                        current = sent
                        continue

                    tentative = current + ' ' + sent
                    if (len(tentative) <= self.max_chunk_chars and est_tokens(tentative) <= self.chunk_size) or est_tokens(current) < self.min_chunk_tokens:
                        current = tentative
                        continue

                    # finalize current chunk
                    chunk_text = current.strip()
                    if chunk_text:
                        chunks.append(Chunk(content=chunk_text, page=page_num))

                    # prepare overlap for next chunk
                    overlap_chars = int(self.chunk_overlap * 4)
                    if overlap_chars > 0:
                        overlap_text = chunk_text[-overlap_chars:]
                        # start next with overlap + current sentence
                        current = (overlap_text + ' ' + sent).strip()
                    else:
                        current = sent

                # paragraph finished; if it's long relative to limits, flush
                if current and (est_tokens(current) >= self.chunk_size or len(current) >= self.max_chunk_chars):
                    chunks.append(Chunk(content=current.strip(), page=page_num))
                    current = ''

            # end of page/segment: flush remaining current
            if current:
                # if still too long, split further
                if len(current) > self.max_chunk_chars or est_tokens(current) > self.chunk_size:
                    chunks.extend(split_long_text(current, page_num))
                else:
                    chunks.append(Chunk(content=current.strip(), page=page_num))

        # ensure every chunk has content and trim
        final_chunks: List[Chunk] = []
        for c in chunks:
            content = (c.content or '').strip()
            if not content:
                continue
            # truncate to max chars if needed
            if len(content) > self.max_chunk_chars:
                # split into safe pieces
                final_chunks.extend(split_long_text(content, c.page))
            else:
                final_chunks.append(Chunk(content=content, page=c.page))

        return final_chunks

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
        try:
            import hashlib
            import time

            p = path.resolve()
            # compute content hash
            try:
                data = p.read_bytes()
            except Exception:
                return

            file_hash = hashlib.sha256(data).hexdigest()
            stat = p.stat()

            # cache file name derived from path to avoid collisions
            path_sig = hashlib.sha256(str(p).encode('utf-8')).hexdigest()
            cache_name = f"{p.name}_{path_sig}.json"
            cache_file = self.cache_path / cache_name

            # if cache exists and hash matches, nothing to do
            if cache_file.exists():
                try:
                    existing = json.loads(cache_file.read_text(encoding='utf-8'))
                    if existing.get('hash') == file_hash:
                        return
                except Exception:
                    # if reading/parsing fails, we'll overwrite
                    pass

            # generate processed chunks
            try:
                chunks = [
                    {'content': c.content, 'page': c.page}
                    for c in self._read_and_chunk_text(p)
                    if c.content and c.content.strip()
                ]
            except Exception:
                chunks = []

            payload = {
                'path': str(p),
                'name': p.name,
                'hash': file_hash,
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'cached_at': time.time(),
                'chunks': chunks,
            }

            cache_file.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
        except Exception:
            return

    def _delete_cache_entry(self, path: Path) -> None:
        try:
            import hashlib

            p = path.resolve()
            path_sig = hashlib.sha256(str(p).encode('utf-8')).hexdigest()
            # primary cache filename
            cache_name = f"{p.name}_{path_sig}.json"
            cache_file = self.cache_path / cache_name
            if cache_file.exists():
                try:
                    cache_file.unlink()
                except Exception:
                    pass

            # also remove any cache files that reference this path in their JSON payload
            for f in self.cache_path.glob('*.json'):
                try:
                    txt = f.read_text(encoding='utf-8')
                    obj = json.loads(txt)
                    if obj.get('path') == str(p):
                        try:
                            f.unlink()
                        except Exception:
                            pass
                except Exception:
                    # if parse/read fails, ignore
                    continue
        except Exception:
            return

    def _index_document(self, path: Path) -> None:
        try:
            p = Path(path).resolve()

            # ensure cache is up to date
            self._cache_document(p)

            # find corresponding cache file (match by stored path)
            cache_obj = None
            for f in self.cache_path.glob('*.json'):
                try:
                    obj = json.loads(f.read_text(encoding='utf-8'))
                    if obj.get('path') == str(p):
                        cache_obj = obj
                        break
                except Exception:
                    continue

            # fallback: if no cache found, generate chunks directly
            chunks = []
            file_hash = None
            stat = None
            try:
                stat = p.stat()
            except Exception:
                stat = None

            if cache_obj:
                chunks = cache_obj.get('chunks', [])
                file_hash = cache_obj.get('hash')
            else:
                try:
                    chunks = [{'content': c.content, 'page': c.page} for c in self._read_and_chunk_text(p)]
                except Exception:
                    chunks = []

            # prepare document metadata
            doc = Document(
                path=p,
                type=p.suffix.lower().lstrip('.'),
                size=(stat.st_size if stat is not None else 0),
                created=(str(stat.st_birthtime) if stat is not None else ''),
                modified=(str(stat.st_mtime) if stat is not None else ''),
                hash=(file_hash or ''),
                processed=True,
            )

            doc_id = self._upsert_document_row(doc)

            # replace chunks for this document
            try:
                self.conn.execute('DELETE FROM chunks WHERE document_id = ?', (doc_id,))
            except Exception:
                pass

            for ch in chunks:
                try:
                    content = ch.get('content') if isinstance(ch, dict) else getattr(ch, 'content', '')
                    page = ch.get('page') if isinstance(ch, dict) else getattr(ch, 'page', None)
                    if not content or not str(content).strip():
                        continue
                    self.conn.execute(
                        'INSERT INTO chunks (document_id, content, page) VALUES (?, ?, ?)',
                        (doc_id, content, page),
                    )
                except Exception:
                    continue

            self.conn.commit()

            # try to rebuild FTS index if present
            try:
                self.conn.execute("INSERT INTO chunks_fts(chunks_fts) VALUES('rebuild')")
                self.conn.commit()
            except Exception:
                # ignore if fts table not present or rebuild unsupported
                pass

        except Exception:
            return

    def _remove_document(self, path: Path) -> None:
        try:
            p = Path(path).resolve()

            # remove cache entries for this path
            try:
                self._delete_cache_entry(p)
            except Exception:
                pass

            # delete document row; chunks table has ON DELETE CASCADE
            try:
                self.conn.execute('DELETE FROM documents WHERE path = ?', (str(p),))
                self.conn.commit()
            except Exception:
                # best-effort: ignore failures
                pass
        except Exception:
            return

    def index_db(self) -> None:
        try:
            # Index all files under the wiki path
            indexed_paths = set()
            for p in self.wiki_path.rglob('*'):
                if not p.is_file():
                    continue
                try:
                    self._index_document(p)
                    indexed_paths.add(str(p.resolve()))
                except Exception:
                    # continue indexing other files even if one fails
                    continue

            # Remove documents from DB that no longer exist on disk
            try:
                rows = self.conn.execute('SELECT path FROM documents').fetchall()
                for (doc_path,) in rows:
                    try:
                        if not Path(doc_path).exists():
                            # this will remove DB row and cache files
                            self._remove_document(Path(doc_path))
                    except Exception:
                        continue
            except Exception:
                pass

            # Remove stale cache files that point to missing documents
            try:
                for f in self.cache_path.glob('*.json'):
                    try:
                        obj = json.loads(f.read_text(encoding='utf-8'))
                        pth = obj.get('path')
                        if pth and not Path(pth).exists():
                            try:
                                f.unlink()
                            except Exception:
                                pass
                    except Exception:
                        # if parse/read fails, leave cache file alone
                        continue
            except Exception:
                pass

        except Exception:
            return

    def search(self, query: str) -> list[SearchHit]:
        hits: List[SearchHit] = []
        if not query or not query.strip():
            return hits

        q = query.strip()

        try:
            # Try full-text search with FTS5 and produce a highlighted snippet
            sql = (
                "SELECT documents.path as path, "
                "snippet(chunks_fts, '<b>', '</b>', '...', 64) as snippet, "
                "chunks.page as page "
                "FROM chunks_fts "
                "JOIN chunks ON chunks_fts.rowid = chunks.chunk_id "
                "JOIN documents ON chunks.document_id = documents.id "
                "WHERE chunks_fts MATCH ? "
                "LIMIT 200"
            )
            cur = self.conn.execute(sql, (q,))
            for row in cur.fetchall():
                path_str, snippet_text, page = row
                if not snippet_text:
                    snippet_text = ''
                hits.append(SearchHit(path=Path(path_str), snippet=snippet_text, page=(page if page is not None else None)))
            return hits
        except Exception:
            # Fallback to simple LIKE search if FTS not available
            try:
                like_q = f"%{q}%"
                cur = self.conn.execute(
                    'SELECT documents.path, chunks.content, chunks.page FROM chunks JOIN documents ON chunks.document_id = documents.id WHERE chunks.content LIKE ? LIMIT 200',
                    (like_q,)
                )
                for path_str, content, page in cur.fetchall():
                    snippet_text = ''
                    try:
                        lower = content.lower()
                        idx = lower.find(q.lower())
                        if idx >= 0:
                            start = max(0, idx - 64)
                            end = min(len(content), idx + len(q) + 64)
                            prefix = '...' if start > 0 else ''
                            suffix = '...' if end < len(content) else ''
                            snippet_text = f"{prefix}{content[start:end]}{suffix}"
                        else:
                            snippet_text = (content[:128] + '...') if len(content) > 128 else content
                    except Exception:
                        snippet_text = (content[:128] + '...') if len(content) > 128 else content

                    hits.append(SearchHit(path=Path(path_str), snippet=snippet_text, page=(page if page is not None else None)))
                return hits
            except Exception:
                return hits

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