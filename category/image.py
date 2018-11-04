from category.category import Category

from util.command import Command
from util.file.server import Server
from util.utils import sendMessage

from random import choice as choose
import discord, json, os, urllib.request, requests

class Image(Category):

    DESCRIPTION = "Anything having to do with images is here."

    EMBED_COLOR = 0x800080

    MEME_SUBREDDITS = [
        "meme",
        "memes",
        "dankmeme",
        "dank_meme"
    ]
    MEME_RANDOM = "https://www.reddit.com/r/{}/.json?sort=top&limit=500"
    REDDIT_BASE = "https://www.reddit.com"

    NASA_RANDOM = "https://images-api.nasa.gov/search?media_type=image&year_start=1960"
    NASA_SEARCH = "https://images-api.nasa.gov/search?q={}&media_type=image"

    def __init__(self, client):
        super().__init__(client, "Image")

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Commands
        self._gif = Command({
            "alternatives": ["gif", "giphy", "g"],
            "info": "Sends a random gif from Giphy.",
            "parameters": {
                "keywords": {
                    "optional": True,
                    "info": "The keywords to search for in Giphy."
                }
            },
            "errors": {
                Category.NO_GIFS_FOUND: {
                    "messages": [
                        "Hmmm. No gifs were found with those keywords. Perhaps broaden your search?"
                    ]
                }
            }
        })

        self._theOffice = Command({
            "alternatives": ["theOffice", "office", "o"],
            "info": "Sends a random gif related to The Office.",
            "errors": {
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "*Why are you the way that you are?* You don't need any parameters."
                    ]
                }
            }
        })

        self._parksAndRec = Command({
            "alternatives": ["parksAndRec", "parks", "pnr"],
            "info": "Sends a random gif related to Parks and Rec.",
            "errors": {
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "No no no. You don't need any parameters to get a gif from Parks and Rec."
                    ]
                }
            }
        })

        self._brooklyn99 = Command({
            "alternatives": ["brooklyn99", "b99", "99"],
            "info": "Sends a random gif related to Brooklyn Nine-Nine.",
            "errors": {
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "No doubt no doubt no doubt you need no parameters for this command."
                    ]
                }
            }
        })

        self._meme = Command({
            "alternatives": ["meme"],
            "info": "Sends a random meme from Reddit.",
            "errors": {
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get a meme, you don't need any parameters."
                    ]
                },
                Category.NO_IMAGE: {
                    "messages": [
                        "Somehow there were no memes found??? Idk try again."
                    ]
                }
            }
        })

        self._nasaImage = Command({
            "alternatives": ["nasa", "NASA", "nasaImage", "NASAImage", "nasaImg", "NASAImg"],
            "info": "Gives you a random NASA image given a search term or no search term.",
            "parameters": {
                "term": {
                    "info": "The term to search for a NASA image.",
                    "optional": True
                }
            },
            "errors": {
                Category.NO_IMAGE: {
                    "messages": [
                        "There were no images matching that search. Try again or broaden your search term."
                    ]
                }
            }
        })

        self.setCommands([
            self._gif,
            self._theOffice,
            self._parksAndRec,
            self._brooklyn99,

            self._meme,

            self._nasaImage
        ])

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def gif(self, keywords):
        """Returns a gif from giphy.\n

         - keywords - The keywords to search by.\n
        """

        # Get data involving gifs from Giphy
        if keywords == "random":
            with urllib.request.urlopen(os.environ["GIPHY_RANDOM_API_URL"]) as url:
                gifData = url.read()
            gifData = json.loads(gifData)
        
        else:
            with urllib.request.urlopen(
                os.environ["GIPHY_SEARCH_API_URL"].format(
                    keywords.replace(" ", "+")
                )
            ) as url:
                gifsData = url.read()
            gifsData = json.loads(gifsData)

            # Return random embed url
            if len(gifsData) > 0:
                gifData = choose(gifsData["data"])
            else:
                return self.getErrorMessage(self._gif, Category.NO_GIFS_FOUND)
        
        return discord.Embed(
            name = "Gif Result",
            description = " ",
            color = Image.EMBED_COLOR
        ).set_image(
            url = gifData["data"]["bitly_gif_url"]
        )
        # return gifData["data"]["url"]
    
    def meme(self):
        """Returns a random meme from Reddit.\n
        """

        # Get data involving Reddit memes
        # Choose random subreddit between meme subreddits (meme, memes, dankmemes, dank_meme)
        subreddit = choose(Image.MEME_SUBREDDITS)

        redditData = requests.get(
            Image.MEME_RANDOM.format(subreddit),
            headers = {
                "User-agent": "Omega Psi"
            }
        ).json()

        # Make sure there are reddit posts
        if len(redditData["data"]["children"]) == 0:
            return self.getErrorMessage(self._meme, Category.NO_IMAGE)
        
        # Choose random reddit post
        redditPost = choose(redditData["data"]["children"])["data"]

        # Return an embed for the reddit post
        return discord.Embed(
            name = "Meme Result",
            description = "[{}]({})".format(
                redditPost["title"],
                Image.REDDIT_BASE + redditPost["permalink"]
            ),
            colour = Image.EMBED_COLOR
        ).set_image(
            url = redditPost["url"]
        ).set_footer(
            text = "👍 {} 💬 {}".format(
                redditPost["score"],
                redditPost["num_comments"]
            )
        )
    
    def nasaImage(self, keywords):
        """Returns an image from NASA.\n

         - keywords - The keywords to search by.\n
        """

        # Get data involving NASA images
        if keywords == "random":
            with urllib.request.urlopen(Image.NASA_RANDOM) as url:
                imageData = url.read()
            imageData = json.loads(imageData)

        else:
            with urllib.request.urlopen(Image.NASA_SEARCH.format(
                keywords.replace(" ", "+")
            )) as url:
                imageData = url.read()
            imageData = json.loads(imageData)

        # Check if there are no images
        if len(imageData["collection"]["items"]) == 0:
            return self.getErrorMessage(self._nasaImage, Category.NO_IMAGE)
        
        # Choose random item from collection
        item = choose(imageData["collection"]["items"])

        # Get href from item
        imageLink = item["links"][0]["href"]

        return discord.Embed(
            title = item["data"][0]["title"],
            description = item["data"][0]["description"],
            colour = Image.EMBED_COLOR
        ).set_image(
            url = imageLink
        )

        # return imageLink

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Parsing
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def on_message(self, message):
        """Parses a message and runs an Image Category command if it can.\n

        message - The Discord Message to parse.\n
        """

        # Make sure message starts with the prefix
        if Server.startsWithPrefix(message.guild, message.content) and not message.author.bot:

            # Split up into command and parameters if possible
            command, parameters = Category.parseText(Server.getPrefixes(message.guild), message.content)
            
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            # Gif Command
            if command in self._gif.getAlternatives():
                result = await self.run(message, self._gif, self.gif, " ".join(parameters) if len(parameters) > 0 else "random")

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
                        message = result
                    )
            
            # The Office Command
            elif command in self._theOffice.getAlternatives():
                
                # 0 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        message = await self.run(message, self._theOffice, self.gif, "the office")
                    )
                
                # 1 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = self.getErrorMessage(self._theOffice, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Parks and Rec Command
            elif command in self._parksAndRec.getAlternatives():
                
                # 0 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        message = await self.run(message, self._parksAndRec, self.gif, "parks and rec")
                    )
                
                # 1 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = self.getErrorMessage(self._parksAndRec, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Brooklyn 99 Command
            elif command in self._brooklyn99.getAlternatives():
                
                # 0 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        message = await self.run(message, self._brooklyn99, self.gif, "brooklyn 99")
                    )
                
                # 1 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = self.getErrorMessage(self._brooklyn99, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Meme Command
            elif command in self._meme.getAlternatives():
                result = await self.run(message, self._meme, self.meme)

                if type(result) == discord.Embed:
                    await sendMessage(
                        self.client,
                        message,
                        embed = result
                    )

            # NASA Image Command
            elif command in self._nasaImage.getAlternatives():
                result = await self.run(message, self._nasaImage, self.nasaImage, " ".join(parameters) if len(parameters) > 0 else "random")

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
                        message = result
                    )

def setup(client):
    client.add_cog(Image(client))
