from discord.ext import commands

from database import database

# Overwrite basic command decorators
async def is_nsfw_or_private(ctx):
    return not ctx.guild or ctx.channel.is_nsfw()

async def guild_only(ctx):
    return ctx.guild

async def is_nsfw_and_guild(ctx):
    return ctx.guild and ctx.channel.is_nsfw()

async def is_developer(ctx):
    return await database.is_developer(ctx.author)

async def can_manage_guild(ctx):
    return ctx.author.permissions_in(ctx.channel).manage_guild

# Custom checks

def is_in_guild(guild_id):
    async def predicate(ctx):
        return ctx.guild and ctx.guild.id == guild_id
    return commands.check(predicate)

async def get_prefix(bot, message):

    # Check if message was sent in guild
    if message.guild == None:
        return ["o.", ""]
    
    return [await database.get_prefix(message.guild)]
