from asyncio import sleep
from discord import Embed
from json import loads
from requests import get

from chess import Board, WHITE, BLACK

from cogs.globals import PRIMARY_EMBED_COLOR, LEAVE
from cogs.game.minigames.base_game.game import Game
from cogs.game.minigames.chess.board import ChessBoard
from cogs.game.minigames.chess.player import ChessPlayer
from cogs.game.minigames.chess.pieces import NUMBERS, RESIGN, UNDO

from util.database.database import database
from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

CREATE_GAME = "http://chess-api-chess.herokuapp.com/api/v1/chess/{}"
GET_BOARD = "http://chess-api-chess.herokuapp.com/api/v1/chess/{}/fen"

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class ChessGame(Game):
    """A ChessGame holds data about two players or a player and an AI
    in a Chess game
    """

    def __init__(self, bot, ctx, challenger, opponent, *, is_smart=False):
        super().__init__(
            bot, ctx,
            challenger = ChessPlayer(challenger),
            opponent = ChessPlayer(opponent)
        )

        # Create a new game using the Chess API
        response = get(
            CREATE_GAME.format(
                "one" if self.opponent.is_ai else "two"
            ))
        response = loads(response.text)

        # Set the Game's data
        self.board = Board()
        self.message = None
        self.id = str(response["game_id"])
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    async def play(self):
        """Lets the players play the game"""
        self.current_player = 1  # opponent always goes first
        if self.opponent.is_ai:
            flip = True
        else:
            flip = self.current_player == 0
        self.message = await self.ctx.send(embed = Embed(
            title = "Chess",
            description = (
                f"{self.get_current_player().get_name()}'s turn\n" +
                f"{ChessBoard.from_FEN(self.board.board_fen(), flip=flip)}\n" +
                f"White: {self.opponent.get_name()}\n" +
                f"Black: {self.challenger.get_name()}\n"
            ),
            colour = PRIMARY_EMBED_COLOR if self.get_current_player().is_ai else await get_embed_color(self.get_current_player().member)
        ).set_footer(
            text = "❕❕React with your chosen column first and then the row❕❕"
        ))

        # Add the reactions to the game message
        for reaction in (NUMBERS + [UNDO, RESIGN]):
            await self.message.add_reaction(reaction)
        
        # Play the game while there is no winner
        winner = None
        while winner is None:
            self.board.turn = WHITE if self.current_player == 1 else BLACK
            if self.opponent.is_ai:
                flip = True
            else:
                flip = self.current_player == 0

            # Let the player take their turn
            #   and check if there is a winner
            result = await self.get_current_player().process_turn(self)
            if result is False or result == LEAVE:
                if result is False:
                    winner = self.get_next_player()
                break

            # Check if there is a check, checkmate, or stalemate
            #   give the player an option to resign
            title = "Chess"
            if self.board.is_check():
                title = "Chess - Check!"
            elif self.board.is_stalemate():
                title = "Chess - Stalemate"

            # There is no winner yet
            if self.board.result() == "*":
                self.next_player()
                await self.message.edit(
                    embed = Embed(
                        title = title,
                        description = (
                            f"{self.get_current_player().get_name()}'s turn\n" +
                            f"{ChessBoard.from_FEN(self.board.board_fen(), flip=flip)}\n" +
                            f"White: {self.opponent.get_name()}\n" +
                            f"Black: {self.challenger.get_name()}\n"
                        ),
                        colour = PRIMARY_EMBED_COLOR if self.get_current_player().is_ai else await get_embed_color(self.get_current_player().member)
                    ).set_footer(
                        text = "❕❕React with your chosen column first and then the row❕❕"
                    )
                )
                await sleep(3)
            
            # There is a winner/draw
            else:
                if not self.board.is_stalemate():
                    winner = self.get_current_player()
                else:
                    break

        # If something doesn't go wrong, let people know who won
        if winner is not None:
            await self.message.edit(
                embed = Embed(
                    title = f"{winner.get_name()} Won!",
                    description = (
                        f"{ChessBoard.from_FEN(self.board.board_fen(), flip=flip)}\n" +
                        f"White: {self.opponent.get_name()}\n" +
                        f"Black: {self.challenger.get_name()}\n"
                    ),
                    colour = PRIMARY_EMBED_COLOR if winner.is_ai else await get_embed_color(winner.member)
                )
            )
            if not self.opponent.is_ai:
                await database.users.update_chess(self.opponent.member, self.opponent.member.id == winner.member.id)
            await database.users.update_chess(self.challenger.member, self.challenger.member.id == winner.member.id)
    
    # # # # # # # # # # # # # # # # # # # # # # # # #