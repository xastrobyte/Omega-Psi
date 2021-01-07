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
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #