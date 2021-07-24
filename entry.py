import aiohttp
import argparse
import aioreloader
from pathlib import Path

from source import create_app
from source.configloader import load_config


# default_config (to get some default values before local config will be loaded)
default_config = load_config()


# console arguments
arg_parser = argparse.ArgumentParser(description='App launcher parser')
arg_parser.add_argument('--host', 
                        help='Host to listen',
                        default=default_config['HOST'])
arg_parser.add_argument('--port', 
                        help='Port to accept connections',
                        default=default_config['PORT'])
arg_parser.add_argument('--reload',
                        action='store_true',
                        help='Autoreload code on change')
arg_parser.add_argument('-c', '--config',
                        help='Path to the config file (yaml)',
                        type=Path,
                        default=None)
args = arg_parser.parse_args()

# reload mode
if args.reload:
    print('Start with reload mode')
    aioreloader.start()

# Creating an app with given config (if config isn't specified using the
# console arguments '-c' or '--config' console arg, the app runs with
# ./source/default_congig.yaml)
config = load_config(args.config)
app = create_app(config)

print('after if __name__...')

if __name__ == '__main__':
    print('Initializing...')
    aiohttp.web.run_app(app, host=args.host, port=args.port)
