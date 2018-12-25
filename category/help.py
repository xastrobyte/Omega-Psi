from category.code import Code
from category.game import Game
from category.image import Image
from category.insult import Insult
from category.internet import Internet
from category.math import Math
from category.meme import Meme
from category.misc import Misc
from category.nsfw import NSFW
from category.rank import Rank
from category.updates import Updates
from category.serverModerator import ServerModerator
from category.botModerator import BotModerator

from util.file.database import omegaPsi, loop
from util.file.omegaPsi import OmegaPsi
from util.file.server import Server

from util.utils.discordUtils import sendMessage, getErrorMessage
from util.utils.miscUtils import datetimeToString
# from util.utils.stringUtils import censor

from datetime import datetime
from functools import partial
from supercog import Category, Command
from supercog.censor import censor
import discord, os, requests, time

class Help(Category):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    EMOJI = {
        "Help": ":question:",
        "Code": ":keyboard:",
        "Game": ":video_game:",
        "Image": ":film_frames:",
        "Insult": ":exclamation:",
        "Internet": ":desktop:",
        "Math": ":asterisk:",
        "Meme": ":laughing:",
        "Misc": ":mag:",
        "NSFW": ":underage:", 
        "Rank": ":up:",
        "Updates": ":new:",
        "Moderator": ":pick:",
        "Owner": ":gear:"
    }

    MARKDOWN_LOCATION = "commands.md"

    GITHUB = "https://www.github.com/FellowHashbrown/omega-psi/blob/master/category/commands.md"

    SUPPORT = "https://discord.gg/mvNxh3f"

    GITHUB_COMMANDS = "https://www.github.com/FellowHashbrown/omega-psi/blob/master/category/commands.md"
    GITHUB_LINK = "https://www.github.com/FellowHashbrown/omega-psi"

    REPL_IT_LINK = "https://repl.it/@FellowHashbrown/Omega-Psi"

    UPTIME_LINK = "https://stats.uptimerobot.com/KQG3Rc54B"
    UPTIME_API_URL = "https://api.uptimerobot.com/v2/getMonitors"

    VOTE_LINK = "https://discordbots.org/bot/503804826187071501/vote"

    WEBSITE = "https://www.fellowhashbrown.com"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Errors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    MEMBER_MISSING_PERMISSION = "MEMBER_MISSING_PERMISSION"
    NO_ACCESS = "NO_ACCESS"
    NOT_NSFW = "NOT_NSFW"

    INVALID_CATEGORY = "INVALID_CATEGORY"
    INVALID_COMMAND = "INVALID_COMMAND"
    INVALID_PARAMETER = "INVALID_PARAMETER"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Constructor
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, client):
        super().__init__(
            client, 
            "Help",
            description = "Shows you the help menu.",
            embed_color = 0x00FF80,
            locally_inactive_error = Server.getInactiveError,
            globally_inactive_error = OmegaPsi.getInactiveError,
            locally_active_check = Server.isCommandActive,
            globally_active_check = OmegaPsi.isCommandActive
        )

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Commands
        self._help = Command(commandDict = {
            "alternatives": ["help", "h", "?"],
            "info": "Gives you help on all commands or a specific command in the bot.",
            "can_be_deactivated": False,
            "parameters": {
                "command | category": {
                    "optional": True,
                    "info": "Gives you help on a specific command or category."
                }
            },
            "errors": {
                Help.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You don't need any more than 1 parameter in the help command."
                    ]
                },
                Help.INVALID_CATEGORY: {
                    "messages": [
                        "That is not a valid category."
                    ]
                },
                Help.INVALID_COMMAND: {
                    "messages": [
                        "That is not a valid command."
                    ]
                },
                Help.NO_ACCESS: {
                    "messages": [
                        "You cannot get help for that category."
                    ]
                },
                Help.MEMBER_MISSING_PERMISSION: {
                    "messages": [
                        "You do not have the permission for that command."
                    ]
                }
            },
            "command": self.help
        })

        self._ping = Command(commandDict = {
            "alternatives": ["ping"],
            "info": "Pings the bot.",
            "errors": {
                Help.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You don't need any parameters to ping the bot."
                    ]
                }
            },
            "command": self.ping
        })

        self._support = Command(commandDict = {
            "alternatives": ["support", "supportServer"],
            "info": "Gives you an invite to the support server for Omega Psi support.",
            "errors": {
                Help.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get the support invite, you don't need any parameters."
                    ]
                }
            },
            "command": self.support
        })

        self._website = Command(commandDict = {
            "alternatives": ["website", "web"],
            "info": "Gives you the link to my developer website.",
            "errors": {
                Help.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get the link to my website, you don't need any parameters."
                    ]
                }
            },
            "command": self.website
        })

        self._vote = Command(commandDict = {
            "alternatives": ["vote"],
            "info": "Allows you to get a link to vote for Omega Psi on discordbots.org",
            "errors": {
                Help.TOO_MANY_PARAMETERS: {
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
                Help.TOO_MANY_PARAMETERS: {
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
                Help.TOO_MANY_PARAMETERS: {
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
                Help.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get the uptime of Omega Psi, you don't need any parameters."
                    ]
                }
            },
            "command": self.uptime
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
                Help.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to send a bug, error, or feedback to the developers of Omega Psi, you need to type in the message."
                    ]
                },
                Help.INVALID_PARAMETER: {
                    "messages": [
                        "That was an invalid message type."
                    ]
                }
            },
            "command": self.sendBug
        })

        self._markdown = Command(commandDict = {
            "alternatives": ["markdown", "getMarkdown", "md", "getMd"],
            "info": "Creates and sends the markdown file for the commands.",
            "bot_moderator_only": True,
            "errors": {
                Help.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get the markdown file, you don't need any parameters."
                    ]
                }
            },
            "command": self.markdown
        })

        self.setCommands([
            self._help,
            self._ping,
            self._support,
            self._website,
            self._vote,
            self._github,
            self._replit,
            self._uptime,
            self._invite,
            self._sendBug,
            self._markdown
        ])

        # Categories
        self._categories = {
            "Help": {
                "object": self,
                "command": "bot"
            },
            "Code": {
                "object": Code(None),
                "command": "code"
            },
            "Game": {
                "object": Game(None),
                "command": "game"
            },
            "Image": {
                "object": Image(None),
                "command": "image"
            },
            "Insult": {
                "object": Insult(None),
                "command": "insults"
            },
            "Internet": {
                "object": Internet(None),
                "command": "internet"
            },
            "Math": {
                "object": Math(None),
                "command": "math"
            },
            "Meme": {
                "object": Meme(None),
                "command": "memes"
            },
            "Misc": {
                "object": Misc(None),
                "command": "misc"
            },
            "NSFW": {
                "object": NSFW(None),
                "command": "nsfw"
            },
            "Rank": {
                "object": Rank(None),
                "command": "ranking"
            },
            "Updates": {
                "object": Updates(None),
                "command": "updates"
            },
            "Moderator": {
                "object": ServerModerator(None),
                "command": "serverMod"
            },
            "Owner": {
                "object": BotModerator(None),
                "command": "botMod"
            }
        }

        amountCommands = 0
        for category in self._categories:
           amountCommands += len(self._categories[category]["object"].getCommands())
        # print(amountCommands)

        self._scrollEmbeds = {}

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def getAllHTML(self):
        """Returns the HTML render text for all the categories in Omega Psi
        """

        # Setup HTML
        html = (
            "<h1>Commands</h1>\n" +
            "  <ul>\n" +
            "{}\n" +
            "  </ul>\n"
        )

        # Iterate through categories
        tableOfContents = []
        for category in self._categories:
            tableOfContents.append("    <li><a href=\"#{}\">{}</a></li>".format(
                self._categories[category]["object"].getCategoryName().lower().replace(" ", "-"),
                self._categories[category]["object"].getCategoryName()
            ))

            html += self._categories[category]["object"].getHTML() + "\n"
        
        return html.format(
            "\n".join(tableOfContents)
        )
    
    def getAllFancyHTML(self):
        """Returns the Fancy HTML render text for all the categories in Omega Psi
        """

        # Setup HTML
        html = ""

        # Iterate through categories
        for category in self._categories:
            html += "  <!--{} Category-->\n".format(category)
            html += self._categories[category]["object"].getFancyHTML() + "\n"
        
        return html
    
    def getAllColumnHTML(self):
        """Returns the Column HTML render text for all the categories in Omega Psi
        """

        # Setup HTML
        html = ""

        # Keep track of columns
        columns = [[], [], []]

        # Iterate through categories
        count = 0
        for category in self._categories:
            text = "  <!--{} Category-->\n".format(category)
            columns[count % 3].append(
                text + self._categories[category]["object"].getColumnHTML() + "\n"
            )
            count += 1
        
        # Add to columns
        for column in columns:

            html += "      <div class=\"categories-column\">\n"
            for category in column:
                html += category
            html += "      </div>\n"
        
        return html

    async def getHelpMenu(self, message):
        """Returns a full help menu on all the commands in Omega Psi.\n

        Parameters:
            message (discord.Message): The Discord Message to determine if moderator commands will be shown and if NSFW results can appear.\n
        """

        # Determine if channel is NSFW
        try:
            isNSFW = message.channel.is_nsfw()
        
        # Channel is not in a Server; Set NSFW to True
        except:
            isNSFW = True

        # Setup Help Embed
        embed = discord.Embed(
            title = "Omega Psi Commands",
            description = (
                "A list of Commands in Omega Psi.\n" +
                "For more in-depth command information, check out [this]({} \"{}\") page."
            ).format(
                Help.GITHUB,
                "Omega Psi Github Page"
            ),
            colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
        )
        
        # Add each category
        for category in self._categories:

            # See if category is a Bot Moderator Category and author is a Bot Moderator
            onBotMod = self._categories[category]["object"].isBotModCategory()
            isBotMod = await OmegaPsi.isAuthorModerator(message.author)

            # See if category is a Server Moderator Category and author is a Server Moderator
            if message.guild != None:
                onServerMod = self._categories[category]["object"].isServerModCategory()
                isServerMod = await Server.isAuthorModerator(message.author)
            else:
                onServerMod = isServerMod = False

            # See if category is an NSFW category
            isNSFWCategory = self._categories[category]["object"].isNSFWCategory()

            # See if category can only run in Server
            isServerCategory = self._categories[category]["object"].isServerCategory()
            inServer = message.guild != None
            
            # Only category to be added if one of the following are True:
            #   - The Category is a Bot Mod category and a Bot Mod accesses it
            #   - The Category is a Server Mod category and a Server Mod accesses it
            #   - The Category is an NSFW category and the Channel is NSFW
            # The final regular case is if None of the above are True
            showCategory = True
            if onBotMod:
                if isBotMod:
                    showCategory = True
                else:
                    showCategory = False

            elif onServerMod:
                if isServerMod:
                    showCategory = True
                else:
                    showCategory = False
                
            elif isNSFWCategory:
                if isNSFW:
                    showCategory = True
                else:
                    showCategory = False

            elif isServerCategory:
                if inServer:
                    showCategory = True
                else:
                    showCategory = False

            if showCategory:
                embed.add_field(
                    name = "{} {} Commands".format(
                        Help.EMOJI[category],
                        category
                    ),
                    value = (
                        "`{}help {}`\n" +
                        "[Need more? Hover me]({} \"{}\")"
                    ).format(
                        OmegaPsi.PREFIX, self._categories[category]["command"],
                        Help.GITHUB + "#" + category.replace(" ", "-"), 
                        self._categories[category]["object"].getDescription()
                    )
                )
        
        return embed
    
    async def isCategoryName(self, categoryName):
        """Returns whether or not the category is a category name.\n

        Parameters:
            categoryName (str): The category name to get.\n
        """

        # Iterate through categories
        for category in self._categories:
            if categoryName == self._categories[category]["command"]:
                return True
        
        return False

    async def getHelpForCategory(self, message, categoryName, *, isNSFW = False):
        """Returns a help menu for a specific category.

        Parameters:
            message (discord.Message): The Discord Message that was sent.
            categoryName (str): The category to get help for.
            isNSFW (bool): Whether or not to show NSFW results.
        """

        # Iterate through categories to see if the command matches anything
        for category in self._categories:
            helpForCategory = self._categories[category]["command"]

            # Category name matches current category
            if categoryName == helpForCategory:

                # See if category is a Bot Moderator Category and author is a Bot Moderator
                onBotMod = self._categories[category]["object"].isBotModCategory()
                isBotMod = await OmegaPsi.isAuthorModerator(message.author)

                # See if category is a Server Moderator Category and author is a Server Moderator
                if message.guild != None:
                    onServerMod = self._categories[category]["object"].isServerModCategory()
                    isServerMod = await Server.isAuthorModerator(message.author)
                else:
                    onServerMod = isServerMod = False

                # See if category is an NSFW category
                isNSFWCategory = self._categories[category]["object"].isNSFWCategory()

                # See if category can only run in Server
                isServerCategory = self._categories[category]["object"].isServerCategory()
                inServer = message.guild != None
                
                # Only category to be added if one of the following are True:
                #   - The Category is a Bot Mod category and a Bot Mod accesses it
                #   - The Category is a Server Mod category and a Server Mod accesses it
                #   - The Category is an NSFW category and the Channel is NSFW
                # The final regular case is if None of the above are True
                showCategory = True
                if onBotMod:
                    if isBotMod:
                        showCategory = True
                    else:
                        showCategory = False

                elif onServerMod:
                    if isServerMod:
                        showCategory = True
                    else:
                        showCategory = False
                    
                elif isNSFWCategory:
                    if isNSFW:
                        showCategory = True
                    else:
                        showCategory = False

                elif isServerCategory:
                    if inServer:
                        showCategory = True
                    else:
                        showCategory = False

                if showCategory:
                    categoryHelp = self.getCategoryHelp(self._categories[category]["object"], isNSFW = isNSFW)

                    # Create the embed
                    embed = discord.Embed(
                        title = categoryHelp["title"],
                        description = "Help for the [{} Commands]({} \"{}\")\n{}\n".format(
                            categoryHelp["title"],
                            Help.GITHUB + "#" + categoryHelp["title"].replace(" ", "-"),
                            self._categories[category]["object"].getDescription(),
                            "```diff\n- {}\n```".format(
                                self._categories[category]["object"].getRestrictionInfo()
                            ) if self._categories[category]["object"].getRestrictionInfo() != None else ""
                        ),
                        colour = self._categories[category]["object"].getEmbedColor() if message.guild == None else message.author.top_role.color
                    ).add_field(
                        name = "Commands {}".format(
                            "Page ({} / {})".format(
                                1, len(categoryHelp["fields"])
                            ) if len(categoryHelp["fields"]) > 1 else ""
                        ),
                        value = censor(categoryHelp["fields"][0]) if not isNSFW else categoryHelp["fields"][0],
                        inline = False
                    )

                    # Send embed message in order to get the id to store
                    # Also add reactions based off of length of fields
                    msg = await message.channel.send(
                        embed = embed
                    )

                    # Add left and right if there are 2 fields
                    if len(categoryHelp["fields"]) == 2:
                        await msg.add_reaction("⬅")
                        await msg.add_reaction("➡")
                    
                    # Add all reactions if there are more than 2 fields
                    elif len(categoryHelp["fields"]) > 2:
                        await msg.add_reaction("⏪")
                        await msg.add_reaction("⬅")
                        await msg.add_reaction("➡")
                        await msg.add_reaction("⏩")

                    self._scrollEmbeds[str(msg.id)] = {
                        "author": str(message.author.id),
                        "fields": [],
                        "value": 0,
                        "min": 0,
                        "max": len(categoryHelp["fields"]) - 1
                    }

                    count = 0
                    for field in categoryHelp["fields"]:
                        count += 1

                        self._scrollEmbeds[str(msg.id)]["fields"].append({
                            "name": "Commands {}".format(
                                "Page ({} / {})".format(
                                    count, len(categoryHelp["fields"])
                                ) if len(categoryHelp["fields"]) > 1 else ""
                            ),
                            "value": field,
                            "inline": False
                        })

                    return None
                
                elif not onBotMod and not isBotMod:
                    return OmegaPsi.getErrorMessage(OmegaPsi.NO_ACCESS)
                
                elif not onServerMod and not isServerMod:
                    return Server.getErrorMessage(Server.NO_ACCESS)
        
        # Category did not match, send error message
        return getErrorMessage(self._help, Help.INVALID_CATEGORY)
    
    async def getHelpForCommand(self, discordMember, command, *, isNSFW = False):
        """Returns help for a specific command.\n

        Parameters:
            command (supercog.Command): The command, or an alternative, to get help for.\n
            isNSFW (bool): Whether or not to show NSFW results.\n
        """

        # Iterate through Categories to see if the command matches anything
        for category in self._categories:
            helpForCommand = self._categories[category]["object"].getHelp(command, isNSFW = isNSFW)

            # See if category is Bot Moderator or Server Moderator and author is a Bot Moderator or Server Moderator
            onBotMod = category == "Bot Moderator"
            isBotMod = await OmegaPsi.isAuthorModerator(discordMember)
            try:
                guild = discordMember.guild
            except:
                guild = None
            
            if guild != None:
                onServerMod = category == "Server Moderator"
                isServerMod = await Server.isAuthorModerator(discordMember)
            else:
                onServerMod = isServerMod = False

            if helpForCommand != None: 

                # Check if serverMod command
                if (onServerMod and not isServerMod) or (onBotMod and not isBotMod):
                    return getErrorMessage(self._help, Help.MEMBER_MISSING_PERMISSION)

                embed = discord.Embed(
                    title = censor(command) if not isNSFW else command,
                    description = "{}\n{}\n".format(
                        helpForCommand["restriction"],
                        helpForCommand["title"]
                    ),
                    colour = self._categories[category]["object"].getEmbedColor() if guild == None else discordMember.top_role.color
                )

                # Iterate through accepted parameters
                for accepted in helpForCommand["accepted"]:

                    # Add each field for a single accepted parameter
                    count = 0
                    for field in helpForCommand["accepted"][accepted]:
                        count += 1
                        embed.add_field(
                            name = "Accepted Parameters for `{}` {}".format(
                                accepted,
                                "({} / {})".format(
                                    count, len(helpForCommand["accepted"][accepted])
                                ) if len(helpForCommand["accepted"][accepted]) > 1 else ""
                            ),
                            value = field,
                            inline = False
                        )

                return embed
            
        # Command did not match, send error message
        return getErrorMessage(self._help, Help.INVALID_COMMAND)
    
    async def help(self, message, parameters):
        """Runs the help command for the bot.
        """

        try:
            self._update
        except:
            self._update = await omegaPsi.getUpdate()
            self._update = self._update["version"]

        # Check for too many parameters
        if len(parameters) > self._help.getMaxParameters():
            embed = getErrorMessage(self._help, Help.TOO_MANY_PARAMETERS)
        
        # There were the right amount of parameters
        else:

            # Check for no parameters
            if len(parameters) == 0:
                embed = await self.run(message, self._help, self.getHelpMenu, message)
            
            # Check for 1 parameter (command or category)
            elif len(parameters) == 1:

                # Determine if channel has nsfw filter on it
                if message.guild != None:
                    isNSFW = message.channel.is_nsfw()
                else:
                    isNSFW = True

                # See if parameter is a category
                if await self.isCategoryName(parameters[0]):
                    embed = await self.run(message, self._help, self.getHelpForCategory, message, parameters[0], isNSFW = isNSFW)
                else:
                    embed = await self.run(message, self._help, self.getHelpForCommand, message.author, parameters[0], isNSFW = isNSFW)

        if embed != None:

            msg = await sendMessage(
                self.client,
                message,
                embed = embed.set_footer(
                    text = "Requested by {}#{}".format(
                        message.author.name,
                        message.author.discriminator
                    ),
                    icon_url = message.author.avatar_url
                ).set_author(
                    name = "Version {}".format(self._update)
                )
            ) 

            if str(message.author.id) in self._scrollEmbeds:  
                self._scrollEmbeds[str(message.author.id)]["message"] = msg
    
    async def ping(self, message, parameters):
        """Pings the bot
        """

        # Check for too many parameters
        if len(parameters) > self._ping.getMaxParameters():
            embed = getErrorMessage(self._ping, Help.TOO_MANY_PARAMETERS)

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
    
    async def support(self, message, parameters):
        """
        """

        # Check for too many parameters
        if len(parameters) > self._support.getMaxParameters():
            embed = getErrorMessage(self._support, Help.TOO_MANY_PARAMETERS)
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
                message = Help.SUPPORT
            )
    
    async def website(self, message, parameters):
        """Returns the link for the my developer website.
        """

        # Check for too many parameters
        if len(parameters) > self._website.getMaxParameters():
            embed = getErrorMessage(self._website, Help.TOO_MANY_PARAMETERS)
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
                message = Help.WEBSITE
            )
    
    async def vote(self, message, parameters):
        """Sends a link to discordbots.org to vote for the bot.
        """

        # Check for too many parameters
        if len(parameters) > self._vote.getMaxParameters():
            embed = getErrorMessage(self._vote, Help.TOO_MANY_PARAMETERS)

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
                message = Help.VOTE_LINK
            )
    
    async def github(self, message, parameters):
        """Returns the Github link for the bot.
        """

        # Check for too many parameters
        if len(parameters) > self._github.getMaxParameters():
            embed = getErrorMessage(self._github, Help.TOO_MANY_PARAMETERS)

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
                message = Help.GITHUB_LINK
            )
    
    async def replit(self, message, parameters):
        """Returns the Repl.it link for the bot.
        """

        # Check for too many parameters
        if len(parameters) > self._replit.getMaxParameters():
            embed = getErrorMessage(self._replit, Help.TOO_MANY_PARAMETERS)
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
                message = Help.REPL_IT_LINK
            )
    
    async def uptime(self, message, parameters):
        """Returns the uptime link for the bot.
        """

        # Check for too many parameters
        if len(parameters) > self._uptime.getMaxParameters():
            embed = getErrorMessage(self._uptime, Help.TOO_MANY_PARAMETERS)

        # There were the proper amount of parameters
        else:

            # Request the downtime from Uptime Robot
            downtime = await loop.run_in_executor(None,
                partial(
                    requests.post,
                    Help.UPTIME_API_URL,
                    data = "api_key={}&format=json&logs=1".format(os.environ["UPTIME_API_KEY"]),
                    headers = {
                        'content-type': "application/x-www-form-urlencoded",
                        'cache-control': "no-cache"
                    }
                )
            )
            downtime = downtime.json()

            # Only get the data if there is no error
            if "error" not in downtime:
                downtimeDay = 0
                downtimeWeek = 0
                downtimeMonth = 0
                recentDowntime = None

                # Go through all the logs and detect the downtime (any log that is not of type 2)
                for log in downtime["monitors"][0]["logs"]:

                    # Get the most recent downtime
                    if log["type"] != 2:
                        if recentDowntime == None:
                            seconds = log["duration"]

                            hours = seconds // 3600
                            seconds -= 3600 * hours

                            minutes = seconds // 60

                            recentDowntime = {
                                "hours": hours,
                                "minutes": minutes,
                                "last": datetimeToString(datetime.fromtimestamp(log["datetime"]))
                            }

                        # Keep track of the last 24 hours
                        if time.time() - log["datetime"] <= 60*60*24:
                            downtimeDay += log["duration"]
                        
                        # Keep track of the last 7 days
                        if time.time() - log["datetime"] <= 60*60*24*7:
                            downtimeWeek += log["duration"]
                        
                        # Keep track of the last 30 days
                        if time.time() - log["datetime"] <= 60*60*24*30:
                            downtimeMonth += log["duration"]
                
                # Keep uptime in separate fields
                fields = {
                    "Last 24 Hours": round(100 - (downtimeDay / (60 * 60 * 24) * 100), 2),
                    "Last 7 Days": round(100 - (downtimeWeek / (60 * 60 * 24 * 7) * 100), 2),
                    "Last 30 Days": round(100 - (downtimeMonth / (60 * 60 * 25 * 30) * 100), 2)
                }

                # Put the text for the most recent downtime in its own text
                recentDowntime = "The latest downtime happened on {} for {} hr{} {} min{}".format(
                    recentDowntime["last"],
                    recentDowntime["hours"], "s" if recentDowntime["hours"] != 1 else "",
                    recentDowntime["minutes"], "s" if recentDowntime["minutes"] != 1 else ""
                )
                
                # Create the embed and add the fields
                embed = discord.Embed(
                    title = "Omega Psi Uptime",
                    description = recentDowntime,
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color,
                    url = Help.UPTIME_LINK
                )

                for field in fields:
                    embed.add_field(
                        name = field,
                        value = str(fields[field]) + "%"
                    )
            
            # There was an error
            else:
                embed = discord.Embed(
                    title = downtime["error"],
                    description = " ",
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
    
    async def sendBug(self, message, parameters):
        """Sends all bot moderators a message from the bot.\n

        discordServer - The Discord Server that the message originated from.\n
        discordMember - The Discord User/Member that wants to send the message.\n
        messageType - The type of message being sent. (Bug, Error, Feedback).\n
        message - The message to send.\n
        """

        # Check for not enough parameters
        if len(parameters) < self._sendBug.getMinParameters():
            embed = getErrorMessage(self._sendBug, Help.NOT_ENOUGH_PARAMETERS)
        
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
                embed = getErrorMessage(self._sendBug, Help.INVALID_PARAMETER)

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
                for moderator in await OmegaPsi.getModerators():

                    # Get the user
                    user = self.client.get_user(int(moderator))

                    # Only send message to user if user is not None
                    if user != None:
                        await user.send(
                            embed = embed
                        )
                
                embed = discord.Embed(
                    title = "Message Sent",
                    description = "Your `{}` report was sent.\nMessage: {}\n".format(
                        messageType, msg
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

    async def markdown(self, message, parameters):
        """Returns the markdown file for the commands.\n"

        Parameters:
            author (discord.User): The sender of the `markdown` command.
        """

        # Check for too many parameters
        if len(parameters) > self._markdown.getMaxParameters():
            embed = getErrorMessage(self._markdown, Help.TOO_MANY_PARAMETERS)
        
        # Parameters do not exceed maximum parameters
        else:

            # Create markdown text
            markdown = "# Commands\n"

            # Add category's hyperlinks
            for category in self._categories:
                markdown += "  * [{}](#{})\n".format(
                    self._categories[category]["object"].getCategoryName(),
                    self._categories[category]["object"].getCategoryName().replace(" ", "-")
                )

            # Go through categories
            for category in self._categories:
                markdown += self._categories[category]["object"].getMarkdown()
            
            # Open file
            mdFile = open(Help.MARKDOWN_LOCATION, "w")
            mdFile.write(markdown)
            mdFile.close()

            mdFile = open(Help.MARKDOWN_LOCATION, "r")

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

            os.remove(Help.MARKDOWN_LOCATION)
        
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
        """Parses a message and runs a Help Category command if it can.\n

        Parameters:
            message (discord.Message): The Discord Message to parse.\n
        """

        # Make sure message starts with the prefix
        if await Server.startsWithPrefix(message.guild, message.content) and not message.author.bot:

            # Split up into command and parameters if possible
            command, parameters = Category.parseText(await Server.getPrefixes(message.guild), message.content)
            
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            # Iterate through Commands
            for cmd in self.getCommands():
                if command in cmd.getAlternatives():
                    async with message.channel.typing():

                        # Run the comand but don't try running others
                        await cmd.getCommand()(message, parameters)
                    break
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Scrollable Embeds
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def manage_scrolling(self, reaction, member):
        """Manages the scrolling of any help embeds
        """

        # Check for message ID in scrollable embeds
        messageId = str(reaction.message.id)
        if messageId in self._scrollEmbeds:
            initial = self._scrollEmbeds[messageId]["value"]

            # Check if the member ID is the same as the stored ID
            if str(member.id) == self._scrollEmbeds[messageId]["author"]:

                # Rewind reaction was added; Move to first field
                if str(reaction) == "⏪":
                    self._scrollEmbeds[messageId]["value"] = self._scrollEmbeds[messageId]["min"]
                
                # Fast Forward reaction was added; Move to last field
                elif str(reaction) == "⏩":
                    self._scrollEmbeds[messageId]["value"] = self._scrollEmbeds[messageId]["max"]
                
                # Arrow Left reaction was added; Move field left
                elif str(reaction) == "⬅":
                    self._scrollEmbeds[messageId]["value"] -= 1
                    if self._scrollEmbeds[messageId]["value"] < self._scrollEmbeds[messageId]["min"]:
                        self._scrollEmbeds[messageId]["value"] = self._scrollEmbeds[messageId]["min"]
                
                # Arrow Right reaction was added; Move field right
                elif str(reaction) == "➡":
                    self._scrollEmbeds[messageId]["value"] += 1
                    if self._scrollEmbeds[messageId]["value"] > self._scrollEmbeds[messageId]["max"]:
                        self._scrollEmbeds[messageId]["value"] = self._scrollEmbeds[messageId]["max"]
                
            # Update the scroll embed
            if self._scrollEmbeds[messageId]["value"] != initial:
                value = self._scrollEmbeds[messageId]["value"]
                
                # Get the embed that is stored; There will only be 1 always
                embed = reaction.message.embeds[0]

                # Set the field at 0
                embed.set_field_at(0,
                    name = self._scrollEmbeds[messageId]["fields"][value]["name"],
                    value = self._scrollEmbeds[messageId]["fields"][value]["value"],
                    inline = self._scrollEmbeds[messageId]["fields"][value]["inline"]
                )

                # Update the embed
                await reaction.message.edit(
                    embed = embed
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
    client.add_cog(Help(client))