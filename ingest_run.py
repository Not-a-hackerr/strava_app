import requests
import yaml
import pprint
import pandas
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
    


# GETTING DATA
def get_activities():
    url = "https://www.strava.com/api/v3/athlete/activities"
    params = { "per_page": 5, "page": 1 }
    headers = { "Authorization": f"Bearer {keys()['ACCESS_TOKEN']}" }
    res = requests.get(url, params=params, headers=headers)

    print(res.status_code)
    data = res.json()
    activities = {}
    for i in range(len(data)):
        activities.update({f"activity_{i+1}":
                            {"start_date":data[i]["start_date"],
                            "distance":data[i]["distance"],
                            "moving_time":data[i]["moving_time"],
                            "average_speed":data[i]["average_speed"],
                            "elev_high":data[i]["elev_high"],
                            "elev_low":data[i]["elev_low"],
                            "start_latlng":data[i]["start_latlng"]
                            }
                        })
    return activities


def normalize_times(start_iso: str, moving_seconds: int):
    dt = datetime.fromisoformat(start_iso)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt_utc = dt.astimezone(timezone.utc)
    end_utc = dt_utc + timedelta(seconds=int(moving_seconds or 0))
    return {
        "start_iso_utc": dt_utc.isoformat()[:-9],
        "end_iso_utc": end_utc.isoformat()[:-9]
    }


def get_weather(latitude,longitude,start_datetime,end_datetime,metric):
    if metric == "temperature":
        weather = "temperature_2m"
    elif metric == "humidity":
        weather = "relative_humidity_2m"
    elif metric == "rain":
        weather = "precipitation"
    elif metric == "wind":
        weather = "wind_speed_10m"

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "minutely_15": weather,
        "start_minutely_15":start_datetime,
        "end_minutely_15":end_datetime,
        "timezone": "GMT"
    }
    responses = requests.get(url, params=params).json()
    # print(responses)
    total = sum(responses["minutely_15"][weather])
    length = len(responses["minutely_15"][weather])
    return total / length


# DATABASE CONNECTION
def get_db_conn(path="activities.db"):
    return duckdb.connect(path)

def create_activities_table(conn):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS activities (
        activity_key TEXT,
        start_date TEXT,
        distance DOUBLE,
        moving_time INTEGER,
        average_speed DOUBLE,
        elev_high DOUBLE,
        elev_low DOUBLE,
        start_latlng TEXT
    )
    """)

def get_location():
    pass

def record_activities():
    pass





