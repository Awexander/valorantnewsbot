from ..main import discord, command, event
from datetime import datetime

bot = command.Bot
class command():
    def __init__(self):
        self.region = 'ap'
        pass

    @bot.command()
    async def id(self, ctx):
        return await _log('[SERVER]',f'Channel ID: {ctx.channel.id}')

    @bot.command()
    async def uptime(self, ctx):
        upSeconds = dt.datetime.now() - event.startTime
        connSeconds = dt.datetime.now() - event.connectionTime
        
        embed = discord.Embed(title='[SERVER]', color=0x02aefd)
        embed.add_field(name='SERVER TIME', value=await _getTimeElapsed(upSeconds), inline=False)
        embed.add_field(name='BOT TIME', value=await _getTimeElapsed(connSeconds), inline=False)

        await _sendlog(embed)

    async def _sendlog(self, embed):
        channel = bot.get_channel(logchannel)
        return await channel.send(embed=embed)

    @bot.command()
    async def update(self, ctx):
        message = await _readjson()
        return await _log('[SERVER]', f"Latest update: {message['updates']['title']} \n Updated at: {message['updates']['date']}")

    @bot.listen()
    async def on_command_error(self, ctx, error):
        return await _log('[ERROR]', f'{error}')

    @bot.command()
    async def lastmatch(self, ctx, *,valorantid):
        #TODO: get lastmatch from db not from api
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
    async def region(self, ctx, *, region):
        matchupdate.region = region
        return await _log('[SERVER]', f'Changed region to: {region}')
