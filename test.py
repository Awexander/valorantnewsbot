import getmatches
import asyncio
from datetime import datetime as datetime

valorant = getmatches.getmatchinfo()

async def main():
    now = datetime.now()
    ctx = input()
    content = ctx.split('#')
    print(f'1: {content[0]} \n2. {content[1]}')
    result , error= await valorant.getmatches(content[0],content[1])
    if result is True:
        print(f'{valorant.match.map}: {valorant.match.gamemode}')
        print(f'{valorant.match.roundWon}:{valorant.match.roundLost}')
        print(int(round(valorant.match.adr)))
        print(int(round(valorant.match.headshot)))
        print(valorant.match.kda)
    else:
        print(error)

    print(datetime.now() - now)
asyncio.get_event_loop().run_until_complete(main())
