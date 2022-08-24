import discord
from discord.ext import tasks
import datetime as dt
import aiohttp
from .matches import getmatchinfo as match
from .utils import utils
from src.CONFIG import BLUE, SLASH
import json
import os

class task():
    def __init__(self, bot) -> None:
        self.match = match()
        self.matchinfo = self.match.match
        self.bot = bot
        self.utils = utils(bot)
        self.region = self.match.region

        self.updateURL = 'https://api.henrikdev.xyz/valorant/v1/website/en-us'
        self.statusURL = f'https://api.henrikdev.xyz/valorant/v1/status/{self.region}'
        self.prevUpdate, self.prevMaintenance, self.prevIncidents = [],[],[]
        self.path = os.getcwd()
        pass

    @tasks.loop(seconds=20)
    async def loop(self):
        updateData = await self._requestsupdates(self.updateURL)
        maintenanceData, incidentData = await self._requestsupdates(self.statusURL)
        isNeed_Append = 'None'

        try:
            latestPatch = await self.readPatch(updateData)
            if latestPatch['title'] != self.prevUpdate['title'] and latestPatch != None:
                self.prevUpdate = latestPatch
                if latestPatch['external_link'] != None:
                    link = latestPatch['external_link']
                else:
                    link = latestPatch['url']
                
                isNeed_Append = 'patch'
                await self.utils.BOT('[BOT]',f'new update is available')
                message= f"**GAME UPDATE** \n\n {latestPatch['title']} \n\n {link}"
                await self._sendNotification(message, isNeed_Append, latestPatch, self.prevMaintenance, self.prevIncidents)
        except Exception as error:
            await self.utils.ERROR(f'processing updates data: \n{error}')

        try:
            if bool (maintenanceData):
                currMaintenance = await self._getstatusData(maintenanceData)
                if currMaintenance['id'] != prevMaintenance['id'] and currMaintenance != None:
                    prevMaintenance = currMaintenance

                    isNeed_Append = 'maintenance'
                    await self.utils.BOT(f'new maintenances updated')
                    message= f"**MAINTENANCE UPDATE**\n\n**{currMaintenance['status'].upper()}: {currMaintenance['title']}**\n{currMaintenance['content']} \n\nUpdated at: {currMaintenance['time']}\nMore info: https://status.riotgames.com/valorant?region=ap&locale=en_US"
                    await self._sendNotification(message, isNeed_Append, self.prevUpdate, currMaintenance, self.prevIncidents)
        except Exception as error:
            await self.utils.ERROR(f'processing maintenances data: \n{error}')

        try:
            if bool(incidentData):
                currIncident = await self._getstatusData(incidentData) 
                if currIncident['id'] != prevIncidents['id'] and currIncident != None:
                    prevIncidents = currIncident
                    
                    isNeed_Append = 'incident'
                    await self.utils.BOT(f'new incidents updated')
                    message= f"**STATUS UPDATE**\n\n**{currIncident['severity'].upper()}: {currIncident['title']}**\n{currIncident['content']} \n\nUpdated at: {currIncident['time']}\nMore info: https://status.riotgames.com/valorant?region=ap&locale=en_US"
                    await self._sendNotification(message, isNeed_Append, self.prevUpdate, self.prevMaintenance, currIncident)
        except Exception as error:
            await self.utils.ERROR(f'processing incidents data: \n{error}')

    @tasks.loop(minutes=30)
    async def getMatchReport(self):
        try:
            with open(self.path + f'{SLASH}data{SLASH}accounts.json', 'r') as r:
                ids = json.loads(r.read())
        except Exception as error:
            await self.utils.ERROR(message=f'error loading ids \n error')
        
        for id in ids:
            result, error = await self.match.getmatches(name=id['name'], tag=id['tag'])

            content = []
            if result is True:
                if self.matchinfo.matchid != id['matchid']:
                    id['matchid'] = self.matchinfo.matchid
                    content = {
                        'account': {
                            'name':id['name'], 
                            'tag':id['tag']
                        },
                        'rank':self.matchinfo.rank,
                        'map':self.matchinfo.map, 
                        'mode':self.matchinfo.gamemode, 
                        'timeplayed': self.matchinfo.matchdate,
                        'matchid': self.matchinfo.matchid,
                        'score':f'{self.matchinfo.roundWon}-{self.matchinfo.roundLost}', 
                        'agent':self.matchinfo.agent,
                        'headshot':int(round(self.matchinfo.headshot)),
                        'kda':self.matchinfo.kda,
                        'adr':int(round(self.matchinfo.adr))
                    }
                    await self._matchReport(message=f"**{id['name'].upper()}#{id['tag'].upper()}** \n Rank: {self.matchinfo.rank}",type='match', content=content)
                
                    if self.matchinfo.rank != id['rank']:
                        id['rank'] = self.matchinfo.rank
                        await self._matchReport(message=f"**{id['name'].upper()}#{id['tag'].upper()}**", type='rank', content={'prevRank':id['rank'], 'currRank':self.matchinfo.rank})
                    
                    try:
                        matchlist = []
                        with open(self.path+f"{SLASH}data{SLASH}accounts{SLASH}{id['name']}#{id['tag']}.json", 'r') as r:
                            matchlist = json.loads(r.read())
                        
                        matchlist.insert(0, content)
                        try:
                            with open(self.path+f"{SLASH}data{SLASH}accounts{SLASH}{id['name']}#{id['tag']}.json", 'w') as w:
                                json.dump(matchlist, w, indent=4, separators=[',',':'])
                        except:
                            await self.utils.ERROR(message=f'error appending matchlist data \n {error}')
                        
                        try:
                            with open(self.path+f'{SLASH}data{SLASH}accounts.json', 'w') as w:
                                json.dump(ids, w, indent=4, separators=[',',':'])
                        except Exception as error:
                            await self.utils.ERROR(f'error update accounts.json \n {error}')
                    except Exception as error:
                        await self.utils.ERROR(f"error loading {id['name']}#{id['tag']}.json \n {error}")
            else:
                await self.utils.ERROR(f"error loading latest match data {id['name']}#{id['tag']} \n {error}")

    async def _matchReport(self, message='', type='', content=[]):
        embed = discord.Embed(
            title='[REPORT]',
            description=message, 
            color=BLUE,
        )
        if type == 'match':
            embed.add_field(name='MAP', value=content['map'], inline=True)
            embed.add_field(name='MODE', value=content['mode'], inline=True)
            embed.add_field(name='SCORE', value=content['score'], inline=True)
            embed.add_field(name='AGENT', value=content['agent'], inline=True)
            embed.add_field(name='K/D', value=float(content['kda'][3]), inline=True)
            embed.add_field(name='KDA', value=f"K:{content['kda'][0]} D:{content['kda'][1]} A:{content['kda'][2]}", inline=True)
            embed.add_field(name='ADR', value=content['adr'], inline=True)
            embed.add_field(name='HS%', value=f"{content['headshot']}%", inline=True)
            embed.set_footer(text=f"played on: {content['timeplayed']}")
        elif type == 'rank':
            embed.add_field(name='Previous Rank', value=content['prevRank'])
            embed.add_field(name='Current Rank', value=content['currRank'])

        return await self.utils.REPORT(embed=embed)

    async def _getstatusData(data):
        for locale in data[0]['titles']:
            if locale['locale'] == 'en_US':
                incident = locale['content']
                break
        
        for translation in data[0]['updates'][0]['translations']:
            if translation['locale'] == 'en_US':
                content = translation['content']
                break
        content_id = data[0]['updates'][0]['id']
        strtime = data[0]['created_at']
        time = dt.datetime.strptime(strtime, "%Y-%m-%dT%H:%M:%S.%f%z") + dt.timedelta(hours=8)

        report = {
            'severity': data[0]['incident_severity'],
            'title': incident,
            'id': data[0]['id'],
            'content': content,
            'content_id': content_id,
            'time': time.strftime("%B %d, %Y at %H:%M GMT+8"),
            'status': data[0]['maintenance_status']
            }
        return report

    async def _requestsupdates(self, url):
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(30)) as session:
                async with session.get(url) as resp:
                    if url == self.updateURL:
                        return await resp.json()
                    elif url == self.statusURL:
                        data = await resp.json()
                        return data['data']['maintenances'], data['data']['incidents']
        except Exception as error:
            await self.utils.ERROR(f'requests failed: \n{error}')

    async def _sendNotification(self, message, isNeed_Append, updateData, currMaintenance, currIncident):
        if isNeed_Append != 'None':
            _prevUpdate, _prevMaintenance, _prevIncidents = await self.utils.readprevdata()
            if isNeed_Append == 'patch': appendUpdate = updateData
            else: appendUpdate = _prevUpdate

            if isNeed_Append == 'maintenance': appendMaintenance = currMaintenance    
            else: appendMaintenance = _prevMaintenance

            if isNeed_Append == 'incident': appendIncident = currIncident
            else: appendIncident = _prevIncidents
            
            isNeed_Append = 'None'
            await self._appendData(appendUpdate, appendMaintenance, appendIncident)

        await self.utils.NOTIFICATION(f'<@&{756538183810023564}> {message}')

    async def _appendData(self, updateData, maintenanceData, incidenctData):
        try:
            data = {           
                "updates": updateData,
                "maintenances": maintenanceData,
                "incidents": incidenctData
            }
            with open(self.path + f'{SLASH}data{SLASH}updates.json', 'w') as w:
                w.write(json.dumps(data, indent=4, separators=[',',':']))

        except Exception as error:
            await self.utils.ERROR(f'error appending updates data \n {error}')

    async def readPatch(data):
        for patch in data['data']:
            if patch['category'] == 'game_updates':
                return patch
        

