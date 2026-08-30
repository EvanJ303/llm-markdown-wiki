from typer import Typer

from cli import ingest, reindex, remove, reset, set_location
from utils import init_vault, wrap_partial


vault = init_vault()
app = Typer(name='llmwiki')

app.command()(wrap_partial(ingest, vault))
app.command()(wrap_partial(reindex, vault))
app.command()(wrap_partial(remove, vault))
app.command()(wrap_partial(reset, vault))
app.command('set-location')(set_location)


if __name__ == '__main__':
	try:
		app()
	finally:
		vault.close()
