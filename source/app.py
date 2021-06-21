from aiohttp import web
from pathlib import Path

from .exceptions import NoDefaultConfigFile
from .routes import setup_routes


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / 'default_config.yaml'


def create_app(config:dict=None):
    if config is None:
        try:
            config = DEFAULT_CONFIG_PATH.open().read()
        except FileNotFoundError:
            raise NoDefaultConfigFile('Cannot find default config.yaml' +
                                      'it should be placed in ./source dir.')
    app = web.Application()    
    app['config'] = config
    setup_routes(app)
    
    return app