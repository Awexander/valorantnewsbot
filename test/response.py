import aiohttp
import asyncio
import json

url = 'https://api.henrikdev.xyz/valorant/v1/status/ap'

async def main():
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(10)) as session:
        async with session.get(url) as response:
            resp = await response.json()

            with open('data/test/response.json', 'w') as w:
                json.dump(resp, w, indent=4, separators=[',',':'])

asyncio.get_event_loop().run_until_complete(main())