from random import randint

class ConnectFour:

    DRAW = "DRAW"
    COLUMN_FULL = "COLUMN_FULL"
    HEIGHT = 6
    WIDTH = 7

    def __init__(self, challenger, opponent = None):
        self._challenger = challenger
        self._opponent = opponent

        self._challenger_move = randint(1, 100) % 2 == 0 or opponent == None

        self._message = None
    
        self.generate_board()
    
    # # # # # # # # # # # # # # # # # # # # # # # # #
    
    def get_challenger(self):
        return self._challenger
    
    def get_opponent(self):
        return self._opponent
    
    def get_current_player(self):
        if self.is_challenger_move():
            return self._challenger
        return self._opponent
    
    def is_challenger_move(self):
        return self._challenger_move
    
    def next_turn(self):
        self._challenger_move = not self._challenger_move
    
    def get_board(self):
        return self._board
    
    def set_message(self, message):
        self._message = message
    
    def get_message(self):
        return self._message

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def generate_board(self):

        # Setup board
        self._board = []

        # Add each row
        for row in range(ConnectFour.HEIGHT):
            self._board.append([])
            for col in range(ConnectFour.WIDTH):
                self._board[row].append(None)
    
    def make_move(self, column):
        """Allows the challenger or opponent to make a move.

        Parameters:
            column (int): The column to make the move at.
        """

        # Check if column is full
        if is_column_full(self._board, column):
            return ConnectFour.COLUMN_FULL

        # Check if playing with AI
        if self.get_opponent() == None:
            add_piece(self._board, column, True)

            # Only do AI move if there is no winner
            if check_for_winner(self._board) == None:
                get_ai_move(self._board)
        
        # Check if playing with real player
        else:
            add_piece(self._board, column, self.is_challenger_move())
            self.next_turn()
        
        # Check for board full or winner
        boardFull = is_board_full(self._board)
        winnerCheck = check_for_winner(self._board)

        # There was a winner
        if winnerCheck in [True, False]:
            return winnerCheck
        
        # There was no winner but there was no draw
        elif winnerCheck == None and not boardFull:
            return None
        
        # There was no winner but board was full
        return ConnectFour.DRAW

    def show_board(self):
        """Returns a representation of the Connect Four board using emojis.

        The list rules are as follows:
            None: signifies the spot has not been taken yet.
            False: signifies the spot was taken by the opponent / AI
            True: signifies the spot was taken by the challenger / Member

        Parameters:
            board (list): The two-dimensional list for the Connect Four board.
        """

        # Keep list of emoji numbers for column numbers
        emojiNumbers = [
            ":one:", ":two:", ":three:", 
            ":four:", ":five:", ":six:",
            ":seven:"
        ]

        # Setup board string
        boardString = ""
        for columnNumber in range(len(self._board[0])):
            boardString += emojiNumbers[columnNumber] + " "
        boardString += "\n"

        # Add board
        for row in self._board:
            for col in row:
                
                # None is an empty spot (empty circle)
                if col == None:
                    boardString += ":black_circle: "
                # False is a Red Circle (opponent / AI)
                elif col == False:
                    boardString += ":red_circle: "
                
                # True is a Blue Circle (challenger / Member)
                else:
                    boardString += ":large_blue_circle: "
            
            boardString += "\n"
        
        return boardString

def is_column_full(board, column):
    """Determines whether or not a specific column in a Connect Four board is full.

    Parameters:
        board (list): The Connect Four board to look at.
        column (int): The column to look at.
    """

    return board[0][column] != None

def add_piece(board, column, isChallenger):
    """Adds a Connect Four piece to a Connect Four board.

    Parameters:
        board (list): The Connect Four board to add the piece to.
        column (int): The column to add the piece to.
        isChallenger (bool): Whether or not the piece is for the challenger.
    """

    # Iterate through rows; Find last place it can put the piece
    lastRow = 0
    for row in range(len(board)):
        
        # Test if current row's column can be placed
        if board[row][column] == None:
            lastRow = row
        
        # Test if current row's column cannot be placed (spot is filled)
        else:
            break
    
    # Place piece at lastRow and column
    board[lastRow][column] = isChallenger

