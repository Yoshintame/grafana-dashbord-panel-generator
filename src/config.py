import json
import sys
from urllib.parse import urlparse, parse_qs

import requests

from src.consts import GRAFANA_API_TOKEN, GRAFANA_API_BASE_URL


# Get viewPanel and dashboard ids from panel url
def get_ids_from_url(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    dash_uid = parsed_url.path.split('/')[-2]
    viewPanel_uid = query_params.get('viewPanel', [''])[0]

    return dash_uid, viewPanel_uid


# Get dashboard from grafana api by its id
def get_dashboard_from_api(dash_uid):
    headers = {"Authorization": f"Bearer {GRAFANA_API_TOKEN}"}
    url = f"{GRAFANA_API_BASE_URL}/dashboards/uid/{dash_uid}"

    try:
        response = requests.request("GET", url, headers=headers)
        response.raise_for_status()

        data = json.loads(response.text)
        return data
    except requests.exceptions.RequestException as e:
        print("An error occurred while making the request to mon, setting label to 'unknown': ", e)
        sys.exit(1)
    except Exception as e:
        print("An unexpected error occurred while making the request to mon, setting label to 'unknown': ", e)
        sys.exit(1)


# Get panel object from dashboard object by its id
def get_panel_from_dashboard(dashboard_data, panel_uid):
    found_panel = None

    for panel in dashboard_data["dashboard"]["panels"]:
        if int(panel["id"]) == int(panel_uid):
            found_panel = panel
            break

    if found_panel is None:
        raise ValueError(f"Not found panel with {panel_uid} id dashboard object")
    return found_panel


# Generate config for panel editing
def generate_config(panel_data):
    mon_url = None
    for param in panel_data["targets"][0]["params"]:
        if "graph.php" in param[1]:
            mon_url = param[1]
            break
    port_ids = search_port_ids_in_mon_url(mon_url)

    fields = panel_data["targets"][0]["fields"]
    config_fields = []
    for index, port_id in enumerate(port_ids):
        field_name = fields[index + 1]["name"].split("_", maxsplit=1)[1] if (
                int(fields[index + 1]["jsonPath"].split('.')[-1]) == index + 1) else None

        config_fields.append({"id": int(port_id), "label": field_name})

    generated_config = {
        "panel_file": f'initial-panel-data-{panel_data["datasource"]["uid"]}.json',
        "colors": {
            "in": "GREEN",
            "out": "BLUE"
        },
        "fields": config_fields
    }

    return generated_config


def search_port_ids_in_mon_url(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    if 'id' not in query_params:
        raise ValueError("Missing id parameter in mon ports link")

    port_ids = query_params['id'][0].split(',')

    return port_ids


def config(grafana_url):
    dash_uid, viewPanel_uid = get_ids_from_url(grafana_url)
    dashboard_data = get_dashboard_from_api(dash_uid)

    panel_data = get_panel_from_dashboard(dashboard_data, viewPanel_uid)
    generated_config = generate_config(panel_data)

    with open(generated_config["panel_file"], 'w') as file:
        json.dump(panel_data, file, indent=4)

    with open(f'config.json', 'w') as file:
        json.dump(generated_config, file, indent=4)
