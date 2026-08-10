from fastmcp import FastMCP
from src.api.train_api import search_station, search_trains, get_railkit_seat_availability

mcp = FastMCP("train_server")

@mcp.tool()
def search_station_tool(name: str):
    """Search for stations by name."""
    return search_station(name)

@mcp.tool()
def search_trains_tool(source: str, destination: str, date: str):
    """Search for trains between two station codes on a given date."""
    return search_trains(source, destination, date)

@mcp.tool()
def get_railkit_availability_tool(train_number: str, source: str, destination: str, date: str, coach: str, quota: str):
    """Get seat availability and fare from RailKit API."""
    return get_railkit_seat_availability(train_number, source, destination, date, coach, quota)

if __name__ == "__main__":
    mcp.run()