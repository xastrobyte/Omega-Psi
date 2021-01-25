from random import randint

from cogs.game.minigames.base_game.game import Game

class BlackBoxGame(Game):
    """A BlackBoxGame contains information about a game of
    Black Box being played
    """
    def __init__(self, bot, ctx, challenger, opponent):
        super().__init__(
            bot, ctx,
            challenger = challenger,
            opponent = opponent
        )
        self.current_player = 0
        self.locations = []
        for locations in range(4):
            location = [ randint(1, 8), randint(1, 8) ]
            if location not in self.locations:
                self.locations.append(location)
        self.message = None
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def play(self):
        """Allows the player to play a game of Black Box"""
        pass