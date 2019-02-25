import asyncio, discord
from random import randint, choice

from category.globals import PRIMARY_EMBED_COLOR

UNO_CARDS = [
    ':R1:548418410032136192', ':R2:548418424225923082', ':R3:548418445901955092', ':R4:548418445822263296', ':R5:548418445364953091', ':R6:548418445784645642', ':R7:548418445658554378', ':R8:548418445797228554', ':R9:548418445906149386', ':RS:548418445914538007', ':RR:548418445495238657', ':RP:548418445952417792', 
    ':G1:548418930167775232', ':G2:548418931984171039', ':G3:548418934295232512', ':G4:548418936639848468', ':G5:548418938254393366', ':G6:548418940972433408', ':G7:548418943627558912', ':G8:548418945854603279', ':G9:548418948559929354', ':GS:548418954545332225', ':GR:548418954285154305', ':GP:548418955002511380', 
    ':B1:548418711745200139', ':B2:548418713972637706', ':B3:548418737468997652', ':B4:548418718401691648', ':B5:548418720960217088', ':B6:548418737036984331', ':B7:548418725624152084', ':B8:548418737028595723', ':B9:548418737515134976', ':BS:548418737582243841', ':BR:548418736965681162', ':BP:548418737821319168', 
    ':Y1:548419099299020832', ':Y2:548419100997713923', ':Y3:548419103262638090', ':Y4:548419104604946432', ':Y5:548419106034941954', ':Y6:548419107830366222', ':Y7:548419109705089026', ':Y8:548419111814955008', ':Y9:548419113899261952', ':YS:548419115962990612', ':YR:548419119373090846', ':YP:548419117133070351', 
    ':R1:548418410032136192', ':R2:548418424225923082', ':R3:548418445901955092', ':R4:548418445822263296', ':R5:548418445364953091', ':R6:548418445784645642', ':R7:548418445658554378', ':R8:548418445797228554', ':R9:548418445906149386', ':RS:548418445914538007', ':RR:548418445495238657', ':RP:548418445952417792', 
    ':G1:548418930167775232', ':G2:548418931984171039', ':G3:548418934295232512', ':G4:548418936639848468', ':G5:548418938254393366', ':G6:548418940972433408', ':G7:548418943627558912', ':G8:548418945854603279', ':G9:548418948559929354', ':GS:548418954545332225', ':GR:548418954285154305', ':GP:548418955002511380', 
    ':B1:548418711745200139', ':B2:548418713972637706', ':B3:548418737468997652', ':B4:548418718401691648', ':B5:548418720960217088', ':B6:548418737036984331', ':B7:548418725624152084', ':B8:548418737028595723', ':B9:548418737515134976', ':BS:548418737582243841', ':BR:548418736965681162', ':BP:548418737821319168', 
    ':Y1:548419099299020832', ':Y2:548419100997713923', ':Y3:548419103262638090', ':Y4:548419104604946432', ':Y5:548419106034941954', ':Y6:548419107830366222', ':Y7:548419109705089026', ':Y8:548419111814955008', ':Y9:548419113899261952', ':YS:548419115962990612', ':YR:548419119373090846', ':YP:548419117133070351', 
    ':WR:548419419647246337', ':W4:548419419395850265', ':WR:548419419647246337', ':W4:548419419395850265'
]

COLOR_CARDS = [
    ":R1:548418410032136192", ":G1:548418930167775232",
    ":B1:548418711745200139", ":Y1:548419099299020832"
]

RED_CARD = COLOR_CARDS[0]
GREEN_CARD = COLOR_CARDS[1]
BLUE_CARD = COLOR_CARDS[2]
YELLOW_CARD = COLOR_CARDS[3]

SKIP_CARDS = [
    ":RS:548418445914538007", ":BS:548418737582243841", 
    ":GS:548418954545332225", ":YS:548419115962990612"
]

REVERSE_CARDS = [
    ":RR:548418445495238657", ":BR:548418736965681162",
    ":GR:548418954285154305", ":YR:548419119373090846"
]

ADD_2_CARDS = [
    ":RP:548418445952417792", ":BP:548418737821319168",
    ":GP:548418955002511380", ":YP:548419117133070351"
]

ADD_4_CARD = ":W4:548419419395850265"

WILD_CARDS = [
    ":WR:548419419647246337", ":W4:548419419395850265"
]

DRAW_UNO = "❓"
QUIT = "❌"
CHALLENGE = "✅"
NO_CHALLENGE = "❎"

class Player:

    def __init__(self, member):
        self._member = member

        self._cards = []
        self._message = None

    def get_player(self):
        return self._member
    
    def get_cards(self):
        return self._cards
    

    def add_card(self, card):
        self._cards.append(card)

    async def show_turn(self, game):

        # Get current player
        current_player = game.get_current_player().get_player()

        # Only show cards and reactions if current player is this player
        if current_player.id == self.get_player().id:

            # Create embed and send message
            self._message = await self.get_player().send(
                embed = discord.Embed(
                    title = "Current Card",
                    description = "<{}>\nYour Cards: {}".format(
                        game.get_current_card(),
                        " ".join([
                            "<{}>".format(
                                card
                            )
                            for card in self._cards
                        ])
                    ),
                    colour = PRIMARY_EMBED_COLOR
                )
            )

            # Add card reactions if card is valid
            for card in self.get_cards():
                if valid_card(game.get_current_card(), card):
                    await self._message.add_reaction(card)
            
            # Now add draw reaction
            await self._message.add_reaction(DRAW_UNO)
            await self._message.add_reaction(QUIT)

        # Current player is not this player, say whose turn it is
        else:
            
            # Create embed and send message
            self._message = await self.get_player().send(
                embed = discord.Embed(
                    title = "_ _",
                    description = "It is {}'s turn.".format(
                        game.get_current_player().get_player().mention
                    ),
                    colour = PRIMARY_EMBED_COLOR
                )
            )

