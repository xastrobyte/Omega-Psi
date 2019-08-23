from datetime import datetime

from random import choice, randint

def minutes_to_runtime(minutes):
    """Turns an amount of minutes into a runtime as if for a movie or TV show
    """

    # Turn the minutes into hours
    hours = minutes // 60

    # Return the result
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
    """Turns a datetime.datetime object into a JSON object
    that keeps track of the year, month, day, hour, minute, and second
    """

    return {
        "year": dateTime.year,
        "month": dateTime.month,
        "day": dateTime.day,
        "hour": dateTime.hour,
        "minute": dateTime.minute,
        "second": dateTime.second
    }

def dict_to_datetime(ddict):
    """Turns a JSON object that keeps track of a datetime's information
    back into a datetime.datetime object
    """
    
    return datetime(
        ddict["year"], ddict["month"], ddict["day"],
        ddict["hour"], ddict["minute"], ddict["second"]
    )

def datetime_to_string(dateTime, *, short = False):
    """Turns a datetime into a readable string.

    Parameters:
        dateTime (datetime.datetime): The datetime object to convert.
    """

    if short:
        return "{}/{}/{}".format(
            dateTime.month,
            dateTime.day,
            dateTime.year
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
        if minute < 10:
            minute = "0" + str(minute)

        return "{}, {} {}, {} {}:{} {}".format(
            weekdays[weekday], months[month], day, year, hour, minute, "AM" if am else "PM"
        )

def datetime_to_length(dateTime):
    """Takes in a datetime.datetime object, compares it with the current time, and returns the difference
    in ascending order starting with seconds, then minutes, then hours, and then days
    """

    # Get the difference of the current time and the datetime
    diff = datetime.now() - dateTime

    # Check if there is at least 1 day difference
    if diff.days >= 1:
        return str(diff.days) + " days"
    
    # Check if there is at least 1 hour difference
    elif diff.seconds // 3600 >= 1:
        return str(diff.seconds // 3600) + " hour{}".format("" if diff.seconds // 3600 == 1 else "s")
    
    # Check if there is at least 1 minute difference
    elif diff.seconds // 60 >= 1:
        return str(diff.seconds // 60) + " minute{}".format("" if diff.seconds // 60 == 1 else "s")
    
    # There is just seconds
    return str(diff.seconds) + " second{}".format("" if diff.seconds == 1 else "s")

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

def get_user_info_html():
    """Returns the HTML text used to render user information using the Jinja syntax
    """

    return (
        """

                        <!--Game Stats Section-->
                        <h2 class="page-section">
                            <code class="field">page</code><code>.</code><code class="field">gameStats</code><code>();</code>
                        </h2>
                        <div class="page-section-block">
                            <table class="command-table" style="width: 100%;">
                                <tr style="width: 100%;">
                                    <td style="width: 40%; text-align: center;"><strong>game</strong></td>
                                    <td style="width: 20%; text-align: center;"><strong>wins</strong></td>
                                    <td style="width: 20%; text-align: center;"><strong>losses</strong></td>
                                    <td style="width: 20%; text-align: center;"><strong>ratio</strong></td>
                                </tr>
                                <tr style="width: 100%;">
                                    <td style="width: 40%; text-align: center;">hangman</td>
                                    <td style="width: 20%; text-align: center;">{{ hangman["won"] }}</td>
                                    <td style="width: 20%; text-align: center;">{{ hangman["lost"] }}</td>
                                    <td style="width: 20%; text-align: center;">{{ hangman["ratio"] }}</td>
                                </tr>
                                <tr style="width: 100%;">
                                    <td style="width: 40%; text-align: center;">scramble</td>
                                    <td style="width: 20%; text-align: center;">{{ scramble["won"] }}</td>
                                    <td style="width: 20%; text-align: center;">{{ scramble["lost"] }}</td>
                                    <td style="width: 20%; text-align: center;">{{ scramble["ratio"] }}</td>
                                </tr>
                                <tr style="width: 100%;">
                                    <td style="width: 40%; text-align: center;">rock paper scissors</td>
                                    <td style="width: 20%; text-align: center;">{{ rps["won"] }}</td>
                                    <td style="width: 20%; text-align: center;">{{ rps["lost"] }}</td>
                                    <td style="width: 20%; text-align: center;">{{ rps["ratio"] }}</td>
                                </tr>
                                <tr style="width: 100%;">
                                    <td style="width: 40%; text-align: center;">tic tac toe</td>
                                    <td style="width: 20%; text-align: center;">{{ tic_tac_toe["won"] }}</td>
                                    <td style="width: 20%; text-align: center;">{{ tic_tac_toe["lost"] }}</td>
                                    <td style="width: 20%; text-align: center;">{{ tic_tac_toe["ratio"] }}</td>
                                </tr>
                                <tr style="width: 100%;">
                                    <td style="width: 40%; text-align: center;">connect four</td>
                                    <td style="width: 20%; text-align: center;">{{ connect_four["won"] }}</td>
                                    <td style="width: 20%; text-align: center;">{{ connect_four["lost"] }}</td>
                                    <td style="width: 20%; text-align: center;">{{ connect_four["ratio"] }}</td>
                                </tr>
                                <tr style="width: 100%;">
                                    <td style="width: 40%; text-align: center;">cards against humanity</td>
                                    <td style="width: 20%; text-align: center;">{{ cards_against_humanity["won"] }}</td>
                                    <td style="width: 20%; text-align: center;">{{ cards_against_humanity["lost"] }}</td>
                                    <td style="width: 20%; text-align: center;">{{ cards_against_humanity["ratio"] }}</td>
                                </tr>
                                <tr style="width: 100%;">
                                    <td style="width: 40%; text-align: center;">uno</td>
                                    <td style="width: 20%; text-align: center;">{{ uno["won"] }}</td>
                                    <td style="width: 20%; text-align: center;">{{ uno["lost"] }}</td>
                                    <td style="width: 20%; text-align: center;">{{ uno["ratio"] }}</td>
                                </tr>
                                <tr style="width: 100%;">
                                    <td style="width: 40%; text-align: center;">game of life</td>
                                    <td style="width: 20%; text-align: center;">{{ game_of_life["won"] }}</td>
                                    <td style="width: 20%; text-align: center;">{{ game_of_life["lost"] }}</td>
                                    <td style="width: 20%; text-align: center;">{{ game_of_life["ratio"] }}</td>
                                </tr>
                                <tr style="width: 100%;">
                                    <td style="width: 40%; text-align: center;">trivia</td>
                                    <td style="width: 20%; text-align: center;">{{ trivia["won"] }}</td>
                                    <td style="width: 20%; text-align: center;">{{ trivia["lost"] }}</td>
                                    <td style="width: 20%; text-align: center;">{{ trivia["ratio"] }}</td>
                                </tr>
                            </table>
                        </div>
        """
    )