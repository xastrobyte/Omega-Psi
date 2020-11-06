from asyncio import sleep
from discord import Embed

from cogs.errors import get_error_message

from cogs.game.minigames.base_game.game import Game
from cogs.game.minigames.connect_four.board import ConnectFourBoard
from cogs.game.minigames.connect_four.player import ConnectFourPlayer
from cogs.game.minigames.connect_four.variables import CONNECT_FOUR_REACTIONS, QUIT

from util.database.database import database
from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class ConnectFourGame(Game):
    """A ConnectFourGame object that holds information about a Connect Four game

    :param bot: The bot object used to wait for reactions
    :param ctx: The context of where this game is being played
    :param challenger: The challenging player
    :param opponent: The player opposing the challenger

    :raises TypeError: When either the challenger or opponent is not given
    """

    DEFAULT_WIDTH = 7
    DEFAULT_HEIGHT = 6

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, bot, ctx, challenger, opponent, *, is_smart = None):
        super().__init__(
            bot, ctx,
            challenger = ConnectFourPlayer(challenger),
            opponent = ConnectFourPlayer(opponent, is_smart = is_smart)
        )
        self.board = ConnectFourBoard()
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
        """Let's the challenger and opponent play this game of Connect Four
        """

        # Send a message to start the game and add the reactions
        self.message = await self.ctx.send(
            embed = Embed(
                title = "Connect Four",
                description = "{}'s Turn\n{}\n{}\n{}".format(
                    self.get_current_player().get_name(),
                    str(self.board),
                    ":blue_circle: {}".format(self.challenger.get_name()),
                    ":red_circle: {}".format(self.opponent.get_name())
                ),
                colour = await get_embed_color(self.challenger.member)
            )
        )
        for reaction in CONNECT_FOUR_REACTIONS:
            await self.message.add_reaction(str(reaction))
        
        # Continue playing the game until there is a winner
        winner = None
        while winner == None:

            # Ask the current player to make a move
            result = await self.get_current_player().process_turn(self)

            # Check if the player is quitting
            if result == ConnectFourPlayer.QUIT:

                # If the game was against a real player, the quitting player loses
                #   and the other player wins
                if not self.opponent.is_ai:
                    winner = self.challenger.id != self.get_current_player().id
                    break
            
            # The player is not quitting, update the game board message
            else:

                # Check if there is a winner
                winner = self.board.check_for_winner()
                if winner != None:
                    break

                # Check if the game is a draw
                elif self.board.is_board_full():
                    await self.message.edit(
                        embed = Embed(
                            title = "Draw!",
                            description = "{}\n{}\n{}".format(
                                str(self.board),
                                ":blue_circle: {}".format(self.challenger.get_name()),
                                ":red_circle: {}".format(self.opponent.get_name())
                            ),
                            colour = await get_embed_color(self.challenger.member)
                        )
                    )
                    break
                
                # The move is either valid or a column is full
                else:
                
                    # Check if the column the player made a move on
                    #   is full, update the message, sleep for 5 seconds so they can read it,
                    #   and restore the original message
                    if result == ConnectFourPlayer.COLUMN_FULL:
                        await self.message.edit(
                            embed = get_error_message("That column is full! Try a different column.")
                        )
                        await sleep(5)
                    
                    # If the column was not full, move to the next player
                    else:
                        self.next_player()
                    
                    # Update the message; This is used either when the next player is going
                    #   or when refreshing the message after telling the current player
                    #   that the column they wanted to go to is full
                    await self.message.edit(
                        embed = Embed(
                            title = "Connect Four",
                            description = "{}'s Turn\n{}\n{}\n{}".format(
                                self.get_current_player().get_name(),
                                str(self.board),
                                ":blue_circle: {}".format(self.challenger.get_name()),
                                ":red_circle: {}".format(self.opponent.get_name())
                            ),
                            colour = await get_embed_color(self.challenger)
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
                        ":blue_circle: {}".format(self.challenger.get_name()),
                        ":red_circle: {}".format(self.opponent.get_name())
                    ),
                    colour = await get_embed_color(self.challenger.member)
                )
            )
        
        # Update the wins in the database
        #   only update the opponents wins if they are not an AI
        await database.users.update_connect_four(self.challenger.member, winner)
        if not self.opponent.is_ai:
            await database.users.update_connect_four(self.opponent.member, not winner)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Other Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_valid_reactions(self):
        """Returns a list of valid reactions a player can make when it is their turn

        :rtype: list
        """

        # Setup a list of valid reactions
        valid_reactions = []
        for column in range(self.board.width):
            if not self.board.is_column_full(column):
                valid_reactions.append(CONNECT_FOUR_REACTIONS[column])
        
        # Add the LEAVE reaction, it is always valid
        valid_reactions.append(QUIT)
        return valid_reactions