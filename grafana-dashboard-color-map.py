from pprint import pprint 
import requests
import json

from color import Color

# PORT_IDS = [74881,31403,75384,66914,1974,1985,30122,1994,2006,47979,1979,77308,31424,78697]
PORT_IDS = [31403,1979]

# PACKETS IN
COLOR_PURPLE = {
    "initial_color": Color(160, 160, 229),
    "steps": {
        "r": 2,
        "g": 12,
        "b": 6
    }
}

# PACKETS OUT
COLOR_ORANGE = {
    "initial_color": Color(252, 184, 62),
    "steps": {
        "r": 2,
        "g": 12,
        "b": 6
    }
}

# TRAFIC IN
COLOR_GREEN = {
    "initial_color": Color(182, 209, 74),
    "steps": {
        "r": 10,
        "g": 7,
        "b": 3
    }
}

# TRAFIC OUT
COLOR_BLUE = {
    "initial_color": Color(160, 160, 229),
    "steps": {
        "r": 10,
        "g": 10,
        "b": 11
    }
}


cookies = {
        # 'OBSID': 't3a8npag4ahr4pkif70rssr795',
        'observium_screen_ratio': '2',
        'observium_screen_resolution': '1512x982',
        'screen_scheme': 'dark',
    }

headers = {
    'authority': 'mon.reconn.local',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    # 'cookie': 'OBSID=t3a8npag4ahr4pkif70rssr795; observium_screen_ratio=2; observium_screen_resolution=1512x982; screen_scheme=dark',
    'dnt': '1',
    'sec-ch-ua': '"Chromium";v="113", "Not-A.Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
}




def get_legend(ids):
    legend = []
    for id in ids:
        response = requests.get(f'https://mon.reconn.local/api/v0/ports/{id}', cookies=cookies, headers=headers, verify=False,  auth=('MihailIvanov', 'Game9-Grain-Pretended'))
        print(response.status_code)
        port = response.json()['port']

        portname = port["entity_shortname"]

        response = requests.get(f'https://mon.reconn.local/api/v0/devices/{port["device_id"]}', cookies=cookies, headers=headers, verify=False,  auth=('MihailIvanov', 'Game9-Grain-Pretended'))
        device = response.json()['device']

        devicename = device["hostname"]

        legend.append(f"{devicename} - {portname}")


    in_legend = []
    out_legend = []
    for field in legend: 
        in_legend.append(f"out_{field}")
        out_legend.append(f"in_{field}")

   

    return in_legend, out_legend


def generate_overrides(color_in, color_out, in_legend, out_legend):
    overrides = []

    # Color overrides
    for field  in in_legend:
        overrides.append(generate_override(color_in["initial_color"], color_in["steps"], field))
    for field  in out_legend:
        overrides.append(generate_override(color_out["initial_color"], color_out["steps"], field))

    # Total overrides 
    overrides.append(generate_total_override("Total in"))
    overrides.append(generate_total_override("Total out"))
    
    
    return overrides

def generate_total_transformation(total_name, legend):
    total_transformation = {
        "id": "calculateField",
        "options": {
            "alias": total_name,
            "mode": "reduceRow",
            "reduce": {
            "include": legend,
            "reducer": "sum"
            }
        }
    }

    return total_transformation

def generate_total_transformations(in_total_name, out_total_name, in_legend, out_legend):
    total_transformations = []
    total_transformations.append(generate_total_transformation(in_total_name, in_legend))
    total_transformations.append(generate_total_transformation(out_total_name, out_legend))

    return total_transformations

def generate_total_override(total_name):
    total_override = {
        "matcher": {
        "id": "byName",
        "options": total_name
        },
        "properties": [
        {
            "id": "custom.lineWidth",
            "value": 0
        },
        {
            "id": "custom.fillOpacity",
            "value": 0
        },
        {
            "id": "custom.scaleDistribution",
            "value": {
            "log": 2,
            "type": "log"
            }
        }
        ]
    }
    
    return total_override

    
def generate_override(color, steps, field):
    matcher = {
            "id": "byName",
            "options": field
        }
    properties = []
    properties.append({
        "id": "color",
        "value": {
            "fixedColor": color.rgb_to_hex(),
            "mode": "fixed"
        }
    })
        

    override = {
        "matcher": matcher,
        "properties": properties
    }

    color.step(steps)

    return override


def generate_fields(legend):
    fields = [{
        "jsonPath": "$.data.*.0",
        "name": "Time",
        "type": "time"
    }]

    for index, field_name in enumerate(legend):
        field = {
            "jsonPath": f"$.data.*.{index + 1}",
            "language": "jsonpath",
            "name": field_name,
            "type": "number"
        }

        fields.append(field)

   

    return fields


if __name__ == "__main__":    
    in_legend, out_legend = get_legend(PORT_IDS)

    overrides = generate_overrides(COLOR_ORANGE, COLOR_PURPLE, in_legend, out_legend)

    transformations = generate_total_transformations("Total out", "Total in", in_legend, out_legend)

    legend =  out_legend + in_legend
    pprint(legend)

    fields = generate_fields(legend)

    
    with open("generated_fields.json", "w") as outfile:
        json_object = json.dumps({"fields": fields}, indent=4)
        outfile.write(json_object)

    with open("generated_overrides.json", "w") as outfile:
        json_object = json.dumps({"overrides": overrides}, indent=4)
        outfile.write(json_object)
    grafana_initial_panel = None


    with open('grafana-panel-initial.json', 'r') as f:
        grafana_initial_panel = json.loads(f.read())

    with open('generated_grafana_panel.json', 'w') as f:
        grafana_initial_panel["fieldConfig"]["overrides"] = overrides
        grafana_initial_panel["targets"][0]["fields"] = fields
        grafana_initial_panel["transformations"] = transformations


        json_object = json.dumps(grafana_initial_panel, indent=4)
        f.write(json_object)



        