def check_for_winner(board):
    """Checks to see if there are any winners in the board.

    Parameters:
        board (list): The Connect Four board to check.
    """

    # Check horizontally and vertically
    copyOfBoard = copy_board(board)
    for rotation in range(4):
        for row in range(len(copyOfBoard) - 1, -1, -1):
            row = copyOfBoard[row]

            # Check four spots at a time
            for initialSpot in range(len(row) - 4):
                if do_all_equal(row[initialSpot: initialSpot + 4]) and row[initialSpot] != None:
                    return row[initialSpot]

        copyOfBoard = rotate_board(copyOfBoard)
    
    # # # Check diagonally next # # #
    # # First check bottom-left - top-right diagonals
    # When checking BL-TR diagonals, only iterate between row(3, height), column(0, width - 3)
    for row in range(3, len(board)):

        # Get four spots
        for col in range(len(board[row]) - 3):
            spots = [board[row][col], board[row - 1][col + 1], board[row - 2][col + 2], board[row - 3][col + 3]]
            if do_all_equal(spots) and spots[0] != None:
                return spots[0]

    # # Then check top-left - bottom-right diagonals
    # When checking TL-BR diagonals, only iterate between row(0, height - 3), column(0, width - 3)
    for row in range(len(board) - 3):

        # Get four spots
        for col in range(len(board[row]) - 3):
            spots = [board[row][col], board[row + 1][col + 1], board[row + 2][col + 2], board[row + 3][col + 3]]
            if do_all_equal(spots) and spots[0] != None:
                return spots[0]
    
    # No winner yet; Return none
    return None

def is_board_full(board):
    """Determines whether or not the board is full.

    Parameters:
        board (list): The board the check.
    """
    return count_pieces(board[0]) == len(board[0])

def get_ai_move(board):
    """Retrieves the move the AI is going to make.

    Parameters:
        board (list): The list for the Connect Four board.
    """

    # Go through each board[0] columns
    # Get a copy of the board
    restrictedMoves = []
    aiMove = -1
    for column in range(len(board[0])):
        aiCopy = copy_board(board)
        playerCopy = copy_board(board)

        # Check if column is full
        if is_column_full(board, column):
            continue   # Move to next column; Column is full

        # Column is not full; Emulate AI and Player moves
        add_piece(aiCopy, column, False)
        add_piece(playerCopy, column, True)

        # Check for AI win or Player win
        aiWinCheck = check_for_winner(aiCopy)
        playerWinCheck = check_for_winner(playerCopy)

        # AI move or Player move would win; Set move and break
        if aiWinCheck == False or playerWinCheck == True:
            aiMove = column
            break
        
        # AI move and Player move would not win; Emulate player next move on same column
        else:

            # Check if column is full
            if is_column_full(aiCopy, column):
                continue
            
            # Column is not full
            add_piece(aiCopy, column, True)

            # Check for player win
            playerWinCheck = check_for_winner(aiCopy)

            # Player move would win; continue to next column
            if playerWinCheck == True:
                restrictedMoves.append(column)  # Add column to restricted moves; We don't want AI to go there

    # aiMove was -1 (no move or full); Generate random column
    if aiMove == -1:

        # See if board is full
        if is_board_full(board):
            return False

        # Board is not full; generate random column
        while True:
            aiMove = randint(0, len(board[0]) - 1)

            # Check to see if column is full
            if is_column_full(board, aiMove):
                continue
            
            # Check to see if this column is the only available column
            #   OR check to see if the restrictedMoves include the only available columns
            elif len(board[0]) - count_pieces(board[0]) == 1 or len(restrictedMoves) == len(board[0]) - count_pieces(board[0]):
                break
            
            # Check to see if move is not in restricted moves
            elif aiMove not in restrictedMoves:
                break
    
    # Use aiMove for move
    add_piece(board, aiMove, False)
    return True

def count_pieces(line, *, forChallenger = None):
    """Counts how many pieces in a line are from a challenger, an opponent, or all.

    Parameters:
        line (list): The line to look at.
        forChallenger (bool): Whether or not to look at pieces from a challenger. (Defaults to None)
    """

    count = 0

    # Count all pieces
    if forChallenger == None:
        for item in line:
            if item != None:
                count += 1

    # Count challenger's pieces
    elif forChallenger:
        for item in line:
            if item == True:
                count += 1

    # Count opponent's pieces
    elif not forChallenger:
        for item in line:
            if item == False:
                count += 1
    
    return count
        
def do_all_equal(line):
    """Determines whether or not all the values in a list are the same.

    Parameters:
        line (list): The list to check.
    """

    # Compare value is the first value
    compare = line[0]

    for item in line:
        if item != compare:
            return False
    
    return True

def rotate_board(board):
    """Returns a copy of a rotation of a two-dimensional list.

    Parameters:
        board (list): The two-dimensional list to rotate.
    """

    # Setup rotated board
    rotatedBoard = []
    
    # Iterate through rows
    for col in range(len(board[0])):
        rotatedBoard.append([])
        for row in range(len(board) - 1, -1, -1):
            rotatedBoard[col].append(board[row][col])
    
    return rotatedBoard

def copy_board(board):
    """Copies the contents of a two-dimensional list.

    Parameters:
        board (list): The board to copy.
    """

    # Setup copyOfBoard
    copyOfBoard = []

    for row in range(len(board)):
        copyOfBoard.append([])
        for col in board[row]:
            copyOfBoard[row].append(col)
    
    return copyOfBoard