from asyncio import sleep, wait, FIRST_COMPLETED
from random import choice

from cogs.errors import get_error_message

from cogs.game.minigames.base_game.player import Player
from cogs.game.minigames.omok.variables import OMOK_REACTIONS, QUIT

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class OmokPlayer(Player):
    """An OmokPlayer object holds information regarding a player in the Omok minigame.

    :param member: The Member defining this OmokPlayer object or
        an int clarifying this OmokPlayer object as an AI player

    :param is_smart: A boolean value determining if this OmokPlayer is playing smart or random
        Note: this only applies to AI players and is only set to True or False if
        this player is an AI player
    """
    
    def __init__(self, member, *, is_smart = None):
        super().__init__(
            member = member, 
            is_smart = is_smart
        )
        self.moves = []
    
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
                move = self.determine_best_move(game)
            
            # The AI is not smart
            else:
                move = choice(game.board.get_legal_moves())
            self.moves.insert(0, move)
            game.board.make_move(*move, False)

            # Use a sleep function to simulate decision making
            await sleep(1)
            return None
        
        # The player is not an AI, wait for them to choose a place to go
        else:
            row = column = -1
            
            while True:

                # Wait for the player to react with the row and column they want to go to
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

                # Check if the player wants to QUIT the OmokGame
                if str(reaction) == QUIT:
                    return OmokPlayer.QUIT
                
                # The player does not want to quit, let them choose their row and column
                else:

                    # Check if the player needs to choose a colum
                    if column == -1:
                        column = OMOK_REACTIONS.index(str(reaction))
                    else:
                        row = OMOK_REACTIONS.index(str(reaction))

                        # Make sure this move is legal
                        if (row, column) in game.board.get_legal_moves():
                            break
                        
                        # The move is not legal
                        else:
                            row = column = -1
                            await game.ctx.send(
                                embed = get_error_message("That row and column is already occupied! Choose a new place."),
                                delete_after = 5
                            )
        
            # Make the players requested move
            self.moves.insert(0, (row, column))
            game.board.make_move(row, column, game.challenger_turn)
            return None
    
    def determine_best_move(self, game):
        """Determines the best move for the AI to go to 
        depending on the Player's last move in the specified board

        :param game: The game to use to determine the best move
        """

        move = None

        # Check if there are good moves for the AI and player
        for row_count in range(5, 1, -1):

            # Get all effective AI moves
            #   if there are any for this row_count, make the move
            ai_moves = sorted([
                move
                for move in self.find_effective_moves(game, row_count, for_player = False)
                if move[1:] in game.board.get_legal_moves()
            ], reverse = True, key = lambda move: move[0])

            # Get all effective player moves
            #   if there are any for this row_count, make the move
            player_moves = sorted([
                move
                for move in self.find_effective_moves(game, row_count, for_player = True)
                if move[1:] in game.board.get_legal_moves()
            ], reverse = True, key = lambda move: move[0])
            
            # Combine all effective moves to get the best one
            all_moves = sorted([
                move
                for move in (ai_moves + player_moves)
                if move[1:] in game.board.get_legal_moves()
            ], reverse = True, key = lambda move: move[0])
            if len(all_moves) != 0:
                return all_moves[0][1:]

        # No move has been found yet, choose a random move
        if not move:
            move = choice(game.board.get_legal_moves())
        return move

    def find_effective_moves(self, game, count, *, for_player = True):
        """Finds effective moves the AI could make by trying to block the player
        on either sides of a possible row given the length of the row

        :param game: The game to use to find the most effective move
        :param count: The distance of the row to take into consideration
        :param for_player: Whether or not to find effective moves for a player
        """

        moves = []

        # Iterate through all moves made by the player/ai
        board = game.board
        if for_player:
            search_moves = game.challenger.moves
        else:
            search_moves = game.opponent.moves

        for last_move in search_moves:
            last_row, last_column = last_move

            # Check horizontals
            left_total = right_total = 0
            open_moves = {"left": [], "right": []}
            for offset in range(1, count):
                if last_column - offset >= 0:
                    if board.board[last_row][last_column - offset] == for_player: 
                        left_total += 1
                    elif board.board[last_row][last_column - offset] == None: 
                        open_moves["left"].append(((5 - offset) * left_total, last_row, last_column - offset))
                if last_column + offset <= board.width - 1:
                    if board.board[last_row][last_column + offset] == for_player: 
                        right_total += 1
                    elif board.board[last_row][last_column + offset] == None: 
                        open_moves["right"].append(((5 - offset) * right_total, last_row, last_column + offset))
            if left_total > 0:
                for move in open_moves["left"]:
                    moves.append((move[0] ** (left_total * count), *move[1:]))
            if right_total > 0:
                for move in open_moves["right"]:
                    moves.append((move[0] ** (right_total * count), *move[1:]))

            # Check verticals
            left_total = right_total = 0
            open_moves = {"left": [], "right": []}
            for offset in range(1, count):
                if last_row - offset >= 0:
                    if board.board[last_row - offset][last_column] == for_player: 
                        left_total += 1
                    elif board.board[last_row - offset][last_column] == None: 
                        open_moves["left"].append(((5 - offset) * left_total, last_row - offset, last_column))
                if last_row + offset <= board.height - 1:
                    if board.board[last_row + offset][last_column] == for_player: 
                        right_total += 1
                    elif board.board[last_row + offset][last_column] == None: 
                        open_moves["right"].append(((5 - offset) * right_total, last_row + offset, last_column))
            if left_total > 0:
                for move in open_moves["left"]:
                    moves.append((move[0] ** (left_total * count), *move[1:]))
            if right_total > 0:
                for move in open_moves["right"]:
                    moves.append((move[0] ** (right_total * count), *move[1:]))

            # Check ascending diagonal
            left_total = right_total = 0
            open_moves = {"left": [], "right": []}
            for offset in range(1, count):
                if last_row - offset >= 0 and last_column - offset >= 0:
                    if board.board[last_row - offset][last_column - offset] == for_player: 
                        left_total +=1
                    elif board.board[last_row - offset][last_column - offset] == None: 
                        open_moves["left"].append(((5 - offset) * left_total, last_row - offset, last_column - offset))
                if last_row + offset <= board.height - 1 and last_column + offset <= board.width - 1:
                    if board.board[last_row + offset][last_column + offset] == for_player: 
                        right_total += 1
                    elif board.board[last_row + offset][last_column + offset] == None: 
                        open_moves["right"].append(((5 - offset) * right_total, last_row + offset, last_column - offset))
            if left_total > 0:
                for move in open_moves["left"]:
                    moves.append((move[0] ** (left_total * count), *move[1:]))
            if right_total > 0:
                for move in open_moves["right"]:
                    moves.append((move[0] ** (right_total * count), *move[1:]))

            # Check descending diagonal
            left_total = right_total = 0
            open_moves = {"left": [], "right": []}
            for offset in range(1, count):
                if last_row + offset <= board.height - 1 and last_column - offset >= 0:
                    if board.board[last_row + offset][last_column - offset] == for_player: 
                        left_total +=1
                    elif board.board[last_row + offset][last_column - offset] == None: 
                        open_moves["left"].append(((5 - offset) * left_total, last_row + offset, last_column - offset))
                if last_row - offset >= 0 and last_column + offset <= board.width - 1:
                    if board.board[last_row - offset][last_column + offset] == for_player: 
                        right_total += 1
                    elif board.board[last_row - offset][last_column + offset] == None: 
                        open_moves["right"].append(((5 - offset) * right_total, last_row - offset, last_column - offset))
            if left_total > 0:
                for move in open_moves["left"]:
                    moves.append((move[0] ** (left_total * count), *move[1:]))
            if right_total > 0:
                for move in open_moves["right"]:
                    moves.append((move[0] ** (right_total * count), *move[1:]))

        return moves
