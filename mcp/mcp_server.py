import json
from functools import partial
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from ..storage import Vault

from .tools.append import append
from .tools.delete import delete
from .tools.edit import edit
from .tools.guide import guide
from .tools.read import read
from .tools.search import search
from .tools.write import write


# Create the MCP server and register the wiki tools
project_dir = Path(__file__).resolve().parent.parent
with (project_dir / 'config.json').open(encoding='utf-8') as config_file:
	config = json.load(config_file)

vault = Vault(Path(config['vault_location']).resolve())
server = FastMCP('llm-markdown-wiki')
server.add_tool(partial(write, vault), name='write', description=write.__doc__)
server.add_tool(partial(append, vault), name='append', description=append.__doc__)
server.add_tool(partial(edit, vault), name='edit', description=edit.__doc__)
server.add_tool(partial(delete, vault), name='delete', description=delete.__doc__)
server.add_tool(partial(read, vault), name='read', description=read.__doc__)
server.add_tool(partial(search, vault), name='search', description=search.__doc__)
server.add_tool(guide, name='guide', description=guide.__doc__)

if __name__ == '__main__':
	server.run()
