import vault
import os
import time
import requests
import gpxpy
import gpxpy.gpx
import polyline as Polyline
import strava_local_heatmap
import pandas as pd
from stravalib.client import Client
from datetime import datetime, timedelta
from logger import Logger


logger = Logger.get_logger("GPX")

strava = vault.Vault("network/strava")
strava_secrets = strava.get_vault_secrets()

data = {
    "client_id": strava_secrets['client_id'],
    "client_secret": strava_secrets['client_secret'],
    "refresh_token": strava_secrets['refresh_token'],
    "grant_type": "refresh_token"
}

response = requests.post("https://www.strava.com/oauth/token", data=data)
if response.status_code == 200:
    logger.info("Successfully obtained access token for strava.")
    access_token = response.json()['access_token']
    client = Client(access_token=access_token)
else:
    logger.info(f"Error obtaining access token: {response.json()}")
    raise HTTPError("https://www.strava.com/oauth/token", response.status_code, response.json(), None, None)


    
def get_athlete_activities(max_activities=20):
    try:
        activities = client.get_activities(limit=max_activities)
        return list(activities)
    except Exception as e:
        logger.error(f"Error fetching activities: {e}")
        raise


def get_gpx_from_activity():
    logger.info("Fetching last %s activities from Strava", os.environ.get('STRAVA_MAX_ACTIVITIES'))
    activities = get_athlete_activities(int(os.environ.get('STRAVA_MAX_ACTIVITIES')))
    for activity in activities:
        logger.info("Creating GPX for activity: %s (%s)", activity.name, activity.id)
        url = f"https://www.strava.com/api/v3/activities/{activity.id}/streams"
        header = {'Authorization': 'Bearer ' + access_token}

        latlong = requests.get(url, headers=header, params={'keys':['latlng']}).json()[0]['data']
        altitude = requests.get(url, headers=header, params={'keys':['altitude']}).json()[1]['data']
        # Create dataframe to store data 'neatly'
        data = pd.DataFrame([*latlong], columns=['lat','long'])
        data['altitude'] = altitude

        gpx = gpxpy.gpx.GPX()
        # Create first track in our GPX:
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)
        # Create first segment in our GPX track:
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)
        # Create points:
        for idx in data.index:
            gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(
                        data.loc[idx, 'lat'],
                        data.loc[idx, 'long'],
                        elevation=data.loc[idx, 'altitude']
            ))
        # Write data to gpx file
        current_dir=os.getcwd()
        if not os.path.exists(current_dir + "/gpx"):
            os.mkdir(current_dir + "/gpx")
            os.chmod(current_dir + "/gpx", 0o777)
        filename = f"{activity.id}.gpx"
        with open(current_dir + "/gpx/" + filename, 'w') as f:
            f.write(gpx.to_xml())


get_gpx_from_activity()
logger.info("Creating Heatmap from GPX files")
strava_local_heatmap.parse_args()
