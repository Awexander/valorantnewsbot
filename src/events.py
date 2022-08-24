import discord
from discord.ext import commands
import asyncio
from src.tasks import task
from src.utils import (
    ERROR,
    SERVER,
    BOT,
    readprevdata
)
import datetime as dt
bot = commands.Bot
print('bot in events')
print(bot)

class event():
    def __init__(self) -> None:
        self.startTime = dt.datetime.now()
        self.connectionTime = dt.datetime.now()
        self.disconnetTime = dt.datetime.now()   
        pass
    
    @bot.event()
    async def on_disconnect(self):
        self.disconnetTime = dt.datetime.now()

    @bot.event()
    async def on_resumed(self):
        self.connectionTime = dt.datetime.now()
        await BOT(f'bot is online') 

    @bot.event()
    async def on_ready(self):
        self.connectionTime = dt.datetime.now()
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening, 
                name=" raspberrypi "
                )
            )

        #prevUpdate, prevMaintenance, prevIncidents = await readprevdata()

        await asyncio.sleep(1)
        dcTime = self.disconnetTime.strftime("%A %m/%d/%Y, %H:%M")
        await BOT(f'bot is online, \n disconnected since {dcTime}')
        task.loop.start()
        task.getMatchReport.start()

    @bot.after_invoke()
    async def on_command(ctx):
        if ctx.author == bot.user:
            return

        if isinstance(ctx.channel, discord.DMChannel):
            return await BOT(f"got a direct message from <@{ctx.author.id}> \n '{ctx.message.content}'")
        
        await ctx.message.delete(delay=1)

    @bot.event()
    async def on_message(message):
        await bot.process_commands(message)
        if message.author == bot.user:
            return

        if isinstance(message.channel, discord.DMChannel):
            return await BOT(f"got a direct message from <@{message.author.id}> \n '{message.content}'")
