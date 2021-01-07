from discord import Member, Embed
from functools import partial
from requests import get
from os import environ
from urllib.parse import quote

from cogs.globals import loop
from cogs.game.minigames.base_game.game import Game

from util.database.database import database
from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

WORDS_API     = "https://wordsapiv1.p.rapidapi.com/words/?random=true"
WORD_FREQ_API = "https://wordsapiv1.p.rapidapi.com/words/{}/frequency"
HANGMAN_CHARS = ["O", "/", "|", "\\", "/", "\\"]

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class HangmanGame(Game):
    """A HangmanGame contains information about a game of hangman
    that is played by a single player

    :param bot: The bot object this game is connected to
    :param ctx: The context of where the game will be played
    :param member: The Member that is playing the game
    """
    def __init__(self, bot, ctx, member: Member):
        super().__init__(
            bot, ctx,
            challenger = member, 
            opponent = member)
        self.message = None
        self.word = None
        self.guesses = ""
        self.mistakes = 0
        self.word_rarity = 7

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def play(self):
        """Allows the game of Hangman to be played"""

        # Get a word from the Words API
        response = await loop.run_in_executor(
            None, 
            partial(
                get, WORDS_API,
                headers = {
                    "x-rapidapi-key": environ["RAPID_API_KEY"]
                }
            ))
        response = response.json()
        self.word = response["word"]
        response = await loop.run_in_executor(
            None,
            partial(
                get, WORD_FREQ_API.format(quote(self.word)),
                headers = {
                    "x-rapidapi-key": environ["RAPID_API_KEY"]
                }
            ))
        response = response.json()
        if "frequency" in response:
            self.word_rarity = response["frequency"]["zipf"]
            if self.word_rarity < 1:
                self.word_rarity = "Rarely Used"
            elif self.word_rarity < 2:
                self.word_rarity = "Used a Few Times"
            elif self.word_rarity < 3:
                self.word_rarity = "Not Always Used"
            elif self.word_rarity < 4:
                self.word_rarity = "Sometimes Used"
            elif self.word_rarity < 5:
                self.word_rarity = "Used Averagely"
            elif self.word_rarity < 6:
                self.word_rarity = "Used Quite Often"
            else:
                self.word_rarity = "Used Everyday"
        else:
            self.word_rarity = ""
        
        # Play until the player loses or guesses correctly
        won = False
        while self.mistakes < 6:
            # Create the embed for the player
            embed = Embed(
                title = "Hangman!",
                description = self.get_hangman(),
                colour = await get_embed_color(self.challenger)
            ).add_field(
                name = "Guesses",
                value = ", ".join(self.guesses) if len(self.guesses) > 0 else "No Guesses Yet",
                inline = False
            )

            if self.message is None:
                self.message = await self.ctx.send(embed = embed)
            else:
                await self.message.edit(embed = embed)
            
            # Allow the player to make a guess
            guess = await self.make_guess()

            # Check if the guess is a letter or a word
            if len(guess) == 1:

                # Check if the guess hasn't been made yet
                if guess not in self.guesses:
                    self.guesses += guess
                    if guess not in self.word:
                        self.mistakes += 1
                    else:

                        # Check if the user has guessed all the letters in the word
                        all_letters = True
                        for char in self.word:
                            if char not in self.guesses and char.isalpha():
                                all_letters = False
                                break
                        if all_letters:
                            await self.message.delete()
                            won = True
                            break
                
                # The guess has been made
                else:
                    await self.ctx.send(embed = Embed(
                        title = "Already Guessed!",
                        description = "You already guessed that letter!",
                        colour = 0x800000
                    ), delete_after = 10)
            else:
                word_only_letters = "".join([
                    char
                    for char in self.word
                    if char.isalpha()
                ])
                guess_only_letters = "".join([
                    char
                    for char in guess
                    if char.isalpha()
                ])

                if word_only_letters == guess_only_letters:
                    won = True
                    break
                else:
                    await self.ctx.send(embed = Embed(
                        title = "Incorrect.",
                        description = "That's not the correct word!",
                        colour = 0x800000
                    ), delete_after = 10)

        await self.ctx.send(embed = Embed(
            title = "You Won!" if won else "You Lost!",
            description = f"The word was {self.word}!",
            colour = await get_embed_color(self.ctx.author)
        ))
        await database.users.update_hangman(self.ctx.author, won)
    
    async def make_guess(self) -> str:
        """Allows the player (challenger) of this Hangman game to
        make a guess

        :returns: The guess the player made
        """

        # Get the player's guess
        message = await self.bot.wait_for("message", check = lambda m: (
            m.author.id == self.challenger.id and
            m.channel.id == self.ctx.channel.id
        ))
        await message.delete()
        guess = message.content.lower().strip()
        return guess
    
    def get_hangman(self) -> str:
        """Gets the hangman string based off the amount of mistakes
        and what has been guessed correctly

        :returns: A string containing the hangman noose, the guessed word,
            and the rarity of the word
        """

        # Create the hangman ASCII art
        hangman = (
            """
            ```
             ------
             |    |
             {0}    |
            {1}{2}{3}   |
            {4} {5}   |
                  |
            -------
            ```
            """
        ).format(*(HANGMAN_CHARS[:self.mistakes] + [" "] * (6 - self.mistakes)))

        # Create the hangman text by splitting up the text by letter
        #   and adding a space in between each letter
        #   but showing the letters that have been guessed already
        guessed_text = ""
        for i in range(len(self.word)):
            char = self.word[i]
            if char in self.guesses or not char.isalpha() or char == " ":
                guessed_text += char
            else:
                guessed_text += "_"
            if i < len(self.word) - 1:
                guessed_text += " "
        
        # Give the player a hint based on the zipf parameter
        #   of the word
        return f"{self.word_rarity}\n{hangman}\n\n`{guessed_text}`"