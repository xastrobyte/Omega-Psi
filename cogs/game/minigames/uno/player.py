from asyncio import sleep
from discord import Embed
from random import choice

from cogs.globals import LEAVE

from cogs.game.minigames.base_game.player import Player
from cogs.game.minigames.uno.variables import COLOR_CARDS, UNO_CARDS, DRAW_UNO

from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class UnoPlayer(Player):
    """An UnoPlayer object holds information about a player in an Uno game

    Keyword Parameters
    ------------------
        member : discord.Member or str
            The discord.Member defining this Player object or
            a str clarifying this Player object as an AI player
        is_smart : boolean
            A boolean value determining if this Player is playing smart or random
            Note: this only applies to AI players and is only set to True or False if
                    this player is an AI player
    """

    def __init__(self, member):
        super().__init__(member = member)

        # Player information
        self.cards = []
        self.message = None
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Getters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    @property
    def cards(self):
        return self.__cards
    
    @property
    def message(self):
        return self.__message
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Setters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @cards.setter
    def cards(self, cards):
        self.__cards = cards
    
    @message.setter
    def message(self, message):
        self.__message = message
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Play Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def setup(self):
        """Setups the player by giving them 7 random uno cards"""
        for i in range(7):
            self.cards.append(choice(UNO_CARDS))

    async def wait_for_card(self, game):
        """Waits for this player to choose a card to place down

        Parameters
        ----------
            game : UnoGame
                The game object this player is connected to

        Returns
        -------
            card : str
                The card this player chose
        """

        # Get all the valid cards that can be current chosen
        valid_cards = game.get_valid_cards()

        # Check if the player is an AI, choose a random valid card
        if self.is_ai:
            await sleep(2)
            return choice(valid_cards)
        
        # The player is a real person
        else:

            # Send the user a message asking which card they want to place down
            #   as long as it's a valid card
            message = await self.member.send(
                embed = Embed(
                    title = "Your Turn!",
                    description = "{}\n{}".format(
                        "Current Card: <{}>".format(game.card),
                        "Your Cards: {}".format(" ".join([
                            "<{}>".format(card) for card in self.cards 
                        ]))
                    ),
                    colour = await get_embed_color(self.member)
                )
            )

            # Add the valid cards as reactions to the message
            #   and ask the user to choose a valid card
            #   add the LEAVE reaction too in case the player wants to leave the game
            for card in valid_cards:
                await message.add_reaction(card)
            await message.add_reaction(LEAVE)
            reaction, user = await game.bot.wait_for("reaction_add", check = lambda reaction, user : (
                reaction.message.id == message.id and
                user.id == self.member.id and
                (str(reaction).replace("<", "").replace(">", "") in valid_cards or str(reaction) == LEAVE)
            ))
            if str(reaction) not in [ DRAW_UNO, LEAVE ]:
                self.cards.remove(str(reaction).replace("<", "").replace(">", ""))
            return str(reaction).replace("<", "").replace(">", "")
    
    async def show_turn(self, game):
        """Sends a message to this player displaying who's turn it is.
        The current player of the game does not receive this message though because they
        are sent a separate message
        """

        # Only send the message if this player is not an AI and if 
        #   the game's current player is not this player
        if game.get_current_player().id != self.id and not self.is_ai:
            self.message = await self.member.send(
                embed = Embed(
                    title = "{}'s turn!".format(game.get_current_player().get_name()),
                    description = "_ _",
                    colour = await get_embed_color(self.member)
                )
            )
    
    async def show_card(self, game, card, *, extras = []):
        """Shows the current player's card choice to this player unless the game's
        current player is this player. The current player of the game already chose
        their card so they know what they chose

        Parameters
        ----------
            game : UnoGame
                The game this player is connected to
            card : str
                The card the current player chose
        
        Keyword Parameters
        ------------------
            extras : str[]
                A list of extra information to add to the message
        """

        # Only send the message if this player is not an AI and if 
        #   the game's current player is not this player
        if game.get_current_player().id != self.id and not self.is_ai:
            await self.message.edit(
                embed = Embed(
                    title = "{}'s turn!".format(game.get_current_player().get_name()),
                    description = "{} chose {}{}{}".format(
                        game.get_current_player().get_name(),
                        "<{}>".format(card) if card != DRAW_UNO else DRAW_UNO,
                        "\n{}".format("\n".join(extras)) if len(extras) != 0 else "",
                        "\n❗ ❗ {} has uno ❗ ❗".format(
                            game.get_current_player().get_name()
                        ) if len(game.get_current_player().cards) == 1 else ""
                    ),
                    colour = await get_embed_color(self.member)
                )
            )
    
    async def show_winner(self, game):
        """Displays the winner of the specified game to this player

        Parameters
        ----------
            game : UnoGame
                The game that this player is connected to
        """

        # Only display the winner this player is not an ai
        if not self.is_ai:
            await self.member.send(
                embed = Embed(
                    title = "{} wins!".format(
                        game.get_current_player().get_name()
                    ) if game.get_current_player().id != self.id else "You win!",
                    description = "_ _",
                    colour = await get_embed_color(self.member)
                )
            )
    
    async def ask_for_new_color(self, game):
        """Asks the player to choose a new color for when they choose a wild card

        Parameters
        ----------
            game : UnoGame
                The game object this player is connected to
            
        Returns
        -------
            card : str
                The new colored card the player chose
        """

        # Check if the player is an ai
        if self.is_ai:
            await sleep(2)
            return choice(COLOR_CARDS)

        # The player is a real person
        else:
        
            # Send a message asking the player which card they want to choose
            message = await self.member.send(
                embed = Embed(
                    title = "Choose a color!",
                    description = "Choose a new color",
                    colour = await get_embed_color(self.member)
                )
            )
            for card in COLOR_CARDS:
                await message.add_reaction(card)
            
            # Wait for the player to choose their card and return it
            reaction, user = await game.bot.wait_for("reaction_add", check = lambda reaction, user: (
                reaction.message.id == message.id and
                user.id == self.member.id and
                str(reaction).replace("<", "").replace(">", "") in COLOR_CARDS
            ))
            await message.delete()

            return str(reaction).replace("<", "").replace(">", "")

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Other Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #