from discord import Embed
from random import choice

from cogs.globals import PRIMARY_EMBED_COLOR, LEAVE

from cogs.game.minigames.base_game.game import Game
from cogs.game.minigames.base_game.turn import Turn
from cogs.game.minigames.uno.player import UnoPlayer
from cogs.game.minigames.uno.variables import WILD_CARDS, DRAW_UNO, SKIP_CARDS, REVERSE_CARDS, ADD_2_CARDS, ADD_4_CARD, UNO_CARDS

from util.database.database import database
from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class UnoGame(Game):
    """An UnoGame object holds information pertaining to a game of Uno

    :param bot: The bot object used to wait for reactions
    :param ctx: The context of where this game is being played
    :param players: The list of players in the game
    """

    def __init__(self, bot, ctx, players):
        super().__init__(bot, ctx, 
            players = [ UnoPlayer(player if not isinstance(player, tuple) else player[0]) for player in players ]
        )
        
        # Keep track of the card that's on top
        self.card = None
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Getters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @property
    def card(self):
        return self.__card

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Setters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    @card.setter
    def card(self, card):
        self.__card = card

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Play Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def play(self):
        """Let's the players in this game play a game of Uno"""

        # Give each player their cards and set a top card
        self.card = choice(UNO_CARDS)
        for player in self.players:
            player.setup()
        
        # Continue playing game until someone runs out of cards
        while True:
            self.new_turn()
            await self.show_turn()

            # Show the current players cards to that player
            #   and have them decide on a card to play
            card = await self.get_current_player().wait_for_card(self)

            # Check if the player left, remove them
            if card == LEAVE:
                await self.add_action("{} left the game!".format(self.get_current_player().get_name()))
                await self.kick_player_out()

                # Check if there aren't at least 2 players, stop the game
                if len(self.players) < 2:
                    break
                
                # Check if the player that left was last in the list
                #   of players; If so, move to the first player
                if self.current_player >= len(self.players):
                    self.current_player = 0
                continue
            
            # Check if the current player has no more cards
            #   stop looping through the game
            if len(self.get_current_player().cards) == 0:
                break
        
            # Process the card that the player chose
            if card != DRAW_UNO:
                self.card = card
            await self.process_card(card)
    
        # Check if there weren't enough players, stop the game and tell the game ctx channel
        if len(self.players) < 2:
            await self.ctx.send(
                embed = Embed(
                    title = "Not Enough Players :(",
                    description = "Too many people left the game. You need at least 2 players to play the game.",
                    colour = PRIMARY_EMBED_COLOR if self.players[0].is_ai else await get_embed_color(self.players[0].member)
                )
            )
        
        # There are still enough players at the end of the loop
        #   someone won
        else:
        
            # The current player has no cards, they win
            #   everyone else loses
            await self.show_winner()
            for player in self.players:
                if not player.is_ai:
                    await database.users.update_uno(
                        player.member,
                        player.id == self.get_current_player().id
                    )
        
    async def process_card(self, card):
        """Processes the specified card if it's a draw "card", reverse card, etc.

        :param card: The card to be processed
        """

        # Show the card to everyone
        await self.show_card(card)

        # Check if the player had to draw a card
        if card == DRAW_UNO:
            self.get_current_player().cards.append(choice(UNO_CARDS))

        # Check if the player used a reverse card
        elif card in REVERSE_CARDS:
            if len(self.players) > 2:
                self.reverse()

        # Check if the player chose a wild card
        elif card in WILD_CARDS:

            # Check if the player chose a +4 card
            #   give the next player 4 more cards
            if card == ADD_4_CARD:
                for i in range(4):
                    self.get_next_player().cards.append(choice(UNO_CARDS))
            
            # Have the player choose a new colored card
            self.card = await self.get_current_player().ask_for_new_color(self)
            await self.add_action(
                "{} chose a new color <{}>".format(
                    self.get_current_player().get_name(),
                    self.card
                )
            )
            for player in self.players:
                await player.show_card(self, card, extras = [
                    "{} chose a new color <{}>".format(
                        self.get_current_player().get_name(),
                        self.card
                    )
                ])

        # Check if the player chose a +2 card
        #   give the next player 2 more cards
        elif card in ADD_2_CARDS:
            for i in range(2):
                self.get_next_player().cards.append(choice(UNO_CARDS))
        
        # Only show cards to all the players if they are not the next player
        #   and the cards are either a +4 card, a +2 card, or a skip card
        self.next_player(skip_next = card in SKIP_CARDS or (card in REVERSE_CARDS and len(self.players) == 2))
    
    async def show_turn(self):
        """Sends a message to each player displaying who's turn it is.
        The current player does not receive this message though because they
        are sent a separate message
        """

        # Add an empty action to send the message to the game channel
        #   and show the current player's turn to all the other players
        await self.add_action("")
        for player in self.players:
            await player.show_turn(self)
    
    async def show_card(self, card, *, extras = []):
        """Shows the current player's card choice to the other players and the game channel

        :param card: The card the current player chose
        :param extras: A list of extra information to add to the message
        """

        # Keep track of actions here to add actions to a message sent to a player
        actions = []

        # Update the turn message for the current turn
        #   if the current player hit the next player with a +2 or +4 card
        #       or if the current player has skipped someone, update the turn message again
        #   if the current player has 1 card left, update the turn message again
        await self.add_action("{} chose {}".format(
            self.get_current_player().get_name(), 
            "<{}>".format(card) if card != DRAW_UNO else DRAW_UNO
        ))
        if card in SKIP_CARDS or (card in REVERSE_CARDS and len(self.players) == 2):
            actions.append("{} skipped {}!".format(
                self.get_current_player().get_name(),
                self.get_next_player().get_name()
            ))
        elif card in (ADD_2_CARDS + [ADD_4_CARD]):
            actions.append("{} hit {} with a {}!".format(
                    self.get_current_player().get_name(),
                    self.get_next_player().get_name(),
                    "+2" if card in ADD_2_CARDS else "+4"
            ))
        if len(self.get_current_player().cards) == 1:
            await self.add_action("❗ ❗ {} has uno ❗ ❗".format(self.get_current_player().get_name()))

        for action in actions:
            await self.add_action(action)
        
        # Update each player's message
        #   that has not already been sent a message based off the card
        for player in self.players:
            if player.id != self.get_current_player().id:
                await player.show_card(self, card, extras = extras + actions)
    
    async def show_winner(self):
        """Displays the winner of this game to everyone"""

        await self.add_action("{} won the game!".format(self.get_current_player().get_name()))
        for player in self.players:
            await player.show_winner(self)
    
    async def kick_player_out(self):
        """Kicks the current player out and notifies the rest of the players"""
        removed_player = self.get_current_player()
        self.players.remove(removed_player)
        for player in self.players:
            if not player.is_ai:
                await player.member.send(
                    embed = Embed(
                        title = "{} left!".format(removed_player.get_name()),
                        description = "{} left the game.{}".format(
                            removed_player.get_name(),
                            "There are not enough players left in the game to continue playing." if len(self.players) < 2 else ""
                        ),
                        colour = await get_embed_color(player.member)
                    ),
                    delete_after = 10 if len(self.players) >= 2 else None
                )

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Other Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def reverse(self):
        """Reverses the playing order of this Uno game whenever a reverse card
        is placed down
        """
        self.increase = 1 if self.increase == -1 else -1
        
    def get_valid_cards(self):
        """Returns a list of valid cards that can be played in reference
        to whatever card is on top

        :rtype: list
        """

        valid_cards = []
        for card in self.get_current_player().cards:

            # Wild cards are always valid
            if card in WILD_CARDS:
                valid_cards.append(card)
            
            # As long as the color of the card or number of the card is the same,
            #   the card is valid
            elif card[1] == self.card[1] or card[2] == self.card[2]:
                valid_cards.append(card)
        
        # The draw "card" is always valid as well
        valid_cards.append(DRAW_UNO)
        return valid_cards
    
    def new_turn(self, player = None):
        """Creates a new Turn object for this Game."""
        self.current_turn = Turn(self)
    
    async def add_action(self, action):
        """Adds a new action to the current turn object in the game

        :param action: The action that happened in this turn
        """
        await self.current_turn.add_action(action)
