import asyncio, base64, discord, os, random, requests

from discord.ext import commands
from random import choice as choose

from category import errors
from category.globals import get_embed_color, add_scroll_reactions
from category.globals import FIRST_PAGE, LAST_PAGE, PREVIOUS_PAGE, NEXT_PAGE, LEAVE, SCROLL_REACTIONS
from category.predicates import is_nsfw_and_guild, is_developer, guild_only

from database import loop
from database import database

from util.discord import send_webhook
from util.email import send_email

from .connect_four import ConnectFour
from .tic_tac_toe import TicTacToe
from .scramble import Scramble
from .hangman import Hangman
from .cards_against_humanity import CardsAgainstHumanity
from .uno import Uno, ADD_4_CARD

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

TRIVIA_REACTIONS = [
    "1\u20e3",
    "2\u20e3",
    "3\u20e3",
    "4\u20e3",
    "❌"
]

TRIVIA_CATEGORIES = {
    "Computers": {
        "shortcuts": ["comp"],
        "value": 18
    },
    "History": {
        "shortcuts": ["hist"],
        "value": 23
    },
    "Comics": {
        "shortcuts": ["comic"],
        "value": 29
    },
    "Video Games": {
        "shortcuts": ["games"],
        "value": 15
    },
    "Mathematics": {
        "shortcuts": ["math"],
        "value": 19
    },
    "Film": {
        "shortcuts": ["film", "movies"],
        "value": 11
    },
    "General": {
        "shortcuts": ["general"],
        "value": 9
    },
    "Any": {
        "shortcuts": ["any"],
        "value": 0
    }
}

RED_PIECE = "🔴"
X_PIECE = "❌"

ROBOT = "🤖"
QUIT = "❌"

REACT_100 = "💯"
REACT_UNO = ADD_4_CARD

# # # # # # # # # # # # # # # # # # # # # # # # #

RPS_ACTIONS = ["rock", "paper", "scissors"]

TRIVIA_API_CALL = "https://opentdb.com/api.php?amount={}&encode=base64&category={}"

# # # # # # # # # # # # # # # # # # # # # # # # #

