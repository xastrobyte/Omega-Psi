from util.file.omegaPsi import OmegaPsi
from util.file.server import Server

from functools import wraps
import discord, inspect, os, signal, traceback

async def sendMessage(client, origMessage, *, message = None, embed = None, filename = None, plain = False):
    """A utility method to send a message to a channel that automatically handles exceptions.\n

    origMessage - The original Discord Message (automatically handles whether to send to use or channel)\n

    Keyword Arguments:\n
     - message - A regular message to send.\n
     - embed - An Embed to send in a Discord Message.\n
     - filename - A file to send given a filename.\n
    """

    if type(origMessage) == discord.TextChannel:
        channel = origMessage
    else:
        channel = origMessage.channel

    # Try sending a message
    try:

        # Message is a regular message
        if message != None:
            await channel.send(message)
        
        # Message is an Embed
        elif embed != None:
            await channel.send(embed = embed)
        
        # Message is a filename
        elif filename != None:
            await channel.send(file = discord.File(filename))
    
    except:
        error = traceback.format_exc()
        await sendErrorMessage(client, error)

async def sendErrorMessage(client, message):
    """A utility method to send an error message to the test server.\n

    message - The message to send.\n
    """

    await getChannel(client,
        os.environ["DISCORD_TEST_SERVER_ID"],
        os.environ["DISCORD_TEST_CHANNEL_ID"]
    ).send("```python\n" + message + "```")

def getChannel(client, serverId, channelId):
    """A utility method that retrieves a Discord Channel given the serverId and channelId.\n

    client - The Discord Client to find the server from.\n
    serverId - The ID of the Discord Server to look in.\n
    channelId - The ID of the Discord Channel to get.\n
    """

    # Iterate through servers the bot is in
    for server in client.guilds:
        if server.id == int(serverId):

            # Iterate through channels the bot has access to
            for channel in server.channels:
                if channel.id == int(channelId):
                    return channel

def censor(text, inCodeBlock = False):
    """Returns a censored version of the string given

    text - The string to censor
    """

    profaneWords = [profane for profane in Server.PROFANE_WORDS if profane in text]

    # Replace text (keep first and last letters of word; replace middle with *)
    for profanity in profaneWords:
        censored = (
            "{}{}{}".format(
                profanity[0],                   # Add first letter of profane word
                "{}".format(                        # Make each letter in between first and last an asterik
                    "*" if inCodeBlock else "\*"        # If the censored word is in a code block, keep it normal
                ) * (len(profanity) - 2),               # If not, add a backslash to prevent text formatting
                profanity[len(profanity) - 1]   # Add last letter of profane word
            )
        )
        text = text.replace(profanity, censored)
    
    return text

def splitText(text, size, byWord = True):
    """Splits text up by size.\n

     - text - The text to split.\n
     - size - The maximum size of each string.\n
     - byWord - Whether or not to split up the text by word or by letter.\n
    """

    # Split up by word
    if byWord:
        text = text.split(" ")

    # Keep track of fields and fieldText
    fields = []
    fieldText = ""
    for value in text:

        value += " " if byWord else ""
        
        if len(fieldText) + len(value) >= size:
            fields.append(fieldText)
            fieldText = ""
        
        fieldText += value
    
    if len(fieldText) > 0:
        fields.append(fieldText)
    
    return fields

def getErrorMessage(commandObject, errorType):
    """Returns a Discord Embed object for an error type given.

    Parameters:
        commandObject: The Command to get the error from.
        errorType: The type of error to return.
    
    Returns:
        embed (discord.Embed)
    """
        
    return discord.Embed(
        title = "Error",
        description = commandObject.getErrorMessage(errorType),
        colour = 0xFF0000
    )

async def run(discordMessage, commandObject, func, *args, **kwargs):
    """Runs a command while testing if the Command is globally or locally inactive.

    Parameters:
        discordMessage: The Discord Message that determines who ran the command and where it is being sent to.
        commandObject: The Command that is being run.
        func: The function that runs the actual code behind a Command.
        *args: The arguments to put into the function.
        **kwargs: The keyword arguments to put into the function.
    
    Returns:
        embed (discord.Embed)
    """

    # Emulate Typing
    async with discordMessage.channel.typing():

        # Command is globally active
        if OmegaPsi.isCommandActive(commandObject):

            # Command is a Bot Moderator Command
            if commandObject.isBotModeratorCommand():

                # Author is a Bot Moderator
                if OmegaPsi.isAuthorModerator(discordMessage.author):
                    
                    # Try running asynchronous function
                    if inspect.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    
                    # Function is synchronous
                    else:
                        return func(*args, **kwargs) # All functions must return an embed
                
                # Author is not a Bot Moderator
                else:
                    return OmegaPsi.getErrorMessage(OmegaPsi.NO_ACCESS)

            # Command is being run in a Server
            elif discordMessage.guild != None:
                
                # Command is locally active
                if Server.isCommandActive(discordMessage.guild, commandObject):

                    # Command is a Server Moderator Command
                    if commandObject.isServerModeratorCommand():

                        # Author is a Server Moderator
                        if Server.isAuthorModerator(discordMessage.guild, discordMessage.author):

                            # Try running asynchronous function
                            if inspect.iscoroutinefunction(func):
                                return await func(*args, **kwargs)
                            
                            # Function is synchronous
                            else:
                                return func(*args, **kwargs) # All functions must return an embed
                        
                        # Author is not a Server Moderator
                        else:
                            return Server.getErrorMessage(Server.NO_ACCESS)
                    
                    # Command is not a Server Moderator Command
                    else:

                        # Try running asynchronous function
                        if inspect.iscoroutinefunction(func):
                            return await func(*args, **kwargs)
                        
                        # Function is synchronous
                        else:
                            return func(*args, **kwargs) # All functions must return an embed
                
                # Command is locally inactive
                else:
                    return Server.getErrorMessage(Server.INACTIVE) # Returns Embed
            
            # Command is being run in a Private Message
            else:
                
                # Command can be run in Private
                if commandObject.canBeRunInPrivate():

                    # Try running asynchronous function
                    if inspect.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    
                    # Function is synchronous
                    else:
                        return func(*args, **kwargs) # All functions must return an embed
                
                # Command cannot be run in Private
                else:
                    # return Category.getErrorMessage(commandObject, Category.CANT_BE_RUN)
                    pass
        
        # Command is globally inactive
        else:
            return OmegaPsi.getErrorMessage(OmegaPsi.INACTIVE) # Returns Embed

# Timeout Decorator
class TimeoutError(Exception): pass
def timeout(seconds = 10, error_message = "Function timed out"):
    def decorator(func):
        def _handle_timeout(signum, frame):
            return discord.Embed(
                title = "Error",
                description = error_message,
                colour = 0xFF0000
            )
        
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            except:
                result = discord.Embed(
                    title = "Error",
                    description = error_message,
                    colour = 0xFF0000
                )
            finally:
                signal.alarm(0)
            return result
        
        return wraps(func)(wrapper)
    
    return decorator
