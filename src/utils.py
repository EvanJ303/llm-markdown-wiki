import inspect
import json
from functools import partial, update_wrapper
from pathlib import Path

from storage.vault import Vault

def init_vault() -> Vault:
    project_dir = Path(__file__).resolve().parent.parent
    with (project_dir / 'config.json').open(encoding='utf-8') as config_file:
        config = json.load(config_file)

    vault = Vault(Path(config['vault_location']).resolve())
    return vault

def wrap_partial(func: callable, *args: tuple, **kwargs: dict) -> callable:
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
