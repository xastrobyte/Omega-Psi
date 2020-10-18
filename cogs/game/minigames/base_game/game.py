from abc import abstractmethod
from random import randint, shuffle

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class Game:
    """A Game object that holds the important information for other possible games
    used in Omega Psi. When given a list of players, the game is set as a 2+ player game.
    When not given a list of players, the challenger and opponent parameters must be given.

    :param bot: The bot object to be used to wait for reactions
    :param ctx: The context of where this game is being played
    :param players: The list of players in the game
    :param challenger: The challenging player
    :param opponent: The opposition player

    :raises TypeError: When either the challenger of opponent is not given in a two-player game
    """

    def __init__(self, bot, ctx, *, players = [], challenger = None, opponent = None):

        # Validate that the players list given is not empty
        if len(players) != 0:
            self.players = players
            shuffle(self.players)
            self.current_player = 0
            self.two_players = False

        # A list of players is not given, 2-player game exists
        else:
            if not challenger or not opponent:
                raise TypeError("Challenger and Opponent in Game must be given.")
            
            self.challenger = challenger
            self.opponent = opponent
            self.current_player = randint(0, 1)
            self.two_players = True

        self.bot = bot
        self.ctx = ctx
        self.current_turn = None
        self.increase = 1

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Getters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @property
    def bot(self):
        return self.__bot
    
    @property
    def ctx(self):
        return self.__ctx

    @property
    def players(self):
        return self.__players

    @property
    def challenger(self):
        return self.__challenger

    @property
    def opponent(self):
        return self.__opponent
    
    @property
    def challenger_turn(self):
        return self.current_player == 0

    @property
    def current_player(self):
        return self.__current_player

    @property
    def max_players(self):
        return 2 if self.two_players else len(self.players)

    @property
    def two_players(self):
        return self.__two_players

    @property
    def current_turn(self):
        return self.__current_turn
    
    @property
    def increase(self):
        return self.__increase

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Setters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @bot.setter
    def bot(self, bot):
        self.__bot = bot
    
    @ctx.setter
    def ctx(self, ctx):
        self.__ctx = ctx

    @players.setter
    def players(self, players):
        self.__players = players

    @challenger.setter
    def challenger(self, challenger):
        self.__challenger = challenger

    @opponent.setter
    def opponent(self, opponent):
        self.__opponent = opponent

    @current_player.setter
    def current_player(self, current_player):
        self.__current_player = current_player

    @two_players.setter
    def two_players(self, two_players):
        self.__two_players = two_players

    @current_turn.setter
    def current_turn(self, current_turn):
        self.__current_turn = current_turn
    
    @increase.setter
    def increase(self, increase):
        self.__increase = increase

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Play Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @abstractmethod
    async def play(self):
        """Lets the players in this game play this Game"""
        pass

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Other Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_current_player(self):
        """Retrieves the current player in the game.

        :rtype: Player
        """

        # Check if the game is a two-player game
        if self.two_players:

            # In a two-player game:
            #   current_player = 0 is challenger
            #                  = 1 is opponent
            if self.current_player == 0: return self.challenger
            else: return self.opponent

        # The game is a 2+ player game
        else:
            return self.players[self.current_player]

    def get_next_player(self):
        """Retrieves the player that comes next in the game.

        :rtype: Player
        """

        # Check if the game is a two-player game
        if self.two_players:

            # In a two-player game:
            #   current_player = 0 is challenger; get opponent
            #                  = 1 is opponent; get challenger
            if self.current_player == 0: return self.opponent
            else: return self.challenger

        # The game is a 2+ player game
        else:

            # The next player is current_player + increase value
            next_player = self.current_player + self.increase

            # Check if current_player + increase is out of range of list
            if next_player >= self.max_players and self.increase > 0:
                next_player = 0
            elif next_player < 0 and self.increase < 0:
                next_player = self.max_players - 1

            return self.players[next_player]

    def next_player(self, *, skip_next = False):
        """Increases the current player value to move onto the next player.
        Wraps around if necessary.

        :param skip_next: Whether or not to skip the next player (Default: False)
        """

        # Increase the current player number to the next number
        #   if the next player is being skipped, skip them
        self.current_player += self.increase if not skip_next else (self.increase * 2)

        # Make sure the value wraps around the list
        #   subtract the amount of max players from the current player
        #   value in case a player was skipped
        if self.current_player >= self.max_players and self.increase > 0:
            self.current_player -= self.max_players
        elif self.current_player < 0 and self.increase < 0:
            self.current_player += self.max_players