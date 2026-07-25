from fastmcp import FastMCP
from train_api import search_station, search_trains, get_seat_availability

mcp = FastMCP("train_server")

@mcp.tool()
def search_station_tool(name: str):
    """
    Search for stations by name.
    name: station name or part of the name
    """
    return search_station(name)

@mcp.tool()
def search_trains_tool(source: str , destination: str , date: str):
    """
    Search for trains between two station codes on a given date.
    source: source station code (e.g. 'UJN')
    destination: destination station code (e.g. 'INDB')
    date: travel date in YYYY-MM-DD format
    """
    return search_trains(source, destination, date)

@mcp.tool()
def get_seat_availability_tool(source: str , destination: str , date: str):
    """
    Get seat classes, availability, fare, and confirmation prediction for all trains
    between two stations on a given date.
    source: source station code
    destination: destination station code
    date: travel date
    """
    return get_seat_availability(source, destination, date)


if __name__ == "__main__":
    mcp.run()