from typing import TypedDict, Optional
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage , SystemMessage
from langgraph.types import interrupt
from src.server.tools import get_search_station_tool_async, get_search_trains_tool_async, get_railkit_availability_tool_async
from langgraph.graph import StateGraph, END
class TrainState(TypedDict):
    user_query: str
    source: str | None
    destination: str | None
    journey_date: str | None
    budget: int | None
    preferred_departure: str | None
    preferred_arrival: str | None
    preferred_class: str | None
    trains: list
    budget_filtered_trains: list
    alternative_class_trains: list
    time_filtered_trains: list
    ranked_trains: list
    recommended_train: dict | None
    final_response: str | None
    follow_up_question: str | None
    recommendation: dict | None
class extract(BaseModel):
     source: Optional[str]
     destination: Optional[str]
     journey_date: Optional[str]
     budget: Optional[int]
     preferred_departure: Optional[str]
     preferred_arrival: Optional[str]
     preferred_class: Optional[str]
extractor_llm = ChatOllama(model = "qwen2.5:3b")
system_extractor_prompt = """
You are a travel constraint extraction assistant for a train recommendation system.
Your job is to extract ALL travel-related constraints explicitly provided by the user
and return them according to the provided Pydantic schema.
Extract the following information whenever it is present:
- source: The user's starting railway station or location.
- destination: The user's destination railway station or location.
- journey_date: The date on which the user wants to travel in YYYY-MM-DD format.
  If the user provides a date without year, assume the current year (2026).
  Examples: "9th August" → "2026-08-09", "tomorrow" → calculate the actual date,
  "15th" → "2026-MM-15" where MM is current or next month.
- budget: The maximum amount the user is willing to spend on the journey.
- preferred_departure: The user's preferred departure time or time period,
  such as morning, afternoon, evening, night, or a specific time.
- preferred_arrival: The user's preferred arrival time or time period,
  such as morning, afternoon, evening, night, or a specific time.
- preferred_class: The user's preferred travel class or coach type,
  such as Sleeper (SL), AC 3-Tier (3A), AC 2-Tier (2A), AC 1st Class (1A),
  AC Chair Car (CC), Second Sitting (2S), or any other class mentioned.
Rules:
1. Extract only information explicitly stated or clearly implied by the user.
2. NEVER invent, guess, or assume a value that the user did not provide.
3. If a constraint is missing, return None for that field.
4. Preserve the user's budget amount accurately. Do not convert currencies.
5. If the user gives a relative date such as "tomorrow", "next Monday",
   or "this Friday", extract the date expression provided by the user.
6. If the user gives a specific time, preserve it accurately.
7. If the user gives a time period such as "at night" or "in the morning",
   extract that as the corresponding preference.
8. If the user mentions multiple constraints, extract ALL of them.
9. For preferred_class, extract the exact class name or abbreviation mentioned by the user.
10. Do not answer the user's travel request.
11. Do not recommend a train.
12. Do not call any tools or APIs.
13. Your only task is constraint extraction.
"""
llm_with_structure = extractor_llm.with_structured_output(extract)
def constraint_extract(state: TrainState):
     query = state["user_query"]
     response :  extract = llm_with_structure.invoke(
          [
               SystemMessage(content = system_extractor_prompt) , 
               HumanMessage(content = query)])
     return {
    "source": response.source if response.source is not None else state["source"],
    "destination": response.destination if response.destination is not None else state["destination"],
    "journey_date": response.journey_date if response.journey_date is not None else state["journey_date"],
    "budget": response.budget if response.budget is not None else state["budget"],
    "preferred_departure": response.preferred_departure if response.preferred_departure is not None else state["preferred_departure"],
    "preferred_arrival": response.preferred_arrival if response.preferred_arrival is not None else state["preferred_arrival"],
    "preferred_class": response.preferred_class if response.preferred_class is not None else state["preferred_class"],
}
def Missing_constraint(state:TrainState):
     print(f"🔍 Missing_constraint check:")
     print(f"  source: {state['source']}")
     print(f"  destination: {state['destination']}")
     print(f"  journey_date: {state['journey_date']}")
     print(f"  budget: {state['budget']}")
     print(f"  preferred_departure: {state['preferred_departure']}")
     print(f"  preferred_arrival: {state['preferred_arrival']}")
     print(f"  preferred_class: {state['preferred_class']}")
     missing = []
     if state["source"] is None:
          missing.append("source")
     if state["destination"] is None:
          missing.append("destination")
     if state["journey_date"] is None:
          missing.append("journey_date")
     if state["budget"] is None:
          missing.append("budget")
     print(f"  missing: {missing}")
     if not missing:
          print("  ✅ No missing constraints, continuing...")
          return {}
     print(f"  ❌ Found missing constraints: {missing}")
     question = "Please provide the following:\n"
     for item in missing:
          question += f"\n {item}"
     answer = interrupt(question)
     return {"user_query" : state["user_query"] + "\n" + answer}
