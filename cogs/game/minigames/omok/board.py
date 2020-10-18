from cogs.game.minigames.base_game.board import Board

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class OmokBoard(Board):
    """An OmokBoard object holds information about an Omok Board in a game"""

    def __init__(self):
        super().__init__(10, 10)
        self.last_player_move = None
        self.last_ai_move = None
        self.last_move = None

    def __str__(self):
        """Returns a stringified version of the board for easy printing in Discord

        :rtype: str
        """

        # Emoji numbers for the top row
        numbers = [
            ":one: ", ":two: ", ":three: ", 
            ":four: ", ":five: ", ":six: ",
            ":seven: ", ":eight: ", ":nine: ",
            ":keycap_ten: "
        ]

        # Setup the resulting string and include the column numbers
        result = ":black_circle: "
        for column in range(self.width):
            result += numbers[column]
        result += "\n"

        # Add the board spots
        for i in range(self.height):
            row = self.board[i]

            # Add the row number to the current result
            result += numbers[i]
            for column in row:

                # If the current spot is None, no person has occupied this spot
                #   if the spot is True, the challenger has occupied this spot
                #   if the spot is False, the opponent has occupied this spot
                if column == None:
                    result += ":black_circle: "
                elif column:
                    result += ":brown_circle: "
                else:
                    result += ":white_circle: "
            result += "\n"
        return result
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Getters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @property
    def last_player_move(self):
        return self.__last_player_move
    
    @property
    def last_ai_move(self):
        return self.__last_ai_move
    
    @property
    def last_move(self):
        return self.__last_move
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Setters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @last_player_move.setter
    def last_player_move(self, last_player_move):
        self.__last_player_move = last_player_move
    
    @last_ai_move.setter
    def last_ai_move(self, last_ai_move):
        self.__last_ai_move = last_ai_move

    @last_move.setter
    def last_move(self, last_move):
        self.__last_move = last_move

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Other Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_moves(self, for_player):
        return [
            (row, column)
            for row in range(self.height)
            for column in range(self.width)
            if self.board[row][column] == for_player
        ]

    def make_move(self, row, column, is_challenger_turn):
        super().make_move(row, column, is_challenger_turn)
        if is_challenger_turn:
            self.last_player_move = row, column
        else:
            self.last_ai_move = row, column
        self.last_move = row, column
    
    def check_for_winner(self):
        """Checks for a winner in the board based off the last move of the game

        :rtype: int
        """

        # Get the row and column of the last move
        row, column = self.last_move
        
        # Check for horizontals by iterating through offsets 1 - 4
        #   once a left or right bound is reached OR 
        #   a left or right piece is not the same as the last move's piece
        #   don't add to the left or right values
        left = right = 0
        add_to_left = add_to_right = True
        for offset in range(1, 5):
            if column - offset < 0 or self.board[row][column - offset] != self.board[row][column]:
                add_to_left = False
            if column + offset >= self.width or self.board[row][column + offset] != self.board[row][column]:
                add_to_right = False
            left += 1 if add_to_left else 0
            right += 1 if add_to_right else 0
        if left + right + 1 == 5 and self.board[row][column] != None:
            return OmokBoard.WIN if self.board[row][column] else OmokBoard.LOSS

        # Check for verticals by iterating through offsets 1 - 4
        #   once an up or down bound is reached OR 
        #   an up or down piece is not the same as the last move's piece
        #   don't add to the up or down values
        up = down = 0
        add_to_up = add_to_down = True
        for offset in range(1, 5):
            if row - offset < 0 or self.board[row - offset][column] != self.board[row][column]:
                add_to_up = False
            if row + offset >= self.width or self.board[row + offset][column] != self.board[row][column]:
                add_to_down = False
            up += 1 if add_to_up else 0
            down += 1 if add_to_down else 0
        if up + down + 1 == 5 and self.board[row][column] != None:
            return OmokBoard.WIN if self.board[row][column] else OmokBoard.LOSS

        # Check for left diagonals
        left_upper = right_lower = 0
        add_to_upper = add_to_lower = True
        for offset in range(1, 5):
            if row - offset < 0 or column - offset < 0 or self.board[row - offset][column - offset] != self.board[row][column]:
                add_to_upper = False
            if row + offset >= self.height or column + offset >= self.width or self.board[row + offset][column + offset] != self.board[row][column]:
                add_to_lower = False
            left_upper += 1 if add_to_upper else 0
            right_lower += 1 if add_to_lower else 0
        if left_upper  + right_lower + 1 == 5 and self.board[row][column] != None:
            return OmokBoard.WIN if self.board[row][column] else OmokBoard.LOSS

        # Check for right diagonals
        left_lower = right_upper = 0
        add_to_lower = add_to_upper = True
        for offset in range(1, 5):
            if row + offset >= self.height or column - offset < 0 or self.board[row + offset][column - offset] != self.board[row][column]:
                add_to_upper = False
            if row - offset < 0 or column + offset >= self.width or self.board[row - offset][column + offset] != self.board[row][column]:
                add_to_lower = False
            left_lower += 1 if add_to_lower else 0
            right_upper += 1 if add_to_upper else 0
        if left_lower  + right_upper + 1 == 5 and self.board[row][column] != None:
            return OmokBoard.WIN if self.board[row][column] else OmokBoard.LOSS
        
        # No winner yet
        return 0
