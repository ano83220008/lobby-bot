from discord.ext import commands
from discord import Embed
import os
import traceback

bot = commands.Bot(command_prefix='!')
token = os.environ['DISCORD_BOT_TOKEN']
cate_lobby_name = os.environ['MATCHING_CATEGORY']

class LobbyManager:
    
    guild=None
    def __init__(self, guild):
        self.guild=guild

    async def close_lobby(self, name):
        lobby = find_lobby_without_status(self.guild, name)
        if(lobby!=None):
            await lobby.delete()

    async def create_lobby(self, name):
        cate = get_category(self.guild, cate_lobby_name)
        lobby = await cate.create_text_channel("ready-" + name)
        return lobby

    async def set_status(self, name, status):
        cate = get_category(self.guild, cate_lobby_name)
        for channel in cate.channels:
            if(channel.name.endswith(name)):
                i = channel.name.find('-')
                await channel.edit(name = status + '-' + channel.name[i+1:])

    def exists_lobby(self, name):
        return find_lobby_without_status(self.guild, name)!=None

def is_my_lobby(channel, member):
    return without_status(channel.name)==member.name

def without_status(name):
    i = name.find('-')
    return name[i+1:]

def get_category(guild, key):
    if(type(key) is int):
        for cat in guild.categories:
            if cat.id==key:
                return cat
    if(type(key) is str):
        for cat in guild.categories:
            if cat.name==key:
                return cat

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

#自分のロビーを作る
@bot.command()
async def lobby(ctx):
    lm = LobbyManager(ctx.message.guild)
    if(lm.exists_lobby(ctx.message.author.name)):
        await ctx.send("lobby is exists.")
        return
    lobby = await lm.create_lobby(ctx.message.author.name)
    embed = Embed(color=0x00FF00, title='READY', description='create lobby #' + ctx.message.author.name)
    await lobby.send(embed=embed)

#full表示
@bot.command()
async def full(ctx):
    if(is_my_lobby(ctx.message.channel, ctx.message.author)):
        lm = LobbyManager(ctx.message.guild)
        await lm.set_status(ctx.message.author.name, "full")
        embed = Embed(color=0xFF0000, title='FULL', description='status changed.')
        await ctx.send(embed=embed)

#ready表示に切り替え
@bot.command()
async def ready(ctx):
    if(is_my_lobby(ctx.message.channel, ctx.message.author)):
        lm = LobbyManager(ctx.message.guild)
        await lm.set_status(ctx.message.author.name, "ready")
        embed = Embed(color=0x00FF00, title='READY', description='status changed.')
        await ctx.send(embed=embed)
        
        
#自分のロビーで実行されていたら、ロビーを閉じる
@bot.command()
async def close(ctx):
    if(is_my_lobby(ctx.message.channel, ctx.message.author)):
    #if(without_status(ctx.message.channel.name)==ctx.message.author.name):
        lm = LobbyManager(ctx.message.guild)
        await lm.close_lobby(ctx.message.author.name)
    
    
@bot.command()
async def command(ctx):
    embed = Embed(color=0x0000FF, title="command", description='コマンド一覧')
    embed.add_field(name="lobby", value="マッチロビーを作成",inline=False)
    embed.add_field(name="full", value="ロビーを満員表示にする。",inline=False)
    embed.add_field(name="ready", value="ロビーを空席表示にする",inline=False)
    embed.add_field(name="close", value="自分のロビーを閉じる。",inline=False)
    await ctx.send(embed=embed)

bot.run(token)
