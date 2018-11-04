from util.file.server import Server

import discord, os, traceback

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
