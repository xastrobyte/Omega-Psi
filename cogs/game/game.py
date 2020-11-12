from asyncio import TimeoutError
from discord import Embed, Member
from discord.ext.commands import Cog, command

from cogs.errors import MEMBER_NOT_FOUND_ERROR
from cogs.globals import JOIN, ROBOT, SMART, RANDOM, PLAY_NOW
from cogs.predicates import is_nsfw_and_guild

from cogs.game.minigames.battleship.game import BattleshipGame
from cogs.game.minigames.cards_against_humanity.game import CardsAgainstHumanityGame
from cogs.game.minigames.chess.game import ChessGame
from cogs.game.minigames.connect_four.game import ConnectFourGame
from cogs.game.minigames.game_of_life.game import GameOfLifeGame
from cogs.game.minigames.kings_cup.game import KingsCupGame
from cogs.game.minigames.mastermind.game import MastermindGame
from cogs.game.minigames.omok.game import OmokGame
from cogs.game.minigames.tic_tac_toe.game import TicTacToeGame
from cogs.game.minigames.uno.game import UnoGame

from util.database.database import database
from util.functions import get_embed_color


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def check_reaction_smart_random(ctx, message, reaction, user):
    """Determines if the given reaction and given user can react to a message
    to choose either a smart AI or a random AI

    :param ctx: The context of where the reaction is taking place
    :param message: The message that the reaction should be taking place at
    :param reaction: The given reaction
    :param user: The user who reacted
    """
    return (
                   (str(reaction) == SMART or str(reaction) == RANDOM) and
                   user.id == ctx.author.id
           ) and message.id == reaction.message.id


def check_reaction_opponent(ctx, message, reaction, user):
    """Determines if the given reaction and given user can react to a message
    when wanting to play against an AI or having other opponents play against them

    :param ctx: The context of where the reaction is taking place
    :param message: The message that the reaction should be taking place at
    :param reaction: The given reaction
    :param user: The user who reacted
    """
    return (
                   (str(reaction) == JOIN and user.id != ctx.author.id and not user.bot) or
                   (str(reaction) in [ROBOT, PLAY_NOW] and user.id == ctx.author.id)
           ) and message.id == reaction.message.id


