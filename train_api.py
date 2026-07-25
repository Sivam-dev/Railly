from dotenv import load_dotenv
import os
import requests
from config import RAILRADAR_API_KEY , IRCTC2_API_KEY
load_dotenv()




def get_all_stations() ->dict:
    """"return the full {code : name} map of all stations
    """
    url = "https://api.railradar.in/v1/lookup/stations"
    headers = {
        "Authorization" : f"Bearer{RAILRADAR_API_KEY}"
    }

    response = requests.get(url , headers = headers)
    data = response.json()
    if not data.get("success"):
        raise Exception(f"API error: {data}")

    return data.get("data", {})

def search_station(name :str) ->dict:
    all_stations = get_all_stations()
    matches = {}
    for code , station_name in all_stations.items():
        if name.lower() in station_name.lower():
            matches[code] = station_name
    return matches

def search_trains(source: str , destination: str , date: str):
    """
    Search trains between two station codes on a given date.
    source: source station code (e.g. 'UJN')
    destination: destination station code (e.g. 'INDB')
    date: travel date in YYYY-MM-DD format
    """

    url = f"https://api.railradar.in/v1/trains/between/{source}/{destination}"

    headers = {"Authorization" : f"Bearer : {RAILRADAR_API_KEY}"}
    params = {"date" : date}

    response = requests.get(url , headers = headers , params = params)
    data = response.json()


def get_seat_availability(source: str , destination: str , date: str):
    """
    Get seat classes, availability, fare, and confirmation prediction for all trains
    between two stations on a given date.
    source: source station code
    destination: destination station code
    date: travel date
    """
    url = "https://irctc-api2.p.rapidapi.com/trainAvailability"
    params = {"source":source,"destination":destination,"date":date}
    headers = {
	"x-rapidapi-key": IRCTC2_API_KEY,
	"x-rapidapi-host": "irctc-api2.p.rapidapi.com",
	"Content-Type": "application/json"
    }
    response = requests.get(url , headers = headers  , params = params)
    data = response.json()

    return data
         

