
from src.reportcard import reportcard
import json 
import asyncio

async def main():
    matchid = '6c3b8e02-3823-4c35-8206-e8b07fbfa589'
    puuid = 'eb885c4c-d77a-54c7-8dc9-f1e1927b6eeb'
    with open('data/match/30677de1-2494-4bd6-832b-aecf53af22c3.json', 'r') as r:
        match = json.loads(r.read())
    
    with open('data/accounts.json', 'r') as r:
        accounts = json.loads(r.read())
    for acc in accounts:
        if matchid not in set(acc.get('matchid')) and acc.get('puuid') == puuid:
            print(matchid)

    report = reportcard()
    img = await report.card(match)

asyncio.get_event_loop().run_until_complete(main())