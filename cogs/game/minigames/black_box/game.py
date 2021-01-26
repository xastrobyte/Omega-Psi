from discord import Embed
from random import randint

from cogs.errors import get_error_message
from cogs.game.minigames.base_game.game import Game
from cogs.game.minigames.black_box.variables import NUMBERS, SYMBOLS, LEFT, RIGHT, UP, DOWN, GUESS, DIRECT, FINALIZE, HIT, MISS
from cogs.game.minigames.functions import wait_for_reaction

from util.database.database import database
from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

dir_to_initial = {
    LEFT: "right",
    RIGHT: "left",
    UP: "bottom",
    DOWN: "top"
}

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class BlackBoxGame(Game):
    """A BlackBoxGame contains information about a game of
    Black Box being played
    """
    def __init__(self, bot, ctx, challenger):
        super().__init__(
            bot, ctx,
            challenger = challenger,
            opponent = challenger
        )
        self.current_player = 0
        self.locations = []
        invalid_locations = []
        for locations in range(4):
            location = (randint(0, 7), randint(0, 7))
            while location in invalid_locations:
                location = (randint(0, 7), randint(0, 7))
            self.locations.append(location)
            for r_off in range(-1, 2):
                for c_off in range(-1, 2):
                    if (location[0] + c_off >= 0 and location[1] + r_off >= 0 and 
                            location[0] + c_off < 8 and location[1] + r_off < 8):
                        invalid_locations.append((location[0] + c_off, location[0] + r_off))
        self.message = None
        self.guesses = {
            "left": [ None ] * 8,
            "right": [ None ] * 8,
            "top": [ None ] * 8,
            "bottom": [ None ] * 8
        }
        self.amt_guesses = 0
        self.location_guesses = []
        print(self.locations)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_black_box(self, *, show_atoms=False) -> str:
        """Turns the black box into emojis to present inside
        a Discord Embed object

        :param show_atoms: Whether or not to actually show the atoms in the black box string
        """

        # Add the top layer of column emojis
        grid = ":black_large_square: "
        for column in range(8):
            if self.guesses["top"][column] is not None:
                grid += self.guesses["top"][column] + " "
            else:
                grid += NUMBERS[column] + " "
        grid += ":black_large_square:\n"

        # Add each row of the black box
        for row in range(8):

            # Add the left column of row emojis
            if self.guesses["left"][row] is not None:
                grid += self.guesses["left"][row] + " "
            else:
                grid += NUMBERS[row] + " "

            for col in range(8):

                # If we want to show the atoms (at the end of the game)
                #   we choose specific circles for the following:
                #       actual location of atoms: blue circle
                #       correct location of atom: green circle
                #       incorrect location of atom: red circle
                if show_atoms:
                    if (col, row) in self.locations and (col, row) in self.location_guesses:
                        grid += ":green_circle: "
                    elif (col, row) in self.locations:
                        grid += ":blue_circle: "
                    elif (col, row) in self.location_guesses:
                        grid += ":red_circle: "
                    else:
                        grid += ":black_large_square: "
                
                # However, if we are not showing the atoms, just show white squares
                #  for where the guesses are and black squares for other squares
                else:
                    if (col, row) in self.location_guesses:
                        grid += ":white_large_square: "
                    else:
                        grid += ":black_large_square: "
            
            # Add the right column of row emojis
            if self.guesses["right"][row] is not None:
                grid += self.guesses["right"][row] + "\n"
            else:
                grid += NUMBERS[row] + "\n"

        # Add the bottom layer of column emojis
        grid += ":black_large_square: "
        for column in range(8):
            if self.guesses["bottom"][column] is not None:
                grid += self.guesses["bottom"][column] + " "
            else:
                grid += NUMBERS[column] + " "
        grid += ":black_large_square: \n"
        return grid
    
    def direct_laser(self, direction, offset):
        """Directs a laser through the black box

        :param direction: The direction to move the laser in
        :param offset: The row or column to move the laser through
        """

        # Start off at the block on the proper side
        #   and create the movement tuple
        if direction == "left":
            movement = [-1, 0]
            current = initial = (7, offset)
            initial_side = "right"

        elif direction == "right":
            movement = [1, 0]
            current = initial = (0, offset)
            initial_side = "left"

        elif direction == "up":
            movement = [0, -1]
            current = initial = (offset, 7)
            initial_side = "bottom"

        elif direction == "down":
            movement = [0, 1]
            current = initial = (offset, 0)
            initial_side = "top"
        
        # Continue looping until the laser either hits an atom
        #   or leaves the black box
        blocks_processed = 0
        while True:
            
            # Check if the current location is an atom
            if current in self.locations:
                self.guesses[initial_side][offset] = HIT
                break
            
            # Test all the boxes in the corners of the current block:
            #   upper left, upper right, lower left, lower right
            #   tuple is (column, row)
            ul_block = (current[0] - 1, current[1] - 1)
            ur_block = (current[0] + 1, current[1] - 1)
            ll_block = (current[0] - 1, current[1] + 1)
            lr_block = (current[0] + 1, current[1] + 1)
            if blocks_processed == 0:
                if direction in ["left", "right"]:
                    up_block = (current[0], current[1] - 1)
                    lo_block = (current[0], current[1] + 1)
                else:
                    ri_block = (current[0] + 1, current[1])
                    le_block = (current[0] - 1, current[1])

            # Check the first blocks depending on if this is the first block processed
            #   if so, the laser bounces back to the input
            if blocks_processed == 0:
                if direction in ["left", "right"] and (up_block in self.locations or lo_block in self.locations):
                    movement[0] = -movement[0]
                elif direction in ["up", "down"] and (ri_block in self.locations or le_block in self.locations):
                    movement[1] = -movement[1]
            
            # Check the corner blocks even if on the first block
            if movement[0] != 0:
                u_block = ul_block if movement[0] == -1 else ur_block
                l_block = ll_block if movement[0] == -1 else lr_block

                if u_block in self.locations and l_block in self.locations:
                    movement[0] = -movement[0]
                elif u_block in self.locations:
                    movement = [0, 1]
                elif l_block in self.locations:
                    movement = [0, -1]
            else:
                l_block = ul_block if movement[1] == -1 else ll_block
                r_block = ur_block if movement[1] == -1 else lr_block

                if l_block in self.locations and r_block in self.locations:
                    movement[1] = -movement[1]
                elif l_block in self.locations:
                    movement = [1, 0]
                elif r_block in self.locations:
                    movement = [-1, 0]
            
            # Check if the next movement will leave the black box
            if ((current[0] + movement[0]) >= 8 or (current[0] + movement[0]) < 0 or 
                    (current[1] + movement[1]) >= 8 or (current[1] + movement[1]) < 0):
                if current == initial:
                    self.guesses[initial_side][offset] = MISS
                else:
                    self.guesses[initial_side][offset] = SYMBOLS[self.amt_guesses]
                    if current[0] == 0 and movement[0] == -1:
                        self.guesses["left"][current[1]] = SYMBOLS[self.amt_guesses]
                    elif current[0] == 7 and movement[0] == 1:
                        self.guesses["right"][current[1]] = SYMBOLS[self.amt_guesses]
                    elif current[1] == 0 and movement[1] == -1:
                        self.guesses["top"][current[0]] = SYMBOLS[self.amt_guesses]
                    elif current[1] == 7 and movement[1] == 1:
                        self.guesses["bottom"][current[0]] = SYMBOLS[self.amt_guesses]
                    self.amt_guesses += 1
                break
            current = (current[0] + movement[0], current[1] + movement[1])
            blocks_processed += 1

    async def play(self):
        """Allows the player to play a game of Black Box"""

        # Continue looping until the player finishes their game
        while True:
            self.message = await self.ctx.send(
                embed = Embed(
                    title = "Black Box",
                    description = "{}\n\n{}\n{}\n{}".format(
                        self.get_black_box(),
                        "To make a guess, react with {}".format(GUESS),
                        "To direct a \"laser\", react with {}".format(DIRECT),
                        "To finalize your guesses, react with {}".format(FINALIZE)
                    ),
                    color = await get_embed_color(self.challenger)
                ).add_field(
                    name = "Symbol Meanings",
                    value = (
                        """
                        {} This symbol means that you hit an atom
                        {} This symbol means that the laser you directed came back to the same spot
                        Any other symbol means that the directed laser went in through one spot
                        and came out at the matching symbol's spot
                        """
                    ).format(HIT, MISS)
                ))
            for reaction in [GUESS, DIRECT, FINALIZE]:
                await self.message.add_reaction(reaction)

            # Ask the player if they want to make a guess or direct a "laser" (or finalize their guesses)
            option = await wait_for_reaction(
                self.bot, self.message,
                self.challenger, [GUESS, DIRECT, FINALIZE])
            await self.message.clear_reactions()
            
            if option == GUESS:
                await self.make_location_guess()
            elif option == DIRECT:
                await self.make_input_guess()
            else:
                if await self.finalize_guesses():
                    break

    async def make_location_guess(self):
        """Allows the player to make a guess on where an atom may be"""

        # Check if 4 guesses have been made
        #   if so, don't try asking for any more guesses
        if len(self.location_guesses) == 4:
            await self.ctx.send(embed = get_error_message(
                "You have already made 4 guesses. Remove one to make another!"
            ))
        else:
            await self.message.edit(
                embed = Embed(
                    title = "Black Box",
                    description = "{0}\n\n{1} {2}\n{1} {3}".format(
                        self.get_black_box(), GUESS,
                        "To place a guess, react with the column first and then the row",
                        "To remove a guess, react with the same column and row as it is in"
                    ),
                    colour = await get_embed_color(self.challenger)
                ).add_field(
                    name = "Symbol Meanings",
                    value = (
                        """
                        {} This symbol means that you hit an atom
                        {} This symbol means that the laser you directed came back to the same spot
                        Any other symbol means that the directed laser went in through one spot
                        and came out at the matching symbol's spot
                        """
                    ).format(HIT, MISS)
                ))
            for number in NUMBERS:
                await self.message.add_reaction(number)
            column = await wait_for_reaction(
                self.bot, self.message, 
                self.challenger, NUMBERS)
            row = await wait_for_reaction(
                self.bot, self.message, 
                self.challenger, NUMBERS)
            column = NUMBERS.index(column)
            row = NUMBERS.index(row)

            if (column, row) in self.location_guesses:
                self.location_guesses.remove((column, row))
            else:
                self.location_guesses.append((column, row))
    
    async def make_input_guess(self):
        """Allows the player to make a guess on the sides of the black box"""
        
        # Get the direction the user wants to move input through
        #   and which row or column they want to move input through
        await self.message.edit(
            embed = Embed(
                title = "Black Box",
                description = "{}\n\n{}{}".format(
                    self.get_black_box(), DIRECT,
                    "Choose a direction to push input through using the directional arrows"
                ),
                colour = await get_embed_color(self.challenger)
            ).add_field(
                name = "Symbol Meanings",
                value = (
                    """
                    {} This symbol means that you hit an atom
                    {} This symbol means that the laser you directed came back to the same spot
                    Any other symbol means that the directed laser went in through one spot
                    and came out at the matching symbol's spot
                    """
                ).format(HIT, MISS)
            ))
        
        # Create a new list of valid direction reactions the user
        #   can react with
        # Then add the reactions to the message and have the user
        #   select which direction they want to move in
        directions = []
        for direction in [LEFT, RIGHT, UP, DOWN]:
            if not all(self.guesses[dir_to_initial[direction]]):
                directions.append(direction)
        for direction in directions:
            await self.message.add_reaction(direction)
        direction = await wait_for_reaction(
            self.bot, self.message,
            self.challenger, directions)
        direction = {LEFT: "left", RIGHT: "right", UP: "up", DOWN: "down"}[direction]

        # Ask the user which row or column to push a laser through
        await self.message.clear_reactions()
        await self.message.edit(
            embed = Embed(
                title = "Black Box",
                description = "{}\n\n{}{}".format(
                    self.get_black_box(), DIRECT,
                    "Choose which {} to push the input through".format(
                        "row" if direction in ["left", "right"] else "column"
                    )
                ),
                colour = await get_embed_color(self.challenger)
            ).add_field(
                name = "Symbol Meanings",
                value = (
                    """
                    {} This symbol means that you hit an atom
                    {} This symbol means that the laser you directed came back to the same spot
                    Any other symbol means that the directed laser went in through one spot
                    and came out at the matching symbol's spot
                    """
                ).format(HIT, MISS)
            ))

        # Create a new list of valid number reactions the user
        #   can react with
        # Then add the reactions to the message and have the user
        #   select which row or column they want to push a laser through
        numbers = []
        for i in range(len(NUMBERS)):
            if ((direction == "left" and self.guesses["right"][i] is None) or
                    (direction == "right" and self.guesses["left"][i] is None) or
                    (direction == "up" and self.guesses["bottom"][i] is None) or
                    (direction == "down" and self.guesses["top"][i] is None)):

                numbers.append(NUMBERS[i])
        for number in numbers:
            await self.message.add_reaction(number)
        offset = await wait_for_reaction(
            self.bot, self.message,
            self.challenger, numbers)
        offset = NUMBERS.index(offset)
        await self.message.clear_reactions()
        self.direct_laser(direction, offset)  # Direct the laser through the black box
    
    async def finalize_guesses(self):
        """Finalizes the guesses of the player and determines if they won or lost
        In order for the player to win, they must get at least 3 of the spots correct
        """

        if len(self.location_guesses) != 4:
            await self.ctx.send(embed = get_error_message(
                "You need to place at least {} more guess{}!".format(
                    4 - len(self.location_guesses),
                    "" if len(self.location_guesses) == 3 else "es"
                )
            ))
            return False
        else:
            correct = 0
            for location in self.locations:
                if location in self.location_guesses:
                    correct += 1
            
            embed = Embed(
                title = "You Won!" if correct >= 3 else "You Lost :(",
                description = self.get_black_box(show_atoms = True),
                colour = await get_embed_color(self.challenger))
            
            await self.message.edit(embed = embed)
            await database.users.update_black_box(self.challenger, correct >= 3)
            return True
