from asyncio import wait, ALL_COMPLETED, sleep
from discord import Embed

from cogs.globals import PRIMARY_EMBED_COLOR

from cogs.game.minigames.base_game.game import Game
from cogs.game.minigames.battleship.board import BattleshipBoard
from cogs.game.minigames.battleship.player import BattleshipPlayer

from util.database.database import database
from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class BattleshipGame(Game):
    """A BattleshipGame object that holds information about a Battleship game

    Parameters
    ----------
    :param bot: The bot object used to wait for reactions
    :param ctx: The context of where this game is being played
    :param challenger: The challenging player
    :param opponent: The player opposing the challenger
            If this parameter is an int, the opponent is an AI
    """

    def __init__(self, bot, ctx, challenger, opponent, *, is_smart = None):
        super().__init__(
            bot, ctx,
            challenger = BattleshipPlayer(challenger),
            opponent = BattleshipPlayer(opponent, is_smart = is_smart)
        )
        self.message = None
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Getters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @property
    def message(self):
        return self.__message

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Setters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @message.setter
    def message(self, message):
        self.__message = message
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Play Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def play(self):
        """Let's the challenger and opponent play this game of Battleship"""

        # Let the players setup their boards
        message = await self.ctx.send(
            embed = Embed(
                title = "Setting up Boards",
                description = "{} and {} are setting up their boards right now!".format(
                    self.challenger.get_name(),
                    self.opponent.get_name()
                ),
                colour = PRIMARY_EMBED_COLOR
            )
        )
        done, pending = await wait([
            self.challenger.setup(self),
            self.opponent.setup(self)
        ], return_when = ALL_COMPLETED)
        for future in pending:
            future.cancel()
        await message.delete()
        
        # Continue playing the game until there is a winner
        winner = None
        while winner is None:

            # Show the board, ask the current player to make a shot, and display the results
            await self.show_board()
            result = await self.get_current_player().process_turn(self)

            # Check if the player is quitting
            if result == BattleshipPlayer.QUIT:

                # Get the quitting player and update the wins/losses in the database
                winner = self.challenger.id != self.get_current_player().id
            
            # The player is not quitting, update messages in the game
            else:

                # Check if there is a winner
                #   by checking if the opposite player's ships are all sunk 
                if self.are_opponent_ships_sunk():
                    winner = self.challenger.id == self.get_current_player().id
                    break
                
                # The game is still going
                else:

                    # Update the players on what happened
                    await self.show_results(result == BattleshipBoard.HIT)
                    await sleep(3)

                    # Check if the current player hit something, they get to go again
                    if result != BattleshipBoard.HIT:
                        self.next_player()
        
        # Tell the players who won
        await self.show_winner()
        await database.users.update_battleship(self.challenger.member, winner)
        if not self.opponent.is_ai:
            await database.users.update_battleship(self.opponent.member, not winner)
    
    async def show_board(self):
        """Show the board to both players and the game channel"""
        await self.challenger.show_board(self)
        await self.opponent.show_board(self)
        
        # Send the message to the game channel. Create a new message if needed
        embed = Embed(
            title = "{}'s Turn!".format(
                self.get_current_player().get_name()
            ),
            description = self.get_current_board().display(False),
            colour = PRIMARY_EMBED_COLOR if self.get_current_player().is_ai else await get_embed_color(self.get_current_player().member)
        )
        if self.message == None:
            self.message = await self.ctx.send(embed = embed)
        
        # Update the existing message
        else:
            await self.message.edit(embed = embed)
    
    async def show_results(self, did_hit):
        """Show the results to both players

        :param did_hit: Whether or not the current player made a HIT on the opposing player's board
        """
        await self.challenger.show_results(self, did_hit)
        await self.opponent.show_results(self, did_hit)

        # Update the message
        await self.message.edit(
            embed = Embed(
                title = "{} {}!".format(
                    self.get_current_player().get_name(),
                    "made a hit" if did_hit else "missed"
                ),
                description = self.get_current_board().display(False),
                colour = PRIMARY_EMBED_COLOR if self.get_current_player().is_ai else await get_embed_color(self.get_current_player().member)
            )
        )
    
    async def show_winner(self):
        """Shows the winner of this Battleship game which will be the current player"""
        await self.challenger.show_winner(self, self.get_current_player())
        await self.opponent.show_winner(self, self.get_current_player())
        await self.message.delete()

        # Show the winner. Send 2 separate messages to show each player's board
        #   since they don't both fit into one embed
        await self.ctx.send(
            embed = Embed(
                title = "{} Won!".format(self.get_current_player().get_name()),
                description = "**{}'s Board**\n{}".format(
                    self.challenger.get_name(),
                    self.challenger.board.display(True)
                ),
                colour = await get_embed_color(self.challenger.member)
            )
        )
        await self.ctx.send(
            embed = Embed(
                title = "{} Won!".format(self.get_current_player().get_name()),
                description = "**{}'s Board**\n{}".format(
                    self.opponent.get_name(),
                    self.opponent.board.display(True)
                ),
                colour = PRIMARY_EMBED_COLOR if self.opponent.is_ai else await get_embed_color(self.opponent.member)
            )
        )
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Other Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def are_opponent_ships_sunk(self):
        """Returns whether or not all of the opponents ships have been sunk

        :rtype: boolean
        """
        for ship in BattleshipBoard.SHIPS:
            if not self.get_current_board().did_ship_sink(ship["number"]):
                return False
        return True

    def did_opponent_submit(self, player):
        """Returns whether or not the opposite player submitted their board

        :param player: The player object that asked if the opponent submitted
        
        :rtype: boolean
        """
        if player.id == self.challenger.id:
            return self.opponent.board is not None
        return self.challenger.board is not None
    
    def get_current_board(self):
        """Returns the opposing player's board

        :rtype: BattleshipBoard
        """
        if self.get_current_player().id == self.challenger.id:
            return self.opponent.board
        return self.challenger.board
