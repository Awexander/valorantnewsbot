
import aiohttp
import cloudscraper
import json

class getmatchinfo():
    def __init__(self):
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
        url = f'https://api.tracker.gg/api/v2/valorant/standard/matches/riot/{name}%23{tag}?type=competitive'
        try:
            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'android',
                    'desktop': False
                }
            )
            with scraper.get(url,timeout=timeout) as r:
                matches = r.json()
                self.matchIndex = 0
                self.matches = []
                for data in matches['data']['matches']:
                    if data['metadata']['modeName'] == 'Competitive':
                        self.matches = data
                        break
                    self.matchIndex += 1

                if self.matches == []:
                    return None, f"{name}#{tag} didn't play any competitive yet"

                #with open(f'data/{name}#{tag}.json', 'w') as fm:
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
        return self.matches['attributes']['id']

    async def _getmap(self):
        return self.matches['metadata']['mapName']

    async def _getGameMode(self):
        return self.matches['metadata']['modeName']
    
    async def _getmatchdate(self):
        return self.matches['metadata']['timestamp']
    
    async def _getstats(self):
        return self.matches['segments'][0]['stats']

    async def _getAgent(self):
        return self.matches['segments'][0]['metadata']['agentName']

    async def _getRank(self):
        return self.matchstats['rank']['metadata']['tierName']

    async def _getMatchResult(self):
        return self.matchstats['roundsWon']['value'], self.matchstats['roundsLost']['value']

    async def _getHeadshot(self):
        return self.matchstats['headshotsPercentage']['value']

    async def _getkda(self):
        return [self.matchstats['kills']['value'], self.matchstats['deaths']['value'], self.matchstats['assists']['value'], float(round(self.matchstats['kdRatio']['value'],1))]
    
    async def _getadr(self):
        return self.matchstats['damagePerRound']['value']
    
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

