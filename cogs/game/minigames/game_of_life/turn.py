from discord import Embed

from cogs.globals import PRIMARY_EMBED_COLOR

from cogs.game.minigames.base_game.turn import Turn

from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class GameOfLifeTurn(Turn):
    """A GameOfLifeTurn object that holds the information about a turn in the game

    Parameters
    ----------
        game : GameOfLifeGame
            The game object that this Turn is connected to
        player : GameOfLifePlayer or None
            The player that this Turn object is directly connected to
            Note that if None is given, the player will automatically be grabbed from the
            game's current player
    """

    def __init__(self, game, player = None):
        super().__init__(game, player)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Other Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def add_action(self, action):
        """Adds the specified action to the Turn's action log
        and updates the message for it.
        If no message is found, a new message is created

        Parameters
        ----------
            action : str
                The action of this turn
        """
        self.actions.append(action)

        # Create the embed for the turn
        #   and add a footer at the end for the current player's amount of money
        embed = Embed(
            title = "{}'s Turn!".format(self.player.get_name()),
            description = "\n".join(self.actions),
            colour = await get_embed_color(self.player.member) if not self.player.is_ai else PRIMARY_EMBED_COLOR
        ).set_footer(
            text = "{} has ${:0,}".format(
                self.player.get_name(),
                self.player.cash
            )
        )

        # Check if there is no message found
        if not self.message:
            self.message = await self.game.ctx.send(embed = embed)
        
        # A message was found, update it
        else:
            await self.message.edit(embed = embed)