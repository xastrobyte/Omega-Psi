import asyncio, discord

from discord.ext import commands
from discord.ext.commands import is_nsfw, guild_only
from random import choice as choose

from category import errors
from category.globals import PRIMARY_EMBED_COLOR
from category.predicates import is_developer

from database import database

from .connect_four import ConnectFour
from .tic_tac_toe import TicTacToe
from .scramble import Scramble
from .hangman import Hangman
from .cards_against_humanity import CardsAgainstHumanity

# # # # # # # # # # # # # # # # # # # # # # # # #

CONNECT_FOUR_REACTIONS = [
    "1\u20e3",
    "2\u20e3",
    "3\u20e3",
    "4\u20e3",
    "5\u20e3",
    "6\u20e3",
    "7\u20e3",
    "❌"
]

TIC_TAC_TOE_REACTIONS = [
    "1\u20e3",
    "2\u20e3",
    "3\u20e3",
    "4\u20e3",
    "5\u20e3",
    "6\u20e3",
    "7\u20e3",
    "8\u20e3",
    "9\u20e3",
    "❌"
]

RED_PIECE = "🔴"
X_PIECE = "❌"

ROBOT = "🤖"
QUIT = "❌"

REACT_100 = "💯"

# # # # # # # # # # # # # # # # # # # # # # # # #

RPS_ACTIONS = ["rock", "paper", "scissors"]

# # # # # # # # # # # # # # # # # # # # # # # # #

