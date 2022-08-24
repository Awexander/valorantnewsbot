import asyncio
from email import message
import discord
from discord.ext import commands
from src.CONFIG import (
    ANNOUNCECHANNEL,
    LOGCHANNEL,
    GREEN, 
    RED,
    BLUE,
    REPORTCHANNEL
)
import os
import json

bot = commands.Bot

async def readprevdata():
    try:
        path = os.cwd()
        with open(path +'/data/updates.json', 'r') as w:
            data = json.loads(w.read())
    except Exception as error:
        await ERROR(f'failed to load updates file \n {error}')

    try:
        prevUpdate = data['updates']
    except Exception as error:
        await ERROR(f'failed to load previous updates details \n {error}')

    try:
        prevMaintenance = data['maintenances']
    except Exception as error:
        await ERROR(f'failed to load previous maintenances details \n {error}')

    try:
        prevIncidents = data['incidents']
    except Exception as error:
        await ERROR(f'failed to load previous incidents details \n {error}')
    
    return prevUpdate, prevMaintenance, prevIncidents

async def ERROR(message):
    embed = discord.Embed(title='[ERROR]', description=message, color=RED)
    return await log(content=embed)

async def BOT(message):
    embed = discord.Embed(title='[BOT]', description=message, color=GREEN)
    return await log(content=embed)

async def SERVER(message):
    embed = discord.Embed(title='[SERVER]', description=message, color=BLUE)
    return await log(content=embed)

async def REPORT(embed=discord.Embed):
    return await bot.get_channel(REPORTCHANNEL).send(embed=embed)

async def NOTIFICATION(message=str):
    return await bot.get_channel(ANNOUNCECHANNEL).send(message)
    
async def log(message=str, content=discord.Embed):
    return await bot.get_channel(LOGCHANNEL).send(message=message, embed=content)
