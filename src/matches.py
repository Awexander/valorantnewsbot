
import aiohttp
import datetime as dt

class getmatchinfo():
    def __init__(self):
        self.region = 'ap'
        self.matchlist = self._latestmatch(
            puuid=None,
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
        self._name = name
        self._tag = tag
        url = f'https://api.henrikdev.xyz/valorant/v3/matches/{self.region}/{name}/{tag}'
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(timeout)) as session:
                async with session.get(url) as resp:
                    matches = await resp.json()
                    if matches['status'] == 200:
                        self.matches = {}
                        for data in matches['data']:
                            if data['metadata']['mode'] == 'Competitive':
                                self.matches = data
                                break

                        if self.matches == {}:
                            return f"{name}#{tag} didn't play any competitive yet"
                    else:
                        return matches

            self.matchlist.matchid = await self._getMatchID()
            self.matchlist.map = await self._getmap()
            self.matchlist.gamemode = await self._getGameMode()
            self.matchlist.matchdate = await self._getmatchdate()

            self.matchstats = await self._getstats()
            self.matchlist.agent = await self._getAgent()
            self.matchlist.rank = await self._getRank()
            self.matchlist.roundWon, self.matchlist.roundLost = await self._getMatchResult()
            self.matchlist.headshot = await self._getHeadshot()
            self.matchlist.kda = await self._getkda()
            self.matchlist.adr = await self._getadr()
            
            return None
            
        except:
            return matches

    async def fullmatch(self):
        data = []
        players = await self._getplayers()
        for player in players:
            self.matchstats = player
            playerData = {
                "puuid": player['puuid'],
                "name": player['name'],
                "tag": player['tag'], 
                "team": player['team'],
                "rank": player['currenttier_patched'],
                "agent": player['character'],
                "acs": await self._getacs(),
                "headshot": await self._getHeadshot(),
                "kda": await self._getkda(),
                "adr": await self._getadr()
            }
            data.append(playerData)
        match = {
            "matchid": await self._getMatchID(),
            "map": await self._getmap(),
            "result": {
                "red": await self._getTeamResult('red'),
                "blue": await self._getTeamResult('blue')
            },
            "gamemode": await self._getGameMode(),
            "timeplayed": await self._getmatchdate(),
            "players": data
        }
        return match

    async def _getMatchID(self):
        return self.matches['metadata']['matchid']

    async def _getmap(self):
        return self.matches['metadata']['map']

    async def _getGameMode(self):
        return self.matches['metadata']['mode']
    
    async def _getmatchdate(self):
        timestamp = dt.datetime.fromtimestamp(self.matches['metadata']['game_start'])
        return timestamp.strftime("%B %d, %Y at %H:%M GMT+8")
    
    async def _getstats(self):
        for stats in self.matches['players']['all_players']:
            if stats['name'].lower() == self._name.lower() and stats['tag'].lower() == self._tag.lower():
                self.matchlist.puuid = stats['puuid']
                return stats

    async def _getplayers(self):
        return self.matches['players']['all_players']

    async def _getAgent(self):
        return self.matchstats['character']

    async def _getRank(self):
        url = f"https://api.henrikdev.xyz/valorant/v1/mmr/{self.region}/{self._name}/{self._tag}"
        async with aiohttp.ClientSession(aiohttp.ClientTimeout(timeout=aiohttp.ClientTimeout)) as session:
            async with session.get(url) as response:
                resp = await response.json()

                if resp.get('status') != 200:
                    return resp.get('status')
                
                return resp.get('data').get('currenttierpatched')

    async def _getMatchResult(self):
        team = self.matchstats['team'].lower()
        return self.matches['teams'][team]['rounds_won'], self.matches['teams'][team]['rounds_lost']

    async def _getTeamResult(self, team):
        return self.matches['teams'][team.lower()]['rounds_won']
    
    async def _getacs(self):
        return int(round(self.matchstats['stats']['score'] / self.matches['metadata']['rounds_played']))

    async def _getHeadshot(self):
        return int(round((self.matchstats['stats']['headshots'] / (self.matchstats['stats']['headshots'] + self.matchstats['stats']['bodyshots'] + self.matchstats['stats']['legshots'])) * 100))

    async def _getkda(self):
        return [self.matchstats['stats']['kills'], self.matchstats['stats']['deaths'], self.matchstats['stats']['assists'], float(round(self.matchstats['stats']['kills'] / self.matchstats['stats']['deaths'],1))]
    
    async def _getadr(self):
        return int(round(self.matchstats['damage_made'] / self.matches['metadata']['rounds_played']))
    
    class _latestmatch():
        def __init__(self, puuid, matchid, map, mode, matchdate, agent, rank, roundWon, roundLost, headshot, kda, adr):
            self.puuid = puuid
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

