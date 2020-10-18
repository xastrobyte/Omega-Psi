from discord import Embed

from cogs.globals import PRIMARY_EMBED_COLOR
from cogs.game.minigames.base_game.turn import Turn

from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class KingsCupTurn(Turn):

    def __init__(self, game):
        super().__init__(game)
    
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
            title = "{} is the Dealer!".format(self.player.get_name()),
            description = "\n".join(self.actions),
            colour = await get_embed_color(self.player.member) if not self.player.is_ai else PRIMARY_EMBED_COLOR
        )

        # Add the rules field if there are any rules
        if len(self.game.rules) > 0:
            embed.add_field(
                name = "Rules",
                value = "\n".join([ rule for rule in self.game.rules ])
            )

        # Check if there is no message found
        if not self.message:
            self.message = await self.game.ctx.send(embed = embed)
        
        # A message was found, update it
        else:
            await self.message.edit(embed = embed)