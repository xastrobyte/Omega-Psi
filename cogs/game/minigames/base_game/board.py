from abc import abstractmethod

class Board:
    """A Board object holds information about an arbitrarily sized board in a minigame
    that uses a board to display the game state

    :param width: The width of the Board
    :param height: The height of the Board
    """

    WIN = 10000
    LOSS = -10000

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.generate_board()

    # # # # # # # # # # # # # # # # # # # # # # # # #
    # Getters
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @property
    def width(self):
        return self.__width
    
    @property
    def height(self):
        return self.__height

    @property
    def board(self):
        return self.__board

    # # # # # # # # # # # # # # # # # # # # # # # # #
    # Setters
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @width.setter
    def width(self, width):
        self.__width = width
    
    @height.setter
    def height(self, height):
        self.__height = height
    
    @board.setter
    def board(self, board):
        self.__board = board

    # # # # # # # # # # # # # # # # # # # # # # # # #
    # Other Methods
    # # # # # # # # # # # # # # # # # # # # # # # # #
    
    def generate_board(self):
        """Generates the board based off the width and height values
        and places it in this board object
        """
        self.board = []
        for row in range(self.height):
            self.board.append([])
            for col in range(self.width):
                self.board[row].append(None)
        
    def get_legal_moves(self):
        """Returns a list of legal moves that can be made based off the state of the board

        :returns: A list of (row, column) tuples that are valid moves
        """
        return [
            (r, c)
            for r in range(self.height)
            for c in range(self.width)
            if self.board[r][c] == None
        ]
    
    def get_max_moves(self):
        """Returns the maximum number of moves that can be made in this game

        :rtype: int
        """
        return self.height * self.width
    
    def is_full(self):
        """Returns whether or not this Board object is full

        :rtype: boolean
        """
        for row in range(self.height):
            for col in range(self.width):
                if self.board[row][col] == None:
                    return False
        return True
    
    def make_move(self, row, column, is_challenger_turn):
        """Makes a move for the specified challenger at the specified row and column

        :param row: The row of the move
        :param column: The column of the move
        :param is_challenger_turn: Whether this move is for the player (True) or the AI (False)
        """
        self.board[row][column] = is_challenger_turn
    
    @abstractmethod
    def check_for_winner(self):
        """An abstract method meant to be inherited in subclasses of Board
        to check for a winner
        """
        pass
