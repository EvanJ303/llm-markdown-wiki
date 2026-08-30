import atexit
import inspect
import json
from functools import partial, update_wrapper
from pathlib import Path

from typer import Typer

from storage import Vault
from cli import ingest, reindex, remove, reset, set_location


project_dir = Path(__file__).resolve().parent.parent
with (project_dir / 'config.json').open(encoding='utf-8') as config_file:
	config = json.load(config_file)

vault = Vault(Path(config['vault_location']).resolve())
atexit.register(vault.close)


def wrap_partial(func, *args, **kwargs):
	partial_func = partial(func, *args, **kwargs)
	update_wrapper(partial_func, func)

	sig = inspect.signature(func)
	bound_names = set(list(sig.parameters)[:len(args)]) | set(kwargs)
	remaining_params = [
		param for param in sig.parameters.values() if param.name not in bound_names
	]
	partial_func.__signature__ = sig.replace(parameters=remaining_params)
	partial_func.__annotations__ = {
		name: annotation
		for name, annotation in func.__annotations__.items()
		if name not in bound_names
	}
	return partial_func


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
