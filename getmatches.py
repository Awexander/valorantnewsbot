
import aiohttp
import json
from datetime import datetime

class getmatchinfo():
    def __init__(self):
        self.region = 'ap'
        self.match = self._latestmatch(
            matchid=None, 
            map=None, 
            mode=None, 
            matchdate=None,
            agent=None, 
            rank=None, 
            roundWon=None, 
            roundLost=None, 
            headshot=None, 
            kda=None, 
            adr=None)
        pass
        
    async def getmatches(self, name, tag, timeout=30):
        url = f'https://api.henrikdev.xyz/valorant/v3/matches/{self.region}/{name}/{tag}'
        puuid_url = f'https://api.henrikdev.xyz/valorant/v1/account/{name}/{tag}?force=true'
        try:
            self.puuid = await self._getpuuid(puuid_url, timeout)
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(timeout)) as session:
                async with session.get(url) as resp:
                    matches = await resp.json()
                    self.matches = []
                    for data in matches['data']:
                        if data['metadata']['mode'] == 'Competitive':
                            self.matches = data
                            break

                    if self.matches == []:
                        return None, f"{name}#{tag} didn't play any competitive yet"

                    #with open('data/test/fullmatches.json', 'w') as fm:
                        #json.dump(self.matches, fm, indent=4, separators=[',',':'])
            
            self.match.matchid = await self._getMatchID()
            self.match.map = await self._getmap()
            self.match.gamemode = await self._getGameMode()
            self.match.matchdate = await self._getmatchdate()
            self.matchstats = await self._getstats()

            self.match.agent = await self._getAgent()
            self.match.rank = await self._getRank()
            self.match.roundWon, self.match.roundLost = await self._getMatchResult()
            self.match.headshot = await self._getHeadshot()
            self.match.kda = await self._getkda()
            self.match.adr = await self._getadr()

            return True, None
            
        except Exception as error:
            return None, error

    async def _getpuuid(self, url, timeout):
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(timeout)) as session:
                async with session.get(url) as pid:
                    puuid = await pid.json()
                    return puuid['data']['puuid']
        except:
            return 'not a valid valorant id'

    async def _getMatchID(self):
        return self.matches['metadata']['matchid']

    async def _getmap(self):
        return self.matches['metadata']['map']

    async def _getGameMode(self):
        return self.matches['metadata']['mode']
    
    async def _getmatchdate(self):
        #TODO: UNIX time
        return self.matches['metadata']['game_start'] 
    
    async def _getstats(self):
        for stats in self.matches['players']['all_players']:
            if stats['puuid'] == self.puuid:
                return stats

    async def _getAgent(self):
        return self.matchstats['character']

    async def _getRank(self):
        return self.matchstats['currenttier_patched']

    async def _getMatchResult(self):
        team = self.matchstats['team'].lower()
        return self.matches['teams'][team]['rounds_won'], self.matches['teams'][team]['rounds_lost']

    async def _getHeadshot(self):
        return float(round(self.matchstats['stats']['headshots'] / (self.matchstats['stats']['headshots'] + self.matchstats['stats']['bodyshots'] + self.matchstats['stats']['legshots']),1))

    async def _getkda(self):
        return [self.matchstats['stats']['kills'], self.matchstats['stats']['deaths'], self.matchstats['stats']['assists'], float(round(self.matchstats['stats']['kills'] / self.matchstats['stats']['deaths'],1))]
    
    async def _getadr(self):
        return self.matchstats['damage_made'] / self.matches['metadata']['rounds_played']
    
    class _latestmatch():
        def __init__(self, matchid, map, mode, matchdate, agent, rank, roundWon, roundLost, headshot, kda, adr):
            self.matchid = matchid
            self.map = map
            self.gamemode = mode
            self.matchdate = matchdate
            self.agent = agent
            self.rank = rank
            self.roundWon = roundWon
            self.roundLost = roundLost
            self.headshot = headshot
            self.kda = kda
            self.adr = adr

