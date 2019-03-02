from datetime import datetime

from random import choice, randint

def minutes_to_runtime(minutes):
    hours = minutes // 60
    return "{}h {}m".format(hours, minutes - (hours * 60))

def timestamp_to_datetime(timestamp):
    """Turns a string timestamp into a datetime.

    Parameters:
        timestamp (str): The string version of the timestamp.
    """

    # Get the date and time
    date = timestamp.split("T")[0].split("-")
    time = timestamp.split("T")[1].replace("Z", "").split(":")

    # Turn it into a datetime
    dateTime = datetime(
        int(date[0]), int(date[1]), int(date[2]),
        int(time[0]), int(time[1]), int(time[2])
    )

    return dateTime

def datetime_to_dict(dateTime):

    return {
        "year": dateTime.year,
        "month": dateTime.month,
        "day": dateTime.day,
        "hour": dateTime.hour,
        "minute": dateTime.minute,
        "second": dateTime.second
    }

def dict_to_datetime(ddict):
    
    return datetime(
        ddict["year"], ddict["month"], ddict["day"],
        ddict["hour"], ddict["minute"], ddict["second"]
    )

def datetime_to_string(dateTime):
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

def split_text(text, size, byWord = True):
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

def generate_random_string():
    """Generates a random string with a random length."""

    characters = (
        [chr(i) for i in range(ord("A"), ord("Z") + 1)] +
        [chr(i) for i in range(ord("a"), ord("z") + 1)] +
        [chr(i) for i in range(ord("0"), ord("9") + 1)]
    )

    # Choose random length
    length = randint(10, 100)
    return "".join([choice(characters) for i in range(length)])