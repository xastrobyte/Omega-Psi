from util.file.database import omegaPsi, loop
from util.file.omegaPsi import OmegaPsi
from util.file.server import Server
from util.weather.weather import getCity, getCountry, getSky, getCurrentTemp, getHighTemp, getLowTemp, getLongitude, getLatitude, getWindSpeed, getWindDirection, getLastUpdated, getWeatherIcon
from util.utils.discordUtils import sendMessage, getErrorMessage
from util.utils.stringUtils import splitText, minutesToRuntime

from bs4 import BeautifulSoup
from datetime import datetime
from imdb import IMDb
from supercog import Category, Command
import discord, os, requests, wikipediaapi

scrollEmbeds = {}

class Internet(Category):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    IMDB = IMDb()

    IMDB_LINK = "https://www.imdb.com/title/tt{}/?ref_=nv_sr_1"

    TRANSLATE_API_CALL = "https://translate.yandex.net/api/v1.5/tr.json/translate?key={}&text={}&lang={}-{}"
    URBAN_API_CALL = "https://api.urbandictionary.com/v0/define?term={}"
    WEATHER_API_CALL = "https://api.openweathermap.org/data/2.5/weather?APPID={}&q={}"
    TINYURL_API = "http://tinyurl.com/api-create.php?url={}"

    URBAN_ICON = "https://vignette.wikia.nocookie.net/creation/images/b/b7/Urban_dictionary_--_logo.jpg/revision/latest?cb=20161002212954"
    WIKIPEDIA_PAGE_IMAGE = "https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles={}"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Errors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    NO_TERM = "NO_TERM"
    NO_PAGE = "NO_PAGE"

    INVALID_TO_LANGUAGE = "INVALID_TO_LANGUAGE"
    INVALID_FROM_LANGUAGE = "INVALID_FROM_LANGUAGE"
    INVALID_LOCATION = "INVALID_LOCATION"
    INVALID_URL = "INVALID_URL"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Constructors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, client):
        super().__init__(
            client, 
            "Internet",
            description = "All commands that deal with the internet are here.",
            embed_color = 0x0044FF,
            nsfw_channel_error = Server.getNSFWChannelError,
            locally_inactive_error = Server.getInactiveError,
            globally_inactive_error = OmegaPsi.getInactiveError,
            locally_active_check = Server.isCommandActive,
            globally_active_check = OmegaPsi.isCommandActive
        )

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Commands

        self._movie = Command(commandDict = {
            "alternatives": ["movie", "mv"],
            "info": "Gives you information about a Movie on IMDb.",
            "parameters": {
                "query": {
                    "info": "The Movie to look up.",
                    "optional": False
                }
            },
            "errors": {
                Internet.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to look up a movie, you need the movie title."
                    ]
                },
                Internet.NO_TERM: {
                    "messages": [
                        "There was no movie found with that name."
                    ]
                }
            },
            "command": self.movie
        })

        self._tvShow = Command(commandDict = {
            "alternatives": ["tvShow", "tv", "show"],
            "info": "Gives you information about a TV Show on IMDb.",
            "parameters": {
                "query": {
                    "info": "The TV Show to look up.",
                    "optional": False
                }
            },
            "errors": {
                Internet.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to look up a tv show, you need the tv show title."
                    ]
                },
                Internet.NO_TERM: {
                    "messages": [
                        "There was no tv show found with that name."
                    ]
                }
            },
            "command": self.tvShow
        })

        self._translate = Command(commandDict = {
            "alternatives": ["translate"],
            "info": "Gives you the translation of given text to and from a language.",
            "parameters": {
                "to": {
                    "info": "The language to translate to.",
                    "optional": False
                },
                "from": {
                    "info": "The language to translate from. (Default is English)",
                    "optional": True
                },
                "text": {
                    "info": "The text to translate.",
                    "optional": False
                }
            },
            "errors": {
                Internet.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to translate text, you need at least the target language and the text."
                    ]
                },
                Internet.INVALID_TO_LANGUAGE: {
                    "messages": [
                        "The language you want to translate to is not valid."
                    ]
                },
                Internet.INVALID_FROM_LANGUAGE: {
                    "messages": [
                        "The language you want to translate from is not valid."
                    ]
                }
            },
            "command": self.translate
        })

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

        self._shortenUrl = Command(commandDict = {
            "alternatives": ["shortenUrl", "shorten", "shortUrl", "url"],
            "info": "Shortens a URL given.",
            "parameters": {
                "url": {
                    "info": "The URL to shorten.",
                    "optional": False
                }
            },
            "errors": {
                Internet.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to shorten a URL, you need the URL to shorten."
                    ]
                },
                Internet.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You don't need more than 1 URL to shorten."
                    ]
                },
                Internet.INVALID_URL: {
                    "messages": [
                        "The URL you gave was invalid. It must start with \"https:\/\/\""
                    ]
                }
            },
            "command": self.shortenUrl
        })

        self.setCommands([
            self._movie,
            self._tvShow,

            self._translate,
            self._urban,
            self._weather,
            self._wikipedia,

            self._shortenUrl
        ])
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def movie(self, message, parameters):
        """Returns information about a Movie on IMDb.

        Parameters:
            query (str): The Movie to look up.
        """

        # Check for not enough parameters
        if len(parameters) < self._movie.getMinParameters():
            embed = getErrorMessage(self._movie, Internet.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            query = " ".join(parameters)

            # Get Movie data
            results = await loop.run_in_executor(None,
                Internet.IMDB.search_movie,
                query
            )
            movies = []
            for movie in results:
                if movie.data["kind"] in ["movie"]:
                    movies.append(movie)

            # There were no movies found
            if len(movies) == 0:
                embed = getErrorMessage(self._movie, Internet.NO_TERM)
            
            # There were movies found
            else:

                movie = await loop.run_in_executor(None,
                    Internet.IMDB.get_movie,
                    movies[0].movieID
                )

                # Get following data only:
                #   - title
                #   - plot outline
                #   - directors
                #   - producers
                #   - year released
                #   - running time
                #   - cast (first 20)
                #   - poster (if possible)
                try: title = movie.get("title")
                except: title = "No Title"

                try: plotOutline = movie.get("plot outline")
                except: plotOutline = "No Plot Outline Yet."

                try: directors = [director.get("name") for director in movie.get("director")]
                except: directors = ["N/A"]

                try: producers = [dist.get("name") for dist in movie.get("production companies")]
                except: producers = ["N/A"]

                try: year = movie.get("year")
                except: year = "No Year"

                try: length = minutesToRuntime(int(movie.get("runtimes")[0]))
                except: length = "N/A"

                try: cast = [person.get("name") for person in movie.get("cast")[:20]]
                except: cast = ["N/A"]

                try: poster = movie.get("cover url")
                except: poster = None

                fields = {
                    "Director(s)": ", ".join(directors),
                    "Producers": ", ".join(producers),
                    "Year Released": year,
                    "Running Time": length,
                    "Cast (first 20)": ", ".join(cast)
                }

                # Add all data to the embed
                embed = discord.Embed(
                    title = title,
                    description = plotOutline,
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color,
                    timestamp = datetime.now(),
                    url = Internet.IMDB_LINK.format(movie.movieID)
                ).set_footer(
                    text = "IMDb"
                )

                for field in fields:
                    embed.add_field(
                        name = field,
                        value = fields[field],
                        inline = False
                    )

                if poster != None:
                    embed.set_image(
                        url = poster
                    )

        await sendMessage(
            self.client,
            message,
            embed = embed
        )

    async def tvShow(self, message, parameters):
        """Returns information about a TV Show on IMDb.

        Parameters:
            query (str): The TV Show to look up.
        """

        # Check for not enough parameters
        if len(parameters) < self._tvShow.getMinParameters():
            embed = getErrorMessage(self._tvShow, Internet.NOT_ENOUGH_PARAMETERS)

        # There were the proper amount of parameters
        else:

            query = " ".join(parameters)

            # Get TV Show data
            results = await loop.run_in_executor(None,
                Internet.IMDB.search_movie,
                query
            )
            shows = []
            for show in results:
                if show.data["kind"] in ["tv show", "tv series"]:
                    shows.append(show)

            # There were no shows found
            if len(shows) == 0:
                embed = getErrorMessage(self._tvShow, Internet.NO_TERM)

            # There were shows found
            else:

                show = await loop.run_in_executor(None,
                    Internet.IMDB.get_movie,
                    shows[0].movieID
                )

                # Get following data only:
                #   - title
                #   - plot outline
                #   - writer
                #   - distributors
                #   - year released
                #   - number of seasons
                #   - cast (first 20)
                #   - poster (if possible)
                try: title = show.get("title")
                except: title = "No Title"

                try: plotOutline = show.get("plot outline")
                except: plotOutline = "No Plot Outline Yet."

                try: writer = [person.get("name") for person in show.get("writer")]
                except: writer = ["N/A"]

                try: producers = [dist.get("name") for dist in show.get("production companies")]
                except: producers = ["N/A"]

                try: year = show.get("year")
                except: year = "No Year"

                try: seasons = show.get("seasons")
                except: seasons = "No Seasons"

                try: cast = [person.get("name") for person in show.get("cast")[:20]]
                except: cast = ["N/A"]

                try: poster = show.get("cover url")
                except: poster = None

                fields = {
                    "Writer(s)": ", ".join(writer),
                    "Producers": ", ".join(producers),
                    "Year Released": year,
                    "Seasons": seasons,
                    "Cast (first 20)": ", ".join(cast)
                }

                # Add all data to the embed
                embed = discord.Embed(
                    title = title,
                    description = plotOutline,
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color,
                    timestamp = datetime.now(),
                    url = Internet.IMDB_LINK.format(show.movieID)
                ).set_footer(
                    text = "IMDb"
                )

                for field in fields:
                    embed.add_field(
                        name = field,
                        value = fields[field],
                        inline = True
                    )

                if poster != None:
                    embed.set_image(
                        url = poster
                    )

        await sendMessage(
            self.client,
            message,
            embed = embed
        )
    
    async def translate(self, message, parameters):
        """Returns a translation of text.

        Parameters:
            to (str): The language to translate to.
            from (str): The language to translate from.
            text (str): The text to translate.
        """

        # Check for not enough parameters
        if len(parameters) < self._translate.getMinParameters():
            embed = getErrorMessage(self._translate, Internet.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            embed = None
        
            if len(parameters) == 2:
                toLang = parameters[0].lower()
                fromLang = "en".lower()
                text = " ".join(parameters[1:])
            else:
                toLang = parameters[0].lower()
                fromLang = parameters[1].lower()
                text = " ".join(parameters[2:])
            
            lang = omegaPsi.getLang()["lang"]
            code = omegaPsi.getLang()["code"]
            
            # Check if toLang is a language name
            if len(toLang) > 3:
                if toLang not in lang:
                    embed = getErrorMessage(self._translate, Internet.INVALID_TO_LANGUAGE)
                else:
                    toLang = lang[toLang]
            else:
                if toLang not in code:
                    embed = getErrorMessage(self._translate, Internet.INVALID_TO_LANGUAGE)
            
            # Check if fromLang is a language name
            if len(fromLang) > 3:
                if fromLang not in lang:
                    embed = getErrorMessage(self._translate, Internet.INVALID_FROM_LANGUAGE)
                else:
                    fromLang = lang[fromLang]
            else:
                if fromLang not in code:
                    embed = getErrorMessage(self._translate, Internet.INVALID_FROM_LANGUAGE)

            # Everything was valid, translate
            if embed == None:
                response = await loop.run_in_executor(None,
                    requests.get,
                    Internet.TRANSLATE_API_CALL.format(
                        os.environ["TRANSLATE_API_KEY"],
                        text, fromLang, toLang
                    )
                )
                response = response.json()

                # Translate was a success; Text tag should be in it
                if "text" in response:
                    text = " ".join(response["text"])

                elif "message" in response:
                    text = response["message"]
                
                embed = discord.Embed(
                    title = "Powered by Yandex.Translate",
                    description = text,
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color,
                    timestamp = datetime.now(),
                    url = "http://translate.yandex.com"
                )

        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )

    async def urban(self, message, parameters):
        """Returns the top 5 urban dictionary entries for the specified term.\n

         - term - The term to search on urban dictionary.\n
         - discordChannel - The Discord Channel the definition is being sent in.\n
        """

        # Check for not enough parameters
        if len(parameters) < self._urban.getMinParameters():
            embed = getErrorMessage(self._urban, Internet.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            term = " ".join(parameters)

            # Use requests to get the data in JSON
            try:
                urlCall = Internet.URBAN_API_CALL.format(term.replace(" ", "+"))
                urbanData = await loop.run_in_executor(None,
                    requests.get,
                    urlCall
                )
                urbanData = urbanData.json()

                # Get first 5 values (or values if there are less than 5)
                if len(urbanData["list"]) < 5:
                    definitions = urbanData["list"]
                else:
                    definitions = urbanData["list"][:5]
                
                # Create discord embed
                embed = discord.Embed(
                    title = "{} Results Of `{}`".format("Top 5" if len(definitions) > 5 else "", term),
                    description = " ",
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
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

            except:
                embed = getErrorMessage(self._urban, Internet.NO_TERM)
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def wikipedia(self, message, parameters):
        """Returns a wikipedia entry for the specified term.

        Parameters:
            term (str): The term to look up on wikipedia.
        """

        # Check for not enough parameters
        if len(parameters) < self._wikipedia.getMinParameters():
            embed = getErrorMessage(self._wikipedia, Internet.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            term = " ".join(parameters)

            # Create Wikipedia API object
            wikiHTML = wikipediaapi.Wikipedia(
                language = "en",
                extract_format = wikipediaapi.ExtractFormat.HTML
            )

            # Find Wiki entry
            termHTML = await loop.run_in_executor(None,
                wikiHTML.page,
                term
            )
            termTitle = termHTML.title

            # Check if wiki entry does not exist
            if not termHTML.exists():
                embed = getErrorMessage(self._wikipedia, Internet.NO_PAGE)
            
            # Wiki entry does exist
            else:

                termBS = await loop.run_in_executor(None,
                    BeautifulSoup,
                    termHTML.summary, 
                    "html.parser"
                )
                paragraphsHTML = termBS.findAll("p")

                # Get terms first paragraph
                paragraph = "No Summary"
                for p in paragraphsHTML:
                    if p.attrs == {} and len(p.text.replace("\n", "")) > 0:
                        paragraph = " ".join(text.strip() for text in p.find_all(text = True))
                        break
                    
                # Get page image
                pageImage = await loop.run_in_executor(None,
                    requests.get,
                    Internet.WIKIPEDIA_PAGE_IMAGE.format(termHTML.fullurl.split("/")[-1])
                )
                pageImage = pageImage.json()
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
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color,
                    timestamp = datetime.now()
                )

                if termImage != None:
                    embed.set_image(url = termImage)

        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )

    async def weather(self, message, parameters):
        """Returns the current weather for the specified location.\n

        location - The location to get the weather of.\n
        """

        # Check for not enough parameters
        if len(parameters) < self._weather.getMinParameters():
            embed = getErrorMessage(self._weather, Internet.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
        
            location = " ".join(parameters)
            
            # Get the url to call the API
            urlCall = Internet.WEATHER_API_CALL.format(
                os.environ["WEATHER_API_KEY"],
                location.replace(" ", "+")
            )

            # Use requests to get the data in JSON
            try:
                weatherData = await loop.run_in_executor(None,
                    requests.get,
                    urlCall
                )
                weatherData = weatherData.json()

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
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color,
                    timestamp = datetime.fromtimestamp(lastUpdated)
                ).set_thumbnail(
                    url = weatherIcon
                )

                # Add fields
                for field in fields:
                    embed.add_field(
                        name = field,
                        value = fields[field],
                        inline = True
                    )
            except:
                embed = getErrorMessage(self._weather, Internet.INVALID_LOCATION)
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def shortenUrl(self, message, parameters):
        """Shortens a URL
        """

        # Check for not enough parameters
        if len(parameters) < self._shortenUrl.getMinParameters():
            embed = getErrorMessage(self._shortenUrl, Internet.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._shortenUrl.getMaxParameters():
            embed = getErrorMessage(self._shortenUrl, Internet.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            url = parameters[0]

            # Check if the url is not valid
            if not url.startswith("https://") and not url.startswith("http://"):
                embed = getErrorMessage(self._shortenUrl, Internet.INVALID_URL)
            
            # URL is valid
            else:
                tinyurl = await loop.run_in_executor(None,
                    requests.get,
                    Internet.TINYURL_API.format(url)
                )
                tinyurl = tinyurl.content.decode()

                embed = discord.Embed(
                    title = "Your TinyURL link was generated!",
                    description = tinyurl,
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )

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

                    # Run the command but don't try running others
                    await self.run(message, cmd, cmd.getCommand(), message, parameters)
                    break

def setup(client):
    client.add_cog(Internet(client))
