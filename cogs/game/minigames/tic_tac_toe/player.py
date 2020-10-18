from asyncio import sleep, wait, FIRST_COMPLETED
from random import choice

from cogs.game.minigames.base_game.alpha_beta import alpha_beta
from cogs.game.minigames.base_game.player import Player
from cogs.game.minigames.tic_tac_toe.variables import TIC_TAC_TOE_REACTIONS, QUIT

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class TicTacToePlayer(Player):
    """A TicTacToePlayer object holds information regarding a player in the Tic Tac Toe minigame.

    :param member: The Member defining this TicTacToePlayer object or
        an int clarifying this TicTacToePlayer object as an AI player

    :param is_smart: A boolean value determining if this OmokPlayer is playing smart or random
        Note: this only applies to AI players and is only set to True or False if
        this player is an AI player
    """
    
    def __init__(self, member, *, is_smart = None):
        super().__init__(
            member = member, 
            is_smart = is_smart
        )
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Play Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def process_turn(self, game):
        """Processes the current turn for this player by waiting until they
        react to make their move or, if this player is an AI, choosing the best place
        to go

        :param game: The game object that this player is connected to
        """

        # Check if the player is an AI
        if self.is_ai:

            # Check if the AI is smart
            if self.is_smart:

                # Determine the best place to go using the alpha-beta pruning algorithm
                #   if the AI goes first in the game, the AI will choose a random place to go
                #   every turn after that uses alpha-beta
                if len(game.board.get_legal_moves()) == 9:
                    move = choice(game.board.get_legal_moves())
                else:
                    move = alpha_beta(game.board, False, max_depth = 8)[1]
            
            # The AI is not smart
            else:
                move = choice(game.board.get_legal_moves())
            game.board.make_move(*move, False)

            # Use a sleep function to simulate decision making
            await sleep(1)
            return None
        
        # The player is not an AI, wait for them to choose a place to go
        else:
            
            # Wait for the player to react with the spot they want to go
            def check_reaction(reaction, user):
                return (
                    reaction.message.id == game.message.id and
                    user.id == self.member.id and
                    str(reaction) in game.get_valid_reactions()
                )
            done, pending = await wait([
                game.bot.wait_for("reaction_add", check = check_reaction),
                game.bot.wait_for("reaction_remove", check = check_reaction)
            ], return_when = FIRST_COMPLETED)
            reaction, user = done.pop().result()
            for future in pending:
                future.cancel()

            # Check if the player wants to QUIT the TicTacToeGame
            if str(reaction) == QUIT:
                return TicTacToePlayer.QUIT
            
            # The player does not want to quit, make their requested move
            else:
                index = TIC_TAC_TOE_REACTIONS.index(str(reaction))
                game.board.make_move(index // 3, index % 3, game.challenger_turn)
                return None
