from random import randint

def getBoard(board):
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
        ":seven:", ":eight:", ":nine:",
        ":keycap_ten:"
    ]

    # Setup board string
    boardString = ""
    for columnNumber in range(len(board[0])):
        boardString += emojiNumbers[columnNumber] + " "
    boardString += "\n"

    # Add board
    for row in board:
        for col in row:
            
            # None is an empty spot (white box)
            if col == None:
                boardString += ":white_large_square: "
            
            # False is a Red Circle (opponent / AI)
            elif col == False:
                boardString += ":red_circle: "
            
            # True is a Blue Circle (challenger / Member)
            else:
                boardString += ":large_blue_circle: "
        
        boardString += "\n"
    
    return boardString

def generateBoard(width, height):
    """Generates and returns a two-dimensional Connect Four board.

    Parameters:
        width (int): The width of the Connect Four board.
        height (int): The height of the Connect Four board.
    """

    # Setup board
    board = []

    # Add each row
    for row in range(height):
        board.append([])
        for col in range(width):
            board[row].append(None)
    
    return board

def isColumnFull(board, column):
    """Determines whether or not a specific column in a Connect Four board is full.

    Parameters:
        board (list): The Connect Four board to look at.
        column (int): The column to look at.
    """

    return board[0][column] != None

def addPiece(board, column, isChallenger):
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

def checkForWinner(board):
    """Checks to see if there are any winners in the board.

    Parameters:
        board (list): The Connect Four board to check.
    """

    # Check horizontally and vertically
    copyOfBoard = copyBoard(board)
    for rotation in range(4):
        for row in range(len(copyOfBoard) - 1, -1, -1):
            row = copyOfBoard[row]

            # Check four spots at a time
            for initialSpot in range(len(row) - 4):
                if doAllEqual(row[initialSpot: initialSpot + 4]) and row[initialSpot] != None:
                    return row[initialSpot]

        copyOfBoard = rotateBoard(copyOfBoard)
    
    # # # Check diagonally next # # #
    # # First check bottom-left - top-right diagonals
    # When checking BL-TR diagonals, only iterate between row(3, height), column(0, width - 3)
    for row in range(3, len(board)):

        # Get four spots
        for col in range(len(board[row]) - 3):
            spots = [board[row][col], board[row - 1][col + 1], board[row - 2][col + 2], board[row - 3][col + 3]]
            if doAllEqual(spots) and spots[0] != None:
                return spots[0]

    # # Then check top-left - bottom-right diagonals
    # When checking TL-BR diagonals, only iterate between row(0, height - 3), column(0, width - 3)
    for row in range(len(board) - 3):

        # Get four spots
        for col in range(len(board[row]) - 3):
            spots = [board[row][col], board[row + 1][col + 1], board[row + 2][col + 2], board[row + 3][col + 3]]
            if doAllEqual(spots) and spots[0] != None:
                return spots[0]
    
    # No winner yet; Return none
    return None

def isBoardFull(board):
    """Determines whether or not the board is full.

    Parameters:
        board (list): The board the check.
    """
    return countPieces(board[0]) == len(board[0])

def getAIMove(board, difficulty):
    """Retrieves the move the AI is going to make given a specific difficulty.

    The difficulty moves are as follows:
        \"easy\": The AI will randomly choose a move.
        \"hard\": The AI will use the Monte Carlo method to choose the best move.

    Parameters:
        board (list): The list for the Connect Four board.
        difficulty (str): The difficulty the AI should use.
    """

    # Go through each board[0] columns
    # Get a copy of the board
    aiMove = -1
    for column in range(len(board[0])):
        playerCopy = copyBoard(board)
        aiCopy = copyBoard(board)

        # Place player piece at column
        addPiece(playerCopy, column, True)
        addPiece(aiCopy, column, False)

        # Get possible win checks
        playerWins = checkForWinner(playerCopy)
        aiWins = checkForWinner(aiCopy)

        # AI would win, go to spot
        if aiWins == True or playerWins == True:
            aiMove = column
            break

        # No winner would be declared; Move to next column
        continue

    # aiMove was -1; Generate random column
    if aiMove == -1:

        # See if board is full
        if isBoardFull(board):
            return False

        # Board is not full; generate random column
        aiMove = randint(0, len(board[0]) - 1)
        while isColumnFull(board, aiMove):
            aiMove = randint(0, len(board[0]) - 1)
    
    # Use aiMove for move
    addPiece(board, aiMove, False)
    return True

def countPieces(line, *, forChallenger = None):
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
        
def doAllEqual(line):
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

def rotateBoard(board):
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

def copyBoard(board):
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

def prettyPrint(board):
    for row in board:
        for col in row:
            if col == None:
                print("- ", end = "")
            elif col == True:
                print("X ", end = "")
            else:
                print("O ", end = "")
        print()
