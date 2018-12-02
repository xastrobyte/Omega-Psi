from random import randint

class TicTacToe:
    """Creates a Tic-Tac-Toe game.

    Parameters:
        difficulty (str): The difficulty of the match (only applies to AI).
        challenger (discord.User): The user who started the game.
        opponent (discord.User | None): The user who is challenging. (Defaults to None for AI)
    """

    DRAW = "DRAW"

    def __init__(self, difficulty, challenger, opponent = None):
        """Creates a Tic-Tac-Toe game.

        Parameters:
            difficulty (str): The difficulty of the match (only applies to AI).
            challenger (discord.User): The user who started the game.
            opponent (discord.User | None): The user who is challenging. (Defaults to None for AI)
        """

        # Set challenger and opponent
        self._difficulty = difficulty
        self._challenger = challenger
        self._opponent = opponent

        # Choose random starter
        self._challenger_move = randint(1, 100) % 2 == 0

        # Set up the board.
        #  - Any values with True are challenger moves
        #  - Any values with False are challenger moves
        self._board = [
            None, None, None, 
            None, None, None, 
            None, None, None
        ] 

    # Getters

    def getChallenger(self):
        """Returns the challenger of the Tic-Tac-Toe game.
        """
        return self._challenger
    
    def getOpponent(self):
        """Returns the opponent of the Tic-Tac-Toe game.
        """
        return self._opponent
    
    def getBoard(self):
        """Returns the current Tic-Tac-Toe board.
        """
        return self._board
    
    def isChallengerTurn(self):
        """Returns whether or not it is the challenger's turn.
        """
        return self._challenger_move
    
    def swapTurns(self):
        """Swaps the person of whose turn it is.
        """
        self._challenger_move = not self._challenger_move

    # Input Methods

    def showBoard(self):
        """Returns a representation of the Tic-Tac-Toe board using emojis.

        The list rules are as follows:
            None: signifies the spot has not been taken yet.
            False: signifies the spot was taken by the opponent.
            True: signifies the spot was taken by the challenger.
        """

        # Keep list of emoji numbers
        emojiNumbers = [
            ":one:", ":two:", ":three:", 
            ":four:", ":five:", ":six:",
            ":seven:", ":eight:", ":nine:"
        ]

        # Setup board string
        boardString = ""

        for slot in range(len(self._board)):

            # None is an empty spot (black box)
            if self._board[slot] == None:
                boardString += emojiNumbers[slot] + " "
            
            # False is an O (the opponent / AI)
            elif self._board[slot] == False:
                boardString += ":o: "
            
            # True is an X (challenger / Member)
            else:
                boardString += ":x: "
            
            # Add a new line if the slot is divisible by 3
            if (slot + 1) % 3 == 0:
                boardString += "\n"
        
        return boardString

    def makeMove(self, spot):
        """Processes through the moves in the board.

        The spot validity will be determined prior to this method being called.

        Parameters:
            spot (int): The integer of the spot to place.
        """

        # Check if going against AI
        if self.getOpponent() == None:

            # Do player and AI moves
            self._board[spot] = True
            self.getAIMove()
        
        # Check if going against actual opponent
        else:
            self._board[spot] = self.isChallengerTurn()
            self.swapTurns()
        
        # Check for a winner / draw
        spotsLeft = self.countSpotsLeft()
        winnerCheck = self.checkForWinner()

        # There was a winner
        if winnerCheck in [True, False]:
            return winnerCheck
        
        # There was no winner but no draw
        elif winnerCheck == None and spotsLeft > 0:
            return None
        
        # There was no winner but there is a draw
        return TicTacToe.DRAW

    # AI Methods

    def getAIMove(self):
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
        if self._difficulty in ["hard"]:
            
            # See if diagonals are near completion
            leftDiag = self.shouldAIGo([self._board[0], self._board[4], self._board[8]])
            rightDiag = self.shouldAIGo([self._board[2], self._board[4], self._board[6]])
            if leftDiag["boolean"]:
                self._board[leftDiag["location"] * 4] = False
                return
            
            elif rightDiag["boolean"]:
                self._board[rightDiag["location"] * 2 + 2] = False
                return
        
        # Difficulty is Medium or Hard
        if self._difficulty in ["medium", "hard"]:
            
            # See if verticals are near completion
            firstColumn = self.shouldAIGo([self._board[0], self._board[3], self._board[6]])
            secondColumn = self.shouldAIGo([self._board[1], self._board[4], self._board[7]])
            thirdColumn = self.shouldAIGo([self._board[2], self._board[5], self._board[8]])
            if firstColumn["boolean"]:
                self._board[firstColumn["location"] * 3] = False
                return
            
            elif secondColumn["boolean"]:
                self._board[secondColumn["location"] * 3 + 1] = False
                return
            
            elif thirdColumn["boolean"]:
                self._board[thirdColumn["location"] * 3 + 2] = False
                return
        
        # Difficulty is Easy Medium or Hard
        if self._difficulty in ["easy", "medium", "hard"]:
            
            # See if horizontals are near completion
            firstRow = self.shouldAIGo(self._board[ : 3])
            secondRow = self.shouldAIGo(self._board[3 : 6])
            thirdRow = self.shouldAIGo(self._board[6 : ])
            if firstRow["boolean"]:
                self._board[firstRow["location"]] = False
                return
            
            elif secondRow["boolean"]:
                self._board[secondRow["location"] + 3] = False
                return
            
            elif thirdRow["boolean"]:
                self._board[thirdRow["location"] + 6] = False
                return
        
        # No move has been made yet, do a random move
        location = randint(0, 8)
        while self._board[location] != None and self.countSpotsLeft() > 0:
            location = randint(0, 8)
        
        self._board[location] = False
    
    def shouldAIGo(self, line):
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

    def checkForWinner(self):
        """Checks to see if there are any winners in the board.

        Parameters:
            board (list): The list of the board.
        """

        # Check horizontally
        if self._board[0] == self._board[1] == self._board[2]:
            return self._board[0]
        elif self._board[3] == self._board[4] == self._board[5]:
            return self._board[3]
        elif self._board[6] == self._board[7] == self._board[8]:
            return self._board[6]
        
        # Check vertically
        elif self._board[0] == self._board[3] == self._board[6]:
            return self._board[0]
        elif self._board[1] == self._board[4] == self._board[7]:
            return self._board[1]
        elif self._board[2] == self._board[5] == self._board[8]:
            return self._board[2]
        
        # Check diagonally
        elif self._board[0] == self._board[4] == self._board[8]:
            return self._board[0]
        elif self._board[2] == self._board[4] == self._board[6]:
            return self._board[2]
        
        # No winners yet
        return None

    def countSpotsLeft(self):
        """Counts how many spots are not occupied yet.

        Parameters:
            board (list): The list of the board.
        """

        count = 0
        for spot in self._board:
            if spot == None:
                count += 1
        return count