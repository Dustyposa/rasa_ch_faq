from typing import Text, Any, Dict, Optional, Union, List

import aiohttp

ANY_DATA = Optional[Dict[Any, Any]]


async def get(url: Text, params: ANY_DATA = None) -> Union[List[Dict], Dict[Any, Any]]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()


async def post(url: Text, data: ANY_DATA = None, params: ANY_DATA = None) \
        -> Union[List[Dict], Dict[Any, Any]]:
    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=params, data=data) as resp:
            return await resp.json()
