CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL,
    type TEXT NOT NULL,
    size INTEGER NOT NULL,
    created TEXT NOT NULL,
    modified TEXT NOT NULL,
    hash TEXT NOT NULL,
    processed BOOLEAN NOT NULL

    UNIQUE(path)
);

CREATE TABLE IF NOT EXISTS chunks (
    chunk_id INTEGER NOT NULL,
    document_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    page INTEGER

    FOREIGN KEY(document_id) REFERENCES documents(id)
);

CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    content,
    content='chunks',
    contentrowid='chunk_id'
)