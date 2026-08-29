import json
import shutil
from pathlib import Path

from ...storage import Vault

project_dir = Path(__file__).resolve().parent.parent.parent


def reset() -> None:
	try:
		config_path = project_dir / 'config.json'
		with open(config_path, 'r', encoding='utf-8') as f:
			config = json.load(f)

		vault = Vault(Path(config['vault_location']).resolve())
		try:
			for child in vault.wiki_path.iterdir():
				if child.is_dir():
					shutil.rmtree(child)
				else:
					child.unlink()

			vault.conn.execute('DELETE FROM chunks')
			vault.conn.execute('DELETE FROM documents')
			vault.conn.execute("INSERT INTO chunks_fts(chunks_fts) VALUES('rebuild')")
			vault.conn.commit()
		finally:
			vault.close()

		print(f"Wiki reset at '{Path(config['vault_location']).resolve()}'.")
	except Exception as e:
		print(f'Error resetting wiki: {e}')
