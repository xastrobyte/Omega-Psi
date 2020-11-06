from discord import Embed
from random import randrange

from cogs.globals import NUMBER_EMOJIS, LEAVE

from cogs.game.minigames.base_game.player import Player

from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class CardsAgainstHumanityPlayer(Player):
    """A CardsAgainstHumanityPlayer object holds information regarding 
    a player in the Cards Against Humanity minigame.

    :param member: The discord member that will be connected to this Player
    """

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Nested Classes
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    class Submission:
        """A Submission object holds information about the submission of a player during
        a round of Cards Against Humanity

        :param player: The player that this submission is connected to
        """

        def __init__(self, player):
            self.player = player
            self.cards = []
        
        def __str__(self):
            return "\n".join([ card.text for card in self.cards ])

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Getters
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        @property
        def player(self):
            return self.__player
        
        @property
        def cards(self):
            return self.__cards

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Setters
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #    
    
        @player.setter
        def player(self, player):
            self.__player = player
        
        @cards.setter
        def cards(self, cards):
            self.__cards = cards

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    DEFAULT_HAND_SIZE = 7 # This is the amount of cards given to a player
                          # when the game begins and the player is being set up

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    def __init__(self, member):
        super().__init__(member = member)

        # Keep track of the player's white cards
        #   and how many times they've won
        #   Also keep track of the player's current submission
        self.cards = []
        self.wins = 0

        # Keep track of the message sent to this user
        #   that is used when updating the current state of the game
        self.message = None
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Getters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @property
    def cards(self):
        return self.__cards
    
    @property
    def wins(self):
        return self.__wins
    
    @property
    def message(self):
        return self.__message

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Setters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @cards.setter
    def cards(self, cards):
        self.__cards = cards
    
    @wins.setter
    def wins(self, wins):
        self.__wins = wins

    @message.setter
    def message(self, message):
        self.__message = message
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Play Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def ask_for_submission(self, game):
        """Asks the player to submit their card(s) for their submission
        If this player is the current player in the game (the judge), 
        they will not be asked for their submission

        :param game: The game object that this player is connected to
        """

        # Check if this player is the current judge in the game
        if self.id == game.get_current_player().id:
            await self.member.send(
                embed = Embed(
                    title = "Round {}".format(game.round),
                    description = "You are the judge this round. Just sit back and wait until everyone has submitted their cards!\n{}".format(
                        str(game.current_black_card)
                    ),
                    colour = await get_embed_color(self.member)
                ).add_field(
                    name = "*Scores*",
                    value = "\n".join([
                        "*{}* - **{}**".format(
                            player.get_name(),
                            player.wins
                        )
                        for player in game.players
                    ])
                )
            )
            return None
        
        # This player is not the current judge, send them their cards and ask for them to
        #   choose a card (or cards)
        else:
            
            # Create the embed that holds all the player's card options
            #   as fields in the embed
            embed = Embed(
                title = "Round {}".format(game.round),
                description = "**Judge**: {}\n{}\n{}".format(
                    game.get_current_player().get_name(),
                    "You can choose {} cards this round!".format(game.current_black_card.pick) if game.current_black_card.pick > 1 else "",
                    str(game.current_black_card)
                ),
                colour = await get_embed_color(self.member)
            )
            for i in range(len(self.cards)):
                embed.add_field(
                    name = NUMBER_EMOJIS[i],
                    value = str(self.cards[i]),
                    inline = False
                )
            
            # Add the scores to the embed
            embed.add_field(
                name = "*Scores*",
                value = "\n".join([
                    "*{}* - **{}**".format(
                        player.get_name(),
                        player.wins
                    )
                    for player in game.players
                ])
            )

            # Send the message to the player and add the reactions that let them choose a card
            #   or cards for their submission
            message = await self.member.send(embed = embed)
            for emoji in NUMBER_EMOJIS[ : len(self.cards)]:
                await message.add_reaction(emoji)
            await message.add_reaction(LEAVE)
        
            # Wait for the user to react with the card they want
            selected = {}
            for card_pick in range(game.current_black_card.pick):
                reaction, user = await game.bot.wait_for("reaction_add", check = lambda reaction, user: (
                    reaction.message.id == message.id and
                    user.id == self.id and
                    (
                        str(reaction) in NUMBER_EMOJIS[ : len(self.cards)] or
                        str(reaction) == LEAVE
                    ) and
                    str(reaction) not in selected
                ))
                
                # Check if the player wants to leave
                if str(reaction) == LEAVE:
                    submission = CardsAgainstHumanityPlayer.Submission(self)
                    submission.cards.append(LEAVE)
                    return submission
                
                # The player chose a card
                selected[str(reaction)] = self.cards.pop(NUMBER_EMOJIS.index(str(reaction)))
            await message.delete()

            # Add each card to the player's submission and return the submission
            submission = CardsAgainstHumanityPlayer.Submission(self)
            for card in selected:
                submission.cards.append(selected[card])
            return submission

    async def show_submissions(self, game):
        """Shows the current submissions for this game once all the cards are in

        :param game: The game object that this player is connected to
        """

        # Check if this player is the judge
        if self.id == game.get_current_player().id:

            # Create the embed, linking each submission to a reaction
            embed = Embed(
                title = "Round {}".format(game.round),
                description = "**Black Card**\n{}".format(
                    str(game.current_black_card)
                ),
                colour = await get_embed_color(self.member)
            )
            
            # Add each submission as a field and link it to a reaction
            #   for the judge to choose
            for i in range(len(game.submissions)):
                embed.add_field(
                    name = NUMBER_EMOJIS[i],
                    value = "```md\n<\n{}\n>\n```".format(str(game.submissions[i])),
                    inline = False
                )
            embed.add_field(
                name = "*Scores*",
                value = "\n".join([
                    "*{}* - **{}**".format(
                        player.get_name(),
                        player.wins
                    )
                    for player in game.players
                ])
            )
            
            # Send the message to the judge and wait for their reaction to choose a submission
            self.message = await self.member.send(embed = embed)
            for emoji in NUMBER_EMOJIS[ : len(game.submissions)]:
                await self.message.add_reaction(emoji)
            reaction, user = await game.bot.wait_for("reaction_add", check = lambda reaction, user: (
                reaction.message.id == self.message.id and
                user.id == self.id and
                str(reaction) in NUMBER_EMOJIS[ : len(game.submissions)]
            ))
            return game.submissions[NUMBER_EMOJIS.index(str(reaction))]
        
        # This player is not the judge
        else:
            self.message = await self.member.send(
                embed = Embed(
                    title = "Round {}".format(game.round),
                    description = "**Judge**: {}\n**Black Card**\n{}\n\n{}".format(
                        game.get_current_player().get_name(),
                        str(game.current_black_card),
                        "\n".join([
                            "```md\n<\n{}\n>\n```".format(
                                str(submission)
                            )
                            for submission in game.submissions
                        ])
                    ),
                    colour = await get_embed_color(self.member)
                ).add_field(
                    name = "*Scores*",
                    value = "\n".join([
                        "*{}* - **{}**".format(
                            player.get_name(),
                            player.wins
                        )
                        for player in game.players
                    ])
                )
            )
    
    async def show_results(self, game, winning_submission):
        """Shows the results for the current round of the game
        Each player's name will be displayed along with their card

        :param game: The game object that this player is connected to
        :param winning_submission: The card submission that won the current round of the game
        """
        
        # Update the player's message with each player's submission matched with their name
        #   the winning player's submission will be boldened
        await self.message.edit(
            embed = Embed(
                title = "Round {}".format(game.round),
                description = "{} Won!\n\n**Judge**: {}\n**Black Card**\n{}\n\n{}".format(
                    winning_submission.player.get_name() 
                        if self.id != winning_submission.player.id
                        else "You",
                    game.get_current_player().get_name(),
                    str(game.current_black_card),
                    "\n".join([
                        "{}```md\n{}\n{}\n<\n{}\n>\n```{}".format(
                            "**_" if submission.player.id == winning_submission.player.id else "",
                            submission.player.get_name(),
                            "=" * len(submission.player.get_name()),
                            str(submission),
                            "_**" if submission.player.id == winning_submission.player.id else "",
                        )
                        for submission in game.submissions
                    ])
                ),
                colour = await get_embed_color(self.member)
            ).add_field(
                name = "*Scores*",
                value = "\n".join([
                    "*{}* - **{}**".format(
                        player.get_name(),
                        player.wins
                    )
                    for player in game.players
                ])
            )
        )

    async def show_winner(self, game, winner):
        """Shows the winner of the game

        :param game: The game object that this player is connected to
        :param winner: The winner of the Cards Against Humanity game
        """
        await self.member.send(
            embed = Embed(
                title = "{} won!".format(winner.get_name() if winner.id != self.id else "You"),
                description = "_ _",
                colour = await get_embed_color(self.member)
            ).add_field(
                name = "*Scores*",
                value = "\n".join([
                    "*{}* - **{}**".format(
                        player.get_name(),
                        player.wins
                    )
                    for player in game.players
                ])
            )
        )

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Other Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    def give_cards(self, game):
        """Gives the player as many cards as needed specified by the amount of cards
        the player will have to pick

        :param game: The game object that this player is connected to
        """

        # If the player does not have 7 cards, give them as many cards as it takes
        #   to get them to seven cards
        # Only give the player extra cards if pick is greater than 1
        #   if this is the case, the amount of extra cards given should
        #   be pick - 1
        pick = game.current_black_card.pick
        if self.id != game.get_current_player().id:
            for card in range(CardsAgainstHumanityPlayer.DEFAULT_HAND_SIZE - len(self.cards) + (pick - 1)):
                self.cards.append(game.white_cards.pop(randrange(len(game.white_cards))))