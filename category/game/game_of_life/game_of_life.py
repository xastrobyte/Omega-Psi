import asyncio, discord, requests

from random import randint, shuffle

from category.globals import PRIMARY_EMBED_COLOR, LEAVE, NUMBER_EMOJIS
from category.globals import GRADUATION, BRIEFCASE
from category.globals import PAYDAY, PAYDAY_BONUS, GET_MONEY, PAY_MONEY, PET, ACTION, HOUSE, LOAN

from util.functions import get_embed_color

from .functions import *

# # # # # # # # # # # # # # # # # # # # # # # # #

class Turn:
    def __init__(self, game, player):
        self._game = game
        self._player = player
        self._message = None
        self._actions = []
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_game(self):
        return self._game
    
    def get_player(self):
        return self._player
    
    def get_message(self):
        return self._message
    
    def get_actions(self):
        return self._actions
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    async def init(self):

        # Create the first message
        self._message = await self.get_game().get_channel().send(
            embed = await self.build_embed()
        )

    async def add_action(self, action):
        
        # Add the action
        self._actions.append(action)

        # Update the message with the new embed
        await self.get_message().edit(embed = await self.build_embed())
    
    async def build_embed(self):

        # Add the actions
        actions_text = ""
        for index in range(len(self.get_actions())):
            action = self.get_actions()[index]

            # Check if the action is the most recent one
            if index == len(self.get_actions()) - 1:
                action = "**{}**\n".format(action)
            else:
                action = "{}\n".format(action)
            
            actions_text += action

        # Create the embed
        embed = discord.Embed(
            title = "{}'s Turn!".format(self.get_player().get_name(title = True)),
            description = actions_text,
            colour = PRIMARY_EMBED_COLOR if self.get_player().is_ai() else await get_embed_color(self.get_player().get_member())
        ).set_footer(
            text = "You have ${}".format(commafy(self.get_player().get_cash()))
        )

        return embed
    

