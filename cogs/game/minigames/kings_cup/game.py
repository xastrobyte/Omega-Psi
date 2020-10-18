from asyncio import sleep
from discord import Embed
from random import choice

from cogs.game.minigames.base_game.game import Game
from cogs.game.minigames.kings_cup.player import KingsCupPlayer
from cogs.game.minigames.kings_cup.turn import KingsCupTurn
from cogs.game.minigames.kings_cup.variables import KINGS_CUP_CARDS, QUIT

from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class KingsCupGame(Game):
    """A KingsCupGame object that holds information about a Kings Cup game

    Parameters
    ----------
        bot : AutoShardedBot
            The bot object used to wait for reactions
        ctx : context
            The context of where this game is being played
        players : Member[]
            A list of discord members that are playing this Kings Cup game
    """

    def __init__(self, bot, ctx, players):
        super().__init__(
            bot, ctx,
            players = [
                KingsCupPlayer(player)
                for player in players
            ]
        )
        self.rules = []
        self.drawn_cards = []
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Getters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @property
    def rules(self):
        return self.__rules
    
    @property
    def drawn_cards(self):
        return self.__drawn_cards

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Setters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @rules.setter
    def rules(self, rules):
        self.__rules = rules
    
    @drawn_cards.setter
    def drawn_cards(self, drawn_cards):
        self.__drawn_cards = drawn_cards
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Play Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def play(self):
        """Let's the players in this game play a Kings Cup game"""

        # Continue playing the game until the dealer quits
        while len(self.drawn_cards) != 52:
            self.new_turn()

            # Ask the player to draw a card
            card = await self.get_current_player().process_turn(self)

            # Check if the player is quitting the game
            if card == QUIT:
                await self.add_action("{} left the game!".format(self.get_current_player().get_name()))
                self.players.remove(self.get_current_player())
                self.current_player -= 1
            
            # Send the card to the dealer if the card is Tongues (6) or Hands (7)
            else:
                self.drawn_cards.append(card)
                if card in ["6", "7"]:
                    await self.get_current_player().send_card(self, card)
                
                # Send the card to the game channel otherwise
                else:
                    await self.add_action("```\n{}\n\t{}\n```".format(
                        KINGS_CUP_CARDS[card]["title"],
                        KINGS_CUP_CARDS[card]["description"]
                    ))

                    # Check if the card is a Waterfall (Ace), Rhyme Time (9), or Categories (10)
                    #   add the list of players to the turn message so people know who goes next
                    if card in ["Ace", "9", "10"]:
                        await self.add_action("\n".join([
                            "{}".format(player.get_name())
                            for player in self.players
                        ]))

                    # Check if the card is a rules card, ask the dealer to type a new rule
                    elif card == "5":
                        rule = await self.get_current_player().ask_for_rule(self)
                        if rule is not None:
                            self.rules.append(rule)
                            await self.add_action("**New Rule**! *{}*".format(rule))
                
                self.next_player()
        
        # Send a message saying the game is finished
        await self.ctx.send(
            embed = Embed(
                title = "King's Cup is over!",
                description = "Bye :)",
                colour = await get_embed_color(self.get_current_player())
            )
        )
    
    def new_turn(self, player = None):
        """Creates a new Turn object for this Game."""
        self.current_turn = KingsCupTurn(self)
    
    async def add_action(self, action):
        """Adds a new action to the current turn object in the game

        Parameters
        ----------
            action : str
                The action that happened in this turn
        """
        await self.current_turn.add_action(action)