class Uno:

    END_GAME = "END_GAME"

    def __init__(self, players, channel, bot):
        self._players = [Player(player) for player in players]

        # Choose random starting player
        self._current = randint(0, len(players) - 1)
        self._inc = 1 # Used for the reverse card changes

        # Choose random card to be on top
        self._card = choice(UNO_CARDS)

        self._channel = channel
        self.bot = bot

        self._message = None
    
    def get_players(self):
        return self._players
    
    def get_current_player(self):
        return self._players[self._current]
    
    def get_current_card(self):
        return self._card
    
    def get_next_player(self):
        current = self._current
        current += self._inc

        if current >= len(self._players):
            current = 0
        if current < 0:
            current = len(self._players) - 1

        return self._players[current]

    def next_player(self, *, skip = False):
        self._current += self._inc
        if skip:
            self._current += self._inc
        
        if self._current >= len(self._players):
            self._current -= len(self._players)
        if self._current < 0:
            self._current += len(self._players)
        
    def set_card(self, card):
        self._card = card
    
    def give_cards(self):

        # Iterate through players and give each one random cards (7)
        for player in self._players:
            for card in range(7):
                player.add_card(choice(UNO_CARDS))
        
    async def show_turn(self):

        # Send message to channel saying whose turn
        self._message = await self._channel.send(
            embed = discord.Embed(
                title = "Uno",
                description = "It is {}'s turn".format(
                    self.get_current_player().get_player().mention
                ),
                colour = PRIMARY_EMBED_COLOR
            )
        )

        # Send message to all players
        for player in self._players:
            await player.show_turn(self)
    
    async def wait_for_card(self):

        # Check for a valid card
        while True:
            def check_reaction(reaction, user):
                return reaction.message.id == self.get_current_player()._message.id and user.id == self.get_current_player().get_player().id and (str(reaction) in [DRAW_UNO, QUIT] or str(reaction).replace("<", "").replace(">", "") in UNO_CARDS)
            
            reaction, user = await self.bot.wait_for("reaction_add", check = check_reaction)
            reaction = str(reaction).replace("<", "").replace(">", "")

            if str(reaction) == DRAW_UNO or str(reaction) == QUIT or valid_card(self.get_current_card(), str(reaction)):
                break
            
            else:
                await user.send(
                    "You can't use that card yet!",
                    delete_after = 5
                )
        
        current_player = self.get_current_player()
    
        # Check if player wants to quit
        if str(reaction) == QUIT:
            self._players.pop(self._current)

            await notify(
                self,
                current_player,
                "Someone Left!",
                "{} left the game :angry:".format(current_player.get_player().mention)
            )

            # Check if there is only 1 player
            if len(self._players) < 2:
                await notify(
                    self,
                    current_player,
                    "Not Enough People",
                    "There are less than 2 people so we gotta stop this game :frowning2:"
                )

                return Uno.END_GAME
            
            return None

        # Make sure reaction wasn't a draw reaction
        if not str(reaction) == DRAW_UNO:

            # Put card on top of pile
            self.set_card(str(reaction))

            # Remove card from player's hand
            current_player._cards.remove(str(reaction))

        # Check how many cards current player has
        if len(current_player._cards) == 1:
            await notify(
                self,
                current_player,
                "❗ ❗ UNO ❗ ❗",
                "{} has Uno!".format(
                    current_player.get_player().mention
                )
            )
        
        # Check if player won
        elif (len(self.get_current_player()._cards)) == 0:
            return current_player.get_player()

        wild_select = None

        # Check if card is draw
        if str(reaction) == DRAW_UNO:
            current_player.add_card(choice(UNO_CARDS))
            self.next_player()

        # Check if card is a reverse card
        elif str(reaction) in REVERSE_CARDS:

            # Check if there are more than two players; Reverse order
            # If there are only 2 players, card acts as a skip; Don't do anything
            if len(self._players) > 2:
                self._inc = -self._inc
                self.next_player()
            
            await notify(
                self, 
                current_player,
                "Reversed!", "{} used a reverse card!".format(
                    current_player.get_player().mention
                )
            )

        # Check if card is a skip card
        elif str(reaction) in SKIP_CARDS:

            await notify(
                self, 
                current_player,
                "Skipped!", 
                "{} was skipped!".format(
                    self.get_next_player().get_player().mention
                ),
                special_next = "oooooofff. You were skipped."
            )

            self.next_player(skip = True)

        # Check if card is a wild card
        elif str(reaction) in WILD_CARDS:

            # Ask player to choose a color
            msg = await current_player.get_player().send(
                embed = discord.Embed(
                    title = "Choose a Color",
                    description = "Choose a new color",
                    colour = PRIMARY_EMBED_COLOR
                )
            )

            # Add color cards
            for card in COLOR_CARDS:
                await msg.add_reaction(card)
            
            # Wait for reaction
            def check_color_reaction(reaction, user):
                return reaction.message.id == msg.id and user.id == current_player.get_player().id and str(reaction).replace("<", "").replace(">", "") in COLOR_CARDS

            wild_reaction, user = await self.bot.wait_for("reaction_add", check = check_color_reaction)
            wild_reaction = str(wild_reaction).replace("<", "").replace(">", "")

            # Add card to top of pile
            self.set_card(str(wild_reaction))

            # Check what color it is
            if str(wild_reaction) == RED_CARD:
                wild_select = "red"
            
            elif str(wild_reaction) == BLUE_CARD:
                wild_select = "blue"
            
            elif str(wild_reaction) == YELLOW_CARD:
                wild_select = "yellow"
            
            elif str(wild_reaction) == GREEN_CARD:
                wild_select = "green"
            
            # Check if the card is also a +4 card
            if str(reaction) == ADD_4_CARD:
                await notify(
                    self,
                    current_player,
                    "+4!",
                    "{} was hit with +4 card. oof.".format(self.get_next_player().get_player().mention),
                    special_next = "You were hit with a +4!\n¯\_(ツ)_/¯"
                )

                for card in range(4):
                    self.get_next_player().add_card(choice(UNO_CARDS))
            
            self.next_player()
        
        # Check if the card adds 2 to the next player
        elif str(reaction) in ADD_2_CARDS:
            await notify(
                self,
                current_player,
                "+2!",
                "{} was hit with a +2 card. oof.".format(self.get_next_player().get_player().mention),
                special_next = "You were hit with a +2!\n¯\_(ツ)_/¯"
            )

            for card in range(2):
                self.get_next_player().add_card(choice(UNO_CARDS))

            self.next_player()
        
        # Regular cards
        else:
            self.next_player()

        # Update channel message
        await self._message.edit(
            embed = discord.Embed(
                title = "Uno",
                description = "{} chose {}\n{}".format(
                    current_player.get_player().mention,
                    "<{}>".format(
                        str(reaction)
                    ) if str(reaction) not in [DRAW_UNO, QUIT] else str(reaction),
                    "" if wild_select == None else ("The new color is " + wild_select)
                ),
                colour = PRIMARY_EMBED_COLOR
            )
        )

        # Update everybody's message
        for player in self._players:
            await player._message.edit(
                embed = discord.Embed(
                    title = "Uno",
                    description = "{} chose {}\n{}".format(
                        current_player.get_player().mention if player != current_player else "You",
                        "<{}>".format(
                            str(reaction)
                        ) if str(reaction) not in [QUIT, DRAW_UNO] else str(reaction),
                        "" if wild_select == None else ("The new color is " + wild_select)
                    ),
                    colour = PRIMARY_EMBED_COLOR
                )
            )

def valid_card(current_card, reaction):
    reaction = str(reaction)

    # Check if reaction is a wild card
    if reaction in WILD_CARDS:
        return True

    # Get slice of card identifier
    current_card = current_card[1:3]
    reaction = reaction[1:3]

    # Check if card color is same or number is same
    return current_card[0] == reaction[0] or current_card[1] == reaction[1]

async def notify(game, current_player, title, message, special_next = None):

    # Send message to channel
    await game._channel.send(
        embed = discord.Embed(
            title = title,
            description = message,
            colour = PRIMARY_EMBED_COLOR
        )
    )

    # See if there is a special message for the next player
    if special_next != None:
        await game.get_next_player().get_player().send(
            embed = discord.Embed(
                title = title,
                description = special_next,
                colour = PRIMARY_EMBED_COLOR
            )
        )

    # Send message to all players (except current)
    for player in game.get_players():

        if player.get_player().id != current_player.get_player().id or (special_next != None and game.get_next_player().get_player().id != player.get_player().id):

            await player.get_player().send(
                embed = discord.Embed(
                    title = title,
                    description = message,
                    colour = PRIMARY_EMBED_COLOR
                )
            )