
import aiohttp
import json

class getmatchinfo():
    def __init__(self):
        self.match = self._latestmatch(map=None, mode=None, roundWon=None, roundLost=None, agent=None, headshot=None, kda=None, adr=None)
        pass
        
    async def getmatches(self, region, name, tag, timeout=30):
        url = f'https://api.henrikdev.xyz/valorant/v3/matches/{region}/{name}/{tag}'
        puuid_url = f'https://api.henrikdev.xyz/valorant/v1/account/{name}/{tag}?force=true'

        try:
            self.puuid = await self._getpuuid(puuid_url, timeout)
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(timeout)) as session:
                async with session.get(url) as resp:
                    self.matches = await resp.json()

                    with open('config/fullmatches.json', 'w') as fm:
                        json.dump(self.matches, fm, indent=4, separators=[',',':'])
            
            self.match.map = await self._getmap()
            self.match.gamemode = await self._getGameMode()
            self.lastmatch = await self._getLatestMatch()
            self.match.roundWon, self.match.roundLost = await self._getMatchResult()
            self.match.agent = await self._getAgent()
            self.match.headshot = await self._getHeadshot()
            self.match.kda = await self._getkda()
            self.match.adr = await self._getadr()

            return True, None
            
        except Exception as error:
            return None, error

    async def _getpuuid(seld, url, timeout):
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(timeout)) as session:
            async with session.get(url) as pid:
                puuid = await pid.json()
                return puuid['data']['puuid']

    async def _getmap(self):
        return self.matches['data'][0]['metadata']['map']

    async def _getGameMode(self):
        return self.matches['data'][0]['metadata']['mode']
        
    async def _getMatchResult(self):
        result =  self.matches['data'][0]['teams'][self.team.lower()]
        return result['rounds_won'], result['rounds_lost']

    async def _getAgent(self):
        return self.lastmatch['character']

    async def _getLatestMatch(self):
        for player in self.matches['data'][0]['players']['all_players']:
            if player['puuid'] == self.puuid:
                self.team = player['team']
                return player

    async def _getHeadshot(self):
        damage = self.lastmatch['stats'] 
        return float(damage['headshots'] / (damage['headshots'] + damage['bodyshots'] + damage['legshots'])) * 100

    async def _getkda(self):
        damage = self.lastmatch['stats']
        return damage['kills'] / damage['deaths']
    
    async def _getadr(self):
        return self.lastmatch['damage_made'] / self.matches['data'][0]['metadata']['rounds_played']
    
    class _latestmatch():
        def __init__(self, map, mode, roundWon, roundLost, agent, headshot, kda, adr):
            self.map = map
            self.gamemode = mode
            self.roundWon = roundWon
            self.roundLost = roundLost
            self.agent = agent
            self.headshot = headshot
            self.kda = kda
            self.adr = adr

