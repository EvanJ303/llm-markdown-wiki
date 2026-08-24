from pathlib import Path

from storage import Vault


def search(vault: Vault, query: str, scope: str | None = None) -> list[dict[str, str | int | None]]:
	"""Search indexed wiki content, optionally restricted to a wiki path."""
	hits = vault.search(query, Path(scope) if scope is not None else None)
	return [
		{'path': str(hit.path), 'snippet': hit.snippet, 'page': hit.page}
		for hit in hits
	]
