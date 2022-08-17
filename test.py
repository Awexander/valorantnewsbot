import getmatches
import asyncio

valorant = getmatches.getmatchinfo()

async def main():
    result , error= await valorant.getmatches('ap', 'awexander', '007')
    if result is True:
        print(valorant.match.map)
        print(valorant.match.gamemode)
        print(valorant.match.roundWon)
        print(valorant.match.roundLost)
        print(int(round(valorant.match.adr)))
        print(int(round(valorant.match.headshot)))
    else:
        print(error)
        
asyncio.get_event_loop().run_until_complete(main())
