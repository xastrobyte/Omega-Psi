from random import randint

def getBoard(board):
    """Returns a representation of the Tic-Tac-Toe board using emojis.

    The list rules are as follows:
        None: signifies the spot has not been taken yet.
        False: signifies the spot was taken by the opponent / AI
        True: signifies the spot was taken by the challenger / Member

    Parameters:
        board (list): The list for the Tic-Tac-Toe board.
    """

    # Keep list of emoji numbers
    emojiNumbers = [
        ":one:", ":two:", ":three:", 
        ":four:", ":five:", ":six:",
        ":seven:", ":eight:", ":nine:"
    ]

    # Setup board string
    boardString = ""

    for slot in range(len(board)):

        # None is an empty spot (black box)
        if board[slot] == None:
            boardString += emojiNumbers[slot] + " "
        
        # False is an O (the opponent / AI)
        elif board[slot] == False:
            boardString += ":o: "
        
        # True is an X (challenger / Member)
        else:
            boardString += ":x: "
        
        # Add a new line if the slot is divisible by 3
        if (slot + 1) % 3 == 0:
            boardString += "\n"
    
    return boardString

def getAIMove(board, difficulty):
    """Retrieves the move the AI is going to make given a specific difficulty.

    The difficulty moves are as follows:
        \"easy\": The AI will check for horizontal only.
        \"medium\": The AI will check for horizontal and vertical.
        \"hard\": The AI will check for horizontal, vertical, and diagonal.

    Parameters:
        board (list): The list for the Tic-Tac-Toe board.
        difficulty (str): The difficulty the AI should use.
    """
    
    # Difficulty is Hard
    if difficulty in ["hard"]:
        
        # See if diagonals are near completion
        leftDiag = shouldAIGo([board[0], board[4], board[8]])
        rightDiag = shouldAIGo([board[2], board[4], board[6]])
        if leftDiag["boolean"]:
            board[leftDiag["location"] * 4] = False
            return
        
        elif rightDiag["boolean"]:
            board[rightDiag["location"] * 2 + 2] = False
            return
    
    # Difficulty is Medium or Hard
    if difficulty in ["medium", "hard"]:
        
        # See if verticals are near completion
        firstColumn = shouldAIGo([board[0], board[3], board[6]])
        secondColumn = shouldAIGo([board[1], board[4], board[7]])
        thirdColumn = shouldAIGo([board[2], board[5], board[8]])
        if firstColumn["boolean"]:
            board[firstColumn["location"] * 3] = False
            return
        
        elif secondColumn["boolean"]:
            board[secondColumn["location"] * 3 + 1] = False
            return
        
        elif thirdColumn["boolean"]:
            board[thirdColumn["location"] * 3 + 2] = False
            return
    
    # Difficulty is Easy Medium or Hard
    if difficulty in ["easy", "medium", "hard"]:
        
        # See if horizontals are near completion
        firstRow = shouldAIGo(board[ : 3])
        secondRow = shouldAIGo(board[3 : 6])
        thirdRow = shouldAIGo(board[6 : ])
        if firstRow["boolean"]:
            board[firstRow["location"]] = False
            return
        
        elif secondRow["boolean"]:
            board[secondRow["location"] + 3] = False
            return
        
        elif thirdRow["boolean"]:
            board[thirdRow["location"] + 6] = False
            return
    
    # No move has been made yet, do a random move
    location = randint(0, 8)
    while board[location] != None and countSpotsLeft(board) > 0:
        location = randint(0, 8)
    
    board[location] = False

def shouldAIGo(line):
    """Determines whether the AI should go in the 3-spot line that's given.

    Parameters:
        line (list): A list of three spots to look at.
    """

    # Determine if 1st and 2nd spot are taken; 3rd one isn't
    if line[0] and line[1] and line[2] == None:
        return {
            "boolean": True,
            "location": 2
        }
    
    # Determine if 1st and 3rd spot are taken; 2nd one isn't
    elif line[0] and line[2] and line[1] == None:
        return {
            "boolean": True,
            "location": 1
        }
    
    # Determine if 2nd and 3rd spots are taken; 1st one isn't
    elif line[1] and line[2] and line[0] == None:
        return {
            "boolean": True,
            "location": 0
        }
    
    # No spots should be taken
    return {
        "boolean": False,
        "location": -1
    }

def checkForWinner(board):
    """Checks to see if there are any winners in the board.

    Parameters:
        board (list): The list of the board.
    """

    # Check horizontally
    if board[0] == board[1] == board[2]:
        return board[0]
    elif board[3] == board[4] == board[5]:
        return board[3]
    elif board[6] == board[7] == board[8]:
        return board[6]
    
    # Check vertically
    elif board[0] == board[3] == board[6]:
        return board[0]
    elif board[1] == board[4] == board[7]:
        return board[1]
    elif board[2] == board[5] == board[8]:
        return board[2]
    
    # Check diagonally
    elif board[0] == board[4] == board[8]:
        return board[0]
    elif board[2] == board[4] == board[6]:
        return board[2]
    
    # No winners yet
    return None

def countSpotsLeft(board):
    """Counts how many spots are not occupied yet.

    Parameters:
        board (list): The list of the board.
    """

    count = 0
    for spot in board:
        if spot == None:
            count += 1
    return count
