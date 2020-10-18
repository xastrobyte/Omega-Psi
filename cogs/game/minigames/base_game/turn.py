from discord import Embed

from cogs.globals import PRIMARY_EMBED_COLOR

from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class Turn:
    """A Turn object that holds the information about any turn's in a game.

    :param game: The game object that this Turn is connected to
    :param player: The player that this Turn object is directly connected to
            Note that if None is given, the player will automatically be grabbed from the
            game's current player
    """
    
    def __init__(self, game, player = None):
        self.game = game
        self.message = None
        self.player = player if player else game.get_current_player()
        self.actions = []

    # # # # # # # # # # # # # # # # # # # #
    # Getters
    # # # # # # # # # # # # # # # # # # # #

    @property
    def game(self):
        return self.__game
    
    @property
    def message(self):
        return self.__message
    
    @property
    def player(self):
        return self.__player

    @property
    def actions(self):
        return self.__actions

    # # # # # # # # # # # # # # # # # # # #
    # Setters
    # # # # # # # # # # # # # # # # # # # #

    @game.setter
    def game(self, game):
        self.__game = game
    
    @message.setter
    def message(self, message):
        self.__message = message
    
    @player.setter
    def player(self, player):
        self.__player = player

    @actions.setter
    def actions(self, actions):
        self.__actions = actions

    # # # # # # # # # # # # # # # # # # # #
    # Other Methods
    # # # # # # # # # # # # # # # # # # # #
    
    async def add_action(self, action):
        """Adds the specified action to the Turn's action log
        and updates the message for it.
        If no message is found, a new message is created

        :param action: The action of this turn
        """
        self.actions.append(action)

        # Create the embed for the turn
        #   and add a footer at the end for the current player's amount of money
        embed = Embed(
            title = "{}'s Turn!".format(self.player.get_name()),
            description = "\n".join(self.actions),
            colour = await get_embed_color(self.player.member) if not self.player.is_ai else PRIMARY_EMBED_COLOR
        )

        # Check if there is no message found
        if not self.message:
            self.message = await self.game.ctx.send(embed = embed)
        
        # A message was found, update it
        else:
            await self.message.edit(embed = embed)
