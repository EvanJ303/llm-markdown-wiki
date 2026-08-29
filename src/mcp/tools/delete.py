from pathlib import Path

from ..permissions import ensure_wiki_path
from ...storage import Vault


def delete(vault: Vault, path: str) -> str:
	"""Delete a document from the wiki."""
	document_path = Path(path)
	ensure_wiki_path(document_path, vault)
	vault.delete_document(document_path)
	return f'Deleted {document_path}'
