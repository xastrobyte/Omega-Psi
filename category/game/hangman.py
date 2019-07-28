from database.database import database

from random import choice as choose

class Hangman:
    """Creates a Hangman game for the specified player.

    Parameters:
        player (discord.User): The Discord User to create the game for.
        difficulty (str): The difficulty of the hangman word.
    """

    GUESSED = "GUESSED"
    FAILED = "FAILED"
    WORD = "WORD"
    NOT_ALPHA = "NOT_ALPHA"
    WON = "WON"

    STAGES = [
        "https://i.imgur.com/hRzVg1N.png",
        "https://i.imgur.com/cQmLMDO.png",
        "https://i.imgur.com/sAeTvqP.png",
        "https://i.imgur.com/yHGrZqc.png",
        "https://i.imgur.com/UKiV6J9.png",
        "https://i.imgur.com/w7QJQFH.png",
        "https://i.imgur.com/apN30T6.png",
        "https://i.imgur.com/KBMsCp9.png"
    ]

    def __init__(self, player):
        """Creates a Hangman game for the specified player.

        Parameters:
            player (discord.User): The Discord User to create the game for.
            difficulty (str): The difficulty of the hangman word.
        """

        self._player = player

        self._guesses = 0
        self._found = []

        self._fails = 0
        self._guessed = []
    
    # Getters

    def get_player(self):
        """Returns the player that is playing this Hangman game.
        """
        return self._player
    
    def get_word(self):
        """Returns the actual word for this hangman game.
        """
        return self._word
    
    def get_guesses(self):
        """Returns the amount of guesses it took the player to guess the word.
        """
        return self._guesses
    
    def get_guessed(self):
        """Returns the letters that were already guessed.
        """
        return self._guessed
    
    def is_winner(self):
        """Returns whether or not all letters have been found in the word.
        """
        return "".join([letter for letter in self._word if (letter in self._found or not letter.isalpha())]) == self._word

    # Setters

    async def generate_word(self):
        """Generates a random word and returns it in hangman style.\n

        difficulty - The difficulty of the word to get.\n

            Examples:\n
                \"half-asleep\" --> \"_ _ _ _ - _ _ _ _ _ _\"\n
                \"ping pong\"   --> \"_ _ _ _  _ _ _ _\"\n
                \"apple\"       --> \"_ _ _ _ _\"\n
        """
        self._word = await database.data.get_hangman_words()
        self._word = choose(self._word["words"])["value"].lower()

    def get_hangman_word(self):

        # Replace letters in word if letter was not found
        newWord = ""
        for char in range(len(self._word)):
            if self._word[char] in self._found:
                newWord += self._word[char]
            else:
                if self._word[char].isalpha():
                    newWord += "_"
                else:
                    newWord += self._word[char]

            # Only add extra space between letters if char is less than length - 1
            if char < len(self._word) - 1:
                newWord += " "
        
        return "```\n{}```".format(newWord)

    def get_hangman(self):
        """Returns the Hangman ascii text depending on how many guesses there are.\n

        guesses - The amount of guesses a user has made.\n
        """

        # """
        hangman = (
            "```css\n" +
            "+----+    \n" +
            "|    |    \n" +
            "|    {0}    \n" +
            "|   {2}{1}{3}   \n" +
            "|    {4}    \n" +
            "|   {5} {6}   \n" +
            "|         \n" +
            "+--------+\n" +
            "|  {7}  |\n" +
            "+--------+\n" +
            "```"
        )

        return hangman.format(
            "0" if self._fails >= 1 else " ",
            "|" if self._fails >= 2 else " ",
            "\\" if self._fails >= 3 else " ",
            "/" if self._fails >= 4 else " ",
            "|" if self._fails >= 5 else " ",
            "/" if self._fails >= 6 else " ",
            "\\" if self._fails >= 7 else " ",
            "DEAD" if self._fails >= 8 else "    "
        )
        # """

        # return Hangman.STAGES[self._fails]

    # Other Methods

    def make_guess(self, guess):
        """Allows the player to make a guess on the hangman word.
        """

        # Check if guess is not a letter
        if not guess.isalpha():
            return Hangman.NOT_ALPHA

        # Check if guess is the word
        elif guess == self._word:
            return Hangman.WORD

        # Check if guess is already in found
        elif guess in self._guessed:
            return Hangman.GUESSED
        
        # Check if guess is not in word
        elif guess not in self._word:
            self._guessed.append(guess)
            self._fails += 1
            self._guesses += 1

            # Check if fail limit was reached
            if self._fails >= 8:
                return Hangman.FAILED

            return False
        
        # Guess is in word
        else:
            self._guessed.append(guess)
            self._found.append(guess)
            self._guesses += 1

            # Check if all letters were found
            if self.is_winner():
                return Hangman.WON

            return True