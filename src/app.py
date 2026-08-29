import atexit
import json
from functools import partial
from pathlib import Path

from typer import Typer

from storage import Vault
from cli import ingest, init, reindex, remove, reset, set_location


project_dir = Path(__file__).resolve().parent.parent
with (project_dir / 'config.json').open(encoding='utf-8') as config_file:
	config = json.load(config_file)

vault = Vault(Path(config['vault_location']).resolve())
atexit.register(vault.close)

app = Typer(name='llmwiki')

app.command()(partial(ingest, vault))
app.command()(partial(reindex, vault))
app.command()(partial(remove, vault))
app.command()(partial(reset, vault))
app.command('set-location')(set_location)


if __name__ == '__main__':
	try:
		app()
	finally:
		vault.close()
