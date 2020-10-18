from asyncio import sleep, wait, FIRST_COMPLETED
from discord import Embed
from random import choice

from cogs.game.minigames.base_game.player import Player
from cogs.game.minigames.kings_cup.variables import QUIT, DRAW_CARD, KINGS_CUP_CARDS, NEXT

from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class KingsCupPlayer(Player):
    """A KingsCupPlayer object holds information regarding a player in the Kings Cup minigame.

    Parameters
    ----------
        member : Member or int
            The Member defining this KingsCupPlayer object or
            an int clarifying this KingsCupPlayer object as an AI player
    """
    
    def __init__(self, member):
        super().__init__(member = member)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Play Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def process_turn(self, game):
        """Processes the current turn for this player by waiting until they
        react to make their move or, if this player is an AI, choosing the best place
        to go

        Parameters
        ----------
            game : KingsCupGame
                The game object that this player is connected to
        """
        
        # The player is not an AI, wait for them to choose a place to go
        if not self.is_ai:

            # Ask the player to react with their choice
            message = await game.ctx.send(
                embed = Embed(
                    title = "Draw a card!",
                    description = "React with {} to draw a card or react with {} to quit the game!".format(
                        DRAW_CARD, QUIT
                    ),
                    colour = await get_embed_color(self.member)
                )
            )
            await message.add_reaction(DRAW_CARD)
            await message.add_reaction(QUIT)
            
            # Wait for the player to react with the spot they want to go
            def check_reaction(reaction, user):
                return (
                    reaction.message.id == message.id and
                    user.id == self.member.id and
                    str(reaction) in [ DRAW_CARD, QUIT ]
                )
            done, pending = await wait([
                game.bot.wait_for("reaction_add", check = check_reaction),
                game.bot.wait_for("reaction_remove", check = check_reaction)
            ], return_when = FIRST_COMPLETED)
            reaction, user = done.pop().result()
            await message.delete()
            for future in pending:
                future.cancel()

            # Check if the player wants to QUIT the KingsCupGame
            if str(reaction) == QUIT:
                return QUIT
            
        card = choice(list(KINGS_CUP_CARDS.keys()))
        while game.drawn_cards.count(card) >= 4:
            card = choice(list(KINGS_CUP_CARDS.keys()))
        return card
    
    async def send_card(self, game, card):
        """Sends a card to the player

        Parameters
        ----------
            card : string
                The card that is being sent to the player
        """
        card = KINGS_CUP_CARDS[card]
        if not self.is_ai:
            message = await self.member.send(
                embed = Embed(
                    title = card["title"],
                    description = "{}\n\nReact with {} to move to the next player!".format(card["description"], NEXT),
                    colour = await get_embed_color(self.member)
                )
            )
            await message.add_reaction(NEXT)

            # Wait for the player to react with the NEXT emoji to move to the next player's turn
            def check_reaction(reaction, user):
                return (
                    reaction.message.id == message.id and
                    user.id == self.member.id and
                    str(reaction) == NEXT
                )
            reaction, user = await game.bot.wait_for("reaction_add", check = check_reaction)
            await message.delete()
    
    async def ask_for_rule(self, game):
        """Asks the player for a new rule to the game

        Parameters
        ----------
            game : KingsCupGame
                The KingsCupGame that this player is connected to
            
        Returns
        -------
            str
                The new rule to be added to the game
        """
        
        # Wait for the player to type a rule
        if not self.is_ai:
            message = await game.bot.wait_for("message", check = lambda message: (
                message.author.id == self.id and
                message.channel.id == game.ctx.channel.id
            ))
            rule = message.content
            await message.delete()
            return rule
        return None