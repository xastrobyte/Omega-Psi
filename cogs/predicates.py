from discord.ext.commands import check, when_mentioned_or

from cogs.errors import NotADeveloper, NotATester, NotAGuildManager, CommandDisabled, NotNSFWOrGuild
from util.database.database import database

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Async Predicates
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

async def is_developer_predicate(ctx):
    """A predicate to test if a user is a developer

    :param ctx: The context of the predicate
    """
    if not await database.bot.is_developer(ctx.author):
        raise NotADeveloper()
    return True

async def is_tester_predicate(ctx):
    """A predicate to test if a user is a tester

    :param ctx: The context of the predicate
    """
    if not await database.bot.is_tester(ctx.author):
        raise NotATester()
    return True

async def guild_manager_predicate(ctx):
    """A predicate to test if a user is a guild manager

    :param ctx: The context of the predicate
    """
    if not ctx.author.permissions_in(ctx.channel).manage_guild:
        raise NotAGuildManager()
    return True

async def is_nsfw_or_private_predicate(ctx):
    """A predicate to test if a channel is NSFW or private

    :param ctx: The context of the predicate
    """
    return not ctx.guild or ctx.channel.is_nsfw()

async def guild_only_predicate(ctx):
    """A predicate to test if a command was run in a guild

    :param ctx: The context of the predicate
    """
    return ctx.guild

async def is_nsfw_and_guild_predicate(ctx):
    """A predicate to test if a command was run in 
    an NSFW channel and inside a guild

    :param ctx: The context of the predicate
    """
    if not ctx.guild or not ctx.channel.is_nsfw():
        raise NotNSFWOrGuild()
    return True

async def is_command_enabled_predicate(ctx):
    """A predicate to test if a command is enabled
    whether globally or in a server

    :param ctx: The context of the predicate
    """

    # Check in the globally disabled commands
    if ctx.command.cog is not None:
        if ((not await database.bot.is_cog_enabled(ctx.command.cog.qualified_name) or
            not await database.bot.is_command_enabled(ctx.command.qualified_name)) and 
            not await database.bot.is_developer(ctx.author) and
            not await database.bot.is_tester(ctx.author)):
            
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
    """A predicate to test if a user can disable commands

    :param ctx: The context of the predicate
    """
    return await is_developer_predicate(ctx) or await guild_manager_predicate(ctx)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Checks
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def is_developer():
    """A check to make sure only a developer can run a command"""
    return check(is_developer_predicate)

def is_tester():
    """A check to make sure only a tester can run a command"""
    return check(is_tester_predicate)

def guild_manager():
    """A check to make sure only a guild manager can run a command"""
    return check(guild_manager_predicate)

def is_nsfw_or_private():
    """A check to make sure a channel is NSFW or private"""
    return check(is_nsfw_or_private_predicate)

def guild_only():
    """A check to make sure a command can only be run in a guild"""
    return check(guild_only_predicate)

def is_nsfw_and_guild():
    """A check to make sure a channel is NSFW and in a guild"""
    return check(is_nsfw_and_guild_predicate)

def is_command_enabled():
    """A check to make a command is enabled"""
    return check(is_command_enabled)

def can_disable_commands():
    """A check to make sure only guild managers can disable commands"""
    return check(can_disable_commands_predicate)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Other Predicates/Checks
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def is_in_guild(*guilds):
    """A check to see if a command can only be run in the
    specified guilds
    
    :param guilds: The guilds to allow a command to run in
    """
    async def predicate(ctx):
        return ctx.guild and ctx.guild.id in guilds
    return check(predicate)

async def get_prefix(bot, message):
    """Retrieves the prefix for a guild or private message

    :param bot: The bot object
    :param message: The message to check the guild prefix of
    """

    # Check if message was not sent in guild
    if message.guild == None:
        return ["o..", "o.", ""]
    
    guild_prefix = await database.guilds.get_prefix(message.guild)
    valid_prefixes = [guild_prefix.strip() + ".", guild_prefix]
    return when_mentioned_or(*valid_prefixes)(bot, message)