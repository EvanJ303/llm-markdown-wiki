from pathlib import Path

from storage import Vault

from ..permissions import ensure_valid_extension, ensure_wiki_path


def append(vault: Vault, path: str, content: str) -> str:
	"""Append content to an existing document in the wiki."""
	document_path = Path(path)
	ensure_wiki_path(document_path, vault)
	ensure_valid_extension(document_path, 'append')
	vault.append_to_document(document_path, content)
	return f'Appended to {document_path}'
