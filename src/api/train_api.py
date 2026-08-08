from dotenv import load_dotenv
import os
import requests
from src.config.config import RAILRADAR_API_KEY, RAILKIT_API_KEY, IRCTC2_API_KEY
load_dotenv()

def get_all_stations() ->dict:
    url = "https://api.railradar.in/v1/lookup/stations"
    headers = {
        "Authorization": f"Bearer {RAILRADAR_API_KEY}"
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
    url = f"https://api.railradar.in/v1/trains/between/{source}/{destination}"
    headers = {"Authorization": f"Bearer {RAILRADAR_API_KEY}"}
    params = {"date": date}
    response = requests.get(url , headers = headers , params = params)
    data = response.json()
    return data

def get_seat_availability(source: str , destination: str , date: str):
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

def get_train_fare_data(train_number: str, source: str, destination: str, date: str):
    url = "https://irctc-api2.p.rapidapi.com/trainAvailability"
    params = {"source": source, "destination": destination, "date": date}
    headers = {
        "x-rapidapi-key": IRCTC2_API_KEY,
        "x-rapidapi-host": "irctc-api2.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    try:
        print(f"    Calling IRCTC2 API: {source} -> {destination} on {date}")
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"    Response status: {response.status_code}")
        print(f"    Response preview: {response.text[:300]}")
        
        if response.status_code != 200:
            print(f"    Non-200 status code: {response.text[:500]}")
            return None
        
        if not response.text or response.text.strip() == "":
            print(f"    Empty response from API")
            return None
            
        data = response.json()
        print(f"    JSON parsed successfully")
        
        if not data.get("success"):
            print(f"    API returned success=false: {data.get('error', 'Unknown error')}")
            return None
            
        trains = data.get("data", [])
        if isinstance(trains, dict):
            trains = trains.get("trains", [])
        print(f"    Found {len(trains)} trains in IRCTC2 response")
        
        for train in trains:
            if str(train.get("trainNumber")) == str(train_number):
                class_avail = train.get("classAvailability", [])
                print(f"    Found train {train_number} with {len(class_avail)} classes")
                return class_avail
        
        print(f"    Train {train_number} not found in IRCTC2 response")
        return None
    except requests.exceptions.Timeout:
        print(f"    Request timeout for train {train_number}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"    Request error for train {train_number}: {e}")
        return None
    except Exception as e:
        print(f"    Error fetching fare for train {train_number}: {e}")
        return None


def get_railkit_seat_availability(train_number: str, source: str, destination: str, date: str, coach: str = "3A", quota: str = "GN"):
    print(f"    Calling RailKit API (via SDK): Train {train_number}, {source} -> {destination} on {date}, class {coach}")
    
    try:
        import subprocess
        import json
        
        result = subprocess.run(
            ['node', 'railkit_wrapper.js', str(train_number), source, destination, date, coach, quota],
            cwd=os.path.dirname(__file__) or os.getcwd(),
            capture_output=True,
            text=True,
            timeout=35,
            env={**os.environ, 'RAILKIT_API_KEY': RAILKIT_API_KEY}
        )
        
        if result.returncode != 0:
            print(f"    RailKit SDK call failed: {result.stderr[:200]}")
            return None
        
        data = json.loads(result.stdout.strip())
        
        if not data.get("success"):
            print(f"    API returned success=false: {data.get('error', 'Unknown error')}")
            return None
        
        print(f"    Got seat availability data from RailKit SDK!")
        return data.get("data")
        
    except subprocess.TimeoutExpired:
        print(f"    Request timeout after 35 seconds")
        return None
    except json.JSONDecodeError as e:
        print(f"    JSON decode error: {str(e)[:100]}")
        print(f"    Raw output: {result.stdout[:200]}")
        return None
    except Exception as e:
        print(f"    Error: {str(e)[:150]}")
        return None


def get_seat_availability_hybrid(train_number: str, source: str, destination: str, date: str, coach: str = "3A", quota: str = "GN"):
    print(f"  Trying RailKit API first...")
    railkit_result = get_railkit_seat_availability(train_number, source, destination, date, coach, quota)
    
    if railkit_result:
        return {"source": "railkit", "data": railkit_result}
    
    print(f"  RailKit failed, falling back to IRCTC2 API...")
    
    url = "https://irctc-api2.p.rapidapi.com/trainAvailability"
    headers = {
        "x-rapidapi-key": IRCTC2_API_KEY,
        "x-rapidapi-host": "irctc-api2.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    params = {"source": source, "destination": destination, "date": date}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list):
                for train_data in data:
                    if str(train_data.get("train_number")) == str(train_number):
                        print(f"    Got data from IRCTC2 API")
                        return {"source": "irctc2", "data": train_data}
        print(f"    IRCTC2 also failed")
        return None
    except Exception as e:
        print(f"    IRCTC2 error: {e}")
        return None
