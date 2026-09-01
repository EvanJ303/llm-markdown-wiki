import atexit
import json
import shutil
from pathlib import Path
from typer import Typer

from llmwiki.vault_storage import Vault
from llmwiki.utils import init_vault, wrap_partial


vault = init_vault()
atexit.register(vault.close)  # Ensure the vault is closed when the program exits

app = Typer(name='llmwiki')


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


def reindex(vault: Vault) -> None:
	try:
		vault.index_db()
		print(f"Wiki reindexed at '{vault.root}'.")
	except Exception as e:
		print(f'Error reindexing wiki: {e}')


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


def reset(vault: Vault) -> None:
	try:
		vault.reset()
		print("Vault reset successfully.")
	except Exception as e:
		print(f"Error resetting vault: {e}")


def set_location(location: Path) -> None:
	project_dir = Path(__file__).resolve().parent.parent.parent
	try:
		config_path = project_dir / 'config.json'
		with open(config_path, 'r', encoding='utf-8') as f:
			config = json.load(f)

		location_path = Path(location).expanduser().resolve()
		config['vault_location'] = str(location_path)

		with open(config_path, 'w', encoding='utf-8') as f:
			json.dump(config, f, indent=4)
			f.write('\n')

		print(f"Vault location set to '{location_path}'.")
	except Exception as e:
		print(f'Error setting vault location: {e}')


app.command()(wrap_partial(ingest, vault))
app.command()(wrap_partial(reindex, vault))
app.command()(wrap_partial(remove, vault))
app.command()(wrap_partial(reset, vault))
app.command('set-location')(set_location)


if __name__ == '__main__':
	app()
