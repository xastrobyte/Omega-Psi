from category.code import Code
from category.game import Game
from category.image import Image
from category.insult import Insult
from category.internet import Internet
from category.math import Math
from category.rank import Rank
from category.misc import Misc
from category.nsfw import NSFW

from util.file.omegaPsi import OmegaPsi
from util.file.server import Server
from util.utils.discordUtils import sendMessage, getErrorMessage

from supercog import Category, Command
import discord, os

class BotModerator(Category):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    BOT_MARKDOWN = "botMarkdown.md"
    MARKDOWN_LOCATION = "commands.md"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Errors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    CANT_BE_DEACTIVATED = "CANT_BE_DEACTIVATED"

    INVALID_ACTIVITY = "INVALID_ACTIVITY"
    INVALID_COMMAND = "INVALID_COMMAND"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Constructor
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, client):
        super().__init__(
            client, 
            "Bot Moderator",
            description = "Very private stuff.",
            embed_color = 0xA456B0,
            restriction_info = "You must be a Bot Moderator to run these commands.",
            bot_mod_category = True,
            bot_mod_error = OmegaPsi.getNoAccessError,
            locally_inactive_error = Server.getInactiveError,
            globally_inactive_error = OmegaPsi.getInactiveError,
            locally_active_check = Server.isCommandActive,
            globally_active_check = OmegaPsi.isCommandActive
        )

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Commands
        
        self._addModerator = Command(commandDict = {
            "alternatives": ["addBotModerator", "addBotMod", "abm"],
            "info": "Allows you to add a bot moderator to the bot.",
            "bot_moderator_only": True,
            "min_parameters": 1,
            "parameters": {
                "member(s)...": {
                    "info": "The member(s) to add as a bot moderator.",
                    "optional": False
                }
            },
            "errors": {
                BotModerator.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to add a bot moderator, you need to mention them."
                    ]
                }
            },
            "command": self.addModerator
        })

        self._removeModerator = Command(commandDict = {
            "alternatives": ["removeBotModerator", "removeBotMod", "remBotMod", "rbm"],
            "info": "Allows you to remove a bot moderator from the bot.",
            "bot_moderator_only": True,
            "min_parameters": 1,
            "parameters": {
                "member(s)...": {
                    "info": "The member(s) to remove as a bot moderator.",
                    "optional": False
                }
            },
            "errors": {
                BotModerator.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to remove a bot moderator, you need to mention them."
                    ]
                }
            },
            "command": self.removeModerator
        })

        self._activate = Command(commandDict = {
            "alternatives": ["activateGlobally", "enableGlobally"],
            "info": "Allows you to activate a command, or commands, globally.",
            "bot_moderator_only": True,
            "min_parameters": 1,
            "parameters": {
                "command(s)": {
                    "info": "The command(s) to activate globally.",
                    "optional": False
                }
            },
            "errors": {
                BotModerator.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to activate a command globally, you need to type it in."
                    ]
                },
                BotModerator.INVALID_COMMAND: {
                    "messages": [
                        "That is not a valid command."
                    ]
                }
            },
            "command": self.activate
        })

        self._deactivate = Command(commandDict = {
            "alternatives": ["deactivateGlobally", "disableGlobally"],
            "info": "Allows you to deactivate a command globally.",
            "bot_moderator_only": True,
            "min_parameters": 1,
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
                BotModerator.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to deactivate a command globally, you need to type it in."
                    ]
                },
                BotModerator.INVALID_COMMAND: {
                    "messages": [
                        "That is not a valid command."
                    ]
                },
                BotModerator.CANT_BE_DEACTIVATED: {
                    "messages": [
                        "This command cannot be deactivated."
                    ]
                }
            },
            "command": self.deactivate
        })

        self._info = Command(commandDict = {
            "alternatives": ["botInfo", "bi"],
            "info": "Allows you to get the info about the bot.",
            "bot_moderator_only": True,
            "max_parameters": 0,
            "errors": {
                BotModerator.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get info about the bot, or the servers it's in, you don't need anything else."
                    ]
                }
            },
            "command": self.getInfo
        })

        self._servers = Command(commandDict = {
            "alternatives": ["servers", "botServers"],
            "info": "Allows you to get a list of servers the bot is in.",
            "bot_moderator_only": True,
            "parameters": {
                "markdown": {
                    "info": "Whether or not to send a markdown version of all the server information.",
                    "optional": True
                }
            },
            "errors": {
                BotModerator.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get a list of servers the bot is in, you only need 1 parameter which is optional."
                    ]
                }
            },
            "command": self.getServers
        })

        self._status = Command(commandDict = {
            "alternatives": ["setStatus", "status"],
            "info": "Allows you to change the presence of the bot.",
            "bot_moderator_only": True,
            "min_parameters": 2,
            "parameters": {
                "activity": {
                    "info": "The activity to set for the presence.",
                    "optional": False,
                    "accepted_parameters": {
                        "playing": {
                            "alternatives": ["playing", "Playing"],
                            "info": "The playing activity type."
                        },
                        "streaming": {
                            "alternatives": ["streaming", "Streaming"],
                            "info": "The streaming activity type."
                        },
                        "listening": {
                            "alternatives": ["listening", "Listening", "listening to", "Listening to"],
                            "info": "The listening activity type."
                        },
                        "watching": {
                            "alternatives": ["watching", "Watching"],
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
                BotModerator.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to set the status, you need the status type and the text to set."
                    ]
                },
                BotModerator.INVALID_ACTIVITY: {
                    "messages": [
                        "The given activity is not a valid activity."
                    ]
                }
            },
            "command": self.setStatus
        })

        self._todo = Command(commandDict = {
            "alternatives": ["todo"],
            "info": "Adds, removes, or lists things in the TODO list.",
            "parameters": {
                "action": {
                    "info": "The action to do.",
                    "optional": True,
                    "accepted": {
                        "add": {
                            "alternatives": ["add", "a"],
                            "info": "Adds something to the TODO list."
                        },
                        "remove": {
                            "alternatives": ["remove", "r"],
                            "info": "Removes something from the TODO list."
                        }
                    }
                },
                "item": {
                    "info": "The item to add or remove.",
                    "optional": True
                }
            },
            "errors": {
                BotModerator.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to add or remove something, you need the item to add or remove."
                    ]
                },
                BotModerator.INVALID_PARAMETER: {
                    "messages": [
                        "That is not a valid parameter."
                    ]
                }
            },
            "command": self.todo
        })

        self._markdown = Command(commandDict = {
            "alternatives": ["markdown", "getMarkdown", "md", "getMd"],
            "info": "Creates and sends the markdown file for the commands.",
            "bot_moderator_only": True,
            "errors": {
                BotModerator.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get the markdown file, you don't need any parameters."
                    ]
                }
            },
            "command": self.markdown
        })

        self._kill = Command(commandDict = {
            "alternatives": ["stop", "quit", "kill"],
            "info": "Kills the bot.",
            "bot_moderator_only": True,
            "max_parameters": 1,
            "parameters": {
                "process": {
                    "info": "The process number to kill.",
                    "optional": True
                }
            },
            "errors": {
                BotModerator.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to kill the bot, you don't need anything other than the process."
                    ]
                }
            },
            "command": self.kill
        })

        self._debug = Command(commandDict = {
            "alternatives": ["debug"],
            "info": "Debugs the bot.",
            "bot_moderator_only": True,
            "max_parameters": 0,
            "errors": {
                BotModerator.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "To debug the bot, you don't need any parameters."
                    ]
                }
            },
            "command": self.debug
        })
    
        self.setCommands([
            self._addModerator,
            self._removeModerator,
            self._activate,
            self._deactivate,
            self._info,
            self._servers,
            self._status,
            self._todo,
            self._markdown,
            self._kill,
            self._debug
        ])

        self._categories = {
            "Code": Code(None),
            "Game": Game(None),
            "Image": Image(None),
            "Insult": Insult(None),
            "Internet": Internet(None),
            "Math": Math(None),
            "Rank": Rank(None),
            "Misc": Misc(None),
            "NSFW": NSFW(None)
        }
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def addModerator(self, message, parameters):
        """Adds bot moderators to the bot.\n

        Parameters:
            parameters: The Discord Users to add as a bot moderator.\n
        """

        # Check if message has no mentions
        if len(message.mentions) < self._addModerator.getMinParameters():
            return getErrorMessage(self._addModerator, BotModerator.NOT_ENOUGH_PARAMETERS)
        
        # There was at least one mention
        else:
        
            # Iterate through each member
            result = ""
            for member in message.mentions:
                result += "{} {}".format(
                    member.mention,
                    " was successfully added as a bot moderator." if OmegaPsi.addModerator(member) else (
                        " is already a bot moderator."
                    )
                )
            
            embed = discord.Embed(
                name = "Added bot Moderators",
                description = result,
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
    
    async def removeModerator(self, message, parameters):
        """Removes a bot moderator from the bot.\n

        Parameters:
            parameters: The Discord Users to remove as a bot moderator.\n
        """

        # Check if message has no mentions
        if len(message.mentions) < self._removeModerator.getMinParameters():
            embed = getErrorMessage(self._removeModerator, BotModerator.NOT_ENOUGH_PARAMETERS)
        
        # There was at least one mention
        else:
        
            # Iterate through each member
            result = ""
            for member in message.mentions:
                result += "{} {} a bot moderator.".format(
                    member.mention,
                    "was successfully removed as" if OmegaPsi.removeModerator(member) else (
                        "is not"
                    )
                )
        
            embed = discord.Embed(
                name = "Removed Moderators",
                description = result,
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
    
    async def activate(self, message, parameters):
        """Activates commands globally in the bot.

        Parameters:
            parameters: The parameters to process.
        """

        # Check if there are not enough parameters
        if len(parameters) < self._activate.getMinParameters():
            embed = getErrorMessage(self._activate, BotModerator.NOT_ENOUGH_PARAMETERS)
        
        # Parameters had the minimum amount of parameters
        else:
        
            # Commands held in each parameter
            commands = parameters
            
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
                            command.getAlternatives()[0]
                        )
                    else:
                        result += "`{}` is already globally active.\n".format(
                            command.getAlternatives()[0]
                        )
            
            else:
                result = ""
                for command in bot["inactive_commands"]:
                    result += "`{}` was activated globally.\n".format(command)
                bot["inactive_commands"] = {}
            
            # Close bot file
            OmegaPsi.closeOmegaPsi(bot)
            
            embed = discord.Embed(
                name = "Activated",
                description = result,
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
    
    async def deactivate(self, message, parameters):
        """Deactivates a command globally in the bot.\n

        Parameters:
            command: The command to globally deactivate.\n
            reason: The reason the command is being globally deactivated.\n
        """

        # Check for minimum amount of parameters
        if len(parameters) < self._deactivate.getMinParameters():
            embed = getErrorMessage(self._deactivate, BotModerator.NOT_ENOUGH_PARAMETERS)
        
        # Parameters had the minimum amount of parameters
        else:

            # Command to be deactivated is first parameter; Reason is every parameter after
            command = parameters[0]
            reason = "No Reason"
            if len(parameters) > 1:
                reason = " ".join(parameters[1:])
            
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

            embed = discord.Embed(
                name = "Deactivated",
                description = result,
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
    
    async def getInfo(self, message, parameters):
        """Returns the info on the bot.\n
        """

        # Check if parameters exceeds maximum parameter
        if len(parameters) > self._info.getMaxParameters():
            embed = getErrorMessage(self._info, BotModerator.TOO_MANY_PARAMETERS)
        
        # Parameters do not exceed maximum parameters
        else:

            # Open the bot info
            omegaPsi = OmegaPsi.openOmegaPsi()

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
            embed = discord.Embed(
                title = "Omega Psi",
                description = "Owner: <@{}>".format(omegaPsi["owner"]),
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
    
    async def getServers(self, message, parameters):
        """Returns a list of servers the bot is in.\n
        """

        # Check if parameters exceeds maximum parameters
        if len(parameters) > self._servers.getMaxParameters():
            embed = getErrorMessage(self._servers, BotModerator.TOO_MANY_PARAMETERS)
        
        # Parameters do not exceed maximum parameters
        else:

            # Getting results through embed
            if len(parameters) == 0:

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
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
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
            
            # Getting results through markdown file
            else:

                # Setup markdown text
                markdown = "# Omega Psi Server Information\n"

                # Iterate through servers bot is in
                for guild in self.client.guilds:

                    # Load file
                    server = Server.openServer(guild)

                    # Add server information (owner, name)
                    try:
                        markdown += "## {} - {}\n".format(
                            guild.name,
                            guild.owner.name + "#" + guild.owner.discriminator
                        )
                    except:
                        markdown += "## {} - No Owner\n".format(
                            guild.name
                        )

                    # Iterate through members in server dictionary
                    for member in server["members"]:
                        member = server["members"][member]
                        discordMember = guild.get_member(int(member["id"]))
                        
                        markdown += (
                            "  * {} ({})\n" +
                            "    * Moderator? {}\n" +
                            "    * Experience: {}\n" +
                            "    * Level: {}\n" +
                            "    * Experience until next level: {}\n"
                        ).format(
                            discordMember.name + "#" + discordMember.discriminator,
                            discordMember.nick,
                            "Yes" if discordMember.guild_permissions.manage_guild else "No",
                            member["experience"],
                            member["level"],
                            Server.getExpFromLevel(member["level"] + 1) - member["experience"]
                        )
                
                # Save markdown temporarily
                mdFile = open(BotModerator.BOT_MARKDOWN, "w")
                mdFile.write(markdown)
                mdFile.close()

                mdFile = open(BotModerator.BOT_MARKDOWN, "r")
            
                # Send file to DMs; Then delete
                await message.author.send(
                    file = discord.File(mdFile)
                )
                os.remove(BotModerator.BOT_MARKDOWN)

                embed = discord.Embed(
                    title = "File sent.",
                    description = "The server information has been sent to your DM's",
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
    
    async def setStatus(self, message, parameters):
        """Sets the presence of the bot given the activity type and text.\n

        Parameters:
            activityType: The type of activity to set for the presence.\n
            text: The text to set.\n
        """

        # Check if parameters is less than minimum parameters
        if len(parameters) < self._status.getMinParameters():
            embed = getErrorMessage(self._status, BotModerator.NOT_ENOUGH_PARAMETERS)
        
        # Parameters has minumum parameters
        else:

            # Activity type is first parameter; Text is every parameter after
            activityType = parameters[0]
            text = " ".join(parameters[1:])

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
                    type = activityType,
                    url = "https://www.twitch.tv/FellowHashbrown"
                )
            )

            embed = discord.Embed(
                title = "Presence Set",
                description = "Activity: {}\nText: {}\n".format(
                    activityText, text
                ),
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
    
    async def todo(self, message, parameters):
        """Runs the todo command.

        Parameters:
            action (str): What action to perform for the todo command.
            item (str): The item to add/remove to/from the TODO list.
        """

        # Check for no parameters; list the TODO list
        if len(parameters) == 0:

            todoList = OmegaPsi.getToDoList()
            todoText = ""
            for item in range(len(todoList)):
                todoText += "{}.) {}\n".format(
                    item + 1, todoList[item]
                )
                
            embed = discord.Embed(
                title = "TODO List",
                description = todoText if len(todoText) > 0 else "Nothing Yet",
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            )
        
        # Check for 2 or more parameters
        else:

            action = parameters[0]

            # There is nothing to add
            if len(parameters) == 1:
                embed = getErrorMessage(self._todo, BotModerator.NOT_ENOUGH_PARAMETERS)
            
            # Check if action is valid
            elif action in self._todo.getAcceptedParameter("action", "add").getAlternatives():

                # Check if index is given
                if parameters[1].isdigit():
                    index = int(parameters[1])
                    item = " ".join(parameters[2:])
                else:
                    index = 0
                    item = " ".join(parameters[1:])

                success = OmegaPsi.addToDo(item, index)

                embed = discord.Embed(
                    title = "Added TODO Item" if success["success"] else "Failed to add TODO Item",
                    description = success["reason"],
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )

            elif action in self._todo.getAcceptedParameter("action", "remove").getAlternatives():
                success = OmegaPsi.removeToDo(" ".join(parameters[1:]))

                embed = discord.Embed(
                    title = "Removed TODO Item" if success["success"] else "Failed to remove TODO Item",
                    description = success["reason"],
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )
            
            # Action is invalid
            else:
                embed = getErrorMessage(self._todo, BotModerator.INVALID_PARAMETER)
        
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
    
    async def markdown(self, message, parameters):
        """Returns the markdown file for the commands.\n"

        Parameters:
            author (discord.User): The sender of the `markdown` command.
        """

        # Check for too many parameters
        if len(parameters) > self._markdown.getMaxParameters():
            embed = getErrorMessage(self._markdown, BotModerator.TOO_MANY_PARAMETERS)
        
        # Parameters do not exceed maximum parameters
        else:

            # Create markdown text
            markdown = "# Commands\n"

            # Add category's hyperlinks
            for category in self._categories:
                markdown += "  * [{}](#{})\n".format(
                    category,
                    category.replace(" ", "-")
                )

            # Go through categories
            for category in self._categories:
                markdown += self._categories[category]["object"].getMarkdown()
            
            # Open file
            mdFile = open(BotModerator.MARKDOWN_LOCATION, "w")
            mdFile.write(markdown)
            mdFile.close()

            mdFile = open(BotModerator.MARKDOWN_LOCATION, "r")

            # Send file to author
            await message.author.send(
                file = discord.File(mdFile)
            )

            # Only send a message if the command was sent in a server
            if message.guild != None:
                embed = discord.Embed(
                    title = "File Sent",
                    description = "The markdown file was sent to your DM's",
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )
            else:
                embed = None

            os.remove(BotModerator.MARKDOWN_LOCATION)
        
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
    
    async def kill(self, message, parameters):
        """Kills the bot and logs out.
        """

        processId = OmegaPsi.PROCESS_ID

        # Check if parameters exceeds maximum parameters
        if len(parameters) > self._kill.getMaxParameters():
            embed = getErrorMessage(self._kill, BotModerator.TOO_MANY_PARAMETERS)
        
        # Parameters do not exceed maximum parameters
        else:
            processId = OmegaPsi.PROCESS_ID if len(parameters) == 0 else parameters[0]

            embed = discord.Embed(
                title = "Bot Killed",
                description = "Omega Psi was killed (Process {})".format(OmegaPsi.PROCESS_ID),
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            )
        
        # Only kill if processId is OmegaPsi.PROCESS_ID
        if processId == OmegaPsi.PROCESS_ID:

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

            await self.client.logout()
    
    async def debug(self, message, parameters):
        """Debugs the bot.
        """

        # Check if parameters exceeds maximum parameters
        if len(parameters) > self._debug.getMaxParameters():
            embed = getErrorMessage(self._debug, BotModerator.TOO_MANY_PARAMETERS)
        
        # Parameters do not exceed maximum parameters
        else:
            embed = discord.Embed(
            title = "Omega Psi Debugging",
            description = "Process ID: {}".format(OmegaPsi.PROCESS_ID),
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
        """Parses a message and runs a Bot Moderator command if it can.\n

        Parameters:
            message: The Discord Message to parse.\n
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
                    await cmd.getCommand()(message, parameters)
                    break

def setup(client):
    client.add_cog(BotModerator(client))