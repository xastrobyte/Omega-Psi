from util.file.server import Server
from util.utils.discordUtils import sendMessage, getErrorMessage
from util.utils.miscUtils import loadImageFromUrl

from supercog import Category, Command
import discord, pygame, random

pygame.init()

scrollEmbeds = {}

class NSFW(Category):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    BOOBS_URL = "http://media.oboobs.ru/boobs_preview/{}.jpg"

    BOOTY_URL = "http://media.obutts.ru/butts_preview/{}.jpg"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Errors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Constructor
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, client):
        super().__init__(
            client,
            "NSFW",
            description = "An NSFW category for 18+",
            embed_color = 0xFFAAAA,
            restriction_info = "You should be 18+ to run the commands in this category!",
            nsfw_category = True,
            nsfw_channel_error = Server.getNSFWChannelError
        )

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Commands

        self._boobs = Command(commandDict = {
            "alternatives": ["boobs", "boob"],
            "info": "Sends a random picture of boobs.",
            "errors": {
                NSFW.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get some boobs, you don't need any parameters."
                    ]
                }
            },
            "command": self.boobs
        })

        self._booty = Command(commandDict = {
            "alternatives": ["booty", "ass"],
            "info": "Sends a random picture of some booty.",
            "errors": {
                NSFW.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get some booty, you don't need any parameters."
                    ]
                }
            },
            "command": self.booty
        })

        self.setCommands([
            self._boobs,
            self._booty
        ])
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def boobs(self, message, parameters):
        """Sends a random picture of some boobs.
        """
        
        # Check for too many parameters
        if len(parameters) > self._boobs.getMaxParameters():
            embed = getErrorMessage(self._boobs, NSFW.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Load image from URL, temporarily save it, send image
            while True:

                # Generate random number for an image; Add 0's to beginning until pad is reached (5)
                boobNumber = str(random.randint(1, 12500))
                boobNumber = boobNumber.rjust(5, "0")

                # Try loading the Image
                try:
                    boobsImage = loadImageFromUrl(NSFW.BOOBS_URL.format(boobNumber))
                    break
                
                # Image load failed; Retry using new number.
                except:
                    pass
            
            embed = discord.Embed(
                title = "Boobs Number {}".format(boobNumber),
                description = " ",
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            ).set_image(
                url = NSFW.BOOBS_URL.format(boobNumber)
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
    
    async def booty(self, message, parameters):
        """Sends a random picture of some booty.
        """
        
        # Check for too many parameters
        if len(parameters) > self._booty.getMaxParameters():
            return getErrorMessage(self._booty, NSFW.TOO_MANY_PARAMETERS)

        # There were the proper amount of parameters
        else:

            # Load image from URL, temporarily save it, send image
            while True:

                # Generate random number for an image; Add 0's to beginning until pad is reached (5)
                bootyNumber = str(random.randint(1, 5400))
                bootyNumber = bootyNumber.rjust(5, "0")

                # Try loading the image
                try:
                    bootyImage = loadImageFromUrl(NSFW.BOOTY_URL.format(bootyNumber))
                    break
                
                # Image load failed; Retry using new number.
                except:
                    pass
            
            embed = discord.Embed(
                title = "Booty Number {}".format(bootyNumber),
                description = " ",
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            ).set_image(
                url = NSFW.BOOTY_URL.format(bootyNumber)
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
        """Parses a message and runs an NSFW Category command if it can.\n

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
    client.add_cog(NSFW(client))