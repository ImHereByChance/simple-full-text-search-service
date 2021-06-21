import aiohttp
import argparse
import aioreloader

from source import create_app
from source.routes import setup_routes
from source.configloader import load_config


# console arguments
arg_parser = argparse.ArgumentParser(description='App launcher parser')
arg_parser.add_argument('--host', help='Host to listen', default='127.0.0.1')
arg_parser.add_argument('--port', 
                        help='Port to accept connections',
                        default=5000)
arg_parser.add_argument('--reload',
                        action='store_true',
                        help='Autoreload code on change')
arg_parser.add_argument('-c', '--config',
                        type=argparse.FileType('r'),
                        help='Path to the config file (yaml)',
                        default=None)
args = arg_parser.parse_args()

# reload mode
if args.reload:
    print('Start with reload mode')
    aioreloader.start()

config = load_config(args.config)
app = create_app(config)


if __name__ == '__main__':
    aiohttp.web.run_app(app, host=args.host, port=args.port)