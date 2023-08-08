import json
import sys
import warnings
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

import requests
from jsonschema import validate
from urllib3.exceptions import InsecureRequestWarning

from src.colormapper import create_custom_cmap, generate_colors
from src.consts import MON_BASE_URL, MON_AUTH

# Completely disable InsecureRequestWarning
warnings.filterwarnings("ignore", category=InsecureRequestWarning)


def generate_config_schema(color_sets):
    CONFIG_SCHEMA = {
        "type": "object",
        "properties": {
            "panel_file": {
                "type": "string",
                "pattern": ".*\.json$"
            },
            "colors": {
                "type": "object",
                "properties": {
                    "in": {
                        "type": "string",
                        "enum": color_sets
                    },
                    "out": {
                        "type": "string",
                        "enum": color_sets
                    }
                },
                "required": ["in", "out"]
            },
            "fields": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "number"},
                        "label": {"type": ["string", "null"]}
                    },
                    "required": ["id", "label"]
                }
            }
        },
        "required": ["panel_file", "colors", "fields"]
    }

    return CONFIG_SCHEMA


COLORS_SETS_SCHEMA = {
    "type": "object",
    "patternProperties": {
        "^[A-Za-z0-9_]+$": {
            "type": "array",
            "minItems": 2,
            "items": {
                "type": "string",
                "pattern": "^#[A-Fa-f0-9]{6}$"
            }
        }
    },
    "minProperties": 1,
    "additionalProperties": False
}


def load_and_validate_config_file(config_path, config_schema):
    try:
        with open(config_path, 'r') as f:
            config_data = json.loads(f.read())

            try:
                validate(config_data, config_schema)
            except Exception as e:
                print("Not valid config file. Error: ", e)
                sys.exit(1)
    except FileNotFoundError:
        print("File 'config.json' not found.")
        sys.exit(1)

    return config_data


def get_label_from_mon_api(port_id):
    try:
        response = requests.get(f'{MON_BASE_URL}/ports/{port_id}', verify=False, auth=MON_AUTH)
        response.raise_for_status()

        port = response.json()['port']
        port_name = response.json()['port']["entity_shortname"]

    except requests.exceptions.RequestException as e:
        print("An error occurred while making the request to mon, setting label to 'unknown': ", e)
        return "unknown"
    except Exception as e:
        print("An unexpected error occurred while making the request to mon, setting label to 'unknown': ", e)
        return "unknown"

    try:
        response = requests.get(f'{MON_BASE_URL}/devices/{port["device_id"]}', verify=False, auth=MON_AUTH)
        response.raise_for_status()

        device_name = "unknown_device" if response.status_code != 200 else response.json()['device']["hostname"]
    except requests.exceptions.RequestException as e:
        print("An error occurred while making the request to mon, setting device part of label to 'unknown_device': ",
              e)
    except Exception as e:
        print("An unexpected error occurred while making the request to mon, setting label to 'unknown_device': ", e)

    return f"{device_name} - {port_name}"


def parse_config(config_data):
    in_legend, out_legend, port_ids = get_legend_from_config_fields(config_data["fields"])
    colors = config_data["colors"]
    panel_file = config_data["panel_file"]

    return in_legend, out_legend, colors, port_ids, panel_file


def get_legend_from_config_fields(config_fields):
    in_legend = []
    out_legend = []
    port_ids = []
    for field in config_fields:
        port_ids.append(field["id"])

        if field["label"] is None:
            field["label"] = get_label_from_mon_api(field["id"])

        in_legend.append(f'out_{field["label"]}')
        out_legend.append(f'in_{field["label"]}')

    return in_legend, out_legend, port_ids


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
    total_transformations = [generate_total_transformation(in_total_name, in_legend),
                             generate_total_transformation(out_total_name, out_legend)]

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


def generate_overrides(in_color_set, out_color_set, in_legend, out_legend):
    overrides = []

    in_custom_cmap = create_custom_cmap(in_color_set)
    in_colors = generate_colors(len(in_legend), in_custom_cmap)

    for field, color in zip(in_legend, in_colors):
        overrides.append(generate_override(color, field))

    out_custom_cmap = create_custom_cmap(out_color_set)
    out_colors = generate_colors(len(out_legend), out_custom_cmap)

    for field, color in zip(out_legend, out_colors):
        overrides.append(generate_override(color, field))

    # Total overrides
    overrides.append(generate_total_override("Total in"))
    overrides.append(generate_total_override("Total out"))

    return overrides


def generate_override(color, field):
    matcher = {
        "id": "byName",
        "options": field
    }
    properties = [{
        "id": "color",
        "value": {
            "fixedColor": color,
            "mode": "fixed"
        }
    }]

    override = {
        "matcher": matcher,
        "properties": properties
    }

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


def generate_mon_api_url(port_ids, panel_data):
    original_url = panel_data["targets"][0]["params"][0][1]
    parsed_url = urlparse(original_url)
    params = parse_qs(parsed_url.query)

    params["id"] = ','.join([str(port_id) for port_id in port_ids])
    updated_query = urlencode(params, doseq=True)
    updated_url = parsed_url._replace(query=updated_query)
    final_url = urlunparse(updated_url)

    return final_url


def load_and_validate_color_sets_file(filename):
    try:
        with open(filename, 'r') as f:
            color_sets = json.loads(f.read())

            try:
                validate(color_sets, COLORS_SETS_SCHEMA)
            except Exception as e:
                print("Not valid color sets file. Error: ", e)
                sys.exit(1)
    except FileNotFoundError:
        print("File 'color_sets.json' not found.")
        sys.exit(1)

    return color_sets


def panel():
    color_sets = load_and_validate_color_sets_file("src/color_sets.json")
    config_schema = generate_config_schema(list(color_sets.keys()))
    config_data = load_and_validate_config_file("config.json", config_schema)

    in_legend, out_legend, color_sets_name, port_ids, panel_file = parse_config(config_data)

    overrides = generate_overrides(color_sets[color_sets_name["out"]], color_sets[color_sets_name["in"]], in_legend,
                                   out_legend)
    transformations = generate_total_transformations("Total out", "Total in", in_legend, out_legend)
    fields = generate_fields(out_legend + in_legend)

    with open(panel_file, 'r') as f:
        initial_panel = json.loads(f.read())

    target_url = generate_mon_api_url(port_ids, initial_panel)

    with open(f'{panel_file.replace("-initial-panel-data", "-generated-panel-data")}.json', 'w') as f:
        initial_panel["fieldConfig"]["overrides"] = overrides
        initial_panel["targets"][0]["fields"] = fields
        initial_panel["transformations"] = transformations
        initial_panel["targets"][0]["params"][0][1] = target_url

        json_object = json.dumps(initial_panel, indent=4)
        f.write(json_object)
