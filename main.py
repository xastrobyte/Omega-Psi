from util.file.omegaPsi import OmegaPsi
from util.file.server import Server

from keepAlive import keepAlive
from util.utils.discordUtils import sendMessage, sendErrorMessage

from discord.ext.commands import Bot
from random import randint

import discord, os, sys, traceback

# Open Bot client
omegaPsi = Bot(command_prefix = OmegaPsi.PREFIX)
omegaPsi.remove_command("help")

extensions = [
    "category.help",
    "category.code",
    "category.game",
    "category.image",
    "category.insult",
    "category.internet",
    "category.math",
    "category.meme",
    "category.misc",
    "category.nsfw",
    "category.rank",
    "category.serverModerator",
    "category.botModerator"
]

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Basic Events
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@omegaPsi.event
async def on_ready():
    activityType = OmegaPsi.getActivityType()
    text = OmegaPsi.getActivityName()

    await omegaPsi.change_presence(
        status = discord.Status.online,
        activity = discord.Activity(
            name = text,
            type = activityType,
            url = "https://www.twitch.tv/FellowHashbrown"
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
                Server.getJoinMessageChannel(member.guild)
            ),
            message = Server.getJoinMessage(member.guild).format(member.mention)
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

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Run Bot
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == "__main__":

    # Choose random process ID between (1000 and 9999)
    OmegaPsi.PROCESS_ID = randint(1000, 9999)

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