import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

_mcp_client = None
_tools = None
_search_station_tool = None
_search_trains_tool = None
_get_railkit_availability_tool = None
_initialized = False
_init_lock = asyncio.Lock()

async def initialize_mcp_client():
    global _mcp_client, _tools, _search_station_tool, _search_trains_tool, _get_railkit_availability_tool, _initialized
    async with _init_lock:
        if _initialized:
            return
        import os
        print("Initializing MCP client...")
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        python_path = os.path.join(project_root, "env5", "Scripts", "python.exe")
        server_script = os.path.join(project_root, "run_server.py")
        _mcp_client = MultiServerMCPClient(
            {
                "train_server": {
                    "command": python_path,
                    "args": [server_script],
                    "transport": "stdio",
                }
            }
        )
        print("Loading MCP tools...")
        _tools = await _mcp_client.get_tools()
        _search_station_tool = next(
            (tool for tool in _tools if tool.name == "search_station_tool"),
            None
        )
        _search_trains_tool = next(
            (tool for tool in _tools if tool.name == "search_trains_tool"),
            None
        )
        _get_railkit_availability_tool = next(
            (tool for tool in _tools if tool.name == "get_railkit_availability_tool"),
            None
        )
        if not all([_search_station_tool, _search_trains_tool, _get_railkit_availability_tool]):
            available = [t.name for t in _tools]
            print(f"Available tools: {available}")
            raise RuntimeError("Not all required tools were loaded")
        _initialized = True
        print("MCP tools loaded successfully!")

async def get_search_station_tool_async():
    if not _initialized:
        await initialize_mcp_client()
    return _search_station_tool

async def get_search_trains_tool_async():
    if not _initialized:
        await initialize_mcp_client()
    return _search_trains_tool

async def get_railkit_availability_tool_async():
    if not _initialized:
        await initialize_mcp_client()
    return _get_railkit_availability_tool

def get_search_station_tool():
    if not _initialized:
        raise RuntimeError("MCP client not initialized. Call initialize_mcp_client() first.")
    return _search_station_tool

def get_search_trains_tool():
    if not _initialized:
        raise RuntimeError("MCP client not initialized. Call initialize_mcp_client() first.")
    return _search_trains_tool

def get_railkit_availability_tool():
    if not _initialized:
        raise RuntimeError("MCP client not initialized. Call initialize_mcp_client() first.")
    return _get_railkit_availability_tool
