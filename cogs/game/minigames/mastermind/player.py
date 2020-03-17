from asyncio import wait, FIRST_COMPLETED
from discord import Embed
from random import choice

from cogs.game.minigames.base_game.player import Player
from cogs.game.minigames.mastermind.variables import PEGS

from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class MastermindPlayer(Player):
    """A MastermindPlayer object holds information regarding a player in the Mastermind minigame.

    Keyword Parameters
    ------------------
        member : discord.Member
            The discord.Member defining this MastermindPlayer object
    """

    def __init__(self, member):
        super().__init__(member = member)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Play Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def ask_for_code(self, game):
        """Has the player ask for the code for a Mastermind game

        Parameters
        ----------
            game : MastermindGame
                The game object this player is connected to
        """
        
        # The player is an AI (as of right now, the setup player will always be an AI)
        code = ""
        for i in range(4):
            color = choice(PEGS)
            while color in code:
                color = choice(PEGS)
            code += color
        return code
    
    async def ask_for_guess(self, game):
        """Asks the player to make their guess in a Mastermind game

        Parameters
        ----------
            game : MastermindGame
                The game object this player is connected to
        """
        
        # The player is a real person
        guess = ""

        # Continue to ask the player for a color until 4 colors have been chosen
        if game.message is None:
            game.message = await game.ctx.send(
                embed = Embed(
                    title = "Mastermind",
                    description = "{}\n\nYour Guess: {}".format(
                        game.get_guesses(),
                        guess
                    ),
                    colour = await get_embed_color(self.member)
                )
            )
            for peg in PEGS:
                await game.message.add_reaction(peg)
        for i in range(4):

            # Wait for the player's reaction
            done, pending = await wait([
                game.bot.wait_for("reaction_add", check = lambda reaction, user : (
                    reaction.message.id == game.message.id and
                    user.id == self.id and
                    str(reaction) in PEGS
                )),
                game.bot.wait_for("reaction_remove", check = lambda reaction, user : (
                    reaction.message.id == game.message.id and
                    user.id == self.id and
                    str(reaction) in PEGS
                ))
            ], return_when = FIRST_COMPLETED)
            reaction, user = done.pop().result()
            for future in pending:
                future.cancel()
            
            # Update the message with the user's current guess
            guess += str(reaction)
            await game.message.edit(
                embed = Embed(
                    title = "Mastermind",
                    description = "{}\n\nYour Guess: {}".format(
                        game.get_guesses(),
                        guess
                    ),
                    colour = await get_embed_color(self.member)
                )
            )
        
        return guess
                