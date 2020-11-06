from asyncio import wait, FIRST_COMPLETED
from discord import Embed
from json import loads
from functools import partial
from requests import post

from cogs.globals import loop, PRIMARY_EMBED_COLOR
from cogs.errors import get_error_message

from cogs.game.minigames.base_game.player import Player
from cogs.game.minigames.chess.board import ChessBoard
from cogs.game.minigames.chess.pieces import COLUMNS, NUMBERS

from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

MAKE_ONE_PLAYER_MOVE = "https://chess-api-chess.herokuapp.com/api/v1/chess/one/move/player"
MAKE_ONE_AI_MOVE = "https://chess-api-chess.herokuapp.com/api/v1/chess/one/move/ai"
MAKE_TWO_PLAYER_MOVE = "https://chess-api-chess.herokuapp.com/api/v1/chess/two/move"
VALIDATE_MOVE = "https://chess-api-chess.herokuapp.com/api/v1/chess/{}/moves"

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class ChessPlayer(Player):

    def __init__(self, member, *, is_smart=False):
        super().__init__(member = member, is_smart = is_smart)
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    async def process_turn(self, game):
        """Processes the player's turn

        :param game: The ChessGame object this player is connected to
        """

        # Determine the flip value
        if game.opponent.is_ai:
            flip = True
        else:
            flip = game.current_player == 0

        await game.message.edit(
            embed = Embed(
                title = "Chess",
                description = (
                    f"{self.get_name()}'s turn\n" +
                    f"{ChessBoard.from_FEN(game.board.board_fen(), flip=flip)}\n" +
                    f"White: {game.opponent.get_name()}\n" +
                    f"Black: {game.challenger.get_name()}\n"
                ),
                colour = PRIMARY_EMBED_COLOR if self.is_ai else await get_embed_color(self.member)
            ).set_footer(
                text = "❕❕React with your chosen column first and then the row❕❕"
            )
        )

        # Check if this player is an AI
        if self.is_ai:

            response = await loop.run_in_executor(
                None,
                partial(
                    post,
                    MAKE_ONE_AI_MOVE,
                    data = {
                        "game_id": game.id
                    },
                    headers = {
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
                )
            )
            response = loads(response.text)
            print(response)
            game.board.push_uci(response["from"] + response["to"])
        
        # This player is not an AI
        else:

            # Get the player's desired piece to move
            column_from, row_from = None, None
            col_num, row_num = 0, 0

            while True:  # Ask the player for their move while
                         #  the move they choose is invalid

                # Column is 0, Row is 1
                for entry in range(2):
                    while True:
                        def check_reaction(reaction, user):
                            return (
                                reaction.message.id == game.message.id and
                                user.id == self.member.id and
                                str(reaction) in COLUMNS
                            )
                        done, pending = await wait([
                            game.bot.wait_for("reaction_add", check = check_reaction),
                            game.bot.wait_for("reaction_remove", check = check_reaction)
                        ], return_when = FIRST_COMPLETED)
                        reaction, user = done.pop().result()
                        for future in pending:
                            future.cancel()
                        
                        # Get the column first, then the row
                        #   but validate the input
                        if entry == 0:  # Column
                            if str(reaction) not in COLUMNS:
                                await game.ctx.send(
                                    embed = get_error_message(
                                        "That is an invalid column! Try again."
                                    ), delete_after = 10)
                            else:

                                # Shift the reaction if the board is flipped 
                                #   (challenger's turn)
                                if game.current_player == 0:
                                    reaction = NUMBERS[7 - NUMBERS.index(str(reaction))]
                                    col_num = 7 - NUMBERS.index(str(reaction))

                                else:
                                    col_num = NUMBERS.index(str(reaction))
                                column_from = COLUMNS[str(reaction)]
                                break
                        else:
                            if str(reaction) not in COLUMNS:
                                await game.ctx.send(
                                    embed = get_error_message(
                                        "That is an invalid row! Try again!"
                                    ), delete_after = 10)
                            else:
                                row_from = str(reaction)[0]  # This will get the number
                                row_num = int(row_from) - 1
                                break
                
                # "Highlight" the player's selected piece
                await game.message.edit(
                    embed = Embed(
                        title = "Chess",
                        description = (
                            f"{self.get_name()}'s turn\n" +
                            f"{ChessBoard.from_FEN(game.board.board_fen(), (row_num, col_num), flip=flip)}\n" +
                            f"White: {game.opponent.get_name()}\n" +
                            f"Black: {game.challenger.get_name()}\n"
                        ),
                        colour = PRIMARY_EMBED_COLOR if self.is_ai else await get_embed_color(self.member)
                    ).set_footer(
                        text = "❕❕React with your chosen column first and then the row❕❕"
                    ))
                    
                # Get the player's desired place to move the piece to and 
                #   validate that the piece can be moved there
                column_to, row_to = None, None

                # Column is 0, Row is 1
                for entry in range(2):
                    while True:
                        def check_reaction(reaction, user):
                            return (
                                reaction.message.id == game.message.id and
                                user.id == self.member.id and
                                str(reaction) in COLUMNS
                            )
                        done, pending = await wait([
                            game.bot.wait_for("reaction_add", check = check_reaction),
                            game.bot.wait_for("reaction_remove", check = check_reaction)
                        ], return_when = FIRST_COMPLETED)
                        reaction, user = done.pop().result()
                        for future in pending:
                            future.cancel()
                        
                        # Get the column first, then the row
                        #   but validate the input
                        if entry == 0:  # Column
                            if str(reaction) not in COLUMNS:
                                await game.ctx.send(
                                    embed = get_error_message(
                                        "That is an invalid column! Try again."
                                    ), delete_after = 10)
                            else:

                                # Shift the reaction if the board is flipped 
                                #   (challenger's turn)
                                if game.current_player == 0:
                                    reaction = NUMBERS[7 - NUMBERS.index(str(reaction))]
                                    
                                column_to = COLUMNS[str(reaction)]
                                break
                        else:
                            if str(reaction) not in COLUMNS:
                                await game.ctx.send(
                                    embed = get_error_message(
                                        "That is an invalid row! Try again!"
                                    ), delete_after = 10)
                            else:
                                row_to = str(reaction)[0]  # This will get the number
                                break
                
                # Check if the player made a valid move
                found = False
                valid_moves = game.board.legal_moves
                for move in valid_moves:
                    if f"{column_from}{row_from}{column_to}{row_to}" == str(move):
                        found = True
                        break
                        
                if not found:
                    await game.ctx.send(
                        embed = get_error_message(
                            "You can't move that piece like that! Try again."
                        ), delete_after = 10
                    )
                else:
                    break
            
            from_position = column_from + row_from
            to_position = column_to + row_to

            # Check if the game is against an AI or not
            #   and let the player make their move
            game.board.push_uci(from_position + to_position)
            url = MAKE_ONE_PLAYER_MOVE if game.opponent.is_ai else MAKE_TWO_PLAYER_MOVE
            await loop.run_in_executor(
                None,
                partial(
                    post, url,
                    data = {
                        "game_id": game.id,
                        "from": from_position,
                        "to": to_position
                    },
                    headers = {
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
                )
            )