import aiohttp
from source import create_app


if __name__ == '__main__':
    app = create_app()
    aiohttp.web.run_app(app,)