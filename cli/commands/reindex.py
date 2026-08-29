import json
from pathlib import Path

from ...storage import Vault

project_dir = Path(__file__).resolve().parent.parent.parent


def reindex() -> None:
	try:
		config_path = project_dir / 'config.json'
		with open(config_path, 'r', encoding='utf-8') as f:
			config = json.load(f)

		vault = Vault(Path(config['vault_location']).resolve())
		try:
			vault.index_db()
		finally:
			vault.close()

		print(f"Wiki reindexed at '{Path(config['vault_location']).resolve()}'.")
	except Exception as e:
		print(f'Error reindexing wiki: {e}')
