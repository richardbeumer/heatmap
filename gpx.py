import requests
import urllib3
import os
from stravaweblib import WebClient, DataFormat
from stravalib.client import Client
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#settings for Strava
auth_url = "https://www.strava.com/oauth/token"
activites_url = "https://www.strava.com/api/v3/athlete/activities"
email = os.environ.get('STRAVA_USER')
password = os.environ.get('STRAVA_PWD')
clientid = os.environ.get('STRAVA_CLIENT_ID')
clientsecret = os.environ.get('STRAVA_CLIENT_SECRET')
refreshtoken = os.environ.get('STRAVA_REFRESH_TOKEN')
maxactivities = int(os.environ.get('STRAVA_MAX_ACTIVITIES'))
payload = {
    'client_id': clientid,
    'client_secret': clientsecret,
    'refresh_token': refreshtoken,
    'grant_type': "refresh_token",
    'f': 'json'
}

#Getting Strava token
print("Requesting Token...\n")
res = requests.post(auth_url, data=payload, verify=False)
access_token = res.json()['access_token']
print("Access Token = {}\n".format(access_token))

#Logging in to Strava
client = Client(access_token=access_token)
webclient = WebClient(access_token=access_token, email=email, password=password)

#Getting last activity
for activity in client.get_activities(limit=maxactivities):
    id=("{0.id}".format(activity))
    data = webclient.get_activity_data(id, fmt=DataFormat.GPX)
    with open("gpx/" + data.filename, 'wb') as f:
        for chunk in data.content:
            if not chunk:
                break
            f.write(chunk)

os.system('python3 strava_local_heatmap.py --output /mnt/index.html')
