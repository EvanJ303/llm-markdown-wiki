import atexit

from mcp.server.fastmcp import FastMCP

from llmwiki.mcp_services import append, delete, edit, guide, read, search, write
from llmwiki.utils import init_vault, wrap_partial


vault = init_vault()
atexit.register(vault.close)  # Ensure the vault is closed when the program exits

server = FastMCP('llm-markdown-wiki')
server.add_tool(wrap_partial(write, vault))
server.add_tool(wrap_partial(append, vault))
server.add_tool(wrap_partial(edit, vault))
server.add_tool(wrap_partial(delete, vault))
server.add_tool(wrap_partial(read, vault))
server.add_tool(wrap_partial(search, vault))
server.add_tool(guide)


def main():
    server.run()


if __name__ == '__main__':
    main()
