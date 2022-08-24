import discord
from discord.ext import commands
import datetime as dt
import asyncio
from src.tasks import task as tasks
from src.commands import command
from src.CONFIG import BOT_TOKEN
from src.utils import utils

description: str= ''' valorant game updates, server status and scheduled maintenance '''
intents = discord.Intents.default()
intents.members = True
intents.messages = True

bot = commands.Bot(command_prefix='.', description=description, intents=intents)
task = tasks(bot)
util = utils(bot)

@bot.event
async def on_resumed():
    command.connectionTime = dt.datetime.now()
    await util.BOT(f'bot is online') 

@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, 
            name=" raspberrypi "
            )
        )

    task.prevUpdate, task.prevMaintenance, task.prevIncidents = await util.readprevdata()
    command.connectionTime = dt.datetime.now()
    await asyncio.sleep(1)
    await util.BOT(f'bot is online')
    task.loop.start()
    task.getMatchReport.start()

@bot.after_invoke
async def on_command(ctx):
    if ctx.author == bot.user:
        return

    if isinstance(ctx.channel, discord.DMChannel):
        return await util.BOT(f"got a direct message from <@{ctx.author.id}> \n '{ctx.message.content}'")
    
    await ctx.message.delete(delay=1)

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user:
        return

    if isinstance(message.channel, discord.DMChannel):
        return await util.BOT(f"got a direct message from <@{message.author.id}> \n '{message.content}'")

bot.add_listener(command.on_command_error)
bot.add_cog(command(bot))
bot.run(BOT_TOKEN)
