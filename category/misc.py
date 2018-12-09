from util.file.database import loop
from util.file.omegaPsi import OmegaPsi
from util.file.server import Server

from util.misc.color import processColor

from util.utils.discordUtils import sendMessage, getErrorMessage
from util.utils.miscUtils import loadImageFromUrl, timestampToDatetime, datetimeToString

from datetime import datetime
from supercog import Category, Command
import discord, os, pygame, random, requests

pygame.init()

scrollEmbeds = {}

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
    NUMBER_FACT_URL = "http://numbersapi.com/random/year?json"
    TRONALD_DUMP_QUOTE = "https://api.tronalddump.io/random/quote"
    TRONALD_DUMP_MEME = "https://api.tronalddump.io/random/meme"

    TWITTER_ICON = "http://pngimg.com/uploads/twitter/twitter_PNG29.png"

    GITHUB_COMMANDS = "https://www.github.com/FellowHashbrown/omega-psi/blob/master/category/commands.md"
    GITHUB_LINK = "https://www.github.com/FellowHashbrown/omega-psi"

    REPL_IT_LINK = "https://repl.it/@FellowHashbrown/Omega-Psi"

    UPTIME_LINK = "https://stats.uptimerobot.com/KQG3Rc54B"

    VOTE_LINK = "https://discordbots.org/bot/503804826187071501/vote"

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

    INVALID_MEMBER = "INVALID_MEMBER"
    INVALID_COLOR_TYPE = "INVALID_COLOR_TYPE"

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

        self._numberFact = Command(commandDict = {
            "alternatives": ["numberFact", "number"],
            "info": "Gives you a fact about a number.",
            "errors": {
                Misc.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get a fact about a random number, you don't need any parameters."
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

        self._ping = Command(commandDict = {
            "alternatives": ["ping"],
            "info": "Pings the bot.",
            "errors": {
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You don't need any parameters to ping the bot."
                    ]
                }
            },
            "command": self.ping
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

        self._invite = Command(commandDict = {
            "alternatives": ["inviteBot", "invite"],
            "info": "Gives you a link so you can invite the bot to your own server.",
            "can_be_deactivated": False,
            "parameters": {
                "permissions...": {
                    "info": "The permissions you want the bot to have in your server.",
                    "optional": True,
                    "accepted_parameters": {
                        # General Permissions
                        "administrator": {
                            "alternatives": ["administrator", "admin"],
                            "info": "Gives the bot administrator privileges.",
                        },
                        "viewAuditLog": {
                            "alternatives": ["viewAuditLog", "auditLog", "audit"],
                            "info": "Gives the bot access to the audit log.",
                        },
                        "manageServer":{
                            "alternatives": ["manageServer", "mngSvr"],
                            "info": "Gives the bot permission to manage the server."
                        },
                        "manageRoles": {
                            "alternatives": ["manageRoles", "mngRoles"],
                            "info": "Gives the bot permission to manage the roles."
                        },
                        "manageChannels": {
                            "alternatives": ["manageChannels", "mngChnls"],
                            "info": "Gives the bot permission to manage the channels."
                        },
                        "kickMembers": {
                            "alternatives": ["kickMembers", "kickMbrs"],
                            "info": "Gives the bot permission to kick members."
                        },
                        "banMembers": {
                            "alternatives": ["banMembers", "banMbrs"],
                            "info": "Gives the bot permission to ban members."
                        },
                        "createInstantInvite": {
                            "alternatives": ["createInstantInvite", "instantInvite", "invite"],
                            "info": "Gives the bot permission to create an instant invite for the server."
                        },
                        "changeNickname": {
                            "alternatives": ["changeNickname", "chngNick"],
                            "info": "Gives the bot permission to change their nickname."
                        },
                        "manageNicknames": {
                            "alternatives": ["manageNicknames", "mngNick"],
                            "info": "Gives the bot permission to manage other people's nicknames."
                        },
                        "manageEmojis": {
                            "alternatives": ["manageEmojis", "mngEmojis"],
                            "info": "Gives the bot permission to manage the server's emojis."
                        },
                        "manageWebhooks": {
                            "alternatives": ["manageWebhooks", "mngWbhks"],
                            "info": "Gives the bot permission to manage the server's webhooks."
                        },
                        "viewChannels": {
                            "alternatives": ["viewChannels", "viewChnls"],
                            "info": "Gives the bot permission to view the channels."
                        },

                        # Text Permissions
                        "sendMessages": {
                            "alternatives": ["sendMessages", "message", "msg"],
                            "info": "Gives the bot permission to send messages."
                        },
                        "sendTtsMessages": {
                            "alternatives": ["sendTtsMessages", "ttsMessages"],
                            "info": "Gives the bot permission to send TTS (text-to-speech) messages."
                        },
                        "manageMessages": {
                            "alternatives": ["manageMessages", "mngMsgs"],
                            "info": "Gives the bot permission to manage messages."
                        },
                        "embedLinks": {
                            "alternatives": ["embedLinks", "links"],
                            "info": "Gives the bot permission to embed links."
                        },
                        "attachFiles": {
                            "alternatives": ["attachFiles", "files"],
                            "info": "Gives the bot permission to attach files."
                        },
                        "readMessageHistory": {
                            "alternatives": ["readMessageHistory", "messageHistory", "msgHist"],
                            "info": "Gives the bot permission to read the message history."
                        },
                        "mentionEveryone": {
                            "alternatives": ["mentionEveryone"],
                            "info": "Gives the bot permission to mention everyone."
                        },
                        "useExternalEmojis": {
                            "alternatives": ["useExternalEmojis", "externalEmojis", "emojis"],
                            "info": "Gives the bot permission to use other server's emojis."
                        },
                        "addReactions": {
                            "alternatives": ["addReactions", "reactions"],
                            "info": "Gives the bot permission to react to messages."
                        },

                        # Voice Permissions
                        "connect": {
                            "alternatives": ["connect"],
                            "info": "Gives the bot permission to connect to a voice channel."
                        },
                        "speak": {
                            "alternatives": ["speak"],
                            "info": "Gives the bot permission to speak in a voice channel."
                        },
                        "muteMembers": {
                            "alternatives": ["muteMembers", "mute"],
                            "info": "Gives the bot permission to mute members in a voice channel."
                        },
                        "deafenMembers": {
                            "alternatives": ["deafenMembers", "deafen"],
                            "info": "Gives the bot permission to deafen members in a voice channel."
                        },
                        "useMembers": {
                            "alternatives": ["useMembers"],
                            "info": "Gives the bot permission to move members to a different voice channel."
                        },
                        "useVoiceActivity": {
                            "alternatives": ["useVoiceActivity", "useVoice", "voice"],
                            "info": "Gives the bot permission to use voice activity in a voice channel."
                        },
                        "prioritySpeaker": {
                            "alternatives": ["prioritySpeaker"],
                            "info": "Gives the bot permission to the priority speaker."
                        }
                    }
                }
            },
            "command": self.invite
        })

        self._vote = Command(commandDict = {
            "alternatives": ["vote"],
            "info": "Allows you to get a link to vote for Omega Psi on discordbots.org",
            "errors": {
                Misc.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get the voting link, you don't need any parameters."
                    ]
                }
            },
            "command": self.vote
        })

        self._github = Command(commandDict = {
            "alternatives": ["github"],
            "info": "Sends you the Github link for the source code.",
            "errors": {
                Misc.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get the Github link, you don't need any parameters."
                    ]
                }
            },
            "command": self.github
        })

        self._replit = Command(commandDict = {
            "alternatives": ["replit", "repl.it", "repl"],
            "info": "Sends you the Repl.it link for the bot.",
            "errors": {
                Misc.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get the Repl.it link, you don't need any parameters."
                    ]
                }
            },
            "command": self.replit
        })

        self._uptime = Command(commandDict = {
            "alternatives": ["uptime"],
            "info": "Sends a link to see the uptime of Omega Psi.",
            "errors": {
                Misc.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get the uptime of Omega Psi, you don't need any parameters."
                    ]
                }
            },
            "command": self.uptime
        })

        self._sendBug = Command(commandDict = {
            "alternatives": ["sendBug", "bug", "error", "feedback"],
            "info": "Allows you to send any feedback, bugs, or errors directly to all developers of Omega Psi.",
            "parameters": {
                "messageType": {
                    "info": "The type of message this is.",
                    "optional": False,
                    "accepted_parameters": {
                        "bug": {
                            "alternatives": ["bug"],
                            "info": "The type of message is a bug in Omega Psi."
                        },
                        "error": {
                            "alternatives": ["error"],
                            "info": "Something is going wrong but you don't know what."
                        },
                        "feedback": {
                            "alternatives": ["feedback"],
                            "info": "You want to provide feedback, suggest features, or anything else that doesn't fit into a message type."
                        },
                        "moderator": {
                            "alternatives": ["moderator"],
                            "info": "If you are the Server Owner and you do not have Server Moderator commands showing up in the help menu, use this."
                        }
                    }
                },
                "message": {
                    "info": "The message to send to the developers of Omega Psi.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to send a bug, error, or feedback to the developers of Omega Psi, you need to type in the message."
                    ]
                },
                Misc.INVALID_PARAMETER: {
                    "messages": [
                        "That was an invalid message type."
                    ]
                }
            },
            "command": self.sendBug
        })

        self.setCommands([
            self._advice,
            self._choice,
            self._chuckNorris,
            self._color,
            self._numberFact,
            self._random,
            self._tronaldDumpMeme,
            self._tronaldDumpQuote,

            self._ping,
            self._nickname,
            self._info,
            self._invite,
            self._vote,
            self._github,
            self._replit,
            self._uptime,
            self._sendBug
        ])
    
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

            # Get the number fact
            numberFactJson = await loop.run_in_executor(None,
                requests.get,
                Misc.NUMBER_FACT_URL
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
    
    async def ping(self, message, parameters):
        """Pings the bot
        """

        # Check for too many parameters
        if len(parameters) > self._ping.getMaxParameters():
            embed = getErrorMessage(self._ping, Misc.TOO_MANY_PARAMETERS)

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
            start = datetime.now()

            pingMessage = await message.channel.send(
                "Ping :slight_smile:"
            )

            end = datetime.now()

            diff = int((end - start).total_seconds() * 1000)

            await pingMessage.edit(
                content = "Ping :slight_smile: `{} ms`".format(
                    diff
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
        server = Server.openServer(discordServer)
        omegaPsi = OmegaPsi.openOmegaPsi()

        # Get name, owner, ranking, join message, inactive commands
        serverPrefixes = server["prefixes"]
        serverName = discordServer.name
        serverOwner = discordServer.owner
        serverCreate = datetimeToString(discordServer.created_at)
        serverRanking = server["ranking"]
        serverJoinMessage = server["join_message"]["active"]
        serverJoinMessageChannel = server["join_message"]["channel"]
        serverInactiveCommands = server["inactive_commands"]

        botInactiveCommands = omegaPsi["inactive_commands"]

        # Create embed
        embed = discord.Embed(
            title = serverName,
            description = "Owner: {} ({})".format(
                serverOwner.mention,
                serverOwner.name + "#" + serverOwner.discriminator
            ),
            colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
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
            "Join Message": "{}\n{}".format(
                "Active" if serverJoinMessage else "Inactive",
                "<#{}>".format(
                    serverJoinMessageChannel
                ) if serverJoinMessageChannel != None else ""
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
                    inline = False
                )

        # Close server file
        Server.closeServer(server)

        return embed
    
    async def getMemberInfo(self, message, discordServer, discordMember):
        """Returns information about the member given as saved by Omega Psi.\n

        discordServer - The Discord Server to load the Discord Member information from.\n
        discordMember - The Discord Member to get information about as saved by Omega Psi.\n
        """

        # Open server file
        server = Server.openServer(discordServer)

        # Get member
        member = Server.getMember(discordServer, discordMember)
        memberName = discordMember.name
        memberDiscriminator = discordMember.discriminator
        memberCreate = datetimeToString(discordMember.created_at)
        memberJoin = datetimeToString(discordMember.joined_at)
        memberId = discordMember.id
        memberNickname = discordMember.nick
        memberModerator = Server.isAuthorModerator(discordMember)
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
        Server.closeServer(server)

        return embed
    
    async def invite(self, message, parameters):
        """Returns the link so someone can invite the bot to their own server.\n

        permissions - The permissions that you want the bot to have.\n
        """

        permissions = parameters

        # Set default permissions
        permissionsInteger = 0

        # Get permissions needed; If the admin permission is found, the integer will default to 8
        adminFound = False

        # Iterate through permissions
        for permission in permissions:

            # Iterate through accepted permissions
            for acceptedPermission in self._invite.getAcceptedParameters("permissions..."):

                # Permission is in the accepted permissions
                if permission in self._invite.getAcceptedParameter("permissions...", acceptedPermission).getAlternatives():

                    # Add the integer value to the permissions integer
                    permissionsInteger += Server.PERMISSIONS[acceptedPermission]

                    # Check if the accepted permission was administrator
                    if acceptedPermission == "administrator":
                        adminFound = True

                    # Since it was found, we don't want to continue searching through the accepted permissions
                    # We want to move to the next permission
                    break

        # The admin permission was found, default the integer to 8
        if adminFound:
            permissionsInteger = Server.PERMISSIONS["administrator"]

        await sendMessage(
            self.client,
            message,
            message = Server.BOT_INVITE.format(permissionsInteger)
        )
    
    async def vote(self, message, parameters):
        """Sends a link to discordbots.org to vote for the bot.
        """

        # Check for too many parameters
        if len(parameters) > self._vote.getMaxParameters():
            embed = getErrorMessage(self._vote, Misc.TOO_MANY_PARAMETERS)

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
            await sendMessage(
                self.client,
                message,
                message = Misc.VOTE_LINK
            )
    
    async def github(self, message, parameters):
        """Returns the Github link for the bot.
        """

        # Check for too many parameters
        if len(parameters) > self._github.getMaxParameters():
            embed = getErrorMessage(self._github, Misc.TOO_MANY_PARAMETERS)

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
            await sendMessage(
                self.client,
                message,
                message = Misc.GITHUB_LINK
            )
    
    async def replit(self, message, parameters):
        """Returns the Repl.it link for the bot.
        """

        # Check for too many parameters
        if len(parameters) > self._replit.getMaxParameters():
            embed = getErrorMessage(self._replit, Misc.TOO_MANY_PARAMETERS)
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
            await sendMessage(
                self.client,
                message,
                message = Misc.REPL_IT_LINK
            )
    
    async def uptime(self, message, parameters):
        """Returns the uptime link for the bot.
        """

        # Check for too many parameters
        if len(parameters) > self._uptime.getMaxParameters():
            embed = getErrorMessage(self._uptime, Misc.TOO_MANY_PARAMETERS)
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
            await sendMessage(
                self.client,
                message,
                message = Misc.UPTIME_LINK
            )
    
    async def sendBug(self, message, parameters):
        """Sends all bot moderators a message from the bot.\n

        discordServer - The Discord Server that the message originated from.\n
        discordMember - The Discord User/Member that wants to send the message.\n
        messageType - The type of message being sent. (Bug, Error, Feedback).\n
        message - The message to send.\n
        """

        # Check for not enough parameters
        if len(parameters) < self._sendBug.getMinParameters():
            embed = getErrorMessage(self._sendBug, Misc.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            messageType = parameters[0]
            msg = " ".join(parameters[1:])

            # Get color and message type for Embed Title
            messageTypeParameters = self._sendBug.getAcceptedParameters("messageType")
            matched = False

            # Iterate through accepted parameters
            for accepted in messageTypeParameters:

                # Message type was an alternative of the accepted parameter
                if messageType in messageTypeParameters[accepted].getAlternatives():

                    # Capitalize message type; Get the embed color; Parameter matched message type
                    messageType = accepted.capitalize()
                    color = Misc.BUG_EMBED_COLORS[messageType]
                    matched = True
                    
                    # We don't need to continue looping
                    break

            # Invalid message type
            if not matched:
                embed = getErrorMessage(self._sendBug, Misc.INVALID_PARAMETER)

            # Valid message type
            else:

                # Setup embed
                embed = discord.Embed(
                    title = messageType,
                    description = "Author: {}#{}\n{}\n".format(
                        message.author.name,
                        message.author.discriminator,
                        msg
                    ),
                    colour = color
                )

                # Server is not None
                if message.guild != None:
                    embed.add_field(
                        name = "Server Information",
                        value = "Name: {}\nID: {}\n".format(
                            message.guild.name,
                            message.guild.id
                        ),
                        inline = False
                    )
                
                else:
                    embed.add_field(
                        name = "Did Not Originate From Server.",
                        value = "Originated From User",
                        inline = False
                    )
                
                # Iterate through Omega Psi moderators
                for moderator in OmegaPsi.getModerators():

                    # Get the user
                    user = self.client.get_user(moderator)

                    # Only send message to user if user is not None
                    if user != None:
                        await user.send(
                            embed = embed
                        )
                
                embed = discord.Embed(
                    title = "Message Sent",
                    description = "Your `{}` report was sent.\nMessage: {}\n".format(
                        messageType, message
                    ),
                    colour = color
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
        """Parses a message and runs a Miscellaneous Category command if it can.\n

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
    client.add_cog(Misc(client))