async def resolve_station(station_name: str, max_retries: int = 3, auto_select_first: bool = False) -> str:
    search_station_tool = await get_search_station_tool_async()
    if not station_name or not station_name.strip():
        if max_retries <= 0:
            raise ValueError("Maximum retries exceeded. No valid station name provided.")
        question = "Please provide a valid station name:"
        user_reply = interrupt(question)
        return await resolve_station(user_reply, max_retries - 1)
    try:
        result = await search_station_tool.ainvoke({"name": station_name.strip()})
        if isinstance(result, list) and len(result) > 0:
            import json
            text_content = result[0].get('text', '{}')
            matches = json.loads(text_content)
        elif hasattr(result, 'content'):
            matches = result.content if isinstance(result.content, dict) else {}
        elif isinstance(result, dict):
            matches = result
        else:
            matches = {}
    except Exception as e:
        if max_retries <= 0:
            raise ValueError(f"Maximum retries exceeded. Error: {str(e)}")
        question = f"Error searching for '{station_name}': {str(e)}\nPlease provide a valid station name:"
        user_reply = interrupt(question)
        return await resolve_station(user_reply, max_retries - 1)
    if not matches:
        if max_retries <= 0:
            raise ValueError(f"No stations found for '{station_name}' after maximum retries.")
        question = f"No stations found for '{station_name}'. Please provide a valid station name:"
        user_reply = interrupt(question)
        return await resolve_station(user_reply, max_retries - 1)
    elif len(matches) == 1:
        return list(matches.keys())[0]
    else:
        if auto_select_first:
            first_code = list(matches.keys())[0]
            first_name = matches[first_code]
            print(f"🚂 Auto-selected: {first_code} ({first_name}) for '{station_name}'")
            return first_code
        station_list = "\n".join([f"  {code}: {name}" for code, name in matches.items()])
        question = (
            f"Multiple stations found for '{station_name}':\n\n{station_list}\n\n"
            f"Please enter the station code you want (e.g., UJN, NDLS):"
        )
        user_reply = interrupt(question)
        if not user_reply or not user_reply.strip():
            return list(matches.keys())[0]
        user_code = user_reply.strip().upper()
        if user_code in matches:
            return user_code
        else:
            error_question = (
                f"Invalid code '{user_reply}'. Please choose from:\n\n{station_list}\n\n"
                f"Enter the station code:"
            )
            user_reply = interrupt(error_question)
            if user_reply and user_reply.strip():
                user_code = user_reply.strip().upper()
                if user_code in matches:
                    return user_code
            return list(matches.keys())[0]
