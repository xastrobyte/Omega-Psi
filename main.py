import app
from app import keep_alive
from discord import Embed, Status, Activity, Intents
from discord.ext.commands import AutoShardedBot
from os import environ
from traceback import format_exception

from cogs.errors import (
    COMMAND_FAILED_ERROR, 
    CommandDisabled, COMMAND_DISABLED_ERROR, 
    NotNSFWOrGuild, NOT_NSFW_OR_GUILD_ERROR,
    NotADeveloper, NOT_A_DEVELOPER_ERROR)

from cogs.help_command import Help, cogs
from cogs.predicates import get_prefix, is_command_enabled_predicate

from util.database.database import database
from util.discord import update_top_gg
from util.functions import create_fields, add_fields
from util.ifttt import IFTTT

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Due to Discord's new API update, we must specify our intent
#   with using their API specifically regarding member's and their presences
intents = Intents.all()

bot = AutoShardedBot(
    command_prefix = get_prefix, case_insensitive = True,
    help_command = Help(),
    intents = intents
)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@bot.check
async def command_enabled(ctx):
    """A check done on every command to determine if 
    the command that was specified is enabled or not

    :param ctx: The context of where the message was sent
    """
    return await is_command_enabled_predicate(ctx)

@bot.event
async def on_ready():
    """This is run when the bot is ready to run"""

    # Set the presence of the bot when it's ready
    await bot.change_presence(
        status = Status.online,
        activity = Activity(
            name = "o.help in {} server{}".format(len(bot.guilds), "s" if len(bot.guilds) != 1 else ""),
            type = 2, # Listening to
            url = "https://twitch.tv/FellowHashbrown"
        )
    )

    # Send a message about restarting only if the restart happened through the command
    restart = await database.bot.get_restart()
    if restart["send"]:

        # Get the channel and author to send a message and mention the author
        channel = bot.get_channel(int(restart["channel_id"]))
        author = bot.get_user(int(restart["author_id"]))
        if not channel:
            channel = author

        # Reset the send value in the database and send a message to the author
        restart["send"] = False
        await database.bot.set_restart(restart)
        await channel.send("{}, I'm back!".format(author.mention))
    
    # Send a push notification to IFTTT
    await IFTTT.push(
        "omega_psi_push",
        "Omega Psi is online!",
        "",
        "Omega Psi is online and ready to go!"
    )
    print("i'm ready to go")

@bot.event
async def on_command(ctx):
    """Emulates the bot typing to show the user their
    command is being processed

    :param ctx: The context of where to send the typing dialogue to
    """
    async with ctx.typing(): pass

@bot.event
async def on_command_error(ctx, error):
    """This is an event that happens when an error
    occurs on any command

    :param ctx: The context of where the error occurred
    :param error: The error that occurred
    """

    # Check if the error pertains to a disabled command
    #   dont send a message to the error channel
    if isinstance(error, CommandDisabled):
        await ctx.send(embed = COMMAND_DISABLED_ERROR(ctx.command.qualified_name))
    
    # Check if the error pertains to an is_nsfw_and_guild error
    elif isinstance(error, NotNSFWOrGuild):
        await ctx.send(embed = NOT_NSFW_OR_GUILD_ERROR(ctx.command.qualified_name))
    
    # Check if the error pertains to not_a_developer error
    elif isinstance(error, NotADeveloper):
        await ctx.send(embed = NOT_A_DEVELOPER_ERROR)

    # Display that the command failed at some point to the user
    #   and send the error to the error channel
    #   however, only send the message if ctx.command exists
    elif ctx.command:
        await ctx.send(embed = COMMAND_FAILED_ERROR(ctx.command))

        # Create embed
        exc = format_exception(type(error), error, error.__traceback__)
        embed = Embed(
            title = "Command Failed",
            description = str(error),
            color = 0x800000
        )

        # Add fields
        fields = {
            "Command Author": ctx.author,
            "Guild Name": ctx.guild.name if ctx.guild is not None else "Private Message",
            "Channel Name": ctx.channel.name if ctx.guild is not None else "Private Message with {}".format(
                str(ctx.author)
            )
        }
        for field in fields:
            embed.add_field(
                name = field,
                value = fields[field],
                inline = False
            )

        # Create and add traceback fields
        add_fields(embed, "Traceback", create_fields(
            exc, 
            key = lambda field: f"```py\n{field}\n```"
        ))
        
        # Get the error channel
        channel = bot.get_channel(int(environ["COMMAND_ERROR_CHANNEL"]))
        await channel.send(
            embed = embed
        )

@bot.event
async def on_guild_join(guild):
    """This is run whenever Omega Psi is added to a new server

    :param guild: The guild that Omega Psi was added to
    """
    await update_top_gg(bot)
    await bot.change_presence(
        status = Status.online,
        activity = Activity(
            name = "o.help in {} server{}".format(len(bot.guilds), "s" if len(bot.guilds) != 1 else ""),
            type = 2, # Listening to
            url = "https://twitch.tv/FellowHashbrown"
        )
    )

@bot.event
async def on_guild_remove(guild):
    """This is run whenever Omega Psi is removed from a server

    :param guild: The guild that Omega Psi was removed from
    """
    await update_top_gg(bot)
    await bot.change_presence(
        status = Status.online,
        activity = Activity(
            name = "o.help in {} server{}".format(len(bot.guilds), "s" if len(bot.guilds) != 1 else ""),
            type = 2, # Listening to
            url = "https://twitch.tv/FellowHashbrown"
        )
    )

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == "__main__":

    for cog in cogs:
        try:
            bot.load_extension(cogs[cog]["extension"])
        except Exception as error:
            print("\n".join(format_exception(type(error), error, error.__traceback__)))
            print("{} cannot be loaded.\n - {}".format(cog, error))
    
    app.OMEGA_PSI = bot
    keep_alive(bot, cogs)
    bot.run(environ["BOT_TOKEN"])