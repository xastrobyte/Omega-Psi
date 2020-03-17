from asyncio import sleep, wait, FIRST_COMPLETED
from discord import Embed
from random import choice, randint

from cogs.errors import get_error_message
from cogs.globals import PRIMARY_EMBED_COLOR

from cogs.game.minigames.base_game.player import Player
from cogs.game.minigames.battleship.board import BattleshipBoard
from cogs.game.minigames.battleship.variables import BATTLESHIP_REACTIONS, DOWN, UP, LEFT, RIGHT, DIRECTIONS, QUIT

from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class BattleshipPlayer(Player):
    """A BattleshipPlayer object holds information regarding 
    a player in the Battleship minigame.

    Parameters
    ----------
        member : Member
            The discord member that will be connected to this Player

    Keyword Parameters
    ------------------
        is_smart : boolean
            A boolean value determining if this Player is playing smart or random
            Note: this only applies to AI players and is only set to True or False if
                    this player is an AI player
    """

    QUIT = "QUIT"
    
    def __init__(self, member, *, is_smart = None):
        super().__init__(
            member = member, 
            is_smart = is_smart
        )
        self.board = None
        self.message = None

        self.last_hit = None
        self.current_direction = None
        self.tried_directions = []

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Getters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @property
    def board(self):
        return self.__board
    
    @property
    def message(self):
        return self.__message
    
    @property
    def last_hit(self):
        return self.__last_hit
    
    @property
    def current_direction(self):
        return self.__current_direction
    
    @property
    def tried_directions(self):
        return self.__tried_directions

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Setters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @board.setter
    def board(self, board):
        self.__board = board
    
    @message.setter
    def message(self, message):
        self.__message = message
    
    @last_hit.setter
    def last_hit(self, last_hit):
        self.__last_hit = last_hit
    
    @current_direction.setter
    def current_direction(self, current_direction):
        self.__current_direction = current_direction
    
    @tried_directions.setter
    def tried_directions(self, tried_directions):
        self.__tried_directions = tried_directions

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Play Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def setup(self, game):
        """Asks the player to setup their ships in the specified Battleship game

        Parameters
        ----------
            game : BattleshipGame
                The game object that this player is connected to
        """

        # Ask the player to decide where they want their ships to go to
        board = BattleshipBoard()
        for ship in BattleshipBoard.SHIPS:
        
            # Check if this player is an AI
            if self.is_ai:
            
                # Choose random locations and random directions for the AIs ships to go to
                valid = False
                while not valid:
                    row, column = randint(0, board.height - 1), randint(0, board.width - 1)

                    # Check if the spot is taken, choose a new spot
                    if board.get_at(row, column) is not None:
                        continue
                    
                    # Choose a random direction (i.e. (-1, 0), (1, 0), etc.)
                    #   and make sure the ship can go that way. If not, 
                    #   try each direction
                    directions = list(DIRECTIONS)   # Make a copy of the DIRECTIONS emojis to
                                                    # decide on the direction of the current ship
                    while len(directions) != 0:
                        direction = directions.pop(randint(0, len(directions) - 1))

                        # Get the lines from the target point to the end point based off
                        #   the direction chosen
                        direction = (
                            1 if str(direction) == DOWN else (-1 if str(direction) == UP else 0),
                            1 if str(direction) == RIGHT else (-1 if str(direction) == LEFT else 0)
                        )

                        # Iterate through the offsets based off the length of the ship and the direction of the ship
                        valid_direction = True
                        for offset in range(ship["length"]):
                            if (
                                row + (offset * direction[0]) > board.height - 1 or 
                                row + (offset * direction[0]) < 0 or
                                column + (offset * direction[1]) > board.width - 1 or
                                column + (offset * direction[1]) < 0
                            ):
                                valid_direction = False
                                break
                            if board.get_at(row + (offset * direction[0]), column + (offset * direction[1])) is not None:
                                valid_direction = False
                                break
                        
                        # If the direction chosen is valid, place the ship there and move onto the next ship
                        if valid_direction:
                            for offset in range(ship["length"]):
                                board.set_at(row + (offset * direction[0]), column + (offset * direction[1]), ship["number"])
                            valid = True
                            break

            # This player is not an AI
            else:

                # Create the embed
                embed = Embed(
                    title = "Place your ships!",
                    description = "{}\nChoose a place for your {} to go (length {})".format(
                        board.display(True),
                        ship["name"], ship["length"]
                    ),
                    colour = await get_embed_color(self.member)
                ).set_footer(
                    text = "❕❕ React with your chosen column first and then the row ❕❕"
                )
                if not self.message:
                    self.message = await self.member.send(embed = embed)
                else:
                    await self.message.edit(embed = embed)
                if BattleshipBoard.SHIPS.index(ship) == 0:
                    for emoji in BATTLESHIP_REACTIONS:
                        await self.message.add_reaction(emoji)
                    
                # Ask the player to select a valid row and column
                row = column = -1
                while True:

                    # Create the embed
                    embed = Embed(
                        title = "Place your ships!",
                        description = "{}\nChoose a place for your {} to go (length {})".format(
                            board.display(True),
                            ship["name"], ship["length"]
                        ),
                        colour = await get_embed_color(self.member)
                    ).set_footer(
                        text = "❕❕ React with your chosen column first and then the row ❕❕"
                    )
                    await self.message.edit(embed = embed)

                    # Wait for the player to react with their row/column
                    def check_reaction(reaction, user):
                        return (
                            reaction.message.id == self.message.id and
                            user.id == self.id and
                            str(reaction) in BATTLESHIP_REACTIONS
                        )
                    done, pending = await wait([
                        game.bot.wait_for("reaction_add", check = check_reaction),
                        game.bot.wait_for("reaction_remove", check = check_reaction)
                    ], return_when = FIRST_COMPLETED)
                    reaction, user = done.pop().result()
                    for future in pending:
                        future.cancel()
                    
                    # Check if the player needs to choose a column
                    if column == -1:
                        column = BATTLESHIP_REACTIONS.index(str(reaction))
                    else:
                        row = BATTLESHIP_REACTIONS.index(str(reaction))

                        # Make sure this row and column is open on the player's board
                        if (row, column) in board.get_legal_moves():
                            
                            # Ask the player what direction they'd like their ship to go towards
                            #   the ship will always go vertical downwards or horizontal rightwards
                            if BattleshipBoard.SHIPS.index(ship) == 0:
                                for emoji in DIRECTIONS:
                                    await self.message.add_reaction(emoji)
                            await self.message.edit(
                                embed = Embed(
                                    title = "What direction?",
                                    description = (
                                        """
                                        If you'd like your ship to go vertical, react with either {} or {}
                                        If you'd like your ship to go horizontal, react with either {} or {}
                                        """
                                    ).format(*DIRECTIONS),
                                    colour = await get_embed_color(self.member)
                                )
                            )
                            done, pending = await wait([
                                game.bot.wait_for("reaction_add", check = lambda reaction, user: (
                                    reaction.message.id == self.message.id and
                                    user.id == self.id and
                                    str(reaction) in DIRECTIONS
                                )),
                                game.bot.wait_for("reaction_remove", check = lambda reaction, user: (
                                    reaction.message.id == self.message.id and
                                    user.id == self.id and
                                    str(reaction) in DIRECTIONS
                                ))
                            ], return_when = FIRST_COMPLETED)
                            reaction, user = done.pop().result()
                            for future in pending:
                                future.cancel()
                            
                            # Make sure the spots below this row and column are open
                            #   given the size of the current ship and that the ship does not go out of bounds
                            if str(reaction) in [DOWN, UP]:
                                comparison = (
                                    (row + (ship["length"] - 1) < board.height)
                                    if str(reaction) == DOWN else
                                    (row - (ship["length"] - 1) >= 0)
                                )
                                row_value = lambda offset: (row + offset) if str(reaction) == DOWN else (row - offset)

                                # Check that the ship would not exceed the vertical bounds
                                if comparison:
                                    valid = True
                                    for offset in range(ship["length"]):
                                        if board.get_at(row_value(offset), column) is not None:
                                            await self.member.send(
                                                embed = get_error_message(
                                                    "The spaces {} ({},{}) are not open. Please choose another place.".format(
                                                        "below" if str(reaction) == DOWN else "above",
                                                        row, column
                                                    )
                                                ),
                                                delete_after = 5
                                            )
                                            row = column = -1
                                            valid = False
                                            continue
                                    
                                    # The direction is valid, set the offsets
                                    if valid:
                                        for offset in range(ship["length"]):
                                            board.set_at(row_value(offset), column, ship["number"])
                                        break
                                
                                # The ship would exceed the vertical bounds
                                else:
                                    row = column = -1
                                    await self.member.send(
                                        embed = get_error_message("You cannot make your ship vertical. It's too {}".format(
                                            "low" if str(reaction) == DOWN else "high"
                                        )),
                                        delete_after = 5
                                    )
                                    continue
                            
                            # Make sure the spots to the right of this row and column are open
                            #   given the size of the current ship and that the ship does not go out of bounds
                            elif str(reaction) in [LEFT, RIGHT]:
                                comparison = (
                                    (column + (ship["length"] - 1) < board.width)
                                    if str(reaction) == RIGHT else
                                    (column - (ship["length"] - 1) >= 0)
                                )
                                column_value = lambda offset: (column + offset) if str(reaction) == RIGHT else (column - offset)

                                # Check that the ship would not exceed the horizontal bounds
                                if comparison:
                                    valid = True
                                    for offset in range(ship["length"]):
                                        if board.get_at(row, column_value(offset)) is not None:
                                            await self.member.send(
                                                embed = get_error_message(
                                                    "The spaces to the {} of ({},{}) are not open. Please choose another place.".format(
                                                        "right" if str(reaction) == RIGHT else "left",
                                                        row, column
                                                )),
                                                delete_after = 5
                                            )
                                            row = column = -1
                                            valid = False
                                            continue
                                    
                                    # The direction is valid, set the offsets
                                    if valid:
                                        for offset in range(ship["length"]):
                                            board.set_at(row, column_value(offset), ship["number"])
                                        break
                                
                                # The ship would exceed the horizontal bounds
                                else:
                                    row = column = -1
                                    await self.member.send(
                                        embed = get_error_message("You cannot make your ship horizontal. It's too far to the {}".format(
                                            "right" if str(reaction) == RIGHT else "left"
                                        )),
                                        delete_after = 5
                                    )
                                    continue
                        
                        # The row and column is not open
                        else:
                            row = column = -1
                            await self.member.send(
                                embed = get_error_message("That row and column is already occupied! Choose a new place."),
                                delete_after = 5
                            )
                
        # Let the player know they must wait until the other player
        #   finishes setting up their board unless this player is the one the other person was waiting on
        self.board = board
        if self.message:    # Only remove the message if it exists currently. We reset this so the direction reactions dont stick
                            # during gameplay for this player
            await self.message.delete()
            self.message = None
        if not game.did_opponent_submit(self) and not self.is_ai:
            await self.member.send(
                embed = Embed(
                    title = "Now you just wait!",
                    description = "Once {} finishes setting up their board, the game will start!".format(
                        (game.opponent if game.opponent.id != self.id else game.challenger).get_name()
                    ),
                    colour = await get_embed_color(self.member)
                ),
                delete_after = 5
            )

    async def process_turn(self, game):
        """
        Parameters
        ----------
            game : BattleshipGame
                The game object that this player is connected to
        
        Returns
        -------
            result : BattleshipBoard.HIT or BattleshipBoard.MISS
                Whether the player made a hit or a miss on their opponents board
        """
        
        # Check if the player is an AI
        if self.is_ai:
            
            # Check if there was a last hit and that the AI is smart
            result = None
            if self.last_hit and self.is_smart:
                row = self.last_hit[0]
                column = self.last_hit[1]

                # Check if a direction exists, continue to go towards that direction
                if self.current_direction:
                    row += self.current_direction[0]
                    column += self.current_direction[1]

                    # Check if the new row and column exceed the board boundaries
                    #   if so, reverse the direction
                    if row < 0 or row >= game.get_current_board().height or column < 0 or column > game.get_current_board().width:
                        self.current_direction = (
                            -self.current_direction[0],
                            -self.current_direction[1]
                        )
                        row += self.current_direction[0]
                        column += self.current_direction[1]

                    # Continue generating a new position until the position is not in shots
                    while (row, column) in game.get_current_board().shots:
                        row += self.current_direction[0]
                        column += self.current_direction[1]
                    result = game.get_current_board().fire(row, column)

                    # If there was a hit, save the last hit and check if the ship was sunk
                    if result == BattleshipBoard.HIT:
                        self.last_hit = row, column
                        if game.get_current_board().did_ship_sink(game.get_current_board().get_at(*self.last_hit)):
                            self.last_hit = None
                            self.current_direction = None
                    
                    # If there was not a hit, check if the last hit was not sunk yet
                    #   if not, reverse the direction
                    else:
                        if not game.get_current_board().did_ship_sink(game.get_current_board().get_at(*self.last_hit)):
                            self.current_direction = (
                                -self.current_direction[0],
                                -self.current_direction[1]
                            )
                
                # The current direction does not exist, try finding adjacent spots
                else:

                    # Find all adjacent spots around the chosen spot and add the
                    #   directions to tried_directions wherever the AI has already gone previously
                    for temp_dir in DIRECTIONS:
                        temp_chosen = (
                            1 if str(temp_dir) == DOWN else (-1 if str(temp_dir) == UP else 0),
                            1 if str(temp_dir) == RIGHT else (-1 if str(temp_dir) == LEFT else 0)
                        )
                        temp_row = row + temp_chosen[0]
                        temp_column = column + temp_chosen[1]

                        # Check if the temp_row, temp_column exceed the boards size, add them to the tried directions
                        if temp_row < 0 or temp_row >= game.get_current_board().height or temp_column < 0 or temp_column >= game.get_current_board().width:
                            self.tried_directions.append(temp_dir)
                        
                        # Check if the temp_row, temp_column has already been made
                        if (temp_row, temp_column) in game.get_current_board().shots and temp_dir not in self.tried_directions:
                            self.tried_directions.append(temp_dir)
                    
                    # While the AI chose a direction that's already been tried, have them continue choosing
                    direction = choice(DIRECTIONS)
                    while direction in self.tried_directions:
                        direction = choice(DIRECTIONS)

                    # The direction has been chosen
                    chosen_direction = (
                        1 if str(direction) == DOWN else (-1 if str(direction) == UP else 0),
                        1 if str(direction) == RIGHT else (-1 if str(direction) == LEFT else 0)
                    )
                    
                    # Attempt to make the hit if the spot is open
                    #   if the spot is not open, continue moving in the current direction
                    #   this will fix itself once an empty spot has been reached
                    #   The AI's next turn will move in the opposite direction
                    row = self.last_hit[0] + chosen_direction[0]
                    column = self.last_hit[1] + chosen_direction[1]
                    while (row, column) in game.get_current_board().shots:
                        row += chosen_direction[0]
                        column += chosen_direction[1]
                    result = game.get_current_board().fire(row, column)

                    # If there was a hit, the current direction has been decided
                    if result == BattleshipBoard.HIT:
                        self.current_direction = chosen_direction
                        self.tried_directions = []
                    
                    # There was no hit, add the direction to the tried directions
                    else:
                        self.tried_directions.append(str(direction))
            
            # There was no last hit or the AI is not smart, make a random hit
            else:

                # Continue generating a random row and column while the chosen row and column have already been taken
                row, column = randint(0, game.get_current_board().height - 1), randint(0, game.get_current_board().width - 1)
                while (row, column) in game.get_current_board().shots:
                    row, column = randint(0, game.get_current_board().height - 1), randint(0, game.get_current_board().width - 1)

                # Check if there was a hit
                result = game.get_current_board().fire(row, column)
                if result == BattleshipBoard.HIT:
                    self.last_hit = row, column
            
            # Sleep for 2 seconds to simulate a decision
            await sleep(2)
            return result
        
        # The player is not an AI, wait for them to choose a place to make a shot
        else:
            row = column = -1

            while True:

                # Wait for the player to react with the column and row they want to go
                def check_reaction(reaction, user):
                    return (
                        reaction.message.id == self.message.id and
                        user.id == self.id and
                        str(reaction) in (BATTLESHIP_REACTIONS + [QUIT])
                    )
                done, pending = await wait([
                    game.bot.wait_for("reaction_add", check = check_reaction),
                    game.bot.wait_for("reaction_remove", check = check_reaction)
                ], return_when = FIRST_COMPLETED)
                reaction, user = done.pop().result()
                for future in pending:
                    future.cancel()

                # Check if the player wants to QUIT the BattleshipGame
                if str(reaction) == QUIT:
                    return BattleshipPlayer.QUIT
                
                # The player does not want to quit, let them choose their row and column
                else:
                    
                    # Check if the player needs to choose a column
                    if column == -1:
                        column = BATTLESHIP_REACTIONS.index(str(reaction))
                    else:
                        row = BATTLESHIP_REACTIONS.index(str(reaction))
                    
                        # Make sure this move is legal
                        if (row, column) not in game.get_current_board().shots:
                            break
                        
                        # The move is not legal
                        else:
                            row = column = -1
                            await self.member.send(
                                embed = get_error_message("You've already gone there! Choose a new place."),
                                delete_after = 5
                            )
            
            # Make the players requested shot
            return game.get_current_board().fire(row, column)
    
    async def show_board(self, game):
        """Shows the opposite player's board depending on who is the current player. 
        If the current player is this player, it will show the opponents board
        If the current player is the opposite player, it will show this player's board

        Parameters
        ----------
            game : BattleshipGame
                The game object that this player is connected to
        """

        # Check if this player is a real player
        if not self.is_ai:

            # Create the embed to send to the player
            embed = Embed(
                title = "{} Turn!".format(
                    "{}'s".format(
                        game.get_current_player().get_name()
                    ) if game.get_current_player().id != self.id else "Your"
                ),
                description = game.get_current_board().display(
                    self.id != game.get_current_player().id
                ),
                colour = await get_embed_color(self.member)
            ).set_footer(
                text = "❕❕ React with your chosen column first and then the row ❕❕" if game.get_current_player().id == self.id else ""
            )

            # Create a new message and add the reactions if necessary
            #   only add the reactions if message was just created
            if self.message is None:
                self.message = await self.member.send(embed = embed)
                for emoji in BATTLESHIP_REACTIONS:
                    await self.message.add_reaction(emoji)
            
            # Update the message
            else:
                await self.message.edit(embed = embed)
    
    async def show_results(self, game, did_hit):
        """Shows the results of the current turn by updating this player's message

        Parameters
        ----------
            game : BattleshipGame
                The game object that this player is connected to
            did_hit : boolean
                Whether or not the current player hit one of the the opposite player's ships
        """

        # Check if this player is a real player
        if not self.is_ai:
            await self.message.edit(embed = Embed(
                title = "{} {}!".format(
                    "You" if game.get_current_player().id == self.id else game.get_current_player().get_name(),
                    "made a hit" if did_hit else "missed"
                ),
                description = game.get_current_board().display(
                    self.id != game.get_current_player().id
                ),
                colour = await get_embed_color(self.member)
            ))
        
    async def show_winner(self, game, winner):
        """Shows the winner of the Battleship game to this player

        Parameters
        ----------
            winner : BattleshipPlayer
                The winner of the current Battleship game
        """
        
        # Check if the player is a real player
        if not self.is_ai:
            await self.message.delete()
            await self.member.send(
                embed = Embed(
                    title = "{} Won!".format(
                        "You" if winner.id == self.id else winner.get_name()
                    ),
                    description = "**_Your board_**\n{}".format(
                        self.board.display(True)
                    ),
                    colour = await get_embed_color(self.member)
                )
            )
            opponent = game.opponent if game.opponent.id != self.id else game.challenger
            await self.member.send(
                embed = Embed(
                    title = " ",
                    description = "**_{}'s board_**\n{}".format(
                        opponent.get_name(),
                        opponent.board.display(True)
                    ),
                    colour = PRIMARY_EMBED_COLOR if opponent.is_ai else await get_embed_color(opponent.member)
                )
            )