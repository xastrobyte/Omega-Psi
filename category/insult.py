from util.file.database import omegaPsi
from util.file.omegaPsi import OmegaPsi
from util.file.server import Server
from util.utils.discordUtils import sendMessage, getErrorMessage

from random import choice as choose

from datetime import datetime
from supercog import Category, Command
import discord

scrollEmbeds = {}

class Insult(Category):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Errors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    USER_NOT_CONNECTED = "USER_NOT_CONNECTED"

    INVALID_INSULT_LEVEL = "INVALID_INSULT_LEVEL"
    INVALID_TAG = "INVALID_TAG"
    INVALID_RANGE = "INVALID_RANGE"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Constructor
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, client):
        super().__init__(
            client, 
            "Insult",
            description = "If you feel in the mood to be insulted, here ya are.",
            embed_color = 0x800000,
            locally_inactive_error = Server.getInactiveError,
            globally_inactive_error = OmegaPsi.getInactiveError,
            locally_active_check = Server.isCommandActive,
            globally_active_check = OmegaPsi.isCommandActive
        )

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Commands
        self._insult = Command(commandDict = {
            "alternatives": ["insult", "i"],
            "info": "Sends you an insult.",
            "parameters": {
                "insultLevel": {
                    "optional": True,
                    "info": "The level of insult to send.",
                    "accepted_parameters": {
                        "touchy": {
                            "alternatives": ["touchy", "t"],
                            "info": "Soft insults for a soft person.",
                        },
                        "remorseful": {
                            "alternatives": ["remorseful", "remorse", "r"],
                            "info": "Harder insults. Might offend you."
                        },
                        "noRemorse": {
                            "alternatives": ["noRemorse", "noremorse", "nr"],
                            "info": "Hardcore insults. And I mean it."
                        }
                    }
                }
            },
            "errors": {
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "Whoa man. The insult command doesn't take more than a single parameter."
                    ]
                },
                Insult.INVALID_INSULT_LEVEL: {
                    "messages": [
                        "That is not a valid insult level. Try `{}help insult` to see the insult levels.".format(OmegaPsi.PREFIX)
                    ]
                }
            },
            "command": self.insult
        })

        self._add = Command(commandDict = {
            "alternatives": ["addInsult", "addI"],
            "info": "Allows you to add your own insult.",
            "parameters": {
                "insultLevel": {
                    "info": "The level of insult to add.",
                    "optional": False,
                    "accepted_parameters": {
                        "touchy": {
                            "alternatives": ["touchy", "t"],
                            "info": "Soft insults for a soft person.",
                        },
                        "remorseful": {
                            "alternatives": ["remorseful", "remorse", "r"],
                            "info": "Harder insults. Might offend you."
                        },
                        "noRemorse": {
                            "alternatives": ["noRemorse", "noremorse", "nr"],
                            "info": "Hardcore insults. And I mean it."
                        }
                    }
                },
                "insult": {
                    "info": "The insult to add.",
                    "optional": False
                },
                "tags": {
                    "info": "Any tags that apply to the insult.",
                    "optional": True,
                    "accepted": {
                        "NSFW": {
                            "alternatives": ["NSFW", "nsfw", "18+"],
                            "info": "Make the insult an NSFW insult."
                        }
                    }
                }
            },
            "errors": {
                Insult.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "If only you had enough parameters, you could actually add your own insult.",
                        "In order to add an insult, you need the insult level, the insult (wrapped in quotes), and any tags that may apply to the insult (also wrapped in quotes)."
                    ]
                },
                Insult.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "Whoa man. The add insult command doesn't take more than 3 parameters."
                    ]
                },
                Insult.INVALID_INSULT_LEVEL: {
                    "messages": [
                        "That is not a valid insult level. Try `{}help addInsult` to see the insult levels.".format(OmegaPsi.PREFIX)
                    ]
                },
                Insult.INVALID_TAG: {
                    "messages": [
                        "You have an invalid tag in there somewhere."
                    ]
                }
            },
            "command": self.addInsult
        })

        self._list = Command(commandDict = {
            "alternatives": ["listInsults", "list", "l"],
            "info": "Lists the insults that can be sent.",
            "parameters": {
                "insultLevel": {
                    "optional": True,
                    "info": "The level of insult to send.",
                    "accepted_parameters": {
                        "touchy": {
                            "alternatives": ["touchy", "t"],
                            "info": "Soft insults for a soft person.",
                        },
                        "remorseful": {
                            "alternatives": ["remorseful", "remorse", "r"],
                            "info": "Harder insults. Might offend you."
                        },
                        "noRemorse": {
                            "alternatives": ["noRemorse", "noremorse", "nr"],
                            "info": "Hardcore insults. And I mean it."
                        }
                    }
                }
            },
            "errors": {
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "Whoa man. The list command doesn't take more than a single parameter."
                    ]
                },
                Insult.INVALID_INSULT_LEVEL: {
                    "messages": [
                        "That is not a valid insult level. Try `!help listInsults` to see the insult levels."
                    ]
                }
            },
            "command": self.listInsults
        })

        self._approveInsult = Command(commandDict = {
            "alternatives": ["approveInsult", "approve"],
            "info": "Approves an insult in the list of pending insults.",
            "bot_moderator_only": True,
            "parameters": {
                "value": {
                    "info": "The number of the insult to approve.",
                    "optional": False
                }
            },
            "errors": {
                Insult.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to approve an insult, you need the number of the insult to approve."
                    ]
                },
                Insult.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You only need the number of the insult to approve."
                    ]
                },
                Insult.INVALID_RANGE: {
                    "messages": [
                        "That index is out of range."
                    ]
                },
                Insult.INVALID_PARAMETER: {
                    "messages": [
                        "That index is not a number."
                    ]
                },
                Insult.USER_NOT_CONNECTED: {
                    "messages": [
                        "The user no longer has access to the bot."
                    ]
                }
            },
            "command": self.approveInsult
        })

        self._denyInsult = Command(commandDict = {
            "alternatives": ["denyInsult", "deny"],
            "info": "Denies an insult in the list of pending insults.",
            "bot_moderator_only": True,
            "parameters": {
                "value": {
                    "info": "The number of the insult to deny.",
                    "optional": False
                },
                "reason": {
                    "info": "The reason the insult was denied.",
                    "optional": False
                }
            },
            "errors": {
                Insult.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to deny an insult, you need the number of the insult to deny and the reason for its denial."
                    ]
                },
                Insult.INVALID_PARAMETER: {
                    "messages": [
                        "That index is not a number."
                    ]
                },
                Insult.INVALID_RANGE: {
                    "messages": [
                        "That index is out of range."
                    ]
                },
                Insult.USER_NOT_CONNECTED: {
                    "messages": [
                        "The user no longer has access to the bot."
                    ]
                }
            },
            "command": self.denyInsult
        })

        self._addInsultTag = Command(commandDict = {
            "alternatives": ["addInsultTag", "addTag"],
            "info": "Adds a tag to an insult if it is not already there.",
            "bot_moderator_only": True,
            "parameters": {
                "value": {
                    "info": "The number of the insult to add the tag to.",
                    "optional": False
                },
                "tag": {
                    "info": "The tag to add to the insult.",
                    "optional": False,
                    "accepted": {
                        "NSFW": {
                            "alternatives": ["NSFW", "nsfw"],
                            "info": "An NSFW tag for an insult."
                        }
                    }
                }
            },
            "errors": {
                Insult.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to add a tag to an insult, you need the number of the insult to add it to and the tag."
                    ]
                },
                Insult.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You only need the number of the insult to add the tag to and the tag."
                    ]
                },
                Insult.INVALID_TAG: {
                    "messages": [
                        "The tag you entered is not valid."
                    ]
                }
            },
            "command": self.addInsultTag
        })

        self._listPendingInsults = Command(commandDict = {
            "alternatives": ["listPendingInsults", "pendingInsults"],
            "info": "Lists the pending insults.",
            "bot_moderator_only": True,
            "errors": {
                Insult.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You don't need any parameters to list the pending insults."
                    ]
                }
            },
            "command": self.listPendingInsults
        })

        self._insultLevelNames = ["touchy", "remorseful", "noRemorse"]
        self._insultLevels = (
            self._insult.getParameter("insultLevel").getAcceptedParameter("touchy").getAlternatives() +
            self._insult.getParameter("insultLevel").getAcceptedParameter("remorseful").getAlternatives() +
            self._insult.getParameter("insultLevel").getAcceptedParameter("noRemorse").getAlternatives()
        )

        self.setCommands([
            self._insult,
            self._add,
            self._list,

            self._approveInsult,
            self._denyInsult,
            self._addInsultTag,
            self._listPendingInsults
        ])
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def insult(self, message, parameters):
        """Returns a random insult from the specified insult level or from any insult level.\n

        Keyword Arguments:\n
         - insultLevel - The level of insult to get.\n
         - isNSFW - Whether or not to allow an NSFW insult.\n
        """

        try:
            isNSFW = message.channel.is_nsfw()
        except:
            isNSFW = True

        # Check for too many parameters
        if len(parameters) > self._insult.getMaxParameters():
            embed = getErrorMessage(self._insult, Insult.TOO_MANY_PARAMETERS)

        # There were the proper amount of parameters
        else:

            insultLevel = None if len(parameters) == 0 else " ".join(parameters)
            valid = False

            # Check if insult level is None; Generate random insult level
            if insultLevel == None:
                insultLevel = choose(self._insultLevelNames)
            
            # Check if insult level is touchy
            if insultLevel in self._insult.getAcceptedParameter("insultLevel", "touchy").getAlternatives():
                insultLevel = "touchy"
                valid = True
            
            # Check if insult level is remorseful
            elif insultLevel in self._insult.getAcceptedParameter("insultLevel", "remorseful").getAlternatives():
                insultLevel = "remorseful"
                valid = True
            
            # Check if insult level is noRemorse
            elif insultLevel in self._insult.getAcceptedParameter("insultLevel", "noRemorse").getAlternatives():
                insultLevel = "noremorse"
                valid = True
            
            # Insult level was invalid
            else:
                embed = getErrorMessage(self._insult, Insult.INVALID_INSULT_LEVEL)
                valid = False
            
            # Only find insult if level is valid
            if valid:

                # Load insults file for insult level
                insults = await omegaPsi.getInsults()
                insults = insults[insultLevel]

                # Choose insult
                target = choose(insults)

                # Regenerate as long as isNSFW is False and result is NSFW
                while not isNSFW and "NSFW" in target["tags"]:
                    target = choose(insults)
                
                embed = discord.Embed(
                    name = "Result",
                    description = target["value"],
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
    
    async def addInsult(self, message, parameters):
        """Adds the specified insult to the specified insult level.\n

        insultLevel - The level of the insult to add to.\n
        insult - The insult to add.\n
        """

        # Check for not enough parameters
        if len(parameters) < self._add.getMinParameters():
            embed = getErrorMessage(self._add, Insult.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._add.getMaxParameters():
            embed = getErrorMessage(self._add, Insult.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            insultLevel = parameters[0]
            insult = parameters[1]
            tags = "" if len(parameters) < 3 else parameters[2]

            # Check if the insult level is touchy
            if insultLevel in self._add.getAcceptedParameter("insultLevel", "touchy").getAlternatives():
                insultLevel = "touchy"
                valid = True
            
            # Check if the insult level is remorseful
            elif insultLevel in self._add.getAcceptedParameter("insultLevel", "remorseful").getAlternatives():
                insultLevel = "remorseful"
                valid = True
            
            # Check if the insult level is noRemorse
            elif insultLevel in self._add.getAcceptedParameter("insultLevel", "noRemorse").getAlternatives():
                insultLevel = "noremorse"
                valid = True
            
            # Insult level is invalid
            else:
                embed = getErrorMessage(self._add, Insult.INVALID_INSULT_LEVEL)
                valid = False
            
            # Make sure insult level was valid
            if valid:
            
                # Check if all the tags are valid
                if len(tags) != 0:
                    tags = tags.split(" ")
                else:
                    tags = []

                # Iterate through tags
                validTag = False
                for tag in range(len(tags)):
                    tagName = tags[tag]
                    acceptedParameters = self._add.getAcceptedParameters("tags")

                    # Iterate through accepted parameters
                    validTag = False
                    for accepted in acceptedParameters:
                        if tagName in acceptedParameters[accepted].getAlternatives():
                            tags[tag] = acceptedParameters[accepted].getAlternatives()[0]
                            validTag = True
                            break
                    
                    if not validTag:
                        break
                
                # See if the tags were valid
                if validTag or len(tags) == 0:

                    # Directly add to list if author is a bot moderator
                    if await OmegaPsi.isAuthorModerator(message.author):
                        await omegaPsi.addInsult(insultLevel, insult, tags)

                        embed = discord.Embed(
                            title = "Insult Added.",
                            description = (
                                "The insult was added.\n" +
                                "Insult: `{}`\n" +
                                "Level: `{}`\n" +
                                "Tags: `{}`\n"
                            ).format(insult, insultLevel, ", ".join(tags) if len(tags) > 0 else "No Tags"),
                            colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                        )
                    
                    # Add to pending list and send to bot moderators
                    else:
                        await omegaPsi.addPendingInsult(message.author, insultLevel, insult, tags)

                        # Send message to all bot moderators
                        for moderator in await OmegaPsi.getModerators():
                            mod = self.client.get_user(int(moderator))
                            await mod.send(
                                embed = discord.Embed(
                                    title = "Insult Addition Requested.",
                                    description = (
                                        "Insult: `{}`\n" +
                                        "Level: `{}`\n" +
                                        "Tags: `{}`"
                                    ).format(insult, insultLevel, ", ".join(tags) if len(tags) > 0 else "No Tags"),
                                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color,
                                    timestamp = datetime.now()
                                ).set_footer(
                                    text = "Requested by {}#{}".format(
                                        message.author.name,
                                        message.author.discriminator
                                    ),
                                    icon_url = message.author.avatar_url
                                )
                            )
                        
                        embed = discord.Embed(
                            title = "Insult Pending.",
                            description = (
                                "Your insult is waiting to be approved.\n" + 
                                "You will receive a message if your insult is added or not.\n" +
                                "Any tags that you may have missed will be added if it applies to your command.\n" + 
                                "Insult: `{}`\n" +
                                "Level: `{}`\n" +
                                "Tags :`{}`\n"
                            ).format(insult, insultLevel, ", ".join(tags) if len(tags) > 0 else "No Tags"),
                            colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                        )
                
                # Tag was invalid
                else:
                    embed = getErrorMessage(self._add, Insult.INVALID_TAG)
        
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
    
    async def listInsults(self, message, parameters, *, recursive = False):
        """Returns a list of insults that can be sent.\n

        Keyword Arguments:\n
         - insultLevel - The level of insult to return a list of insults from.\n
         - recursive = Whether or not the insults are being added to a list rather than returned in an embed.\n
        """

        # Get is NSFW
        try:
            isNSFW = message.channel.is_nsfw()
        except:
            isNSFW = True

        # Check for too many parameters
        if len(parameters) > self._list.getMaxParameters():
            embed = getErrorMessage(self._list, Insult.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # No parameters, list all insults
            if len(parameters) == 0:
                insultLevel = None
            else:
                insultLevel = parameters[0]

            # Check if insult level is None; Add each insult level
            if insultLevel == None:

                # Setup insults embed
                embed = discord.Embed(
                    title = "Insults",
                    description = "A list of insults that can be sent.",
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )

                # Add each insult level
                for level in self._insultLevelNames:

                    # Field list comes from recursive definition
                    fields = await self.listInsults(message, [level], recursive = True)

                    # Add each field
                    count = 0
                    for field in fields:
                        count += 1
                        embed.add_field(
                            name = "{} Insults {}".format(
                                level,
                                "({} / {})".format(
                                    count, len(fields)
                                ) if len(fields) > 1 else ""
                            ),
                            value = field
                        )
            
            # Check if insult level is a valid insult level
            elif insultLevel in self._insultLevels:

                # Change insult level into something readable
                if insultLevel in self._list.getAcceptedParameter("insultLevel", "touchy").getAlternatives():
                    insultLevel = "touchy"
                
                elif insultLevel in self._list.getAcceptedParameter("insultLevel", "remorseful").getAlternatives():
                    insultLevel = "remorseful"

                elif insultLevel in self._list.getAcceptedParameter("insultLevel", "noRemorse").getAlternatives():
                    insultLevel = "noremorse"
                
                # Open insult file
                insults = await omegaPsi.getInsults()
                insults = insults[insultLevel]

                # Setup insults text
                insultsFields = []
                insultsText = ""
                bolden = True

                # Iterate through insults
                for insult in insults:
                    tagList = insult["tags"]
                    tags = " ".join(["**_`{}`_**".format(tag) for tag in insult["tags"]])

                    # Only add if tag is NSFW and channel isNSFW
                    addInsult = True
                    if not isNSFW:
                        if "NSFW" in tagList:
                            addInsult = False
                        else:
                            addInsult = True

                    if addInsult:
                        if bolden:
                            insult = "{} **{}**".format(tags, insult["value"])
                        else:
                            insult = "{} {}".format(tags, insult["value"])
                        bolden = not bolden

                        # Add newline to insult if there is no newline
                        if not insult.endswith("\n"):
                            insult += "\n"
                        
                        # Check if adding insult will exceed message threshold
                        if len(insultsText) + len(insult) >= OmegaPsi.MESSAGE_THRESHOLD:
                            insultsFields.append(insultsText)
                            insultsText = ""
                        
                        insultsText += insult
                
                if len(insultsText) > 0:
                    insultsFields.append(insultsText)
                
                # Return fields if recursive
                if recursive:
                    return insultsFields
                
                # Return embed if not recursive
                else:

                    # Setup embed and add fields
                    embed = discord.Embed(
                        title = "{} Insults".format(insultLevel),
                        description = "A list of insults in the {} category.\n".format(insultLevel),
                        colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                    )

                    count = 0
                    for field in insultsFields:
                        count += 1
                        embed.add_field(
                            name = "{} Insults {}".format(
                                insultLevel,
                                "({} / {})".format(
                                    count, len(fields)
                                ) if len(fields) > 1 else ""
                            ),
                            value = field
                        )
            
            # Insult level is invalid
            else:
                embed = getErrorMessage(self._list, Insult.INVALID_INSULT_LEVEL)
        
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

    async def approveInsult(self, message, parameters):
        """Approves the insult given and sends a message to the requester.
        """
        
        # Check for not enough parameters
        if len(parameters) < self._approveInsult.getMinParameters():
            embed = getErrorMessage(self._approveInsult, Insult.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._approveInsult.getMaxParameters():
            embed = getErrorMessage(self._approveInsult, Insult.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Get the value of the insult number
            try:
                value = int(parameters[0]) - 1

                # Get the pending insults
                pendingInsults = await omegaPsi.getPendingInsults()["pending_insults"]

                # See if value is within range of pending insults
                if value >= 0 and value < len(pendingInsults):
                    insult = pendingInsults[value]

                    # Get insult addition requester
                    user = self.client.get_user(int(insult["user"]))

                    # Check if user is not None
                    if user != None:

                        # Add insult to bot
                        await omegaPsi.addInsult(insult["level"], insult["insult"], insult["tags"])

                        # Message user saying that it's been added
                        await user.send(
                            embed = discord.Embed(
                                title = "Your Insult Was Approved.",
                                description = (
                                    "The insult you requested to add\n" +
                                    "```diff\n" +
                                    "+ {}\n" +
                                    "```\n" +
                                    "was added to the bot. Thanks!"
                                ).format(insult["insult"]),
                                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color,
                                timestamp = datetime.now()
                            ).set_footer(
                                text = "Approved by {}#{}".format(
                                    message.author.name,
                                    message.author.discriminator
                                ),
                                icon_url = message.author.avatar_url
                            )
                        )
                    
                    # User is None
                    else:
                        embed = getErrorMessage(self._approveInsult, Insult.USER_NOT_CONNECTED)
                
                # Value was out of range
                else:
                    embed = getErrorMessage(self._approveInsult, Insult.INVALID_RANGE)
            
            # Value was not an integer
            except:
                embed = getErrorMessage(self._approveInsult, Insult.INVALID_PARAMETER)
        
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
    
    async def denyInsult(self, message, parameters):
        """Denies the insult given and sends a message to the requester.
        """
        
        # Check for not enough parameters
        if len(parameters) < self._denyInsult.getMinParameters():
            embed = getErrorMessage(self._denyInsult, Insult.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._denyInsult.getMaxParameters():
            embed = getErrorMessage(self._denyInsult, Insult.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Get the value of the insult number
            try:
                value = int(parameters[0]) - 1
                reason = " ".join(parameters[1:])

                # Get the pending insults
                pendingInsults = await omegaPsi.getPendingInsults()["pending_insults"]

                # See if value is within range of pending insults
                if value >= 0 and value < len(pendingInsults):
                    insult = pendingInsults[value]

                    # Get insult addition requester
                    user = self.client.get_user(int(insult["user"]))

                    # Only send message if user is not None
                    if user != None:

                        # Message user saying that it's been added
                        await user.send(
                            embed = discord.Embed(
                                title = "Your Insult Was Denied.",
                                description = (
                                    "The insult you requested to add\n" +
                                    "```diff\n" +
                                    "- {}\n" +
                                    "```\n" +
                                    "was not added to the bot.\n" +
                                    "Reason: `{}`\n"
                                ).format(
                                    insult["value"], reason
                                ),
                                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color,
                                timestamp = datetime.now()
                            ).set_footer(
                                text = "Denied by {}#{}".format(
                                    message.author.name,
                                    message.author.discriminator
                                ),
                                icon_url = message.author.avatar_url
                            )
                        )

                    await omegaPsi.removePendingInsult(value)

                    embed = discord.Embed(
                        title = "Insult Denied.",
                        description = "The insult was denied.",
                        colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color,
                        timestamp = datetime.now()
                    )
                
                # Value was out of range
                else:
                    embed = getErrorMessage(self._denyInsult, Insult.INVALID_RANGE)
            
            # Value was not an integer
            except Exception as e:
                print(e)
                embed = getErrorMessage(self._denyInsult, Insult.INVALID_PARAMETER)
        
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
    
    async def addInsultTag(self, message, parameters):
        """Adds a tag to the pending insult.
        """
        
        # Check for not enough parameters
        if len(parameters) < self._addInsultTag.getMinParameters():
            embed = getErrorMessage(self._addInsultTag, Insult.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._addInsultTag.getMaxParameters():
            embed = getErrorMessage(self._addInsultTag, Insult.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Get the value of the insult number to add the tag to
            try:
                value = int(parameters[0]) - 1
                tag = parameters[1]

                # Get the pending insults
                pendingInsults = await omegaPsi.getPendingInsults()["pending_insults"]

                # See if value is within range of pending results
                if value >= 0 and value < len(pendingInsults):
                    insult = pendingInsults[value]

                    # Make sure tag is valid
                    acceptedTags = self._addInsultTag.getAcceptedParameters("tags")

                    validTag = True
                    for acceptedTag in acceptedTags:
                        if not tag in acceptedTags[acceptedTag].getAlternatives():
                            validTag = False
                            break
                    
                    # Tag is valid
                    if validTag:

                        # Add insult tag and update insult
                        insult["addedTags"].append(tag)
                        await omegaPsi.setPendingInsult(value, pendingInsults)

                        embed = discord.Embed(
                            title = "Tag Added.",
                            description = "`{}` was added to the insult `{}`".format(
                                tag, insult
                            ),
                            colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                        )
                    
                    # Tag is not valid
                    else:
                        embed = getErrorMessage(self._addInsultTag, Insult.INVALID_TAG)
                
                # Value is not within range
                else:
                    embed = getErrorMessage(self._addInsultTag, Insult.INVALID_RANGE)
            
            # Value is not a number
            except:
                embed = getErrorMessage(self._addInsultTag, Insult.INVALID_PARAMETER)
        
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
    
    async def listPendingInsults(self, message, parameters):
        """Lists the pending insults.
        """

        # Check for not enough parameters
        if len(parameters) < self._listPendingInsults.getMinParameters():
            embed = getErrorMessage(self._listPendingInsults, Insult.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._listPendingInsults.getMaxParameters():
            embed = getErrorMessage(self._listPendingInsults, Insult.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Iterate through pending insults
            pendingInsults = await omegaPsi.getPendingInsults()["pending_insults"]
            fields = []
            fieldText = ""

            for pendingInsult in pendingInsults:

                # Get insult addition requester
                user = self.client.get_user(int(pendingInsult["user"]))

                pendingInsultsText = (
                    "Insult: `{}`\n" +
                    "Level: `{}`\n" +
                    "Tags: `{}`\n" +
                    "Requested by {}#{}\n\n"
                ).format(
                    pendingInsult["value"],
                    pendingInsult["level"],
                    ", ".join(pendingInsult["tags"]) if len(pendingInsult["tags"]) > 0 else "No Tags",
                    user.name, user.discriminator
                )

                if len(fieldText) + len(pendingInsultsText) >= OmegaPsi.MESSAGE_THRESHOLD:
                    fields.append(fieldText)
                    fieldText = ""
                
                fieldText += pendingInsultsText
            
            if len(fieldText) > 0:
                fields.append(fieldText)

            embed = discord.Embed(
                title = "Pending Insults.",
                description = "There {} {} pending insult{}.".format(
                    "is" if len(pendingInsults) == 1 else "are",
                    "no" if len(pendingInsults) == 0 else len(pendingInsults),
                    "" if len(pendingInsults) == 1 else "s"
                ),
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color,
                timestamp = datetime.now()
            )
            
            count = 0
            for field in fields:
                count += 1
                embed.add_field(
                    name = "Pending Insults {}".format(
                        "({} / {})".format(
                            count, len(fields)
                        ) if len(fields) > 1 else ""
                    ),
                    value = field,
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

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Parsing
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def on_message(self, message):
        """Parses a message and runs an Insult Category command if it can.\n

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

def setup(client):
    client.add_cog(Insult(client))