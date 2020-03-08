from cogs.game.minigames.base_game.board import Board
from cogs.game.minigames.battleship.variables import BATTLESHIP_REACTIONS

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class BattleshipBoard(Board):
    """A BattleshipBoard object that holds information a board in a Battleship game"""

    SHIPS = [
        {
            "name": "Carrier",
            "length": 5,
            "number": 0,
            "emoji": ":red_square: "
        },
        {
            "name": "Battleship",
            "length": 4,
            "number": 1,
            "emoji": ":orange_square: "
        },
        {
            "name": "Cruiser",
            "length": 3,
            "number": 2,
            "emoji": ":yellow_square: "
        },
        {
            "name": "Submarine",
            "length": 3,
            "number": 3,
            "emoji": ":green_square: "
        },
        {
            "name": "Destroyer",
            "length": 2,
            "number": 4,
            "emoji": ":blue_square: "
        }
    ]

    EMPTY = ":black_circle: "
    MISS = ":white_circle: "
    HIT = ":x: "
    
    def __init__(self):
        super().__init__(10, 10)
        self.shots = []
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Getters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @property
    def shots(self):
        return self.__shots
    
    def get_at(self, row, column):
        """Returns the value at the specified row and column

        Parameters
        ----------
            row : int
                The row to get the value at
            column : int
                The column to get the value at
        
        Returns
        -------
            ship_number : int or None
                The ship number at the specified location
                If None is returned, the space is unoccupied
        """
        return self.board[row][column]

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Setters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @shots.setter
    def shots(self, shots):
        self.__shots = shots
    
    def set_at(self, row, column, ship_number):
        """Sets a ship number at the specified row and column

        Parameters
        ----------
            row : int
                The row to set the ship number at
            column : int
                The column to set the ship number at
            ship_number : int
                The ship number to set
        """
        if self.board[row][column] is None:
            self.board[row][column] = ship_number
            return True
        return False

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Other Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def fire(self, row, column):
        """Makes a shot at the specified location and returns whether or not it was a hit

        Parameters
        ----------
            row : int
                The row to make a move at
            column : int
                The column to make a move at
        
        Returns
        -------
            value : HIT or MISS
                A value describing whether the player hit a ship or if they missed
        """
        self.shots.append((row, column))
        if self.get_at(row, column) is not None:
            return BattleshipBoard.HIT
        return BattleshipBoard.MISS
    
    def did_ship_sink(self, ship_number = None):
        """Determines if the specified ship number has been sank

        Parameters
        ----------
            ship_number : int
                The ship number to determine if it sank or not

        Returns
        -------
            boolean
                Whether or not the specified ship has been sunken
        """

        # If the ship number does not exist, get the value at the last shot
        #   in the board
        if ship_number is None:
            ship_number = self.board[self.shots[-1][0]][self.shots[-1][1]]
        count = 0
        for shot in self.shots:
            if self.board[shot[0]][shot[1]] == ship_number:
                count += 1
        return count == BattleshipBoard.SHIPS[ship_number]["length"]
    
    def display(self, for_player, include_ships = True):
        """Returns the contents of this board in a string. If for_player is True,
        the ships will be shown using their associated emoji. Any shots the opponent made
        will be written with an X instead. Missed shots will be shown with a white bubble

        Parameters
        ----------
            for_player : boolean
                Whether or not to show the full contents of the board

        Keyword Parameters
        ------------------
            include_ships : boolean
                Whether or not to show which ships have been sunken
        
        Returns
        -------
            str
                The board in emoji representation
        """

        # Add a row of the column emojis to the result
        result = BattleshipBoard.EMPTY + " "
        for column in range(self.width):
            result += BATTLESHIP_REACTIONS[column] + " "
        result += "\n"

        # Add the emojis to the result to display the board
        for row in range(len(self.board)):

            # Add the row number to the current result
            result += BATTLESHIP_REACTIONS[row]
            for column in range(len(self.board[row])):

                # Check if the spot is a miss
                if (row, column) in self.shots and self.board[row][column] is None:
                    result += BattleshipBoard.MISS
                
                # Check if the spot is a hit
                elif (row, column) in self.shots and self.board[row][column] is not None:
                    result += BattleshipBoard.HIT
                
                # The spot is a ship and it's being displayed to the player
                elif self.board[row][column] is not None and for_player:
                    result += BattleshipBoard.SHIPS[self.board[row][column]]["emoji"]
                
                # The spot is open or is not being displayed to the player
                else:
                    result += BattleshipBoard.EMPTY
            result += "\n"
        
        # Add each sunken ship to the result
        if include_ships:
            result += "\n"
            for ship in BattleshipBoard.SHIPS:
                if self.did_ship_sink(ship["number"]):
                    result += "{} has been sunken!\n".format(ship["name"])
        return result