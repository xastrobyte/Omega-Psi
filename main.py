import app
from app import keep_alive
from discord import Embed, Status, Activity
from discord.ext.commands import AutoShardedBot
from os import environ
from traceback import format_exception

from cogs.errors import COMMAND_FAILED_ERROR, CommandDisabled, COMMAND_DISABLED_ERROR, NotNSFWOrGuild, NOT_NSFW_OR_GUILD_ERROR
from cogs.globals import FIELD_THRESHOLD
from cogs.help_command import Help, cogs
from cogs.predicates import get_prefix, is_command_enabled_predicate

from util.database.database import database
from util.discord import update_top_gg
from util.ifttt import IFTTT

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

bot = AutoShardedBot(
    command_prefix = get_prefix, case_insensitive = True,
    help_command = Help()
)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@bot.check
async def command_enabled(ctx):
    return await is_command_enabled_predicate(ctx)

@bot.event
async def on_ready():

    # Set the presence of the bot when it's ready
    print("i'm ready to go")
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

@bot.event
async def on_command_error(ctx, error):

    # Check if the error pertains to a disabled command
    #   dont send a message to the error channel
    if isinstance(error, CommandDisabled):
        await ctx.send(embed = COMMAND_DISABLED_ERROR(ctx.command.qualified_name))
    
    # Check if the error pertains to an is_nsfw_and_guild error
    elif isinstance(error, NotNSFWOrGuild):
        await ctx.send(embed = NOT_NSFW_OR_GUILD_ERROR(ctx.command.qualified_name))

    # Display that the command failed at some point to the user
    #   and send the error to the error channel
    #   however, only send the message if ctx.command exists
    elif ctx.command:
        await ctx.send(embed = COMMAND_FAILED_ERROR(ctx.command))

        # Get only the files that pertain to the bot
        #   if any files are found outside of the bot
        #   ignore them and stop there
        exc = format_exception(type(error), error, error.__traceback__)

        # Create embed
        embed = Embed(
            title = "Command Failed",
            description = str(error),
            color = 0x800000
        )

        # Add fields
        fields = {
            "Command Author": ctx.author,
            "Guild Name": ctx.guild.name if ctx.guild != None else "Private Message",
            "Channel Name": ctx.channel.name if ctx.guild != None else "Private Message with {}".format(
                str(ctx.author)
            )
        }

        # Create traceback fields
        tb_fields = []
        tb_field = ""
        for line in exc:

            line += "\n"

            if len(tb_field) + len(line) > FIELD_THRESHOLD:
                tb_fields.append(tb_field)
                tb_field = ""
            
            tb_field += line
        
        if len(tb_field) > 0:
            tb_fields.append(tb_field)

        for field in fields:
            embed.add_field(
                name = field,
                value = fields[field],
                inline = False
            )
        
        count = 0
        for field in tb_fields:
            count += 1
            embed.add_field(
                name = "Traceback {}".format(
                    "({} / {})".format(
                        count, len(tb_fields)
                    ) if len(tb_fields) > 1 else ""
                ),
                value = "```py\n{}\n```".format(field),
                inline = False
            )
        
        # Get the error channel
        channel = bot.get_channel(int(environ["COMMAND_ERROR_CHANNEL"]))

        await channel.send(
            embed = embed
        )

@bot.event
async def on_guild_join(guild):
    await update_top_gg(bot)

@bot.event
async def on_guild_remove(guild):
    await update_top_gg(bot)

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