import argparse, textwrap
import os

from argparse import RawTextHelpFormatter

from src.config import config
from src.panel import panel


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=textwrap.dedent('''
This script allows you to edit the Grafana panel by adding new port IDs and changing their labels, generating color gradients, and total fields.

To use it, you need to set MON_AUTH_LOGIN, MON_AUTH_PASSWORD, and GRAFANA_API_TOKEN fields in the .env file.

USAGE EXAMPLE:
python main.py config -u "{grafana_panel_url}"

This command will generate a config file and backup the initial Grafana panel JSON file.
Next, edit the config file by adding new port IDs or changing existing ones. You can also change the gradient colors to one of the following options: BLUE, GREEN, PURPLE, or ORANGE.

To apply the config, use the following command:
python main.py panel


This command will generate a new Grafana panel JSON. Copy the JSON and paste it into Grafana -> Panel -> Inspect -> Panel JSON.
    '''), formatter_class=RawTextHelpFormatter)
    subparsers = parser.add_subparsers(dest='command', required=True)

    config_parser = subparsers.add_parser('config', help='Generate initial panel data file and config file for its editing')
    config_parser.add_argument('-u', '--url', help="Grafana panel url", required=True)

    panel_parser = subparsers.add_parser('panel', help='Applies the config to the initial panel, generating a new one')

    args = parser.parse_args()

    if args.command == 'config':
        print('URL:', args.url)
        config(args.url)


    elif args.command == 'panel':
        panel()

