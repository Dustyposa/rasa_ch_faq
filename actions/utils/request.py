from typing import Text, Any, Dict, Optional, Union, List

import aiohttp


async def get(url: Text, params: Optional[Dict[Any, Any]] = None) -> Union[List[Dict], Dict[Any, Any]]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()
