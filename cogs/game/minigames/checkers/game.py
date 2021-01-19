from asyncio import sleep
from discord import Embed

from cogs.globals import PRIMARY_EMBED_COLOR, LEAVE
from cogs.game.minigames.base_game.game import Game
from cogs.game.minigames.checkers.pieces import UNDO, RESIGN, NUMBERS, COLUMNS, PIECES, HIGHLIGHT
from cogs.game.minigames.checkers.player import CheckersPlayer
from checkers.game import Game as ImparaaiGame

from util.database.database import database
from util.functions import get_embed_color

class CheckersGame(Game):
    """A CheckersGame contains information about a checkers game
    being played
    """
    def __init__(self, bot, ctx, challenger, opponent, *, is_smart=False):
        super().__init__(
            bot, ctx,
            challenger = CheckersPlayer(challenger),
            opponent = CheckersPlayer(opponent)
        )

        self.game = ImparaaiGame()
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_board(self, selected = None, *, flip = False):
        """Returns the board to render in a Discord embed

        :param selected: The current selected piece
        :param flip: Whether to flip the board or not
        """

        # Create a grid for the Checkers board
        grid = []
        for row in range(8):
            grid.append([])
            for col in range(8):
                grid[row].append(None)

        # Insert the pieces into the grid
        for piece in self.game.board.pieces:
            if piece.position is not None:
                if flip:
                    row = piece.get_row()
                    col = (3 - piece.get_column()) * 2
                    col += 1 if piece.get_row() % 2 != 0 else 0
                else:
                    row = 7 - piece.get_row()
                    col = piece.get_column() * 2
                    col += 1 if piece.get_row() % 2 == 0 else 0
                grid[row][col] = "{}{}".format(
                    "b" if piece.player == 1 else "r",
                    "k" if piece.king else "n"
                )
        
        def is_white(row, col) -> bool:
            """Returns whether or not the board space is a white space

            :param row: The row to look at
            :param col: the column to look at
            """
            return (row % 2 == 0) == (col % 2 == 0)
        
        # Convert the grid into a string replacing all instances
        #   of r* to red pieces and b* to black pieces
        #   whether they are a regular piece or a king piece
        result = ":black_large_square: "
        for emoji in COLUMNS:
            result += emoji + " "
        result += "\n"
        for i in range(len(grid)):
            row = grid[i]
            result += list(COLUMNS.keys())[i] + " "
            for j in range(len(row)):
                col = row[j]
                if col is None:
                    col = (":white_large_square: " 
                            if is_white(i, j)
                            else ":black_large_square: ")
                else:
                    if selected == (i, j):
                        col = HIGHLIGHT[col[1]]
                    else:
                        col = PIECES[col]
                result += col
            result += "\n"
        return result
    
    async def play(self):
        """Lets the players play the game"""

        if self.opponent.is_ai:
            flip = True
        else:
            flip = self.current_player == 0
        self.message = await self.ctx.send(embed = Embed(
            title = "Chess",
            description = (
                f"{self.get_current_player().get_name()}'s turn\n" +
                f"{self.get_board(flip = flip)}\n" +
                f":red_large_circle:: {self.opponent.get_name()}\n" +
                f":brown_large_circle:: {self.challenger.get_name()}\n"
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

            # Do this manually because of a double jump issue
            #   if .next_player() is used, the players will swap
            #   colors after every opportunity for a double jump
            if self.game.whose_turn() == 1:
                self.current_player = 1
            else:
                self.current_player = 0
            
            # Flip the board if needed
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
            title = "Checkers"

            # There is no winner yet
            if not self.game.is_over():
                await self.message.edit(
                    embed = Embed(
                        title = title,
                        description = (
                            f"{self.get_current_player().get_name()}'s turn\n" +
                            f"{self.get_board(flip = flip)}\n" +
                            f":red_large_circle:: {self.opponent.get_name()}\n" +
                            f":brown_large_circle:: {self.challenger.get_name()}\n"
                        ),
                        colour = PRIMARY_EMBED_COLOR if self.get_current_player().is_ai else await get_embed_color(self.get_current_player().member)
                    ).set_footer(
                        text = "❕❕React with your chosen column first and then the row❕❕"
                    )
                )
                await sleep(3)
            
            # There is a winner/draw
            else:
                if self.game.is_over():
                    winner = self.get_current_player()
                else:
                    break

        # If something doesn't go wrong, let people know who won
        if winner is not None:
            await self.message.edit(
                embed = Embed(
                    title = f"{winner.get_name()} Won!",
                    description = (
                        f"{self.get_board(flip = flip)}\n" +
                        f":red_large_circle:: {self.opponent.get_name()}\n" +
                        f":brown_large_circle:: {self.challenger.get_name()}\n"
                    ),
                    colour = PRIMARY_EMBED_COLOR if winner.is_ai else await get_embed_color(winner.member)
                )
            )
            if not self.opponent.is_ai:
                await database.users.update_checkers(self.opponent.member, self.opponent.member.id == winner.id)
            await database.users.update_checkers(self.challenger.member, self.challenger.member.id == winner.id)

    