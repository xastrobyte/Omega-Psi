from util.file.server import Server
from util.utils import sendMessage, loadImageFromUrl, getErrorMessage

from supercog import Category, Command
import discord, os, pygame, random

pygame.init()

class NSFW(Category):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    EMBED_COLOR = 0xFFAAAA

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
            restriction_info = "You should be 18+ to run the commands in this channel!",
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
            }
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
            }
        })

        self.setCommands([
            self._boobs,
            self._booty
        ])
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def boobs(self, parameters):
        """Sends a random picture of some boobs.
        """
        
        # Check for too many parameters
        if len(parameters) > self._boobs.getMaxParameters():
            return getErrorMessage(self._boobs, NSFW.TOO_MANY_PARAMETERS)

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
            
        image = "BOOBS_{}.png".format(boobNumber)
        pygame.image.save(boobsImage, image)
        return image
    
    def booty(self, parameters):
        """Sends a random picture of some booty.
        """
        
        # Check for too many parameters
        if len(parameters) > self._booty.getMaxParameters():
            return getErrorMessage(self._booty, NSFW.TOO_MANY_PARAMETERS)

        # Load image from URL, temporarily save it, send image
        while True:

            # Generate random number for an image; Add 0's to beginning until pad is reached (5)
            bootyNumber = str(random.randint(1, 5400))
            bootyNumber = bootyNumber.rjust(5, "0")

            # Try loading the image
            try:
                bootyImage = loadImageFromUrl(NSFW.BOOTY_URL.format(bootyNumber))
            
            # Image load failed; Retry using new number.
            except:
                pass

        image = "BOOTY_{}.png".format(bootyNumber)
        pygame.image.save(bootyImage, image)
        return image

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

            # Boobs Command
            if command in self._boobs.getAlternatives():
                result = await self.run(message, self._boobs, self.boobs, parameters)

                if type(result) == discord.Embed:
                    await sendMessage(
                        self.client,
                        message,
                        embed = result
                    )
                else:
                    await sendMessage(
                        self.client,
                        message,
                        filename = result
                    )

                    os.remove(result)
            
            # Booty Command
            elif command in self._booty.getAlternatives():
                result = await self.run(message, self._booty, self.booty, parameters)

                if type(result) == discord.Embed:
                    await sendMessage(
                        self.client,
                        message,
                        embed = result
                    )
                else:
                    await sendMessage(
                        self.client,
                        message,
                        filename = result
                    )
                    
                    os.remove(result)

def setup(client):
    client.add_cog(NSFW(client))
