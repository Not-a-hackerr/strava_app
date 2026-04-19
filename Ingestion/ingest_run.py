from datetime import datetime, timedelta, timezone
import requests
import json
import boto3
import yaml

# API KEYS
def keys():
    with open("../keys.yml", "r") as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    return data

def replace_access_token():
    url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": keys()['CLIENT_ID'],
        "client_secret": keys()['CLIENT_SECRET']
        ,
        "grant_type": "refresh_token",
        "refresh_token": keys()['REFRESH_TOKEN']
    }
    
    res = requests.post(url, data=payload)
    res = res.json()

    access_token = res['access_token']

    with open('../keys.yml', 'r') as f:
        data = yaml.safe_load(f)
        data['ACCESS_TOKEN'] = access_token
    with open('keys.yml', 'w') as f:
        yaml.dump(data, f, sort_keys=False)


def obtain_recent_activity_ids(epoch_date):
    url = "https://www.strava.com/api/v3/athlete/activities"
    params = { "per_page": 50, "page": 1, "after": int(epoch_date) }
    headers = { "Authorization": f"Bearer {keys()['ACCESS_TOKEN']}" }
    res = requests.get(url, params=params, headers=headers)
    ids = [{'ID':i.get('id'),'start_date':timestamp_to_epoch(i.get('start_date'))} for i in res.json()]
    return ids

def timestamp_to_epoch(ts_str):
    # Replace 'Z' with '+00:00' to make it compatible with fromisoformat
    ts_str = ts_str.replace('Z', '+00:00')
    dt = datetime.fromisoformat(ts_str)
    return int(dt.timestamp())

def load_last_timestamp():
    try:
        with open("last_timestamp.yml", "r") as f:
            data = yaml.load(f, Loader=yaml.SafeLoader)
        return data['last_timestamp']
    except FileNotFoundError:
        return "2020-01-01T00:00:00Z"

def save_last_timestamp(timestamp):
    data = {'last_timestamp': timestamp}
    with open("last_timestamp.yml", "w") as f:
        yaml.dump(data, f, sort_keys=False)

def upload_strava_activity(activity_id, prefix="strava/raw"):
    url = f"https://www.strava.com/api/v3/activities/{activity_id}"
    params = {"include_all_efforts": 1}
    headers = {"Authorization": f"Bearer {keys()['ACCESS_TOKEN']}"}
    res = requests.get(url, params=params, headers=headers)
    data = res.json()
    bucket = 'strava-running-data'
    s3 = boto3.client('s3')
    
    filename = f"activity_{activity_id}.json"
    key = f"{prefix}/{filename}"
    
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(data),
        ContentType="application/json",
    )
    print(f"Uploaded activity {activity_id} to s3://{bucket}/{key}")

replace_access_token()
last_timestamp = load_last_timestamp()
bucket = 'strava-running-data'

last_timestamp = load_last_timestamp()
new_ids = obtain_recent_activity_ids(last_timestamp)

for activity in new_ids:
    upload_strava_activity(activity['ID'])

    if activity['start_date'] > last_timestamp:
        last_timestamp = activity['start_date']


save_last_timestamp(last_timestamp)