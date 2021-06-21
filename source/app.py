import yaml
from aiohttp import web
from pathlib import Path

from .exceptions import NoDefaultConfigFile
from .routes import setup_routes


DEFAULT_CONFIG_FILE_PATH = Path(__file__).resolve().parent / 'default_config.yaml'


def create_app(costum_config:dict=None):
    """Create aiohttp.web.app instance."""
    app = web.Application()  
    
    try:
        default_config = yaml.safe_load(DEFAULT_CONFIG_FILE_PATH.open())
    except FileNotFoundError:
        raise NoDefaultConfigFile('Cannot find default_config.yaml:' +
                                  'it should be placed in ./source dir.')
    
    app['config'] = default_config
    if costum_config is not None:
        app['config'].update(**costum_config)
    
           
    


    setup_routes(app)
    
    return app