from discord.ext.commands import check, when_mentioned_or

from cogs.errors import NotADeveloper, NotAGuildManager, CommandDisabled, NotNSFWOrGuild
from util.database.database import database

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Async Predicates
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

async def is_developer_predicate(ctx):
    if not await database.bot.is_developer(ctx.author):
        raise NotADeveloper()
    return True

async def guild_manager_predicate(ctx):
    if not ctx.author.permissions_in(ctx.channel).manage_guild:
        raise NotAGuildManager()
    return True

async def is_nsfw_or_private_predicate(ctx):
    return not ctx.guild or ctx.channel.is_nsfw()

async def guild_only_predicate(ctx):
    return ctx.guild

async def is_nsfw_and_guild_predicate(ctx):
    if not ctx.guild or not ctx.channel.is_nsfw():
        raise NotNSFWOrGuild()
    return True

async def is_command_enabled_predicate(ctx):

    # Check in the globally disabled commands
    if not await database.bot.is_command_enabled(ctx.command.qualified_name) and not await database.bot.is_developer(ctx.author):
        raise CommandDisabled()
    
    # Check in the guild disabled commands
    if ctx.guild:
        if not await database.guilds.is_command_enabled(ctx.guild, ctx.command.qualified_name):

            # Check if the user is a guild manager, let them run it
            try: 
                await guild_manager_predicate(ctx)
                return True
            except: 
                raise CommandDisabled()
    return True

async def can_disable_commands_predicate(ctx):
    return await is_developer_predicate(ctx) or await guild_manager_predicate(ctx)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Checks
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def is_developer():
    return check(is_developer_predicate)

def guild_manager():
    return check(guild_manager_predicate)

def is_nsfw_or_private():
    return check(is_nsfw_or_private_predicate)

def guild_only():
    return check(guild_only_predicate)

def is_nsfw_and_guild():
    return check(is_nsfw_and_guild_predicate)

def is_command_enabled():
    return check(is_command_enabled)

def can_disable_commands():
    return check(can_disable_commands_predicate)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Other Predicates/Checks
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def is_in_guild(guild_id):
    async def predicate(ctx):
        return ctx.guild and ctx.guild.id == guild_id
    return check(predicate)

async def get_prefix(bot, message):

    # Check if message was not sent in guild
    if message.guild == None:
        return ["o..", "o.", ""]
    
    guild_prefix = await database.guilds.get_prefix(message.guild)
    valid_prefixes = [guild_prefix.strip() + ".", guild_prefix]
    return when_mentioned_or(*valid_prefixes)(bot, message)