
import asyncio
from typing import Any
import discord
from discord.ext import commands, tasks
import datetime as dt
import getmatches as match
import requests
import json
import os

matchupdate = match.getmatchinfo()
intents = discord.Intents.default()
intents.members = True
intents.messages = True


updateURL = 'https://api.henrikdev.xyz/valorant/v1/website/en-us'
statusURL = 'https://api.henrikdev.xyz/valorant/v1/status/ap'
servername, logchannel, reportchannel = 1010443668659908788, 1007170918549819412, 1010808789680803871
prevUpdate, prevMaintenance, prevIncidents = [],[],[]

description: str= ''' valorant game updates, server status and scheduled maintenance ''' 

bot = commands.Bot(command_prefix='.', description=description, intents=intents)
isNeed_Append = 'None'
startTime = dt.datetime.now()
connectionTime = dt.datetime.now()
disconnetTime = dt.datetime.now()

@bot.event 
async def on_disconnect():
    global disconnetTime
    disconnetTime = dt.datetime.now()

@bot.event
async def on_resumed():
    global connectionTime
    connectionTime = dt.datetime.now()
    await _log('[BOT]',f'bot is online') 

@bot.event
async def on_ready():
    global connectionTime, disconnetTime, prevUpdate, prevMaintenance, prevIncidents
    connectionTime = dt.datetime.now()
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, 
            name=" raspberrypi "
            )
        )

    prevUpdate, prevMaintenance, prevIncidents = await _readjson()

    await asyncio.sleep(1)
    dcTime = disconnetTime.strftime("%A %m/%d/%Y, %H:%M")
    await _log('[BOT]',f'bot is online, \n disconnected since {dcTime}')
    loop.start()
    getMatchReport.start()

@bot.after_invoke
async def on_command(ctx):
    if ctx.author == bot.user:
        return

    if isinstance(ctx.channel, discord.DMChannel):
        return await _log('[BOT]',f"got a direct message from <@{ctx.author.id}> \n '{ctx.message.content}'")
    
    await ctx.message.delete(delay=1)

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user:
        return

    if isinstance(message.channel, discord.DMChannel):
        return await _log('[BOT]',f"got a direct message from <@{message.author.id}> \n '{message.content}'")

@bot.command()
async def id(ctx):
    return await _log('[SERVER]',f'Channel ID: {ctx.channel.id}')

@bot.command()
async def uptime(ctx):
    upSeconds = dt.datetime.now() - startTime
    connSeconds = dt.datetime.now() - connectionTime
    
    upTime = await _getTimeElapsed(upSeconds)
    connTime = await _getTimeElapsed(connSeconds)

    return await _log('[SERVER]',f"[SERV TIME]\t {upTime} \n[BOT TIME]\t {connTime}")

@bot.command()
async def update(ctx):
    message = await _readjson()
    return await _log('[SERVER]', f"Latest update: {message['updates']['title']} \n Updated at: {message['updates']['date']}")

@bot.listen()
async def on_command_error(ctx, error):
    return await _log('[ERROR]', f'{error}')

@bot.command()
async def lastmatch(ctx, *,valorantid):
    
    nametag = valorantid.split('#')
    result , error= await matchupdate.getmatches(nametag[0], nametag[1])
    if result is True:
        content = {
        'map':matchupdate.match.map, 
        'mode':matchupdate.match.gamemode, 
        'score':f'{matchupdate.match.roundWon}-{matchupdate.match.roundLost}', 
        'agent':matchupdate.match.agent,
        'headshot':int(round(matchupdate.match.headshot)),
        'kda':matchupdate.match.kda,
        'adr':int(round(matchupdate.match.adr))
        }
        await _log('[REPORT]',message=f'**{valorantid.upper()}** \n Rank: {matchupdate.match.rank}',type='match', content=content)
    else:
        await _log('[ERROR]', f'error loading latest match data \n {error}')

@bot.command()
async def region(ctx, *, region):
    matchupdate.region = region
    return await _log('[SERVER]', f'Changed region to: {region}')
    
