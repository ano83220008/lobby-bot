from discord.ext import commands
import os
import traceback

bot = commands.Bot(command_prefix='/')
token = os.environ['DISCORD_BOT_TOKEN']
cate_lobby_name = os.environ['MATCHING_CATEGORY']

#ロビーを名前のみで検索
def find_lobby_without_status(guild, name):
    cate = get_category(guild, cate_lobby_name)
    for channel in cate.channels:
        if(channel.name.endswith(name)):
            return channel

#空きのあるロビーを検索
def find_free_lobby(guild):
    cat = get_category(guild, cate_lobby_name)
    if cat==None:
        return
    for channel in cat.channels:
        l = MatchLobby
        i = channel.name.find('-')
        num = int(channel.name[:i])
        if(len(channel.members)<num):
            return channel

@bot.event
async def on_command_error(ctx, error):
    orig_error = getattr(error, "original", error)
    error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
    await ctx.send(error_msg)


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


bot.run(token)
