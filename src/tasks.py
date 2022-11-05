import discord
from discord.ext import tasks
import datetime as dt
import aiohttp
from .matches import getmatchinfo as match
from src.database.valorantdb import database
from .utils import utils
from .reportcard import reportcard
from src.CONFIG import BLUE, SLASH
import random
import json
import os

class task():
    def __init__(self, bot) -> None:
        self.match = match()
        self.matchinfo = self.match.matchlist
        self.bot = bot
        self.utils = utils(bot)
        self.db = database()
        self.region = self.match.region
        self.matchtime = dt.datetime.now().timestamp()
        self.looptime = dt.datetime.now().timestamp()
        self.reportcard = reportcard()

        self.updateURL = 'https://api.henrikdev.xyz/valorant/v1/website/en-us'
        self.statusURL = f'https://api.henrikdev.xyz/valorant/v1/status/{self.region}'
        self.prevUpdate, self.prevMaintenance, self.prevIncidents = [],[],[]
        self.path = os.getcwd()
        self.isThere_Incidents = False
        self.isThere_Maintenance = False
        pass

    @tasks.loop(seconds=1)
    async def loop(self):
        delay = random.randrange(20,50)
        if dt.datetime.now().timestamp() - self.looptime >= delay:
            self.looptime = dt.datetime.now().timestamp()
            updateData = await self._requestsupdates(self.updateURL)
            maintenanceData, incidentData = await self._requestsupdates(self.statusURL)
            isNeed_Append = 'None'

            if updateData['status'] == 200:
                latestPatch = await self.readPatch(updateData)
                if latestPatch['title'] != self.prevUpdate['title'] and latestPatch != None:
                    self.prevUpdate = latestPatch
                    if latestPatch['external_link'] != None:
                        link = latestPatch['external_link']
                    else:
                        link = latestPatch['url']
                    
                    isNeed_Append = 'patch'
                    await self.utils.BOT(f'new update is available')
                    message= f"**GAME UPDATE** \n\n {latestPatch['title']} \n\n {link}"
                    await self._sendNotification(message, isNeed_Append, latestPatch, self.prevMaintenance, self.prevIncidents)
            else:
                await self.utils.ERROR(f"Processing updates data \nError code: {updateData['status']}")

            try:
                if bool (maintenanceData):
                    currMaintenance = await self._getstatusData(maintenanceData)
                    if currMaintenance['id'] != self.prevMaintenance['id'] and currMaintenance != None:
                        self.prevMaintenance = currMaintenance

                        isNeed_Append = 'maintenance'
                        self.isThere_Maintenance = True
                        await self.utils.BOT(f'new maintenances updated')
                        message= f"**MAINTENANCE UPDATE**\n\n**{currMaintenance['status'].upper()}: {currMaintenance['title']}**\n{currMaintenance['content']} \n\nUpdated at: {currMaintenance['time']}\nMore info: https://status.riotgames.com/valorant?region=ap&locale=en_US"
                        await self._sendNotification(message, isNeed_Append, self.prevUpdate, currMaintenance, self.prevIncidents)
                else:
                    if self.isThere_Maintenance != False:
                        isNeed_Append = 'maintenance'
                        self.isThere_Maintenance = False
                        await self.utils.BOT(f'incidents resolved.')
                        message= f"**STATUS UPDATE**\n\n**MAINTENANCE RESOLVED: {self.prevMaintenance['title']}**\n{self.prevMaintenance['content']} \n\nUpdated at: {self.prevMaintenance['time']}\nMore info: https://status.riotgames.com/valorant?region=ap&locale=en_US"
                        await self._sendNotification(message, isNeed_Append, self.prevUpdate, self.prevMaintenance, self.prevIncidents)
            except:
                await self.utils.ERROR(f"Processing maintenances data \nError code: {maintenanceData['status']}")

            try:
                if bool(incidentData):
                    currIncident = await self._getstatusData(incidentData) 
                    if currIncident['id'] != self.prevIncidents['id'] and currIncident != None:
                        self.prevIncidents = currIncident
                        
                        isNeed_Append = 'incident'
                        self.isThere_Incidents = True
                        await self.utils.BOT(f'new incidents updated')
                        message= f"**STATUS UPDATE**\n\n**{currIncident['severity'].upper()}: {currIncident['title']}**\n{currIncident['content']} \n\nUpdated at: {currIncident['time']}\nMore info: https://status.riotgames.com/valorant?region=ap&locale=en_US"
                        await self._sendNotification(message, isNeed_Append, self.prevUpdate, self.prevMaintenance, currIncident)
                else:
                    if self.isThere_Incidents != False:
                        isNeed_Append = 'incident'
                        self.isThere_Incidents = False
                        await self.utils.BOT(f'incidents resolved.')
                        message= f"**STATUS UPDATE**\n\n**INCIDENTS RESOLVED: {self.prevIncidents['title']}**\n{self.prevIncidents['content']} \n\nUpdated at: {self.prevIncidents['time']}\nMore info: https://status.riotgames.com/valorant?region=ap&locale=en_US"
                        await self._sendNotification(message, isNeed_Append, self.prevUpdate, self.prevMaintenance, self.prevIncidents)
            except:
                await self.utils.ERROR(f"Processing incidents data \nError code: {incidentData['status']}")

    @tasks.loop(seconds = 2)
    async def getMatchReport(self):
        if dt.datetime.now().timestamp() - self.matchtime >= random.randrange(1,1200):
            self.matchtime = dt.datetime.now().timestamp()
            try:
                with open(self.path + f'{SLASH}data{SLASH}accounts.json', 'r') as r:
                    ids = json.loads(r.read())
            except Exception as error:
                await self.utils.ERROR(message=f'error loading ids \n error')
            
            for id in ids:
                try:
                    result = await self.match.getmatches(name=id['name'], tag=id['tag'])
                    content = []
                    if result.get('status') == 200:
                        if self.matchinfo.matchid not in set(id['matchid']) and self.matchinfo.puuid == id['puuid']:
                            await self.match.processmatch()
                            id['matchid'].append(self.matchinfo.matchid)
                            content = {
                                'account': {
                                    'name':id['name'], 
                                    'tag':id['tag']
                                },
                                'puuid':self.matchinfo.puuid,
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
                            await self.utils.report(message=f"**{id['name'].upper()}#{id['tag'].upper()}** \n Rank: {self.matchinfo.rank}",type='match', content=content)
                        
                            if self.matchinfo.rank != id['rank']:
                                await self.utils.report(message=f"**{id['name'].upper()}#{id['tag'].upper()}**", type='rank', content={'prevRank':id['rank'], 'currRank':self.matchinfo.rank})
                                id['rank'] = self.matchinfo.rank
                            
                            img = await self._savefullmatch()
                            await self._savematchreport(content, id, ids)
                            await self.utils.SENDIMAGE(img)
                    else:
                        await self.utils.ERROR(f"requesting data for {id['name']}#{id['tag']} \n {result['status']}: {result['errors']['message']}")
                except Exception as error:
                    await self.utils.ERROR(f"error requesting match data for {id['name']}#{id['tag']}\n {error}")

    async def _savefullmatch(self):
        matchreport = await self.match.fullmatch()
        
        with open(f"data/match/{matchreport['matchid']}.json", 'w') as w:
            json.dump(matchreport, w, indent=4, separators=[',',':'])
        
        self.db.savematch(matchreport)
        return await self.reportcard.card(matchreport)

    async def _savematchreport(self, data, id, ids):
        try:
            matchlist = []
            with open(self.path+f"{SLASH}data{SLASH}accounts{SLASH}{id['name']}#{id['tag']}.json", 'r') as r:
                matchlist = json.loads(r.read())
            
            matchlist.insert(0, data)
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

    async def _getstatusData(self, data):
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
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(30)) as session:
            async with session.get(url) as resp:
                data = await resp.json()
                if data['status'] == 200:
                    if url == self.updateURL:
                        return data
                    else:
                        if bool(data['data']['maintenances']) or bool(data['data']['incidents']):
                            return data['data']['maintenances'], data['data']['incidents']
                        else: 
                            return None, None
                else: 
                    if url == self.updateURL: return data
                    else: return data, data

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

    async def readPatch(self, data):
        for patch in data['data']:
            if patch['category'] == 'game_updates':
                return patch
        

