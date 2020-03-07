from asyncio import sleep, wait, FIRST_COMPLETED
from random import randint

from cogs.game.minigames.base_game.player import Player
from cogs.game.minigames.connect_four.variables import CONNECT_FOUR_REACTIONS, QUIT

class ConnectFourPlayer(Player):
    """A Player object that holds the important information for other possible game instances
    used in Omega Psi. When given a `str`, the player is set as an AI player.

    Keyword Parameters
    ------------------
        member : discord.Member or str
            The discord.Member defining this Player object or
            a str clarifying this Player object as an AI player
        is_smart : boolean
            A boolean value determining if this Player is playing smart or random
            Note: this only applies to AI players and is only set to True or False if
                    this player is an AI player
    """

    COLUMN_FULL = "COLUMN_FULL"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

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

        Parameters
        ----------
            game : ConnectFourGame
                The game object that this player is connected to
        """

        # Check if the player is an AI
        if self.is_ai:
            
            # Determine the best place to go and return the location
            #   Use a sleep function to simulate decision making
            await sleep(1)
            self.determine_best_move(game.board)
            return None
        
        # The player is not an AI
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

            # Check if the player wants to QUIT the ConnectFourGame
            if str(reaction) == QUIT:
                return ConnectFourPlayer.QUIT
            
            # The player does not want to quit, make their requested move
            else:
                
                # Check if the column is full
                if game.board.is_column_full(CONNECT_FOUR_REACTIONS.index(str(reaction))):
                    return ConnectFourPlayer.COLUMN_FULL
                
                # The column is not full, let the player go there
                else:
                    game.board.add_piece(CONNECT_FOUR_REACTIONS.index(str(reaction)), is_challenger = game.challenger_turn)
                    return None

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Other Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def determine_best_move(self, board):
        """Determines the best move for an AI to go to given the current board's state
        If no best move is found, a random move is returned.

        Parameters
        ----------
            board : ConnectFourBoard
                The board to determine a best move from
        
        Returns
        -------
            int
                The move that the AI will take
        """

        # Check if the AI is smart, run a smart version of the AI
        if self.is_smart:

            # Iterate through every column
            #   keep track of any restricted moves (moves that may cause the challenger to win)
            #   and keep track of the final result of where the AI should move
            restricted = []
            ai_move = -1
            for column in range(board.width):

                # Create two copies of the board to emulate AI moves and player moves
                ai_copy = board.copy()
                player_copy = board.copy()

                # Check if the current column is full, move onto the next column
                if board.is_column_full(column):
                    continue
                
                # Column is not full; Emulate AI and player moves at this column
                ai_copy.add_piece(column, is_challenger = False)  # AI move
                player_copy.add_piece(column, is_challenger = True) # Player move

                # Check if either the ai_copy or player_copy has a win in it
                ai_win_check = ai_copy.check_for_winner()
                player_win_check = player_copy.check_for_winner()

                # If either board has a win in it, make that the AI move
                #   if the player would go to this current column in their next move
                #       they would win, the AI should try to stop it
                #   if the ai would go to this current column in its next move
                #       they would win, the AI should immediately go here
                if ai_win_check == False or player_win_check == True:
                    ai_move = column
                    break
                
                # Neither of the moves would win in either board, 
                #   emulate the next moves on the same column
                else:

                    # Check if the column is full, move onto the next column
                    if ai_copy.is_column_full(column):
                        continue
                    
                    # Column is not full, emulate the player move on the AI copy
                    ai_copy.add_piece(column, is_challenger = True)

                    # Check if the player would win; If so, do not let the AI go to this column
                    player_win_check = ai_copy.check_for_winner()
                    if player_win_check == True:
                        restricted.append(column)
            
            # There has been no ai_move generated yet
            #   generate a random column
            if ai_move == -1:

                # Check if the board is full, there must be a draw
                if board.is_board_full():
                    return False
                
                # The board is not full, generate a random column that is not full
                while True:
                    ai_move = randint(0, board.width - 1)

                    # Check if the column is full, continue generating a random column
                    if board.is_column_full(ai_move):
                        continue
                    
                    # Check to see if this is the only available column to go to
                    #   or check to see if this column is a restricted move
                    elif board.board[0].count(None) == 1 or len(restricted) == board.board[0].count(None):
                        break
                    
                    # Check to see if the move is not a restricted move
                    elif ai_move not in restricted:
                        break
        
        # The AI is not smart, choose a random place
        else:
            ai_move = randint(0, board.width - 1)
            while board.is_column_full(ai_move):
                ai_move = randint(0, board.width - 1)
            
        # Make the AI go to its chosen move
        board.add_piece(ai_move, is_challenger = False)
        return True

