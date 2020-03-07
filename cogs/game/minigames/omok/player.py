from asyncio import sleep, wait, FIRST_COMPLETED
from random import choice

from cogs.errors import get_error_message

from cogs.game.minigames.base_game.player import Player
from cogs.game.minigames.omok.variables import OMOK_REACTIONS, QUIT

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class OmokPlayer(Player):
    """An OmokPlayer object holds information regarding a player in the Omok minigame.

    Parameters
    ----------
        member : Member or int
            The Member defining this OmokPlayer object or
            an int clarifying this OmokPlayer object as an AI player

    Keyword Parameters
    ------------------
        is_smart : boolean
            A boolean value determining if this OmokPlayer is playing smart or random
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

        Parameters
        ----------
            game : OmokGame
                The game object that this player is connected to
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

        Parameters
        ----------
            board : OmokBoard
                The board object to process
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

        Parameters
        ----------
            board : OmokBoard
                The board object to process
            count : int
                The distance of the row to take into consideration
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

    """
    # Check horizontally
    left = right = -1
    left_count = right_count = total = 0
    add_left = add_right = True
    for offset in range(1, 5):

        # Check if the left offset reaches a space that's different from the last move
        #   or if the offset reaches the bound of the board
        if (last_column - offset <= 0 or board.board[last_row][last_column - offset] != last_move) and add_left:
            left = last_column - offset
            right = left + count + 1
            add_left = False

        # Check if the right offset reaches a space that's different from the last move
        #   of if the offset reaches the bound of the board
        if (last_column + offset >= board.width - 1 or board.board[last_row][last_column + offset] != last_move) and add_right:
            right = last_column + offset
            left = right - count
            add_right = False
        
        # There are still possibilities open to either the left or right
        left_count += 1 if add_left else 0
        right_count += 1 if add_right else 0
        total += 1 if add_left else 0 + 1 if add_right else 0
    
    # Check if the horizontal row has pieces >= the specified count
    #   only add the left or right side if they are in bounds and if
    #   the moves are not already taken
    print(left_count, right_count, count)
    if left_count + right_count + 1 >= count:
        if left >= 0 and board.board[last_row][left] == None:
            moves.append(((left_count + right_count + 1) ** count, last_row, left))
        if right <= board.width - 1 and board.board[last_row][right] == None:
            moves.append(((left_count + right_count + 1) ** count, last_row, right))
    
    # Check vertically
    up = down = 0
    up_count = down_count = total = 0
    add_up = add_down = True
    for offset in range(1, 5):

        # Check if the up offset reaches a space that's different from the last move
        #   or if the offset reaches the bound of the board
        if last_row - offset <= 0 and add_up:
            up = last_row - offset
            down = up + count + 1
            add_up = False

        # Check if the right offset reaches a space that's different from the last move
        #   of if the offset reaches the bound of the board
        if (last_row + offset >= board.height - 1 or board.board[last_row + offset][last_column] != last_move) and add_down:
            down = last_row + offset
            up = down - count
            add_down = False
        
        # There are still possibilities open to either up or down
        up_count += 1 if add_up else 0
        down_count += 1 if add_down else 0
        total += 1 if add_up else 0 + 1 if add_down else 0

    # Check if the vertical column has pieces >= the specified count
    #   only add the up or down side if they are in bounds and if
    #   the moves are not already taken
    if up_count + down_count + 1 >= count:
        if up >= 0 and board.board[up][last_column] == None:
            moves.append(((up_count + down_count + 1) ** count, up, last_column))
        if down <= board.height - 1 and board.board[down][last_column] == None:
            moves.append(((up_count + down_count + 1) ** count, down, last_column))

    # Check left_upper to right_lower diagonal
    left_upper = right_lower = (0, 0)
    left_upper_count = right_lower_count = 0
    add_left_upper = add_right_lower = True
    for offset in range(1, 5):

        # Check if the left upper offset reaches a space that's different from the last move
        #   or if the offset reaches the bound of the board
        if (last_column - offset <= 0 or last_row - offset <= 0 or board.board[last_row - offset][last_column - offset] != last_move) and add_left_upper:
            left_upper = (last_row - offset, last_column - offset)
            right_lower = (left_upper[0] + count + 1, left_upper[1] + count + 1)
            add_left_upper = False

        # Check if the right lower offset reaches a space that's different from the last move
        #   of if the offset reaches the bound of the board
        if (last_column + offset >= board.width - 1 or last_row + offset >= board.height - 1 or board.board[last_row + offset][last_column + offset] != last_move) and add_right_lower:
            right_lower = (last_row + offset, last_column + offset)
            left_upper = (right_lower[0] - count + 1, right_lower[1] - count + 1)
            add_right_lower = False
        
        # There are still possibilities open to either left upper or right lower
        left_upper_count += 1 if add_left_upper else 0
        right_lower_count += 1 if add_right_lower else 0

    # Check if the descending diagonal has pieces >= the specified count
    #   only add the left upper or right lower side if they are in bounds and if
    #   the moves are not already taken
    if left_upper_count + right_lower_count + 1 >= count:
        if left_upper[0] >= 0 and left_upper[1] >= 0 and board.board[left_upper[0]][left_upper[1]] == None:
            moves.append(((left_upper_count + right_lower_count + 1) ** count, left_upper[0], left_upper[1]))
        if right_lower[0] <= board.height - 1 and right_lower[1] <= board.width - 1 and board.board[right_lower[0]][right_lower[1]] == None:
            moves.append(((left_upper_count + right_lower_count + 1) ** count, right_lower[0], right_lower[1]))

    # Check left_lower to right_upper diagonal
    left_lower = right_upper = (0, 0)
    left_lower_count = right_upper_count = 0
    add_left_lower = add_right_upper = True
    for offset in range(1, 5):

        # Check if the left lower offset reaches a space that's different from the last move
        #   or if the offset reaches the bound of the board
        if (last_column - offset <= 0 or last_row + offset >= board.height - 1 or board.board[last_row + offset][last_column - offset] != last_move) and add_left_lower:
            left_lower = (last_row + offset, last_column - offset)
            right_upper = (left_lower[0] - count - 1, left_lower[1] + count + 1)
            add_left_lower = False
        
        # Check if the right upper offset reaches a space that's different from the last move
        #   or if the offset reaches the bound of the board
        if (last_column + offset >= board.width - 1 or last_row - offset <= 0 or board.board[last_row - offset][last_column + offset] != last_move) and add_right_upper:
            right_upper = (last_row - offset, last_column + offset)
            left_lower = (right_upper[0] + count - 1, right_upper[1] - count + 1)
            add_right_upper = False
        
        # There are still possibilities open to either left lower or right upper
        left_lower_count += 1 if add_left_lower else 0
        right_upper_count += 1 if add_right_upper else 0

    # Check if the ascending diagonal has pieces >= the specified count
    #   only add the left lower or right upper side if they are in bounds and if
    #   the moves are not already taken
    if left_lower_count + right_upper_count + 1 >= count:
        if left_lower[0] <= board.height - 1 and left_lower[1] >= 0 and board.board[left_lower[0]][left_lower[1]] == None:
            moves.append(((left_lower_count + right_upper_count + 1) ** count, left_lower[0], left_lower[1]))
        if right_upper[0] >= 0 and right_upper[1] <= board.width - 1 and board.board[right_upper[0]][right_upper[1]] == None:
            moves.append(((left_lower_count + right_upper_count + 1) ** count, right_upper[0], right_upper[1]))
    """
