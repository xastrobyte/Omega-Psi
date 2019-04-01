import asyncio, discord
from random import randint, choice

from category.globals import PRIMARY_EMBED_COLOR

UNO_CARDS = [
    ":R1:549406471633371147", ":R2:549406503602356245", ":R3:549406530298970124", ":R4:549406528642220033", ":R5:549406529602846742", ":R6:549406531347808284", ":R7:549406528470253579", ":R8:549406531079372815", ":R9:549406531700129792", ":RR:549406530437644289", ":RS:549406531679158272", ":RP:549406530932310017", 
    ":G1:549406885946589185", ":G2:549406888127889409", ":G3:549406890812112896", ":G4:549406892787630080", ":G5:549406894956216320", ":G6:549406897053368352", ":G7:549406899460898838", ":G8:549406901763309569", ":G9:549406903969513493", ":GR:549406910944641054", ":GS:549406911171395604", ":GP:549406911410208768", 
    ":B1:549406714248822786", ":B2:549406716912074772", ":B3:549406755847798787", ":B4:549406720854720533", ":B5:549406732485394433", ":B6:549406755722100736", ":B7:549406754254094376", ":B8:549406755701129216", ":B9:549406755680157716", ":BR:549406755218653194", ":BS:549406755596009476", ":BP:549406755755393064", 
    ":Y1:549407012996513803", ":Y2:549407014808453120", ":Y3:549407016607809536", ":Y4:549407018298114060", ":Y5:549407020231688193", ":Y6:549407022215593984", ":Y7:549407023603777547", ":Y8:549407025394745345", ":Y9:549407027911196683", ":YR:549407033720569857", ":YS:549407029656289283", ":YP:549407031757635624", 
    ":R1:549406471633371147", ":R2:549406503602356245", ":R3:549406530298970124", ":R4:549406528642220033", ":R5:549406529602846742", ":R6:549406531347808284", ":R7:549406528470253579", ":R8:549406531079372815", ":R9:549406531700129792", ":RR:549406530437644289", ":RS:549406531679158272", ":RP:549406530932310017", 
    ":G1:549406885946589185", ":G2:549406888127889409", ":G3:549406890812112896", ":G4:549406892787630080", ":G5:549406894956216320", ":G6:549406897053368352", ":G7:549406899460898838", ":G8:549406901763309569", ":G9:549406903969513493", ":GR:549406910944641054", ":GS:549406911171395604", ":GP:549406911410208768", 
    ":B1:549406714248822786", ":B2:549406716912074772", ":B3:549406755847798787", ":B4:549406720854720533", ":B5:549406732485394433", ":B6:549406755722100736", ":B7:549406754254094376", ":B8:549406755701129216", ":B9:549406755680157716", ":BR:549406755218653194", ":BS:549406755596009476", ":BP:549406755755393064", 
    ":Y1:549407012996513803", ":Y2:549407014808453120", ":Y3:549407016607809536", ":Y4:549407018298114060", ":Y5:549407020231688193", ":Y6:549407022215593984", ":Y7:549407023603777547", ":Y8:549407025394745345", ":Y9:549407027911196683", ":YR:549407033720569857", ":YS:549407029656289283", ":YP:549407031757635624", 
    ":W4:549407153736253460", ":WR:549407154118066189", ":W4:549407153736253460", ":WR:549407154118066189"
]

COLOR_CARDS = [
    UNO_CARDS[0],
    UNO_CARDS[12],
    UNO_CARDS[24],
    UNO_CARDS[36]
]

RED_CARD = COLOR_CARDS[0]
GREEN_CARD = COLOR_CARDS[1]
BLUE_CARD = COLOR_CARDS[2]
YELLOW_CARD = COLOR_CARDS[3]

REVERSE_CARDS = [
    UNO_CARDS[9],
    UNO_CARDS[21],
    UNO_CARDS[33],
    UNO_CARDS[45]
]

SKIP_CARDS = [
    UNO_CARDS[10],
    UNO_CARDS[22],
    UNO_CARDS[34],
    UNO_CARDS[46]
]

ADD_2_CARDS = [
    UNO_CARDS[11],
    UNO_CARDS[23],
    UNO_CARDS[35],
    UNO_CARDS[47]
]

WILD_CARDS = [
    ":W4:549407153736253460", ":WR:549407154118066189"
]

ADD_4_CARD = WILD_CARDS[0]

