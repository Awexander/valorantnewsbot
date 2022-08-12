

import asyncio
from dataclasses import field
import discord
from discord.ext import commands, tasks
from datetime import datetime
import requests
import json

intents = discord.Intents.default()
intents.members = True
intents.messages = True

updateURL = 'https://api.henrikdev.xyz/valorant/v1/website/en-us'
statusURL = 'https://api.henrikdev.xyz/valorant/v1/status/ap'
channelAwe, servername, logchannel = 1006779252215132161, 723078810702184448, 1007170918549819412
uColor, red, green, blue = 0xffffff, 0xf50101, 0x01f501, 0x02aefd
updatesjson, maintenancesjson, incidentsjson = './updates.json', './maintenances.json', './incidents.json'
updateList, maintenanceList, incidentsList = [],[],[]
prevUpdate, prevMaintenance, prevIncidents = '','',''

description: str= ''' valorant game updates, server status and scheduled maintenance '''

bot = commands.Bot(command_prefix='--', description=description, intents=intents)
startTime = datetime.now()
connectionTime = datetime.now()

@bot.event 
async def on_disconnect():
    await _log('[BOT]',f'disconnected')

@bot.event
async def on_resumed():
    await _log('[BOT]',f'bot is online') 
    global connectionTime
    connectionTime = datetime.now()

@bot.event
async def on_ready():
    global connectionTime
    connectionTime = datetime.now()
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, 
            name=" raspberrypi "
            )
        )

    await _log('[BOT]',f'bot is online')
    await _readjson()
    await asyncio.sleep(3)
    loop.start()

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
    upSeconds = datetime.now() - startTime
    connSeconds = datetime.now() - connectionTime
    
    upTime = _getupTime(upSeconds)
    connTime = _getconnTime(connSeconds)

    return await _log('[SERVER]',f"[SERV TIME] {upTime} \n[BOT TIME] {connTime}")

@bot.command()
async def update(ctx):
    return await _log('[SERVER]', f"Latest update: {updateList[0]['title']} \n Updated at: {updateList[0]['date']}")


@tasks.loop(seconds=20)
async def loop():
    global prevUpdate, prevMaintenance, prevIncidents, updatesjson, maintenancesjson, incidentsjson
    updateData = await getJSON(updateURL)
    maintenanceData, incidenctData = await getJSON(statusURL)
    
    try:   
        if updateData['category'] == 'game_updates':
            if updateData['title'] != prevUpdate:
                prevUpdate = updateData['title']
                await _log('[BOT]',f'new update is available')
                if updateData['external_link'] != None:
                    link = updateData['external_link']
                else:
                    link = updateData['url']
                
                #notification here
                await _sendNotification(f"<@&{756538183810023564}> **GAME UPDATE** \n\n {updateData['title']} \n\n {link}")
                
                updateList.insert(0, updateData)
                with open(updatesjson, 'w') as up:
                    json.dump(updateList, up, indent=4, separators=[',',':'])

    except Exception as error:
        await _log('[ERROR]',f'processing updates data: \n{error}')

    try:
        if bool (maintenanceData):
            if maintenanceData['titles'] != prevMaintenance:
                await _log('[BOT]', maintenanceData)
    except Exception as error:
        await _log('[ERROR]',f'processing maintenances data: \n{error}')

    try:
        if bool(incidenctData):     
            if incidenctData['title'] != prevIncidents:
                await _log('[BOT]',f'{incidenctData}')
    except Exception as error:
        await _log('[ERROR]',f'processing incidents data: \n{error}')

async def getJSON(url):
    try:
        resp = requests.get(url, timeout=10)
        if url == updateURL:
            return resp.json()['data'][0]
        elif url == statusURL:
            data = resp.json()['data']
            return data['maintenances'], data['incidents']

    except Exception as error:
       await _log('[ERROR]',f'requests failed: \n{error}')

async def _log(code, message):
    global uColor, red, green
    channel = bot.get_channel(logchannel)
    if code == '[ERROR]':
        uColor = red
    elif code == '[BOT]':
        uColor = green
    elif code == '[SERVER]':
        uColor = blue
    else:
        uColor = 0xffffff

    embed = discord.Embed(title=code,description=message, color=uColor)
    await channel.send(embed=embed)

async def _sendNotification(message):
    channel = bot.get_channel(servername)
    await channel.send(f'{message}')

async def _readjson():
    global prevUpdate, prevMaintenance, prevIncidents, updateList, maintenanceList, incidentsList, updatesjson, maintenancesjson, incidentsjson
    try:
        with open('updates.json', 'rb') as upjson:
            updateList = json.load(upjson)
            prevUpdate = updateList[0]['title']
    except:
        await _log('[ERROR]',f'failed to load updates.json')
    
    try:
        with open(maintenancesjson, 'rb') as maint:
            maintenanceList = json.load(maint)
            prevMaintenance = maintenanceList[0]['title']
    except:
        await _log('[ERROR]',f'failed to load maintenances.json')
    
    try:
        with open(incidentsjson, 'rb') as inc:
            incidentsList = json.load(inc)
            prevIncidents = incidentsList[0]['title']
    except:
        await _log('[ERROR]',f'failed to load incidents.json')

def _getupTime(upSeconds):
    minutes, seconds = divmod(upSeconds.total_seconds(), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    upTime = []
    if days: 
        upTime.append('{:01} Days'.format(int(days)))
    if hours:
        upTime.append('{:01} Hours'.format(int(hours)))
    if minutes:
        upTime.append('{:01} Minutes'.format(int(minutes)))
    if seconds:
        upTime.append('{:01} Seconds'.format(int(seconds)))

    return ','.join(upTime)

def _getconnTime(connSeconds):
    minutes, seconds = divmod(connSeconds.total_seconds(), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    connTime = []
    if days: 
        connTime.append('{:01} Days'.format(int(days)))
    if hours:
        connTime.append('{:01} Hours'.format(int(hours)))
    if minutes:
        connTime.append('{:01} Minutes'.format(int(minutes)))
    if seconds:
        connTime.append('{:01} Seconds'.format(int(seconds)))

    return ','.join(connTime)

bot.run('NzIzMDkwNTg1MDE5NDgyMTU1.GM8W1H.DqsAL1RM5-1tXehKSgGa3gfD-cAyubStdXj6dk')