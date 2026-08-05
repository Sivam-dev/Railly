"""
MCP Tools Module

This module handles loading and providing access to MCP tools.
Tools are lazy-loaded on first use to avoid connection issues at import time.
"""

import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient


# Global variables for tools (lazy loaded)
_tools = None
_search_station_tool = None
_search_trains_tool = None
_get_seat_availability_tool = None


def _get_tools():
    """Lazy load MCP tools only when needed."""
    global _tools, _search_station_tool, _search_trains_tool, _get_seat_availability_tool
    
    if _tools is None:
        async def load_tools():
            client = MultiServerMCPClient(
                {
                    "train_server": {
                        "command": "python",
                        "args": ["server.py"],
                        "transport": "stdio",
                    }
                }
            )
            return await client.get_tools()
        
        _tools = asyncio.run(load_tools())
        
        _search_station_tool = next(
            tool for tool in _tools if tool.name == "search_station_tool"
        )
        
        _search_trains_tool = next(
            tool for tool in _tools if tool.name == "search_trains_tool"
        )
        
        _get_seat_availability_tool = next(
            tool for tool in _tools if tool.name == "get_seat_availability_tool"
        )
    
    return _search_station_tool, _search_trains_tool, _get_seat_availability_tool


def get_search_station_tool():
    """Get the search_station_tool."""
    tools = _get_tools()
    return tools[0]


def get_search_trains_tool():
    """Get the search_trains_tool."""
    tools = _get_tools()
    return tools[1]


def get_seat_availability_tool():
    """Get the get_seat_availability_tool."""
    tools = _get_tools()
    return tools[2]
