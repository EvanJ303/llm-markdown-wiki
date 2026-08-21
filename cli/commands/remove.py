import json
import sys
from pathlib import Path

project_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_dir))

from storage import Vault


def remove(path: Path) -> None:
	try:
		config_path = project_dir / 'config.json'
		with open(config_path, 'r', encoding='utf-8') as f:
			config = json.load(f)

		vault = Vault(Path(config['vault_location']).resolve())
		try:
			requested_path = Path(path)
			if not requested_path.is_absolute():
				requested_path = vault.wiki_path / requested_path
			document_path = requested_path.resolve()
			vault.delete_document(document_path)
		finally:
			vault.close()

		print(f"Removed document '{document_path}'.")
	except Exception as e:
		print(f'Error removing document: {e}')
