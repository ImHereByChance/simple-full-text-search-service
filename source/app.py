import logging.config
from aiohttp import web

from .dbase import DBaseHandler
from .routes import setup_routes


def create_app(config:dict):
    """Create aiohttp.web.app instance."""
    
    # Init an app instance.
    app = web.Application()
    
    # Apply app configs.
    app['config'] = config
    
    # Logging settings.
    logging.basicConfig(level=config['LOGGER_BASIC_LEVEL'])
    logging.config.dictConfig(config['LOGGER_CONFIG'])
    app['loggers'] = {
        'partial_deletion_logger': logging.getLogger('partial_deletion_logger'),
        'app_logger': logging.getLogger('aiohttp.server.app_logger')
    }
    
    # Routes.
    setup_routes(app)

    # Database.
    app['dbase'] = DBaseHandler(dbase_config=config['DATABASE_CONFIG'])
    
    return app
