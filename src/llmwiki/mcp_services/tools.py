from pathlib import Path

from llmwiki.mcp_services.permissions import ensure_valid_extension, ensure_wiki_path
from llmwiki.vault_storage import Vault


def append(vault: Vault, path: str, content: str) -> str:
	"""Append content to an existing document in the wiki."""
	document_path = Path(path)
	ensure_wiki_path(document_path, vault)
	ensure_valid_extension(document_path, 'append')
	vault.append_to_document(document_path, content)
	return f'Appended to {document_path}'


def delete(vault: Vault, path: str) -> str:
	"""Delete a document from the wiki."""
	document_path = Path(path)
	ensure_wiki_path(document_path, vault)
	vault.delete_document(document_path)
	return f'Deleted {document_path}'


def edit(vault: Vault, path: str, pattern: str, replacement: str) -> str:
	"""Replace matching text in a document inside the wiki."""
	document_path = Path(path)
	ensure_wiki_path(document_path, vault)
	ensure_valid_extension(document_path, 'write')
	vault.edit_document(document_path, pattern, replacement)
	return f'Edited {document_path}'


def guide() -> str:
	"""Describe the wiki tools and their path and file-type restrictions."""
	return (
		'Use read and search to inspect the wiki. Use write to create or replace '
		'allowed document types, append to add content to an existing allowed '
		'text document, edit to replace text in an allowed document, and delete '
		'to remove a document. File paths must be inside the wiki directory.'
	)


def read(
	vault: Vault,
	path: str,
	page_start: int | None = None,
	page_end: int | None = None,
) -> dict[str, str | None]:
	"""Read a document, optionally limited to an inclusive page range."""
	document = vault.read_document(Path(path), page_start, page_end)
	return {
		'path': str(document.path),
		'content': document.content,
		'created': document.created,
		'modified': document.modified,
	}


def search(vault: Vault, query: str, scope: str | None = None) -> list[dict[str, str | int | None]]:
	"""Search indexed wiki content, optionally restricted to a wiki path."""
	hits = vault.search(query, Path(scope) if scope is not None else None)
	return [
		{'path': str(hit.path), 'snippet': hit.snippet, 'page': hit.page}
		for hit in hits
	]


def write(vault: Vault, path: str, content: str) -> str:
	"""Create or replace a document in the wiki."""
	document_path = Path(path)
	ensure_wiki_path(document_path, vault)
	ensure_valid_extension(document_path, 'write')
	vault.write_document(document_path, content)
	return f'Wrote {document_path}'
