from util.file.database import loop
from util.file.server import Server
from util.file.omegaPsi import OmegaPsi

from util.utils.discordUtils import sendMessage, getErrorMessage
from util.utils.miscUtils import loadImageFromUrl
from util.utils.stringUtils import generateRandomString, capitalizeSentences

from functools import partial
from random import choice as choose, randint
from supercog import Category, Command
import discord, os, pygame, requests, timchen

pygame.init()

class Image(Category):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    AVATAR_LIST = "https://api.adorable.io/avatars/list"
    AVATAR_API  = "https://api.adorable.io/avatars/face/{}/{}/{}/{}"

    DOG_API = "https://dog.ceo/api/breeds/image/random"
    CAT_API = "https://api.thecatapi.com/v1/images/search"

    ROBOHASH_API = "https://robohash.org/{}"

    TIMCHEN_API = "https://timchen.tk/api"

    NASA_RANDOM = "https://images-api.nasa.gov/search?media_type=image&year_start=1960"
    NASA_SEARCH = "https://images-api.nasa.gov/search?q={}&media_type=image"
    DESCRIPTION_THRESHOLD = 2000

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Errors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    NO_GIFS_FOUND = "NO_GIFS_FOUND"
    NO_IMAGE = "NO_IMAGE"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Constructor
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, client):
        super().__init__(
            client, 
            "Image",
            description = "Anything having to do with images is here.",
            embed_color = 0x800080,
            locally_inactive_error = Server.getInactiveError,
            globally_inactive_error = OmegaPsi.getInactiveError,
            locally_active_check = Server.isCommandActive,
            globally_active_check = OmegaPsi.isCommandActive
        )

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Commands
        self._gif = Command(commandDict = {
            "alternatives": ["gif", "giphy", "g"],
            "info": "Sends a random gif from Giphy.",
            "parameters": {
                "keywords": {
                    "optional": True,
                    "info": "The keywords to search for in Giphy."
                }
            },
            "errors": {
                Image.NO_GIFS_FOUND: {
                    "messages": [
                        "Hmmm. No gifs were found with those keywords. Perhaps broaden your search?"
                    ]
                }
            },
            "command": self.gif
        })

        self._dog = Command(commandDict = {
            "alternatives": ["dog", "doggy", "dogMe"],
            "info": "Sends a random picture of a random dog from the internet.",
            "errors": {
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get a picture of a dog, you don't need any parameters"
                    ]
                }
            },
            "command": self.dog
        })

        self._cat = Command(commandDict = {
            "alternatives": ["cat", "kitty", "catMe"],
            "info": "Sends a random picture of a random cat from the internet.",
            "errors": {
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get a picture of a cat, you don't need any parameters."
                    ]
                }
            },
            "command": self.cat
        })

        self._avatar = Command(commandDict = {
            "alternatives": ["avatar", "avatarMe"],
            "info": "Sends a random cute avatar.",
            "errors": {
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get an avatar, you don't need any parameters."
                    ]
                }
            },
            "command": self.avatar
        })

        self._robohash = Command(commandDict = {
            "alternatives": ["robohash", "robo"],
            "info": "Sends a robohash avatar based off the text you enter.",
            "parameters":{
                "content": {
                    "info": "The text to use to generate the robohash avatar.",
                    "optional": True,
                    "accepted": {
                        "random": {
                            "alternatives": ["random", "surprise", "surpriseMe"],
                            "info": "Allows you to have a completely random robohash to be sent."
                        }
                    }
                }
            },
            "command": self.robohash
        })

        self._timchen = Command(commandDict = {
            "alternatives": ["timchen", "tim", "chen", "t"],
            "info": {
                "text": "Sends a random picture of Timchen (a Repl.it moderator) using an API made by {}",
                "hyperlink": "https://repl.it/@mat1",
                "hyperlink_text": "mat#6207"
            },
            "errors": {
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get a picture of Timchen, you don't need any parameters."
                    ]
                }
            },
            "command": self.timchen
        })

        self._nasaImage = Command(commandDict = {
            "alternatives": ["nasa", "NASA", "nasaImage", "NASAImage", "nasaImg", "NASAImg"],
            "info": "Gives you a random NASA image given a search term or no search term.",
            "parameters": {
                "term": {
                    "info": "The term to search for a NASA image.",
                    "optional": True
                }
            },
            "errors": {
                Image.NO_IMAGE: {
                    "messages": [
                        "There were no images matching that search. Try again or broaden your search term."
                    ]
                }
            },
            "command": self.nasaImage
        })

        self.setCommands([
            self._gif,
            self._dog,
            self._cat,
            self._avatar,
            self._robohash,
            self._timchen,
            self._nasaImage
        ])

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def gif(self, message, parameters):
        """Returns a gif from giphy.
        """

        keywords = " ".join(parameters)

        # Get data involving gifs from Giphy
        if keywords == "random":
            gifData = await loop.run_in_executor(None,
                requests.get,
                os.environ["GIPHY_RANDOM_API_URL"]
            )
            gifData = gifData.json()

            result = gifData["data"]["embed_url"]
        
        else:
            gifsData = await loop.run_in_executor(None,
                requests.get,
                os.environ["GIPHY_SEARCH_API_URL"].format(
                    keywords.replace(" ", "+")
                )
            )
            gifsData = gifsData.json()

            # Return random embed url
            if len(gifsData) > 0:
                gifData = choose(gifsData["data"])
                result = gifData["embed_url"]
            else:
                result = getErrorMessage(self._gif, Image.NO_GIFS_FOUND)
        
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result.set_footer(
                    text = "Requested by {}#{}".format(
                        message.author.name,
                        message.author.discriminator
                    ),
                    icon_url = message.author.avatar_url
                )
            )
        
        else:
            await sendMessage(
                self.client,
                message,
                message = result
            )
    
    async def dog(self, message, parameters):
        """Returns a random dog from the internet
        """

        # Check for too many parameters
        if len(parameters) > self._dog.getMaxParameters():
            embed = getErrorMessage(self._dog, Image.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                requests.get,
                Image.DOG_API
            )
            result = result.json()

            embed = discord.Embed(
                title = "Dog from the internet",
                description = " ",
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            ).set_image(
                url = result["message"]
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
    
    async def cat(self, message, parameters):
        """Returns a random cat from the internet.
        """

        # Check for too many parameters
        if len(parameters) > self._cat.getMaxParameters():
            embed = getErrorMessage(self._cat, Image.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                partial(
                    requests.get,
                    Image.CAT_API,
                    headers = {
                        "x-api-key": os.environ["CAT_API_KEY"]
                    }
                )
            )
            result = result.json()

            embed = discord.Embed(
                title = "Cat from the internet",
                description = " ",
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            ).set_image(
                url = result[0]["url"]
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
        

    async def avatar(self, message, parameters):
        """Returns a random cute avatar that can be used as a placeholder.

        Parameters:
            parameters (list): The parameters that detect for too many parameters.
        """

        # Check for too many parameters
        if len(parameters) > self._avatar.getMaxParameters():
            embed = getErrorMessage(self._avatar, Image.TOO_MANY_PARAMETERS)
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

            # Get list of face features
            faceValues = await loop.run_in_executor(None,
                requests.get,
                Image.AVATAR_LIST
            )
            faceValues = faceValues.json()["face"]

            # Choose random eyes, nose, mouth, and color
            eyes  = choose(faceValues["eyes"])
            nose  = choose(faceValues["nose"])
            mouth = choose(faceValues["mouth"])
            color = hex(randint(0, 16777215))[2:].rjust(6, "0")

            # Load image
            image = await loop.run_in_executor(None,
                loadImageFromUrl,
                Image.AVATAR_API.format(
                    eyes, nose,
                    mouth, color
                )
            )

            # Save image temporarily
            avatarFile = "{}_{}_{}_{}.png".format(
                eyes, nose, mouth, color
            )
            pygame.image.save(image, avatarFile)

            # Send file then delete image
            await sendMessage(
                self.client,
                message,
                filename = avatarFile
            )

            os.remove(avatarFile)
    
    async def robohash(self, message, parameters):
        """Sends a random robohash avatar or a generated one based off of the content.
        """

        # Generate personal robohash if content is empty
        content = " ".join(parameters)

        if len(content) == 0:
            content = "{}-{}".format(
                message.author.name,
                message.author.discriminator
            )
        
        # Generate totally random robohash if content is random
        elif content in self._robohash.getAcceptedParameter("content", "random").getAlternatives():
            content = generateRandomString()
        
        # Load image
        image = await loop.run_in_executor(None,
            loadImageFromUrl,
            Image.ROBOHASH_API.format(content)
        )

        # Save image temporarily
        avatarFile = "{}.png".format(
            content
        )
        pygame.image.save(image, avatarFile)
        
        # Send the file and then delete it
        await sendMessage(
            self.client,
            message,
            filename = avatarFile
        )

        os.remove(avatarFile)
    
    async def timchen(self, message, parameters):
        """Returns a random picture of Timchen with the caption.
        """
        
        # Check for too many parameters
        if len(parameters) > self._timchen.getMaxParameters():
            embed = getErrorMessage(self._timchen, Image.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Get a random image
            timchenData = await timchen.get_random()

            embed = discord.Embed(
                title = "Timchen!",
                description = capitalizeSentences(timchenData.description),
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            ).set_image(
                url = timchenData.url
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
    
    async def nasaImage(self, message, parameters):
        """Returns an image from NASA.
        """

        keywords = " ".join(parameters)

        # Get data involving NASA images
        if keywords == "random":
            imageData = await loop.run_in_executor(None,
                requests.get,
                Image.NASA_RANDOM
            )

        else:
            imageData = await loop.run_in_executor(None,
                requests.get,
                Image.NASA_SEARCH.format(
                    keywords.replace(" ", "+")
                )
            )
        
        imageData = imageData.json()

        # Check if there are no images
        if len(imageData["collection"]["items"]) == 0:
            embed = getErrorMessage(self._nasaImage, Image.NO_IMAGE)
        
        # There are images
        else:

            # Choose random item from collection
            item = choose(imageData["collection"]["items"])

            # Get href from item
            imageLink = item["links"][0]["href"]

            # Make sure description is less than 2000 characters
            if len(item["data"][0]["description"]) < Image.DESCRIPTION_THRESHOLD:
                description = item["data"][0]["description"]
            else:
                description = item["data"][0]["description"][:Image.DESCRIPTION_THRESHOLD] + "[...]"

            embed = discord.Embed(
                title = item["data"][0]["title"],
                description = description,
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            ).set_image(
                url = imageLink
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
        """Parses a message and runs an Image Category command if it can.\n

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
    client.add_cog(Image(client))