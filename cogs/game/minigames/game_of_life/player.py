from asyncio import sleep
from discord import Embed
from math import ceil
from random import randint, choice

from cogs.globals import PRIMARY_EMBED_COLOR, NUMBER_EMOJIS, LEAVE

from cogs.game.minigames.base_game.player import Player

from cogs.game.minigames.game_of_life.functions import choose_house
from cogs.game.minigames.game_of_life.variables import (
    MARRIED, GRADUATION, BRIEFCASE, SPIN, BABY, FAMILY, RISKY_ROAD, RETIRED, GIFTS,
    BUY_HOUSE, SELL_HOUSE, DO_NOTHING, HOUSE, LOANS,
    PAYDAY, GET_MONEY, PAY_MONEY, ACTION, PAYDAY_BONUS
)

from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class GameOfLifePlayer(Player):
    """A GameOfLifePlayer object holds information regarding a player in the Game of Life minigame.

    :param member: The discord.Member defining this GameOfLifePlayer object or
        a str clarifying this GameOfLifePlayer object as an AI player
    """

    def __init__(self, member):
        super().__init__(member = member)

        # Game player data
        self.is_married = False
        self.is_retired = False
        self.is_college = False
        self.move_modify = False
        self.extra_turn = False

        # Other player data
        self.space = "c0"
        self.babies = 0
        self.pets = 1
        self.cash = 200000
        self.career = None
        self.action_cards = 0
        self.house_cards = []
        self.pet_cards = 0
        self.loans = 0
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Getter
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @property
    def member(self):
        return self.__member
    
    @property
    def is_ai(self):
        return self.__is_ai
    
    # # # # # # # # # # # # # # # # # # # #
    
    @property
    def is_married(self):
        return self.__is_married
    
    @property
    def is_retired(self):
        return self.__is_retired
    
    @property
    def is_college(self):
        return self.__is_college
    
    @property
    def move_modify(self):
        return self.__move_modify
    
    @property
    def extra_turn(self):
        return self.__extra_turn

    # # # # # # # # # # # # # # # # # # # #

    @property
    def space(self):
        return self.__space

    @property
    def babies(self):
        return self.__babies
    
    @property
    def pets(self):
        return self.__pets

    @property
    def cash(self):
        return self.__cash
    
    @property
    def career(self):
        return self.__career
    
    @property
    def action_cards(self):
        return self.__action_cards
    
    @property
    def house_cards(self):
        return self.__house_cards
    
    @property
    def pet_cards(self):
        return self.__pet_cards
    
    @property
    def loans(self):
        return self.__loans

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Setter
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @member.setter
    def member(self, member):
        self.__member = member
    
    @is_ai.setter
    def is_ai(self, is_ai):
        self.__is_ai = is_ai
    
    # # # # # # # # # # # # # # # # # # # #

    @is_married.setter
    def is_married(self, is_married):
        self.__is_married = is_married
    
    @is_retired.setter
    def is_retired(self, is_retired):
        self.__is_retired = is_retired
    
    @is_college.setter
    def is_college(self, is_college):
        self.__is_college = is_college
    
    @move_modify.setter
    def move_modify(self, move_modify):
        self.__move_modify = move_modify
    
    @extra_turn.setter
    def extra_turn(self, extra_turn):
        self.__extra_turn = extra_turn
    
    # # # # # # # # # # # # # # # # # # # #

    @space.setter
    def space(self, space):
        self.__space = space

    @babies.setter
    def babies(self, babies):
        self.__babies = babies
    
    @pets.setter
    def pets(self, pets):
        self.__pets = pets
    
    @cash.setter
    def cash(self, cash):
        self.__cash = cash
    
    @career.setter
    def career(self, career):
        self.__career = career
    
    @action_cards.setter
    def action_cards(self, action_cards):
        self.__action_cards = action_cards
    
    @house_cards.setter
    def house_cards(self, house_cards):
        self.__house_cards = house_cards
    
    @pet_cards.setter
    def pet_cards(self, pet_cards):
        self.__pet_cards = pet_cards
    
    @loans.setter
    def loans(self, loans):
        self.__loans = loans

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Play Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def setup(self, game):
        """Let's the player decide if they are going to college or choosing a career.

        :param game: The game object that this player is connected to
        """

        # Check if the player is an AI and simulate a decision
        if self.is_ai:
            await sleep(2)
            college = randint(1, 10) % 2 == 0
        
        # The player is a real person
        else:

            # Ask the player if they want to go to college or into a career
            college = False
            message = await game.ctx.send(
                self.member.mention,
                embed = Embed(
                    title = "College or Career?",
                    description = "If you want to go to college, react with {}\nIf you want to go straight into a career, react with {}".format(
                        GRADUATION, BRIEFCASE
                    ),
                    colour = await get_embed_color(self.member)
                )
            )
            await message.add_reaction(GRADUATION)
            await message.add_reaction(BRIEFCASE)

            # Check for the user's reaction
            def check_reaction(reaction, user):
                return (
                    reaction.message.id == message.id and
                    str(reaction) in [GRADUATION, BRIEFCASE] and
                    user.id == self.member.id
                )
            reaction, user = await game.bot.wait_for("reaction_add", check = check_reaction)
            college = str(reaction) == GRADUATION
        
        # Check if the user is going to college
        if college:

            # Take 100k from the user, set their college attribute to True
            #   and send a message saying they are going to college
            self.cash -= 100000
            self.is_college = True
            self.space = "c0"
            await game.ctx.send(
                embed = Embed(
                    title = "{} is going to college!".format(
                        self.get_name()
                    ),
                    description = "{} has to pay $100,000 for tuition fees".format(
                        self.get_name()
                    ),
                    colour = PRIMARY_EMBED_COLOR if self.is_ai else await get_embed_color(self.member)
                )
            )
        
        # Check if the user is going into a career
        #   have them decide and then display their career
        else:
            self.space = "j0"
            self.career = await self.ask_for_career(game)
            await game.ctx.send(
                embed = Embed(
                    title = "{} chose a career!".format(self.get_name()),
                    description = str(self.career),
                    colour = PRIMARY_EMBED_COLOR if self.is_ai else await get_embed_color(self.member)
                )
            )
    
    async def process_turn(self, game):
        """Processes the current turn for this player by waiting until they
        react to make their move or, if this player is an AI, choosing the best place
        to go

        :param game: The game object that this player is connected to
        """

        # Check if the player has an extra turn, remove it
        self.extra_turn = False
        
        # Ask the player to spin
        number = await self.ask_for_spin(game, allow_leave = True)

        # Check if the player is leaving
        if number == LEAVE:
            await game.add_action("{} left the game!".format(self.get_name()))
            return LEAVE
        
        # Add the number they spun to the current turn
        await game.add_action(
            "{} {} spun a {}!".format(
                SPIN, self.get_name(),
                number
            )
        )

        # The player is not leaving, check if there is a bonus paid to any player
        await game.pay_bonus(number)

        # Check what spot the player has landed on
        board_space = self.next_space(game, number)
        self.space = board_space.current

        # Check if the player got any paydays
        if board_space.paydays_passed > 0:
            await game.add_action(
                "{} {} got {} payday{}!".format(
                    PAYDAY,
                    self.get_name(), board_space.paydays_passed,
                    "s" if board_space.paydays_passed > 1 else ""
                )
            )
        
        # Check if the space is a pet space
        if board_space.type == "pet":
            await self.process_pet_space(game)

        # Check if the space is an action space
        elif board_space.type == "action":
            await game.process_action_card(board_space)

        # Check if the space is a house space
        elif board_space.type == "house":
            await self.ask_for_house(game)

        # Check if the space is a spin-to-win space
        elif board_space.type == "spin_to_win":
            await game.spin_to_win()

        # Check if the space is a stop space
        elif board_space.stop:
            await self.process_stop_space(game, board_space)

        # Check if the space is a baby space
        elif board_space.type in ["baby", "twins", "triplets"]:
            await self.process_baby_space(game, board_space)

        # Check if the user has to pay money or receive money
        elif board_space.type == "pay_money":
            self.cash -= board_space.amount
            await game.add_action(
                "{} {} has to pay ${:0,}!".format(
                    PAY_MONEY,
                    self.get_name(), board_space.amount
                )
            )
        
        elif board_space.type == "get_money":
            self.cash += board_space.amount
            await game.add_action(
                "{} {} gets paid ${:0,}!".format(
                    GET_MONEY,
                    self.get_name(), board_space.amount
                )
            )

        # Check if the player landed on a payday space
        elif board_space.type == "payday":
            self.cash += 100000
            await game.add_action(
                "{} {} landed on a payday and got a $100,000 bonus!".format(
                    PAYDAY_BONUS, self.get_name()
                )
            )

        # Sleep for 3 seconds so everyone can read what happened
        await sleep(3)
        return False
    
    async def ask_for_spin(self, game, *, is_color = False, allow_leave = False):
        """Let's the player spin for a number or a color
        If getting color, when this: returns True, the color is black
                                     returns False, the color is red

        :param game: The game object this player is connected to
        :param is_color: Whether or not to get the color of the result or just a number. (Defaults to False)
        :param allow_leave: Whether or not to allow the player to leave during this spin. (Defaults to False)
        
        :returns: The resulting number or whether the color is black or red
        """

        # Check if the player is an AI, simulate waiting to spin
        if self.is_ai:
            await sleep(2)
        
        # The player is a real person, wait for their reaction to spin
        else:

            # Send the message and add the valid reactions
            message = await game.ctx.send(
                embed = Embed(
                    title = "Spin!",
                    description = "{}, react with {} when you're ready to spin.{}".format(
                        self.get_name(), SPIN,
                        "\nIf you'd like to leave, react with {}".format(
                            LEAVE
                        ) if allow_leave else ""
                    ),
                    colour = await get_embed_color(self.member)
                )
            )
            await message.add_reaction(SPIN)
            if allow_leave:
                await message.add_reaction(LEAVE)

            # Wait for the user's reaction
            def check_reaction(reaction, user):
                return (
                    reaction.message.id == message.id and
                    user.id == self.member.id and
                    str(reaction) in (
                        [SPIN, LEAVE] if allow_leave else [SPIN]
                    )
                )
            reaction, user = await game.bot.wait_for("reaction_add", check = check_reaction)
            await message.delete()

            # Check if the player is leaving
            if str(reaction) == LEAVE:
                return LEAVE
            
        # Choose a random number
        number = None
        for value in range(randint(1, 10)):
            number = randint(1, 10)
        is_black = number % 2 == 0

        # Check if returning color or number
        if is_color:
            return is_black
        return number
    
    async def ask_for_career(self, game, *, new_career = False):
        """Let's the player choose their career given two cards

        :param game: The game object this player is connected to
        :param new_career: Whether the player is choosing between their current
            career and a new one or choosing between two new careers
        
        :returns: The career the player chose
        :rtype: CareerCard
        """

        # Set the target deck of career cards depending on whether or not
        #   this player is a college player
        career_cards = game.career_cards if not self.is_college else game.college_career_cards

        # If choosing between two new careers, choose two random careers from the deck
        # and have them decide
        if not new_career:
            career_one = career_cards.pop(randint(0, len(career_cards) - 1))
            career_two = career_cards.pop(randint(0, len(career_cards) - 1))
        
        # The player is choosing between their current career and a new one
        else:
            career_one = self.career
            career_two = career_cards.pop(randint(0, len(career_cards) - 1))
        
        # Check if the player is an AI, simulate a decision
        if self.is_ai:
            await sleep(2)
            return career_one if randint(1, 10) % 2 == 0 else career_two
        
        # The player is a real person, have them decide
        else:
            await game.ctx.send(
                embed = Embed(
                    title = "Choose a Career!",
                    description = "Check your DMs for your career choices!",
                    colour = await get_embed_color(self.member)
                ),
                delete_after = 5
            )

            message = await self.member.send(
                embed = Embed(
                    title = "Choose a Career!",
                    description = "_ _",
                    colour = await get_embed_color(self.member)
                ).add_field(
                    name = NUMBER_EMOJIS[0],
                    value = str(career_one),
                    inline = False
                ).add_field(
                    name = NUMBER_EMOJIS[1],
                    value = str(career_two),
                    inline = False
                )
            )
            await message.add_reaction(NUMBER_EMOJIS[0])
            await message.add_reaction(NUMBER_EMOJIS[1])

            # Wait for the user to decide which card they want
            def check_reaction(reaction, user):
                return (
                    reaction.message.id == message.id and
                    user.id == self.member.id and
                    str(reaction) in NUMBER_EMOJIS[ : 2]
                )
            reaction, user = await game.bot.wait_for("reaction_add", check = check_reaction)
            if str(reaction) == NUMBER_EMOJIS[0]:
                return career_one
            return career_two
        
    async def ask_for_house(self, game, *, sell_house = False, house = None):
        """Let's the player decide if they want to buy a house, sell a house, or do nothing

        :param game: The game that this player is connected to
        :param sell_house: Whether or not to directly sell a player's house
            Note that this is primarily used when finalizing the end of a game
        :param house: The specific house to sell
            Note that this is primarily used when finalizing the end of a game
        
        :rtype: int
        """

        # Only ask the player what they want to do if not directly selling a house
        action = None if not sell_house else "sell"
        if not sell_house:

            # Check if the player is an AI, simulate deciding on an action
            if self.is_ai:
                actions = ["buy", "sell", "nothing"]
                action = choice(actions)
                while action == "sell" and len(self.house_cards) == 0:
                    action = choice(actions)
                await sleep(2)
            
            # The player is a real person, ask them what they want to do
            else:

                # Send a message asking them what they want to do and add
                #   the necessary reactions
                message = await game.ctx.send(
                    embed = Embed(
                        title = "Buy, Sell, or do nothing?",
                        description = "{}{}{}".format(
                            "If you want to buy a house, react with {}\n".format(BUY_HOUSE),
                            "If you want to sell a house, react with {}\n".format(SELL_HOUSE) if len(self.house_cards) > 0 else "",
                            "If you want to do nothing, react with {}".format(DO_NOTHING)
                        ),
                        colour = await get_embed_color(self.member)
                    )
                )
                await message.add_reaction(BUY_HOUSE)
                if len(self.house_cards) > 0:
                    await message.add_reaction(SELL_HOUSE)
                await message.add_reaction(DO_NOTHING)

                # Wait for the player to react
                def check_reaction(reaction, user):
                    return (
                        reaction.message.id == message.id and
                        user.id == self.member.id and
                        str(reaction) in (
                            [BUY_HOUSE, SELL_HOUSE, DO_NOTHING]
                            if len(self.house_cards) > 0 else
                            [BUY_HOUSE, DO_NOTHING]
                        )
                    )
                reaction, user = await game.bot.wait_for("reaction_add", check = check_reaction)
                if str(reaction) == BUY_HOUSE:
                    action = "buy"
                elif str(reaction) == SELL_HOUSE:
                    action = "sell"
                else:
                    action = "nothing"
                await message.delete()
            
        # The player will buy a house
        if action == "buy":
            
            # Keep track of how many loans need to be taken
            #   the chosen house
            #   and the houses to choose from
            take_loans = False
            chosen_house = None
            house_cards = game.house_cards
            house_one = house_cards.pop(0)
            house_two = house_cards.pop(0)

            # Check if the player is an AI, choose a house intelligently and simulate a decision
            if self.is_ai:
                chosen_house = choose_house(self, house_one = house_one, house_two = house_two)
                take_loans = chosen_house != None
            
            # The player is a real person, have them choose a house if they want to
            else:
                message = await self.member.send(
                    embed = Embed(
                        title = "Choose a house!",
                        description = "_ _",
                        colour = await get_embed_color(self.member)
                    ).add_field(
                        name = NUMBER_EMOJIS[0],
                        value = str(house_one),
                        inline = False
                    ).add_field(
                        name = NUMBER_EMOJIS[1],
                        value = str(house_two),
                        inline = False
                    )
                )
                await message.add_reaction(NUMBER_EMOJIS[0])
                await message.add_reaction(NUMBER_EMOJIS[1])

                # Wait for the player to decide which house they want
                reaction, user = await game.bot.wait_for("reaction_add", check = lambda reaction, user: (
                    reaction.message.id == message.id and
                    user.id == self.member.id and
                    str(reaction) in NUMBER_EMOJIS[ : 2]
                ))

                # The player chose the first house
                if str(reaction) == NUMBER_EMOJIS[0]:
                    chosen_house = house_one
                
                # The player chose the second house
                elif str(reaction) == NUMBER_EMOJIS[1]:
                    chosen_house = house_two
                await message.delete()

                # Check if the player can buy the house without loans
                #   add the other house back to the deck
                if chosen_house.purchase <= self.cash:
                    if str(reaction) == NUMBER_EMOJIS[0]:
                        house_cards.append(house_two)
                    else:
                        house_cards.append(house_one)
                    take_loans = True
                
                # The player has to take out loans for their chosen house
                #   ask them if they still want to buy the house
                else:

                    # Send a message asking the player what they want to do
                    #   and add the reactions
                    take_loans = await self.ask_for_split_path(
                        game,
                        title = "Loans Needed",
                        description = (
                            """
                            In order to buy that house, you need to take out some loans.
                            If you want to take loans out, react with {}.
                            If you want to cancel buying the house, react with {}.
                            """
                        ),
                        true_path = LOANS, false_path = LEAVE
                    )
            
            # The player wants to buy the house, check if they need to take out loans
            if take_loans:
                loans_needed = ceil((chosen_house.purchase - self.cash) / 50000)
                if loans_needed > 0:
                    self.loans += loans_needed
                    self.cash += 50000 * loans_needed
                
                # Take cash from the player to purchase the house
                self.cash -= chosen_house.purchase
                self.house_cards.append(chosen_house)
                await game.add_action(
                    "{} {} bought a new house{}!\n{}".format(
                        HOUSE, self.get_name(),
                        " after taking out some loans" if loans_needed > 0 else "",
                        str(chosen_house)
                    )
                )
            
            # The player does not want to take out loans
            else:
                house_cards.append(house_one)
                house_cards.append(house_two)
                await game.add_action(
                    "{} {} did not want to take any loans! They will not buy the house.".format(
                        ACTION, self.get_name()
                    )
                )
        
        # The player will sell a house
        elif action == "sell":

            # Update the turn message
            await game.add_action(
                "{} {} is selling a house!".format(
                    HOUSE, self.get_name()
                )
            )

            # Only ask the player to choose a house if a house has not been specified
            #   to sell directly
            chosen_house = house
            if not sell_house:

                # Check if the player is an AI
                #   decide on what house to sell and sleep for 2 seconds to simulate the decision
                if self.is_ai:
                    chosen_house = choose_house(self, buy = False)
                    self.house_cards.remove(chosen_house)
                
                # The player is a real person, have them decide on the house
                else:

                    # Create the embed to ask for which house to sell
                    #   and add number fields for each house the player has
                    embed = Embed(
                        title = "Choose a house to sell!",
                        description = "_ _",
                        colour = await get_embed_color(self.member)
                    )
                    for index in range(len(self.house_cards)):
                        house = self.house_cards[index]
                        embed.add_field(
                            name = NUMBER_EMOJIS[index],
                            value = str(house),
                            inline = False
                        )
                    
                    # Send the message to ask the player which house to sell
                    #   and add the valid reactions
                    message = await self.member.send(embed = embed)
                    for emoji in NUMBER_EMOJIS[ : len(self.house_cards)]:
                        await message.add_reaction(emoji)
                    
                    # Wait for the user to choose which house to sell and delete the message
                    reaction, user = await game.bot.wait_for("reaction_add", check = lambda reaction, user: (
                        reaction.message.id == message.id and
                        user.id == self.member.id and
                        str(reaction) in NUMBER_EMOJIS[ : len(self.house_cards)]
                    ))
                    await message.delete()
                    chosen_house = self.house_cards.pop(NUMBER_EMOJIS.index(str(reaction)))
            
            # Update the turn message with which house the player is selling
            await game.add_action(
                "{} {} is selling the following house:\n{}".format(
                    HOUSE, self.get_name(), str(chosen_house)
                )
            )

            # Have the player spin to see how much they sell their house for
            is_black = await self.ask_for_spin(game, is_color = True)
            amount = chosen_house.spin_black if is_black else chosen_house.spin_red

            # Update the turn message with how much the house was sold for
            self.cash += amount
            await game.add_action(
                "{} {} sold their house for ${:0,}".format(
                    GET_MONEY, self.get_name(), amount
                )
            )

            # Return the amount that the player sold the house for
            return amount
        
        # The player will do nothing
        else:   
            await game.add_action(
                "{} {} chose not to buy nor sell a house.".format(
                    ACTION,
                    self.get_name()
                )
            )
    
    async def ask_for_opponent(self, game, *, is_lawsuit = False):
        """Asks this player to choose an opponent for a competition or a lawsuit card

        :param game: The game that this player is connected to
        :param is_lawsuit: Whether or not this player is choosing an opponent for
            a lawsuit. (Defaults to False)
        
        :rtype: GameOfLifePlayer
        """

        # Check if the player is an AI
        #   the AI will choose someone with the highest salary
        #   Also sleep for 2 seconds to simulate a decision
        if self.is_ai:
            opponent = max(game.players, key = lambda player: (
                player.career.salary 
                if (player.career and player.id != self.id) 
                else 0
            ))
            while opponent.id == self.id:
                opponent = choice(game.players)
            await sleep(2)
        
        # The player is a real person, ask them who they want to choose
        #   as their opponent
        else:
            
            # Create the embed to ask for the opponent
            embed = Embed(
                title = "Choose an opponent!",
                description = "_ _",
                colour = await get_embed_color(self.member)
            )

            # Add the opponents as fields to choose from
            #   linked to number emojis
            opponents = list(filter(lambda player: self.id != player.id, game.players))
            for index in range(len(opponents)):
                embed.add_field(
                    name = NUMBER_EMOJIS[index],
                    value = opponents[index].get_name(),
                    inline = False
                )
            
            # Send the message to the game's ctx and add the 
            #   number emoji reactions for this player to react to
            #   in order to choose an opponent
            message = await game.ctx.send(embed = embed)
            for emoji in NUMBER_EMOJIS[ : len(opponents)]:
                await message.add_reaction(emoji)
            
            # Wait for the player to react with which opponent they want to choose
            #   and then delete the message
            reaction, user = await game.bot.wait_for("reaction_add", check = lambda reaction, user: (
                reaction.message.id == message.id and
                user.id == self.id and
                str(reaction) in NUMBER_EMOJIS[ : len(opponents)]
            ))
            await message.delete()

            # Get the opponent that they chose 
            opponent = opponents[NUMBER_EMOJIS.index(str(reaction))]
        
        # If this is not for a lawsuit, update the turn message in the game
        if not is_lawsuit:
            await game.add_action(
                "{} {} chose {}!".format(
                    ACTION,
                    self.get_name(), opponent.get_name()
                )
            )
        return opponent
    
    async def ask_for_spot(self, game, message, spots, *, choose_from = 1):
        """Asks the player to choose a spot for their Spin to Win token.

        :param game: The game that this player is connected to
        :param message: The message to use to keep track of people's chosen spots
        :param spots: A dict object that holds data about spots already chosen
            and who chose the spot
        :param choose_from: The amount of spots the player can choose from. (Default is 1)
        """

        # Let the player decide on how many spots to take
        for spot_choice in range(choose_from):

            # Check if this player is an AI, have them choose a random spot after
            #   sleeping for 2 seconds to simulate a decision
            if self.is_ai:
                await sleep(2)
                spot = choice(NUMBER_EMOJIS)
                while str(spot) in spots:
                    spot = choice(NUMBER_EMOJIS)
        
            # The player is a real person, have them decide on a spot as long as it's not taken yet
            else:

                # Create an embed showing the spots already taken
                embed = Embed(
                    title = "Spin to Win!",
                    description = "{}, choose your spot{}!".format(
                        self.get_name(), "s" if choose_from - spot_choice > 1 else ""
                    ),
                    colour = PRIMARY_EMBED_COLOR if game.get_current_player().is_ai else await get_embed_color(game.get_current_player().member)
                ).add_field(
                    name = "Spots Taken",
                    value = "\n".join([
                        "{} - {}".format(
                            str(spot), spots[spot].get_name()
                        )
                        for spot in spots
                    ]) if len(spots) > 0 else "None Taken Yet!",
                    inline = False
                )

                # Edit the message to update the embed
                #   add the reactions, and wait for the player to react
                await message.edit(embed = embed)
                for emoji in NUMBER_EMOJIS:
                    if str(emoji) not in spots:
                        await message.add_reaction(emoji)
                reaction, user = await game.bot.wait_for("reaction_add", check = lambda reaction, user: (
                    reaction.message.id == message.id and
                    user.id == self.id and
                    str(reaction) in NUMBER_EMOJIS and
                    str(reaction) not in spots
                ))
                await message.clear_reactions()

                # Get the player's spot
                spot = str(reaction)
            
            # Add the player's spot to the spots dictionary
            spots[spot] = self
        
        return spots
    
    async def process_pet_space(self, game):
        """Processes the pet space when a player lands on it

        :param game: The game object that this player is connected to
        """
        
        # Pull a card from the game's pet card deck
        card = game.pet_cards.pop(0)
        await game.add_action(str(card))
        self.pet_cards += 1

        # Check if the player is collecting money
        if card.action == "collect":

            # Give the player money and update the turn message
            self.cash += card.amount
            await game.add_action(
                "{} {} collected ${:0,}".format(
                    GET_MONEY,
                    self.get_name(), card.amount
                )
            )
        
        # Check if the player is collecting money for each pet
        elif card.action == "collect_for_each":

            # Give the player money for as many pets as they have
            #   and update the turn message
            total = self.pets * card.amount
            self.cash += total
            await game.add_action(
                "{} {} collected ${:0,}{}!".format(
                    GET_MONEY,
                    self.get_name(), card.amount,
                    " for each pet for a total of ${:0,}".format(total) if total != card.amount else ""
                )
            )
        
        # Check if the player is collecting money from each player
        elif card.action == "collect_from_each":
            
            # Take money from each player that is not this player
            #   and give it to this player
            total = (len(game.players) - 1) * card.amount
            for player in game.players:
                if player.id != self.id:
                    player.cash -= card.amount
            
            # Update the turn message
            await game.add_action(
                "{} {} collected ${:0,}{}!".format(
                    GET_MONEY,
                    self.get_name(), card.amount,
                    " from everyone for a total of ${:0,}".format(total) if total != card.amount else ""
                )
            )
        
        # Check if the player is paying money
        elif card.action == "pay":

            # Take money from the player and update the turn message
            self.cash -= card.amount
            await game.add_action(
                "{} {} had to pay the bank ${:0,}!".format(
                    PAY_MONEY,
                    self.get_name(), card.amount
                )
            )
        
        # Check if the player is paying money for each pet
        elif card.action == "pay_for_each":

            # Take money from the player for each pet they have
            #   and update the turn message
            total = self.pets * card.amount
            self.cash -= total
            await game.add_action(
                "{} {} had to pay the bank ${:0,}{}!".format(
                    PAY_MONEY,
                    self.get_name(), card.amount,
                    " for each pet for a total of ${:0,}".format(total) if total != card.amount else ""
                )
            )
        
        # Check if the player is competing against another player
        elif card.action == "compete":

            # Have two players compete against each other and give the
            #   winning player the amount on this card
            #   then update the turn message
            winner, _ = await game.compete(self)
            winner.cash += card.amount
            await game.add_action(
                "{} {} collected ${:0,} for spinning higher!".format(
                    GET_MONEY,
                    self.get_name(), card.amount
                )
            )
    
    async def process_stop_space(self, game, board_space):
        """Processes the stop space when this player lands on it

        :param game: The game object that this player is connected to
        :param board_space: The board space object where this player is current occupying
        """

        # Check if the player is graduating, ask them to choose a career
        if board_space.type == "graduation":
            self.is_college = True
            self.career = await self.ask_for_career(game)
            await game.add_action(
                "{} {} graduated and chose a career!\n{}".format(
                    GRADUATION,
                    self.get_name(), str(self.career)
                )
            )
        
        # Check if the player is getting married
        elif board_space.type == "married":
            
            # Send a message saying the player got married
            await game.add_action(
                "{} {} got married!\n{}, spin for gifts from everyone!".format(
                    MARRIED, self.get_name(),
                    GIFTS, self.get_name()
                )
            )

            # Ask the player to spin for gifs from everyone (apart from this player)
            #   and have each player give the gift amount
            #   depending on the color
            is_black = await self.ask_for_spin(game, is_color = True)
            amount = 100000 if is_black else 50000
            total = amount * (len(game.players) - 1)
            for player in filter(lambda player: player.id != self.id, game.players):
                player.cash -= amount
            self.cash += total

            # Update the turn message saying how much money the player got in total
            await game.add_action(
                "{} {} collected ${:0,}{}!".format(
                    GET_MONEY,
                    self.get_name(), amount,
                    " from everyone for a total of ${:0,}".format(
                        total
                    ) if total != amount else ""
                )
            )
        
        # Check if the player is spinning for babies
        elif board_space.type == "spin_for_babies":
            
            # Update the turn message saying the player is spinning for babies
            await game.add_action(
                "{} {} is spinning to see if they have any more babies!".format(
                    BABY, self.get_name()
                )
            )

            # Ask the player to spin to see how many babies they get
            #   and update the turn message
            value = await self.ask_for_spin(game)
            self.babies += board_space.spin[str(value)]
            await game.add_action(
                "{} {} had {} bab{}!".format(
                    BABY,
                    self.get_name(), board_space.spin[str(value)],
                    "ies" if board_space.spin[str(value)] != 1 else "y"
                )
            )
        
        # Check if the player is deciding on night school
        elif board_space.type == "night_school":

            # Check if the player is an AI
            #   sleep for 2 seconds to simulate a decision
            night_school = False
            if self.is_ai:
                night_school = randint(1, 10) % 2 == 0
                await sleep(2)
            
            # The player is a real person, let them decide
            else:

                # Send the message asking the player to decide
                night_school = await self.ask_for_split_path(
                    game,
                    title = "Night School?",
                    description = (
                        """
                        If you want to go to Night School, react with {}.
                        If you don't want to go, react with {}.
                        """
                    ),
                    true_path = GRADUATION, false_path = SPIN
                )
            
            # Make sure the player moves in the correct direction
            self.move_modify = night_school

            # Check if the player wants to go to night school
            if night_school:
                self.is_college = True
                self.cash -= 100000
                await game.add_action(
                    "{} {} had to pay ${:0,} to go to Night School!".format(
                        PAY_MONEY,
                        self.get_name(), 100000
                    )
                )

                # Ask for a new career
                self.career = await self.ask_for_career(game, new_career = True)
            
            # The player does not want to go to night school
            else:
                await game.add_action(
                    "{} {} chose not to go to Night School!".format(
                        ACTION, self.get_name()
                    )
                )
        
        # Check if the player is deciding on the family path
        elif board_space.type == "family_path":

            # Check if this player is an AI, sleep for 2 seconds to simulate a decision
            family_path = False
            if self.is_ai:
                family_path = randint(1, 10) % 2 == 0
                await sleep(2)
            
            # This player is a real player, let them decide
            else:

                # Send the message asking the player to decide
                family_path = await self.ask_for_split_path(
                    game,
                    title = "Family Path?",
                    description = (
                        """
                        If you want to go down the Family Path, react with {}.
                        If you don't want to, react with {}.
                        """
                    ),
                    true_path = FAMILY, false_path = SPIN
                )
            
            # Update the turn message about the player's decision
            self.move_modify = family_path
            await game.add_action(
                "{} {} is{} going down the Family Path!".format(
                    FAMILY if family_path else ACTION,
                    self.get_name(),
                    "" if family_path else " not"
                )
            )
        
        # Check if the player is deciding on risky road
        elif board_space.type == "risky_road":
            
            # Check if this player is an AI, sleep for 2 seconds to simulate a decision
            risky_road = False
            if self.is_ai:
                risky_road = randint(1, 10) % 2 == 0
                await sleep(2)
            
            # This player is a real player, let them decide
            else:

                # Send the message asking the player to decide
                risky_road = await self.ask_for_split_path(
                    game,
                    title = "Risky Road?",
                    description = (
                        """
                        If you want to go down the Risky Road, react with {}.
                        If you don't want to, react with {}.
                        """
                    ),
                    true_path = RISKY_ROAD, false_path = SPIN
                )
            
            # Update the turn message about the player's decision
            self.move_modify = risky_road
            await game.add_action(
                "{} {} is{} going down the Risky Road!".format(
                    RISKY_ROAD if risky_road else ACTION,
                    self.get_name(),
                    "" if risky_road else " not"
                )
            )
        
        # Check if the player is retiring
        elif board_space.type == "retirement":
            
            # Give the player their retirement money
            #   have the player retire
            #   and update the turn message
            amount = 100000 * (5 - len(game.get_retired()))
            self.cash += amount
            self.is_retired = True
            await game.add_action(
                "{} {} has retired and collected ${:0,}".format(
                    RETIRED,
                    self.get_name(), amount
                )
            )
        
        # The player takes another turn if the space is not the 
        #   retirement space
        if board_space.type != "retirement":
            self.extra_turn = True
    
    async def process_baby_space(self, game, board_space):
        """Processes the baby space when this player lands on it

        :param game: The game object that this player is connected to
        :param board_space: The board space object where this player is current occupying
        """
        
        # Determine what action the baby space is
        if board_space.type == "baby":
            description = "{} {} had a baby!"
            self.babies += 1
        elif board_space.type == "twins":
            description = "{} {} had twins!"
            self.babies += 2
        elif board_space.type == "triplets":
            description = "{} {} had triplets!"
            self.babies += 3
        
        # Update the turn message
        await game.add_action(description.format(BABY, self.get_name()))
    
    async def ask_for_split_path(self, game, *, title = None, description = None, true_path = None, false_path = None):
        """Asks the player to decide on a split path

        :param game: The game object that this player is connected to
        :param title: The title of the embed to send
        :param description: A formatted description of the embed to send
            Note that this description must include format braces to take into account
            the true_path and false_path emojis
        :param true_path: An emoji for the player to go towards the new split path
        :param false_path: An emoji for the player to stay on the same path
        
        :rtype: bool
        """

        # Send a message asking the player if they want to go down the new path or stay on
        #   the current path
        message = await game.ctx.send(
            embed = Embed(
                title = title,
                description = description.format(true_path, false_path),
                colour = await get_embed_color(self.member)
            )
        )
        await message.add_reaction(true_path)
        await message.add_reaction(false_path)

        # Wait for the user to react with their choice and delete the message
        reaction, user = await game.bot.wait_for("reaction_add", check = lambda reaction, user: (
            reaction.message.id == message.id and
            user.id == self.id and
            str(reaction) in [true_path, false_path]
        ))
        await message.delete()
        return str(reaction) == true_path

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Other Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def next_space(self, game, number):
        """Moves the player as many moves as specfied by number

        :param game: The game object that this player is connected to
        :param number: The amount of spaces to move the player
        """
        
        # Keep track of how many moves have been made,
        #   how many paydays were passed
        #   and the board of the game
        moves = 0
        paydays = 0
        board = game.board
        current = self.space
        while True:

            # Check if the player moves in a specific way
            #   For example, if the player comes to a stop sign
            #   and there are two different paths that can be taken,
            #   the player will have decided on which path to take
            if board[current].next_true != None:
                if self.move_modify:
                    current = board[current].next_true
                else:
                    current = board[current].next_false
            
            # The player moves normally
            else:
                current = board[current].next
            
            # Check if the space reached is a stop sign or all the moves have been made
            moves += 1
            if board[current].stop or moves == number:

                # Check if the current space is a payday
                #   give the player a bonus payday
                if board[current].type == "payday":
                    paydays += 1
                break
            
            # The player passed a payday
            if board[current].type == "payday":
                paydays += 1
        
        # Add the player's payday to their cash
        for payday in range(paydays):
            self.cash += self.career.salary
        
        # Return a JSON object describing the player's current board state
        board[current].paydays_passed = paydays
        board[current].current = current
        return board[current]


    def get_name(self):
        """Returns the name of this Player.
        If the player is a discord.Member object, the name
        will be their username + discriminator

        :rtype: str
        """
        if self.is_ai:
            return self.member
        return str(self.member)
    
    def give_payday(self, *, paydays_passed = 1):
        """Gives the player a payday from their career

        :param paydays_passed: The amount of paydays to give to the player
        """
        self.cash += self.career.salary * paydays_passed