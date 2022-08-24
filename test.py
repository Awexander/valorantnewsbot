import discord
from discord.ext import commands
from src.tasks import task as tasks

description: str= ''' valorant game updates, server status and scheduled maintenance '''
intents = discord.Intents.default()
intents.members = True
intents.messages = True
bot = commands.Bot(command_prefix='.', description=description, intents=intents)
BOT_TOKEN = ''
task = tasks(bot)
bot.run(BOT_TOKEN)