async def Train_details_node(state: TrainState):
    print("🚂 Starting Train_details_node...")
    print(f"🔍 Resolving stations: source='{state['source']}', destination='{state['destination']}'")
    try:
        source_code = await resolve_station(state["source"], auto_select_first=True)
        print(f"✅ Source resolved: {state['source']} -> {source_code}")
    except Exception as e:
        print(f"❌ Source resolution failed: {e}")
        raise
    try:
        destination_code = await resolve_station(state["destination"], auto_select_first=True)
        print(f"✅ Destination resolved: {state['destination']} -> {destination_code}")
    except Exception as e:
        print(f"❌ Destination resolution failed: {e}")
        raise
    journey_date = state["journey_date"]
    from datetime import datetime
    date_formats = [
        "%Y-%m-%d",           # 2026-08-09
        "%d-%m-%Y",           # 09-08-2026
        "%d/%m/%Y",           # 09/08/2026
        "%Y/%m/%d",           # 2026/08/09
        "%d %B %Y",           # 9 August 2026
        "%d %b %Y",           # 9 Aug 2026
        "%B %d, %Y",          # August 9, 2026
    ]
    formatted_date = None
    for fmt in date_formats:
        try:
            date_obj = datetime.strptime(journey_date, fmt)
            formatted_date = date_obj.strftime("%d-%m-%Y")
            print(f"📅 Date converted: {journey_date} → {formatted_date}")
            break
        except:
            continue
    if formatted_date is None:
        try:
            if journey_date and len(journey_date.split()) == 2:
                journey_date_with_year = f"{journey_date} 2026"
                for fmt in ["%d %B %Y", "%dth %B %Y", "%dnd %B %Y", "%drd %B %Y", "%dst %B %Y"]:
                    try:
                        date_obj = datetime.strptime(journey_date_with_year, fmt)
                        formatted_date = date_obj.strftime("%d-%m-%Y")
                        print(f"📅 Date converted (added year): {journey_date} → {formatted_date}")
                        break
                    except:
                        continue
        except:
            pass
    if formatted_date is None:
        formatted_date = journey_date
        print(f"⚠️ Could not parse date format: {formatted_date}")
        print(f"⚠️ API may reject this date. Please use YYYY-MM-DD format.")
    print(f"🔍 Searching trains with RailRadar API: {source_code} → {destination_code} on {formatted_date}")
    search_trains_tool = await get_search_trains_tool_async()
    formatted_date_yyyy = formatted_date
    try:
        from datetime import datetime
        date_obj = datetime.strptime(formatted_date, "%d-%m-%Y")
        formatted_date_yyyy = date_obj.strftime("%Y-%m-%d")
    except:
        pass
    result = await search_trains_tool.ainvoke({
        "source": source_code,
        "destination": destination_code,
        "date": formatted_date_yyyy
    })
    train_details = []
    if isinstance(result, list) and len(result) > 0:
        import json
        text_content = result[0].get('text', '{}')
        api_response = json.loads(text_content)
        if api_response.get('success'):
            data = api_response.get('data', {})
            trains_array = data.get('trains', [])
            print(f"✅ Found {len(trains_array)} trains from RailRadar API")
            for train_info in trains_array:
                train_obj = train_info.get('train', {})
                from_info = train_info.get('from', {})
                to_info = train_info.get('to', {})
                train_details.append({
                    "trainNumber": train_obj.get('number'),
                    "trainName": train_obj.get('name'),
                    "from": {
                        "code": from_info.get('code'),
                        "name": from_info.get('name')
                    },
                    "to": {
                        "code": to_info.get('code'),
                        "name": to_info.get('name')
                    },
                    "departure": from_info.get('departure'),
                    "arrival": to_info.get('arrival'),
                    "duration": f"{train_info.get('duration', 0) // 60}h {train_info.get('duration', 0) % 60}m",
                    "distanceKm": train_info.get('distance'),
                    "classAvailability": []  # Note: RailRadar doesn't provide class/fare info
                })
            print(f"✅ Processed {len(train_details)} trains (note: fare info not available from RailRadar)")
        else:
            error_msg = api_response.get('error', 'Unknown error')
            print(f"❌ API returned error: {error_msg}")
    else:
        print(f"⚠️ Unexpected result format: {type(result)}")
    return {"trains": train_details}
