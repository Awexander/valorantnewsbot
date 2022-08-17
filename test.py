import getmatches
import asyncio
from datetime import datetime as datetime

valorant = getmatches.getmatchinfo()

async def main():
    now = datetime.now()
    result , error= await valorant.getmatches('ap', 'awexander', '007')
    if result is True:
        print(f'{valorant.match.map}: {valorant.match.gamemode}')
        print(f'{valorant.match.roundWon}:{valorant.match.roundLost}')
        print(int(round(valorant.match.adr)))
        print(int(round(valorant.match.headshot)))
    else:
        print(error)

    print(datetime.now() - now)
asyncio.get_event_loop().run_until_complete(main())
