
import asyncio
import json
from .. import getmatches as match

matchupdate = match.getmatchinfo()
async def main():
    try:
        with open('..data/accounts.json', 'r') as r:
            ids = json.loads(r.read())
    except Exception as error:
        print(error)
    
    for id in ids:
        result, error = await matchupdate.getmatches(name=id['name'], tag=id['tag'])

        if result is True:
            if matchupdate.match.matchid != id['matchid']:
                id['matchid'] = matchupdate.match.matchid
                content = {
                    'account': {
                        "name": id['name'],
                        "tag": id['tag']
                    },
                    'rank':matchupdate.match.rank,
                    'map':matchupdate.match.map, 
                    'mode':matchupdate.match.gamemode, 
                    'matchid': matchupdate.match.matchid,
                    'score':f'{matchupdate.match.roundWon}-{matchupdate.match.roundLost}', 
                    'agent':matchupdate.match.agent,
                    'headshot':int(round(matchupdate.match.headshot)),
                    'kda':matchupdate.match.kda,
                    'adr':int(round(matchupdate.match.adr))
                }

                if matchupdate.match.rank != id['rank']:
                    id['rank'] = matchupdate.match.rank

                try:
                    matchlist = []
                    with open(f"..data/accounts/{id['name']}#{id['tag']}.json", 'r') as r:
                        matchlist = json.loads(r.read())
                    
                    matchlist.insert(0, content)

                    try:
                        with open(f"..data/accounts/{id['name']}#{id['tag']}.json", 'w') as w:
                            json.dump(matchlist, w, indent=4, separators=[',',':'])
                    except:
                        print("error append")

                    try:
                        with open('..data/accounts.json', 'w') as w:
                            json.dump(ids, w, indent=4, separators=[',',':'])
                    except Exception as error:
                        print(f'error update accounts.json \n {error}')
                except Exception as error:
                    print(error)
        else:
            print(error)

asyncio.get_event_loop().run_until_complete(main())