class Game(commands.Cog, name = "game"):
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @commands.command(
        name = "gamestats",
        description = "Gets the stats of someone you specify, or yourself, of all mini-games in the bot.",
        cog_name = "game"
    )
    async def gamestats(self, ctx, *, member = None):

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
                ":skull_crossbones: Hangman": await database.users.get_hangman(member),
                ":cyclone: Scramble": await database.users.get_scramble(member),
                ":scissors: RPS": await database.users.get_rps(member),
                ":x: Tic Tac Toe": await database.users.get_tic_tac_toe(member),
                ":red_circle: Connect Four": await database.users.get_connect_four(member),
                "<:cah:540281486633336862> CAH": await database.users.get_cards_against_humanity(member),
                "<{}> Uno".format(ADD_4_CARD): await database.users.get_uno(member),
                ":question: Trivia": await database.users.get_trivia(member)
            }

            embed = discord.Embed(
                title = "Stats",
                description = "Game Stats for {}".format(member.mention),
                colour = await get_embed_color(ctx.author)
            )

            for stat in stats:
                won = stats[stat]["won"]
                lost = stats[stat]["lost"]

                embed.add_field(
                    name = "{} ({})".format(
                        stat, 
                        0 if won == 0 else (won if lost == 0 else round(won / lost, 2))
                    ),
                    value = "{}: {}\n{}: {}".format(
                        "Won" if stat.find("Trivia") == -1 else "Correct", won, 
                        "Lost" if stat.find("Trivia") == -1 else "Incorrect", lost
                    )
                )

            await ctx.send(
                embed = embed
            )

    @commands.command(
        name = "hangman",
        description = "Allows you to play a Hangman game.",
        cog_name = "game"
    )
    async def hangman(self, ctx):
    
        try: await ctx.message.delete()
        except: pass

        # Create hangman game
        game = Hangman(ctx.author)
        await game.generate_word()

        msg = await ctx.send(
            embed = discord.Embed(
                title = "Hangman",
                description = "Guesses: {}".format(
                    ", ".join(game.get_guessed()) if len(game.get_guessed()) > 0 else "No Guesses"
                ),
                colour = await get_embed_color(ctx.author)
            ).add_field(
                name = "_ _",
                value = game.get_hangman(),
                inline = False
            ).add_field(
                name = "_ _",
                value = game.get_hangman_word(),
                inline = False
            )
        )

        # Wait until loss or win
        count = 0 # Keep track of guesses made
                    # Delete old message and send new message as to keep it as low as possible
        while True:

            # Get guess
            def check_guess(message):
                return message.author.id == game.get_player().id and (len(message.content) == 1 or message.content.lower() == game.get_word())
            guess_message = await self.bot.wait_for("message", check = check_guess)
            guess = guess_message.content.lower()
            try: await guess_message.delete()
            except: pass

            # Make the guess
            guess = game.make_guess(guess)

            # Guess was the word
            if guess == Hangman.WORD:
                await msg.delete()
                await ctx.send(
                    embed = discord.Embed(
                        title = "Guessed",
                        description = "You guessed correctly! The word was {}\nIt took you {} guess{}!".format(
                            game.get_word(),
                            game.get_guesses(),
                            "es" if game.get_guesses() != 1 else ""
                        ),
                        colour = await get_embed_color(ctx.author)
                    ),
                    delete_after = 10
                )

                await database.users.update_hangman(game.get_player(), True)
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
                await msg.delete()
                await ctx.send(
                    embed = discord.Embed(
                        title = "Game Ended - Word: `{}`".format(game.get_word()),
                        description = "You did not guess the word quick enough.",
                        colour = await get_embed_color(ctx.author)
                    ).add_field(
                        name = "_ _",
                        value = game.get_hangman()
                    ),
                    delete_after = 10
                )

                await database.users.update_hangman(game.get_player(), False)
                break
            
            # Guess was a win
            elif guess == Hangman.WON:
                await msg.delete()
                await ctx.send(
                    embed = discord.Embed(
                        title = "Success!",
                        description = "The word was `{}`\nYou guessed in {} guess{}.".format(
                            game.get_word(),
                            game.get_guesses(),
                            "es" if len(game.get_guessed()) > 1 else ""
                        ),
                        colour = await get_embed_color(ctx.author)
                    ),
                    delete_after = 10
                )

                await database.users.update_hangman(game.get_player(), True)
                break
            
            # Guess was a correct/incorrect letter
            elif guess in [True, False]:
                count += 1
                if count % 5 == 0:
                    await msg.delete()
                    msg = await ctx.send(
                        embed = discord.Embed(
                            title = "Hangman",
                            description = "Guesses: {}".format(
                                ", ".join(game.get_guessed()) if len(game.get_guessed()) > 0 else "No Guesses"
                            ),
                            colour = await get_embed_color(ctx.author)
                        ).add_field(
                            name = "_ _",
                            value = game.get_hangman(),
                            inline = False
                        ).add_field(
                            name = "_ _",
                            value = game.get_hangman_word(),
                            inline = False
                        )
                    )
                
                else:
                    await msg.edit(
                        embed = discord.Embed(
                            title = "Hangman",
                            description = "Guesses: {}".format(
                                ", ".join(game.get_guessed()) if len(game.get_guessed()) > 0 else "No Guesses"
                            ),
                            colour = await get_embed_color(ctx.author)
                        ).add_field(
                            name = "_ _",
                            value = game.get_hangman(),
                            inline = False
                        ).add_field(
                            name = "_ _",
                            value = game.get_hangman_word(),
                            inline = False
                        )
                    )
    
    @commands.command(
        name = "scramble",
        description = "Allows you to play Scramble game.",
        cog_name = "game"
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
                    colour = await get_embed_color(ctx.author)
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
                            colour = await get_embed_color(ctx.author)
                        ),
                        delete_after = 5
                    )

                    await database.users.update_scramble(ctx.author, guess)

            except asyncio.TimeoutError:

                await msg.delete()
                await ctx.send(
                    embed = discord.Embed(
                        title = "Timed Out",
                        description = "Unfortunately, you did not guess the word in time.\nThe word was `{}`".format(
                            game.get_word()
                        ),
                        colour = await get_embed_color(ctx.author)
                    ),
                    delete_after = 5
                )

                await database.users.update_scramble(ctx.author, False)
    
    @commands.command(
        name = "rps",
        description = "Allows you to play Rock Paper Scissors.",
        cog_name = "game"
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
                await database.users.update_rps(ctx.author, True)
            
            elif (
                (bot_action == "rock" and user_action == "scissors") or 
                (bot_action == "paper" and user_action == "rock") or
                (bot_action == "scissors" and user_action == "paper")
            ):
                title = "You Lost!"
                await database.users.update_rps(ctx.author, True)
            
            embed = discord.Embed(
                title = title,
                description = result,
                colour = await get_embed_color(ctx.author)
            )

        await ctx.send(
            embed = embed,
            delete_after = 5
        )
    
    @commands.command(
        name = "trivia",
        aliases = ["triv"],
        description = "Allows you to play a trivia game where you can decide how many questions to answer (Max 30. Default 10).",
        cog_name = "game"
    )
    async def trivia(self, ctx, amount : int = 10):

        # Check if amount is greater than 30
        if amount > 30:
            await ctx.send(
                embed = errors.get_error_message(
                    "You can answer no more than 30 trivia questions."
                ),
                delete_after = 5
            )
        
        # Check if amount is less than 1
        elif amount < 1:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need to answer at least 1 trivia question."
                ),
                delete_after = 5
            )
        
        else:

            # Ask player which category they want
            shortcuts = []
            for category in TRIVIA_CATEGORIES:
                shortcuts += TRIVIA_CATEGORIES[category]["shortcuts"]

            embed = discord.Embed(
                title = "Choose a Category",
                description = "\n".join([
                    "{} (`{}`)".format(
                        category,
                        ", ".join(TRIVIA_CATEGORIES[category]["shortcuts"])
                    )
                    for category in TRIVIA_CATEGORIES
                ]),
                colour = await get_embed_color(ctx.author)
            )

            await ctx.send(
                embed = embed
            )

            # Wait for response
            def check_message(message):
                return ctx.author.id == message.author.id and message.channel.id == ctx.channel.id and (message.content.lower() in shortcuts or message.content.lower() in [category.lower() for category in list(TRIVIA_CATEGORIES.keys())])
            
            try:
                message = await self.bot.wait_for("message", check = check_message, timeout = 30)
                category = message.content.lower()
                try: await message.delete()
                except: pass

                # Player responded in time
                for target in TRIVIA_CATEGORIES:
                    if category in TRIVIA_CATEGORIES[target]["shortcuts"] or category == target.lower():
                        category = TRIVIA_CATEGORIES[target]["value"]
                        break
                
                # Call Trivia API
                response = await loop.run_in_executor(None,
                    requests.get,
                    TRIVIA_API_CALL.format(
                        amount,
                        category
                    )
                )
                response = response.json()

                # Turn each question into something readable
                questions = []
                for q in response["results"]:

                    # Decode question
                    question = base64.b64decode(q["question"].encode()).decode()

                    # Decode correct answer
                    correct_answer = base64.b64decode(q["correct_answer"].encode()).decode()

                    # Decode incorrect answers
                    incorrect_answers = []
                    for incorrect in q["incorrect_answers"]:
                        incorrect_answers.append(base64.b64decode(incorrect.encode()).decode())
                    
                    # Add all answers to single list and shuffle
                    answers = incorrect_answers + [correct_answer]
                    random.shuffle(answers)
                    correct = answers.index(correct_answer)

                    questions.append({
                        "question": question,
                        "answers": answers,
                        "correct": correct
                    })
                
                # Send initial message
                current = 0
                msg = await ctx.send(
                    embed = discord.Embed(
                        title = questions[current]["question"],
                        description = "\n".join([
                            "**{}.)** {}".format(
                                index + 1,
                                questions[current]["answers"][index]
                            )
                            for index in range(len(questions[current]["answers"]))
                        ]),
                        colour = await get_embed_color(ctx.author)
                    )
                )

                for index in range(len(questions[current]["answers"])):
                    await msg.add_reaction(TRIVIA_REACTIONS[index])
                await msg.add_reaction(QUIT)

                # Let player play until finished
                amt_correct = 0
                while True:
                    question = questions[current]
                    
                    # Wait for reaction
                    def check_reaction(reaction, user):
                        return reaction.message.id == msg.id and user.id == ctx.author.id and str(reaction) in TRIVIA_REACTIONS
                    
                    done, pending = await asyncio.wait([
                        self.bot.wait_for("reaction_add", check = check_reaction),
                        self.bot.wait_for("reaction_remove", check = check_reaction)
                    ], return_when = asyncio.FIRST_COMPLETED)
                    reaction, user = done.pop().result()

                    # Cancel all futures
                    for future in pending:
                        future.cancel()

                    # Reaction is quit
                    if str(reaction) == QUIT:
                        await msg.delete()
                        await ctx.send(
                            embed = discord.Embed(
                                title = "Game Quit",
                                description = "The game was successfully quit.",
                                colour = await get_embed_color(ctx.author)
                            ),
                            delete_after = 5
                        )
                        break
                    
                    # See if reaction was correct or incorrect
                    correct = TRIVIA_REACTIONS.index(str(reaction)) == question["correct"]
                    await msg.edit(
                        embed = discord.Embed(
                            title = "Incorrect." if not correct else "Correct!",
                            description = "Nope! The correct answer was *{}*.".format(
                                question["answers"][question["correct"]]
                            ) if not correct else "You got that one right!",
                            colour = 0x800000 if not correct else 0x008000
                        )
                    )

                    # Update user trivia score
                    await database.users.update_trivia(ctx.author, correct)
                    amt_correct += 1 if correct else 0
                    current += 1
                    if current < amount:
                        question = questions[current]

                    # Wait 3 seconds before going to next question
                    await asyncio.sleep(3)
                    if current >= amount:
                        await msg.delete()
                        break

                    # Update embed
                    await msg.edit(
                        embed = discord.Embed(
                            title = question["question"],
                            description = "\n".join([
                                "**{}.)** {}".format(
                                    index + 1,
                                    question["answers"][index]
                                )
                                for index in range(len(question["answers"]))
                            ]),
                            colour = await get_embed_color(ctx.author)
                        )
                    )
                
                # Game is over; Show how many questions user got right
                await ctx.send(
                    embed = discord.Embed(
                        title = "Results",
                        description = "You got {} correct ({}%)".format(
                            amt_correct,
                            round((amt_correct / amount) * 100, 2)
                        ),
                        colour = await get_embed_color(ctx.author)
                    ),
                    delete_after = 10
                )

            # Player took too long to choose a category
            except asyncio.TimeoutError:
                await ctx.send(
                    embed = errors.get_error_message(
                        "You took too long to choose a category."
                    ),
                    delete_after = 5
                )
    
    @commands.command(
        name = "ticTacToe", 
        aliases = ["ttt"],
        description = "Allows you to play a game of Tic Tac Toe with the AI or a person who reacts to it.",
        cog_name = "game"
    )
    async def tic_tac_toe(self, ctx, *, difficulty : str = None):

        # Ask if anyone specific is joining; Only if difficulty is not given
        if difficulty == None:
            msg = await ctx.send(
                embed = discord.Embed(
                    title = "Waiting for Player",
                    description = "If you're going to play against {}, react with {}.\n{}, if you're playing alone, react with {}.".format(
                        ctx.author.mention, X_PIECE,
                        ctx.author.mention, ROBOT
                    ),
                    colour = await get_embed_color(ctx.author)
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
                    colour = await get_embed_color(ctx.author)
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
                            await database.users.update_tic_tac_toe(game.get_challenger(), False)
                            await database.users.update_tic_tac_toe(game.get_opponent(), True)

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
                                    colour = await get_embed_color(ctx.author)
                                ),
                                delete_after = 5
                            )

                            break
                        
                        # There is a winner
                        elif result in [True, False]:

                            # Update wins/losses
                            await database.users.update_tic_tac_toe(game.get_challenger(), result)
                            if game.get_opponent() != None:
                                await database.users.update_tic_tac_toe(game.get_challenger(), not result)
                            
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
                                    colour = await get_embed_color(ctx.author)
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
                                    colour = await get_embed_color(ctx.author)
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
                    colour = await get_embed_color(ctx.author)
                ),
                delete_after = 5
            )
    
    @commands.command(
        name = "connectFour", 
        aliases = ["cf"],
        description = "Allows you to play a game of Connect Four with the AI or a person who reacts to it.",
        cog_name = "game"
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
                colour = await get_embed_color(ctx.author)
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
                    colour = await get_embed_color(ctx.author)
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
                            await database.users.update_connect_four(game.get_challenger(), False)
                            await database.users.update_connect_four(game.get_opponent(), True)

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
                                    colour = await get_embed_color(ctx.author)
                                ),
                                delete_after = 5
                            )

                            break
                        
                        # There is a winner
                        elif result in [True, False]:

                            # Update wins/losses
                            await database.users.update_connect_four(game.get_challenger(), result)
                            if game.get_opponent() != None:
                                await database.users.update_connect_four(game.get_challenger(), not result)
                            
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
                                    colour = await get_embed_color(ctx.author)
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
                                    colour = await get_embed_color(ctx.author)
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
                    colour = await get_embed_color(ctx.author)
                ),
                delete_after = 5
            )
    
    @commands.command(
        name = "uno",
        description = "Allows you to play a game of Uno with other people.",
        cog_name = "game"
    )
    @commands.check(guild_only)
    async def uno(self, ctx):

        # Wait for players (max of 5)
        players = [ctx.author]

        # Send join message
        msg = await ctx.send(
            embed = discord.Embed(
                title = "Join Uno!",
                description = "React with <{}> to join the game. {}, react with :robot: if you want to play against 4 other AIs\n**Players**\n{}".format(
                    REACT_UNO,
                    ctx.author.mention,
                    "\n".join([user.mention for user in players])
                ),
                colour = await get_embed_color(ctx.author)
            )
        )

        await msg.add_reaction(REACT_UNO)
        await msg.add_reaction(ROBOT)

        play_game = None
        against_ais = False
        while play_game == None:

            # Wait for player reactions
            def check(reaction, user):
                return (str(reaction) == "<{}>".format(REACT_UNO) and reaction.message.id == msg.id and user not in players and not user.bot) or (str(reaction) == ROBOT and user.id == ctx.author.id and not user.bot)
            
            # Try waiting
            try:
                reaction, user = await self.bot.wait_for("reaction_add", check = check, timeout = 30)

                # Check if the reaction is a robot reaction
                if str(reaction) == ROBOT:
                    play_game = True
                    against_ais = True
                    break

                players.append(user)

                await msg.edit(
                    embed = discord.Embed(
                        title = "Join Uno!",
                        description = "React with <{}> to join the game. {}, react with :robot: if you want to play against 4 other AIs\n**Players**\n{}".format(
                            REACT_UNO,
                            ctx.author.mention,
                            "\n".join([user.mention for user in players])
                        ),
                        colour = await get_embed_color(ctx.author)
                    )
                )

                # See if there are 5 players
                if len(players) == 5 or against_ais:
                    play_game = True
            
            # No one responded for 30 seconds
            except asyncio.TimeoutError:

                # Check if there are enough players
                play_game = len(players) >= 2
            
        # Check if game will be played
        if play_game:
            
            # Create the game
            game = Uno(players, ctx.channel, self.bot, against_ais = against_ais)
            game.give_cards()

            # Continue playing game until only 1 person left or someone wins

            while True:

                # Send cards to players
                await game.show_turn()

                # Wait for card response
                winner = await game.wait_for_card()

                # Check if game was ended
                if winner == Uno.END_GAME:
                    break

                # Check if winner exists; Update wins and losses
                if winner:

                    # Check if winner is not an AI
                    if winner.is_ai():
                        winner_mention = winner.get_player()
                        winner_user = ctx.author
                    else:
                        winner_mention = winner.get_player().mention
                        winner_user = winner.get_player()

                    # Send message to channel and all players
                    await ctx.channel.send(
                        embed = discord.Embed(
                            title = "Game Over!",
                            description = "{} won the game!".format(winner_mention),
                            colour = await get_embed_color(winner_user)
                        )
                    )
                    
                    for player in players:
                        await player.send(
                            embed = discord.Embed(
                                title = "You Won!" if player == winner.get_player() else "You Lost.",
                                description = "{} won the game.".format(
                                    winner_mention
                                ) if player != winner.get_player() else "_ _",
                                colour = await get_embed_color(winner_user)
                            )
                        )
                        if not winner.is_ai():
                            await database.users.update_uno(player, player == winner)
                
                    break
        
        # Game will not be played
        else:
            await msg.delete()
            await ctx.send(
                embed = discord.Embed(
                    title = "Not enough people :frowning2:",
                    description = "There needs to be at least 2 people to play Uno.",
                    colour = await get_embed_color(ctx.author)
                ),
                delete_after = 5
            )
    
    @commands.command(
        name = "cardsAgainstHumanity",
        aliases = ["cah"],
        description = "Allows you to play Cards Against Humanity with other people.",
        cog_name = "game"
    )
    @commands.check(is_nsfw_and_guild)
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
                colour = await get_embed_color(ctx.author)
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
                        colour = await get_embed_color(ctx.author)
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
            cah_cards = await database.data.get_cards_against_humanity_cards()
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
                        await database.users.update_cards_against_humanity(player.get_player(), player.get_wins() >= 7)
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
                            colour = await get_embed_color(ctx.author)
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
                    colour = await get_embed_color(ctx.author)
                ),
                delete_after = 5
            )
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @commands.command(
        name = "addHangman",
        description = "Allows you to add a custom hangman phrase.",
        cog_name = "game"
    )
    async def add_hangman(self, ctx, *, phrase = None):

        # Check if phrase is None; Send error
        if phrase == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You can't add an empty phrase."
                )
            )
        
        # Phrase is not None; Add it, notify all developers, notify author
        else:

            # Add to pending hangman
            await database.data.add_pending_hangman(phrase, str(ctx.author.id))

            # Notify all developers
            for dev in await database.bot.get_developers():

                # Get dev user object
                user = self.bot.get_user(int(dev))

                # Only send if user is found
                if user != None:
                    await user.send(
                        embed = discord.Embed(
                            title = "New Pending Hangman Phrase",
                            description = " ",
                            colour = await get_embed_color(ctx.author)
                        ).add_field(
                            name = "Author",
                            value = "{} ({})".format(
                                ctx.author.mention, ctx.author
                            ),
                            inline = False
                        ).add_field(
                            name = "Phrase",
                            value = phrase,
                            inline = False
                        )
                    )
            
            # Notify author
            await ctx.send(
                embed = discord.Embed(
                    title = "Phrase Pending!",
                    description = "Your phrase was added to be reviewed by an Omega Psi developer.\nYou will be notified if it is denied or approved.",
                    colour = await get_embed_color(ctx.author)
                )
            )

            # Send the bug to the discord channel dedicated to hangman phrases
            await send_webhook(
                os.environ["HANGMAN_WEBHOOK"],
                discord.Embed(
                    title = "Hangman Phrase Suggested",
                    description = " ",
                    colour = await get_embed_color(ctx.author)
                ).add_field(
                    name = "User",
                    value = ctx.author
                ).add_field(
                    name = "Origin",
                    value = ("Server: " + ctx.guild.name) if ctx.guild != None else "Private Message"
                ).add_field(
                    name = "Phrase",
                    value = phrase
                ).set_thumbnail(
                    url = ctx.author.avatar_url
                )
            )
    
    @commands.command(
        name = "pendingHangman",
        aliases = ["pendingH", "pendHangman", "pendH"],
        description = "Allows you to see the pending hangman phrases.",
        cog_name = "game"
    )
    @commands.check(is_developer)
    async def pending_hangman(self, ctx):

        # Get list of pending hangman
        pending_hangmans = await database.data.get_pending_hangman()
        
        # Check if there are any pending hangmans
        if len(pending_hangmans) > 0:

            # Create Embed
            current = 0
            author = self.bot.get_user(int(pending_hangmans[current]["author"]))
            embed = discord.Embed(
                title = "Pending Hangman Phrases {}".format(
                    "({} / {})".format(
                        current + 1, len(pending_hangmans)
                    ) if len(pending_hangmans) > 1 else ""
                ),
                description = "**Phrase**: {}\n**Author**: {}".format(
                    pending_hangmans[current]["phrase"],
                    "Unknown" if author == None else "{} ({})".format(
                        author.mention, author
                    )
                ),
                colour = await get_embed_color(ctx.author)
            )

            msg = await ctx.send(
                embed = embed
            )

            await add_scroll_reactions(msg, pending_hangmans)

            while True:

                def check_reaction(reaction, user):
                    return reaction.message.id == msg.id and ctx.author.id == user.id and str(reaction) in SCROLL_REACTIONS
                
                done, pending = await asyncio.wait([
                    self.bot.wait_for("reaction_add", check = check_reaction),
                    self.bot.wait_for("reaction_remove", check = check_reaction)
                ], return_when = asyncio.FIRST_COMPLETED)
                reaction, user = done.pop().result()

                # Cancel all futures
                for future in pending:
                    future.cancel()
                
                # Reaction is first page
                if str(reaction) == FIRST_PAGE:
                    current = 0

                # Reaction is last page
                elif str(reaction) == LAST_PAGE:
                    current = len(pending_hangmans) - 1

                # Reaction is previous page
                elif str(reaction) == PREVIOUS_PAGE:
                    current -= 1
                    if current < 0:
                        current = 0

                # Reaction is next page
                elif str(reaction) == NEXT_PAGE:
                    current += 1
                    if current > len(pending_hangmans) - 1:
                        current = len(pending_hangmans) - 1

                # Reaction is leave
                elif str(reaction) == LEAVE:
                    await msg.delete()
                    break

                # Update embed
                author = self.bot.get_user(int(pending_hangmans[current]["author"]))
                embed = discord.Embed(
                    title = "Pending Hangmans {}".format(
                        "({} / {})".format(
                            current + 1, len(pending_hangmans)
                        ) if len(pending_hangmans) > 1 else ""
                    ),
                    description = "**Phrase (#{})**: {}\n**Author**: {}".format(
                        pending_hangmans[current]["number"],
                        pending_hangmans[current]["phrase"],
                        "Unknown" if author == None else "{} ({})".format(
                            author.mention, author
                        )
                    ),
                    colour = await get_embed_color(ctx.author)
                )

                await msg.edit(
                    embed = embed
                )

        # There are no pending insutls
        else:

            await ctx.send(
                embed = discord.Embed(
                    title = "No Pending Hangman Phrases",
                    description = "There aren't currently any pending hangman phrases to review.",
                    colour = await get_embed_color(ctx.author)
                )
            )

    @commands.command(
        name = "approveHangman",
        aliases = ["approveH"],
        description = "Allows you to approve a pending hangman phrase.",
        cog_name = "game"
    )
    @commands.check(is_developer)
    async def approve_hangman(self, ctx, index : int):

        # Get list of pending hangmans
        pending_hangmans = await database.data.get_pending_hangman()

        # Check if index is in range of pending hangmans
        index -= 1
        if index >= 0 and index < len(pending_hangmans):

            # Approve the hangman phrase and let the author know
            author = self.bot.get_user(int(pending_hangmans[index]["author"]))

            embed = discord.Embed(
                title = "Hangman Phrase Approved!",
                description = "Phrase: *{}*".format(
                    pending_hangmans[index]["phrase"]
                ),
                colour = await get_embed_color(ctx.author)
            )

            # Only send message if author was found
            await database.data.approve_pending_hangman(index)
            if author != None:

                # Try sending author a message
                try:
                    await author.send(
                        embed = embed
                    )
                except:

                    # Send the person an email if it can
                    sent_email = False
                    if "email" in pending_hangmans[index]:

                        try:
                            await loop.run_in_executor(None,
                                send_email,
                                pending_hangmans[index]["email"],
                                "Hangman Phrase".format(index),
                                "Your hangman phrase was approved.\n{}".format(
                                    pending_hangmans[index]["phrase"]
                                ),
                                "<p>Your hangman phrase was approved.</p><br><em>{}</em>".format(
                                    pending_hangmans[index]["phrase"]
                                )
                            )
                            sent_email = True
                        except:
                            pass

                    await ctx.send(
                        embed = discord.Embed(
                            title = "Could Not Send Message",
                            description = "I tried sending the message to the suggestor but they didn't allow me to send the message.\n{}".format(
                                "I could not send them an email either." if not sent_email else "I did send them an email instead."
                            ),
                            colour = 0x800000
                        ),
                        delete_after = 10
                    )
            
            # Let dev know
            await ctx.send(
                embed = embed
            )
        
        # Index is out of range`
        else:
            await ctx.send(
                embed = errors.get_error_message(
                    "The index you gave is out of range."
                )
            )
    
    @commands.command(
        name = "denyHangman",
        aliases = ["denyH"],
        description = "Allows you to deny a pending hangman phrase.",
        cog_name = "game"
    )
    @commands.check(is_developer)
    async def deny_hangman(self, ctx, index : int, *, reason = None):
        
        # Get list of pending hangmans
        pending_hangmans = await database.data.get_pending_hangman()

         # Check if index is in range of pending hangmans
        index -= 1
        if index >= 0 and index < len(pending_hangmans):
            
            # Deny the phrase and tell the author why
            author = self.bot.get_user(int(pending_hangmans[index]["author"]))

            embed = discord.Embed(
                title = "Hangman Phrase Denied.",
                description = "Phrase: *{}*\n\nReason: *{}*".format(
                    pending_hangmans[index]["phrase"],
                    reason if reason != None else "No Reason Provided. DM a developer for the reason."
                ),
                colour = await get_embed_color(ctx.author)
            )

            # Only send message if author was found
            await database.data.deny_pending_hangman(index)
            if author != None:
                
                # Try sending author a message
                try:
                    await author.send(
                        embed = embed
                    )
                except:

                    # Send the person an email if it can
                    sent_email = False
                    if "email" in pending_hangmans[index]:

                        try:
                            await loop.run_in_executor(None,
                                send_email,
                                pending_hangmans[index]["email"],
                                "Hangman Phrase".format(index),
                                "Your hangman phrase was denied.\n{}\nReason: {}".format(
                                    pending_hangmans[index]["phrase"],
                                    reason
                                ),
                                "<p>Your hangman phrase was approved.</p><br><em>{}</em><br><strong>Reason</strong>: <em>{}</em>".format(
                                    pending_hangmans[index]["phrase"],
                                    reason
                                )
                            )
                            sent_email = True
                        except:
                            pass

                    await ctx.send(
                        embed = discord.Embed(
                            title = "Could Not Send Message",
                            description = "I tried sending the message to the suggestor but they didn't allow me to send the message.\n{}".format(
                                "I could not send them an email either." if not sent_email else "I did send them an email instead."
                            ),
                            colour = 0x800000
                        ),
                        delete_after = 10
                    )
            
            await ctx.send(
                embed = embed
            )
        
        # Index is out of range`
        else:
            await ctx.send(
                embed = errors.get_error_message(
                    "The index you gave is out of range."
                )
            )
    
    @commands.command(
        name = "addScramble",
        description = "Allows you to add a custom scramble phrase.",
        cog_name = "game"
    )
    async def add_scramble(self, ctx, *, phrase = None):

        # Check if phrase is None; Send error
        if phrase == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You can't add an empty phrase."
                )
            )
        
        # Phrase is not None; Add it, notify all developers, notify author
        else:

            # Add to pending scramble
            await database.data.add_pending_scramble(phrase, str(ctx.author.id))

            # Notify all developers
            for dev in await database.bot.get_developers():

                # Get dev user object
                user = self.bot.get_user(int(dev))

                # Only send if user is found
                if user != None:
                    await user.send(
                        embed = discord.Embed(
                            title = "New Pending Scramble Phrase",
                            description = " ",
                            colour = await get_embed_color(ctx.author)
                        ).add_field(
                            name = "Author",
                            value = "{} ({})".format(
                                ctx.author.mention, ctx.author
                            ),
                            inline = False
                        ).add_field(
                            name = "Phrase",
                            value = phrase,
                            inline = False
                        )
                    )
            
            # Notify author
            await ctx.send(
                embed = discord.Embed(
                    title = "Phrase Pending!",
                    description = "Your phrase was added to be reviewed by an Omega Psi developer.\nYou will be notified if it is denied or approved.",
                    colour = await get_embed_color(ctx.author)
                )
            )

            # Send the bug to the discord channel dedicated to scramble
            await send_webhook(
                os.environ["SCRAMBLE_WEBHOOK"],
                discord.Embed(
                    title = "Scramble Phrase Suggested",
                    description = " ",
                    colour = await get_embed_color(ctx.author)
                ).add_field(
                    name = "User",
                    value = ctx.author
                ).add_field(
                    name = "Origin",
                    value = ("Server: " + ctx.guild.name) if ctx.guild != None else "Private Message"
                ).add_field(
                    name = "Phrase",
                    value = phrase
                ).set_thumbnail(
                    url = ctx.author.avatar_url
                )
            )
    
    @commands.command(
        name = "pendingScramble",
        aliases = ["pendingS", "pendScramble", "pendS"],
        description = "Allows you to see the pending scramble phrases.",
        cog_name = "game"
    )
    @commands.check(is_developer)
    async def pending_scramble(self, ctx):

        # Get list of pending scramble
        pending_scrambles = await database.data.get_pending_scramble()
        
        # Check if there are any pending scrambles
        if len(pending_scrambles) > 0:

            # Create Embed
            current = 0
            author = self.bot.get_user(int(pending_scrambles[current]["author"]))
            embed = discord.Embed(
                title = "Pending Scramble Phrases {}".format(
                    "({} / {})".format(
                        current + 1, len(pending_scrambles)
                    ) if len(pending_scrambles) > 1 else ""
                ),
                description = "**Phrase**: {}\n**Author**: {}\n**Hints**: `{}`".format(
                    pending_scrambles[current]["phrase"],
                    "Unknown" if author == None else "{} ({})".format(
                        author.mention, author
                    ),
                    ", ".join(pending_scrambles[current]["hints"]) if len(pending_scrambles[current]["hints"]) > 0 else "None"
                ),
                colour = await get_embed_color(ctx.author)
            )

            msg = await ctx.send(
                embed = embed
            )

            await add_scroll_reactions(msg, pending_scrambles)

            while True:

                def check_reaction(reaction, user):
                    return reaction.message.id == msg.id and ctx.author.id == user.id and str(reaction) in SCROLL_REACTIONS
                
                done, pending = await asyncio.wait([
                    self.bot.wait_for("reaction_add", check = check_reaction),
                    self.bot.wait_for("reaction_remove", check = check_reaction)
                ], return_when = asyncio.FIRST_COMPLETED)
                reaction, user = done.pop().result()

                # Cancel all futures
                for future in pending:
                    future.cancel()
                
                # Reaction is first page
                if str(reaction) == FIRST_PAGE:
                    current = 0

                # Reaction is last page
                elif str(reaction) == LAST_PAGE:
                    current = len(pending_scrambles) - 1

                # Reaction is previous page
                elif str(reaction) == PREVIOUS_PAGE:
                    current -= 1
                    if current < 0:
                        current = 0

                # Reaction is next page
                elif str(reaction) == NEXT_PAGE:
                    current += 1
                    if current > len(pending_scrambles) - 1:
                        current = len(pending_scrambles) - 1

                # Reaction is leave
                elif str(reaction) == LEAVE:
                    await msg.delete()
                    break

                # Update embed
                author = self.bot.get_user(int(pending_scrambles[current]["author"]))
                embed = discord.Embed(
                    title = "Pending Scrambles {}".format(
                        "({} / {})".format(
                            current + 1, len(pending_scrambles)
                        ) if len(pending_scrambles) > 1 else ""
                    ),
                    description = "**Phrase**: {}\n**Author**: {}\n**Hints**: `{}`".format(
                        pending_scrambles[current]["phrase"],
                        "Unknown" if author == None else "{} ({})".format(
                            author.mention, author
                        ),
                        ", ".join(pending_scrambles[current]["hints"]) if len(pending_scrambles[current]["hints"]) > 0 else "None"
                    ),
                    colour = await get_embed_color(ctx.author)
                )

                await msg.edit(
                    embed = embed
                )

        # There are no pending insutls
        else:

            await ctx.send(
                embed = discord.Embed(
                    title = "No Pending Scramble Phrases",
                    description = "There aren't currently any pending scramble phrases to review.",
                    colour = await get_embed_color(ctx.author)
                )
            )
    
    @commands.command(
        name = "addScrambleHint",
        aliases = ["addSHint"],
        description = "Allows you to add a hint for a scramble phrase.",
        cog_name = "game"
    )
    @commands.check(is_developer)
    async def add_scramble_hint(self, ctx, index : int, *hints):

        # Get list of pending scramble
        pending_scrambles = await database.data.get_pending_scramble()

        # Check if index is in range of list
        index -= 1
        hints = list(hints)
        if index >= 0 and index < len(pending_scrambles):

            # Add the tags to the insult
            await database.data.add_pending_scramble_hints(index, hints)

            await ctx.send(
                embed = discord.Embed(
                    title = "Hints Added" if len(hints) > 1 else "Hint Added",
                    description = "The following hint{} been added: `{}`".format(
                        "s have" if len(hints) > 1 else " has",
                        ", ".join(hints)
                    ),
                    colour = await get_embed_color(ctx.author)
                )
            )
        
        # Index is out of range
        else:
            await ctx.send(
                embed = errors.get_error_message(
                    "The index you gave is out of range."
                )
            )

    @commands.command(
        name = "approveScramble",
        aliases = ["approveS"],
        description = "Allows you to approve a pending scramble phrase.",
        cog_name = "game"
    )
    @commands.check(is_developer)
    async def approve_scramble(self, ctx, index : int):

        # Get list of pending scrambles
        pending_scrambles = await database.data.get_pending_scramble()

        # Check if index is in range of pending scrambles
        index -= 1
        if index >= 0 and index < len(pending_scrambles):

            # Approve the scramble phrase and let the author know
            author = self.bot.get_user(int(pending_scrambles[index]["author"]))

            embed = discord.Embed(
                title = "Scramble Phrase Approved!",
                description = "Phrase: *{}*\n{}".format(
                    pending_scrambles[index]["phrase"],
                    "These hints were given to the phrase: `{}`".format(
                        ", ".join(pending_scrambles[index]["hints"])
                    ) if len(pending_scrambles[index]["hints"]) > 0 else ""
                ),
                colour = await get_embed_color(ctx.author)
            )

            # Only send message if author was found
            await database.data.approve_pending_scramble(index)
            if author != None:
                
                # Try sending author a message
                try:
                    await author.send(
                        embed = embed
                    )
                except:

                    # Send the person an email if it can
                    sent_email = False
                    if "email" in pending_scrambles[index]:

                        try:
                            await loop.run_in_executor(None,
                                send_email,
                                pending_scrambles[index]["email"],
                                "Scramble Phrase".format(index),
                                "Your scramble phrase was approved.\n{}\n{}".format(
                                    pending_scrambles[index]["phrase"],
                                    "These hints were given to the phrase: {}".format(
                                        ", ".join(pending_scrambles[index]["hints"])
                                    ) if len(pending_scrambles[index]["hints"]) > 0 else ""
                                ),
                                "<p>Your scramble phrase was approved.</p><br><em>{}</em><br>{}".format(
                                    pending_scrambles[index]["phrase"],
                                    "<strong>These hints were given to the phrase</strong>: <em>{}</em>".format(
                                        ", ".join(pending_scrambles[index]["hints"])
                                    ) if len(pending_scrambles[index]["hints"]) > 0 else ""
                                )
                            )
                            sent_email = True
                        except:
                            pass

                    await ctx.send(
                        embed = discord.Embed(
                            title = "Could Not Send Message",
                            description = "I tried sending the message to the suggestor but they didn't allow me to send the message.\n{}".format(
                                "I could not send them an email either." if not sent_email else "I did send them an email instead."
                            ),
                            colour = 0x800000
                        ),
                        delete_after = 10
                    )
            
            # Let dev know
            await ctx.send(
                embed = embed
            )
        
        # Index is out of range`
        else:
            await ctx.send(
                embed = errors.get_error_message(
                    "The index you gave is out of range."
                )
            )
    
    @commands.command(
        name = "denyScramble",
        aliases = ["denyS"],
        description = "Allows you to deny a pending scramble phrase.",
        cog_name = "game"
    )
    @commands.check(is_developer)
    async def deny_scramble(self, ctx, index : int, *, reason = None):
        
        # Get list of pending scrambles
        pending_scrambles = await database.data.get_pending_scramble()

         # Check if index is in range of pending scrambles
        index -= 1
        if index >= 0 and index < len(pending_scrambles):
            
            # Deny the phrase and tell the author why
            author = self.bot.get_user(int(pending_scrambles[index]["author"]))

            embed = discord.Embed(
                title = "Scramble Phrase Denied.",
                description = "Phrase: *{}*\n\nReason: *{}*".format(
                    pending_scrambles[index]["phrase"],
                    reason if reason != None else "No Reason Provided. DM a developer for the reason."
                ),
                colour = await get_embed_color(ctx.author)
            )

            # Only send message if author was found
            await database.data.deny_pending_scramble(index)
            if author != None:
                
                # Try sending author a message
                try:
                    await author.send(
                        embed = embed
                    )
                except:

                    # Send the person an email if it can
                    sent_email = False
                    if "email" in pending_scrambles[index]:

                        try:
                            await loop.run_in_executor(None,
                                send_email,
                                pending_scrambles[index]["email"],
                                "Scramble Phrase".format(index),
                                "Your scramble phrase was denied.\n{}\nReason: {}".format(
                                    pending_scrambles[index]["phrase"],
                                    reason
                                ),
                                "<p>Your scramble phrase was denied.</p><br><em>{}</em><br><strong>Reason</strong>: <em>{}</em>".format(
                                    pending_scrambles[index]["phrase"],
                                    reason
                                )
                            )
                            sent_email = True
                        except:
                            pass

                    await ctx.send(
                        embed = discord.Embed(
                            title = "Could Not Send Message",
                            description = "I tried sending the message to the suggestor but they didn't allow me to send the message.\n{}".format(
                                "I could not send them an email either." if not sent_email else "I did send them an email instead."
                            ),
                            colour = 0x800000
                        ),
                        delete_after = 10
                    )
            
            await ctx.send(
                embed = embed
            )
        
        # Index is out of range`
        else:
            await ctx.send(
                embed = errors.get_error_message(
                    "The index you gave is out of range."
                )
            )
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @pending_hangman.error
    @pending_scramble.error
    @approve_hangman.error
    @approve_scramble.error
    @deny_hangman.error
    @deny_scramble.error
    async def developer_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(
                embed = errors.get_error_message(
                    "You can't run this command."
                )
            )
    
    @uno.error
    async def guild_only_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(
                embed = errors.get_error_message(
                    "This command can only be run in guilds. Not in DMs."
                )
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
    
def setup(bot):
    bot.add_cog(Game(bot))