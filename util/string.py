from datetime import datetime
from dateutil.relativedelta import relativedelta

from random import choice, randint

def minutes_to_runtime(minutes):
    """Turns an amount of minutes into a runtime as if for a movie or TV show

    :param minutes: The amount of minutes to turn into a runtime
    """

    # Turn the minutes into hours
    hours = minutes // 60

    # Return the result
    return "{}h {}m".format(hours, minutes - (hours * 60))

def timestamp_to_datetime(timestamp):
    """Turns a string timestamp into a datetime.

    :param timestamp: The string version of the timestamp
    
    :rtype: datetime
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

def datetime_to_dict(date_time):
    """Turns a datetime.datetime object into a JSON object
    that keeps track of the year, month, day, hour, minute, and second

    :param date_time: A datetime object to convert into a JSON object
    
    :rtype: dict
    """

    return {
        "year": date_time.year,
        "month": date_time.month,
        "day": date_time.day,
        "hour": date_time.hour,
        "minute": date_time.minute,
        "second": date_time.second
    }

def dict_to_datetime(datetime_dict):
    """Turns a JSON object that keeps track of a datetime's information
    back into a datetime.datetime object

    :param datetime_dict: A JSON object to turn into a datetime object
    
    :rtype: datetime
    """
    
    return datetime(
        datetime_dict["year"], datetime_dict["month"], datetime_dict["day"],
        datetime_dict["hour"], datetime_dict["minute"], datetime_dict["second"]
    )

def datetime_to_string(date_time, *, short = False):
    """Turns a datetime into a readable string.

    :param date_time: The datetime object to convert
    :param short: Whether or not to get a shortened version of the datetime in the MM/DD/YYYY format. (Defaults to False)
    """

    if short:
        return "{}/{}/{}".format(
            date_time.month,
            date_time.day,
            date_time.year
        )
    
    else:

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
        weekday = date_time.weekday()
        month = date_time.month - 1
        day = date_time.day
        year = date_time.year
        hour = date_time.hour
        am = True
        if hour == 0:
            hour = 12
            am = True
        elif hour > 12:
            hour -= 12
            am = False
        minute = date_time.minute
        if minute < 10:
            minute = "0" + str(minute)

        return "{}, {} {}, {} {}:{} {}".format(
            weekdays[weekday], months[month], day, year, hour, minute, "AM" if am else "PM"
        )

def datetime_to_length(date_time):
    """Takes in a datetime.datetime object, compares it with the current time, and returns the difference
    in descending order starting with years, months, days, etc.

    :param date_time The datetime object to convert to a length
    
    :rtype: str
    """

    # Get the current datetime and get the difference
    now = datetime.now()
    diff = relativedelta(now, date_time)

    # Strip away any value that has a 0
    result = []
    if diff.years != 0:
        result.append("{} year{}".format(diff.years, "s" if diff.years != 1 else ""))
    if diff.months != 0:
        result.append("{} month{}".format(diff.months, "s" if diff.months != 1 else ""))
    if diff.days != 0:
        result.append("{} day{}".format(diff.days, "s" if diff.days != 1 else ""))
    if diff.hours != 0:
        result.append("{} hour{}".format(diff.hours, "s" if diff.hours != 1 else ""))
    if diff.minutes != 0:
        result.append("{} minute{}".format(diff.minutes, "s" if diff.minutes != 1 else ""))
    
    # Check if there is only 1 result
    if len(result) == 1:
        return result[0]
    
    # Check if there is more than 1 result, use the {value}, {value}, and {value} format
    return "{}{} and {}".format(
        ", ".join(result[:-1]), 
        "," if len(result) > 2 else "",
        result[-1]
    )

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