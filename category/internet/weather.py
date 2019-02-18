import discord
from datetime import datetime

from category.globals import PRIMARY_EMBED_COLOR

def weather(weather_json):

    # Get location information
    location = "{}, {}, {}".format(
        weather_json["location"]["name"],
        weather_json["location"]["region"],
        weather_json["location"]["country"]
    )
    
    # Get the temperature
    temperature = "{}°F ({}°C)".format(
        weather_json["current"]["temp_f"],
        weather_json["current"]["temp_c"]
    )

    # Get the feels like
    feels_like = "{}°F ({}°C)".format(
        weather_json["current"]["feelslike_f"],
        weather_json["current"]["feelslike_c"]
    )

    # Get the UV index
    uv = weather_json["current"]["uv"]

    # Get the condition text and icon
    condition_text = weather_json["current"]["condition"]["text"]
    condition_icon = weather_json["current"]["condition"]["icon"]

    # Get the wind speed and degree
    wind_speed = "{} mph ({} kph)".format(
        weather_json["current"]["wind_mph"],
        weather_json["current"]["wind_kph"]
    )
    wind_dir = weather_json["current"]["wind_dir"]

    # Get humidity
    humidity = weather_json["current"]["humidity"]

    # Get last updated
    last_updated = weather_json["current"]["last_updated_epoch"]

    # Create and return the embed
    embed = discord.Embed(
        title = "Weather for {}".format(
            location
        ),
        description = "_ _",
        colour = PRIMARY_EMBED_COLOR,
        timestamp = datetime.fromtimestamp(last_updated)
    ).set_author(
        name = "Apixu",
        icon_url = "https://cdn.apixu.com/v4/images/logo.png",
        url = "https://www.apixu.com"
    ).set_footer(
        text = "Last Updated"
    ).set_thumbnail(
        url = "https:{}".format(condition_icon)
    )

    fields = {
        "Temperature": temperature,
        "Feels Like": feels_like,
        "UV Index": uv,
        "Condition": condition_text,
        "Wind": "{} at {}".format(wind_speed, wind_dir),
        "Humidity": humidity
    }

    for field in fields:
        embed.add_field(
            name = field,
            value = fields[field]
        )
    
    return embed

def forecast(weather_json):

    weekdays = [
        "Monday", "Tuesday", "Wednesday", 
        "Thursday", "Friday", "Saturday",
        "Sunday"
    ]

    months = [
        "January", "February", "March", "April",
        "May", "June", "July", "August",
        "September", "October",
        "November", "December"
    ]

    # Keep track of following 7 days in separate fields
    # Fields will be used for scrolling in actual command
    fore_cast = {
        "location": "{}, {}, {}".format(
            weather_json["location"]["name"],
            weather_json["location"]["region"],
            weather_json["location"]["country"]
        ),
        "forecasts": []
    }
    forecasts = weather_json["forecast"]["forecastday"]

    # Iterate through forecasts
    for forecast in forecasts:

        # Get date
        date = datetime.fromtimestamp(forecast["date_epoch"])
        date = "{}, {} {}, {}".format(
            weekdays[date.weekday()],
            months[date.month - 1],
            date.day,
            date.year
        )

        # Get High and Low temperatures
        high = "{}°F ({}°C)".format(
            forecast["day"]["maxtemp_f"],
            forecast["day"]["maxtemp_c"]
        )
        low = "{}°F ({}°C)".format(
            forecast["day"]["mintemp_f"],
            forecast["day"]["mintemp_c"]
        )

        # Get UV index
        uv = forecast["day"]["uv"]

        # Get max wind
        max_wind = "{} mph ({} kph)".format(
            forecast["day"]["maxwind_mph"],
            forecast["day"]["maxwind_kph"]
        )

        # Get precipitation
        precipitation = "{} in. ({} mm.)".format(
            forecast["day"]["totalprecip_in"],
            forecast["day"]["totalprecip_mm"]
        )

        # Get Condition
        condition_text = forecast["day"]["condition"]["text"]
        condition_icon = forecast["day"]["condition"]["icon"]

        # Get Sunrise and Sunset
        sunrise = forecast["astro"]["sunrise"]
        sunset = forecast["astro"]["sunset"]

        fore_cast["forecasts"].append({
            "date": date,
            "High and Low Temperatures": "High: {}\nLow: {}".format(
                high, low
            ),
            "UV Index": uv,
            "Max Wind": max_wind,
            "Precipitation": precipitation,
            "Condition": condition_text,
            "Sunrise": sunrise,
            "Sunset": sunset,
            "condition_icon": "https:{}".format(condition_icon)
        })
    
    return fore_cast