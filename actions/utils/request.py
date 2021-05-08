from typing import Text, Any, Dict, Optional

import aiohttp


async def get(url: Text, params: Optional[Dict[Any, Any]] = None) -> Dict[Any, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()
