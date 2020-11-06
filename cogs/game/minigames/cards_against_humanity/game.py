from asyncio import wait, sleep, ALL_COMPLETED
from discord import Embed
from random import shuffle
from requests import get

from cogs.globals import LEAVE

from cogs.game.minigames.base_game.game import Game
from cogs.game.minigames.cards_against_humanity.cards import BlackCard, WhiteCard
from cogs.game.minigames.cards_against_humanity.player import CardsAgainstHumanityPlayer
from cogs.game.minigames.cards_against_humanity.turn import CardsAgainstHumanityTurn

from util.database.database import database
from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

CAH_SETS_API = "https://cards-against-humanity-api.herokuapp.com/sets"
CAH_SET_CARDS_API = "https://cards-against-humanity-api.herokuapp.com/sets/{}"

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class CardsAgainstHumanityGame(Game):
    """A CardsAgainstHumanityGame object that holds information about a Cards Against Humanity game.
    When this object is created, all sets available at https://cards-against-humanity-api.herokuapp.com/sets
    are loaded including each white and black card.

    :param bot: The bot object used to wait for reactions
    :param ctx: The context of where this game is being played
    :param players: A list of players that are playing this game
    """

    def __init__(self, bot, ctx, players):
        super().__init__(bot, ctx, players = 
            [ CardsAgainstHumanityPlayer(player) for player in players ]
        )

        # Keep track of all white cards and black cards
        #   the current round number and the current round submissions
        self.current_black_card = None
        self.black_cards = []
        self.white_cards = []
        self.round = 1
        self.submissions = []

        # Load a list of sets in Cards Against Humanity
        #   using the CARDS_AGAINST_HUMANITY APIs
        sets = get(CAH_SETS_API).json()

        # Iterate through all the sets
        #   and add each white card and black card to their respective lists
        for set in sets:
            set_data = get(CAH_SET_CARDS_API.format(
                set["setName"]
            )).json()
            for black_card in set_data["blackCards"]:
                self.black_cards.append(BlackCard(black_card))
            for white_card in set_data["whiteCards"]:
                self.white_cards.append(WhiteCard(white_card))
        shuffle(self.black_cards)
        shuffle(self.white_cards)
    
        # Keep track of the current turn
        self.current_turn = None
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Getters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @property
    def current_black_card(self):
        return self.__current_black_card
    
    @property
    def black_cards(self):
        return self.__black_cards

    @property
    def white_cards(self):
        return self.__white_cards
    
    @property
    def round(self):
        return self.__round
    
    @property
    def submissions(self):
        return self.__submissions
    
    @property
    def current_turn(self):
        return self.__current_turn

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Setters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @current_black_card.setter
    def current_black_card(self, current_black_card):
        self.__current_black_card = current_black_card
    
    @black_cards.setter
    def black_cards(self, black_cards):
        self.__black_cards = black_cards
    
    @white_cards.setter
    def white_cards(self, white_cards):
        self.__white_cards = white_cards
    
    @round.setter
    def round(self, round):
        self.__round = round
    
    @submissions.setter
    def submissions(self, submissions):
        self.__submissions = submissions
    
    @current_turn.setter
    def current_turn(self, current_turn):
        self.__current_turn = current_turn
            
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Play Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def play(self):
        """Let's the players in this game play Cards Against Humanity"""

        winner = None
        while not winner:
            self.new_turn()

            # Retrieve a random black card for this round and give player's their cards
            self.current_black_card = self.black_cards.pop()
            for player in self.players:
                player.give_cards(self)
            
            # Wait for all the submissions to come in and wait for the judge
            #   to choose their favorite submission
            winning_submission = await self.wait_for_submissions()

            # Show the results of this round, give the winning player a point
            #   and check if the player has reached 7 points
            winning_submission.player.wins += 1
            await self.show_results(winning_submission)
            if winning_submission.player.wins >= 7:
                winner = winning_submission.player
            self.next_judge()
        
        # Show the winner of this game and update everyone's stats
        await self.show_winner(winner)
        for player in self.players:
            await database.users.update_cards_against_humanity(player.member, player.id == winner.id)
    
    async def wait_for_submissions(self):
        """Asks each player to submit their cards for the current black card in the game"""
        
        # Ask each player to make their submissions
        while True:
            done, pending = await wait([
                player.ask_for_submission(self)
                for player in self.players
            ], return_when = ALL_COMPLETED)
            for future in pending:  # There shouldn't be any, but do so just in case
                future.cancel()
            for submission in done:
                if submission.result():
                    self.submissions.append(submission.result())
        
        # Show the submissions to everybody and wait for the judge to choose their favorite submission
        await self.add_action(
            "Everyone submitted their cards!\n{}".format(
                "\n".join([
                    "```md\n<\n{}\n>\n```".format(
                        str(submission)
                    )
                    for submission in self.submissions
                ])
            )
        )
        for player in self.players:
            if player.id != self.get_current_player().id:
                await player.show_submissions(self)
        return await self.get_current_player().show_submissions(self)
    
    async def show_results(self, winning_submission):
        """Shows the results of the current round of the game

        :param winning_submission: The card submission that won the current round of the game
        """
        await self.add_action(
            "{} won this round!\n{}".format(
                winning_submission.player.get_name(),
                "\n".join([
                    "{}```md\n{}\n{}\n<\n{}\n>\n```{}".format(
                        "**_" if submission.player.id == winning_submission.player.id else "",
                        submission.player.get_name(),
                        "=" * len(submission.player.get_name()),
                        str(submission),
                        "_**" if submission.player.id == winning_submission.player.id else "",
                    )
                    for submission in self.submissions
                ])
            )
        )
        for player in self.players:
            await player.show_results(self, winning_submission)
        await sleep(3)
    
    async def show_winner(self, winner):
        """Shows the winner of the game to everyone and ends the game

        :param winner: The winner of this game
        """
        await self.ctx.send(
            embed = Embed(
                title = "{} won the game!".format(winner.get_name()),
                description = "_ _",
                colour = await get_embed_color(winner.member)
            )
        )
        for player in self.players:
            await player.show_winner(self, winner)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Other Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def next_judge(self):
        """Moves to the next judge and increases the round count"""
        super().next_player()
        self.round += 1
        self.submissions = []

    def new_turn(self, player = None):
        """Creates a new Turn object for this Game.
        
        :param player: The player to initiate a turn with
        """
        self.current_turn = CardsAgainstHumanityTurn(self, player)
    
    async def add_action(self, action):
        """Adds a new action to the current turn object in the game

        :param action: The action that happened in this turn
        """
        await self.current_turn.add_action(action)