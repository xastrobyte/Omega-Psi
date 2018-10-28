from category.category import Category

from util.command.command import Command
from util.file.omegaPsi import OmegaPsi
from util.utils import sendMessage

from random import choice as choose
import discord, json, os, urllib.request

class Gif(Category):

    EMBED_COLOR = 0x800080

    def __init__(self, client):
        super().__init__(client, "Gif")

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

        self.setCommands([
            self._gif,
            self._theOffice,
            self._parksAndRec,
            self._brooklyn99
        ])

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def getGif(self, keywords):
        """Returns a gif from giphy.\n

        keywords - The keywords to search by.\n
        """

        # Get data involving gifs from Giphy
        if keywords == "random":
            with urllib.request.urlopen(os.environ["GIPHY_RANDOM_API_URL"]) as url:
                gifData = url.read()
            gifData = json.loads(gifData)

            # Return embed url
            return gifData["data"]["embed_url"]
        
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
                return choose(gifsData["data"])["embed_url"]
            else:
                return self.getErrorMessage(self._gif, Category.NO_GIFS_FOUND)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Parsing
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def on_message(self, message):
        """Parses a message and runs a Gif Category command if it can.\n

        message - The Discord Message to parse.\n
        """

        # Make sure message starts with the prefix
        if Server.startsWithPrefix(message.guild, message.content) and not message.author.bot:

            # Split up into command and parameters if possible
            command, parameters = Category.parseText(Server.getPrefixes(message.guild), message.content)
            
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            # Gif Command
            if command in self._gif.getAlternatives():
                result = await self.run(message, self._gif, self.getGif, " ".join(parameters) if len(parameters) > 0 else "random")

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
                        message = await self.run(message, self._theOffice, self.getGif, "the office")
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
                        message = await self.run(message, self._parksAndRec, self.getGif, "parks and rec")
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
                        message = await self.run(message, self._brooklyn99, self.getGif, "brooklyn 99")
                    )
                
                # 1 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = self.getErrorMessage(self._brooklyn99, Category.TOO_MANY_PARAMETERS)
                    )

def setup(client):
    client.add_cog(Gif(client))
