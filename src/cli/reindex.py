from storage import Vault


def reindex(vault: Vault) -> None:
	try:
		vault.index_db()
		print(f"Wiki reindexed at '{vault.root}'.")
	except Exception as e:
		print(f'Error reindexing wiki: {e}')
