import shutil

from ...storage import Vault


def reset(vault: Vault) -> None:
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
		print(f"Wiki reset at '{vault.root}'.")
	except Exception as e:
		print(f'Error resetting wiki: {e}')
