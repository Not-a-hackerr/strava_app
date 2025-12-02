import requests
import yaml
import pprint
import time

def keys():
    with open("keys.yml", "r") as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    return data

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
    expires_at = res['expires_at']

    with open('keys.yml', 'r') as f:
        data = yaml.safe_load(f)
        data['ACCESS_TOKEN'] = access_token
        data['ACCESS_TOKEN_EXPIRES'] = expires_at
    with open('keys.yml', 'w') as f:
        yaml.dump(data, f, sort_keys=False)
    


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
                            "elev_low":data[i]["elev_low"]
                            }
                        })
    pprint.pp(activities)

try:
    get_activities()
except:
    replace_access_token()
    print('Access token has expired, a new access token has been generated.')
