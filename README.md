# llm-markdown-wiki

A CLI and Model Context Protocol (MCP) server for building a searchable Markdown wiki from selected source documents.

## Overview

`llm-markdown-wiki` gives an LLM a local, persistent workspace in which it can read, search, create, edit, append to, and delete wiki documents. It can also ingest documents such as PDFs, Word files, Excel workbooks, and plain text, then index their content in a local SQLite database.

The project is intended for source-grounded workflows: copy source material into a vault, let the LLM produce linked Markdown notes and summaries, and keep the resulting knowledge base available across sessions.

## How It Works

1. **A vault stores the wiki.** The vault contains a `wiki/` directory and a `.llmwiki/index.db` SQLite index.
2. **Documents are ingested or written.** The CLI copies source files into the wiki and reindexes them. MCP tools can create and update Markdown or other configured text documents.
3. **Text is extracted and chunked.** PDFs are read page by page, DOCX files are read as text, Excel workbooks are converted into sheet and row text, and plain text files are split into pages or chunks.
4. **Content is indexed.** Text chunks and metadata are stored in SQLite so the MCP search tool can find relevant passages.
5. **An MCP-aware LLM uses the tools.** The server exposes read, search, write, append, edit, delete, and guidance tools while keeping file operations inside the vault's `wiki/` directory.

The default vault location is `C:\Vault` on Windows. Use `llmwiki set-location` to choose a persistent location before ingesting documents.

## Requirements

- **Python 3.10 or newer** (minimum supported version)
- A Python environment containing the project dependencies

Runtime dependencies declared in `pyproject.toml`:

- `mcp[cli] >= 1.0.0` — MCP server and CLI support
- `typer >= 0.12.0` — command-line interface
- `python-docx >= 1.1.2` — DOCX text extraction
- `pypdf >= 4.0.0` — PDF text extraction
- `openpyxl >= 3.1.0` — Excel workbook extraction
- `platformdirs >= 4.0.0` — platform-specific configuration paths

SQLite support is provided by the Python standard library.

## Installation

From the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

This installs the `llmwiki` and `llmwiki-mcp` commands.

## Usage

### Set the vault location

```powershell
llmwiki set-location "D:\Knowledge\my-wiki"
```

The location is saved in the platform's user configuration directory.

### Ingest a source document

```powershell
llmwiki ingest "D:\Sources\reference.pdf" reference/reference.pdf
```

The source must exist as a file, and the destination must remain inside the vault's `wiki/` directory. Ingesting immediately reindexes the vault.

### Reindex the wiki

```powershell
llmwiki reindex
```

Use this after copying or changing files outside the CLI or MCP tools.

### Remove or reset content

```powershell
llmwiki remove "reference/reference.pdf"
llmwiki reset
```

`remove` deletes a specific document. `reset` removes all content from the wiki, so use it carefully.

### Run the MCP server

```powershell
llmwiki-mcp
```

Configure your MCP-capable client to launch this command in the project environment. The server provides these tools:

- `guide` — explains available operations and restrictions
- `read` — reads a document, optionally by page range
- `search` — searches indexed content, optionally within a path scope
- `write` — creates or replaces an allowed document
- `append` — appends text to an existing allowed text document
- `edit` — replaces matching text in an allowed document
- `delete` — removes a document inside the wiki

Paths are interpreted relative to the vault unless an absolute path is supplied, and they must remain inside the wiki directory.

## Inspiration and Credit

This project is inspired by [Andrej Karpathy's LLM Wiki workflow](https://github.com/karpathy). Karpathy's approach uses an LLM to maintain a Markdown knowledge base from source material through ingesting, synthesizing, linking, and continually updating notes. `llm-markdown-wiki` adapts that workflow into a local vault with a CLI and MCP interface for LLM-driven read and write operations.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