class Game(Cog, name="game"):
    """There are minigames here you can play!"""

    def __init__(self, bot):
        self.bot = bot

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @command(
        name="gamestats",
        description="Shows you the stats of someone you specify, or yourself, of all the mini-games in Omega Psi.",
        cog_name="game"
    )
    async def gamestats(self, ctx, *, member=None):
        """Allows a user to show gamestats for themselves or someone they specify

        :param ctx: The context of where the message was sent
        :param member: The member to get the gamestats for
        """

        # Member is None or in private message; Get self
        if not member or not ctx.guild:
            member = ctx.author

        # Member is not None; find the member
        else:

            # Check if the member is not of type discord.Member
            if not isinstance(member, Member):

                # Look for the member in the guild
                found = False
                members = ctx.guild.members
                for _member in members:
                    if member.lower() == _member.name.lower():
                        member = _member
                        found = True
                        break

                if not found:
                    member = None
                    embed = MEMBER_NOT_FOUND_ERROR

        # Get the member data if they were found
        if member:
            minigame_data = await database.users.get_minigame_data(member)
            stats = {
                minigame.replace("_", " ").title(): minigame_data[minigame]
                for minigame in minigame_data
            }

            embed = Embed(
                title="Stats",
                description="Game Stats for {}".format(member.mention),
                colour=await get_embed_color(ctx.author)
            )

            for stat in stats:

                # Get the ratio of wins/losses as long as there is at least 1 loss
                #   if there are no losses, the ratio is just the wins
                if stats[stat]:
                    if stats[stat]["lost"] != 0:
                        ratio = stats[stat]["won"] / stats[stat]["lost"]
                    else:
                        ratio = stats[stat]["won"]

                # Add the game stat as a field to the embed
                embed.add_field(
                    name=stat,
                    value="```md\n{}\n```".format(
                        "  [Won][{}]\n [Lost][{}]\n[Ratio][{}]".format(
                            stats[stat]["won"], stats[stat]["lost"], round(ratio, 2)
                        ) if stats[stat] else "# No Stats Yet"
                    )
                )

        await ctx.send(embed=embed)

    @command(
        name="battleship",
        description="Play a game of Battleship against an AI or against another person",
        cog_name="game"
    )
    async def battleship(self, ctx):
        """Allows a user to play a game of Battleship

        :param ctx: The context of where the message was sent
        """

        # Wait for other players
        result = await self.wait_for_users(ctx, "Waiting for a Battleship opponent",
                                           is_two_player=True,
                                           timeout=30
                                           )

        # The result is not None, it must be either a user or
        #   the SMART/RANDOM reaction
        if result is not None:
            game = BattleshipGame(
                self.bot, ctx,
                ctx.author,
                1 if result in [SMART, RANDOM] else result,
                is_smart=result == SMART
            )
            await game.play()

        # The result is None, no one wanted to play the game
        else:
            await ctx.send(
                embed=Embed(
                    title="No responses :frowning2:",
                    description="It seems like no one wanted to play with you.",
                    colour=await get_embed_color(ctx.author)
                )
            )

    @command(
        name="cardsAgainstHumanity",
        aliases=["cah"],
        description="Play a game of Cards Against Humanity with at least 2 other players.",
        cog_name="game"
    )
    @is_nsfw_and_guild()
    async def cards_against_humanity(self, ctx):
        """Allows a user to play a game of Cards Against Humanity

        :param ctx: The context of where the message was sent
        """

        # Wait for other players
        result = await self.wait_for_users(ctx, "Waiting for Cards Against Humanity opponents",
                                           is_two_player=False,
                                           allow_ai=False,
                                           timeout=30,
                                           min_players=3
                                           )

        # The result is not None, there are players
        if result is not None:

            # Check if there were not enough players
            if not result:
                await ctx.send(
                    embed=Embed(
                        title="There weren't enough players :frowning:",
                        description="To play Cards Against Humanity, you need at least 3 players.",
                        colour=await get_embed_color(ctx.author)
                    )
                )

            # There were enough players
            else:
                game = CardsAgainstHumanityGame(self.bot, ctx, result)
                await game.play()

        # The result is None, no one wanted to play the game
        else:
            await ctx.send(
                embed=Embed(
                    title="No responses :frowning2:",
                    description="It seems like no on wanted to play with you.",
                    colour=await get_embed_color(ctx.author)
                )
            )
    
    @command(
        name="chess",
        description="Play a game of Chess against an opponent or an AI",
        cog_name="game"
    )
    async def chess(self, ctx, *, fen_string=None):
        """Allows a user to play a game of Chess

        :param ctx: The context of where the message was sent
        """

        # Wait for other players
        result = await self.wait_for_users(
            ctx, "Waiting for a Chess opponent",
            is_two_player = True,
            allow_intelligent_ai = False,
            timeout = 30
        )

        # The result is not None, it must either be a user or
        #   the SMART/RANDOM reaction
        if result is not None:
            game = ChessGame(
                self.bot, ctx,
                ctx.author,
                1 if result == RANDOM else result,
                is_smart = result == SMART,
                fen_string = fen_string
            )
            await game.play()
        
        # The result is None, no one wanted to play the game
        else:
            await ctx.send(
                embed=Embed(
                    title="No responses :frowning2:",
                    description="It seems like no one wanted to play with you.",
                    colour=await get_embed_color(ctx.author)
                )
            )


    @command(
        name="connectFour",
        aliases=["cf", "c4"],
        description="Play a game of Connect Four against an opponent or an AI",
        cog_name="game"
    )
    async def connect_four(self, ctx):
        """Allows a user to play a game of Connect Four

        :param ctx: The context of where the message was sent
        """

        # Wait for other players
        result = await self.wait_for_users(ctx, "Waiting for a Connect Four opponent",
                                           is_two_player=True,
                                           timeout=30
                                           )

        # The result is not None, it must be either a user or
        #   the SMART/RANDOM reaction
        if result is not None:
            game = ConnectFourGame(
                self.bot, ctx,
                ctx.author,
                1 if result in [SMART, RANDOM] else result,
                is_smart=result == SMART
            )
            await game.play()

        # The result is None, no one wanted to play the game
        else:
            await ctx.send(
                embed=Embed(
                    title="No responses :frowning2:",
                    description="It seems like no one wanted to play with you.",
                    colour=await get_embed_color(ctx.author)
                )
            )

    @command(
        name="gameOfLife",
        aliases=["gol"],
        description="Play the Game of Life against up to 4 opponents, real people or AIs",
        cog_name="game"
    )
    async def game_of_life(self, ctx):
        """Allows a user to play the Game of Life

        :param ctx: The context of where the message was sent
        """

        # Wait for other players
        result = await self.wait_for_users(ctx, "Waiting for Game of Life opponents",
                                           allow_intelligent_ai=False,
                                           timeout=30
                                           )

        # The result is not None, it must be either a list of users or
        #   the ROBOT reaction
        if result is not None:
            game = GameOfLifeGame(self.bot, ctx, result)
            await game.play()

        # The result is None, no one wanted to play the game
        else:
            await ctx.send(
                embed=Embed(
                    title="No responses :frowning2:",
                    description="It seems like no one wanted to play with you.",
                    colour=await get_embed_color(ctx.author)
                )
            )

    @command(
        name="mastermind",
        aliases=["codeBreaker", "codeBreak"],
        description="Play a game of Mastermind",
        cog_name="game"
    )
    async def mastermind(self, ctx):
        """Allows a user to play a game of Mastermind

        :param ctx: The context of where the message was sent
        """
        await MastermindGame(self.bot, ctx, ctx.author).play()

    @command(
        name="omok",
        aliases=["gomoku", "go"],
        description="Play a game of Omok against an opponent or an AI",
        cog_name="game"
    )
    async def omok(self, ctx):
        """Allows a user to play a game of Omok

        :param ctx: The context of where the message was sent
        """

        # Wait for other players
        result = await self.wait_for_users(ctx, "Waiting for an Omok opponent",
                                           is_two_player=True,
                                           timeout=30
                                           )

        # The result is not None, it must be either a user or
        #   the SMART/RANDOM reaction
        if result is not None:
            game = OmokGame(
                self.bot, ctx, ctx.author,
                1 if result in [SMART, RANDOM] else result,
                is_smart=result == SMART
            )
            await game.play()

        # The result is None, no one wanted to play the game
        else:
            await ctx.send(
                embed=Embed(
                    title="No responses :frowning2:",
                    description="It seems like no one wanted to play with you.",
                    colour=await get_embed_color(ctx.author)
                )
            )

    @command(
        name="ticTacToe",
        aliases=["ttt"],
        description="Play a game of Tic Tac Toe against an opponent or an AI",
        cog_name="game"
    )
    async def tic_tac_toe(self, ctx):
        """Allows a user to play a game of Tic Tac Toe

        :param ctx: The context of where the message was sent
        """

        # Wait for other players
        result = await self.wait_for_users(ctx, "Waiting for a Tic Tac Toe opponent",
                                           is_two_player=True,
                                           timeout=30
                                           )

        # The result is not None, it must be either a user or
        #   the SMART/RANDOM reaction
        if result is not None:
            game = TicTacToeGame(
                self.bot, ctx, ctx.author,
                1 if result in [SMART, RANDOM] else result,
                is_smart=result == SMART
            )
            await game.play()

        # The result is None, no one wanted to play the game
        else:
            await ctx.send(
                embed=Embed(
                    title="No responses :frowning2:",
                    description="It seems like no one wanted to play with you.",
                    colour=await get_embed_color(ctx.author)
                )
            )

    @command(
        name="uno",
        description="Play a game of Uno against up to 4 opponents, real people or AIs",
        cog_name="game"
    )
    async def uno(self, ctx):
        """Allows a user to play a game of Uno

        :param ctx: The context of where the message was sent
        """

        # Wait for other players
        result = await self.wait_for_users(ctx, "Waiting for Uno opponents",
                                           allow_intelligent_ai=False,
                                           timeout=30
                                           )

        # The result is not None, it must be either a user or a ROBOT reaction
        if result is not None:
            game = UnoGame(self.bot, ctx, result)
            await game.play()

        # The result is None, no one wanted to play the game
        else:
            await ctx.send(
                embed=Embed(
                    title="No responses :frowning2:",
                    description="It seems like no one wanted to play with you.",
                    colour=await get_embed_color(ctx.author)
                )
            )

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @command(
        name="kingsCup",
        description="Play a drinking game of Kings Cup",
        cog_name="game"
    )
    # @is_in_guild(521185038969208850, 450208093524066317)
    @is_nsfw_and_guild()
    async def kings_cup(self, ctx):
        """Allows a user to play a drinking game of Kings Cup with friends

        :param ctx: The context of where the message was sent
        """

        # Wait for other players
        result = await self.wait_for_users(ctx, "Waiting for Kings Cup players",
                                           allow_ai=False,
                                           timeout=30
                                           )

        # The result is not None, it must be users
        if result is not None:
            game = KingsCupGame(self.bot, ctx, result)
            await game.play()

        # The result is None, no on wanted to play the game
        else:
            await ctx.send(
                embed=Embed(
                    title="No responses :frowning2:",
                    description="It seems like no one wanted to play with you.",
                    colour=await get_embed_color(ctx.author)
                )
            )

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def wait_for_users(self, ctx, title, *, is_two_player=False, min_players=2, max_players=5, allow_ai=True,
                             allow_intelligent_ai=True, timeout=60):
        """Waits for users to react to a message when playing a minigame

        :param ctx: The context of where the waiting is taking place
        :param title: The title of the embed to wait for players
        
        :param is_two_player: Whether or not to wait for a single opponent (Default is False)
        :param min_players: The minimum amount of players to wait for when not in a two-player game (Default is 2)
        :param max_players: The maximum amount of players to wait for when not in a two-player game (Default is 5)
        :param allow_ai: Whether or not to allow the option for an AI (Default is True)
        :param allow_intelligent_ai: Whether or not the AI can act smart (Default is True)
        :param timeout: How many seconds to wait before raising a TimeoutError (Default is 60)
            
        :returns: Depending on the type of game, it will either return:
            User, Reaction, list, None
        """

        # Keep track of all players that have joined apart from the original author
        players = [ctx.author]

        # Ask the player if they want to wait for someone to go against 
        #   or if they want to play against an AI

        def create_message_embed(color):
            return Embed(
                title=title,
                description="If you're going to play against {}, react with {}.{}{}{}".format(
                    ctx.author, JOIN,
                    "\n{}, if you'd like to start the game immediately, react with {}".format(
                        ctx.author, PLAY_NOW
                    ) if not is_two_player else "",
                    "\n{}, if you'd like to {}, react with {}.".format(
                        ctx.author,
                        "fill the current player list with AIs" if not is_two_player else "play alone",
                        ROBOT
                    ) if allow_ai else "",
                    "\n{}".format(
                        "\n".join([
                            "`{}`".format(str(player))
                            for player in players
                        ])
                    ) if not is_two_player else ""
                ),
                colour=color
            )
        message = await ctx.send(embed=create_message_embed(await get_embed_color(ctx.author)))
        await message.add_reaction(JOIN)
        if not is_two_player:
            await message.add_reaction(PLAY_NOW)
        if allow_ai:
            await message.add_reaction(ROBOT)

        # Loop until there are enough players
        ai_chosen = False
        while len(players) != max_players:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add",
                    check=lambda r, u: check_reaction_opponent(ctx, message, r, u),
                    timeout=timeout
                )

                # Check if the reaction is ROBOT, ask the user if they want the AI to be smart or random
                #  only process this if allow_ai is True
                is_smart = None
                if str(reaction) == ROBOT and allow_ai:
                    ai_chosen = True

                    # Check if an intelligent AI is allowed
                    if allow_intelligent_ai:
                        await message.clear_reactions()
                        await message.edit(
                            embed=Embed(
                                title="Smart or Random?",
                                description=(
                                    "React with {} if you want the AI to be smart.\n" +
                                    "React with {} if you want the AI to be random."
                                    ).format(
                                        SMART, RANDOM
                                    ),
                                colour=await get_embed_color(ctx.author)
                            )
                        )
                        await message.add_reaction(SMART)
                        await message.add_reaction(RANDOM)
                        smart_reaction, _ = await self.bot.wait_for(
                            "reaction_add",
                            check=lambda r, u: check_reaction_smart_random(ctx, message, r, u)
                        )
                        is_smart = str(smart_reaction) == SMART

                    # An intelligent AI is not allowed
                    #   return the list of players filled with AI IDs
                    else:
                        is_smart = False

                    # Return a list of current players + AIs if this game
                    #   is a multiplayer game
                    if not is_two_player:
                        for ai in range(max_players - len(players)):
                            players.append((ai + 1, is_smart))
                        return players

                # Check if the author wants to play the game immediately
                elif str(reaction) == PLAY_NOW:
                    raise TimeoutError()

                # Check if the game is a two-player game
                if is_two_player:
                    await message.delete()

                    # If is_smart has not been set to True or False
                    #   the user who reacted is the one who is playing the game against
                    #   the original author
                    if is_smart is None:
                        return user
                    else:
                        return SMART if is_smart else RANDOM

                # The game is a multiplayer game
                #   add the user to the game if they haven't already joined 
                #   and update the message
                else:
                    found = False
                    for player in players:
                        if player.id == user.id:
                            found = True
                            break
                    if not found:
                        players.append(user)
                        await message.edit(
                            embed=create_message_embed(await get_embed_color(ctx.author))
                        )
                        continue  # move back to the beginning of the loop
                        #   to get more players

            # No one reacted within the timeout range
            except TimeoutError:
                await message.delete()

                # Check if an AI is allowed and an AI was not chosen
                if allow_ai and not ai_chosen:
                    return None

                # Check if there are enough players
                if len(players) >= min_players:
                    return players

                # Check if there are players but not enough
                elif len(players) != 0:
                    return False

                # There weren't enough players
                return None

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def setup(bot):
    """Add's this cog to the bot

    :param bot: The bot to add the cog to
    """
    bot.add_cog(Game(bot))
