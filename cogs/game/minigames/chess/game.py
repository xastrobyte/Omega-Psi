from asyncio import sleep
from discord import Embed
from functools import partial
from json import loads
from requests import get, post

from chess import Board

from cogs.globals import loop, PRIMARY_EMBED_COLOR

from cogs.game.minigames.base_game.game import Game
from cogs.game.minigames.chess.board import ChessBoard
from cogs.game.minigames.chess.player import ChessPlayer
from cogs.game.minigames.chess.pieces import COLUMNS

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
            )
        )
        response = loads(response.text)

        # Set the Game's data
        self.board = Board()
        self.message = None
        self.id = response["game_id"]
    
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
        for reaction in COLUMNS:
            await self.message.add_reaction(reaction)
        
        # Play the game while there is no winner
        winner = None
        while winner == None:

            # Let the player take their turn
            #   and check if there is a winner
            await self.get_current_player().process_turn(self)
            winner = await ChessBoard.check_for_winner(self)
            if self.opponent.is_ai:
                flip = True
            else:
                flip = self.current_player == 0

            # There is no winner yet
            if winner == None:
                self.next_player()
                await self.message.edit(
                    embed = Embed(
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
                    )
                )
            await sleep(3)
    
    # # # # # # # # # # # # # # # # # # # # # # # # #