@tasks.loop(seconds=20)
async def loop():
    global prevUpdate, prevMaintenance, prevIncidents, isNeed_Append
    updateData = await _requestsupdates(updateURL)
    maintenanceData, incidentData = await _requestsupdates(statusURL)
    
    try:
        latestPatch = await _getPatch(updateData)
        if latestPatch != prevUpdate['title'] and latestPatch != None:
            prevUpdate = latestPatch
            if updateData['external_link'] != None:
                link = updateData['external_link']
            else:
                link = updateData['url']
            
            isNeed_Append = 'patch'
            await _log('[BOT]',f'new update is available')
            message= f"**GAME UPDATE** \n\n {updateData['title']} \n\n {link}"
    except Exception as error:
        await _log('[ERROR]',f'processing updates data: \n{error}')

    try:
        if bool (maintenanceData):
            currMaintenance = await _getMaintenance(maintenanceData)
            if currMaintenance['id'] != prevMaintenance['id']:
                prevMaintenance['id'] = currMaintenance['id']
                
                await _log('[BOT]',f'new maintenances updated')
                message= f"**SERVER UPDATE**\n\n**{currMaintenance['title']}**\n{currMaintenance['content']} \n\nUpdated at: {currMaintenance['time']}\nMore info: https://status.riotgames.com/valorant?region=ap&locale=en_US"
    except Exception as error:
        await _log('[ERROR]',f'processing maintenances data: \n{error}')

    try:
        if bool(incidentData):
            currIncident = await _getIncident(incidentData) 
            if currIncident['id'] != prevIncidents['id']:
                prevIncidents['id'] = currIncident['id']
                
                isNeed_Append = 'incident'
                await _log('[BOT]',f'new incidents updated')
                message= f"**STATUS UPDATE**\n\n**{currIncident['title']}**\n{currIncident['content']} \n\nUpdated at: {currIncident['time']}\nMore info: https://status.riotgames.com/valorant?region=ap&locale=en_US"
    except Exception as error:
        await _log('[ERROR]',f'processing incidents data: \n{error}')

    if isNeed_Append != 'None':
        _prevUpdate, _prevMaintenance, _prevIncidents = await _readjson()
        if isNeed_Append == 'patch': appendUpdate = updateData
        else: appendUpdate = _prevUpdate

        if isNeed_Append == 'maintenance': appendMaintenance = currMaintenance    
        else: appendMaintenance = _prevMaintenance

        if isNeed_Append == 'incident': appendIncident = currIncident
        else: appendIncident = _prevIncidents
        
        isNeed_Append = 'None'
        await _sendNotification(message)
        await _appendData(appendUpdate, appendMaintenance, appendIncident)

@tasks.loop(hours=1)
async def getMatchReport():
    result, error = await matchupdate.getmatches(name='awexander', tag='007')
    try: 
        with open('data/matchlist.json', 'r') as r:
            data = json.loads(r.read())
            prevMatchid = data['matchid']
    except: 
        await _log('[ERROR]', message=f'error loading matchlist file \n {error}')

    if result is True:
        if matchupdate.match.matchid != prevMatchid:
            content = {
            'map':matchupdate.match.map, 
            'mode':matchupdate.match.gamemode, 
            'matchid': matchupdate.match.matchid,
            'score':f'{matchupdate.match.roundWon}-{matchupdate.match.roundLost}', 
            'agent':matchupdate.match.agent,
            'headshot':int(round(matchupdate.match.headshot)),
            'kda':matchupdate.match.kda,
            'adr':int(round(matchupdate.match.adr))
            }
            try:
                with open('data/matchlist.json', 'w') as w:
                    json.dump(content, w, indent=4, separators=[',',':'])
            except:
                await _log('[ERROR]', message=f'error appending matchlist data \n {error}')

            await _matchReport('[REPORT]',message=f'**AWEXANDER#007** \n Rank: {matchupdate.match.rank}',type='match', content=content)
    else:
        await _log('[ERROR]', f'error loading latest match data \n {error}')

async def _matchReport(code, message='', type='', content=Any):
    channel = bot.get_channel(reportchannel)
    embed = discord.Embed(
        title=code,
        description=message, 
        color=0x02aefd
    )
    if code == '[REPORT]':
        if type == 'match':
            embed.add_field(name='MAP', value=content['map'], inline=True)
            embed.add_field(name='MODE', value=content['mode'], inline=True)
            embed.add_field(name='SCORE', value=content['score'], inline=True)
            embed.add_field(name='AGENT', value=content['agent'], inline=True)
            embed.add_field(name='K/D', value=float(content['kda'][3]), inline=True)
            embed.add_field(name='KDA', value=f"K:{content['kda'][0]} D:{content['kda'][1]} A:{content['kda'][2]}", inline=True)
            embed.add_field(name='ADR', value=content['adr'], inline=True)
            embed.add_field(name='HS%', value=f"{content['headshot']}%", inline=True)
    await channel.send(embed=embed)

