from util.file.database import loop
from util.file.server import Server
from util.file.omegaPsi import OmegaPsi
from util.file.user import User

from util.utils.discordUtils import sendMessage, getErrorMessage
from util.utils.miscUtils import loadImageFromUrl
from util.utils.stringUtils import generateRandomString, capitalizeSentences

from functools import partial
from random import choice as choose, randint
from supercog import Category, Command
import discord, os, pygame, requests, timchen

pygame.init()

reactions = ["⏪", "⬅", "➡", "⏩"]

class Image(Category):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    IMGUR_ALBUM_API = "https://api.imgur.com/3/album"
    IMGUR_ALBUM_GET_API = "https://api.imgur.com/3/album/{}"
    IMGUR_IMAGE_API = "https://api.imgur.com/3/image"

    IMGUR_ALBUM_URL = "https://imgur.com/a/{}"
    IMGUR_IMAGE_URL = "https://i.imgur.com/{}"

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

        self._imgur = Command(commandDict = {
            "alternatives": ["imgur"],
            "info": "Allows you to upload an image to an anonymous imgur album.",
            "parameters": {
                "image": {
                    "info": "The URL or image file of the image to upload.",
                    "optional": False,
                    "accepted": {
                        "me": {
                            "alternatives": ["me", "self"],
                            "info": "Gets your album of images from imgur."
                        }
                    }
                }
            },
            "errors": {
                Image.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to upload an image to imgur, you need the image."
                    ]
                }
            },
            "command": self.imgur
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
            self._imgur,
            self._dog,
            self._cat,
            self._avatar,
            self._robohash,
            self._timchen,
            self._nasaImage
        ])

        self._scrollEmbeds = {}

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
    
    async def imgur(self, message, parameters):
        """
        """

        attachments = message.attachments
        canScroll = False

        # Check for no attachments and no parameters
        if len(attachments) == 0 and len(parameters) == 0:
            embed = getErrorMessage(self._imgur, Image.NOT_ENOUGH_PARAMETERS)
        
        # There was at least one of either
        else:

            # Check if the first parameter is in the accepted for getting the album to the images
            #  and getting a scroll embed to show the images
            try:
                if parameters[0] in self._imgur.getAcceptedParameter("image", "me").getAlternatives():
                    me = True
                else:
                    me = False
            except:
                me = False
            
            # Get user's imgur album ID
            album = await User.getImgurAlbum(message.author)
            albumHash = album["hash"]
            albumId = album["id"]

            # See if user does not have an album attached to them
            fields = []
            fieldValue = ""
            if not albumId:
                response = await loop.run_in_executor(None,
                    partial(
                        requests.post,
                        Image.IMGUR_ALBUM_API,
                        data = {
                            "title": "{}#{}".format(
                                message.author.name,
                                message.author.discriminator
                            ),
                            "description": "An anonymous imgur album made for the above Discord User"
                        },
                        headers = {
                            "Authorization": "Client-ID {}".format(
                                os.environ["IMGUR_API_KEY"]
                            )
                        }
                    )
                )
                response = response.json()

                # See if album creation failed
                if response["status"] != 200:
                    error = response["data"]["error"] + "\n"

                    # Add the error to the result field
                    if len(fieldValue) + len(error) > OmegaPsi.MESSAGE_THRESHOLD:
                        fields.append(fieldValue)
                        fieldValue = ""
                    fieldValue += error
                
                # Album creation did not fail
                else:
                    success = "Anonymous Album Created at [this link]({}).\n".format(
                        Image.IMGUR_ALBUM_URL.format(
                            response["data"]["id"]
                        )
                    )

                    # Add the success message to the result field
                    if len(fieldValue) + len(success) > OmegaPsi.MESSAGE_THRESHOLD:
                        fields.append(fieldValue)
                        fieldValue = ""
                    fieldValue += success

                    # Set the user's imgur album
                    albumHash = response["data"]["deletehash"]
                    albumId = response["data"]["id"]
                    await User.setImgurAlbum(message.author, {"hash": albumHash, "id": albumId})

            # Not getting their album and images; Adding one
            if not me:

                # Get url for each attachment
                for attachment in range(len(attachments)):
                    attachments[attachment] = attachments[attachment].url
                
                attachments += parameters
                
                # Iterate through attachments
                for attachment in attachments:                    

                    # Upload image
                    response = await loop.run_in_executor(None,
                        partial(
                            requests.post,
                            Image.IMGUR_IMAGE_API,
                            data = {
                                "image": attachment,
                                "album": albumHash
                            },
                            headers = {
                                "Authorization": "Client-ID {}".format(
                                    os.environ["IMGUR_API_KEY"]
                                )
                            }
                        )
                    )
                    print(response.content)
                    response = response.json()

                    # See if image upload failed
                    if response["status"] != 200:
                        error = response["data"]["error"] + "\n"

                        # Add the error to the result field
                        if len(fieldValue) + len(error) > OmegaPsi.MESSAGE_THRESHOLD:
                            fields.append(fieldValue)
                            fieldValue = ""
                        fieldValue += error
                    
                    # Image upload did not fail
                    else:
                        success = "Anonymous Image Uploaded and Added to your album. [Here]({}) is the direct link to the image.\n".format(
                            Image.IMGUR_IMAGE_URL.format(
                                response["data"]["id"]
                            )
                        )

                        # Add the success message to the result field
                        if len(fieldValue) + len(success) > OmegaPsi.MESSAGE_THRESHOLD:
                            fields.append(fieldValue)
                            fieldValue = ""
                        fieldValue += success

                # Add the trailing result field
                if len(fieldValue) > 0:
                    fields.append(fieldValue)
                    
                # Create embed
                embed = discord.Embed(
                    title = "Results {}".format(
                        "({} / {})".format(
                            1, len(fields)
                        ) if len(fields) > 1 else ""
                    ),
                    description = fields[0],
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )

                # Add all the fields to the embed
                count = 1
                for field in fields[1:]:
                    count += 1
                    embed.add_field(
                        name = "Results {}".format(
                            "({} / {})".format(
                                count, len(fields)
                            ) if len(fields) > 1 else ""
                        ),
                        value = field,
                        inline = False
                    )

            # Getting the author's images
            else:

                # Get the list of images
                album = await loop.run_in_executor(None,
                    partial(
                        requests.get,
                        Image.IMGUR_ALBUM_GET_API.format(
                            albumId
                        ),
                        headers = {
                            "Authorization": "Client-ID f473d8889fc2daf"
                        }
                    )
                )
                album = album.json()

                # Create the first embed
                embed = discord.Embed(
                    title = "Image {}".format(
                        "({} / {})".format(
                            1, len(album["data"]["images"])
                        ) if len(album["data"]["images"]) > 1 else ""
                    ),
                    description = album["data"]["description"],
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color,
                    url = album["data"]["link"]
                ).set_image(
                    url = None if len(album["data"]["images"]) == 0 else album["data"]["images"][0]["link"]
                ).set_author(
                    name = album["data"]["title"],
                    icon_url = message.author.avatar_url if album["data"]["cover"] == None else Image.IMGUR_IMAGE_URL.format(album["data"]["cover"])
                )
                
                # Create the scrolling embed
                self._scrollEmbeds[str(message.author.id)] = {
                    "message": None,
                    "images": album["data"]["images"],
                    "value": 0,
                    "min": 0, 
                    "max": len(album["data"]["images"]) - 1
                }

                canScroll = len(album["data"]["images"]) > 0
        
        msg = await sendMessage(
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

        if canScroll:
            for reaction in reactions:
                await msg.add_reaction(reaction)
            self._scrollEmbeds[str(message.author.id)]["message"] = msg
    
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
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Reactions
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def manage_scrolling(self, reaction, member):
        """Manages the scrolling of any scroll embeds
        """

        # Check for message ID in scrollable embeds
        memberId = str(member.id)
        if memberId in self._scrollEmbeds:
            initial = self._scrollEmbeds[memberId]["value"]

            # Rewind reaction was added; Move to first field
            if str(reaction) == "⏪":
                self._scrollEmbeds[memberId]["value"] = self._scrollEmbeds[memberId]["min"]
            
            # Fast Forward reaction was added; Move to last field
            elif str(reaction) == "⏩":
                self._scrollEmbeds[memberId]["value"] = self._scrollEmbeds[memberId]["max"]
            
            # Arrow Left reaction was added; Move field left
            elif str(reaction) == "⬅":
                self._scrollEmbeds[memberId]["value"] -= 1
                if self._scrollEmbeds[memberId]["value"] < self._scrollEmbeds[memberId]["min"]:
                    self._scrollEmbeds[memberId]["value"] = self._scrollEmbeds[memberId]["min"]
            
            # Arrow Right reaction was added; Move field right
            elif str(reaction) == "➡":
                self._scrollEmbeds[memberId]["value"] += 1
                if self._scrollEmbeds[memberId]["value"] > self._scrollEmbeds[memberId]["max"]:
                    self._scrollEmbeds[memberId]["value"] = self._scrollEmbeds[memberId]["max"]
            
            # Update the scroll embed
            if self._scrollEmbeds[memberId]["value"] != initial and reaction.message.id == self._scrollEmbeds[memberId]["message"].id:
                value = self._scrollEmbeds[memberId]["value"]

                # Get the image Id at the current value
                image = self._scrollEmbeds[memberId]["images"][value]

                # Update the embed
                currentEmbed = self._scrollEmbeds[str(member.id)]["message"].embeds[0]
                currentEmbed.title = "Image {}".format(
                        "({} / {})".format(
                            value + 1, self._scrollEmbeds[str(member.id)]["max"] + 1
                        ) if self._scrollEmbeds[str(member.id)]["max"] > 0 else ""
                    )
                currentEmbed.set_image(
                    url = image["link"]
                )
                await self._scrollEmbeds[str(member.id)]["message"].edit(
                    embed = currentEmbed
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
    client.add_cog(Image(client))