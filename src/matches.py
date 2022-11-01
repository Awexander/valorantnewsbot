
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
            print(url)
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(timeout)) as session:
                async with session.get(url) as resp:
                    matches = await resp.json()
                    print(matches.get('status'))
                    if matches.get('status') == 200:
                        self.matches = []
                        for data in matches.get('data'):
                            if data.get('metadata').get('mode') == 'Competitive':
                                self.matches = data
                                break
                    else:
                        return matches.get('status')

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

            return matches.get('status')
        except:
            return matches.get('status')

    async def _getMatchID(self):
        return self.matches['metadata']['matchid']

    async def _getmap(self):
        return self.matches['metadata']['map']

    async def _getGameMode(self):
        return self.matches['metadata']['mode']

    async def _getmatchdate(self):
        # TODO: UNIX time
        timestamp = dt.datetime.fromtimestamp(
            self.matches['metadata']['game_start'])
        return timestamp.strftime("%B %d, %Y at %H:%M GMT+8")

    async def _getstats(self):
        for stats in self.matches['players']['all_players']:
            if stats['name'].lower() == self._name.lower() and stats['tag'].lower() == self._tag.lower():
                self.matchlist.puuid = stats['puuid']
                return stats

    async def _getAgent(self):
        return self.matchstats['character']

    async def _getRank(self):
        return self.matchstats['currenttier_patched']

    async def _getMatchResult(self):
        team = self.matchstats['team'].lower()
        return self.matches['teams'][team]['rounds_won'], self.matches['teams'][team]['rounds_lost']

    async def _getHeadshot(self):
        headshots = 0
        totalshots = 0

        for rounds in self.matches.get('rounds'):
            for player in rounds.get('player_stats'):
                if player.get('player_puuid') == self.matchlist.puuid:
                    for dmg_event in player.get('damage_events'):
                        if dmg_event.get('receiver_puuid') != self.matchlist.puuid:
                            headshots += dmg_event.get('headshots')
                            totalshots += (dmg_event.get('heashots') +
                                           dmg_event.get('bodyshots') + dmg_event.get('legshots'))

        return round((headshots / totalshots) * 100)

    async def _getkda(self):
        return [self.matchstats.get('stats').get('kills'),
                self.matchstats.get('stats').get('deaths'),
                self.matchstats.get('stats').get('assists'),
                float(round(self.matchstats.get('stats').get('kills') /
                      self.matchstats.get('stats').get('deaths'), 1))
                ]

    async def _getadr(self):
        damage_made = 0
        for rounds in self.matches.get('rounds'):
            for player in rounds.get('player_stats'):
                if player.get('player_puuid') == self.matchlist.puuid:
                    for dmg_event in player.get('damage_events'):
                        if dmg_event.get('receiver_puuid') != self.matchlist.puuid:
                            damage_made += dmg_event.get('damage')

        return round(damage_made / self.matches.get('metadata').get('rounds_played'))

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
