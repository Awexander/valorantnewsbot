import discord 
from discord.ext import commands
from src.CONFIG import BLUE
from src.matches import getmatchinfo
from src.utils import utils
import datetime as dt
import os

class command(commands.Cog):
    def __init__(self, bot):
        self.region = 'ap'
        self.matches = getmatchinfo()
        self.matchinfo = self.matches.match
        self.utils = utils(bot)
        
        self.path = os.getcwd()
        self.startTime = dt.datetime.now()

    @commands.command()
    async def id(self, ctx):
        return await self.utils.SERVER(f'Channel ID: {ctx.channel.id}')

    @commands.command()
    async def uptime(self, ctx):
        upSeconds = dt.datetime.now() - self.startTime
        connSeconds = dt.datetime.now() - self.connectionTime
        
        embed = discord.Embed(title='[SERVER]', color=BLUE)
        embed.add_field(name='SERVER TIME', value=await self.utils.TIME(upSeconds), inline=False)
        embed.add_field(name='BOT TIME', value=await self.utils.TIME(connSeconds), inline=False)

        await self.utils.LOG(embed)

    @commands.command()
    async def update(self, ctx):
        update, maintenance, incidents  = await self.utils.readprevdata()
        return await self.utils.SERVER(f"Latest update: {update['title']} \n Updated at: {update['date']}")

    @commands.command()
    async def latestmatch(self, ctx, *,valorantid):
        #TODO: get lastmatch from db not from api
        nametag = valorantid.split('#')
        result , error= await self.matches.getmatches(nametag[0], nametag[1])
        if result is True:
            content = {
            'map':self.matchinfo.map, 
            'mode':self.matchinfo.gamemode, 
            'score':f'{self.matchinfo.roundWon}-{self.matchinfo.roundLost}', 
            'agent':self.matchinfo.agent,
            'headshot':int(round(self.matchinfo.headshot)),
            'kda':self.matchinfo.kda,
            'adr':int(round(self.matchinfo.adr))
            }
            await self.utils.matchReport(message=f"**{id['name'].upper()}#{id['tag'].upper()}** \n Rank: {self.matchinfo.rank}",type='match', content=content)
        else:
            await self.utils.ERROR(f'error loading latest match data \n {error}')

    @commands.command()
    async def setregion(self, ctx, *, region):
        self.matches.region = region
        return await self.utils.SERVER(f'Changed region to: {self.matches.region}')
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        return await self.utils.ERROR(f'{error}')
