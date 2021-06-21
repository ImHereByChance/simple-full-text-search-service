import aiohttp
from source import create_app
from source.routes import setup_routes

if __name__ == '__main__':
    app = create_app()

    aiohttp.web.run_app(app,)