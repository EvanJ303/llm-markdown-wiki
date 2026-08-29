from pathlib import Path

from ...storage import Vault


def read(
	vault: Vault,
	path: str,
	page_start: int | None = None,
	page_end: int | None = None,
) -> dict[str, str | None]:
	"""Read a document, optionally limited to an inclusive page range."""
	document = vault.read_document(Path(path), page_start, page_end)
	return {
		'path': str(document.path),
		'content': document.content,
		'created': document.created,
		'modified': document.modified,
	}