class Game:
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @commands.command(
        name = "gamestats",
        description = "Gets the stats of someone you specify, or yourself, of all mini-games in the bot.",
        cog_name = "Game"
    )
    async def gamestats(self, ctx, member = None):

        # Member is none or in private message; Get self
        if member == None or ctx.guild == None:
            member = ctx.author
        
        # Member is not none; Find member
        else:

            # See if member is not a discord.Member`
            if type(member) != discord.Member:

                # Look for member in guild
                found = False
                members = ctx.guild.members
                for _member in members:
                    if member.lower() == _member.name.lower():
                        member = _member
                        found = True
                        break
                    
                if not found:
                    member = None
                    await ctx.send(
                        embed = errors.get_error_message(
                            "That member was not found in this guild."
                        )
                    )
        
        # Get member if it is not None
        if member != None:
            stats = {
                ":skull_crossbones: Hangman": await database.get_hangman(member),
                ":cyclone: Scramble": await database.get_scramble(member),
                ":scissors: RPS": await database.get_rps(member),
                ":x: Tic Tac Toe": await database.get_tic_tac_toe(member),
                ":red_circle: Connect Four": await database.get_connect_four(member),
                "<:cah:540281486633336862> CAH": await database.get_cards_against_humanity(member)
            }

            embed = discord.Embed(
                title = "Stats",
                description = "Game Stats for {}".format(member.mention),
                colour = PRIMARY_EMBED_COLOR
            )

            for stat in stats:
                won = stats[stat]["won"]
                lost = stats[stat]["lost"]

                embed.add_field(
                    name = "{} ({})".format(
                        stat, 
                        0 if won == 0 else (won if lost == 0 else round(won / lost, 2))
                    ),
                    value = "Won: {}\nLost: {}".format(won, lost)
                )

            await ctx.send(
                embed = embed
            )

    @commands.command(
        name = "hangman",
        description = "Allows you to play a Hangman game.",
        cog_name = "Game"
    )
    async def hangman(self, ctx, *, difficulty : str = "easy"):
        
        # Validate difficulty
        valid = True
        if difficulty in ["easy", "e"]:
            difficulty = "easy"
        elif difficulty in ["medium", "m"]:
            difficulty = "medium"
        elif difficulty in ["hard", "h"]:
            difficulty = "hard"
        
        # Difficulty was invalid
        else:
            valid = False
            await ctx.send(
                embed = errors.get_error_message(
                    "The difficulty you have was invalid."
                )
            )
        
        if valid:
            try: await ctx.message.delete()
            except: pass

            # Create hangman game
            game = Hangman(ctx.author, difficulty)
            await game.generate_word()

            msg = await ctx.send(
                embed = discord.Embed(
                    title = "Hangman",
                    description = "{}\nGuesses: {}".format(
                        game.get_hangman_word(),
                        ", ".join(game.get_guessed()) if len(game.get_guessed()) > 0 else "No Guesses"
                    ),
                    colour = PRIMARY_EMBED_COLOR
                ).set_image(
                    url = game.get_hangman()
                )
            )

            # Wait until loss or win
            while True:

                # Get guess
                def check_guess(message):
                    return message.author == game.get_player() and (len(message.content) == 1 or message.content == game.get_word())
                guess_message = await self.bot.wait_for("message", check = check_guess)
                guess = guess_message.content.lower()
                try: await guess_message.delete()
                except: pass

                # Make the guess
                guess = game.make_guess(guess)

                # Guess was the word
                if guess == Hangman.WORD:

                    await msg.edit(
                        embed = discord.Embed(
                            title = "Guessed",
                            description = "You guessed correctly! The word was {}\nIt took you {} guess{}!".format(
                                game.get_word(),
                                game.get_guesses(),
                                "es" if game.get_guesses() != 1 else ""
                            ),
                            colour = PRIMARY_EMBED_COLOR
                        ),
                        delete_after = 5
                    )

                    await database.update_hangman(game.get_player(), True)
                    break
                
                # Guess was not a letter
                elif guess == Hangman.NOT_ALPHA:
                    await ctx.send(
                        embed = errors.get_error_message(
                            "That is not a letter."
                        ),
                        delete_after = 5
                    )
                
                # Guess was already guessed
                elif guess == Hangman.GUESSED:
                    await ctx.send(
                        embed = errors.get_error_message(
                            "You already guessed that letter."
                        ),
                        delete_after = 5
                    )
                
                # Guess was a fail
                elif guess == Hangman.FAILED:
                    await msg.edit(
                        embed = discord.Embed(
                            title = "Game Ended - Word: `{}`".format(game.get_word()),
                            description = "You did not guess the word quick enough.",
                            colour = PRIMARY_EMBED_COLOR
                        ).set_image(
                            url = game.get_hangman()
                        ),
                        delete_after = 5
                    )

                    await database.update_hangman(game.get_player(), False)
                    break
                
                # Guess was a win
                elif guess == Hangman.WON:
                    await msg.edit(
                        embed = discord.Embed(
                            title = "Success!",
                            description = "The word was `{}`\nYou guessed in {} guess{}.".format(
                                game.get_word(),
                                game.get_guesses(),
                                "es" if len(game.get_guessed()) > 1 else ""
                            ),
                            colour = PRIMARY_EMBED_COLOR
                        ),
                        delete_after = 5
                    )

                    await database.update_hangman(game.get_player(), True)
                    break
                
                # Guess was a correct/incorrect letter
                elif guess in [True, False]:
                    await msg.edit(
                        embed = discord.Embed(
                            title = "Hangman",
                            description = "{}\nGuesses: {}".format(
                                game.get_hangman_word(),
                                ", ".join(game.get_guessed()) if len(game.get_guessed()) > 0 else "No Guesses"
                            ),
                            colour = PRIMARY_EMBED_COLOR
                        ).set_image(
                            url = game.get_hangman()
                        )
                    )
    
    @commands.command(
        name = "scramble",
        description = "Allows you to play Scramble game.",
        cog_name = "Game"
    )
    async def scramble(self, ctx, *, difficulty : str = "normal"):
        
        # Validate difficulty
        valid = True
        if difficulty in ["normal", "n"]:
            difficulty = "normal"
        elif difficulty in ["expert", "e"]:
            difficulty = "expert"
        
        # Difficulty was invalid
        else:
            valid = False
            await ctx.send(
                embed = errors.get_error_message(
                    "The difficulty you gave was invalid."
                )
            )
        
        if valid:
            try: await ctx.message.delete() 
            except: pass

            # Create scramble game
            game = Scramble(ctx.author, difficulty)
            await game.generate_word()

            msg = await ctx.send(
                embed = discord.Embed(
                    title = "Scrambled",
                    description = "Unscramble this word/phrase. You have 15 seconds. Good luck.\n`{}`".format(
                        game.get_scrambled_word()
                    ),
                    colour = PRIMARY_EMBED_COLOR
                ).add_field(
                    name = "Hint",
                    value = game.get_hint()
                )
            )

            # Wait for guess
            try:
                def check_player(message):
                    return message.author == game.get_player()
                guess_message = await self.bot.wait_for("message", timeout = 15, check = check_player)
                guess = guess_message.content.lower()
                try: await guess_message.delete()
                except: pass

                # Check if it's right
                if len(guess) > 1:

                    guess = game.make_guess(guess)

                    await msg.delete()
                    await ctx.send(
                        embed = discord.Embed(
                            title = "Success" if guess else "Failed",
                            description = "{} `{}`.".format(
                                "You guessed the word correctly! It was" if guess else "Unfortunately, you did not guess the word.\nThe word was",
                                game.get_word()
                            ),
                            colour = PRIMARY_EMBED_COLOR
                        ),
                        delete_after = 5
                    )

                    await database.update_scramble(ctx.author, guess)

            except asyncio.TimeoutError:

                await msg.delete()
                await ctx.send(
                    embed = discord.Embed(
                        title = "Timed Out",
                        description = "Unfortunately, you did not guess the word in time.\nThe word was `{}`".format(
                            game.get_word()
                        ),
                        colour = PRIMARY_EMBED_COLOR
                    ),
                    delete_after = 5
                )

                await database.update_scramble(ctx.author, False)
    
    @commands.command(
        name = "rps",
        description = "Allows you to play Rock Paper Scissors.",
        cog_name = "Game"
    )
    async def rps(self, ctx, action = None):
        
        # Validate user's action
        valid = True
        if action in ["rock", "r"]:
            user_action = "rock"
        elif action in ["paper", "p"]:
            user_action = "paper"
        elif action in ["scissors", "s"]:
            user_action = "scissors"
        
        # Action was invalid
        else:
            valid = False
            embed = errors.get_error_message(
                "The action you gave was invalid."
            )
        
        if valid:
            try: await ctx.message.delete() 
            except: pass

            # Generate bot's action
            bot_action = choose(RPS_ACTIONS)

            # Check if values are the same
            result = "You had {} and I had {}".format(
                user_action, bot_action
            )

            if bot_action == user_action:
                title = "Tied!"
                result = "You and I both tied."
            
            elif (
                (bot_action == "rock" and user_action == "paper") or 
                (bot_action == "paper" and user_action == "scissors") or
                (bot_action == "scissors" and user_action == "rock")
            ):
                title = "You Won!"
                await database.update_rps(ctx.author, True)
            
            elif (
                (bot_action == "rock" and user_action == "scissors") or 
                (bot_action == "paper" and user_action == "rock") or
                (bot_action == "scissors" and user_action == "paper")
            ):
                title = "You Lost!"
                await database.update_rps(ctx.author, True)
            
            embed = discord.Embed(
                title = title,
                description = result,
                colour = PRIMARY_EMBED_COLOR
            )

        await ctx.send(
            embed = embed,
            delete_after = 5
        )
    
    @commands.command(
        name = "ticTacToe", 
        aliases = ["ttt"],
        description = "Allows you to play a game of Tic Tac Toe with the AI or a person who reacts to it.",
        cog_name = "Game"
    )
    async def tic_tac_toe(self, ctx, *, difficulty : str = None):

        # Ask if anyone specific is joining; Only if difficulty is not given
        if difficulty == None:
            msg = await ctx.send(
                embed = discord.Embed(
                    title = "Waiting for Player",
                    description = "If you're going to play against {}, react with {}.\n{}, if you're playing alone, react with {}.".format(
                        ctx.author.mention, RED_PIECE,
                        ctx.author.mention, ROBOT
                    ),
                    colour = PRIMARY_EMBED_COLOR
                )
            )
            await msg.add_reaction(
                X_PIECE
            )
            await msg.add_reaction(
                ROBOT
            )

            # Wait for reaction
            def check_start(reaction, user):

                return (

                    # Reaction is X_PIECE and user is not challenger
                    (str(reaction) == X_PIECE and user != ctx.author and not user.bot) or 

                    # Reaction is ROBOT and user is challenger
                    (str(reaction) == ROBOT and user == ctx.author)

                )
        
        try:
            if difficulty == None:
                reaction, user = await self.bot.wait_for("reaction_add", check = check_start, timeout = 10)
                try: await msg.delete()
                except: pass
            
            else:
                reaction = ROBOT

            # Reaction is X_PIECE, set opponent
            if str(reaction) == X_PIECE:
                game = TicTacToe(difficulty, ctx.author, user)
            
            # Reaction is ROBOT, set challenger only
            else:
                if difficulty == None:
                    difficulty = "easy"
                game = TicTacToe(difficulty, ctx.author)
            
            # Show game board and add reactions
            msg = await ctx.send(
                embed = discord.Embed(
                    title = "Tic Tac Toe",
                    description = "{}'s Turn\n{}\n{}\n{}".format(
                        game.get_challenger().mention if game.is_challenger_move() else "{}".format(
                            "AI" if game.get_opponent() == None else game.get_opponent().mention
                        ),
                        game.show_board(),
                        ":x: {}".format(
                            game.get_challenger().mention
                        ),
                        ":o: {}".format(
                            "AI" if game.get_opponent() == None else game.get_opponent().mention
                        )
                    ),
                    colour = PRIMARY_EMBED_COLOR
                )
            )
            for reaction in TIC_TAC_TOE_REACTIONS:
                await msg.add_reaction(reaction)
            
            game.set_message(msg)

            # Play until something happens
            while True:
                
                # Wait for a reaction
                try:

                    def check_play(reaction, user):
                        return (

                            # Reaction is a connect four reaction and user is current player
                            (str(reaction) in TIC_TAC_TOE_REACTIONS and user == game.get_current_player()) or

                            # Reaction is quit and user is in the game
                            (str(reaction) == QUIT and user in [game.get_challenger(), game.get_opponent()])
                        ) and (
                            reaction.message.id == game.get_message().id
                        )

                    # Only wait if either player's turn on AI game or any turn in real person game
                    if game.get_opponent() == None and game.is_challenger_move() or game.get_opponent() != None:

                        done, pending = await asyncio.wait([
                            self.bot.wait_for("reaction_add", check = check_play),
                            self.bot.wait_for("reaction_remove", check = check_play)
                        ], return_when = asyncio.FIRST_COMPLETED)
                        reaction, user = done.pop().result()

                        # Cancel any futures
                        for future in pending:
                            future.cancel()
                    
                    else:
                        reaction = None

                    # See if the reaction was QUIT
                    if str(reaction) == str(QUIT):
                        try: await game.get_message().delete()
                        except: pass

                        # If the user was in a game with a real person, it counts as forfeiture
                        if game.get_opponent() != None:
                            await database.update_tic_tac_toe(game.get_challenger(), False)
                            await database.update_tic_tac_toe(game.get_opponent(), True)

                        await ctx.send(
                            embed = discord.Embed(
                                title = "Game Quit",
                                description = "The game was successfully quit.",
                                colour = 0xEC7600
                            ),
                            delete_after = 5
                        )

                        break
                    
                    else:
                
                        # Make move
                        result = game.make_move(TIC_TAC_TOE_REACTIONS.index(str(reaction)))

                        # Column is full
                        while result == TicTacToe.SPOT_TAKEN:
                            await ctx.send(
                                embed = discord.Embed(
                                    title = "Invalid Move",
                                    description = "That spot is taken.",
                                    colour = 0xFF8000
                                ),
                                delete_after = 5
                            )

                            done, pending = await asyncio.wait([
                                self.bot.wait_for("reaction_add", check = check_play),
                                self.bot.wait_for("reaction_remove", check = check_play)
                            ], return_when = asyncio.FIRST_COMPLETED)
                            reaction, user = done.pop().result()

                            # Cancel any futures
                            for future in pending:
                                future.cancel()

                            result = game.make_move(TIC_TAC_TOE_REACTIONS.index(str(reaction)))
                        
                        # There is a draw
                        if result == TicTacToe.DRAW:
                            await game.get_message().edit(
                                embed = discord.Embed(
                                    title = "Draw!",
                                    description = "{}\n{}\n{}".format(
                                        game.show_board(),
                                        ":x: {}".format(
                                            game.get_challenger().mention
                                        ),
                                        ":o: {}".format(
                                            "AI" if game.get_opponent() == None else game.get_opponent().mention
                                        )
                                    ),
                                    colour = PRIMARY_EMBED_COLOR
                                ),
                                delete_after = 5
                            )

                            break
                        
                        # There is a winner
                        elif result in [True, False]:

                            # Update wins/losses
                            await database.update_tic_tac_toe(game.get_challenger(), result)
                            if game.get_opponent() != None:
                                await database.update_tic_tac_toe(game.get_challenger(), not result)
                            
                            # Edit embed
                            await game.get_message().edit(
                                embed = discord.Embed(
                                    title = "{} Wins!".format(
                                        "{}#{}".format(
                                            game.get_challenger().display_name,
                                            game.get_challenger().discriminator
                                        ) if result else "{}".format(
                                            "AI" if game.get_opponent() == None else "{}#{}".format(
                                                game.get_opponent().display_name,
                                                game.get_opponent().discriminator
                                            )
                                        )
                                    ),
                                    description = "{}\n{}\n{}".format(
                                        game.show_board(),
                                        ":x: {}".format(
                                            game.get_challenger().mention
                                        ),
                                        ":o: {}".format(
                                            "AI" if game.get_opponent() == None else game.get_opponent().mention
                                        )
                                    ),
                                    colour = PRIMARY_EMBED_COLOR
                                ),
                                delete_after = 5
                            )

                            break
                        
                        # There is no winner yet
                        else:
                            await game.get_message().edit(
                                embed = discord.Embed(
                                    title = "Tic Tac Toe",
                                    description = "{}'s Turn\n{}\n{}\n{}".format(
                                        game.get_challenger().mention if game.is_challenger_move() else "{}".format(
                                            "AI" if game.get_opponent() == None else game.get_opponent().mention
                                        ),
                                        game.show_board(),
                                        ":x: {}".format(
                                            game.get_challenger().mention
                                        ),
                                        ":o: {}".format(
                                            "AI" if game.get_opponent() == None else game.get_opponent().mention
                                        )
                                    ),
                                    colour = PRIMARY_EMBED_COLOR
                                )
                            )
                
                except asyncio.TimeoutError:
                    try: await game.get_message().delete()
                    except: pass

                    await ctx.send(
                        embed = discord.Embed(
                            title = "Game Timed Out",
                            description = "The Tic Tac Toe game timed out. Automatically quitting.",
                            colour = 0xEC7600
                        ),
                        delete_after = 5
                    )

                    break
        
        # No responses
        except asyncio.TimeoutError:
            await ctx.send(
                embed = discord.Embed(
                    title = "No responses :frowning2:",
                    description = "It seems like no one wanted to play with you.",
                    colour = PRIMARY_EMBED_COLOR
                ),
                delete_after = 5
            )
    
    @commands.command(
        name = "connectFour", 
        aliases = ["cf"],
        description = "Allows you to play a game of Connect Four with the AI or a person who reacts to it.",
        cog_name = "Game"
    )
    async def connect_four(self, ctx):
        try: await ctx.message.delete() 
        except: pass

        # Ask if anyone specific is joining
        msg = await ctx.send(
            embed = discord.Embed(
                title = "Waiting for Player",
                description = "If you're going to play against {}, react with {}.\n{}, if you're playing alone, react with {}.".format(
                    ctx.author.mention, RED_PIECE,
                    ctx.author.mention, ROBOT
                ),
                colour = PRIMARY_EMBED_COLOR
            )
        )
        await msg.add_reaction(
            RED_PIECE
        )
        await msg.add_reaction(
            ROBOT
        )

        # Wait for reaction
        def check_start(reaction, user):

            return (

                # Reaction is RED_PIECE and user is not challenger
                (str(reaction) == RED_PIECE and user != ctx.author and not user.bot) or

                # Reaction is ROBOT and user is challenger
                (str(reaction) == ROBOT and user == ctx.author)

            )

        try:
            reaction, user = await self.bot.wait_for("reaction_add", check = check_start, timeout = 10)
            try: await msg.delete()
            except: pass

            # Reaction is RED_PIECE, set opponent
            if str(reaction) == RED_PIECE:
                game = ConnectFour(ctx.author, user)
            
            # Reaction is ROBOT, set challenger only
            else:
                game = ConnectFour(ctx.author)
            
            # Show game board and add reactions
            msg = await ctx.send(
                embed = discord.Embed(
                    title = "Connect Four",
                    description = "{}'s Turn\n{}\n{}\n{}".format(
                        game.get_challenger().mention if game.is_challenger_move() else "{}".format(
                            "AI" if game.get_opponent() == None else game.get_opponent().mention
                        ),
                        game.show_board(),
                        ":large_blue_circle: {}".format(
                            game.get_challenger().mention
                        ),
                        ":red_circle: {}".format(
                            "AI" if game.get_opponent() == None else game.get_opponent().mention
                        )
                    ),
                    colour = PRIMARY_EMBED_COLOR
                )
            )
            for reaction in CONNECT_FOUR_REACTIONS:
                await msg.add_reaction(reaction)
            
            game.set_message(msg)

            # Play until something happens
            while True:
                
                # Wait for a reaction
                try:

                    def check_play(reaction, user):
                        return (

                            # Reaction is a connect four reaction and user is current player
                            (str(reaction) in CONNECT_FOUR_REACTIONS and user == game.get_current_player()) or

                            # Reaction is quit and user is in the game
                            (str(reaction) == QUIT and user in [game.get_challenger(), game.get_opponent()])
                        ) and (
                            reaction.message.id == game.get_message().id
                        )

                    # Only wait if either player's turn on AI game or any turn in real person game
                    if game.get_opponent() == None and game.is_challenger_move() or game.get_opponent() != None:

                        done, pending = await asyncio.wait([
                            self.bot.wait_for("reaction_add", check = check_play),
                            self.bot.wait_for("reaction_remove", check = check_play)
                        ], return_when = asyncio.FIRST_COMPLETED)
                        reaction, user = done.pop().result()

                        # Cancel any futures
                        for future in pending:
                            future.cancel()
                    
                    else:
                        reaction = None

                    # See if the reaction was QUIT
                    if str(reaction) == str(QUIT):
                        try: await game.get_message().delete()
                        except: pass

                        # If the user was in a game with a real person, it counts as forfeiture
                        if game.get_opponent() != None:
                            await database.update_connect_four(game.get_challenger(), False)
                            await database.update_connect_four(game.get_opponent(), True)

                        await ctx.send(
                            embed = discord.Embed(
                                title = "Game Quit",
                                description = "The game was successfully quit.",
                                colour = 0xEC7600
                            ),
                            delete_after = 5
                        )

                        break
                    
                    else:
                
                        # Make move
                        result = game.make_move(CONNECT_FOUR_REACTIONS.index(str(reaction)))

                        # Column is full
                        while result == ConnectFour.COLUMN_FULL:
                            await ctx.send(
                                embed = discord.Embed(
                                    title = "Invalid Move",
                                    description = "That column is full. Go to another one.",
                                    colour = 0xFF8000
                                ),
                                delete_after = 5
                            )

                            done, pending = await asyncio.wait([
                                self.bot.wait_for("reaction_add", check = check_play),
                                self.bot.wait_for("reaction_remove", check = check_play)
                            ], return_when = asyncio.FIRST_COMPLETED)
                            reaction, user = done.pop().result()

                            # Cancel any futures
                            for future in pending:
                                future.cancel()

                            result = game.make_move(CONNECT_FOUR_REACTIONS.index(str(reaction)))
                        
                        # There is a draw
                        if result == ConnectFour.DRAW:
                            await game.get_message().edit(
                                embed = discord.Embed(
                                    title = "Draw!",
                                    description = "{}\n{}\n{}".format(
                                        game.show_board(),
                                        ":large_blue_circle: {}".format(
                                            game.get_challenger().mention
                                        ),
                                        ":red_circle: {}".format(
                                            "AI" if game.get_opponent() == None else game.get_opponent().mention
                                        )
                                    ),
                                    colour = PRIMARY_EMBED_COLOR
                                ),
                                delete_after = 5
                            )

                            break
                        
                        # There is a winner
                        elif result in [True, False]:

                            # Update wins/losses
                            await database.update_connect_four(game.get_challenger(), result)
                            if game.get_opponent() != None:
                                await database.update_connect_four(game.get_challenger(), not result)
                            
                            # Edit embed
                            await game.get_message().edit(
                                embed = discord.Embed(
                                    title = "{} Wins!".format(
                                        "{}#{}".format(
                                            game.get_challenger().display_name,
                                            game.get_challenger().discriminator
                                        ) if result else "{}".format(
                                            "AI" if game.get_opponent() == None else "{}#{}".format(
                                                game.get_opponent().display_name,
                                                game.get_opponent().discriminator
                                            )
                                        )
                                    ),
                                    description = "{}\n{}\n{}".format(
                                        game.show_board(),
                                        ":large_blue_circle: {}".format(
                                            game.get_challenger().mention
                                        ),
                                        ":red_circle: {}".format(
                                            "AI" if game.get_opponent() == None else game.get_opponent().mention
                                        )
                                    ),
                                    colour = PRIMARY_EMBED_COLOR
                                ),
                                delete_after = 5
                            )

                            break
                        
                        # There is no winner yet
                        else:
                            await game.get_message().edit(
                                embed = discord.Embed(
                                    title = "Connect Four",
                                    description = "{}'s Turn\n{}\n{}\n{}".format(
                                        game.get_challenger().mention if game.is_challenger_move() else "{}".format(
                                            "AI" if game.get_opponent() == None else game.get_opponent().mention
                                        ),
                                        game.show_board(),
                                        ":large_blue_circle: {}".format(
                                            game.get_challenger().mention
                                        ),
                                        ":red_circle: {}".format(
                                            "AI" if game.get_opponent() == None else game.get_opponent().mention
                                        )
                                    ),
                                    colour = PRIMARY_EMBED_COLOR
                                )
                            )
                
                except asyncio.TimeoutError:
                    try: await game.get_message().delete()
                    except: pass

                    await ctx.send(
                        embed = discord.Embed(
                            title = "Game Timed Out",
                            description = "The Connect Four game timed out. Automatically quitting.",
                            colour = 0xEC7600
                        ),
                        delete_after = 5
                    )

                    break
        
        # No responses
        except asyncio.TimeoutError:
            await ctx.send(
                embed = discord.Embed(
                    title = "No responses :frowning2:",
                    description = "It seems like no one wanted to play with you.",
                    colour = PRIMARY_EMBED_COLOR
                ),
                delete_after = 5
            )
    
    @commands.command(
        name = "cardsAgainstHumanity",
        aliases = ["cah"],
        description = "Allows you to play Cards Against Humanity with other people. (STILL IN DEVELOPMENT)",
        cog_name = "Game"
    )
    @guild_only()
    @is_nsfw()
    async def cards_against_humanity(self, ctx):

        # Wait for players (max of 5)
        players = [ctx.author]

        # Send join message
        msg = await ctx.send(
            embed = discord.Embed(
                title = "Join Cards Against Humanity",
                description = "React with :100: to join the game.\n**Players**\n{}".format(
                    "\n".join([user.mention for user in players])
                ),
                colour = PRIMARY_EMBED_COLOR
            )
        )

        await msg.add_reaction(REACT_100)

        play_game = None
        while play_game == None:

            # Wait for player reactions
            def check(reaction, user):
                return str(reaction) == REACT_100 and reaction.message.id == msg.id and user not in players and not user.bot
            
            # Try waiting
            try:
                reaction, user = await self.bot.wait_for("reaction_add", check = check, timeout = 30) # wait for 30 seconds maximum per person
                players.append(user)

                await msg.edit(
                    embed = discord.Embed(
                        title = "Join Cards Against Humanity",
                        description = "React with :100: to join the game.\n**Players**\n{}".format(
                            "\n".join([user.mention for user in players])
                        ),
                        colour = PRIMARY_EMBED_COLOR
                    )
                )

                # See if there are 5 players
                if len(players) == 5:
                    play_game = True
            
            # No one responded for 30 seconds
            except asyncio.TimeoutError:

                # Check if there are enough players
                play_game = len(players) >= 3
            
        # Check if game will be played
        if play_game:
            
            # Get a list of cards from database
            cah_cards = await database.get_cards_against_humanity_cards()
            black_cards = cah_cards["blackCards"]
            white_cards = cah_cards["whiteCards"]

            # Create the game
            game = CardsAgainstHumanity(players, black_cards, ctx.channel, self.bot)

            # Continue playing game until less than 3 people exist or until all black cards are gone

            while True:

                # Choose black card and give players cards
                await game.choose_cards(white_cards)

                # Wait for all submissions; See if people quit and there are less than 3 people left
                quit_game = await game.wait_for_submissions()
                if quit_game:
                    await ctx.send(
                        "{}, too many people left to continue playing :frowning2:".format(
                            " ".join([player.get_player().mention for player in game.get_players()])
                        )
                    )
                    break
                
                # Let the judge choose now
                await game.judge_choose()

                # See if anybody has won the game
                if game._game_over:

                    # Update all scores
                    winner = None
                    for player in game.get_players():
                        await database.update_cards_against_humanity(player.get_player(), player.get_wins() >= 7)
                        if player.get_wins() >= 7:
                            winner = player.get_player()
                    
                    # Send message to all players and channel
                    for player in game.get_players():
                        await player.get_player().send(
                            embed = discord.Embed(
                                title = "Game Over",
                                description = "{} won the Game!".format(winner.mention),
                                colour = 0xFF0000 if player.get_wins() < 7 else 0x00FF00
                            )
                        )
                    
                    await game._channel.send(
                            embed = discord.Embed(
                            title = "Game Over",
                            description = "{} won the Game!".format(winner.mention),
                            colour = PRIMARY_EMBED_COLOR
                        )
                    )
                    break

        # Game will not be played
        else:
            await msg.delete()
            await ctx.send(
                embed = discord.Embed(
                    title = "Not enough people :frowning2:",
                    description = "There needs to be at least 3 people to play Cards Against Humanity.",
                    colour = PRIMARY_EMBED_COLOR
                ),
                delete_after = 5
            )
    
    @cards_against_humanity.error
    async def nsfw_only_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):

            # Check if in guild; Not in NSFW channel
            if ctx.guild:
                await ctx.send(
                    embed = errors.get_error_message(
                        "This command can only be run in an NSFW channel."
                    )
                )
            
            # Not in guild
            else:
                await ctx.send(
                    embed = errors.get_error_message(
                        "This command can only be run in guilds. Not in DMs."
                    )
                )
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @commands.command(
        name = "addHangman",
        description = "Allows you to add a word/phrase to the Hangman list (DEV ONLY)",
        cog_name = "Game"
    )
    @commands.check(is_developer)
    async def add_hangman(self, ctx):
        pass
    
    @commands.command(
        name = "addScramble",
        description = "Allows you to add a word/phrase to the Scramble list (DEV ONLY)",
        cog_name = "Game"
    )
    @commands.check(is_developer)
    async def add_scramble(self, ctx):
        pass
    
def setup(bot):
    bot.add_cog(Game(bot))