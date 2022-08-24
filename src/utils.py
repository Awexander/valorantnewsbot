import discord
from src.CONFIG import (
    ANNOUNCECHANNEL,
    LOGCHANNEL,
    GREEN, 
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
        embed = discord.Embed(title='[ERROR]', description=message, color=RED)
        return await self.log(content=embed)

    async def BOT(self, message):
        embed = discord.Embed(title='[BOT]', description=message, color=GREEN)
        return await self.log(content=embed)

    async def SERVER(self, message):
        embed = discord.Embed(title='[SERVER]', description=message, color=BLUE)
        return await self.log(content=embed)

    async def REPORT(self, embed=discord.Embed):
        return await self.bot.get_channel(REPORTCHANNEL).send(embed=embed)

    async def NOTIFICATION(self, message=str):
        return await self.bot.get_channel(ANNOUNCECHANNEL).send(message)

    async def log(self, content=discord.Embed):
        channel = self.bot.get_channel(LOGCHANNEL)
        return await channel.send(embed=content)