def class_budget_filter(state: TrainState):
    budget = state["budget"]
    preferred_class = state["preferred_class"]
    trains = state["time_filtered_trains"]
    
    print(f"💰 Filtering {len(trains)} trains by seat availability and budget...")
    
    filtered_trains = []
    alternative_trains = []
    trains_without_data = 0
    
    for train in trains:
        seat_data = train.get("seat_data")
        
        if not seat_data:
            print(f"  ⚠️ Train {train.get('trainNumber')}: No seat data, skipping")
            trains_without_data += 1
            continue
        
        source = seat_data.get("source")
        data = seat_data.get("data")
        
        if source == "railkit":
            train_info = data.get("train", {})
            fare_info = data.get("fare", {})
            availability_list = data.get("availability", [])
            
            if not availability_list:
                print(f"  ⚠️ Train {train.get('trainNumber')}: No availability data")
                trains_without_data += 1
                continue
            
            first_day = availability_list[0]
            status = first_day.get("status", "")
            avail_text = first_day.get("availabilityText", "")
            total_fare = fare_info.get("totalFare", 0)
            
            print(f"  🚂 Train {train.get('trainNumber')} (RailKit): Fare ₹{total_fare}, Status: {status}, {avail_text}")
            
            # Check if seats are available (not waitlist)
            if status == "WAITLIST" and "WL" in avail_text:
                print(f"     ❌ Waitlist only, excluding")
                continue
            
            if total_fare > budget:
                print(f"     ❌ Over budget")
                continue
            
            train_copy = train.copy()
            train_copy["selected_classes"] = [{
                "class": train_info.get("travelClass", preferred_class or "3A"),
                "fare": str(total_fare),
                "availability": avail_text,
                "displayStatus": first_day.get("prediction", avail_text),
                "status": status
            }]
            filtered_trains.append(train_copy)
            
        elif source == "irctc2":
            classes = data.get("classes", [])
            if not classes:
                print(f"  ⚠️ Train {train.get('trainNumber')}: No class data from IRCTC2")
                trains_without_data += 1
                continue
            
            print(f"  🚂 Train {train.get('trainNumber')} (IRCTC2): {len(classes)} classes")
            
            valid_classes = []
            for cls in classes:
                avail = cls.get("availability", "")
                fare = cls.get("fare", 0)
                
                try:
                    fare_int = int(fare) if fare else 0
                except:
                    fare_int = 0
                
                if "NOT AVAILABLE" not in avail.upper() and fare_int <= budget:
                    valid_classes.append(cls)
            
            if not valid_classes:
                print(f"     ❌ No available classes within budget")
                continue
            
            train_copy = train.copy()
            train_copy["selected_classes"] = valid_classes
            filtered_trains.append(train_copy)
        
        print(f"     ✅ Train passed filter")
    
    if trains_without_data > 0:
        print(f"⚠️ {trains_without_data} trains skipped due to unavailable seat data")
    
    print(f"✅ {len(filtered_trains)} trains passed seat availability and budget filter")
    
    return {"budget_filtered_trains": filtered_trains, "alternative_class_trains": alternative_trains}
