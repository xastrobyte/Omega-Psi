from database import database

from random import choice as choose

class Scramble:
    """Creates a Scramble game for the specified player.

    Parameters:
        player (discord.User): The Discord User to create the game for.
        difficulty (str): The difficulty of the game.
    """

    HINTS = [
        "hint",
        "hint me",
        "i need a hint",
        "hint please"
    ]

    def __init__(self, player, difficulty):
        """Creates a Scramble game for the specified player.

        Parameters:
            player (discord.User): The Discord User to create the game for.
            difficulty (str): The difficulty of the game.
        """

        self._player = player
        self._difficulty = difficulty
        self._hints_used = 0
        self._message = None
    
    # Getters

    def set_message(self, message):
        self._message = message

    def get_message(self):
        return self._message

    def get_player(self):
        """Returns the player that is playing the scramble game.
        """
        return self._player

    def get_word(self):
        """Returns the word/phrase that this scramble game uses.
        """
        return self._word["value"].lower()
    
    def get_scrambled_word(self):
        """Returns the scrambled version of this word/phrase
        """
        return self._scramble.lower()
    
    def get_hint(self):
        """Returns a random hint for the scrambled word.
        """
        self._hints_used += 1
        return choose(self._hints).lower()
    
    def get_hints_used(self):
        """Returns the amount of hints used in the game.
        """
        return self._hints_used

    # Setters

    async def generate_word(self):
        """Returns a random word from the list of words in the database
        """
        self._word = await database.get_scramble_words()
        self._word = choose(self._word["words"])
        self._hints = self._word["hints"]
        self._scramble = self.scramble_word(self._word["value"], self._difficulty)

    def scramble_word(self, word, difficulty):
        """Returns a scrambled word.\n

        difficulty - The difficulty of the scrambled word.\n
            Note: A \"normal\" difficulty will scramble each word (if there are multiple words).\n
                  An \"expert\" difficulty will scramble the entire phrase.\n
        """

        # Normal scramble
        if difficulty == "normal":

            # Split words into list
            wordList = word.split(" ")
            newWordList = []
            for word in wordList:
                newWordList.append(
                    self.scramble_word(word, "expert")
                )
            
            return " ".join(newWordList)
        
        # Expert scramble
        else:

            # Split up word normally
            wordList = list(word)
            newWord = ""
            while len(wordList) > 0:
                char = choose(wordList)
                wordList.remove(char)
                newWord += char
            return newWord

    # Other Methods

    def make_guess(self, guess):
        """Allows the player to make a guess.

        Parameters:
            guess (str): The guess that the player made.
        """

        # See if guess is asking for a hint
        if guess in Scramble.HINTS:
            return self.get_hint()
        
        # See if guess is equal to the word
        elif guess == self.get_word():
            return True
        
        # Guess is not the word
        return False


