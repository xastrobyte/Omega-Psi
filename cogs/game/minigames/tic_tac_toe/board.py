from cogs.game.minigames.base_game.board import Board

class TicTacToeBoard(Board):
    """A TicTacToeBoard object holds information about a Tic Tac Toe board in a game"""

    def __init__(self):
        super().__init__(3, 3)

    def __str__(self):

        # Keep track of emoji numbers
        numbers = [
            ":one:", ":two:", ":three:", 
            ":four:", ":five:", ":six:",
            ":seven:", ":eight:", ":nine:"
        ]

        # Setup board string and iterate through the spots in the board
        #   to add the proper emojis to the message
        board_string = ""
        for row in range(self.height):
            for col in range(self.width):
                # if the current spot is None, the spot is still available; Put a number emoji
                #   if the current spot is False, the opponent occupies that spot
                #   if the current spot is True, the challenger occupies that spot
                if self.board[row][col] == None:
                    board_string += numbers[row * 3 + col % 3] + " "
                elif not self.board[row][col]:
                    board_string += ":o: "
                else:
                    board_string += ":x: "
            
            board_string += "\n"

        return board_string

    def check_for_winner(self):
        """Checks for a winner in the board

        Returns
        -------
            int
                TicTacToeBoard.WIN if the player wins
                TicTacToeBoard.LOSS if the player loses
                0 if there is no winner yet
        """

        # Iterate through the rows
        for row in range(self.height):
            if self.board[row][0] == self.board[row][1] == self.board[row][2] and self.board[row][0] != None:
                return Board.WIN if self.board[row][0] else Board.LOSS
        
        # Iterate through the columns
        for col in range(self.width):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] and self.board[0][col] != None:
                return Board.WIN if self.board[0][col] else Board.LOSS
        
        # Diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] and self.board[0][0] != None:
            return Board.WIN if self.board[0][0] else Board.LOSS
        if self.board[0][2] == self.board[1][1] == self.board[2][0] and self.board[0][2] != None:
            return Board.WIN if self.board[0][2] else Board.LOSS
        
        # No winner yet
        return 0