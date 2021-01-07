from cogs.game.minigames.base_game.game import Game

class CheckersGame(Game):
    """A CheckersGame contains information about a checkers game
    being played
    """
    def __init__(self, bot, ctx, challenger, opponent):
        super().__init__(
            bot, ctx,
            challenger = challenger,
            opponent = opponent
        )
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #