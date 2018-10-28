from category.category import Category
from category.code import Code
from cateogry.game import Game
from category.gif import Gif
from category.insult import Insult
from category.math import Math
from category.rank import Rank
from category.weather import Weather

from util.command.command import Command
from util.file.omegaPsi import OmegaPsi
from util.file.server import Server
from util.utils import sendMessage

import discord

class BotModerator(Category):

    EMBED_COLOR = 0xA456B0

    def __init__(self, client):
        super().__init__(client, "Bot Moderator")

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Commands
        self._addModerator = Command({
            "alternatives": ["addBotModerator", "addBotMod", "abm"],
            "info": "Allows you to add a bot moderator to the bot.",
            "bot_moderator_only": True,
            "parameters": {
                "member(s)...": {
                    "info": "The member(s) to add as a bot moderator.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to add a bot moderator, you need to mention them."
                    ]
                }
            }
        })

        self._removeModerator = Command({
            "alternatives": ["removeBotModerator", "removeBotMod", "remBotMod", "rbm"],
            "info": "Allows you to remove a bot moderator from the bot.",
            "bot_moderator_only": True,
            "parameters": {
                "member(s)...": {
                    "info": "The member(s) to remove as a bot moderator.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to remove a bot moderator, you need to mention them."
                    ]
                }
            }
        })

        self._activate = Command({
            "alternatives": ["activateGlobally", "enableGlobally"],
            "info": "Allows you to activate a command, or commands, globally.",
            "bot_moderator_only": True,
            "parameters": {
                "command(s)": {
                    "info": "The command(s) to activate globally.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to activate a command globally, you need to type it in."
                    ]
                },
                Category.INVALID_COMMAND: {
                    "messages": [
                        "That is not a valid command."
                    ]
                }
            }
        })

        self._deactivate = Command({
            "alternatives": ["deactivateGlobally", "disableGlobally"],
            "info": "Allows you to deactivate a command globally.",
            "bot_moderator_only": True,
            "parameters": {
                "command": {
                    "info": "The command to deactivate globally.",
                    "optional": False
                },
                "reason": {
                    "info": "The reason the command is being deactivated globally.",
                    "optional": True
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to deactivate a command globally, you need to type it in."
                    ]
                },
                Category.INVALID_COMMAND: {
                    "messages": [
                        "That is not a valid command."
                    ]
                },
                Category.CANT_BE_DEACTIVATED: {
                    "messages": [
                        "This command cannot be deactivated."
                    ]
                }
            }
        })

        self._info = Command({
            "alternatives": ["botInfo", "bi"],
            "info": "Allows you to get the info about the bot.",
            "bot_moderator_only": True,
            "errors": {
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get info about the bot, or the servers it's in, you don't need anything else."
                    ]
                }
            }
        })

        self._servers = Command({
            "alternatives": ["servers", "botServers"],
            "info": "Allows you to get a list of servers the bot is in.",
            "bot_moderator_only": True,
            "errors": {
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get a list of servers the bot is in, you don't need any parameters."
                    ]
                }
            }
        })

        self._status = Command({
            "alternatives": ["setStatus", "status"],
            "info": "Allows you to change the presence of the bot.",
            "bot_moderator_only": True,
            "parameters": {
                "activity": {
                    "info": "The activity to set for the presence.",
                    "optional": False,
                    "accepted": {
                        "playing": {
                            "alternatives": ["playing"],
                            "info": "The playing activity type."
                        },
                        "streaming": {
                            "alternatives": ["streaming"],
                            "info": "The streaming activity type."
                        },
                        "listening": {
                            "alternatives": ["listening"],
                            "info": "The listening activity type."
                        },
                        "watching": {
                            "alternatives": ["watching"],
                            "info": "The watching activity type."
                        }
                    }
                },
                "text": {
                    "info": "The text to set as the presence.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to set the status, you need the status type and the text to set."
                    ]
                },
                Category.INVALID_ACTIVITY: {
                    "messages": [
                        "The given activity is not a valid activity."
                    ]
                }
            }
        })
        
        self._kill = Command({
            "alternatives": ["stop", "quit", "kill"],
            "info": "Kills the bot.",
            "bot_moderator_only": True,
            "errors": {
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to kill the bot, you don't need any parameters."
                    ]
                }
            }
        })
    
        self.setCommands([
            self._addModerator,
            self._removeModerator,
            self._activate,
            self._deactivate,
            self._info,
            self._servers,
            self._status,
            self._kill
        ])

        self._categories = {
            "Code": Code(None),
            "Game": Game(None),
            "Gif": Gif(None),
            "Insult": Insult(None),
            "Math": Math(None),
            "Rank": Rank(None),
            "Weather": Weather(None)
        }
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def addModerator(self, members):
        """Adds bot moderators to the bot.\n

        members - The Discord Users to add as a bot moderator.\n
        """
        
        # Iterate through each member
        result = ""
        for member in members:
            result += "{} {}".format(
                member.mention,
                " was successfully added as a bot moderator." if OmegaPsi.addModerator(member) else (
                    " is already a bot moderator."
                )
            )
        
        return discord.Embed(
            name = "Added bot Moderators",
            description = result,
            colour = BotModerator.EMBED_COLOR
        )
    
    def removeModerator(self, members):
        """Removes a bot moderator from the bot.\n

        members - The Discord Users to remove as a bot moderator.\n
        """
        
        # Iterate through each member
        result = ""
        for member in members:
            result += "{} {} a bot moderator.".format(
                member.mention,
                "was successfully removed as" if OmegaPsi.removeModerator(member) else (
                    "is not"
                )
            )
        
        return discord.Embed(
            name = "Removed Moderators",
            description = result,
            colour = BotModerator.EMBED_COLOR
        )
    
    def activate(self, commands):
        """Activates commands globally in the bot.\n

        commands - The commands to globally activate.\n
        """
        
        # Open bot file
        bot = OmegaPsi.openOmegaPsi()

        # Iterate through commands
        if len(commands) > 0:
            result = ""
            acCommands = []
            for command in commands:

                # Iterate through categories
                added = False
                for category in self._categories:

                    # Check if command was part of category
                    commandObject = self._categories[category].getCommand(command)
                    if commandObject != None:
                        acCommands.append(commandObject)
                        added = True
                    
                if not added:
                    result += "`{}` is not a valid command.\n".format(
                        command
                    )
            
            # Activate commands
            for command in acCommands:
                if command.getAlternatives()[0] in bot["inactive_commands"]:
                    bot["inactive_commands"].pop(command.getAlternatives()[0])
                    result += "`{}` was activated globally.\n".format(
                        commandObject.getAlternatives()[0]
                    )
                else:
                    result += "`{}` is already globally active.\n".format(
                        commandObject.getAlternatives()[0]
                    )
        
        else:
            result = ""
            for command in bot["inactive_commands"]:
                result += "`{}` was activated globally.\n".format(command)
            bot["inactive_commands"] = {}
        
        # Close bot file
        OmegaPsi.closeOmegaPsi(bot)
        
        return discord.Embed(
            name = "Activated",
            description = result,
            colour = BotModerator.EMBED_COLOR
        )
    
    def deactivate(self, command, reason):
        """Deactivates a command globally in the bot.\n

        command - The command to globally deactivate.\n
        reason - The reason the command is being globally deactivated.\n
        """
        
        # Open bot file
        bot = OmegaPsi.openOmegaPsi()

        # Check if command is valid
        commandObject = None
        for category in self._categories:
            commandObject = self._categories[category].getCommand(command)
            if commandObject != None:
                break
        if commandObject == None:
            result = "`{}` is not a valid command.".format(
                command
            )
        else:
            bot["inactive_commands"][commandObject.getAlternatives()[0]] = reason
            result = "`{}` was globally deactivated.\nReason: {}".format(
                commandObject.getAlternatives()[0],
                reason
            )
        
        # Close bot file
        OmegaPsi.closeOmegaPsi(bot)

        return discord.Embed(
            name = "Deactivated",
            description = result,
            colour = BotModerator.EMBED_COLOR
        )
    
    def getInfo(self):
        """Returns the info on the bot.\n
        """

        # Open the bot info
        omegaPsi = OmegaPsi.openOmegaPsi()

        botModerators = ""
        for moderator in omegaPsi["moderators"]:
            botModerators += "<@{}>\n".format(moderator)
        
        inactiveCommands = ""
        for command in omegaPsi["inactive_commands"]:
            inactiveCommands += "{}\nReason: {}\n".format(
                command, omegaPsi["inactive_commands"][command]
            )

        tags = {
            "Bot Moderators": botModerators,
            "Inactive Commands": inactiveCommands
        }

        embed = discord.Embed(
            title = "Omega Psi",
            description = "Owner: <@{}>".format(omegaPsi["owner"]),
            colour = BotModerator.EMBED_COLOR
        )

        for tag in tags:
            embed.add_field(
                name = tag,
                value = tags[tag] if len(tags[tag]) > 0 else "None",
                inline = False
            )
        
        return embed
    
    def getServers(self):
        """Returns a list of servers the bot is in.\n
        """

        # Add results to fields
        fields = []
        fieldText = ""
        for server in self.client.guilds:
            
            text = "`{}` | Owner: {}\n".format(
                server.name, server.owner.mention
            )

            if len(fieldText) + len(text) >= OmegaPsi.MESSAGE_THRESHOLD:
                fields.append(fieldText)
                fieldText = ""
            
            fieldText += text
        
        # Add trailing field text
        if len(fieldText) > 0:
            fields.append(fieldText)
        
        # Create embed object
        embed = discord.Embed(
            title = "Servers",
            description = "A list of servers that Omega Psi is in.",
            colour = BotModerator.EMBED_COLOR
        )

        # Add fields to embed object
        count = 0
        for field in fields:
            count += 1
            embed.add_field(
                name = "Servers {}".format(
                    "({} / {})".format(
                        count, len(fields)
                    ) if len(fields) > 1 else ""
                ),
                value = field,
                inline = False
            )
        
        return embed
    
    async def setStatus(self, activityType, text):
        """Sets the presence of the bot given the activity type and text.\n

        activityType - The type of activity to set for the presence.\n
        text - The text to set.\n
        """

        # Get the specific activity type
        activityText = activityType
        if activityType in self._status.getAcceptedParameter("activity", "playing").getAlternatives():
            activityType = discord.ActivityType.playing
            activityText = "Playing"

        elif activityType in self._status.getAcceptedParameter("activity", "streaming").getAlternatives():
            activityType = discord.ActivityType.streaming
            activityText = "Streaming"

        elif activityType in self._status.getAcceptedParameter("activity", "listening").getAlternatives():
            activityType = discord.ActivityType.listening
            activityText = "Listening"

        elif activityType in self._status.getAcceptedParameter("activity", "watching").getAlternatives():
            activityType = discord.ActivityType.watching
            activityText = "Watching"
        
        # Update the bot's activity setting
        OmegaPsi.setActivityType(activityType)
        OmegaPsi.setActivityName(text)

        # Change the presence of the bot
        await self.client.change_presence(
            status = discord.Status.online,
            activity = discord.Activity(
                name = text,
                type = activityType
            )
        )

        return discord.Embed(
            title = "Presence Set",
            description = "Activity: {}\nText: {}\n".format(
                activityText, text
            ),
            colour = BotModerator.EMBED_COLOR
        )
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Parsing
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def on_message(self, message):
        """Parses a message and runs a Rank Category command if it can.\n

        message - The Discord Message to parse.\n
        """

        # Make sure message starts with the prefix
        if Server.startsWithPrefix(message.guild, message.content) and not message.author.bot:

            # Split up into command and parameters if possible
            command, parameters = Category.parseText(Server.getPrefixes(message.guild), message.content)
            
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            # Add Moderator Command
            if command in self._addModerator.getAlternatives():

                # 0 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = self.getErrorMessage(self._addModerator, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 1 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await self.run(message, self._addModerator, self.addModerator, message.mentions)
                    )
            
            # Remove Moderator Command
            elif command in self._removeModerator.getAlternatives():

                # 0 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = self.getErrorMessage(self._removeModerator, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 1 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await self.run(message, self._removeModerator, self.removeModerator, message.mentions)
                    )

            # Activate Command
            elif command in self._activate.getAlternatives():

                # If parameters are empty, it will activate all inactive commands
                await sendMessage(
                    self.client,
                    message,
                    embed = await self.run(message, self._activate, self.activate, parameters)
                )
            
            # Deactivate Command
            elif command in self._deactivate.getAlternatives():

                # 0 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = self.getErrorMessage(self._deactivate, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 1 or 2 Parameters Exist
                elif len(parameters) in [1, 2]:

                    reason = None
                    if len(parameters) == 2:
                        reason = parameters[1]
                    
                    await sendMessage(
                        self.client,
                        message,
                        embed = await self.run(message, self._deactivate, self.deactivate, parameters[0], reason)
                    )
                
                # 3 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = self.getErrorMessage(self._deactivate, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Info Command
            elif command in self._info.getAlternatives():

                # 0 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await self.run(message, self._info, self.getInfo)
                    )
                
                # 1 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = self.getErrorMessage(self._info, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Servers Command
            elif command in self._servers.getAlternatives():

                # 0 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await self.run(message, self._servers, self.getServers)
                    )
                
                # 1 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = self.getErrorMessage(self._servers, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Status Command
            elif command in self._status.getAlternatives():

                # Less than 2 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = self.getErrorMessage(self._status, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 2 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await self.run(message, self._status, self.setStatus, parameters[0], " ".join(parameters[1:]))
                    )
            
            # Kill Command
            elif command in self._kill.getAlternatives():

                # 0 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = discord.Embed(
                            title = "Bot Killed",
                            description = "Omega Psi was killed.",
                            colour = BotModerator.EMBED_COLOR
                        )
                    )
                    await self.client.logout()

def setup(client):
    client.add_cog(BotModerator(client))
