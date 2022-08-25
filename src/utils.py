import discord
from src.CONFIG import (
    ANNOUNCECHANNEL,
    LOGCHANNEL,
    GREEN,
    RANKCHANNEL, 
    RED,
    BLUE,
    REPORTCHANNEL,
    SLASH
)
import os
import json

class utils():
    def __init__(self, bot) -> None:
        self.bot = bot
        pass
    async def readprevdata(self):
        try:
            path = os.getcwd()
            with open(path + f'{SLASH}data{SLASH}updates.json', 'r') as w:
                data = json.loads(w.read())
        except Exception as error:
            await self.ERROR(f'failed to load updates file \n {error}')

        try:
            prevUpdate = data['updates']
        except Exception as error:
            await self.ERROR(f'failed to load previous updates details \n {error}')

        try:
            prevMaintenance = data['maintenances']
        except Exception as error:
            await self.ERROR(f'failed to load previous maintenances details \n {error}')

        try:
            prevIncidents = data['incidents']
        except Exception as error:
            await self.ERROR(f'failed to load previous incidents details \n {error}')
        
        return prevUpdate, prevMaintenance, prevIncidents

    async def ERROR(self, message):
        if self.lastmessage == message:
            return 
        else:
            #avoid repeating error log
            self.lastmessage = message
            embed = discord.Embed(title='[ERROR]', description=message, color=RED)
            return await self.LOG(content=embed)

    async def BOT(self, message):
        embed = discord.Embed(title='[BOT]', description=message, color=GREEN)
        return await self.LOG(content=embed)

    async def SERVER(self, message):
        embed = discord.Embed(title='[SERVER]', description=message, color=BLUE)
        return await self.LOG(content=embed)

    async def REPORT(self, embed=discord.Embed):
        return await self.bot.get_channel(REPORTCHANNEL).send(embed=embed)
    
    async def RANK(self, embed=discord.Embed):
        return await self.bot.get_channel(RANKCHANNEL).send(embed=embed)

    async def NOTIFICATION(self, message=str):
        return await self.bot.get_channel(ANNOUNCECHANNEL).send(message)

    async def LOG(self, content=discord.Embed):
        return await self.bot.get_channel(LOGCHANNEL).send(embed=content)

    async def TIME(self, timeSeconds):
        minutes, seconds = divmod(timeSeconds.total_seconds(), 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        upTime = []
        if days: 
            upTime.append('**{:01}** Days'.format(int(days)))
        if hours:
            upTime.append(' **{:02}** Hours'.format(int(hours)))
        if minutes:
            upTime.append(' **{:02}** Minutes'.format(int(minutes)))
        if seconds:
            upTime.append(' **{:02}** Seconds'.format(int(seconds)))

        return ':'.join(upTime)

    async def matchReport(self, message='', type='', content=[]):
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

            return await self.REPORT(embed=embed)
        elif type == 'rank':
            embed.add_field(name='Previous Rank', value=content['prevRank'])
            embed.add_field(name='Current Rank', value=content['currRank'])

            return await self.RANK(embed=embed)
