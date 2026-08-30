from mcp.server.fastmcp import FastMCP

from mcp_services.tools import append, delete, edit, guide, read, search, write
from utils import init_vault, wrap_partial


vault = init_vault()

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
