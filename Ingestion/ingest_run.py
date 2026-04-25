from datetime import datetime
import requests
import json
import boto3

def get_parameter(name):
    ssm = boto3.client('ssm', region_name='eu-west-2')
    response = ssm.get_parameter(Name=name, WithDecryption=True)
    return response['Parameter']['Value']

def get_api_key():
    client = boto3.client(
        'secretsmanager',
        region_name='eu-west-1'
    )
    response = client.get_secret_value(SecretId='strava/api_keys')
    return json.loads(response['SecretString'])

# CONNECTING TO CONNECTIONS
def replace_access_token():
    url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": get_api_key()['CLIENT_ID'],
        "client_secret": get_api_key()['CLIENT_SECRET'],
        "grant_type": "refresh_token",
        "refresh_token": get_api_key()['REFRESH_TOKEN']
    }
    
    res = requests.post(url, data=payload)
    res = res.json()

    new_access_token = res['access_token']
    
    client = boto3.client(
        'secretsmanager',
        region_name='eu-west-1'
    )

    current = get_api_key()
    
    # Merge updates into current secrets
    current.update({"ACCESS_TOKEN": new_access_token})
    
    client.update_secret(
        SecretId='strava/api_keys',
        SecretString=json.dumps(current)
    )    


def obtain_recent_activity_ids(epoch_date):
    url = "https://www.strava.com/api/v3/athlete/activities"
    params = { "per_page": 50, "page": 1, "after": int(epoch_date) }
    headers = { "Authorization": f"Bearer {get_api_key()['ACCESS_TOKEN']}" }
    res = requests.get(url, params=params, headers=headers)
    ids = [{'ID':i.get('id'),'start_date':timestamp_to_epoch(i.get('start_date'))} for i in res.json()]
    return ids

def timestamp_to_epoch(ts_str):
    # Replace 'Z' with '+00:00' to make it compatible with fromisoformat
    ts_str = ts_str.replace('Z', '+00:00')
    dt = datetime.fromisoformat(ts_str)
    return int(dt.timestamp())

def load_last_timestamp():
    s3 = boto3.client('s3')
    response = s3.get_object(
        Bucket=get_parameter("/strava/bucket_name"),
        Key="strava/last_timestep_uploaded/timestamp.json"
    )
    timestamp = json.loads(response['Body'].read().decode('utf-8'))
    return timestamp["last_timestamp"]

def save_last_timestamp(timestamp):
    data = {'last_timestamp': int(timestamp)}
    
    s3 = boto3.client('s3')
    
    s3.put_object(
        Bucket=get_parameter("/strava/bucket_name"),
        Key=get_parameter("/strava/last_timestep_bucket"),
        Body=json.dumps(data),
        ContentType="application/json"
    )

def upload_strava_activity(activity_id, prefix="strava/raw"):
    url = f"https://www.strava.com/api/v3/activities/{activity_id}"
    params = {"include_all_efforts": 1}
    headers = {"Authorization": f"Bearer {get_api_key()['ACCESS_TOKEN']}"}
    res = requests.get(url, params=params, headers=headers)
    data = res.json()
    s3 = boto3.client('s3')
    filename = f"activity_{activity_id}.json"
    key = f"{prefix}/{filename}"
    
    s3.put_object(
        Bucket=get_parameter("/strava/bucket_name"),
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