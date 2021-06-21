import logging
from aiohttp import web
from pathlib import Path

from .routes import setup_routes


def create_app(config:dict):
    """Create aiohttp.web.app instance."""
    
    # Init an app instance.
    app = web.Application()
    
    # Apply app configs.
    app['config'] = config
    
    # Logging settings.
    logger_basic_level = app['config'].get('LOGGER_BASIC_LEVEL')
    logging.basicConfig(level=logger_basic_level)
           
    # Routes.
    setup_routes(app)
    
    return app
