from util.file.database import loop
from util.file.omegaPsi import OmegaPsi
from util.file.server import Server
from util.utils.discordUtils import sendMessage, getErrorMessage
from util.utils.miscUtils import loadImageFromUrl
from util.utils.stringUtils import splitText

from supercog import Category, Command
import discord, pygame, random, requests

pygame.init()

class NSFW(Category):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    BOOBS_URL = "http://media.oboobs.ru/boobs_preview/{}.jpg"

    BOOTY_URL = "http://media.obutts.ru/butts_preview/{}.jpg"

    URBAN_API_CALL = "https://api.urbandictionary.com/v0/define?term={}"
    URBAN_ICON = "https://vignette.wikia.nocookie.net/creation/images/b/b7/Urban_dictionary_--_logo.jpg/revision/latest?cb=20161002212954"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Errors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    NO_TERM = "NO_TERM"

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

        self._urban = Command(commandDict = {
            "alternatives": ["urban", "urbanDictionary", "urbanDict"],
            "info": "Gives you the top 5 urban dictionary entries for a term.",
            "nsfw": True,
            "parameters": {
                "term": {
                    "info": "The term to look up in urban dictionary.",
                    "optional": False
                }
            },
            "errors": {
                NSFW.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "You need the term to look something up in urban dictionary."
                    ]
                },
                NSFW.NO_TERM: {
                    "messages": [
                        "The term you entered does not exist on urban dictionary."
                    ]
                }
            },
            "command": self.urban
        })

        self.setCommands([
            self._boobs,
            self._booty,
            self._urban
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
                    loadImageFromUrl(NSFW.BOOBS_URL.format(boobNumber))
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
                    loadImageFromUrl(NSFW.BOOTY_URL.format(bootyNumber))
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
    
    async def urban(self, message, parameters):
        """Returns the top 5 urban dictionary entries for the specified term.\n

         - term - The term to search on urban dictionary.\n
         - discordChannel - The Discord Channel the definition is being sent in.\n
        """

        # Check for not enough parameters
        if len(parameters) < self._urban.getMinParameters():
            embed = getErrorMessage(self._urban, NSFW.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            term = " ".join(parameters)

            # Use requests to get the data in JSON
            try:
                urlCall = NSFW.URBAN_API_CALL.format(term.replace(" ", "+"))
                urbanData = await loop.run_in_executor(None,
                    requests.get,
                    urlCall
                )
                urbanData = urbanData.json()

                # Get first 5 values (or values if there are less than 5)
                if len(urbanData["list"]) < 5:
                    definitions = urbanData["list"]
                else:
                    definitions = urbanData["list"][:5]
                
                # Create discord embed
                embed = discord.Embed(
                    title = "{} Results Of `{}`".format("Top 5" if len(definitions) > 5 else "", term),
                    description = " ",
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                ).set_thumbnail(
                    url = NSFW.URBAN_ICON
                )

                # Add definitions
                defCount = 0
                for definition in definitions:
                    defCount += 1

                    # Get definition; Split up into multiple fields if necessary
                    definitionFields = splitText(definition["definition"], OmegaPsi.MESSAGE_THRESHOLD)

                    count = 0
                    for field in definitionFields:
                        count += 1
                        embed.add_field(
                            name = "Definition {} {}".format(
                                defCount,
                                "({} / {})".format(
                                    count, len(definitionFields)
                                ) if len(definitionFields) > 1 else ""
                            ),
                            value = field,
                            inline = False
                        )

            except:
                embed = getErrorMessage(self._urban, NSFW.NO_TERM)
        
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
    client.add_cog(NSFW(client))