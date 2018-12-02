from datetime import datetime
from functools import wraps
from PIL import Image

import discord, json, os, pygame, requests, signal

pygame.init()

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

def datetimeToString(dateTime):
    """Turns a datetime into a readable string.

    Parameters:
        dateTime (datetime.datetime): The datetime object to convert.
    """

    weekdays = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday",
        "Saturday", "Sunday"
    ]

    months = [
        "January", "February", "March", "April",
        "May", "June", "July", "August",
        "September", "October", "November", "December"
    ]

    # Get the weekday, month, day, year, time (AM or PM)
    weekday = dateTime.weekday()
    month = dateTime.month - 1
    day = dateTime.day
    year = dateTime.year
    hour = dateTime.hour
    am = True
    if hour == 0:
        hour = 12
        am = True
    elif hour > 12:
        hour -= 12
        am = False
    minute = dateTime.minute

    return "{}, {} {}, {} {}:{} {}".format(
        weekdays[weekday], months[month], day, year, hour, minute, "AM" if am else "PM"
    )

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

    # Iterate through the factors
    for factor in factors:

        # See if the difference between these factors is smaller than the current
        if abs(factor[0] - factor[1]) <= diff:
            diff = abs(factor[0] - factor[1])
            value = factor
    
    # Make the width bigger than the height if applicable
    if value[0] < value[1]:
        return value[::-1]

    return value

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