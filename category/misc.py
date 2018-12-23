from util.file.database import loop
from util.file.omegaPsi import OmegaPsi
from util.file.server import Server

from util.misc.color import processColor

from util.utils.discordUtils import sendMessage, getErrorMessage
from util.utils.miscUtils import loadImageFromUrl, timestampToDatetime, datetimeToString

from datetime import datetime
from functools import partial
from supercog import Category, Command
import discord, os, pygame, random, requests

pygame.init()

reactions = ["⏪", "⬅", "➡", "⏩"]

class Misc(Category):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    BUG_EMBED_COLORS = {
        "Bug": 0xFF0000,
        "Error": 0xFF00FF,
        "Feedback": 0x00FFFF,
        "Moderator": 0xAA0000
    }

    ADVICE_URL = "https://api.adviceslip.com/advice"
    CHUCK_NORRIS_URL = "https://api.chucknorris.io/jokes/random"
    COLOR_HEX_URL = "http://thecolorapi.com/id?hex={}&format=json"
    COLOR_RGB_URL = "http://thecolorapi.com/id?rgb={},{},{}&format=json"
    COLOR_HSL_URL = "http://thecolorapi.com/id?hsl={},{}%,{}%&format=json"
    COLOR_CMYK_URL = "http://thecolorapi.com/id?cmyk={},{},{},{}&format=json"
    NUMBER_FACT_RANDOM_URL = "http://numbersapi.com/random/trivia?json"
    NUMBER_FACT_NUMBER_URL = "http://numbersapi.com/{}?json"
    TRONALD_DUMP_QUOTE = "https://api.tronalddump.io/random/quote"
    TRONALD_DUMP_MEME = "https://api.tronalddump.io/random/meme"
    LLAMAS_API = "https://www.fellowhashbrown.com/api/llamas?episode={}&fullScript={}"

    TWITTER_ICON = "http://pngimg.com/uploads/twitter/twitter_PNG29.png"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Errors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    NOT_ENOUGH_HEX_PARAMETERS = "NOT_ENOUGH_HEX_PARAMETERS"
    NOT_ENOUGH_RGB_PARAMETERS = "NOT_ENOUGH_RGB_PARAMETERS"
    NOT_ENOUGH_HSL_PARAMETERS = "NOT_ENOUGH_HSL_PARAMETERS"
    NOT_ENOUGH_CMYK_PARAMETERS = "NOT_ENOUGH_CMYK_PARAMETERS"

    TOO_MANY_HEX_PARAMETERS = "TOO_MANY_HEX_PARAMETERS"
    TOO_MANY_RGB_PARAMETERS = "TOO_MANY_RGB_PARAMETERS"
    TOO_MANY_HSL_PARAMETERS = "TOO_MANY_HSL_PARAMETERS"
    TOO_MANY_CMYK_PARAMETERS = "TOO_MANY_CMYK_PARAMETERS"

    NOT_A_NUMBER = "NOT_A_NUMBER"
    END_LESS_THAN_START = "END_LESS_THAN_START"
    NO_ACCESS = "NO_ACCESS"
    TOO_LONG = "TOO_LONG"

    INVALID_EPISODE = "INVALID_EPISODE"
    INVALID_MEMBER = "INVALID_MEMBER"
    INVALID_COLOR_TYPE = "INVALID_COLOR_TYPE"
    INVALID_PARAMETER = "INVALID_PARAMETER"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Constructor
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, client):
        super().__init__(
            client, 
            "Miscellaneous",
            description = "Other commands that don't really fit into a category yet.",
            embed_color = 0x00FF80,
            locally_inactive_error = Server.getInactiveError,
            globally_inactive_error = OmegaPsi.getInactiveError,
            locally_active_check = Server.isCommandActive,
            globally_active_check = OmegaPsi.isCommandActive
        )

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        self._advice = Command(commandDict = {
            "alternatives": ["advice"],
            "info": "Gives you a random piece of advice.",
            "errors": {
                Misc.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get a random piece of advice, you don't need any parameters."
                    ]
                }
            },
            "command": self.advice
        })

        self._choice = Command(commandDict = {
            "alternatives": ["choose", "choice"],
            "info": "Gives you a random choice from a specified list.",
            "parameters": {
                "choice(s)...": {
                    "info": "A list of choices to choose from.",
                    "optional": False
                }
            },
            "errors": {
                Misc.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to choose from a list, you need to give a list of at least 2 items."
                    ]
                }
            },
            "command": self.randomChoice
        })

        self._chuckNorris = Command(commandDict = {
            "alternatives": ["chuckNorris", "chuck", "norris"],
            "info": "Gives you a random Chuck Norris joke.",
            "errors": {
                Misc.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get a random Chuck Norris joke, you don't need any parameters."
                    ]
                }
            },
            "command": self.chuckNorris
        })

        self._color = Command(commandDict = {
            "alternatives": ["color"],
            "info": "Gives you the information about a color given either the Hex, RGB, HSL, or CMYK.",
            "parameters": {
                "colorType": {
                    "info": "The type of color to look up.",
                    "optional": True,
                    "accepted": {
                        "hex": {
                            "alternatives": ["hex", "HEX"],
                            "info": "Get color information using a hex code."
                        },
                        "rgb": {
                            "alternatives": ["rgb", "RGB"],
                            "info": "Get color information using an RGB tuple."
                        },
                        "hsl": {
                            "alternatives": ["hsl", "HSL"],
                            "info": "Get color information using HSL."
                        },
                        "cmyk": {
                            "alternatives": ["cmyk", "CMYK"],
                            "info": "Get color information using CMYK."
                        }
                    }
                },
                "color": {
                    "info": "The color information either in Hex, RGB, HSL, HSV, or CMYK.",
                    "optional": False
                }
            },
            "errors": {
                Misc.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to get color information, you need at least the type and the value."
                    ]
                },
                Misc.NOT_ENOUGH_HEX_PARAMETERS: {
                    "messages": [
                        "You need at least the hex code for this color type."
                    ]
                },
                Misc.NOT_ENOUGH_RGB_PARAMETERS: {
                    "messages": [
                        "You need at least the red, green, and blue values for this color type."
                    ]
                },
                Misc.NOT_ENOUGH_HSL_PARAMETERS: {
                    "messages": [
                        "You need the hue, saturation, and lightness for this color type."
                    ]
                },
                Misc.NOT_ENOUGH_CMYK_PARAMETERS: {
                    "messages": [
                        "You need the cyan, magenta, yellow, and black values for this color type."
                    ]
                },
                Misc.TOO_MANY_HEX_PARAMETERS: {
                    "messages": [
                        "You only need the hex code for this color type.."
                    ]
                },
                Misc.TOO_MANY_RGB_PARAMETERS: {
                    "messages": [
                        "You only need the red, green, and blue values for this color type."
                    ]
                },
                Misc.TOO_MANY_HSL_PARAMETERS: {
                    "messages": [
                        "You only need the hue, saturation, and lightness for this color type."
                    ]
                },
                Misc.TOO_MANY_CMYK_PARAMETERS: {
                    "messages": [
                        "You only need the cyan, magenta, yellow, and black values for this color type."
                    ]
                },
                Misc.INVALID_COLOR_TYPE: {
                    "messages": [
                        "The color type you entered is invalid."
                    ]
                }
            },
            "command": self.color
        })

        self._llamas = Command(commandDict = {
            "alternatives": ["llamas", "llamasWithHats", "llama"],
            "info": "Gives you a random quote from Llamas With Hats. You can also get the full script of an episode.",
            "parameters": {
                "episode": {
                    "info": "The episode to get the quote from. (This is required if you're getting a full script).",
                    "optional": True
                },
                "fullScript": {
                    "info": "Whether or not to get the full script of an episode.",
                    "optional": True,
                    "accepted": {
                        "script": {
                            "alternatives": ["fullScript", "full", "script"],
                            "info": "Get the full script of an episode."
                        }
                    }
                }
            },
            "errors": {
                Misc.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You have too many parameters for this. You only need the episode and whether or not you want the script."
                    ]
                },
                Misc.INVALID_EPISODE: {
                    "messages": [
                        "That is not a valid episode."
                    ]
                },
                Misc.INVALID_PARAMETER: {
                    "messages": [
                        "That is not a valid parameter."
                    ]
                }
            },
            "command": self.llamas
        })

        self._numberFact = Command(commandDict = {
            "alternatives": ["numberFact", "number"],
            "info": "Gives you a fact about a number.",
            "parameters": {
                "number": {
                    "info": "The number to get a fact about.",
                    "optional": False
                }
            },
            "errors": {
                Misc.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get a fact about a random number, you only need one number."
                    ]
                },
                Misc.INVALID_PARAMETER: {
                    "messages": [
                        "The number you entered is not a number."
                    ]
                }
            },
            "command": self.numberFact
        })

        self._random = Command(commandDict = {
            "alternatives": ["random", "rand", "randint"],
            "info": "Gives you a random number between the specified range.",
            "parameters": {
                "start": {
                    "info": "The number to start at.",
                    "optional": False
                },
                "end": {
                    "info": "The number to end at.",
                    "optional": False
                }
            },
            "errors": {
                Misc.NOT_A_NUMBER: {
                    "messages": [
                        "The value you entered is not a number."
                    ]
                },
                Misc.END_LESS_THAN_START: {
                    "messages": [
                        "The end value is less than the start value."
                    ]
                },
                Misc.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get a random number, you only need the start and end numbers."
                    ]
                }
            },
            "command": self.randomNumber
        })

        self._tronaldDumpQuote = Command(commandDict = {
            "alternatives": ["tronaldDumpQuote", "tronaldQuote", "trumpQuote"],
            "info": "Gives you a random quote from Donald Trump.",
            "errors": {
                Misc.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get a Donald Trump quote, you don't need any parameters."
                    ]
                }
            },
            "command": self.tronaldDumpQuote
        })

        self._tronaldDumpMeme = Command(commandDict = {
            "alternatives": ["tronaldDumpMeme", "tronaldMeme", "trumpMeme"],
            "info": "Gives you a random meme from Donald Trump.",
            "errors": {
                Misc.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get a Donald Trump meme, you don't need any parameters."
                    ]
                }
            },
            "command": self.tronaldDumpMeme
        })

        self._nickname = Command(commandDict = {
            "alternatives": ["nickname", "nick"],
            "info": "Changes your nickname.",
            "parameters": {
                "nickname": {
                    "info": "The new nickname to set.",
                    "optional": True
                }
            },
            "errors": {
                Misc.TOO_LONG: {
                    "messages": [
                        "To set your nickname, it must be less than 32 characters."
                    ]
                },
                Misc.NO_ACCESS: {
                    "messages": [
                        "I do not seem to have access to do that. You might be a higher role than me."
                    ]
                }
            },
            "command": self.nickname
        })

        self._botInfo = Command(commandDict = {
            "alternatives": ["botInfo", "bi"],
            "info": "Allows you to get the info about the bot.",
            "max_parameters": 0,
            "errors": {
                Misc.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get info about the bot, or the servers it's in, you don't need anything else."
                    ]
                }
            },
            "command": self.botInfo
        })

        self._info = Command(commandDict = {
            "alternatives": ["info", "??"],
            "info": "Gives you info on a member or the server as saved by the bot.",
            "run_in_private": False,
            "can_be_deactivated": False,
            "parameters": {
                "member": {
                    "optional": True,
                    "info": "Gives you info on a member in the server."
                }
            },
            "errors": {
                Misc.INVALID_MEMBER: {
                    "messages": [
                        "That member is not in the server."
                    ]
                }
            },
            "command": self.info
        })

        self.setCommands([
            self._advice,
            self._choice,
            self._chuckNorris,
            self._color,
            self._llamas,
            self._numberFact,
            self._random,
            self._tronaldDumpMeme,
            self._tronaldDumpQuote,

            self._nickname,
            self._botInfo,
            self._info
        ])

        self._scrollEmbeds = {}
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def advice(self, message, parameters):
        """Returns a random piece of advice.

        Parameters:
            parameters (list): The parameters given to the command.
        """

        # Check for too many parameters
        if len(parameters) > self._advice.getMaxParameters():
            embed = getErrorMessage(self._advice, Misc.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Get the advice
            adviceJson = await loop.run_in_executor(None,
                requests.get,
                Misc.ADVICE_URL
            )
            adviceJson = adviceJson.json()

            embed = discord.Embed(
                title = "Advice Number {}".format(adviceJson["slip"]["slip_id"]),
                description = adviceJson["slip"]["advice"],
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color,
                timestamp = datetime.now()
            ).set_footer(
                text = "Advice Slip API"
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
    
    async def randomChoice(self, message, parameters):
        """Returns a random choice from a list of choices.

        Parameters:
            choices (list): The list of choices to choose from.
        """

        # There is only 1 choice
        if len(parameters) < 2:
            embed = getErrorMessage(self._choice, Misc.NOT_ENOUGH_PARAMETERS)
        
        # There were at least 2 choices
        else:

            # Choose random option
            choice = random.choice(parameters)
            embed = discord.Embed(
                title = "Result",
                description = choice,
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
    
    async def chuckNorris(self, message, parameters):
        """Returns a random chuck norris fact.

        Parameters:
            parameters (list): The parameters given to the command.
        """

        # Check for too many parameters
        if len(parameters) > self._chuckNorris.getMaxParameters():
            embed = getErrorMessage(self._chuckNorris, Misc.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Get the joke; and URL
            chuckNorrisJson = await loop.run_in_executor(None,
                requests.get,
                Misc.CHUCK_NORRIS_URL
            )
            chuckNorrisJson = chuckNorrisJson.json()

            embed = discord.Embed(
                name = "Chuck Norris",
                description = chuckNorrisJson["value"],
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color,
                timestamp = datetime.now()
            ).set_author(
                name = "Chuck Norris Joke",
                icon_url = chuckNorrisJson["icon_url"]
            ).set_footer(
                text = "Chuck Norris API"
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
    
    async def color(self, message, parameters):
        """Returns information about a color.
        """

        # Check for not enough parameters
        if len(parameters) < self._color.getMinParameters():
            embed = getErrorMessage(self._color, Misc.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
        
            # Get the type of color to look up and validate it
            colorType = parameters[0]

            # HEX Color Type
            if colorType in self._color.getAcceptedParameter("colorType", "hex").getAlternatives():

                # HEX has only 1 parameter
                if len(parameters[1:]) > 1:
                    embed = getErrorMessage(self._color, Misc.TOO_MANY_HEX_PARAMETERS)
                elif len(parameters[1:]) < 1:
                    embed = getErrorMessage(self._color, Misc.NOT_ENOUGH_HEX_PARAMETERS)

                else:
                    response = await loop.run_in_executor(None,
                        requests.get,
                        Misc.COLOR_HEX_URL.format(
                            parameters[1]
                        )
                    )
                    response = response.json()

                    embed = processColor(response)

            # RGB Color Type
            elif colorType in self._color.getAcceptedParameter("colorType", "rgb").getAlternatives():

                # RGB has only 3 parameters
                if len(parameters[1:]) > 3:
                    return getErrorMessage(self._color, Misc.TOO_MANY_RGB_PARAMETERS)
                elif len(parameters[1:]) < 3:
                    return getErrorMessage(self._color, Misc.NOT_ENOUGH_RGB_PARAMETERS)

                else:
                    response = await loop.run_in_executor(None,
                        requests.get,
                        Misc.COLOR_RGB_URL.format(
                            parameters[1], parameters[2], parameters[3]
                        )
                    )
                    response = response.json()

                    embed = processColor(response)
            
            # HSL Color Type
            elif colorType in self._color.getAcceptedParameter("colorType", "hsl").getAlternatives():

                # HSL has only 3 parameters
                if len(parameters[1:]) > 3:
                    return getErrorMessage(self._color, Misc.TOO_MANY_HSL_PARAMETERS)
                elif len(parameters[1:]) < 3:
                    return getErrorMessage(self._color, Misc.NOT_ENOUGH_HSL_PARAMETERS)

                else:
                    response = await loop.run_in_executor(None,
                        requests.get,
                        Misc.COLOR_HSL_URL.format(
                            parameters[1], parameters[2], parameters[3]
                        )
                    )
                    response = response.json()

                    embed = processColor(response)
            
            # CMYK Color Type
            elif colorType in self._color.getAcceptedParameter("colorType", "cmyk").getAlternatives():

                # CMYK has only 4 parameters
                if len(parameters[1:]) > 4:
                    return getErrorMessage(self._color, Misc.TOO_MANY_CMYK_PARAMETERS)
                elif len(parameters[1:]) < 4:
                    return getErrorMessage(self._color, Misc.NOT_ENOUGH_CMYK_PARAMETERS)
                
                else:
                    response = await loop.run_in_executor(None,
                        requests.get,
                        Misc.COLOR_CMYK_URL.format(
                            parameters[1], parameters[2], parameters[3], parameters[4]
                        )
                    )
                    response = response.json()

                    embed = processColor(response)
            
            # Invalid Color Type
            else:
                embed = getErrorMessage(self._color, Misc.INVALID_COLOR_TYPE)
        
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
    
    async def llamas(self, message, parameters):
        """
        """

        script = None
        # Check for too many parameters
        if len(parameters) > self._llamas.getMaxParameters():
            embed = getErrorMessage(self._llamas, Misc.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            episode = random.randint(1, 12) if len(parameters) < 1 else parameters[0]
            script = False if len(parameters) < 2 else parameters[1]
            valid = True

            # Check if episode is valid
            try:
                episode = int(episode)
                if not (episode >= 1 and episode <= 12):
                    raise ValueError()
            except:
                embed = getErrorMessage(self._llamas, Misc.INVALID_EPISODE)
                valid = False
            
            # Check if script is valid
            if script != False:
                if script in self._llamas.getAcceptedParameter("fullScript", "script").getAlternatives():
                    script = True
                else:
                    embed = getErrorMessage(self._llamas, Misc.INVALID_PARAMETER)
                    valid = False
            
            # Only run if valid
            if valid:

                # Make API call
                response = await loop.run_in_executor(None,
                    requests.get,
                    Misc.LLAMAS_API.format(
                        episode, script if script else ""
                    )
                )
                response = response.json()

                image = response["image"]

                # Create embed
                if script:
                    fields = []
                    fieldValue = ""
                    for quote in response["quotes"]:
                        line = "**{}** {}\n".format(
                            (quote["author"] + ":") if len(quote["author"]) > 0 else "",
                            quote["value"]
                        )

                        if len(fieldValue) + len(line) >= OmegaPsi.MESSAGE_THRESHOLD:
                            fields.append(fieldValue)
                            fieldValue = ""
                        
                        fieldValue += line
                    
                    if len(fieldValue) > 0:
                        fields.append(fieldValue)

                    self._scrollEmbeds[str(message.author.id)] = {
                        "message": None,
                        "embeds": [],
                        "value": 0,
                        "min": 0,
                        "max": len(fields) - 1
                    }

                    count = 0
                    for field in fields:
                        count += 1
                        embed = discord.Embed(
                            title = "Episode {}{}".format(
                                episode,
                                " - Script {}".format(
                                    "({} / {})".format(
                                        count, len(fields)
                                    ) if len(fields) > 1 else ""
                                ) if script else ""
                            ),
                            description = field,
                            colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                        )

                        if image != None:
                            embed.set_thumbnail(
                                url = image
                            )

                        self._scrollEmbeds[str(message.author.id)]["embeds"].append(embed)
                    
                    embed = self._scrollEmbeds[str(message.author.id)]["embeds"][0]
                
                else:
                    description = "**{}** {}".format(
                            (response["author"] + ":") if len(response["author"]) > 0 else "",
                            response["value"]
                        )

                    embed = discord.Embed(
                        title = "Episode {}{}".format(
                            episode,
                            " - Script" if script else ""
                        ),
                        description = description
                    )

                    if image != None:
                        embed.set_thumbnail(
                            url = image
                        )
        
        msg = await sendMessage(
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

        if script:
            self._scrollEmbeds[str(message.author.id)]["message"] = msg
            for reaction in reactions:
                await msg.add_reaction(reaction)
    
    async def numberFact(self, message, parameters):
        """Returns a fact about a random number.

        Parameters:
            parameters (list): The list of choices to choose from.
        """

        # Check for too many parameters
        if len(parameters) > self._numberFact.getMaxParameters():
            embed = getErrorMessage(self._numberFact, Misc.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            number = None if len(parameters) == 0 else parameters[0]

            # Make sure number is valid
            try:
                if number != None:
                    number = int(number)

                # Get the number fact
                numberFactJson = await loop.run_in_executor(None,
                    requests.get,
                    Misc.NUMBER_FACT_RANDOM_URL if number == None else Misc.NUMBER_FACT_NUMBER_URL.format(number)
                )
                numberFactJson = numberFactJson.json()

                embed = discord.Embed(
                    title = "Fact about the number *{}*".format(numberFactJson["number"]),
                    description = numberFactJson["text"],
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color,
                    timestamp = datetime.now()
                ).set_footer(
                    text = "NumbersAPI"
                )
            except:
                embed = getErrorMessage(self._numberFact, Misc.INVALID_PARAMETER)

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

    async def randomNumber(self, message, parameters):
        """Returns a random number between the start and end values.

        Parameters:
            start (int): The number to start at.
            end (int): The number to end at.
        """

        # Set default values
        start = 0
        end = 100
        
        # Check for too many parameters
        if len(parameters) > 2:
            embed = getErrorMessage(self._random, Misc.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Check for 2 parameters
            if len(parameters) == 2:
                start = parameters[0]
                end = parameters[1]
            
            # Check if start or end are not numbers
            if not str(start).isdigit() or not str(end).isdigit():
                embed = getErrorMessage(self._random, Misc.NOT_A_NUMBER)
            
            # Start and end were numbers
            else:

                start = int(start)
                end = int(end)
                
                # Check if end is less than start
                if end < start:
                    embed = getErrorMessage(self._random, Misc.END_LESS_THAN_START)
                
                # Start was less than end
                else:

                    # Choose random number
                    number = random.randint(start, end)
                    embed = discord.Embed(
                        title = "Result",
                        description = str(number),
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
    
    async def tronaldDumpMeme(self, message, parameters):
        """Returns a random Tronald Dump meme.

        Parameters:
            parameters (list): The parameters given to the command.
        """
    
        # Check for too many parameters
        if len(parameters) > self._tronaldDumpMeme.getMaxParameters():
            embed = getErrorMessage(self._tronaldDumpMeme, Misc.TOO_MANY_PARAMETERS)

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
        
        # There were the proper amount of parameters
        else:

            # Get the meme
            meme = await loop.run_in_executor(None,
                loadImageFromUrl,
                Misc.TRONALD_DUMP_MEME
            )

            # Temporarily save the image
            current = datetime.now()
            image = "TRONALD_DUMP_MEME_{}_{}_{}.png".format(
                current.hour, current.minute, current.second
            )
            pygame.image.save(meme, image)

            # Send file then remove
            await sendMessage(
                self.client,
                message,
                filename = image
            )
            os.remove(image)
    
    async def tronaldDumpQuote(self, message, parameters):
        """Returns a random Tronald Dump quote.

        Parameters:
            parameters (list): The parameters given to the command.
        """
        
        # Check for too many parameters
        if len(parameters) > self._tronaldDumpQuote.getMaxParameters():
            embed = getErrorMessage(self._tronaldDumpQuote, Misc.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Get the quote
            quoteJson = await loop.run_in_executor(None,
                requests.get,
                Misc.TRONALD_DUMP_QUOTE
            )
            quoteJson = quoteJson.json()

            embed = discord.Embed(
                title = "Donald Trump Quote",
                description = quoteJson["value"],
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color,
                timestamp = timestampToDatetime(quoteJson["appeared_at"]),
                url = quoteJson["_embedded"]["source"][0]["url"]
            ).set_author(
                name = quoteJson["_embedded"]["author"][0]["name"],
                icon_url = Misc.TWITTER_ICON
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
    
    async def nickname(self, message, parameters):
        """Changes the nickname of the specified member.

        Parameters:
            discordMember (discord.Member): The Discord Member to change the nickname of.
            nickname (str): The new nickname to set. (No nickname will clear the nickname).
        """

        # See if there are no parameters
        if len(parameters) == 0:

            # Try to clear it
            try:
                await message.author.edit(
                    nick = None
                )
                embed = discord.Embed(
                    title = "Nickname Cleared",
                    description = "Your nickname has been cleared.",
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )
            
            except discord.Forbidden:
                embed = getErrorMessage(self._nickname, Misc.NO_ACCESS)
        
        # There are parameters
        else:

            try:

                # See if nickname is too long
                if len(" ".join(parameters)) > 32:
                    embed = getErrorMessage(self._nickname, Misc.TOO_LONG)

                # Nickname is not too long
                else:
                    await message.author.edit(
                        nick = " ".join(parameters)
                    )

                    embed = discord.Embed(
                        title = "Nickname Set",
                        description = "Your nickname has been set to `{}`".format(" ".join(parameters)),
                        colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                    )
            
            except discord.Forbidden:
                embed = getErrorMessage(self._nickname, Misc.NO_ACCESS)
        
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
    
    async def botInfo(self, message, parameters):
        """Returns the info on the bot.\n
        """

        # Check if parameters exceeds maximum parameter
        if len(parameters) > self._info.getMaxParameters():
            embed = getErrorMessage(self._info, Misc.TOO_MANY_PARAMETERS)
        
        # Parameters do not exceed maximum parameters
        else:

            # Open the bot info
            omegaPsi = await OmegaPsi.openOmegaPsi()

            # Add a list of bot moderators and inactive commands
            botModerators = ""
            for moderator in omegaPsi["moderators"]:
                botModerators += "<@{}>\n".format(moderator)
        
            inactiveCommands = ""
            for command in omegaPsi["inactive_commands"]:
                inactiveCommands += "{}\nReason: {}\n".format(
                    command, omegaPsi["inactive_commands"][command]
                )

            # Set these up in a dictionary to add to an embed
            tags = {
                "Bot Moderators": botModerators,
                "Inactive Commands": inactiveCommands
            }

            # Create the embed and add the tags as fields
            owner = await self.client.application_info()
            owner = owner.owner
            
            embed = discord.Embed(
                title = "Omega Psi",
                description = "Owner: {} ({}#{})".format(
                    owner.mention,
                    owner.name, owner.discriminator
                ),
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            )

            for tag in tags:
                embed.add_field(
                    name = tag,
                    value = tags[tag] if len(tags[tag]) > 0 else "None",
                    inline = False
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
    
    async def info(self, message, parameters):
        """Returns information about the server or a member mentioned
        """

        # Check for too many mentions
        if len(message.mentions) > 1:
            embed = getErrorMessage(self._info, Misc.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of mentions
        else:

            # See if there are no mentions
            if len(message.mentions) == 0:
                embed = await self.getServerInfo(message, message.guild)

            # There is one mention
            else:
                embed = await self.getMemberInfo(message, message.guild, message.mentions[0])
        
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
    
    async def getServerInfo(self, message, discordServer):
        """Returns information about the server given as saved by Omega Psi.\n

        discordServer - The Discord Server to get information about as saved by Omega Psi.\n
        """

        # Open server file and bot file
        server = await Server.openServer(discordServer)
        omegaPsi = await OmegaPsi.openOmegaPsi()

        # Get name, owner, ranking, join message, inactive commands
        serverPrefixes = server["prefixes"]
        serverName = discordServer.name
        serverOwner = discordServer.owner
        serverCreate = datetimeToString(discordServer.created_at)

        serverRanking = server["ranking"]

        serverWelcomeMessage = server["welcome_message"]["active"]
        serverWelcomeMessageChannel = server["welcome_message"]["channel"]
        serverDmOnWelcomeFail = server["welcome_message"]["dm_on_fail"]

        serverProfanityFilter = server["profanity_filter"]["active"]
        serverDmOnProfanityFail = server["profanity_filter"]["dm_on_fail"]

        serverAutorole = server["autorole"]["active"]
        serverAutoroleRole = server["autorole"]["role"]
        serverDmOnAutoroleFail = server["autorole"]["dm_on_fail"]

        serverInactiveCommands = server["inactive_commands"]

        botInactiveCommands = omegaPsi["inactive_commands"]

        # Create embed
        embed = discord.Embed(
            title = serverName,
            description = "Owner: {} ({})".format(
                "Unknown" if serverOwner == None else serverOwner.mention,
                "Unknown" if serverOwner == None else (serverOwner.name + "#" + serverOwner.discriminator)
            ),
            colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
        ).set_thumbnail(
            url = discordServer.icon_url
        )

        # Add fields
        serverCommands = ""
        for command in serverInactiveCommands:
            serverCommands += "{}\nReason: {}\n\n".format(
                command, serverInactiveCommands[command]
            )
        
        botCommands = ""
        for command in botInactiveCommands:
            botCommands += "{}\nReason: {}\n\n".format(
                command, botInactiveCommands[command]
            )

        tags = {
            "Created At": serverCreate,
            "Prefixes": ", ".join(serverPrefixes),
            "Ranking": "Yes" if serverRanking else "No",
            "Welcome Message": "{}\n{}\n{}".format(
                "Active" if serverWelcomeMessage else "Inactive",
                "<#{}>".format(
                    serverWelcomeMessageChannel
                ) if serverWelcomeMessageChannel != None else "No Channel Set",
                "{} on fail.".format(
                    "Will DM" if serverDmOnWelcomeFail else "Will Not DM"
                )
            ),
            "Profanity Filter": "{}\n{}".format(
                "Active" if serverProfanityFilter else "Inactive",
                "{} on fail.".format(
                    "Will DM" if serverDmOnProfanityFail else "Will Not DM"
                )
            ),
            "Autorole": "{}\n{}\n{}".format(
                "Active" if serverAutorole else "Inactive",
                "<@&{}>".format(
                    serverAutoroleRole
                ) if serverAutoroleRole != None else "No Role Set",
                "{} on fail.".format(
                    "Will DM" if serverDmOnAutoroleFail else "Will Not DM"
                )
            ),
            "Locally Inactive Commands": serverCommands if len(serverCommands) > 0 else None,
            "Globally Inactive Commands": botCommands if len(botCommands) > 0 else None
        }
        for tag in tags:

            # only add if tag field is not None
            if tags[tag] != None:
                embed.add_field(
                    name = tag,
                    value = tags[tag],
                    inline = tag not in ["Created At", "Locally Inactive Commands", "Globally Inactive Commands"]
                )

        # Close server file
        await Server.closeServer(server)

        return embed
    
    async def getMemberInfo(self, message, discordServer, discordMember):
        """Returns information about the member given as saved by Omega Psi.\n

        discordServer - The Discord Server to load the Discord Member information from.\n
        discordMember - The Discord Member to get information about as saved by Omega Psi.\n
        """

        # Open server file
        server = await Server.openServer(discordServer)

        # Get member
        member = await Server.getMember(discordServer, discordMember)
        memberName = discordMember.name
        memberDiscriminator = discordMember.discriminator
        memberCreate = datetimeToString(discordMember.created_at)
        memberJoin = datetimeToString(discordMember.joined_at)
        memberId = discordMember.id
        memberNickname = discordMember.nick
        memberModerator = await Server.isAuthorModerator(discordMember)
        memberExperience = member["experience"]
        memberLevel = member["level"]

        # Create embed
        embed = discord.Embed(
            title = memberName + "#" + memberDiscriminator,
            description = "<@{}>".format(
                memberId
            ),
            colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
        )

        # Add fields
        tags = {
            "Created At": memberCreate,
            "Joined At": memberJoin,
            "Nickname": memberNickname,
            "Moderator": "Yes" if memberModerator else "No"
        }

        if server["ranking"]:
            tags["Experience"] = memberExperience
            tags["Level"] = memberLevel

        for tag in tags:
            embed.add_field(
                name = tag,
                value = tags[tag],
                inline = False
            )

        # Close server file
        await Server.closeServer(server)

        return embed
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Parsing
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def on_message(self, message):
        """Parses a message and runs a Miscellaneous Category command if it can.\n

        message - The Discord Message to parse.\n
        """

        # Make sure message starts with the prefix
        if await Server.startsWithPrefix(message.guild, message.content) and not message.author.bot:

            # Split up into command and parameters if possible
            command, parameters = Category.parseText(await Server.getPrefixes(message.guild), message.content)
            
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            # Iterate through commands
            for cmd in self.getCommands():
                if command in cmd.getAlternatives():
                    async with message.channel.typing():

                        # Run the command but don't try running others
                        await self.run(message, cmd, cmd.getCommand(), message, parameters)
                    break
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Reactions
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def manage_scrolling(self, reaction, member):
        """Manages the scrolling of any help embeds
        """

        # See if the member has a scrolling embed in the list
        if str(member.id) in self._scrollEmbeds:

            if self._scrollEmbeds[str(member.id)]["message"].id == reaction.message.id:
                initial = self._scrollEmbeds[str(member.id)]["value"]

                # User wants to go to the beginning
                if str(reaction) == "⏪":
                    self._scrollEmbeds[str(member.id)]["value"] = 0

                # User wants to go to the end
                elif str(reaction) == "⏩":
                    self._scrollEmbeds[str(member.id)]["value"] = len(self._scrollEmbeds[str(member.id)]["embeds"]) - 1

                # User wants to go left
                elif str(reaction) == "⬅":
                    self._scrollEmbeds[str(member.id)]["value"] -= 1
                    if self._scrollEmbeds[str(member.id)]["value"] < 0:
                        self._scrollEmbeds[str(member.id)]["value"] = 0

                # User wants to go right
                elif str(reaction) == "➡":
                    self._scrollEmbeds[str(member.id)]["value"] += 1
                    if self._scrollEmbeds[str(member.id)]["value"] > len(self._scrollEmbeds[str(member.id)]["embeds"]) - 1:
                        self._scrollEmbeds[str(member.id)]["value"] = len(self._scrollEmbeds[str(member.id)]["embeds"]) - 1

                # Update the embed if necessary
                if self._scrollEmbeds[str(member.id)]["value"] != initial:
                    value = self._scrollEmbeds[str(member.id)]["value"]

                    await reaction.message.edit(
                        embed = self._scrollEmbeds[str(member.id)]["embeds"][value]
                    )

    async def on_reaction_add(self, reaction, member):
        """Determines which reaction was added to a message. Only reactions right now are

        :arrow_left: which tells the embed to scroll back a field.
        :arrow_right: which tells the embed to scroll forward a field.
        :rewind: which tells the embed to go back to the beginning.
        :fast_forward: which tells the embed to go to the end.
        """
        await self.manage_scrolling(reaction, member)
    
    async def on_reaction_remove(self, reaction, member):
        """Determines which reaction was removed from a message. Only reactions right now are

        :arrow_left: which tells the embed to scroll back a field.
        :arrow_right: which tells the embed to scroll forward a field.
        :rewind: which tells the embed to go back to the beginning.
        :fast_forward: which tells the embed to go to the end.
        """
        await self.manage_scrolling(reaction, member)

def setup(client):
    client.add_cog(Misc(client))