import urllib3
import os
from stravaweblib import WebClient, DataFormat
from stravalib.client import Client
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from exceptions import VariableNotSetException, ConnectionException
import vault
import shutil
import time
from logger import Logger
import jwt
import strava_local_heatmap

logger = Logger.get_logger("GPX")
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
jwt_token=strava_secrets['jwt_token']

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
        logger.info("Updating tokens...")
        refresh_response = client.refresh_access_token(client_id=client_id, client_secret=client_secret, refresh_token=refresh_token)
        access_token = refresh_response['access_token']
        new_refresh_token = refresh_response['refresh_token']
        expires_at = refresh_response['expires_at']
        client.access_token = access_token
        client.refresh_token = refresh_token
        client.token_expires_at = expires_at
        strava_secrets.update({"refresh_token":new_refresh_token, "access_token":access_token, "expires_at":expires_at})
        strava.update_vault_secret(strava_secrets)
    else:
        logger.info("Token still valid...")

def check_jwt():
    if time.time() > jwt.decode(jwt_token, options={"verify_signature": False})['exp']:
        logger.info("Updating jwt...")
        jwt_refresh_response = WebClient(access_token=access_token, jwt=jwt_token)
        new_jwt_token = jwt_refresh_response.jwt
        webclient.jwt = new_jwt_token
        strava_secrets.update({"jwt_token": new_jwt_token})
        strava.update_vault_secret(strava_secrets)
    else:
        logger.info("JWT still valid....")


check_token()
webclient = WebClient(access_token=client.access_token, email=email, password=password)

current_dir=os.getcwd()
if not os.path.exists(current_dir + "/gpx"):
    os.mkdir(current_dir + "/gpx")
    os.chmod(current_dir + "/gpx", 0o777)

#Getting last activity
for activity in client.get_activities(limit=maxactivities):
    id=("{0.id}".format(activity))
    data = webclient.get_activity_data(id, fmt=DataFormat.GPX)
    logger.info("Processing activity: %s on file %s", activity, data.filename)
    with open(current_dir + "/gpx/" + data.filename, 'wb') as f:
        for chunk in data.content:
            if not chunk:
                break
            f.write(chunk)

logger.info(os.listdir(current_dir + "/gpx"))

strava_local_heatmap.parse_args()
shutil.rmtree(current_dir + "/gpx")
