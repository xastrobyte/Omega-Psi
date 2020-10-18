from asyncio import sleep
from discord import Embed

from cogs.game.minigames.base_game.game import Game
from cogs.game.minigames.mastermind.player import MastermindPlayer

from util.database.database import database
from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class MastermindGame(Game):
    """A MastermindGame that holds information about a player's game
    of mastermind

    :param bot: The bot to use to wait for reactions
    :param ctx: The context of where the game is being played
    :param challenger: The player that is playing the game
    """

    def __init__(self, bot, ctx, challenger):
        super().__init__(
            bot, ctx,
            challenger = MastermindPlayer(challenger),
            opponent = MastermindPlayer(1) # Currently, it's 1 (an AI) because the opponent player will
                                           # setup the game and the challenger will make the guesses
                                           # which makes the opponent player not have to do anything
                                           # for the rest of the game and that's just boring
        )
        self.current_player = 0
        self.code = None
        self.guesses = [
            "{} | {}".format(
                ":black_circle:" * 4,
                ":black_circle:" * 4
            )
            for i in range(10)
        ]
        self.message = None
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Getters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @property
    def code(self):
        return self.__code
    
    @property
    def guesses(self):
        return self.__guesses

    @property
    def message(self):
        return self.__message

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Setters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @code.setter
    def code(self, code):
        self.__code = code
    
    @guesses.setter
    def guesses(self, guesses):
        self.__guesses = guesses
    
    @message.setter
    def message(self, message):
        self.__message = message

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Play Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def play(self):
        """Allows the player to play a game of Mastermind
        """
        self.code = await self.opponent.ask_for_code(self)
        won = False
        for i in range(9, -1, -1):

            # Display the message and ask the challenger player to make a guess
            guess = await self.challenger.ask_for_guess(self)
            print(guess)

            # Check if the guess is the same as the code
            if guess == self.code:
                won = True

            # Get a number of black and white dots to be shown
            black = 0
            white = 0
            for j in range(len(guess)):
                if guess[j] == self.code[j]:
                    black += 1
                elif guess[j] in self.code:
                    white += 1
            
            # Get a string of brown and white dots
            result = ":brown_circle:" * black + ":white_circle:" * white + ":black_circle:" * (4 - black - white)
            self.guesses[i] = "{} | {}".format(guess, result)
            await self.message.edit(
                embed = Embed(
                    title = "Mastermind",
                    description = "{}\n\n{}".format(
                        self.get_guesses(),
                        "Your Guess: " if not won else "You won!"
                    ),
                    colour = await get_embed_color(self.challenger.member)
                )
            )
            await sleep(1) # Sleep for 1 second to reduce possibility of the message resetting to a previous message

            # If the player won, break from the game
            if won:
                break
        
        # Check if the player guessed in 10 guesses (won == True)
        if not won:
            await self.message.edit(
                embed = Embed(
                    title = "Mastermind",
                    description = "{}\n\nYou lost :(\nCode: {}".format(
                        self.get_guesses(),
                        self.code
                    ),
                    colour = await get_embed_color(self.challenger.member)
                )
            )
        await database.users.update_mastermind(self.challenger.member, won)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Other Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_guesses(self):
        """Returns a list of guesses made in the game
        into a single string

        :rtype: str
        """
        return "\n".join(self.guesses)