class Player:
    def __init__(self, member, ai = False):
        self._member = member
        self._id = 0 if type(member) == str else member.id
        self._ai = ai
        self._married = False
        self._babies = 0
        self._current_space = None
        self._pets = 1
        self._cash = 200000
        self._career = None
        self._college = False
        self._action_cards = 0
        self._house_cards = []
        self._pet_cards = 0
        self._loans = 0
        self._retired = False
        self._move_modify = None
        self._extra_turn = False
        self._won = False
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_member(self):
        return self._member
    
    def set_id(self, id):
        self._id = id
    
    def get_id(self):
        return self._id
    
    def is_ai(self):
        return self._ai
    
    def gets_married(self):
        self._married = True
    
    def has_baby(self):
        self._babies += 1
    
    def get_babies(self):
        return self._babies

    def get_current_space(self):
        return self._current_space
    
    def get_pets(self):
        return self._pets
    
    def get_cash(self):
        return self._cash
    
    def set_career(self, career):
        self._career = career
    
    def get_career(self):
        return self._career
    
    def is_college(self):
        return self._college
    
    def goes_to_college(self):
        self._college = True
    
    def get_action_cards(self):
        return self._action_cards
    
    def add_action_card(self):
        self._action_cards += 1
    
    def get_houses(self):
        return self._house_cards
    
    def add_house(self, card):
        self._house_cards.append(card)
    
    def get_pet_cards(self):
        return self._pet_cards
    
    def add_pet_card(self):
        self._pet_cards += 1
    
    def get_loans(self):
        return self._loans
    
    def pull_out_loans(self, amount = 1):
        self._loans += amount
        self.give_cash(50000 * amount)
    
    def is_retired(self):
        return self._retired
    
    def retire(self):
        self._retired = True
    
    def did_win(self):
        return self._won
    
    def won(self):
        self._won = True
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_name(self, *, title = False):
        if self.is_ai():
            return self.get_member()
        if title:
            return "{}#{}".format(
                self.get_member().name,
                self.get_member().discriminator
            )
        return self.get_member().mention
    
    def give_cash(self, amount):
        self._cash += amount
    
    def take_cash(self, amount):
        self._cash -= amount
    
    def payday(self):
        self.give_cash(self.get_career()["salary"])
    
    def modify_move(self, move_modify):
        self._move_modify = move_modify
    
    def extra_turn(self):
        self._extra_turn = True
    
    def has_extra_turn(self):
        return self._extra_turn
    
    def remove_extra_turn(self):
        self._extra_turn = False
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    def next_space(self, game, length):

        # Keep track of how many moves were made and how many paydays were passed
        moves = 0
        paydays = 0

        # Continue moving to the next space
        board = game.get_board()
        current = self.get_current_space()
        while True:
            
            # Check if the player moves in a specific way
            if "next_true" in board[current]:
                current = board[current]["next_{}".format(str(self._move_modify).lower())]
            
            # The player moves normally
            else:

                # Update the current space
                current = board[current]["next"]

            # The space reached is a stop space or all the moves have been made
            moves += 1            
            if board[current]["stop"] or moves == length:
                
                # Check if the current space is a payday
                if board[current]["type"] == "payday":
                    paydays += 1
                break
            
            # The player passed a payday
            if board[current]["type"] == "payday":
                paydays += 1
    
        # Add the player's paydays
        for payday in range(paydays):
            self.payday()

        board[current]["paydays_passed"] = paydays
        board[current]["current"] = current
        return board[current]

    async def setup(self, game):
        
        # Check if the player is an AI
        if self.is_ai():

            # Sleep for 2 seconds simulating a decision
            await asyncio.sleep(2)
            
            # Determine whether or not the AI is going to college
            college = randint(1, 10) % 2 == 0   # Even number means going to college
                                                # Odd number means career
            # Going to college
            if college:
                self.take_cash(100000)
                self._college = True
                self._current_space = "c0"
                await game.get_channel().send(
                    embed = discord.Embed(
                        title = "{} is going to college!".format(self.get_name(title = True)),
                        description = "{} has to pay $100,000 for tuition fees".format(self.get_name()),
                        colour = PRIMARY_EMBED_COLOR if self.is_ai() else await get_embed_color(self._member)
                    )
                )
            
            # Going into a career
            else:
                
                # Choose a random card from the game's deck
                card = game.get_career_cards().pop(randint(0, len(game.get_career_cards()) - 1))
                self._career = card
                self._current_space = "j0"
                await game.get_channel().send(
                    embed = discord.Embed(
                        title = "{} chose a career!".format(self.get_name(title = True)),
                        description = display_career(self._career),
                        colour = PRIMARY_EMBED_COLOR if self.is_ai() else await get_embed_color(self._member)
                    )
                )
        
        # The player is a real person
        else:
            
            # Ask if the player wants to go to college or not
            college = False
            msg = await game.get_channel().send(
                self._member.mention,
                embed = discord.Embed(
                    title = "College or Career?",
                    description = (
                        """
                        If you want to go to college, react with {}
                        If you want to go straight into a career, react with {}
                        """.format(
                            GRADUATION, BRIEFCASE
                        )
                    ),
                    colour = await get_embed_color(self._member)
                )
            )
            await msg.add_reaction(GRADUATION)
            await msg.add_reaction(BRIEFCASE)

            # Get the reaction as long as it's from the user
            def check_reaction(reaction, user):
                return reaction.message.id == msg.id and str(reaction) in [GRADUATION, BRIEFCASE] and user.id == self._member.id
            reaction, user = await game.get_bot().wait_for("reaction_add", check = check_reaction)
            college = str(reaction) == GRADUATION

            # Check if the user is going to college
            if college:

                # Take 100k from the user and set their college attribute to true
                self.take_cash(100000)
                self._college = True
                self._current_space = "c0"
                await game.get_channel().send(
                    embed = discord.Embed(
                        title = "{} is going to college!".format(self.get_name(title = True)),
                        description = "{} has to pay $100,000 for tuition fees".format(self.get_name()),
                        colour = PRIMARY_EMBED_COLOR if self.is_ai() else await get_embed_color(self._member)
                    )
                )
            
            # The user is not going to college
            else:
                self._current_space = "j0"

                # Choose 2 random cards from the career deck
                career_deck = game.get_career_cards()
                card_one = career_deck.pop(randint(0, len(career_deck) - 1))
                card_two = career_deck.pop(randint(0, len(career_deck) - 1))

                # Have the player decide which career they want
                await game.get_channel().send(
                    "Check your DM's for your career choices!",
                    delete_after = 10
                )
                msg = await self._member.send(
                    embed = discord.Embed(
                        title = "Choose a Career!",
                        description = "_ _",
                        colour = await get_embed_color(self._member)
                    ).add_field(
                        name = NUMBER_EMOJIS[0],
                        value = display_career(card_one),
                        inline = False
                    ).add_field(
                        name = NUMBER_EMOJIS[1],
                        value = display_career(card_two),
                        inline = False
                    )
                )
                await msg.add_reaction(NUMBER_EMOJIS[0])
                await msg.add_reaction(NUMBER_EMOJIS[1])

                # Wait for the user's reaction
                def check_reaction(reaction, user):
                    return (
                        reaction.message.id == msg.id and
                        str(reaction) in NUMBER_EMOJIS[:2] and
                        user.id == self.get_member().id
                    )
                reaction, user = await game.get_bot().wait_for("reaction_add", check = check_reaction)
                if str(reaction) == NUMBER_EMOJIS[0]:
                    self.set_career(card_one)
                    game.get_career_cards().append(card_two)
                elif str(reaction) == NUMBER_EMOJIS[1]:
                    self.set_career(card_two)
                    game.get_career_cards().append(card_one)
                
                # Display the career card to the channel
                await game.get_channel().send(
                    embed = discord.Embed(
                        title = "{} chose a career!".format(self.get_name(title = True)),
                        description = display_career(self.get_career()),
                        colour = PRIMARY_EMBED_COLOR if self.is_ai() else await get_embed_color(self._member)
                    )
                )
    
    async def spin(self, game):

        # Send the Turn message
        turn = Turn(game, self)
        await turn.init()

        # Ask the player to spin
        value = await ask_for_spin(game, turn)

        # Check if the player is leaving
        if value == LEAVE:
            return True

        # Check if the number spun belongs to any career card
        await game.pay_bonus(turn, value)

        # See what spot the player lands on
        board_space = self.next_space(game, value)
        self._current_space = board_space["current"]
    
        # Check if the player got any paydays
        if board_space["paydays_passed"] > 0:
            await turn.add_action(
                "{} {} got {} payday{}!".format(
                    PAYDAY,
                    self.get_name(),
                    board_space["paydays_passed"],
                    "s" if board_space["paydays_passed"] > 1 else ""
                )
            )
        
        # Check if the space is a pet space
        if board_space["type"] == "pet":
            await process_pet_card(game, turn)
        
        # Check if the space is an action space
        elif board_space["type"] == "action":
            await process_action_card(game, turn)
        
        # Check if the space is a house space
        elif board_space["type"] == "house":
            await ask_for_house(game, turn)

        # Check if the space is a spin to win
        elif board_space["type"] == "spin_to_win":
            await spin_to_win(game, turn)
        
        # Check if the space is a stop space
        elif board_space["stop"]:
            await process_stop_space(game, turn, board_space["type"], board_space)
        
        # Check if the space is a baby space
        elif board_space["type"] in ["baby", "twins", "triplets"]:
            await process_baby_space(game, turn, board_space)
        
        # Check if the user has to pay money or get money
        elif board_space["type"] == "pay_money":

            # Update the turn message
            self.take_cash(board_space["amount"])
            await turn.add_action(
                "{} {} has to pay *${}*".format(
                    PAY_MONEY,
                    self.get_name(), commafy(board_space["amount"])
                )
            )
        
        elif board_space["type"] == "get_money":

            # Update the turn message
            self.give_cash(board_space["amount"])
            await turn.add_action(
                "{} {} gets paid *${}*".format(
                    GET_MONEY,
                    self.get_name(), commafy(board_space["amount"])
                )
            )
        
        # Check if the player landed on a payday space
        elif board_space["type"] == "payday":

            # Give the player a $100,000 bonus and update the turn message
            self.give_cash(100000)
            await turn.add_action(
                "{} {} landed on a payday and got a $100,000 bonus!".format(
                    PAYDAY_BONUS,
                    self.get_name()
                )
            )
        
        return False

