from util.file.omegaPsi import OmegaPsi
from util.file.server import Server
from util.utils import sendMessage, getErrorMessage, loadImageFromUrl, timestampToDatetime

from datetime import datetime
from supercog import Category, Command
import discord, os, pygame, random, requests

pygame.init()

class Misc(Category):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    EMBED_COLOR = 0x00FF80

    BUG_EMBED_COLORS = {
        "Bug": 0xFF0000,
        "Error": 0xFF00FF,
        "Feedback": 0x00FFFF,
        "Moderator": 0xAA0000
    }

    ADVICE_URL = "https://api.adviceslip.com/advice"
    CHUCK_NORRIS_URL = "https://api.chucknorris.io/jokes/random"
    NUMBER_FACT_URL = "http://numbersapi.com/random/year?json"
    TRONALD_DUMP_QUOTE = "https://api.tronalddump.io/random/quote"
    TRONALD_DUMP_MEME = "https://api.tronalddump.io/random/meme"

    TWITTER_ICON = "http://pngimg.com/uploads/twitter/twitter_PNG29.png"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Errors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    NOT_A_NUMBER = "NOT_A_NUMBER"
    END_LESS_THAN_START = "END_LESS_THAN_START"
    NO_ACCESS = "NO_ACCESS"
    TOO_LONG = "TOO_LONG"

    INVALID_MEMBER = "INVALID_MEMBER"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Constructor
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, client):
        super().__init__(
            client, 
            "Miscellaneous",
            description = "Other commands that don't really fit into a category yet.",
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
            }
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
            }
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
            }
        })

        self._numberFacts = Command(commandDict = {
            "alternatives": ["numberFact", "number"],
            "info": "Gives you a fact about a number.",
            "errors": {
                Misc.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get a fact about a random number, you don't need any parameters."
                    ]
                }
            }
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
            }
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
            }
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
            }
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
            }
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
            }
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
            }
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
            }
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
            }
        })

        self.setCommands([
            self._advice,
            self._choice,
            self._chuckNorris,
            self._numberFacts,
            self._random,
            self._tronaldDumpMeme,
            self._tronaldDumpQuote,

            self._info,
            self._invite,
            self._sendBug,
            self._ping,
            self._nickname
        ])
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def advice(self, parameters):
        """Returns a random piece of advice.

        Parameters:
            parameters (list): The parameters given to the command.
        """

        # Check for too many parameters
        if len(parameters) > self._advice.getMaxParameters():
            return getErrorMessage(self._advice, Misc.TOO_MANY_PARAMETERS)
        
        # Get the advice
        adviceJson = requests.get(Misc.ADVICE_URL).json()

        return discord.Embed(
            title = "Advice Number {}".format(adviceJson["slip"]["slip_id"]),
            description = adviceJson["slip"]["advice"],
            colour = Misc.EMBED_COLOR,
            timestamp = datetime.now()
        ).set_footer(
            text = "Advice Slip API"
        )
    
    def randomChoice(self, parameters):
        """Returns a random choice from a list of choices.

        Parameters:
            choices (list): The list of choices to choose from.
        """

        # There is only 1 choice
        if len(parameters) < 2:
            return getErrorMessage(self._choice, Misc.NOT_ENOUGH_PARAMETERS)
        
        # Choose random option
        choice = random.choice(parameters)
        return discord.Embed(
            title = "Result",
            description = choice,
            colour = Misc.EMBED_COLOR
        )
    
    def chuckNorris(self, parameters):
        """Returns a random chuck norris fact.

        Parameters:
            parameters (list): The parameters given to the command.
        """

        # Check for too many parameters
        if len(parameters) > self._chuckNorris.getMaxParameters():
            return getErrorMessage(self._chuckNorris, Misc.TOO_MANY_PARAMETERS)
        
        # Get the joke; and URL
        chuckNorrisJson = requests.get(Misc.CHUCK_NORRIS_URL).json()

        return discord.Embed(
            name = "Chuck Norris",
            description = chuckNorrisJson["value"],
            colour = Misc.EMBED_COLOR,
            timestamp = datetime.now()
        ).set_author(
            name = "Chuck Norris Joke",
            icon_url = chuckNorrisJson["icon_url"]
        ).set_footer(
            text = "Chuck Norris API"
        )
    
    def numberFacts(self, parameters):
        """Returns a fact about a random number.

        Parameters:
            parameters (list): The list of choices to choose from.
        """

        # Check for too many parameters
        if len(parameters) > self._numberFacts.getMaxParameters():
            return getErrorMessage(self._numberFacts, Misc.TOO_MANY_PARAMETERS)
        
        # Get the number fact
        numberFactJson = requests.get(Misc.NUMBER_FACT_URL).json()

        return discord.Embed(
            title = "Fact about the number *{}*".format(numberFactJson["number"]),
            description = numberFactJson["text"],
            colour = Misc.EMBED_COLOR,
            timestamp = datetime.now()
        ).set_footer(
            text = "NumbersAPI"
        )

    def randomNumber(self, parameters):
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
            return getErrorMessage(self._random, Misc.TOO_MANY_PARAMETERS)
        
        # Check for 2 parameters
        if len(parameters) == 2:
            start = parameters[0]
            end = parameters[1]
        
        # Check if start or end are not numbers
        if not str(start).isdigit() or not str(end).isdigit():
            return getErrorMessage(self._random, Misc.NOT_A_NUMBER)
        
        # Start and end were numbers
        start = int(start)
        end = int(end)
        
        # Check if end is less than start
        if end < start:
            return getErrorMessage(self._random, Misc.END_LESS_THAN_START)
        
        # Choose random number
        number = random.randint(start, end)
        return discord.Embed(
            title = "Result",
            description = str(number),
            colour = Misc.EMBED_COLOR
        )
    
    def tronaldDumpMeme(self, parameters):
        """Returns a random Tronald Dump meme.

        Parameters:
            parameters (list): The parameters given to the command.
        """
    
        # Check for too many parameters
        if len(parameters) > self._tronaldDumpMeme.getMaxParameters():
            return getErrorMessage(self._tronaldDumpMeme, Misc.TOO_MANY_PARAMETERS)
        
        # Get the meme
        meme = loadImageFromUrl(Misc.TRONALD_DUMP_MEME)

        # Temporarily save the image
        current = datetime.now()
        image = "TRONALD_DUMP_MEME_{}_{}_{}.png".format(
            current.hour, current.minute, current.second
        )
        pygame.image.save(meme, image)
        return image
    
    def tronaldDumpQuote(self, parameters):
        """Returns a random Tronald Dump quote.

        Parameters:
            parameters (list): The parameters given to the command.
        """
        
        # Check for too many parameters
        if len(parameters) > self._tronaldDumpQuote.getMaxParameters():
            return getErrorMessage(self._tronaldDumpQuote, Misc.TOO_MANY_PARAMETERS)
        
        # Get the quote
        quoteJson = requests.get(Misc.TRONALD_DUMP_QUOTE).json()

        return discord.Embed(
            title = "Donald Trump Quote",
            description = quoteJson["value"],
            colour = Misc.EMBED_COLOR,
            timestamp = timestampToDatetime(quoteJson["appeared_at"]),
            url = quoteJson["_embedded"]["source"][0]["url"]
        ).set_author(
            name = quoteJson["_embedded"]["author"][0]["name"],
            icon_url = Misc.TWITTER_ICON
        ).set_footer(
            text = "Tronald Dump API"
        )
    
    def getServerInfo(self, discordServer):
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
            colour = Misc.EMBED_COLOR
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
    
    def getMemberInfo(self, discordServer, discordMember):
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
        memberId = discordMember.id
        memberNickname = discordMember.nick
        memberModerator = Server.isAuthorModerator(discordServer, discordMember)
        memberExperience = member["experience"]
        memberLevel = member["level"]

        # Create embed
        embed = discord.Embed(
            title = memberName + "#" + memberDiscriminator,
            description = "<@{}>".format(
                memberId
            ),
            colour = Misc.EMBED_COLOR
        )

        # Add fields
        tags = {
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
    
    def getInviteLink(self, permissions = []):
        """Returns the link so someone can invite the bot to their own server.\n

        permissions - The permissions that you want the bot to have.\n
        """

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

        return Server.BOT_INVITE.format(permissionsInteger)
    
    async def sendBug(self, discordServer, discordMember, messageType, message):
        """Sends all bot moderators a message from the bot.\n

        discordServer - The Discord Server that the message originated from.\n
        discordMember - The Discord User/Member that wants to send the message.\n
        messageType - The type of message being sent. (Bug, Error, Feedback).\n
        message - The message to send.\n
        """

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
                
                # We don't need to continute looping
                break

        # Invalid message type
        if not matched:
            return getErrorMessage(self._sendBug, Misc.INVALID_PARAMETER)

        # Setup embed
        embed = discord.Embed(
            title = messageType,
            description = "Author: {}\n{}\n".format(
                discordMember.mention,
                message
            ),
            colour = color
        )

        # Server is not None
        if discordServer != None:
            embed.add_field(
                name = "Server Information",
                value = "Name: {}\nID: {}\n".format(
                    discordServer.name,
                    discordServer.id
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
        
        return discord.Embed(
            title = "Message Sent",
            description = "Your `{}` report was sent.\nMessage: {}\n".format(
                messageType, message
            ),
            colour = color
        )
    
    async def nickname(self, discordMember, parameters):
        """Changes the nickname of the specified member.

        Parameters:
            discordMember (discord.Member): The Discord Member to change the nickname of.
            nickname (str): The new nickname to set. (No nickname will clear the nickname).
        """

        # See if there are no parameters
        if len(parameters) == 0:

            # Try to clear it
            try:
                await discordMember.edit(
                    nick = None
                )
                return discord.Embed(
                    title = "Nickname Cleared",
                    description = "Your nickname has been cleared.",
                    colour = Misc.EMBED_COLOR
                )
            
            except discord.Forbidden:
                return getErrorMessage(self._nickname, Misc.NO_ACCESS)
        
        # There are parameters
        try:

            # See if nickname is too long
            if len(" ".join(parameters)) > 32:
                return getErrorMessage(self._nickname, Misc.TOO_LONG)

            await discordMember.edit(
                nick = " ".join(parameters)
            )
            return discord.Embed(
                title = "Nickname Set",
                description = "Your nickname has been set to `{}`".format(" ".join(parameters)),
                colour = Misc.EMBED_COLOR
            )
        
        except discord.Forbidden:
            return getErrorMessage(self._nickname, Misc.NO_ACCESS)
    
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

            # Advice Command
            if command in self._advice.getAlternatives():
                await sendMessage(
                    self.client,
                    message,
                    embed = await self.run(message, self._advice, self.advice, parameters)
                )
            
            # Chuck Norris
            elif command in self._chuckNorris.getAlternatives():
                await sendMessage(
                    self.client,
                    message,
                    embed = await self.run(message, self._chuckNorris, self.chuckNorris, parameters)
                )

            # Choice Command
            elif command in self._choice.getAlternatives():
                await sendMessage(
                    self.client,
                    message,
                    embed = await self.run(message, self._choice, self.randomChoice, parameters)
                )
            
            # Number Facts Command
            elif command in self._numberFacts.getAlternatives():
                await sendMessage(
                    self.client,
                    message,
                    embed = await self.run(message, self._numberFacts, self.numberFacts, parameters)
                )

            # Random Command
            elif command in self._random.getAlternatives():
                await sendMessage(
                    self.client,
                    message,
                    embed = await self.run(message, self._random, self.randomNumber, parameters)
                )

            # Tronald Dump meme Command
            elif command in self._tronaldDumpMeme.getAlternatives():
                result = await self.run(message, self._tronaldDumpMeme, self.tronaldDumpMeme, parameters)

                if type(result) == discord.Embed:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await self.run(message, self._tronaldDumpMeme, self.tronaldDumpMeme, parameters)
                    )
                else:
                    await sendMessage(
                        self.client,
                        message,
                        filename = result
                    )

                    os.remove(result) # Remove temporary image
            
            # Tronald Dump quote Command
            elif command in self._tronaldDumpQuote.getAlternatives():
                await sendMessage(
                    self.client,
                    message,
                    embed = await self.run(message, self._tronaldDumpQuote, self.tronaldDumpQuote, parameters)
                )

            # Info Command
            elif command in self._info.getAlternatives():

                # 0 Parameters Exist (server info)
                if len(parameters) == 0:

                    embed = await self.run(message, self._info, self.getServerInfo, message.guild)

                    await sendMessage(
                        self.client,
                        message,
                        embed = embed
                    )
                
                # 1 Parameter Exists (member info)
                elif len(parameters) == 1:

                    # See if member was mentioned or just the text
                    if len(message.mentions) == 0:
                        embed = await self.run(message, self._info, self.getMemberInfo, message.guild, username = parameters[0])
                    else:
                        embed = await self.run(message, self._info, self.getMemberInfo, message.guild, discordMember = message.mentions[0])

                    await sendMessage(
                        self.client,
                        message,
                        embed = embed
                    )

                # 2 or More Parameters Exist (TOO_MANY_PARAMETERS)
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._info, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Invite Link
            elif command in self._invite.getAlternatives():

                await sendMessage(
                    self.client,
                    message,
                    message = await self.run(message, self._invite, self.getInviteLink, parameters)
                )
            
            # Send Bug
            elif command in self._sendBug.getAlternatives():

                # Less than 2 Parameters Exist
                if len(parameters) < 2:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._sendBug, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 2 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await self.run(message, self._sendBug, self.sendBug, message.guild, message.author, parameters[0], " ".join(parameters[1:]))
                    )
            
            # Ping
            elif command in self._ping.getAlternatives():

                # 0 Parameters Exist
                if len(parameters) == 0:

                    # Get start time
                    start = datetime.now()

                    # Send message
                    tempMessage = await message.channel.send("Pong :)")

                    # Get end time
                    end = datetime.now()

                    # Edit message
                    await tempMessage.edit(
                        content = "Pong :) `{} ms`".format(
                            int((end - start).total_seconds() * 1000)
                        )
                    )
                
                # 1 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._ping, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Nickname
            elif command in self._nickname.getAlternatives():
                await sendMessage(
                    self.client,
                    message,
                    embed = await self.run(message, self._nickname, self.nickname, message.author, parameters)
                )

def setup(client):
    client.add_cog(Misc(client))
