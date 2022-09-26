import aiohttp
import asyncio
import json

url = 'https://valorant-api.com/v1/agents'

async def main():
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(10)) as session:
        async with session.get(url) as response:
            resp = await response.text()
            with open('data/test/agents.json', 'w') as w:
                json.dump(w, w, indent=4, separators=[',',':'])

asyncio.get_event_loop().run_until_complete(main())