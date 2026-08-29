import shutil
from pathlib import Path

from storage import Vault


def ingest(vault: Vault, source: Path, destination: Path) -> None:
	try:
		source_path = Path(source).resolve()
		if not source_path.is_file():
			raise FileNotFoundError(f'source document does not exist: {source}')

		destination_path = (vault.wiki_path / Path(destination)).resolve()
		try:
			destination_path.relative_to(vault.wiki_path.resolve())
		except ValueError as exc:
			raise ValueError(
				f'destination must be inside the wiki directory: {destination}'
			) from exc

		if destination_path.exists() and destination_path.is_dir():
			destination_path = destination_path / source_path.name

		destination_path.parent.mkdir(parents=True, exist_ok=True)
		shutil.copy2(source_path, destination_path)
		vault.index_db()
		print(f"Ingested '{source_path}' into '{destination_path}'.")
	except Exception as e:
		print(f'Error ingesting document: {e}')
