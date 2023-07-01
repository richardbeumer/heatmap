import hvac
import requests
import os
from requests.auth import HTTPBasicAuth
from logger import Logger
from exceptions import VariableNotSetException, ConnectionException

class Vault:
    logger = Logger.get_logger(__name__)
    connection_error = "Error when connecting to URL: %s"
    
    def __init__(self, path):
        self.path = path
    
    def get_env(self, env):
        if env in os.environ:
            data = os.getenv(env)
            return data
        else:
            self.logger.error("Environment Variable " + env + " not set")
            raise VariableNotSetException(env)
    
        
    def get_keycloak_token(self):
        url = self.get_env("KEYCLOAK_URL") + "/realms/"+ self.get_env("KEYCLOAK_REALM") +"/protocol/openid-connect/token"
    
        payload = 'grant_type=client_credentials'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    
        try:
            response = requests.request("POST", url, headers=headers, data=payload,
                auth=HTTPBasicAuth(self.get_env("CLIENT_ID"), self.get_env("CLIENT_SECRET"))).json()
        except requests.exceptions.ConnectionError:
            self.logger.error(self.connection_error, url)
            raise ConnectionException(url)

        if "access_token" in response:
             keycloak_token = response["access_token"]
        else:
            self.logger.error("No access token. Keycloak responded with: %s", response)
        return  keycloak_token
    
    
    def vault_oidc_login(self):
        url=self.get_env("VAULT_URL")
        try:
            client = hvac.Client(url)
            client.auth.jwt.jwt_login(
            role="degiro",
            jwt=self.get_keycloak_token()
        )
        except requests.exceptions.ConnectionError:
            self.logger.error(self.connection_error, url)
            raise ConnectionException(url)


        return client

    
    def get_vault_secrets(self):
        client = self.vault_oidc_login()
        secret_version_response = client.secrets.kv.v2.read_secret_version(
            path=self.path
        )
        data=secret_version_response['data']['data']
        return data
    
    def update_vault_secret(self, value):
        client = self.vault_oidc_login()
        update = client.secrets.kv.v2.create_or_update_secret(
            path=self.path,
            secret=dict(value)
        )
        return update