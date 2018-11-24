from util.file.omegaPsi import OmegaPsi
from util.file.server import Server
from util.weather.weather import getCity, getCountry, getSky, getCurrentTemp, getHighTemp, getLowTemp, getLongitude, getLatitude, getWindSpeed, getWindDirection, getLastUpdated, getWeatherIcon
from util.utils import sendMessage, getErrorMessage, splitText

from bs4 import BeautifulSoup
from datetime import datetime
from supercog import Category, Command
import discord, json, os, requests, wikipediaapi

class Internet(Category):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    EMBED_COLOR = 0x0044FF

    WEATHER_API_CALL = "https://api.openweathermap.org/data/2.5/weather?APPID={}&q={}"
    URBAN_API_CALL = "https://api.urbandictionary.com/v0/define?term={}"

    URBAN_ICON = "https://vignette.wikia.nocookie.net/creation/images/b/b7/Urban_dictionary_--_logo.jpg/revision/latest?cb=20161002212954"
    WIKIPEDIA_PAGE_IMAGE = "https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles={}"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Errors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    NO_TERM = "NO_TERM"
    NO_PAGE = "NO_PAGE"

    INVALID_LOCATION = "INVALID_LOCATION"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Constructors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, client):
        super().__init__(
            client, 
            "Internet",
            description = "All commands that deal with the internet are here.",
            nsfw_channel_error = Server.getNSFWChannelError,
            locally_inactive_error = Server.getInactiveError,
            globally_inactive_error = OmegaPsi.getInactiveError,
            locally_active_check = Server.isCommandActive,
            globally_active_check = OmegaPsi.isCommandActive
        )

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Commands

        self._urban = Command(commandDict = {
            "alternatives": ["urban", "urbanDictionary", "urbanDict"],
            "info": "Gives you the top 5 urban dictionary entries for a term.",
            "nsfw": True,
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
                Internet.NO_TERM: {
                    "messages": [
                        "The term you entered does not exist on urban dictionary."
                    ]
                }
            },
            "command": self.urban
        })

        self._wikipedia = Command(commandDict = {
            "alternatives": ["wikipedia", "wiki"],
            "info": "Gets a wikipedia entry you type in.",
            "parameters": {
                "term": {
                    "info": "The search term, or phrase, you want to look up.",
                    "optional": False
                }
            },
            "errors": {
                Internet.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to search something up on wikipedia, you need to type it in."
                    ]
                },
                Internet.NO_PAGE: {
                    "messages": [
                        "There was no wikipedia entry found for that term."
                    ]
                }
            },
            "command": self.wikipedia
        })

        self._weather = Command(commandDict = {
            "alternatives": ["weather", "forecast", "getWeather"],
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
                Internet.INVALID_LOCATION: {
                    "messages": [
                        "The location you entered is not valid."
                    ]
                }
            },
            "command": self.weather
        })

        self.setCommands([
            self._urban,
            self._wikipedia,
            self._weather
        ])
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def urban(self, parameters):
        """Returns the top 5 urban dictionary entries for the specified term.\n

         - term - The term to search on urban dictionary.\n
         - discordChannel - The Discord Channel the definition is being sent in.\n
        """

        # Check for not enough parameters
        if len(parameters) < self._urban.getMinParameters():
            return getErrorMessage(self._urban, Internet.NOT_ENOUGH_PARAMETERS)
        
        term = " ".join(parameters)

        # Use requests to get the data in JSON
        try:
            urlCall = Internet.URBAN_API_CALL.format(term.replace(" ", "+"))
            urbanData = requests.get(urlCall).json()

        except:
            return getErrorMessage(self._urban, Internet.NO_TERM)
        
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
    
    def wikipedia(self, parameters):
        """Returns a wikipedia entry for the specified term.

        Parameters:
            term (str): The term to look up on wikipedia.
        """

        # Check for not enough parameters
        if len(parameters) < self._wikipedia.getMinParameters():
            return getErrorMessage(self._wikipedia, Internet.NOT_ENOUGH_PARAMETERS)
        
        term = " ".join(parameters)

        # Create Wikipedia API object
        wikiHTML = wikipediaapi.Wikipedia(
            language = "en",
            extract_format = wikipediaapi.ExtractFormat.HTML
        )

        # Find Wiki entry
        termHTML = wikiHTML.page(term)
        termTitle = termHTML.title

        # Check if wiki entry does not exist
        if not termHTML.exists():
            return getErrorMessage(self._wikipedia, Internet.NO_PAGE)
        
        # Wiki entry does exist
        termBS = BeautifulSoup(termHTML.summary, "html.parser")
        paragraphsHTML = termBS.findAll("p")

        # Get terms first paragraph
        paragraph = "No Summary"
        for p in paragraphsHTML:
            if p.attrs == {} and len(p.text.replace("\n", "")) > 0:
                paragraph = " ".join(text.strip() for text in p.find_all(text = True))
                break
            
        # Get page image
        pageImage = requests.get(Internet.WIKIPEDIA_PAGE_IMAGE.format(termHTML.fullurl.split("/")[-1])).json()
        try:
            termImage = pageImage["query"]["pages"][str(termHTML.pageid)]["original"]["source"]
        except:
            termImage = None

        embed = discord.Embed(
            name = termTitle,
            description = "**[{}]({})**\n{}".format(
                termTitle.title(),
                termHTML.fullurl,
                paragraph
            ),
            colour = Internet.EMBED_COLOR,
            timestamp = datetime.now()
        ).set_footer(
            text = "Wikipedia-API"
        )

        if termImage != None:
            embed.set_image(url = termImage)
            
        return embed

    def weather(self, parameters):
        """Returns the current weather for the specified location.\n

        location - The location to get the weather of.\n
        """

        # Check for not enough parameters
        if len(parameters) < self._weather.getMinParameters():
            return getErrorMessage(self._weather, Internet.NOT_ENOUGH_PARAMETERS)
        
        location = " ".join(parameters)
        
        # Get the url to call the API
        urlCall = Internet.WEATHER_API_CALL.format(
            os.environ["WEATHER_API_KEY"],
            location.replace(" ", "+")
        )

        # Use requests to get the data in JSON
        try:
            weatherData = requests.get(urlCall).json()
        except:
            return getErrorMessage(self._weather, Internet.INVALID_LOCATION)
        
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

            # Iterate through commands
            for cmd in self.getCommands():
                if command in cmd.getAlternatives():
                    await sendMessage(
                        self.client,
                        message,
                        embed = await self.run(message, cmd, cmd.getCommand(), parameters)
                    )

def setup(client):
    client.add_cog(Internet(client))
