from urllib.parse import urlparse, parse_qs
import requests
import json
from pprint import pprint

GRAFANA_URL = "https://eye.reconn.ru/d/JkuONx-Vk1/dc-2?orgId=1&refresh=1m&viewPanel=21"


# Get viewPanel and dashboard ids from panel url
def get_ids_from_url(URL):
    parsed_url = urlparse(URL)
    query_params = parse_qs(parsed_url.query)

    dash_uid = parsed_url.path.split('/')[-2]
    viewPanel_uid = query_params.get('viewPanel', [''])[0]

    print("dash_uid:", dash_uid)
    print("panel_uid:", viewPanel_uid)

    return dash_uid, viewPanel_uid

# Get dashboard from grafana api by its id
def get_databoard_from_api(dash_uid):
    headers = {"Authorization": "Bearer eyJrIjoiY05qUVNwUGd0b0NFQnUydG9GSUR2bkk0dnRETlZhVlAiLCJuIjoiZGFzaGdlbiIsImlkIjoxfQ=="}
    url = f"https://eye.reconn.ru/api/dashboards/uid/{dash_uid}"

    response = requests.request("GET", url, headers=headers)
    data = json.loads(response.text)
    return data

# Get panel from dashboard object by its id
def get_panel_from_dashboard(dashboard_data, viewPanel_uid):
    found_panel = None
    for panel in dashboard_data["dashboard"]["panels"]:
        print(panel["id"])
        if int(panel["id"]) == int(viewPanel_uid):
            found_panel = panel
            break

    if found_panel is None:
        print(f"Panel with id {viewPanel_uid} not found")
    return found_panel

# Gererate config for panel editing
def generate_config(paneld_data):
    mon_url = None
    for param in paneld_data["targets"][0]["params"]:
        if "graph.php" in param[1]:
            mon_url = param[1]
            break

    port_ids = search_ids_in_mon_url(mon_url)


    fields = paneld_data["targets"][0]["fields"]
    config = []
    for index, port_id in enumerate(port_ids):
        field_name = fields[index+1]["name"] if (int(fields[index+1]["jsonPath"].split('.')[-1]) == index+1) else "-"
        config.append({"id": port_id, "label": field_name})

    return config


def search_ids_in_mon_url(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    if 'id' not in query_params:
        raise ValueError("Missing id parameter in mon ports link")

    id_list = query_params['id'][0].split(',')

    return id_list


if __name__ == "__main__":
    dash_uid, viewPanel_uid = get_ids_from_url(GRAFANA_URL)
    dashboard_data = get_databoard_from_api(dash_uid)

    panel_data = get_panel_from_dashboard(dashboard_data, viewPanel_uid)
    with open(f'initial-panel-data-{panel_data["datasource"]["uid"]}.json', 'w') as file:
        json.dump(panel_data, file, indent=4)

    config = generate_config(panel_data)
    with open(f'config.json', 'w') as file:
        json.dump(config, file, indent=4)


