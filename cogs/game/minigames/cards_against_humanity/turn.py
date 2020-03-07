from discord import Embed

from cogs.globals import PRIMARY_EMBED_COLOR

from cogs.game.minigames.base_game.turn import Turn

from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class CardsAgainstHumanityTurn(Turn):
    """A CardsAgainstHumanityTurn keeps track of actions that happen during a judge's turn
    the current player of the game is the judge of the game

    Parameters
    ----------
        game : CardsAgainstHumanityGame
            The game object that this Turn is connected to
        player : CardsAgainstHumanityPlayer or None
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
        self.actions = [action]

        # Create the embed for the turn
        #   and add a footer at the end for the current player's amount of money
        embed = Embed(
            title = "Round {}".format(self.game.round),
            description = "\n".join(self.actions),
            colour = await get_embed_color(self.player.member)
        ).add_field(
            name = "Scores",
            value = "\n".join([
                "*{}* - **{}**".format(
                    player.get_name(), player.wins
                )
                for player in self.game.players
            ])
        )

        # Check if there is no message found
        if not self.message:
            self.message = await self.game.ctx.send(embed = embed)
        
        # A message was found, update it
        else:
            await self.message.edit(embed = embed)

