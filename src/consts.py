import os

def load_env(path):
    with open(path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip("\n").split("=", 1)

            key = line[0]
            value = line[1]
            os.environ[key] = value


load_env('.env')

MON_BASE_URL = os.environ.get('MON_BASE_URL')
MON_AUTH_LOGIN = os.environ.get('MON_AUTH_LOGIN')
MON_AUTH_PASSWORD = os.environ.get('MON_AUTH_PASSWORD')
MON_AUTH = (MON_AUTH_LOGIN, MON_AUTH_PASSWORD)
GRAFANA_API_BASE_URL = os.environ.get('GRAFANA_API_BASE_URL')
GRAFANA_API_TOKEN = os.environ.get('GRAFANA_API_TOKEN')
