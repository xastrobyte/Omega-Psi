from util.file.database import loop
from util.file.server import Server
from util.file.omegaPsi import OmegaPsi
from util.rank.image import createRankImage

from util.utils.discordUtils import sendMessage, getErrorMessage

from supercog import Category, Command
import discord, math, os

scrollEmbeds = {}

class Rank(Category):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Errors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    INVALID_INTERACTION = "INVALID_INTERACTION"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Constructor
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, client):
        super().__init__(
            client, 
            "Rank",
            description = "The ranking system is strong with this category.",
            embed_color = 0x008080,
            server_category = True,
            locally_inactive_error = Server.getInactiveError,
            globally_inactive_error = OmegaPsi.getInactiveError,
            locally_active_check = Server.isCommandActive,
            globally_active_check = OmegaPsi.isCommandActive
        )

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Commands
        self._rank = Command(commandDict = {
            "alternatives": ["rank", "r"],
            "info": "Shows you your current level and experience in this server.",
            "run_in_private": False,
            "errors": {
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "When you are getting your ranking card, you don't need any parameters."
                    ]
                }
            },
            "command": self.rank
        })

        self._levelUp = Command(commandDict = {
            "alternatives": ["levelUp"],
            "info": "Shows you how many profane words, reactions, or normal messages you need to send to level up.",
            "run_in_private": False,
            "parameters": {
                "interaction": {
                    "info": "The type of interaction to check the number of until you level up.",
                    "optional": True,
                    "accepted_parameters": {
                        "profanity": {
                            "alternatives": ["profanity", "profane"],
                            "info": "Check how many profane words you need to level up."
                        },
                        "reactions": {
                            "alternatives": ["reactions", "reacts"],
                            "info": "Check how many reactions you need to level up."
                        },
                        "normal": {
                            "alternatives": ["normal", "basic"],
                            "info": "Check how many regular messages you need to send to level up."
                        }
                    }
                }
            },
            "errors": {
                Rank.INVALID_INTERACTION: {
                    "messages": [
                        "That is not a valid interaction type to check."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        " When you are getting your level up info, you don't need more than just the inquiry."
                    ]
                }
            },
            "command": self.levelUp
        })

        self.setCommands({
            self._rank,
            self._levelUp
        })
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def rank(self, message, parameters):
        """Returns an image displaying the rank of the member in this server.\n

        discordMember - The member to get the rank of.\n
        """

        # Check for too many parameters
        if len(parameters) > self._rank.getMaxParameters():
            result = getErrorMessage(self._rank, Rank.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            result = await loop.run_in_executor(None,
                createRankImage,
                message.author
            )

        # Check for an error
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

            # Send rank image and remove
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def levelUp(self, message, parameters):
        """Returns the amount of different interactions a Discord Member needs to level up.

        Parameters:
            discordMember (discord.Member): The Discord Member to get the interactions of.
            interactionType (str): The type of interaction to get.
        """

        # Check for too many parameters
        if len(parameters) > self._levelUp.getMaxParameters():
            embed = getErrorMessage(self._levelUp, Rank.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            interactionType = None if len(parameters) == 0 else parameters[0]

            # Get member info from server
            member = Server.getMember(message.guild, message.author)

            # Get member's current and next experience
            currentExp = member["experience"]
            nextExp = Server.getExpFromLevel(member["level"] + 1)

            # Get each interaction type before checking the interaction type
            profanity = math.ceil(
                (nextExp - currentExp) / (Server.PROFANE_XP + Server.NORMAL_XP)
            )
            reactions = math.ceil(
                (nextExp - currentExp) / Server.REACTION_XP
            )
            normal = math.ceil(
                (nextExp - currentExp) / Server.NORMAL_XP
            )

            # Check if interaction type is None; Get all stats
            if interactionType == None:
                embed = discord.Embed(
                    title = "In order to level up, you need either",
                    description = "{} Profane Messages\nor\n{} Reactions\nor\n{} Regular Messages".format(
                        profanity, reactions, normal
                    ),
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )
            
            # Check if interaction type is valid
            if interactionType in self._levelUp.getAcceptedParameter("interaction", "profanity").getAlternatives():
                embed = discord.Embed(
                    title = "In order to level up, you need",
                    description = "{} Profane Messages".format(profanity),
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )
            
            elif interactionType in self._levelUp.getAcceptedParameter("interaction", "reactions").getAlternatives():
                embed = discord.Embed(
                    title = "In order to level up, you need",
                    description = "{} Reactions".format(profanity),
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )
            
            elif interactionType in self._levelUp.getAcceptedParameter("interaction", "normal").getAlternatives():
                embed = discord.Embed(
                    title = "In order to level up, you need",
                    description = "{} Regular Messages".format(profanity),
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )
            
            # Interaction type is invalid; error
            else:
                embed = getErrorMessage(self._levelUp, Rank.INVALID_INTERACTION)
        
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
        """Parses a message and runs a Rank Category command if it can.\n

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
    client.add_cog(Rank(client))