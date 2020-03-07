class ConnectFourBoard:

    DEFAULT_WIDTH = 7
    DEFAULT_HEIGHT = 6

    def __init__(self, *, width = DEFAULT_WIDTH, height = DEFAULT_HEIGHT):
        self.width = width
        self.height = height
        self.generate_board(width, height)
    
    def __str__(self):
        """Returns a stringified version of the board for easy printing in Discord

        Returns
        -------
            string
        """

        # Emoji numbers for the top row
        numbers = [
            ":one: ", ":two: ", ":three: ", 
            ":four: ", ":five: ", ":six: ",
            ":seven: "
        ]

        # Setup the resulting string and include the column numbers
        result = ""
        for column in range(self.width):
            result += numbers[column]
        result += "\n"

        # Add the board spots
        for row in self.board:
            for column in row:

                # If the current spot is None, no person has occupied this spot
                #   if the spot is True, the challenger has occupied this spot
                #   if the spot is False, the opponent has occupied this spot
                if column == None:
                    result += ":black_circle: "
                elif column:
                    result += ":blue_circle: "
                else:
                    result += ":red_circle: "
            result += "\n"
        return result
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Getters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @property
    def width(self):
        return self.__width
    
    @property
    def height(self):
        return self.__height
    
    @property
    def board(self):
        return self.__board

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Setters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @width.setter
    def width(self, width):
        self.__width = width
    
    @height.setter
    def height(self, height):
        self.__height = height
    
    @board.setter
    def board(self, board):
        self.__board = board
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Other Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def generate_board(self, width, height):
        """Generates a board with the specified width and height

        Parameters
        ----------
            width : int
                The width of the Connect Four board
            height : int
                The height of the Connect Four board
            
        Returns
        -------
            list
                The generated Connect Four board
        """
        self.board = []
        for row in range(height):
            self.board.append([])
            for col in range(width):
                self.board[row].append(None)
                    # Each board position is filled with None at first
                    #   later in the game,  True is a challenger spot
                    #                       False is an opponent spot
    
    def copy(self):
        """A method to copy this board and return the copy
            
        Returns
        -------
            ConnectFourBoard
                A copy of this board
        """
        new_board = ConnectFourBoard(width = self.width, height = self.height)
        for row in range(self.height):
            for column in range(self.width):
                new_board.board[row][column] = self.board[row][column]
        return new_board
    
    def is_column_full(self, column):
        """Determines whether or not a specified column is full in this Connect Four board

        Parameters
        ----------
            column : int
                The column to check if it is full or not
            
        Returns
        -------
            boolean
                Whether or not the specified column is full
        """
        return self.board[0][column] != None
    
    def is_board_full(self):
        """Determines whether or not the entire board is full in this Connect Four board
    
        Returns
        -------
            boolean
                Whether or not the specified board is full
        """
        return self.board[0].count(None) == 0
    
    def check_for_winner(self):
        """Checks to see if there are any winners in this Connect Four board

        Returns
        -------
            boolean or None
                True, the winner of this board is the challenger
                False, the winner of this board is the opponent
                None, there is no winner of this board yet
        """

        # Check horizontally
        for row in range(self.height):
            for col in range(self.width - 3):
                if self.board[row][col] == self.board[row][col + 1] == self.board[row][col + 2] == self.board[row][col + 3] and self.board[row][col] != None:
                    return self.board[row][col]
        
        # Check vertically
        for col in range(self.width):
            for row in range(self.height - 3):
                if self.board[row][col] == self.board[row + 1][col] == self.board[row + 2][col] == self.board[row + 3][col] and self.board[row][col] != None:
                    return self.board[row][col]
        
        # Check ascending diagonals
        for row in range(3, self.height):
            for col in range(self.width - 3):
                if self.board[row][col] == self.board[row - 1][col + 1] == self.board[row - 2][col + 2] == self.board[row - 3][col + 3] and self.board[row][col] != None:
                    return self.board[row][col]
        
        # Check descending diagonals
        for row in range(self.height - 3):
            for col in range(self.width - 3):
                if self.board[row][col] == self.board[row + 1][col + 1] == self.board[row + 2][col + 2] == self.board[row + 3][col + 3] and self.board[row][col] != None:
                    return self.board[row][col]
        
        # No winners were found
        return None
    
    def add_piece(self, column, *, is_challenger = None):
        """Adds a Connect Four piece to this Connect Four board at the specified column

        Parameters
        ----------
            column : int
                The column to add the piece to
        
        Keyword Parameters
        ------------------
            is_challenger : boolean or None
                Whether or not the piece being added is a challenger's piece
                or an opponent's piece
        """

        # Iterate through the rows from the bottom up
        for row in range(self.height - 1, -1, -1):

            # Check if the row and column is open
            #   if so, place the piece
            if self.board[row][column] == None:
                self.board[row][column] = is_challenger
                break

        # No piece was added because the column is full
        return None
    
    def remove_piece(self, column):
        """Removes a Connect Four piece from this Connect Four board

        Parameters
        ----------
            column : int
                The column to remove a piece from
        """

        # Iterate through the rows from the top down
        for row in range(self.height):

            # Check if the row and column is not open
            #   if so, remove the piece
            if self.board[row][column] != None:
                self.board[row][column] = None
                break