async def _getIncident(incidentData):
    for locale in incidentData[0]['titles']:
        if locale['locale'] == 'en_US':
            incident = locale['content']
            break
    
    for translation in incidentData[0]['updates'][0]['translations']:
        if translation['locale'] == 'en_US':
            content = translation['content']
            break
    content_id = incidentData[0]['updates'][0]['id']
    strtime = incidentData[0]['created_at']
    time = dt.datetime.strptime(strtime, "%Y-%m-%dT%H:%M:%S.%f%z") + dt.timedelta(hours=8)

    report = {
        'severity': incidentData[0]['incident_severity'].upper(),
        'title': incident,
        'id': incidentData[0]['id'],
        'content': content,
        'content_id': content_id,
        'time': time.strftime("%B %d, %Y at %H:%M GMT+8"),
        'status': incidentData[0]['maintenance_status']
        }
    return report

async def _getMaintenance(maintenanceData):
    print(maintenanceData)

async def _requestsupdates(url):
    try:
        resp = requests.get(url, timeout=10)
        if url == updateURL:
            return resp.json()['data'][0]
        elif url == statusURL:
            data = resp.json()['data']
            return data['maintenances'], data['incidents']

    except Exception as error:
       await _log('[ERROR]',f'requests failed: \n{error}')

async def _log(code, message='', type='', content=Any):
    uColor, red, green, blue = 0xffffff, 0xf50101, 0x01f501, 0x02aefd
    channel = bot.get_channel(logchannel)
    if code == '[ERROR]':
        uColor = red
    elif code == '[BOT]':
        uColor = green
    elif code == '[SERVER]' or '[REPORT]':
        uColor = blue
    
    embed = discord.Embed(
        title=code,
        description=message, 
        color=uColor
    )
    if code == '[REPORT]':
        if type == 'match':
            embed.add_field(name='MAP', value=content['map'], inline=True)
            embed.add_field(name='MODE', value=content['mode'], inline=True)
            embed.add_field(name='SCORE', value=content['score'], inline=True)
            embed.add_field(name='AGENT', value=content['agent'], inline=True)
            embed.add_field(name='K/D', value=float(content['kda'][3]), inline=True)
            embed.add_field(name='KDA', value=f"K:{content['kda'][0]} D:{content['kda'][1]} A:{content['kda'][2]}", inline=True)
            embed.add_field(name='ADR', value=content['adr'], inline=True)
            embed.add_field(name='HS%', value=f"{content['headshot']}%", inline=True)
        
    await channel.send(embed=embed)

async def _sendNotification(message):
    channel = bot.get_channel(servername)
    await channel.send(f'<@&{756538183810023564}> {message}')

async def _readjson():
    try:
        path = os.getcwd()
        with open(path +'/data/updates.json', 'r') as w:
            data = json.loads(w.read())
    except Exception as error:
        await _log('[ERROR]',f'failed to load updates file \n {error}')

    try:
        prevUpdate = data['updates']
    except Exception as error:
        await _log('[ERROR]',f'failed to load previous updates details \n {error}')

    try:
        prevMaintenance = data['maintenances']
    except Exception as error:
        await _log('[ERROR]',f'failed to load previous maintenances details \n {error}')

    try:
        prevIncidents = data['incidents']
    except Exception as error:
        await _log('[ERROR]',f'failed to load previous incidents details \n {error}')
    
    return prevUpdate, prevMaintenance, prevIncidents

async def _getPatch(data):
    if data['category'] == 'game_updates':
        return data['title']

async def _appendData(updateData, maintenanceData, incidenctData):
    try:
        path = os.getcwd()
        data = {           
            "updates": updateData,
            "maintenances": maintenanceData,
            "incidents": incidenctData
        }
        with open(path+'/data/updates.json', 'w') as w:
            w.write(json.dumps(data, indent=4, separators=[',',':']))
    except Exception as error:
        await _log('[ERROR]',f'error appending updates data \n {error}')
        
async def _getTimeElapsed(timeSeconds):
    minutes, seconds = divmod(timeSeconds.total_seconds(), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    upTime = []
    if days: 
        upTime.append('{:01}D '.format(int(days)))
    if hours:
        upTime.append('{:02}H '.format(int(hours)))
    if minutes:
        upTime.append('{:02}M'.format(int(minutes)))
    if seconds:
        upTime.append('{:02}S'.format(int(seconds)))

    return ':'.join(upTime)

bot.run(BOT_TOKEN)