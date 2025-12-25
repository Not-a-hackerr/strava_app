import requests
import yaml
import duckdb
from datetime import datetime, timedelta, timezone

# API KEYS
def keys():
    with open("keys.yml", "r") as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    return data

# CONNECTING TO CONNECTIONS
def replace_access_token():
    url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": keys()['CLIENT_ID'],
        "client_secret": keys()['CLIENT_SECRET'],
        "grant_type": "refresh_token",
        "refresh_token": keys()['REFRESH_TOKEN']
    }
    
    res = requests.post(url, data=payload)
    res = res.json()

    access_token = res['access_token']

    with open('keys.yml', 'r') as f:
        data = yaml.safe_load(f)
        data['ACCESS_TOKEN'] = access_token
    with open('keys.yml', 'w') as f:
        yaml.dump(data, f, sort_keys=False)

# INGESTING DATA
def get_weather(latitude,longitude,start_datetime,end_datetime):
    url = "https://api.open-meteo.com/v1/forecast"

    weather = {}
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "minutely_15": ['temperature_2m','relative_humidity_2m','precipitation','wind_speed_10m'],
        "start_minutely_15":start_datetime,
        "end_minutely_15":end_datetime,
        "timezone": "GMT"}
        
    responses = requests.get(url, params=params).json()
    
    temp = responses['minutely_15']['temperature_2m']
    humid = responses['minutely_15']['relative_humidity_2m']
    rain = responses['minutely_15']['precipitation']
    wind = responses['minutely_15']['wind_speed_10m']

    weather.update({'temperature':sum(temp)/len(temp),
                    'humidity':sum(humid)/len(humid),
                    'rain':sum(rain)/len(rain),
                    'wind_speed':sum(wind)/len(wind)
                    })
    return weather

def get_location(latitude,longitude):
    loc_url = "https://geocode.maps.co/reverse"
    headers = {"Authorization": f"Bearer {keys()['LOC_API_KEY']}"}
    params = {"lat":latitude, "lon":longitude}
    location = requests.get(url=loc_url,headers=headers,params=params).json()
    keyword = list(location["address"].keys())
    if "town" in keyword:
        return {"location": location["address"]["town"]}
    elif "city" in keyword:
        return {"location": location["address"]["city"]}

def get_activities():
    url = "https://www.strava.com/api/v3/athlete/activities"
    params = { "per_page": 5, "page": 1 }
    headers = { "Authorization": f"Bearer {keys()['ACCESS_TOKEN']}" }
    res = requests.get(url, params=params, headers=headers)

    data = res.json()
    activities = {}
    for i in range(len(data)):
        if data[i]['type'] == 'Run':
            activities.update({
                f"run_{i+1}":{
                "activity_id": data[i]["id"],
                "start_datetime":data[i]["start_date"],
                "end_datetime": "null",
                "distance_km": data[i]["distance"],  # raw (meters)
                "moving_time_mins": data[i]["moving_time"],
                "avg_pace_minskm": "null",
                "elev_high":data[i]["elev_high"],
                "elev_low":data[i]["elev_low"],
                "start_latlng":data[i]["start_latlng"]
                                }
                            })
    return activities

# NORMALISING DATA
def normalize_times(start_iso: str, moving_seconds: int):
    dt = datetime.fromisoformat(start_iso)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt_utc = dt.astimezone(timezone.utc)
    end_utc = dt_utc + timedelta(seconds=int(moving_seconds or 0))
    return {
        "start_datetime": dt_utc.isoformat()[:-9],
        "end_datetime": end_utc.isoformat()[:-9]
    }

def normalising_units(run):
    
    distance_km = run['distance_km'] / 1000
    moving_time_mins = run['moving_time_mins'] / 60
    avg_pace_minskm = run['moving_time_mins'] / run['distance_km']

    return {"distance_km":distance_km,
            "moving_time_mins":moving_time_mins,
            "avg_pace_minskm":avg_pace_minskm}

# DATABASE CONNECTION
def get_db_conn(path="activities.db"):
    return duckdb.connect(path)

def create_activities_table(conn):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS activities (
        activity_id TEXT,
        start_date TEXT,
        end_date TEXT,        
        distance_km DOUBLE,
        moving_time_mins INTEGER,
        average_speed DOUBLE,
        elev_high DOUBLE,
        elev_low DOUBLE,
        start_latlng TEXT
    )
    """)

def record_activities():
    pass

# 
try:
    replace_access_token()
    activities = get_activities()

    for i in activities:
        act = activities[i]
        normalized_times = normalize_times(act['start_datetime'], act['moving_time'])
        activities[i].update(normalized_times)

        weath = get_weather(act['start_latlng'][0],act['start_latlng'][1],act['start_datetime'],act['end_datetime'])
        act.update(weath)
    
        location = get_location(act['start_latlng'][0],act['start_latlng'][1])
        activities[i].update(location)

        units = normalising_units(act)
        act.update(units)

except:
    pass

