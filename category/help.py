from category.code import Code
from category.game import Game
from category.image import Image
from category.insult import Insult
from category.internet import Internet
from category.math import Math
from category.rank import Rank
from category.misc import Misc
from category.nsfw import NSFW
from category.serverModerator import ServerModerator
from category.botModerator import BotModerator

from util.file.omegaPsi import OmegaPsi
from util.file.server import Server

from util.utils import sendMessage, getErrorMessage, censor

from supercog import Category, Command
import discord, os

class Help(Category):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    EMBED_COLOR = 0x00FF80

    EMOJI = {
        "Help": ":question:",
        "Code": ":keyboard:",
        "Game": ":video_game:",
        "Image": ":film_frames:",
        "Insult": ":exclamation:",
        "Internet": ":desktop:",
        "Math": ":asterisk:",
        "Rank": ":up:",
        "Misc": ":mag:",
        "NSFW": ":no_entry_sign: ", 
        "Moderator": ":pick:",
        "Bot": ":gear:"
    }

    GITHUB = "https://www.github.com/FellowHashbrown/omega-psi-py/blob/master/category/commands.md"

    MARKDOWN_LOCATION = "commands.md"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Errors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    MEMBER_MISSING_PERMISSION = "MEMBER_MISSING_PERMISSION"
    NO_ACCESS = "NO_ACCESS"
    NOT_NSFW = "NOT_NSFW"

    INVALID_CATEGORY = "INVALID_CATEGORY"
    INVALID_COMMAND = "INVALID_COMMAND"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Constructor
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, client):
        super().__init__(
            client, 
            "Help",
            description = "Shows you the help menu.",
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
            }
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
            }
        })

        self.setCommands([
            self._help,
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
            "Rank": {
                "object": Rank(None),
                "command": "leveling"
            },
            "Misc": {
                "object": Misc(None),
                "command": "misc"
            },
            "NSFW": {
                "object": NSFW(None),
                "command": "nsfw"
            },
            "Moderator": {
                "object": ServerModerator(None),
                "command": "serverMod"
            },
            "Bot": {
                "object": BotModerator(None),
                "command": "botMod"
            }
        }

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

    def getHelpMenu(self, message):
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
            colour = Help.EMBED_COLOR
        )
        
        # Add each category
        for category in self._categories:

            # See if category is a Bot Moderator Category and author is a Bot Moderator
            onBotMod = self._categories[category]["object"].isBotModCategory()
            isBotMod = OmegaPsi.isAuthorModerator(message.author)

            # See if category is a Server Moderator Category and author is a Server Moderator
            if message.guild != None:
                onServerMod = self._categories[category]["object"].isServerModCategory()
                isServerMod = Server.isAuthorModerator(message.guild, message.author)
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
    
    def isCategoryName(self, categoryName):
        """Returns whether or not the category is a category name.\n

        Parameters:
            categoryName (str): The category name to get.\n
        """

        # Iterate through categories
        for category in self._categories:
            if categoryName == self._categories[category]["command"]:
                return True
        
        return False

    def getHelpForCategory(self, message, categoryName, *, isNSFW = False):
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
                isBotMod = OmegaPsi.isAuthorModerator(message.author)

                # See if category is a Server Moderator Category and author is a Server Moderator
                if message.guild != None:
                    onServerMod = self._categories[category]["object"].isServerModCategory()
                    isServerMod = Server.isAuthorModerator(message.guild, message.author)
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
                        colour = Help.EMBED_COLOR
                    )

                    count = 0
                    for field in categoryHelp["fields"]:
                        count += 1
                        embed.add_field(
                            name = "Commands {}".format(
                                "({} / {})".format(
                                    count, len(categoryHelp["fields"])
                                ) if len(categoryHelp["fields"]) > 1 else ""
                            ),
                            value = field,
                            inline = False
                        )
                    
                    return embed
                
                elif not onBotMod and not isBotMod:
                    return OmegaPsi.getErrorMessage(OmegaPsi.NO_ACCESS)
                
                elif not onServerMod and not isServerMod:
                    return Server.getErrorMessage(Server.NO_ACCESS)
        
        # Category did not match, send error message
        return getErrorMessage(self._help, Help.INVALID_CATEGORY)
    
    def getHelpForCommand(self, discordMember, command, *, isNSFW = False):
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
            isBotMod = OmegaPsi.isAuthorModerator(discordMember)
            try:
                guild = discordMember.guild
            except:
                return getErrorMessage(self._help, Help.NO_ACCESS)
            
            if guild != None:
                onServerMod = category == "Server Moderator"
                isServerMod = Server.isAuthorModerator(guild, discordMember) or OmegaPsi.isAuthorModerator(discordMember)
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
                    colour = Help.EMBED_COLOR
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
    
    async def markdown(self, author):
        """Returns the markdown file for the commands.\n"

        Parameters:
            author (discord.User): The sender of the `markdown` command.
        """

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
        mdFile = open(Help.MARKDOWN_LOCATION, "w")
        mdFile.write(markdown)
        mdFile.close()

        mdFile = open(Help.MARKDOWN_LOCATION, "r")

        # Send file to author
        await author.send(
            file = discord.File(mdFile)
        )

        os.remove(Help.MARKDOWN_LOCATION)

        try:
            guild = author.guild

            return discord.Embed(
                title = "File Sent",
                description = "The markdown file was sent to your DM's",
                colour = Help.EMBED_COLOR
            )
        except:
            pass

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Parsing
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def on_message(self, message):
        """Parses a message and runs a Help Category command if it can.\n

        Parameters:
            message (discord.Message): The Discord Message to parse.\n
        """

        # Make sure message starts with the prefix
        if Server.startsWithPrefix(message.guild, message.content) and not message.author.bot:

            # Split up into command and parameters if possible
            command, parameters = Category.parseText(Server.getPrefixes(message.guild), message.content)
            
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            # Help Command
            if command in self._help.getAlternatives():

                # 0 Parameter Exist (full help menu)
                if len(parameters) == 0:

                    embed = await self.run(message, self._help, self.getHelpMenu, message)

                    await sendMessage(
                        self.client,
                        message,
                        embed = embed
                    )
                
                # 1 Parameter Exists (command)
                elif len(parameters) == 1:

                    # Determine if channel has nsfw filter on it
                    if message.guild != None:
                        isNSFW = message.channel.is_nsfw()
                    else:
                        isNSFW = True

                    # See if parameter is a category
                    if self.isCategoryName(parameters[0]):
                        embed = await self.run(message, self._help, self.getHelpForCategory, message, parameters[0], isNSFW = isNSFW)
                    else:
                        embed = await self.run(message, self._help, self.getHelpForCommand, message.author, parameters[0], isNSFW = isNSFW)

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
                        embed = getErrorMessage(self._help, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Markdown
            elif command in self._markdown.getAlternatives():

                # No Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await self.run(message, self._markdown, self.markdown, message.author)
                    )
                
                # 1 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._markdown, Category.TOO_MANY_PARAMETERS)
                    )

def setup(client):
    client.add_cog(Help(client))
