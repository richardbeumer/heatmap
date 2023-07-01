import requests
import vault

#http://www.strava.com/oauth/authorize?client_id=2677&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=profile:read_all,activity:read_all

strava = vault.Vault("network/strava")
strava_secrets = strava.get_vault_secrets()

#settings for Strava
auth_url = "https://www.strava.com/oauth/token"
activites_url = "https://www.strava.com/api/v3/athlete/activities"
clientid=strava_secrets['client_id']
clientsecret=strava_secrets['client_secret']

code="b1c89482f0f5b80e76f4957650277c882721d254"
payload = {
    'client_id': clientid,
    'client_secret': clientsecret,
    'code': code,
    'grant_type': "authorization_code"    
}

response=requests.post(url=auth_url, data=payload)
strava_token = response.json()
print(strava_token)