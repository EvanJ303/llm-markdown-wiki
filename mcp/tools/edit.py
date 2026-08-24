from pathlib import Path

from storage import Vault

from ..permissions import ensure_valid_extension, ensure_wiki_path


def edit(vault: Vault, path: str, pattern: str, replacement: str) -> str:
	"""Replace matching text in a document inside the wiki."""
	document_path = Path(path)
	ensure_wiki_path(document_path, vault)
	ensure_valid_extension(document_path, 'write')
	vault.edit_document(document_path, pattern, replacement)
	return f'Edited {document_path}'
