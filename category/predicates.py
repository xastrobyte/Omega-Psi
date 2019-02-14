from discord.ext import commands

from database import database

def is_developer():
    async def predicate(ctx):
        return await database.is_developer(ctx.author)
    return commands.check(predicate)

async def is_developer_async(ctx):
    return await database.is_developer(ctx.author)

def is_in_guild(guild_id):
    async def predicate(ctx):
        return ctx.guild and ctx.guild.id == guild_id
    return commands.check(predicate)

def is_nsfw_or_private():
    async def predicate(ctx):
        return not ctx.guild or ctx.channel.is_nsfw()
    return commands.check(predicate)

async def is_nsfw_or_private_async(ctx):
    return not ctx.guild or ctx.channel.is_nsfw()

async def get_prefix(bot, message):

    # Check if message was sent in guild
    if message.guild == None:
        return ["o.", ""]
    
    return [await database.get_prefix(message.guild)]