from util.file.server import Server
from util.file.omegaPsi import OmegaPsi
from util.rank.image import createRankImage

from util.utils import sendMessage, getErrorMessage, run

from supercog import Category, Command
import discord, math, os

class Rank(Category):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    EMBED_COLOR = 0x008080

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
            }
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
            }
        })

        self.setCommands({
            self._rank,
            self._levelUp
        })
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def rank(self, discordMember):
        """Returns an image displaying the rank of the member in this server.\n

        discordMember - The member to get the rank of.\n
        """

        # Get and return the rank image file for the member
        return createRankImage(discordMember)
    
    def levelUp(self, discordMember, interactionType = None):
        """Returns the amount of different interactions a Discord Member needs to level up.

        Parameters:
            discordMember (discord.Member): The Discord Member to get the interactions of.
            interactionType (str): The type of interaction to get.
        """

        # Get member info from server
        member = Server.getMember(discordMember.guild, discordMember)

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
            return discord.Embed(
                title = "In order to level up, you need either",
                description = "{} Profane Messages\nor\n{} Reactions\nor\n{} Regular Messages".format(
                    profanity, reactions, normal
                ),
                colour = Rank.EMBED_COLOR
            )
        
        # Check if interaction type is valid
        if interactionType in self._levelUp.getAcceptedParameter("interaction", "profanity").getAlternatives():
            return discord.Embed(
                title = "In order to level up, you need",
                description = "{} Profane Messages".format(profanity),
                colour = Rank.EMBED_COLOR
            )
        
        elif interactionType in self._levelUp.getAcceptedParameter("interaction", "reactions").getAlternatives():
            return discord.Embed(
                title = "In order to level up, you need",
                description = "{} Reactions".format(profanity),
                colour = Rank.EMBED_COLOR
            )
        
        elif interactionType in self._levelUp.getAcceptedParameter("interaction", "normal").getAlternatives():
            return discord.Embed(
                title = "In order to level up, you need",
                description = "{} Regular Messages".format(profanity),
                colour = Rank.EMBED_COLOR
            )
        
        # Interaction type is invalid; error
        return getErrorMessage(self._levelUp, Rank.INVALID_INTERACTION)

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

            # Rank Command
            if command in self._rank.getAlternatives():

                # 0 Parameters Exist
                if len(parameters) == 0:

                    imageSource = await run(message, self._rank, self.rank, message.author)
                    
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
                        embed = getErrorMessage(self._rank, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Level Up Command
            elif command in self._levelUp.getAlternatives():

                # 0 or 1 Parameter Exists
                if len(parameters) in [0, 1]:

                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._levelUp, self.levelUp, message.author, None if len(parameters) == 0 else parameters[0])
                    )
                
                # 2 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._levelUp, Category.TOO_MANY_PARAMETERS)
                    )

def setup(client):
    client.add_cog(Rank(client))
