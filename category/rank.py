from category.category import Category

from util.command.command import Command
from util.file.omegaPsi import OmegaPsi
from util.file.server import Server
from util.level.image import createRankImage

from util.utils import sendMessage

import os

class Rank(Category):

    EMBED_COLOR = 0x008080

    def __init__(self, client):
        super().__init__(client, "Rank")

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Commands
        self._rank = Command({
            "alternatives": ["rank", "r"],
            "info": "Shows you your current level and experience in this server.",
            "errors": {
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "When you are getting your level, you don't need any parameters."
                    ]
                }
            }
        })

        self.setCommands({
            self._rank
        })
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def getRank(self, discordMember):
        """Returns an image displaying the rank of the member in this server.\n

        discordMember - The member to get the rank of.\n
        """

        # Get member info from server
        member = Server.getMember(discordMember.guild, discordMember)

        # Get and return the rank image file for the member
        return createRankImage(member)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Parsing
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def on_message(self, message):
        """Parses a message and runs a Rank Category command if it can.\n

        message - The Discord Message to parse.\n
        """

        # Make sure message starts with the prefix
        if message.content.startswith(OmegaPsi.PREFIX) and not message.author.bot:

            # Split up into command and parameters if possible
            command, parameters = Category.parseText(message.content)
            
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            # Rank Command
            if command in self._rank.getAlternatives():

                # 0 Parameters Exist
                if len(parameters) == 0:

                    imageSource = await self.run(message, self._rank, self.getRank, message.author)
                    
                    if type(imageSource) == str:
                        await sendMessage(
                            self.client,
                            message,
                            filename = imageSource
                        )
                        os.remove(imageSource) # Remove the image, we don't want to keep it in the file system
                    
                    else:
                        await sendMessage(
                            self.client,
                            message,
                            embed = imageSource
                        )
                
                # 1 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = self.getErrorMessage(self._rank, Category.TOO_MANY_PARAMETERS)
                    )

def setup(client):
    client.add_cog(Rank(client))