import requests
import urllib3
import os
from stravaweblib import WebClient, DataFormat
from stravalib.client import Client
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from exceptions import VariableNotSetException, ConnectionException
import vault
import shutil
import time

strava = vault.Vault("network/strava")
strava_secrets = strava.get_vault_secrets()

#settings for Strava
auth_url = "https://www.strava.com/oauth/token"
activites_url = "https://www.strava.com/api/v3/athlete/activities"
email=strava_secrets['user']
password=strava_secrets['password']
client_id=strava_secrets['client_id']
client_secret=strava_secrets['client_secret']
refresh_token=strava_secrets['refresh_token']
expires_at=strava_secrets['expires_at']
access_token=strava_secrets['access_token']
maxactivities = int(os.environ.get('STRAVA_MAX_ACTIVITIES'))

payload = {
    'client_id': client_id,
    'client_secret': client_secret,
    'refresh_token': refresh_token,
    'grant_type': "refresh_token"    
}

client = Client()
client.token_expires_at = expires_at
client.access_token = access_token
client.refresh_token = refresh_token

def check_token():
    if time.time() > float(client.token_expires_at):
        print("Updating tokens...")
        refresh_response = client.refresh_access_token(client_id=client_id, client_secret=client_secret, refresh_token=refresh_token)
        access_token = refresh_response['access_token']
        new_refresh_token = refresh_response['refresh_token']
        expires_at = refresh_response['expires_at']
        client.access_token = access_token
        client.refresh_token = refresh_token
        client.token_expires_at = expires_at
        strava_secrets.update({"refresh_token":new_refresh_token, "access_token":access_token, "expires_at":expires_at})
    else:
        print("Token still valid...")

check_token()

webclient = WebClient(access_token=access_token, email=email, password=password)

# Store the current session's information
jwt = webclient.jwt
webclient_access_token = webclient.access_token

# Create a new webclient that continues to use the previous web session
webclient = WebClient(access_token=webclient_access_token, jwt=jwt)

current_dir=os.getcwd()
os.mkdir(current_dir + "/gpx")

#Getting last activity
for activity in client.get_activities(limit=maxactivities):
    id=("{0.id}".format(activity))
    data = webclient.get_activity_data(id, fmt=DataFormat.GPX)
    with open(current_dir + "/gpx/" + data.filename, 'wb') as f:
        for chunk in data.content:
            if not chunk:
                break
            f.write(chunk)

os.system('python3 strava_local_heatmap.py --output /mnt/index.html')

shutil.rmtree(current_dir + "/gpx")