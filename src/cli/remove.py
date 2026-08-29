from pathlib import Path

from storage import Vault


def remove(vault: Vault, path: Path) -> None:
	try:
		requested_path = Path(path)
		if not requested_path.is_absolute():
			requested_path = vault.wiki_path / requested_path
		document_path = requested_path.resolve()
		vault.delete_document(document_path)
		print(f"Removed document '{document_path}'.")
	except Exception as e:
		print(f'Error removing document: {e}')
