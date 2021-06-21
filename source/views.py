import aiohttp
import json
import logging
from aiohttp import web


class IndexEndPoint(web.View):
    """ / """
    
    async def get(self):
        """GET /"""
        # TODO: return API documentation instead
        return web.json_response(data=self.request.app['config'])
