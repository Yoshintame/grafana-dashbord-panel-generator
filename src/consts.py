import os

from dotenv import load_dotenv

load_dotenv()

MON_BASE_URL = os.getenv('MON_BASE_URL')
MON_AUTH_LOGIN = os.getenv('MON_AUTH_LOGIN')
MON_AUTH_PASSWORD = os.getenv('MON_AUTH_PASSWORD')
MON_AUTH = (MON_AUTH_LOGIN, MON_AUTH_PASSWORD)
GRAFANA_API_BASE_URL = os.getenv('GRAFANA_API_BASE_URL')
GRAFANA_API_TOKEN = os.getenv('GRAFANA_API_TOKEN')
