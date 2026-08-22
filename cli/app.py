from typer import Typer

from .commands import ingest, init, reindex, remove, reset, set_location

app = Typer(name='llmwiki')

app.command()(init)
app.command()(ingest)
app.command()(reindex)
app.command()(remove)
app.command()(reset)
app.command('set-location')(set_location)


if __name__ == '__main__':
	app()
