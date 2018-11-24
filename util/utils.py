from util.file.server import Server

from datetime import datetime
from functools import wraps
from PIL import Image

import discord, json, os, pygame, requests, signal, traceback

pygame.init()

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

def timestampToDatetime(timestamp):
    """Turns a string timestamp into a datetime.

    Parameters:
        timestamp (str): The string version of the timestamp.
    """

    # Get the date and time
    date = timestamp.split("T")[0].split("-")
    time = timestamp.split("T")[1].split(":")

    # Turn it into a datetime
    dateTime = datetime(
        int(date[0]), int(date[1]), int(date[2]),
        int(time[0]), int(time[1]), int(time[2])
    )

    return dateTime

def getSmallestRect(number):
    """Gets the shortest and thinnest rectangle given a number.

    Parameters:
        number (int): The number to process.
    """

    # Get all factors of number
    factors = []
    for i in range(number, -1, -1):
        for j in range(number):
            if i * j == number:
                factors.append([i, j])
    
    # Find smallest difference
    diff = number
    value = [factors[0]]
    for factor in factors:
        if abs(factor[0] - factor[1]) <= diff:
            diff = abs(factor[0] - factor[1])
            value = factor
    
    if value[0] < value[1]:
        return value[::-1]

    return value

def loadImageFromUrl(url):
    """Loads and returns an image from a URL

    Parameters:
        url (str): The URL to load the image from.

    Returns:
        image (pygame.image): The image.
    """

    # Make Request; Get Image through Pillow
    response = requests.get(url, stream = True)
    response.raw.decode_content = True

    pillowImage = Image.open(response.raw)

    # Turn the Pillow Image into a Pygame Image
    pillowImageMode = pillowImage.mode
    pillowImageSize = pillowImage.size
    pillowImageData = pillowImage.tobytes()

    pygameImage = pygame.image.fromstring(pillowImageData, pillowImageSize, pillowImageMode)

    return pygameImage

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

def discordIdToString(jsonObject):
    """Turns every Discord ID given by the value \"id\" in
    a JSON object into a String to save to MongoDB.

    Parameters:
        jsonObject (dict): The dictionary to iterate through.
    """

    # Iterate through keys in dictionary
    for key in jsonObject:
        value = jsonObject[key]

        # Value is another dictionary, make a recursive call
        if type(value) == dict:
            discordIdToString(value)
        
        # Value is a number, turn into String if necessary
        elif type(value) == int and key == "id":
            if value > 1 * 10 ** 17:
                jsonObject[key] = str(value)

def migrateToDB(directory, database):
    """Migrates all the Server and User Files straight to the MongoDB.

    Parameters:
        directory (str): The directory to migrate to MongoDB.
        database (pymongo.Collection): The database collection to add it to.
    """

    # Iterate through files in directory
    for filename in os.listdir(directory):

        # Load JSON represenation of the file.
        fileJson = json.load(open(directory + "/" + filename, "r"))

        # Turn every ID to a String
        discordIdToString(fileJson)

        # Get the ID to add
        _id = fileJson.pop("id")

        # Add the file (if needed); Update the file
        if database.find_one({"_id": _id}) == None:
            database.insert_one({"_id": _id})
        database.update_one({"_id": _id}, {"$set": fileJson}, upsert = False)

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
            except Exception as e:
                result = discord.Embed(
                    title = "Error",
                    description = e.args[0],
                    colour = 0xFF0000
                )
            finally:
                signal.alarm(0)
            return result
        
        return wraps(func)(wrapper)
    
    return decorator
