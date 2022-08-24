@bot.event 
async def on_disconnect():
    global disconnetTime
    disconnetTime = dt.datetime.now()

@bot.event
async def on_resumed():
    global connectionTime
    connectionTime = dt.datetime.now()
    await _log('[BOT]',f'bot is online') 

@bot.event
async def on_ready():
    global connectionTime, disconnetTime, prevUpdate, prevMaintenance, prevIncidents
    connectionTime = dt.datetime.now()
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, 
            name=" raspberrypi "
            )
        )

    prevUpdate, prevMaintenance, prevIncidents = await _readjson()

    await asyncio.sleep(1)
    dcTime = disconnetTime.strftime("%A %m/%d/%Y, %H:%M")
    await _log('[BOT]',f'bot is online, \n disconnected since {dcTime}')
    loop.start()
    getMatchReport.start()

@bot.after_invoke
async def on_command(ctx):
    if ctx.author == bot.user:
        return

    if isinstance(ctx.channel, discord.DMChannel):
        return await _log('[BOT]',f"got a direct message from <@{ctx.author.id}> \n '{ctx.message.content}'")
    
    await ctx.message.delete(delay=1)

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user:
        return

    if isinstance(message.channel, discord.DMChannel):
        return await _log('[BOT]',f"got a direct message from <@{message.author.id}> \n '{message.content}'")
