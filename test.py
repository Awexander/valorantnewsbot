

import discord
from discord.ext import commands
from .src import commands as cmd , events, tasks
from src import CONFIG
import json
import os


description: str= ''' valorant game updates, server status and scheduled maintenance '''
intents = discord.Intents.default()
intents.members = True
intents.messages = True
bot = commands.Bot(command_prefix='.', description=description, intents=intents)
command = cmd.command()
event = events.event()
task = tasks.task()

BOT_TOKEN = CONFIG.BOT_TOKEN
isNeed_Append = 'None'

async def _log(code, message='', type='', content=[]):
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

async def _sendNotification(message, isNeed_Append, updateData, currMaintenance, currIncident):
    if isNeed_Append != 'None':
        _prevUpdate, _prevMaintenance, _prevIncidents = await _readjson()
        if isNeed_Append == 'patch': appendUpdate = updateData
        else: appendUpdate = _prevUpdate

        if isNeed_Append == 'maintenance': appendMaintenance = currMaintenance    
        else: appendMaintenance = _prevMaintenance

        if isNeed_Append == 'incident': appendIncident = currIncident
        else: appendIncident = _prevIncidents
        
        isNeed_Append = 'None'
        await _appendData(appendUpdate, appendMaintenance, appendIncident)

    channel = bot.get_channel(servername)
    await channel.send(f'<@&{756538183810023564}> {message}')





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