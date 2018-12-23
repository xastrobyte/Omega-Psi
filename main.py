from util.file.omegaPsi import OmegaPsi
from util.file.server import Server

from keepAlive import keepAlive
from util.utils.discordUtils import sendMessage, sendErrorMessage
from util.utils.stringUtils import PROFANE_WORDS

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
    "category.updates",
    "category.serverModerator",
    "category.botModerator"
]

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Basic Events
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@omegaPsi.event
async def on_ready():
    activityType = await OmegaPsi.getActivityType()
    text = await OmegaPsi.getActivityName()

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

            # Check if profanity_filter is not active in the server
            if not await Server.isProfanityFilterActive(message.guild):

                # Update experience; Get message
                message = await Server.updateExperience(message)

                # Rank up message existed
                if message != None:

                    await sendMessage(
                        omegaPsi, origMessage,
                        message = message, plain = True
                    )
            
            # profanity_filter is active. delete message, tell user not to use profanity
            else:

                # Check if message has profanity
                profanity = [word for word in PROFANE_WORDS if word in message.content]
                if len(profanity) > 0:

                    # Try to delete their message
                    try:
                        await message.delete()
                    
                    # Couldn't delete message because of Forbidden
                    # Send message to server owner, if dm_on_fail is True, saying that profanity filter is active
                    #    but Omega Psi doesn't have permission to delete the message
                    except discord.Forbidden:

                        # Make sure owner is not None (That has happened before)
                        if message.guild.owner != None and await Server.dmOwnerOnProfanityFail(message.guild):
                            await message.guild.owner.send(
                                embed = discord.Embed(
                                    title = "Missing Permissions",
                                    description = "You have the Profanity Filter activated but I can't delete messages that contain profanity.",
                                    colour = 0xFF0000
                                ).set_author(
                                    name = "In Server: {}".format(
                                        message.guild.name
                                    )
                                )
                            )
                    
                    await origMessage.channel.send(
                        "{} you're not supposed to use profanity...".format(
                            message.author.mention
                        ),
                        delete_after = 5
                    )

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Member Events
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@omegaPsi.event
async def on_member_join(member):

    # Update member
    await Server.updateMember(member.guild, member)

    # Open server file
    server = await Server.openServer(member.guild)

    # Send message in welcome message channel
    if server["welcome_message"]["active"]:
        
        # Make sure the welcome message channel exists
        if server["welcome_message"]["channel"]:
            message = await Server.getWelcomeMessage(member.guild)

            await sendMessage(
                omegaPsi,
                member.guild.get_channel(
                    await Server.getWelcomeMessageChannel(member.guild)
                ),
                message = message.format(member.mention)
            )
        
        # Send message to owner if they can be grabbed
        #  and if they want to receive DM's on Fail
        else:
            owner = member.guild.owner

            if owner != None and await Server.dmOwnerOnWelcomeFail(member.guild):
                await owner.send(
                    embed = discord.Embed(
                        title = "Welcome Channel Not Set",
                        description = "You have the Welcome Message activated but you don't have a channel set. Set it with `omega setWelcomeMessageChannel`",
                        colour = 0xFF0000
                    ).set_author(
                        name = "In Server: {}".format(
                            member.guild.name
                        )
                    )
                )
    
    # Give person role if autorole is active
    if server["autorole"]["active"]:

        # Make sure the autorole role exists
        if server["autorole"]["role"]:
            role = member.guild.get_role(int(server["autorole"]["role"]))

            await member.add_roles(
                role,
                reason = "well because they joined. duh"
            )
        
        # Send message to owner if they can be grabbed
        #   and if they want to receive DM's on Fail
        else:
            owner = member.guild.owner

            if owner!= None and await Server.dmOwnerOnAutoroleFail(member.guild):
                await owner.send(
                    embed = discord.Embed(
                        title = "Autorole Not Set",
                        description = "You have the Autorole feature activated but you don't have a role set. Set it with `omega setAutorole`",
                        colour = 0xFF0000
                    ).set_author(
                        name = "In Server: {}".format(
                            member.guild.name
                        )
                    )
                )

    # Close server file
    await Server.closeServer(server)

@omegaPsi.event
async def on_member_remove(member):

    # Open servers file
    server = await Server.openServer(member.guild)

    # Remove member
    if str(member.id) in server["members"]:
        server["members"].pop(str(member.id))

    # Close servers file
    await Server.closeServer(server)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Reaction Events
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@omegaPsi.event
async def on_reaction_add(reaction, member):
    
    # Open server file
    server = await Server.openServer(member.guild)

    # Update member experience
    if str(member.id) in server["members"]:
        server["members"][str(member.id)]["experience"] += Server.REACTION_XP

    # Close server file
    await Server.closeServer(server)

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