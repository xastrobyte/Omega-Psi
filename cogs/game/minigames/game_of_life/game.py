from asyncio import sleep
from discord import Embed
from random import shuffle
from requests import get

from cogs.globals import PRIMARY_EMBED_COLOR, LEAVE, NUMBER_EMOJIS

from cogs.game.minigames.base_game.game import Game
from cogs.game.minigames.game_of_life.cards import HouseCard, CareerCard, PetCard, ActionCard, BoardSpace
from cogs.game.minigames.game_of_life.player import GameOfLifePlayer
from cogs.game.minigames.game_of_life.turn import GameOfLifeTurn
from cogs.game.minigames.game_of_life.variables import GET_MONEY, PAY_MONEY, ACTION, SUED, SPIN

from util.database.database import database
from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class GameOfLifeGame(Game):
    """A GameOfLifeGame object that holds information about a game of The Game of Life

    :param bot: The bot object used to wait for reactions
    :param ctx: The context of where this game is being played
    :param players: The list of players in the game
    :param against_ais: Whether or not this game is being played against AIs
    :param ai_amount: The amount of AIs to play against
    """

    def __init__(self, bot, ctx, players, *, against_ais = False, ai_amount = 4):
        super().__init__(
            bot, ctx,
            players = [ GameOfLifePlayer(player if not isinstance(player, tuple) else player[0]) for player in players ]
        )

        # Save the cards into this game instance
        game_of_life = get("https://fellowhashbrown.com/api/gameOfLife?target=game_of_life")
        game_of_life = game_of_life.json()

        self.career_cards = [ CareerCard(json = card) for card in game_of_life["career_cards"] ]
        self.college_career_cards = [ CareerCard(json = card) for card in game_of_life["college_career_cards"] ]
        self.house_cards = [ HouseCard(json = card) for card in game_of_life["house_cards"] ]
        self.pet_cards = [ PetCard(json = card) for card in game_of_life["pet_cards"] ]
        self.action_cards = [ ActionCard(json = card) for card in game_of_life["action_cards"] ]
        self.board = { space: BoardSpace(space = space, json = game_of_life["board_spaces"][space]) for space in game_of_life["board_spaces"] }

        shuffle(self.career_cards)
        shuffle(self.college_career_cards)
        shuffle(self.house_cards)
        shuffle(self.action_cards)
        shuffle(self.pet_cards)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Getter
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @property
    def bot(self):
        return self.__bot
    
    @property
    def ctx(self):
        return self.__ctx
    
    # # # # # # # # # # # # # # # # # # # #

    @property
    def career_cards(self):
        return self.__career_cards
    
    @property
    def college_career_cards(self):
        return self.__college_career_cards
    
    @property
    def house_cards(self):
        return self.__house_cards
    
    @property
    def pet_cards(self):
        return self.__pet_cards
    
    @property
    def action_cards(self):
        return self.__action_cards
    
    @property
    def board(self):
        return self.__board

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Setter
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @bot.setter
    def bot(self, bot):
        self.__bot = bot
    
    @ctx.setter
    def ctx(self, ctx):
        self.__ctx = ctx
    
    # # # # # # # # # # # # # # # # # # # #

    @career_cards.setter
    def career_cards(self, career_cards):
        self.__career_cards = career_cards
    
    @college_career_cards.setter
    def college_career_cards(self, college_career_cards):
        self.__college_career_cards = college_career_cards
    
    @house_cards.setter
    def house_cards(self, house_cards):
        self.__house_cards = house_cards
    
    @pet_cards.setter
    def pet_cards(self, pet_cards):
        self.__pet_cards = pet_cards
    
    @action_cards.setter
    def action_cards(self, action_cards):
        self.__action_cards = action_cards
    
    @board.setter
    def board(self, board):
        self.__board = board

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Play Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def play(self):
        """Let's the players in this game play the Game of Life"""

        # Setup each player
        for player in self.players:
            await player.setup(self)

        # Play the game until everyone has retired
        while not self.is_everyone_retired():
            self.new_turn()

            # Process through the player's turn
            result = await self.get_current_player().process_turn(self)

            # Check if the player left, remove them
            if result == LEAVE:
                self.players.remove(self.get_current_player())

                # Check if there aren't at least 2 players, stop the game
                if len(self.players) < 2:
                    break
                
                # Check if the player that left was last in the list
                #   of players; If so, move to the first player
                if self.current_player >= len(self.players):
                    self.current_player = 0
                continue

            # Check if the current player does not get an extra turn
            if not self.get_current_player().extra_turn:

                # Continue to move to the next player while the current player 
                #   is already retired
                self.next_player()
                while self.get_current_player().is_retired and not self.is_everyone_retired():
                    self.next_player()
        
        # Check if there weren't enough players, stop the game and tell the game ctx channel
        if len(self.players) < 2:
            await self.ctx.send(
                embed = Embed(
                    title = "Not Enough Players :(",
                    description = "Too many people left the game. You need at least 2 players to play the game.",
                    colour = PRIMARY_EMBED_COLOR if self.players[0].is_ai else await get_embed_color(self.players[0].member)
                )
            )
        
        # The game successfully ended, finalize it
        await self.finalize_game()
    
    async def finalize_game(self):
        """Finalizes the game by adding up all the action cards and pet cards,
        having players sell their houses, and taking money for each loan each player has.
        """

        # Send a message saying everyone retired
        await self.ctx.send(
            embed = Embed(
                title = "Everyone Retired!",
                description = "Now let's add up all your earnings!",
                colour = PRIMARY_EMBED_COLOR
            )
        )

        # Iterate through each player to sell their houses,
        #   pay back their loans, get money for each pet card and action card
        #   and collect money for each baby they have
        for player in self.players:

            # Keep track of everything in one turn message for each player
            self.new_turn(player)

            # Sell the players houses and update the turn message each time
            for house in player.house_cards:
                value = await player.ask_for_house(self, sell_house = True, house = house)
                player.cash += value
                await sleep(2)
            
            # Give the player $100,000 for each action card the player has
            player.cash += 100000 * player.action_cards
            await self.add_action(
                "{} {} had {} action card{} and collected ${:0,}{}!".format(
                    ACTION,
                    player.get_name(), player.action_cards,
                    "s" if player.action_cards != 1 else "",
                    100000 * player.action_cards,
                    " from them" if player.action_cards > 1 else ""
                )
            )
            await sleep(2)
        
            # Give the player $100,000 for each pet card the player has
            player.cash += 100000 * player.pet_cards
            await self.add_action(
                "{} {} had {} pet card{} and collected ${:0,}{}!".format(
                    ACTION,
                    player.get_name(), player.pet_cards,
                    "s" if player.pet_cards != 1 else "",
                    100000 * player.pet_cards,
                    " from them" if player.pet_cards > 1 else ""
                )
            )
            await sleep(2)

            # Give the player $50,000 for each baby the player has
            player.cash += 100000 * player.babies
            await self.add_action(
                "{} {} had {} bab{} and collected ${:0,}{}!".format(
                    ACTION,
                    player.get_name(), player.babies,
                    "ies" if player.babies != 1 else "y",
                    50000 * player.babies,
                    " for them" if player.babies > 1 else ""
                )
            )
            await sleep(2)

            # Take $60,000 from the player for each loan the player has
            player.cash -= 60000 * player.loans
            await self.add_action(
                "{} {} had {} loan{} and was deducted ${:0,}{}!".format(
                    ACTION,
                    player.get_name(), player.loans,
                    "s" if player.loans != 1 else "",
                    60000 * player.loans,
                    " from them" if player.loans > 1 else ""
                )
            )
            await sleep(2)
        
        # Find the winners of the game
        #   and update their wins in the database
        winners = [self.players[0]]
        winner = winners[0]
        for player in self.players:
            if player.cash > winner.cash:
                winners = [player]
                winner = player
            elif player.cash == winner.cash and player.id != winner.id:
                winners.append(player)
        
        for winner in winners:
            if not winner.is_ai:
                await database.users.update_game_of_life(winner.member, True)
        
        
        # Setup the text displaying everyone's totals and who won
        text = "\n".join([
            "{} - ${:0,}".format(
                player.get_name(), player.cash
            )
            for player in self.players
        ])

        # Check if there is only 1 winner
        if len(winners) == 1:
            text += "\n*{} won the game!*".format(winner.get_name())
        
        # Check if everyone tied
        elif len(winners) == len(self.players):
            text += "\n*Everyone Tied!*"
        
        # Check if 2+ people tied but not everyone tied
        else:
            text += "\n{}{} and {} {} tied!".format(
                ", ".join([
                    winner.get_name() for winner in winners
                ]) if len(winners) > 2 else winner.get_name(),
                "," if len(winners) > 2 else "",
                winners[len(winners) - 1].get_name(),
                "all" if len(winners) > 2 else "both"
            )
        
        # Send a message in the ctx
        await self.ctx.send(
            embed = Embed(
                title = "Results!",
                description = text,
                colour = PRIMARY_EMBED_COLOR
            )
        ) 
    
    async def pay_bonus(self, number):
        """Pays a bonus to any player that holds a salary card
        with the bonus number matching the specified number

        :param number: The number to pay bonuses to players who have this number
        """

        # Iterate through all players who have a career card
        #   only give a bonus if the player did not spin their own bonus number
        for player in filter(lambda player: player.career, self.players):
            if player.career.bonus == number and self.get_current_player().id != player.id:

                # Add the action of paying bonuses to the turn message
                await self.add_action(
                    "{} {} had to pay {} ${:0,} for spinning {}".format(
                        PAY_MONEY,
                        self.get_current_player().get_name(), player.get_name(),
                        player.career.salary // 10,
                        number
                    )
                )

                # Have the current player pay this player
                self.get_current_player().cash -= player.career.salary // 10
                player.cash += player.career.salary // 10
    
    async def process_action_card(self, board_space):
        """Processes the action card that a player lands on

        :param board_space: The board space that is used to process the action card
        """
        
        # Pull a card from the game's action cards
        #   if the card is a FIRED card but the current player does not have a career yet
        #   don't give them that card
        index = 0
        card = self.action_cards[index]
        while card.action.type == "fired" and not self.get_current_player().career:
            index += 1
            card = self.action_cards[index]
        
        # A valid card was found, remove it from the deck and add it to the player's deck
        card = self.action_cards.pop(index)
        self.get_current_player().action_cards += 1
        await self.add_action(str(card))

        # Check if the player is collecting money
        if card.action.type == "collect":

            # Check if there is a spin type for the card
            #   if so, the player will spin to collect a variable
            #   amount of money
            if card.spin.type != None:

                # Check if the spin type is of type color
                #   have the player spin a color
                amount = None
                if card.spin.type == "color":

                    # Ask the player to spin to get the proper amount
                    is_black = await self.get_current_player().ask_for_spin(self, is_color = True)
                    amount = card.spin.high.amount if is_black else card.spin.low.amount
                    await self.add_action(
                        "{} {} spun {}!".format(
                            SPIN, self.get_current_player().get_name(),
                            "black" if is_black else "red"
                        )
                    )
                
                # The spin type is by number
                else:
                    value = await self.get_current_player().ask_for_spin(self)
                    await self.add_action(
                        "{} {} spun a {}!".format(
                            SPIN, self.get_current_player().get_name(),
                            value
                        )
                    )

                    # Get the low values
                    if card.spin.low != None:
                        low = card.spin.low.low
                        high = card.spin.low.high
                        if value >= low and value <= high:
                            amount = card.spin.low.amount
                    
                    # Get the medium values
                    if card.spin.medium != None and amount == None:
                        low = card.spin.medium.low
                        high = card.spin.medium.high
                        if value >= low and value <= high:
                            amount = card.spin.medium.amount
                    
                    # Get the high values
                    if card.spin.high != None and amount == None:
                        low = card.spin.high.low
                        high = card.spin.high.high
                        if value >= low and value <= high:
                            amount = card.spin.high.amount
            
            # There is no spin type for this card
            #   get the amount on the card
            else:
                amount = card.spin.amount
            
            # Update the turn message saying who collected money and how much
            self.get_current_player().cash += amount
            await self.add_action(
                "{} {} collected ${:0,}".format(
                    GET_MONEY, self.get_current_player().get_name(), amount
                )
            )

        # Check if the player is collecting money x 10k of their spin
        elif card.action.type == "collect_10k":

            # Ask the player to spin, give them the amount of money times their spin
            #   and update the turn message
            value = await self.get_current_player().ask_for_spin(self)
            self.get_current_player().cash += value * card.spin.amount
            await self.add_action(
                "{} {} collected ${:0,}".format(
                    GET_MONEY, self.get_current_player().get_name(), value * card.spin.amount
                )
            )

        # Check if the player is collecting a lawsuit
        elif card.action.type == "collect_lawsuit":

            # Have the player choose an opponent to give them money
            #   take the money from the opponent and give it to the player
            #   and update the turn message
            opponent = await self.get_current_player().ask_for_opponent(self, is_lawsuit = True)
            opponent.cash -= card.spin.amount
            self.get_current_player().cash += card.spin.amount
            await self.add_action(
                "{} {} sued {} for ${:0,}".format(
                    SUED, self.get_current_player().get_name(), opponent.get_name(), card.spin.amount
                )
            )

        # Check if the player is competing against another player
        elif card.action.type == "compete":

            # Have the player choose an opponent to compete against
            #   give the winner the amount on the card
            #   and update the turn message
            winner, _ = await self.compete(self.get_current_player())
            winner.cash += card.spin.amount
            await self.add_action(
                "{} {} won and collected ${:0,}".format(
                    GET_MONEY, winner.get_name(), card.spin.amount
                )
            )

        # Check if the player is competing x 10k against another player
        elif card.action.type == "compete_10k":

            # Have the player choose an opponent to compete against
            #   give the winner the amount on the card
            #   and update the turn message
            winner, value = await self.compete(self.get_current_player())
            winner.cash += card.spin.amount *  value
            await self.add_action(
                "{} {} won and collected ${:0,}".format(
                    GET_MONEY, winner.get_name(), card.spin.amount * value
                )
            )

        # Check if the player is paying money
        elif card.action.type == "pay":

            # Take money from the player and update the turn message
            self.get_current_player().cash -= card.spin.amount
            await self.add_action(
                "{} {} had to pay the bank ${:0,}".format(
                    PAY_MONEY, self.get_current_player().get_name(), card.spin.amount
                )
            )

        # Check if the player got fired
        elif card.action.type == "fired":

            # Take the player's career card and have them choose another career
            if self.get_current_player().is_college:
                cards = self.college_career_cards
            else:
                cards = self.career_cards
            cards.append(self.get_current_player().career)
            self.get_current_player().career = None
            self.get_current_player().career = await self.get_current_player().ask_for_career(self)

        # Check if all players are spinning for money
        elif card.action.type == "collect_all":

            # Iterate through all the players
            for player in self.players:

                # Ask for the player's spin
                value = await player.ask_for_spin(self)
                await self.add_action(
                    "{} {} spun a {}".format(
                        SPIN, player.get_name(), value
                    )
                )
                amount = None

                # Get the low values
                if card.spin.low != None:
                    low = card.spin.low.low
                    high = card.spin.low.high
                    if value >= low and value <= high:
                        amount = card.spin.low.amount
                
                # Get the medium values
                if card.spin.medium != None and amount == None:
                    low = card.spin.medium.low
                    high = card.spin.medium.high
                    if value >= low and value <= high:
                        amount = card.spin.medium.amount
                
                # Get the high values
                if card.spin.high != None and amount == None:
                    low = card.spin.high.low
                    high = card.spin.high.high
                    if value >= low and value <= high:
                        amount = card.spin.high.amount
                
                # Give the player their cash and update the turn message
                player.cash += amount
                await self.add_action(
                    "{} {} collected ${:0,}".format(
                        GET_MONEY, player.get_name(), amount
                    )
                )
    
    async def spin_to_win(self):
        """Let's all the players in the game play the Spin To Win minigame
        """
        
        # Keep track of the spots taken and the message that shows each spin result
        spots = {}

        # Send a message saying it's a Spin to Win
        message = await self.ctx.send(
            embed = Embed(
                title = "Spin to Win!",
                description = "Everyone chooses a spot!",
                colour = PRIMARY_EMBED_COLOR if self.get_current_player().is_ai else await get_embed_color(self.get_current_player().member)
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
        )

        # Have each player decide on their spot(s)
        #   Then update the message
        for player in self.players:
            spots = await player.ask_for_spot(
                self, message, spots, 
                choose_from = 2 if player.id == self.get_current_player().id else 1
            )
            await message.edit(
                embed = Embed(
                    title = "Spin to Win!",
                    description = "_ _",
                    colour = PRIMARY_EMBED_COLOR if self.get_current_player().is_ai else await get_embed_color(self.get_current_player().member)
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
            )
        
        # Keep spinning until someone wins
        #  and update the message with a new embed displaying each spinning result
        await sleep(2)
        embed = Embed(
            title = "Spin to Win!",
            description = "{} is spinning!".format(self.get_current_player().get_name()),
            colour = PRIMARY_EMBED_COLOR if self.get_current_player().is_ai else await get_embed_color(self.get_current_player().member)
        ).add_field(
            name = "Spots",
            value = "\n".join([
                "{} - {}".format(
                    str(spot), spots[spot].get_name()
                )
                for spot in spots
            ]) if len(spots) > 0 else "None Taken Yet!",
            inline = False
        )
        await message.edit(embed = embed)
        spinning_results = []
        winner = None
        while not winner:

            # Ask the player to spin for a number
            number = await self.get_current_player().ask_for_spin(self)
            result = "{} spun a {}".format(
                self.get_current_player().get_name(),
                number
            )

            # Determine if someone won the spin to win
            emoji = str(NUMBER_EMOJIS[number - 1])
            if emoji in spots:
                result += " and {} won the Spin to Win!".format(spots[emoji].get_name())
                winner = spots[emoji]
            
            # Sleep for 2 seconds so everyone can read what happened
            # Update the message with a new embed displaying each spinning result
            spinning_results.append(result)
            embed = Embed(
                title = "Spin to Win!",
                description = "\n".join(spinning_results),
                colour = PRIMARY_EMBED_COLOR if self.get_current_player().is_ai else await get_embed_color(self.get_current_player().member)
            ).add_field(
                name = "Spots",
                value = "\n".join([
                    "{} - {}".format(
                        str(spot), spots[spot].get_name()
                    )
                    for spot in spots
                ]) if len(spots) > 0 else "None Taken Yet!",
                inline = False
            )
            await message.edit(embed = embed)
            await sleep(2)
        
        # Give the winner of the spin to win $200,000
        winner.cash += 200000
    
    async def compete(self, challenger):
        """Asks the challenging player to choose an opponent to spin against each other
        to see who gets the higher number.

        :param challenger: The player who is choosing their opponent to spin off against
        
        :returns: The winner of the spin off and the number that the winning player spun
        :rtype: tuple
        """
        
        # Have the player choose an opponent in this game
        opponent = await challenger.ask_for_opponent(self)

        # Ask each player to spin while the spins are the same value
        while True:
            value_challenger = await challenger.ask_for_spin(self, allow_leave = False)
            await self.add_action(
                "{} {} spun a {}!".format(
                    SPIN, challenger.get_name(), value_challenger
                )
            )
            value_opponent = await opponent.ask_for_spin(self, allow_leave = False)
            await self.add_action(
                "{} {} spun a {}!".format(
                    SPIN, opponent.get_name(), value_opponent
                )
            )

            # Check if the values are the same, have them spin again
            if value_challenger == value_opponent:
                await self.add_action(
                    "{} {} and {} both spun {}. They have to spin again!".format(
                        ACTION,
                        challenger.get_name(), opponent.get_name(),
                        value_challenger
                    )
                )
                await sleep(2)
            
            # The values are different, return the winner and their winning number
            else:
                winner = challenger if value_challenger > value_opponent else opponent
                await self.add_action(
                    "{} {} spun higher!".format(
                        ACTION, winner.get_name()
                    )
                )
                return winner, max([value_challenger, value_opponent])

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Other Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_retired(self):
        """Returns a list of players who have already retired

        :rtype: list
        """
        return [ player for player in self.players if player.is_retired ]

    def is_everyone_retired(self):
        """Returns whether or not each player in the game has retired

        :rtype: bool
        """
        for player in self.players:
            if not player.is_retired:
                return False
        return True
    
    def new_turn(self, player = None):
        """Creates a new Turn object for this Game."""
        self.current_turn = GameOfLifeTurn(self, player)
    
    async def add_action(self, action):
        """Adds a new action to the current turn object in the game

        :param action: The action that happened in this turn
        """
        await self.current_turn.add_action(action)