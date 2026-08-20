PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL,
    type TEXT NOT NULL,
    size INTEGER NOT NULL,
    created TEXT NOT NULL,
    modified TEXT NOT NULL,
    hash TEXT NOT NULL,
    processed BOOLEAN NOT NULL,

    UNIQUE(path)
);

CREATE TABLE IF NOT EXISTS chunks (
    chunk_id INTEGER NOT NULL,
    document_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    page INTEGER,

    FOREIGN KEY(document_id) REFERENCES documents(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE INDEX idx_chunks_document_id ON chunks(document_id);

CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    content,
    content='chunks',
    content_rowid='chunk_id'
);