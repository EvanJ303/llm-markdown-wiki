import inspect
import json
from functools import partial, update_wrapper
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from storage import Vault
from mcp_services.tools import append, delete, edit, guide, read, search, write


# Create the MCP server and register the wiki tools
project_dir = Path(__file__).resolve().parent.parent
with (project_dir / 'config.json').open(encoding='utf-8') as config_file:
	config = json.load(config_file)

vault = Vault(Path(config['vault_location']).resolve())


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


server = FastMCP('llm-markdown-wiki')
server.add_tool(wrap_partial(write, vault))
server.add_tool(wrap_partial(append, vault))
server.add_tool(wrap_partial(edit, vault))
server.add_tool(wrap_partial(delete, vault))
server.add_tool(wrap_partial(read, vault))
server.add_tool(wrap_partial(search, vault))
server.add_tool(guide)


if __name__ == '__main__':
	try:
		server.run()
	finally:
		vault.close()