def time_preference_filter(state: TrainState):
    trains = state["trains"]
    preferred_departure = state.get("preferred_departure")
    preferred_arrival = state.get("preferred_arrival")
    TIME_PERIODS = {
        "morning": (5, 12),
        "afternoon": (12, 17),
        "evening": (17, 21),
        "night": (21, 5),
        "early morning": (5, 8),
        "late night": (23, 2),
    }
    def parse_time_to_minutes(time_str):
        if not time_str:
            return None
        time_str = time_str.strip()
        try:
            if ":" in time_str:
                parts = time_str.split(":")
                hours = int(parts[0])
                minutes = int(parts[1])
                return hours * 60 + minutes
            else:
                hours = int(time_str)
                return hours * 60
        except (ValueError, IndexError):
            return None
    def matches_time_period(time_str, period_text):
        if not time_str or not period_text:
            return False
        time_minutes = parse_time_to_minutes(time_str)
        if time_minutes is None:
            return False
        period_text_lower = period_text.lower()
        for period_name, (start_hour, end_hour) in TIME_PERIODS.items():
            if period_name in period_text_lower:
                start_minutes = start_hour * 60
                end_minutes = end_hour * 60
                if start_hour > end_hour:
                    return time_minutes >= start_minutes or time_minutes < end_minutes
                else:
                    return start_minutes <= time_minutes < end_minutes
        if "after" in period_text_lower:
            parts = period_text_lower.split("after")
            if len(parts) > 1:
                reference_time = parse_time_to_minutes(parts[1].strip())
                if reference_time is not None:
                    return time_minutes >= reference_time
        if "before" in period_text_lower or "by" in period_text_lower:
            for keyword in ["before", "by"]:
                if keyword in period_text_lower:
                    parts = period_text_lower.split(keyword)
                    if len(parts) > 1:
                        reference_time = parse_time_to_minutes(parts[1].strip())
                        if reference_time is not None:
                            return time_minutes <= reference_time
        reference_time = parse_time_to_minutes(period_text)
        if reference_time is not None:
            return abs(time_minutes - reference_time) <= 30
        return False
    def score_train(train):
        score = 0
        departure_time = train.get("departure", "")
        arrival_time = train.get("arrival", "")
        if preferred_departure:
            if matches_time_period(departure_time, preferred_departure):
                score += 100
        else:
            dep_minutes = parse_time_to_minutes(departure_time)
            if dep_minutes and 360 <= dep_minutes < 720:
                score += 50
        if preferred_arrival:
            if matches_time_period(arrival_time, preferred_arrival):
                score += 100
        else:
            arr_minutes = parse_time_to_minutes(arrival_time)
            if arr_minutes and 360 <= arr_minutes < 1320:
                score += 30
        duration_str = train.get("duration", "")
        try:
            hours = 0
            minutes = 0
            if "h" in duration_str:
                hours = int(duration_str.split("h")[0].strip())
            if "m" in duration_str:
                minutes = int(duration_str.split("h")[-1].replace("m", "").strip())
            total_minutes = hours * 60 + minutes
            score += max(0, 50 - (total_minutes // 30))
        except (ValueError, IndexError):
            pass
        rating = train.get("rating", 0)
        try:
            score += float(rating) * 10
        except (ValueError, TypeError):
            pass
        return score
    scored_trains = []
    for train in trains:
        train_score = score_train(train)
        include_train = True
        if preferred_departure:
            if not matches_time_period(train.get("departure", ""), preferred_departure):
                include_train = False
        if preferred_arrival:
            if not matches_time_period(train.get("arrival", ""), preferred_arrival):
                include_train = False
        if include_train:
            scored_trains.append((train_score, train))
    scored_trains.sort(key=lambda x: x[0], reverse=True)
    filtered_trains = [train for score, train in scored_trains]
    if not filtered_trains:
        all_scored = [(score_train(train), train) for train in trains]
        all_scored.sort(key=lambda x: x[0], reverse=True)
        filtered_trains = [train for score, train in all_scored]
    return {"time_filtered_trains": filtered_trains}

async def fetch_railkit_data_node(state: TrainState):
    """Fetch seat availability using hybrid approach: RailKit → IRCTC2 fallback"""
    trains = state["time_filtered_trains"]
    source_code = None
    dest_code = None
    
    for train in trains:
        if train.get("from", {}).get("code"):
            source_code = train["from"]["code"]
            dest_code = train["to"]["code"]
            break
    
    if not source_code or not dest_code:
        print("⚠️ Cannot fetch seat data: missing station codes")
        return {}
    
    journey_date = state["journey_date"]
    from datetime import datetime
    try:
        date_obj = datetime.strptime(journey_date, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%d-%m-%Y")
    except:
        formatted_date = journey_date
    
    CLASS_MAP = {
        "Sleeper": "SL",
        "SL": "SL",
        "AC 3-Tier": "3A",
        "3A": "3A",
        "AC 2-Tier": "2A",
        "2A": "2A",
        "AC 1st Class": "1A",
        "1A": "1A",
        "AC Chair Car": "CC",
        "CC": "CC",
        "Second Sitting": "2S",
        "2S": "2S",
    }
    
    preferred_class = state.get("preferred_class")
    coach_code = CLASS_MAP.get(preferred_class, "3A") if preferred_class else "3A"
    
    # Limit to top 3 trains to reduce API calls
    MAX_TRAINS_TO_CHECK = 3
    trains_to_check = trains[:MAX_TRAINS_TO_CHECK]
    
    print(f"💳 Fetching seat data for top {len(trains_to_check)} trains (out of {len(trains)} total, class: {coach_code}, quota: GN)...")
    
    from src.api.train_api import get_seat_availability_hybrid
    
    enriched_trains = []
    for train in trains_to_check:
        train_number = train.get("trainNumber")
        print(f"  🎫 Fetching seat data for train {train_number}...")
        
        try:
            result = get_seat_availability_hybrid(str(train_number), source_code, dest_code, formatted_date, coach_code, "GN")
            
            if result:
                train_copy = train.copy()
                train_copy["seat_data"] = result
                enriched_trains.append(train_copy)
                print(f"     ✅ Got data from {result['source'].upper()}")
            else:
                enriched_trains.append(train)
                print(f"     ⚠️ No seat data available")
                
        except Exception as e:
            print(f"     ❌ Error: {e}")
            enriched_trains.append(train)
    
    # Add remaining trains without seat data (won't pass filter anyway)
    for train in trains[MAX_TRAINS_TO_CHECK:]:
        enriched_trains.append(train)
    
    print(f"💳 Enriched {len(enriched_trains)} trains (checked {len(trains_to_check)} for seats)")
    return {"time_filtered_trains": enriched_trains}

def rank_trains(state: TrainState):
    trains = state["budget_filtered_trains"]
    ranked_trains = []
    for train in trains:
        score = 0
        total_seats = 0
        available_seats = 0
        if "selected_classes" in train:
            for coach in train["selected_classes"]:
                availability = coach.get("availability", "")
                if "AVAILABLE" in availability.upper() or "AVBL" in availability.upper():
                    if "CURR_AVBL" in availability or "CURR_AVL" in availability:
                        try:
                            seats = int(''.join(filter(str.isdigit, availability)))
                            available_seats += seats
                            total_seats += seats
                            score += 50
                        except ValueError:
                            score += 30
                    elif "GNWL" in availability or "RLWL" in availability:
                        score += 10
                    else:
                        score += 30
                elif "NOT AVAILABLE" in availability.upper():
                    score += 0
                else:
                    score += 20
        if "selected_classes" in train:
            total_fare = 0
            count = 0
            for coach in train["selected_classes"]:
                try:
                    fare = int(coach.get("fare", "0"))
                    total_fare += fare
                    count += 1
                except (ValueError, TypeError):
                    pass
            if count > 0:
                avg_fare = total_fare / count
                budget = state.get("budget", 5000)
                if avg_fare <= budget * 0.5:
                    score += 50
                elif avg_fare <= budget * 0.75:
                    score += 30
                elif avg_fare <= budget:
                    score += 10
        departure_time = train.get("departure", "")
        arrival_time = train.get("arrival", "")
        try:
            if ":" in departure_time:
                dep_hour = int(departure_time.split(":")[0])
                if 6 <= dep_hour < 12:
                    score += 30
                elif 12 <= dep_hour < 18:
                    score += 20
                elif 18 <= dep_hour < 22:
                    score += 25
        except (ValueError, IndexError):
            pass
        try:
            if ":" in arrival_time:
                arr_hour = int(arrival_time.split(":")[0])
                if 6 <= arr_hour < 22:
                    score += 20
        except (ValueError, IndexError):
            pass
        duration_str = train.get("duration", "")
        try:
            hours = 0
            minutes = 0
            if "h" in duration_str:
                hours = int(duration_str.split("h")[0].strip())
            if "m" in duration_str:
                minutes = int(duration_str.split("h")[-1].replace("m", "").strip())
            total_minutes = hours * 60 + minutes
            if total_minutes < 360:
                score += 50
            elif total_minutes < 720:
                score += 30
            elif total_minutes < 1440:
                score += 10
        except (ValueError, IndexError):
            pass
        rating = train.get("rating", 0)
        try:
            score += float(rating) * 10
        except (ValueError, TypeError):
            pass
        train_copy = train.copy()
        train_copy["score"] = score
        ranked_trains.append(train_copy)
    ranked_trains = sorted(
        ranked_trains,
        key=lambda train: train["score"],
        reverse=True
    )
    return {
        "ranked_trains": ranked_trains
    }
def generate_recommendation(state: TrainState):
    ranked_trains = state["ranked_trains"]
    alternative_trains = state.get("alternative_class_trains", [])
    
    if not ranked_trains:
        final_response = (
            f"Sorry, no trains found matching your criteria:\n"
            f"- From: {state['source']}\n"
            f"- To: {state['destination']}\n"
            f"- Date: {state['journey_date']}\n"
        )
        if state.get("preferred_class"):
            final_response += f"- Preferred Class: {state['preferred_class']}\n"
        if state.get("preferred_departure"):
            final_response += f"- Departure: {state['preferred_departure']}\n"
        if state.get("preferred_arrival"):
            final_response += f"- Arrival: {state['preferred_arrival']}\n"
        
        final_response += "\nPlease try:\n- A different date\n- Different time preferences\n- Another route"
        
        return {
            "recommended_train": None,
            "final_response": final_response
        }
    
    best_train = ranked_trains[0]
    train_number = best_train.get("trainNumber", "N/A")
    train_name = best_train.get("trainName", "N/A")
    departure = best_train.get("departure", "N/A")
    arrival = best_train.get("arrival", "N/A")
    duration = best_train.get("duration", "N/A")
    score = best_train.get("score", 0)
    from_station = best_train.get("from", {}).get("name", state["source"])
    to_station = best_train.get("to", {}).get("name", state["destination"])
    fare = "Check with railway"
    class_type = state.get("preferred_class", "All classes")
    
    if "selected_classes" in best_train and best_train["selected_classes"]:
        first_class = best_train["selected_classes"][0]
        fare_val = first_class.get("fare", "")
        if fare_val and fare_val != "N/A" and fare_val != "0":
            fare = fare_val
        class_type = first_class.get("class", class_type)
    
    best_train_with_fare = best_train.copy()
    best_train_with_fare["fare"] = fare
    best_train_with_fare["class"] = class_type
    
    final_response = f"🚂 Recommended Train:\n\n"
    final_response += f"Train: {train_number} - {train_name}\n"
    final_response += f"From: {from_station} at {departure}\n"
    final_response += f"To: {to_station} at {arrival}\n"
    final_response += f"Duration: {duration}\n"
    final_response += f"Match Score: {score}/240\n\n"
    
    if not best_train.get("has_preferred_class", True) and state.get("preferred_class"):
        final_response += f"⚠️ Note: {state['preferred_class']} class not available. Showing alternative classes:\n\n"
    
    if "selected_classes" in best_train:
        final_response += "Available Classes:\n"
        for coach in best_train["selected_classes"]:
            class_name = coach.get("class", "N/A")
            fare = coach.get("fare", "N/A")
            availability = coach.get("availability", "N/A")
            display_status = coach.get("displayStatus", "")
            final_response += f"  • {class_name}: ₹{fare} - {display_status or availability}\n"
    
    rating = best_train.get("rating")
    if rating:
        final_response += f"\nRating: ⭐ {rating}/5\n"
    distance = best_train.get("distanceKm")
    if distance:
        final_response += f"Distance: {distance} km\n"
    pantry = best_train.get("pantry")
    if pantry:
        final_response += f"Pantry: {pantry}\n"
    
    if len(ranked_trains) > 1:
        final_response += f"\n📋 {len(ranked_trains) - 1} other train(s) also available.\n"
    
    return {
        "recommended_train": best_train_with_fare,
        "final_response": final_response
    }
def missing_constraints_router(state: TrainState):
    """
    Router to check if required constraints are missing.
    Returns 'missing' if any required field is None, else 'complete'.
    Only checks REQUIRED fields (source, destination, date, budget).
    Optional fields: preferred_departure, preferred_arrival, preferred_class
    """
    required_fields = [
        "source",
        "destination", 
        "journey_date",
        "budget"
    ]
    for field in required_fields:
        if state.get(field) is None:
            return "missing"
    return "complete"
def refinement_router(state: TrainState):
    """
    Router to check if user wants to refine the recommendation.
    Returns 'refine' if user wants changes, else 'end'.
    Note: This is a placeholder. In a real implementation,
    you would check for follow-up user input.
    """
    follow_up = state.get("follow_up_question")
    if follow_up:
        return "refine"
    return "end"
def build_train_recommendation_graph():
    """
    Build the complete train recommendation workflow graph.
    """
    workflow = StateGraph(TrainState)
    workflow.add_node("constraint_extract", constraint_extract)
    workflow.add_node("missing_constraint", Missing_constraint)
    workflow.add_node("fetch_train_details", Train_details_node)
    workflow.add_node("timing_filter", time_preference_filter)
    workflow.add_node("fetch_railkit_data", fetch_railkit_data_node)
    workflow.add_node("class_budget_filter", class_budget_filter)
    workflow.add_node("rank_trains", rank_trains)
    workflow.add_node("recommendation", generate_recommendation)
    workflow.set_entry_point("constraint_extract")
    workflow.add_edge("constraint_extract", "missing_constraint")
    workflow.add_conditional_edges(
        "missing_constraint",
        missing_constraints_router,
        {
            "missing": "constraint_extract",
            "complete": "fetch_train_details"
        }
    )
    workflow.add_edge("fetch_train_details", "timing_filter")
    workflow.add_edge("timing_filter", "fetch_railkit_data")
    workflow.add_edge("fetch_railkit_data", "class_budget_filter")
    workflow.add_edge("class_budget_filter", "rank_trains")
    workflow.add_edge("rank_trains", "recommendation")
    workflow.add_conditional_edges(
        "recommendation",
        refinement_router,
        {
            "refine": "constraint_extract",
            "end": END
        }
    )
    return workflow.compile()
if __name__ == "__main__":
    import asyncio
    async def main():
        print("🚀 Starting train recommendation workflow...")
        graph = build_train_recommendation_graph()
        initial_state = {
            "user_query": "I want to travel from MUMBAI CENTRAL to NEW DELHI on 2026-08-15 with budget 2000, 3A class, morning departure, evening arrival",
            "source": None,
            "destination": None,
            "journey_date": None,
            "budget": None,
            "preferred_departure": None,
            "preferred_arrival": None,
            "preferred_class": None,
            "trains": [],
            "budget_filtered_trains": [],
            "time_filtered_trains": [],
            "ranked_trains": [],
            "recommended_train": None,
            "final_response": None,
            "follow_up_question": None,
            "recommendation": None
        }
        print(f"📝 Initial query: {initial_state['user_query']}")
        try:
            result = await graph.ainvoke(initial_state)
            print(f"\n🔍 Debug - Final state keys:")
            for key, value in result.items():
                if key == "trains" and isinstance(value, list) and value:
                    print(f"  {key}: list with {len(value)} items")
                    print(f"    → Train details: {value[0] if value else 'none'}")
                elif isinstance(value, (list, dict)) and value:
                    print(f"  {key}: {type(value).__name__} with {len(value)} items")
                elif value is not None:
                    print(f"  {key}: {value}")
                else:
                    print(f"  {key}: None")
            print("\n" + "="*60)
            print("FINAL RECOMMENDATION")
            print("="*60)
            print(result.get("final_response", "No recommendation generated"))
            print("="*60)
        except Exception as e:
            print(f"❌ Error during execution: {e}")
            import traceback
            traceback.print_exc()
    asyncio.run(main())
