from pathlib import Path

from storage import Vault

from ..permissions import ensure_valid_extension, ensure_wiki_path


def write(vault: Vault, path: str, content: str) -> str:
	"""Create or replace a document in the wiki."""
	document_path = Path(path)
	ensure_wiki_path(document_path, vault)
	ensure_valid_extension(document_path, 'write')
	vault.write_document(document_path, content)
	return f'Wrote {document_path}'
