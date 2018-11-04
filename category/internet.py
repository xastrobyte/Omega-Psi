from category.category import Category

from util.command import Command
from util.file.omegaPsi import OmegaPsi
from util.file.server import Server
from util.weather.weather import getCity, getCountry, getSky, getCurrentTemp, getHighTemp, getLowTemp, getLongitude, getLatitude, getWindSpeed, getWindDirection, getLastUpdated, getWeatherIcon
from util.utils import sendMessage, splitText

from datetime import datetime
import discord, json, os, urllib.request

class Internet(Category):

    DESCRIPTION = "Do you wanna know weather stuff? Here you go!"

    EMBED_COLOR = 0x0044FF

    WEATHER_API_CALL = "https://api.openweathermap.org/data/2.5/weather?APPID={}&q={}"
    URBAN_API_CALL = "https://api.urbandictionary.com/v0/define?term={}"

    URBAN_ICON = "https://vignette.wikia.nocookie.net/creation/images/b/b7/Urban_dictionary_--_logo.jpg/revision/latest?cb=20161002212954"

    def __init__(self, client):
        super().__init__(client, "Weather")

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Commands

        self._urban = Command({
            "alternatives": ["urban", "urbanDictionary", "urbanDict"],
            "info": "Gives you the top 5 urban dictionary entries for a term.",
            "parameters": {
                "term": {
                    "info": "The term to look up in urban dictionary.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "You need the term to look something up in urban dictionary."
                    ]
                },
                Category.NO_TERM: {
                    "messages": [
                        "The term you entered does not exist on urban dictionary."
                    ]
                },
                Category.NOT_NSFW: {
                    "messages": [
                        "You can't run this in this channel. You must be in an NSFW channel."
                    ]
                }
            }
        })

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
            self._urban,
            self._weather
        ])
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def urban(self, term, discordChannel):
        """Returns the top 5 urban dictionary entries for the specified term.\n

         - term - The term to search on urban dictionary.\n
         - discordChannel - The Discord Channel the definition is being sent in.\n
        """

        # See if discordChannel has NSFW tag
        try:
            isNSFW = discordChannel.is_nsfw()
        
        # discordChannel is DM or Group; Make NSFW
        except:
            isNSFW = True

        # Only run function if isNSFW
        if isNSFW:

            # Use urllib to get the data in JSON
            try:
                urlCall = Internet.URBAN_API_CALL.format(term.replace(" ", "+"))
                with urllib.request.urlopen(urlCall) as url:
                    urbanData = json.load(url)
            except:
                return self.getErrorMessage(self._urban, Category.NO_TERM)
            
            # Get first 5 values (or values if there are less than 5)
            if len(urbanData["list"]) < 5:
                definitions = urbanData["list"]
            else:
                definitions = urbanData["list"][:5]
            
            # Create discord embed
            embed = discord.Embed(
                title = "{} Results Of `{}`".format("Top 5" if len(definitions) > 5 else "", term),
                description = " ",
                colour = Internet.EMBED_COLOR
            ).set_thumbnail(
                url = Internet.URBAN_ICON
            )

            # Add definitions
            defCount = 0
            for definition in definitions:
                defCount += 1

                # Get definition; Split up into multiple fields if necessary
                definitionFields = splitText(definition["definition"], OmegaPsi.MESSAGE_THRESHOLD)

                count = 0
                for field in definitionFields:
                    count += 1
                    embed.add_field(
                        name = "Definition {} {}".format(
                            defCount,
                            "({} / {})".format(
                                count, len(definitionFields)
                            ) if len(definitionFields) > 1 else ""
                        ),
                        value = field,
                        inline = False
                    )
            
            return embed
        
        # Channel is not NSFW
        return self.getErrorMessage(self._urban, Category.NOT_NSFW)

    def weather(self, location):
        """Returns the current weather for the specified location.\n

        location - The location to get the weather of.\n
        """
        
        # Get the url to call the API
        urlCall = Internet.WEATHER_API_CALL.format(
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
            "Coordinates": "{}, {}".format(
                longitude.replace("-", ""),  # Remove negative (-) from longitude and latitude if it exists
                latitude.replace("-", "")
            )
        }

        # Setup embed
        embed = discord.Embed(
            title = "Weather",
            description = "{}, {}".format(city, country),
            colour = Internet.EMBED_COLOR,
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

            # Urban Command
            if command in self._urban.getAlternatives():

                # 0 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = self.getErrorMessage(self._urban, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 1 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await self.run(message, self._urban, self.urban, " ".join(parameters), message.channel)
                    )

            # Weather Command
            elif command in self._weather.getAlternatives():

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
                        embed = await self.run(message, self._weather, self.weather, " ".join(parameters))
                    )

def setup(client):
    client.add_cog(Internet(client))
