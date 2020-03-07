from discord import Embed

from cogs.game.minigames.base_game.game import Game
from cogs.game.minigames.omok.board import OmokBoard
from cogs.game.minigames.omok.player import OmokPlayer
from cogs.game.minigames.omok.variables import OMOK_REACTIONS, QUIT

from util.database.database import database
from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class OmokGame(Game):
    """An OmokGame object that holds information about an Omok game

    Parameters
    ----------
        bot : AutoShardedBot
            The bot object used to wait for reactions
        ctx : context
            The context of where this game is being played
        challenger : Member
            The challenging player
        opponent : Member or int
            The player opposing the challenger
            If this parameter is an int, the opponent is an AI
    """

    def __init__(self, bot, ctx, challenger, opponent, *, is_smart = False):
        super().__init__(
            bot, ctx,
            challenger = OmokPlayer(challenger),
            opponent = OmokPlayer(opponent, is_smart = is_smart)
        )
        self.board = OmokBoard()
        self.message = None
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Getters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @property
    def board(self):
        return self.__board
    
    @property
    def message(self):
        return self.__message
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Setters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @board.setter
    def board(self, board):
        self.__board = board
    
    @message.setter
    def message(self, message):
        self.__message = message

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Play Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def play(self):
        """Let's the challenger and opponent play this game of Omok"""

        # Send a message to start the game and add the reactions
        self.message = await self.ctx.send(
            embed = Embed(
                title = "Omok",
                description = "{}'s Turn\n{}\n{}\n{}".format(
                    self.get_current_player().get_name(),
                    str(self.board),
                    ":brown_circle: {}".format(self.challenger.get_name()),
                    ":white_circle: {}".format(self.opponent.get_name())
                ),
                colour = await get_embed_color(self.challenger.member)
            ).set_footer(
                text = "{}".format(
                    "❕❕ React with your chosen column first and then the row ❕❕"
                ) if not self.get_current_player().is_ai else ""
            )
        )
        for reaction in OMOK_REACTIONS:
            await self.message.add_reaction(str(reaction))

        # Continue playing the game until there is a winner
        winner = None
        while winner == None:
        
            # Ask the current player to make a move
            result = await self.get_current_player().process_turn(self)

            # Check if the player is quitting
            if result == OmokPlayer.QUIT:

                # Get the quitting player and update the wins/losses in the database
                winner = self.challenger.id != self.get_current_player().id
            
            # The player is not quitting, update the game board message
            else:

                # Check if there is a winner
                #   the check_for_winner function returns an integer
                #   Board.WIN for player win, Board.LOSS for AI win, 0 for No winner yet
                winner = self.board.check_for_winner()
                if winner != 0:
                    winner = winner == OmokBoard.WIN
                    break
                else:
                    winner = None

                # Check if the game is a draw
                if self.board.is_full():
                    await self.message.edit(
                        embed = Embed(
                            title = "Draw!",
                            description = "{}\n{}\n{}".format(
                                str(self.board),
                                ":brown_circle: {}".format(self.challenger.get_name()),
                                ":white_circle: {}".format(self.opponent.get_name())
                            ),
                            colour = await get_embed_color(self.challenger)
                        )
                    )
                    break

                # The game is still going; Move to the next player and
                #   update the message with the player's turn
                else:
                    self.next_player()
                    await self.message.edit(
                        embed = Embed(
                            title = "Omok",
                            description = "{}'s Turn\n{}\n{}\n{}".format(
                                self.get_current_player().get_name(),
                                str(self.board),
                                ":brown_circle: {}".format(self.challenger.get_name()),
                                ":white_circle: {}".format(self.opponent.get_name())
                            ),
                            colour = await get_embed_color(self.challenger)
                        ).set_footer(
                            text = "{}".format(
                                "❕❕ React with your chosen column first and then the row ❕❕"
                            ) if not self.get_current_player().is_ai else ""
                        )
                    )
        
        # Tell the players who won, if anyone won
        if winner != None:
            await self.message.edit(
                embed = Embed(
                    title = "{} Wins!".format(
                        self.challenger.get_name() if winner else self.opponent.get_name()
                    ),
                    description = "{}\n{}\n{}".format(
                        str(self.board),
                        ":brown_circle: {}".format(self.challenger.get_name()),
                        ":white_circle: {}".format(self.opponent.get_name())
                    ),
                    colour = await get_embed_color(self.challenger)
                )
            )
        
            # Update the wins in the database
            #   only update the opponents wins if they are not an AI
            await database.users.update_omok(self.challenger.member, winner)
            if not self.opponent.is_ai:
                await database.users.update_omok(self.opponent.member, not winner)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Other Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_valid_reactions(self):
        """Returns a list of valid reactions a player can make when it is their turn

        Returns
        -------
            list
                Valid reactions a player can make during their turn
        """
        
        # Setup a list of valid reactions
        valid_reactions = OMOK_REACTIONS
        """
        for row in range(self.board.height):
            for col in range(self.board.width):
                if self.board.board[row][col] == None:
                    valid_reactions.append(OMOK_REACTIONS[row * 3 + col % 3])
        """
        
        # Add the QUIT reaction, it is always valid
        valid_reactions.append(QUIT)
        return valid_reactions