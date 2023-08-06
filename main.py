import argparse
import os

from src.config import config
from src.panel import panel


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This script allows you to edit the graphana's panel by adding new port ids and changing their labels, generates color gradients and total fields.")
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