class GameOfLife:

    END_GAME = "END_GAME"

    def __init__(self, players, bot, channel, *, against_ais = False, ai_amount = 3):
        self._players = [Player(player) for player in players]

        # If player goes against AIs, keep the first player and make the rest AIs
        if against_ais:
            self._players = [self._players[0]]
            for player in range(ai_amount):
                self._players.append(Player("AI {}".format(player + 1), True))
        
        # If not against AIs, sort the players by their Discord ID
        else:
            self._players.sort(key = lambda user: user.get_member().id)
        
        # Give each player an ID
        next_ai = 1
        for player in self._players:
            if player.is_ai():
                player.set_id(next_ai)
                next_ai += 1
            else:
                player.set_id(player.get_member().id)
        self._current_player = 0
        
        self._channel = channel
        self._bot = bot

        # Save all the cards into the game instance
        #   First, request the Game Of Life API
        game_of_life = requests.get("https://www.fellowhashbrown.com/api/gameOfLife?target=game_of_life")
        game_of_life = game_of_life.json()

        self._career_cards = game_of_life["career_cards"]
        self._college_career_cards = game_of_life["college_career_cards"]
        self._house_cards = game_of_life["house_cards"]
        self._pet_cards = game_of_life["pet_cards"]
        self._action_cards = game_of_life["action_cards"]
        self._board = game_of_life["board_spaces"]
        self._rules = game_of_life["rules"]
    
    # # # # # # # # # # # # # # # # # # # #
    
    def get_players(self):
        return self._players

    def get_current_player(self):
        return self._players[self._current_player]
    
    def all_players_retired(self):
        for player in self._players:
            if not player.is_retired():
                return False
        return True
    
    def get_retired(self):
        return [
            player
            for player in self._players
            if player.is_retired()
        ]
        
    def next_player(self):

        # Check if the current player does not have an extra turn
        if not self.get_current_player().has_extra_turn():
            self._current_player += 1
        
        # The player does have an extra turn, remove their extra turn
        else:
            self.get_current_player().remove_extra_turn()
        
        # Loop back to the first player
        if self._current_player >= len(self._players):
            self._current_player = 0
    
    def remove_player(self, player):

        # Add the career card back in only
        if player.is_college():
            self.get_college_career_cards().append(player.get_career())
        else:
            self.get_career_cards().append(player.get_career())
        
        # Remove the player
        index = 0
        for temp_player in self.get_players():
            if temp_player.get_id() == player.get_id():
                self.get_players().pop(index)
                break
            index += 1
    
    def get_channel(self):
        return self._channel
    
    def get_bot(self):
        return self._bot
    
    def get_career_cards(self):
        shuffle(self._career_cards)
        return self._career_cards
    
    def get_college_career_cards(self):
        shuffle(self._college_career_cards)
        return self._college_career_cards
    
    def get_house_cards(self):
        shuffle(self._house_cards)
        return self._house_cards
    
    def get_pet_cards(self):
        shuffle(self._pet_cards)
        return self._pet_cards
    
    def get_action_cards(self):
        shuffle(self._action_cards)
        return self._action_cards
    
    def get_board(self):
        return self._board
    
    def get_rules(self):
        return self._rules
    
    # # # # # # # # # # # # # # # # # # # #

    async def pay_bonus(self, turn, number):
        source = turn.get_player()
        
        # Iterate through players
        for player in self._players:

            # Check if the player has a career card and if the player is not the same as the source
            if player.get_career() != None and player.get_id() != source.get_id():

                # Check if the player's bonus matches the given number
                if player.get_career()["bonus"] == number:

                    # Send a message to the channel that says who has to pay who
                    await turn.add_action(
                        "{} {} had to pay {} $20,000 for spinning {}".format(
                            PAY_MONEY,
                            source.get_name(),
                            player.get_name(),
                            number
                        )
                    )
                    source.take_cash(20000)
                    player.give_cash(20000)
    
    async def play(self):

        # Setup each player
        for player in self.get_players():
            await player.setup(self)
        
        # Sleep for 2 seconds so players can read what happened
        await asyncio.sleep(2)

        # Play the game until all players are retired
        while True:

            # Get the current player
            player = self.get_current_player()
            player_left = await player.spin(self)

            # Check if the player left
            if player_left:
                self.remove_player(player)

                # Check if there is only 1 player
                if len(self.get_players()) == 1:
                    return GameOfLife.END_GAME
            
            # Check if all players are retired
            if self.all_players_retired():
                break
            
            # Not all players are retired
            self.next_player()
            while self.get_current_player().is_retired():
                self.next_player()
        
        # End the game
        return await self.end_game()
    
    async def end_game(self):

        # Keep track of everything in one single message
        await self.get_channel().send(
            embed = discord.Embed(
                title = "Everyone Retired!",
                description = "Now let's add up all your earnings!",
                colour = PRIMARY_EMBED_COLOR
            )
        )
        
        # Go through each player and find the winning player
        winners = [self.get_players()[0]]
        winner = winners[0]
        for player in self.get_players():

            # Keep track of everything in one single message per player
            text = ""
            message = await self.get_channel().send(
                embed = discord.Embed(
                    title = player.get_name(title = True),
                    description = text,
                    colour = PRIMARY_EMBED_COLOR if player.is_ai() else await get_embed_color(player.get_member())
                )
            )

            # For each action card, give the player 100,000
            for i in range(player.get_action_cards()):
                player.give_cash(100000)
            
            # Update the message and sleep for 2 seconds so players can read what happened
            text = "{} {} had {} action card{} and collected ${} {}\n".format(
                ACTION,
                player.get_name(),
                player.get_action_cards(),
                "s" if player.get_action_cards() != 1 else "",
                commafy(100000 * player.get_action_cards()),
                "from them" if player.get_action_cards() > 1 else ""
            )
            await message.edit(
                embed = discord.Embed(
                    title = player.get_name(title = True),
                    description = text,
                    colour = PRIMARY_EMBED_COLOR if player.is_ai() else await get_embed_color(player.get_member())
                )
            )
            await asyncio.sleep(2)

            # For each pet card, give the player 100,000
            for i in range(player.get_pet_cards()):
                player.give_cash(100000)
            
            # Update the message and sleep for 2 seconds so players can read what happened
            text += "{} {} had {} pet card{} and collected ${} {}\n".format(
                PET,
                player.get_name(),
                player.get_pet_cards(),
                "s" if player.get_pet_cards() != 1 else "",
                commafy(100000 * player.get_pet_cards()),
                "from them" if player.get_pet_cards() > 1 else ""
            )
            await message.edit(
                embed = discord.Embed(
                    title = player.get_name(title = True),
                    description = text,
                    colour = PRIMARY_EMBED_COLOR if player.is_ai() else await get_embed_color(player.get_member())
                )
            )
            await asyncio.sleep(2)

            # For each loan, take 60,000 from the player
            for i in range(player.get_loans()):
                player.take_cash(60000)
            
            # Update the message and sleep for 2 seconds so players can read what happened
            text += "{} {} had {} loan{} and was deducted ${} {}\n".format(
                LOAN,
                player.get_name(),
                player.get_loans(),
                "s" if player.get_loans() != 1 else "",
                commafy(60000 * player.get_loans()),
                "from them" if player.get_loans() > 1 else ""
            )
            await message.edit(
                embed = discord.Embed(
                    title = player.get_name(title = True),
                    description = text,
                    colour = PRIMARY_EMBED_COLOR if player.is_ai() else await get_embed_color(player.get_member())
                )
            )
            await asyncio.sleep(2)

            # Have each player sell any houses they have
            for house in player.get_houses():
                value = await sell_house(self, player, house)
                player.give_cash(value)

                # Update the message and sleep for 2 seconds so players can read what happened
                text += "{} {} sold their house for ${}".format(
                    HOUSE,
                    player.get_name(), commafy(value)
                )
                await message.edit(
                    embed = discord.Embed(
                        title = player.get_name(title = True),
                        description = text,
                        colour = PRIMARY_EMBED_COLOR if player.is_ai() else await get_embed_color(player.get_member())
                    )
                )
                await asyncio.sleep(2)
            
            # Update the winner (or winners)
            if player.get_cash() > winner.get_cash():
                winners = [player]
                winner = player
            elif player.get_cash() == winner.get_cash():
                winners.append(player)
            
        # Setup the text displaying everyone's totals and who won
        text = ""
        for player in self.get_players():
            text += "{} - ${}\n".format(
                player.get_name(), commafy(player.get_cash())
            )
        
        # Check if there is only 1 winner
        if len(winners) == 1:
            text += "{} won the game!".format(winner.get_name())
        
        # Check if everyone tied
        elif len(winners) == len(self.get_players()):
            text += "Everyone Tied!"
        
        # Check if 2+ people tied but not everyone tied
        else:
            text += "{}{} and {} {} tied!".format(
                ", ".join([winner.get_name() for winner in winners]) if len(winners) > 2 else winner[0],
                "," if len(winners) > 2 else "",
                winner[len(winners) - 1],
                "all" if len(winners) > 2 else "both"
            )
    
        # Update who won and send a message in the channel
        for winner in winners:
            winner.won()
        await self.get_channel().send(
            embed = discord.Embed(
                title = "Results!",
                description = text,
                colour = PRIMARY_EMBED_COLOR
            )
        )