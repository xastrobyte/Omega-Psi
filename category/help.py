from category.category import Category
from category.code import Code
from category.game import Game
from category.image import Image
from category.insult import Insult
from category.internet import Internet
from category.math import Math
from category.rank import Rank
from category.misc import Misc
from category.serverModerator import ServerModerator
from category.botModerator import BotModerator

from util.command import Command
from util.file.omegaPsi import OmegaPsi
from util.file.server import Server

from util.utils import sendMessage

import discord, os

class Help(Category):

    DESCRIPTION = "Shows you the help menu."

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
        "Server Moderator": ":pick:",
        "Bot Moderator": ":gear:"
    }

    MARKDOWN_LOCATION = "commands.md"

    def __init__(self, client):
        super().__init__(client, "Help")

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Commands
        self._help = Command({
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
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You don't need any more than 1 parameter in the help command."
                    ]
                },
                Category.INVALID_CATEGORY: {
                    "messages": [
                        "That is not a valid category."
                    ]
                },
                Category.INVALID_COMMAND: {
                    "messages": [
                        "That is not a valid command."
                    ]
                }
            }
        })

        self._markdown = Command({
            "alternatives": ["markdown", "getMarkdown", "md", "getMd"],
            "info": "Creates and sends the markdown file for the commands.",
            "bot_moderator_only": True,
            "errors": {
                Category.TOO_MANY_PARAMETERS: {
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
            "Server Moderator": {
                "object": ServerModerator(None),
                "command": "serverMod"
            },
            "Bot Moderator": {
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
        html = ""

        # Iterate through categories
        for category in self._categories:
            html += self._categories[category]["object"].getHTML() + "\n"
        
        return html

    def getHelpMenu(self, message):
        """Returns a full help menu on all the commands in Omega Psi.\n

        message - The Discord Message to determine if moderator commands will be shown and if NSFW results can appear.\n
        """

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

            # Keep track of server and bot moderator
            onBotModAndIsBotMod = category == "Bot Moderator" and OmegaPsi.isAuthorModerator(message.author)
            if message.guild != None:
                onServerModAndIsServerMod = category == "Server Moderator" and Server.isAuthorModerator(message.guild, message.author)
            else:
                onServerModAndIsServerMod = False
            
            if onServerModAndIsServerMod or onBotModAndIsBotMod or category not in ["Server Moderator", "Bot Moderator"]:
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
                        Category.GITHUB + "#" + category.replace(" ", "-"), 
                        self._categories[category]["object"].DESCRIPTION
                    )
                )
        
        return embed
    
    def isCategoryName(self, categoryName):
        """Returns whether or not the category is a category name.\n

        categoryName - The category name to get.\n
        """

        # Iterate through categories
        for category in self._categories:
            if categoryName == self._categories[category]["command"]:
                return True
        
        return False

    def getHelpForCategory(self, discordMessage, categoryName, *, isNSFW = False):
        """Returns a help menu for a specific category.\n

        discordMessage - The Discord Message that was sent.\n
        categoryName - The category to get help for.\n

        Keyword Arguments:\n
         - isNSFW - Whether or not to show NSFW results.\n
        """

        # Iterate through categories to see if the command matches anything
        for category in self._categories:
            helpForCategory = self._categories[category]["command"]

            # Category name matches current category
            if categoryName == helpForCategory:

                # Get bot mod and server mod info
                onBotModAndIsBotMod = category == "Bot Moderator" and OmegaPsi.isAuthorModerator(discordMessage.author)
                if discordMessage.guild != None:
                    onServerModAndIsServerMod = category == "Server Moderator" and Server.isAuthorModerator(discordMessage.guild, discordMessage.author)
                else:
                    onServerModAndIsServerMod = False
                
                if onBotModAndIsBotMod or onServerModAndIsServerMod or category not in ["Server Moderator", "Bot Moderator"]:
                    return self.getCategory(self._categories[category]["object"], isNSFW = isNSFW)
                
                elif not onBotModAndIsBotMod:
                    return OmegaPsi.getErrorMessage(OmegaPsi.NO_ACCESS_CATEGORY)
                
                elif not onServerModAndIsServerMod:
                    return Server.getErrorMessage(Server.NO_ACCESS_CATEGORY)
        
        # Category did not match, send error message
        return self.getErrorMessage(self._help, Category.INVALID_CATEGORY)
    
    def getHelpForCommand(self, command, *, isNSFW = False):
        """Returns help for a specific command.\n

        command - The command, or an alternative, to get help for.\n

        Keyword Arguments:\n
         - isNSFW - Whether or not to show NSFW results.\n
        """

        # Iterate through Categories to see if the command matches anything
        for category in self._categories:
            helpForCommand = self._categories[category]["object"].getHelp(command, isNSFW = isNSFW)
            if helpForCommand != None:
                return helpForCommand
            
        # Command did not match, send error message
        return self.getErrorMessage(self._help, Category.INVALID_COMMAND)
    
    async def markdown(self, author):
        """Returns the markdown file for the commands.\n"
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

        message - The Discord Message to parse.\n
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
                        embed = await self.run(message, self._help, self.getHelpForCommand, parameters[0], isNSFW = isNSFW)

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
                        embed = self.getErrorMessage(self._help, Category.TOO_MANY_PARAMETERS)
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
                        embed = self.getErrorMessage(self._markdown, Category.TOO_MANY_PARAMETERS)
                    )

def setup(client):
    client.add_cog(Help(client))