DRAW_UNO = "❓"
QUIT = "❌"
CHALLENGE = "✅"
NO_CHALLENGE = "❎"

class Player:

    def __init__(self, member, is_ai = False):
        self._member = member

        self._cards = []
        self._message = None
        self._is_ai = is_ai

    def get_player(self):
        return self._member
    
    def get_cards(self):
        return self._cards
    
    def is_ai(self):
        return self._is_ai
    

    def add_card(self, card):
        self._cards.append(card)

    async def show_turn(self, game):

        # Only send if player is not an AI
        if not self._is_ai:

            # Get current player
            current_player = game.get_current_player().get_player()
            current_player_ai = game.get_current_player().is_ai()

            # Only show cards and reactions if current player is this player
            if not current_player_ai and current_player.id == self.get_player().id:

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
                if game.get_current_player().is_ai():
                    player_mention = game.get_current_player().get_player()
                else:
                    player_mention = game.get_current_player().get_player().mention

                self._message = await self.get_player().send(
                    embed = discord.Embed(
                        title = "_ _",
                        description = "It is {}'s turn.".format(
                            player_mention
                        ),
                        colour = PRIMARY_EMBED_COLOR
                    )
                )

class Uno:

    END_GAME = "END_GAME"

    def __init__(self, players, channel, bot, *, against_ais = False):
        self._players = [Player(player) for player in players]

        # If player goes against AIs, keep the first player and make the rest AIs
        if against_ais:
            self._players = [self._players[0]]
            for player in range(4):
                self._players.append(Player("AI {}".format(player + 1), True))

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

        if self.get_current_player().is_ai():
            player_mention = self.get_current_player().get_player()
        else:
            player_mention = self.get_current_player().get_player().mention

        # Send message to channel saying whose turn
        self._message = await self._channel.send(
            embed = discord.Embed(
                title = "Uno",
                description = "It is {}'s turn".format(
                    player_mention
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
            
            # Check if current player is not an AI
            if not self.get_current_player().is_ai():
                def check_reaction(reaction, user):
                    return reaction.message.id == self.get_current_player()._message.id and user.id == self.get_current_player().get_player().id and (str(reaction) in [DRAW_UNO, QUIT] or str(reaction).replace("<", "").replace(">", "") in UNO_CARDS)

                reaction, user = await self.bot.wait_for("reaction_add", check = check_reaction)
                reaction = str(reaction).replace("<", "").replace(">", "")
            
            # Current player is an AI, choose random valid card
            else:

                # Sleep for 1 second to emulate choosing
                await asyncio.sleep(1)

                # Check if AI has any valid cards
                valid_found = False
                reaction = None
                for card in self.get_current_player()._cards:

                    # Check all valid cards
                    if valid_card(self.get_current_card(), card.replace("<", "").replace(">", "")):
                        valid_found = True

                        # Check if AI card is a +4 card
                        if card == ADD_4_CARD:
                            reaction = card
                            break
                        
                        # Check if AI card is a +2 card
                        elif card in ADD_2_CARDS:
                            reaction = card
                            break
                        
                        # Check if AI card is a skip card
                        elif card in SKIP_CARDS:
                            reaction = card
                            break
                        
                        # Check if AI card is a wild card
                        elif card in WILD_CARDS:
                            reaction = card
                            break
                
                # Draw card; No valid cards found
                if not valid_found:
                    reaction = DRAW_UNO
                
                # Choose random card while card is invalid
                if reaction == None:
                    reaction = choice(self.get_current_player()._cards).replace("<", "").replace(">", "")
                    while not valid_card(self.get_current_card(), reaction):
                        reaction = choice(self.get_current_player()._cards).replace("<", "").replace(">", "")

            if str(reaction) == DRAW_UNO or str(reaction) == QUIT or valid_card(self.get_current_card(), str(reaction)):
                break
            
            else:
                if not self.get_current_player().is_ai():
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

            if current_player.is_ai():
                player_mention = current_player.get_player()
            else:
                player_mention = current_player.get_player().mention

            await notify(
                self,
                current_player,
                "❗ ❗ UNO ❗ ❗",
                "{} has Uno!".format(
                    player_mention
                )
            )
        
        # Check if player won
        elif (len(self.get_current_player()._cards)) == 0:
            return current_player

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
            
            if current_player.is_ai():
                player_mention = current_player.get_player()
            else:
                player_mention = current_player.get_player().mention
            
            await notify(
                self, 
                current_player,
                "Reversed!", "{} used a reverse card!".format(
                    player_mention
                )
            )

        # Check if card is a skip card
        elif str(reaction) in SKIP_CARDS:

            if self.get_next_player().is_ai():
                player_mention = self.get_next_player().get_player()
            else:
                player_mention = self.get_next_player().get_player().mention

            await notify(
                self, 
                current_player,
                "Skipped!", 
                "{} was skipped!".format(
                    player_mention
                ),
                special_next = "oooooofff. You were skipped."
            )

            self.next_player(skip = True)

        # Check if card is a wild card
        elif str(reaction) in WILD_CARDS:

            # Check if player is not AI
            if not current_player.is_ai():

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

            # Current player is AI, choose random color
            else:
                wild_reaction = choice([RED_CARD, BLUE_CARD, YELLOW_CARD, GREEN_CARD])

            # Check what color it is
            if str(wild_reaction) == RED_CARD:
                wild_select = "red"
            
            elif str(wild_reaction) == BLUE_CARD:
                wild_select = "blue"
            
            elif str(wild_reaction) == YELLOW_CARD:
                wild_select = "yellow"
            
            elif str(wild_reaction) == GREEN_CARD:
                wild_select = "green"
            
            # Add card to top of pile
            self.set_card(str(wild_reaction))
            
            # Check if the card is also a +4 card
            if str(reaction) == ADD_4_CARD:
                if self.get_next_player().is_ai():
                    player_mention = self.get_next_player().get_player()
                else:
                    player_mention = self.get_next_player().get_player().mention

                await notify(
                    self,
                    current_player,
                    "+4!",
                    "{} was hit with +4 card. oof.".format(player_mention),
                    special_next = "You were hit with a +4!\n¯\_(ツ)_/¯"
                )

                for card in range(4):
                    self.get_next_player().add_card(choice(UNO_CARDS))
            
            self.next_player()
        
        # Check if the card adds 2 to the next player
        elif str(reaction) in ADD_2_CARDS:
            if self.get_next_player().is_ai():
                player_mention = self.get_next_player().get_player()
            else:
                player_mention = self.get_next_player().get_player().mention
                
            await notify(
                self,
                current_player,
                "+2!",
                "{} was hit with a +2 card. oof.".format(player_mention),
                special_next = "You were hit with a +2!\n¯\_(ツ)_/¯"
            )

            for card in range(2):
                self.get_next_player().add_card(choice(UNO_CARDS))

            self.next_player()
        
        # Regular cards
        else:
            self.next_player()

        # Update channel message; Make sure the AI's are treated as players too.
        if not current_player.is_ai():
            player_mention = current_player.get_player().mention
        else:
            player_mention = current_player.get_player()

        await self._message.edit(
            embed = discord.Embed(
                title = "Uno",
                description = "{} chose {}\n{}".format(
                    player_mention,
                    "<{}>".format(
                        str(reaction)
                    ) if str(reaction) not in [DRAW_UNO, QUIT] else str(reaction),
                    "" if wild_select == None else ("The new color is " + wild_select)
                ),
                colour = PRIMARY_EMBED_COLOR
            )
        )

        # Update everybody's message; Only if they are not an AI
        for player in self._players:
            
            if not player.is_ai():

                if not current_player.is_ai():
                    player_mention = current_player.get_player().mention
                else:
                    player_mention = current_player.get_player()

                await player._message.edit(
                    embed = discord.Embed(
                        title = "Uno",
                        description = "{} chose {}\n{}".format(
                            player_mention if player != current_player else "You",
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

    # See if there is a special message for the next player and if next player is not AI
    if special_next != None:
        if not game.get_next_player().is_ai():
            await game.get_next_player().get_player().send(
                embed = discord.Embed(
                    title = title,
                    description = special_next,
                    colour = PRIMARY_EMBED_COLOR
                )
            )

    # Send message to all players (except current or if not AI)
    for player in game.get_players():

        if not player.is_ai():

            # Check if player is not current player
            is_player_eq_current = current_player.is_ai() or player.get_player().id != current_player.get_player().id

            # Check if special exists and player is not next player
            is_player_eq_next = game.get_next_player().is_ai() or game.get_next_player().get_player().id != player.get_player().id
            
            if is_player_eq_current or (special_next != None and is_player_eq_next):

                await player.get_player().send(
                    embed = discord.Embed(
                        title = title,
                        description = message,
                        colour = PRIMARY_EMBED_COLOR
                    )
                )
