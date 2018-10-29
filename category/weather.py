from category.category import Category

from util.command.command import Command
from util.file.server import Server
from util.weather.weather import getCity, getCountry, getSky, getCurrentTemp, getHighTemp, getLowTemp, getLongitude, getLatitude, getWindSpeed, getWindDirection, getLastUpdated, getWeatherIcon
from util.utils import sendMessage

from datetime import datetime
import discord, json, os, urllib.request

class Weather(Category):

    DESCRIPTION = "Do you wanna know weather stuff? Here you go!"

    EMBED_COLOR = 0x0044FF

    API_CALL = "https://api.openweathermap.org/data/2.5/weather?APPID={}&q={}"

    def __init__(self, client):
        super().__init__(client, "Weather")

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Commands

        self._weather = Command({
            "alternatives": ["forecast", "getWeather"],
            "info": "Gets the weather for a specified location.",
            "parameters": {
                "location": {
                    "info": "The location to search for.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to get the weather for a place, you need the location."
                    ]
                },
                Category.INVALID_LOCATION: {
                    "messages": [
                        "The location you entered is not valid."
                    ]
                }
            }
        })

        self.setCommands([
            self._weather
        ])
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def getWeather(self, location):
        """Returns the current weather for the specified location.\n

        location - The location to get the weather of.\n
        """
        
        # Get the url to call the API
        urlCall = Weather.API_CALL.format(
            os.environ["WEATHER_API_KEY"],
            location.replace(" ", "+")
        )

        # Use urllib to get the data in JSON
        try:
            with urllib.request.urlopen(urlCall) as url:
                weatherData = json.load(url)
        except:
            return self.getErrorMessage(self._weather, Category.INVALID_LOCATION)
        
        # Get necessary values
        # Values we want to use include:
        # - City Name and Country
        city = getCity(weatherData)
        country = getCountry(weatherData)
        # - Current, High, and Low Temps (in F)
        currentTemp = getCurrentTemp(weatherData, country != "United States")
        highTemp = getHighTemp(weatherData, country != "United States")
        lowTemp = getLowTemp(weatherData, country != "United States")
        # - Sky conditions
        skyCondition = getSky(weatherData)
        # - Longitude and Latitude
        longitude = getLongitude(weatherData)
        latitude = getLatitude(weatherData)
        # - Wind Speed and Direction
        windSpeed = getWindSpeed(weatherData, country != "United States")
        windDirection = getWindDirection(weatherData, False)
        # - Last Updated and Weather Icon
        lastUpdated = getLastUpdated(weatherData)
        weatherIcon = getWeatherIcon(weatherData)

        # Setup Field Order
        fields = {
            "Temperature ({})".format("°C" if country != "United States" else "°F"): "{}\n({} / {}) H/L".format(currentTemp, highTemp, lowTemp),
            "Sky Conditions": skyCondition,
            "Wind ({})".format("mps" if country != "United States" else "mph"): "{} {}".format(windSpeed, windDirection),
            "Coordinates": "{}, {}".format(longitude, latitude)
        }

        # Setup embed
        embed = discord.Embed(
            title = "Weather",
            description = "{}, {}".format(city, country),
            colour = Weather.EMBED_COLOR,
            timestamp = datetime.fromtimestamp(lastUpdated)
        )
        embed.set_thumbnail(
            url = weatherIcon
        )

        # Add fields
        for field in fields:
            embed.add_field(
                name = field,
                value = fields[field],
                inline = True
            )
        
        return embed

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Parsing
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def on_message(self, message):
        """Parses a message and runs a Weather Category command if it can.\n

        message - The Discord Message to parse.\n
        """

        # Make sure message starts with the prefix
        if Server.startsWithPrefix(message.guild, message.content) and not message.author.bot:

            # Split up into command and parameters if possible
            command, parameters = Category.parseText(Server.getPrefixes(message.guild), message.content)
            
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            # Weather Command
            if command in self._weather.getAlternatives():

                # 0 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = self.getErrorMessage(self._weather, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 1 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await self.run(message, self._weather, self.getWeather, " ".join(parameters))
                    )

def setup(client):
    client.add_cog(Weather(client))
