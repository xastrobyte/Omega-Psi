from util.file.omegaPsi import OmegaPsi
from util.file.server import Server

from keepAlive import keepAlive
from util.utils import sendMessage, sendErrorMessage, getChannel

from discord.ext.commands import Bot

from random import choice as choose
import discord, os, sys, traceback

# Open Bot client
omegaPsi = Bot(command_prefix = OmegaPsi.PREFIX)
omegaPsi.remove_command("help")

extensions = [
    "category.help",
    "category.code",
    "category.game",
    "category.gif",
    "category.insult",
    "category.math",
    "category.rank",
    "category.weather",
    "category.misc",
    "category.serverModerator",
    "category.botModerator"
]

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Basic Events
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@omegaPsi.event
async def on_ready():
    await omegaPsi.change_presence(
        status = discord.Status.online,
        activity = discord.Activity(
            name = OmegaPsi.getActivityName(),
            type = OmegaPsi.getActivityType()
        )
    )

@omegaPsi.event
async def on_error(event, *args, **kwargs):
    await sendErrorMessage(omegaPsi,
        message = (
            "".join(traceback.format_tb(sys.exc_info()[2])) + "\n" +
            str(sys.exc_info()[0]) + " --> " + str(sys.exc_info()[1])
        )
    )

@omegaPsi.event
async def on_message(message):
    origMessage = message

    # Only run if a real user sends a message
    if not message.author.bot:

        # Check if message was in server
        if message.guild != None:

            # Update experience; Get message
            message = Server.updateExperience(message)

            # Rank up message existed
            if message != None:

                await sendMessage(
                    omegaPsi, origMessage,
                    message = message, plain = True
                )

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Server Events
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@omegaPsi.event
async def on_server_join(server):

    # Open server file
    server = Server.openServer(server)

    await sendMessage(omegaPsi,
        getChannel(omegaPsi,
            os.environ["DISCORD_TEST_SERVER_ID"],
            os.environ["DISCORD_TEST_CHANNEL_ID"]
        ),
        embed = discord.Embed(
            title = "Omega Psi Joined a Server",
            description = "<@{}>".format(),
            colour = 0x00FF80
        )
    )

    # Close server file
    Server.closeServer(server)

@omegaPsi.event
async def on_server_remove(server):
    pass

@omegaPsi.event
async def on_server_update(before, after):
    pass

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Channel Events
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@omegaPsi.event
async def on_channel_delete(channel):
    pass

@omegaPsi.event
async def on_channel_create(channel):
    pass

@omegaPsi.event
async def on_channel_update(before, after):
    pass

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Member Events
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@omegaPsi.event
async def on_member_join(member):

    # Open server file
    server = Server.openServer(member.guild)

    # Update member
    Server.updateMember(member.guild, member)

    # Send message in join message channel
    if server["join_message"]["active"]:
        await sendMessage(
            omegaPsi,
            member.guild.get_channel(
                server["join_message"]["channel"]
            ),
            message = choose(Server.JOIN_MESSAGES).format(
                "<@{}>".format(member.id)
            )
        )

    # Close server file
    Server.closeServer(server)

@omegaPsi.event
async def on_member_remove(member):

    # Open servers file
    server = Server.openServer(member.guild)

    # Remove member
    if str(member.id) in server["members"]:
        server["members"].pop(str(member.id))

    # Close servers file
    Server.closeServer(server)

@omegaPsi.event
async def on_member_update(before, after):
    """

    # Open server file
    server = Server.openServer(after.guild)

    # Update member in files
    Server.updateMember(after.guild, after)

    # Close server file
    Server.closeServer(server)
    """
    pass

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Message Events
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@omegaPsi.event
async def on_message_delete(message):
    pass

@omegaPsi.event
async def on_message_edit(before, after):
    pass

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Reaction Events
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@omegaPsi.event
async def on_reaction_add(reaction, member):
    
    # Open server file
    server = Server.openServer(member.guild)

    # Update member experience
    if str(member.id) in server["members"]:
        server["members"][str(member.id)]["experience"] += Server.REACTION_XP

    # Close server file
    Server.closeServer(server)

@omegaPsi.event
async def on_reaction_remove(reaction, member):
    pass

@omegaPsi.event
async def on_reaction_clear(message, reactions):
    pass

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Run Bot
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == "__main__":

    # Load command extensions
    for ext in extensions:

        try:
            omegaPsi.load_extension(ext)
        except:
            print("{} Cannot be loaded. [{}]".format(ext, traceback.format_exc()))
    
    # Keep bot running
    keepAlive()

    # Run bot
    omegaPsi.run(os.environ["DISCORD_BOT_TOKEN"])
