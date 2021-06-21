import aiohttp
import json
import logging.config
from aiohttp import web


class IndexEndPoint(web.View):
    async def get(self):
        # TODO: return API documentation instead
        return web.json_response(data={'hello': 'there'})