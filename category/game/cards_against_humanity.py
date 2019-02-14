import asyncio, discord
from random import randint, shuffle

from category import errors
from category.globals import PRIMARY_EMBED_COLOR, NUMBER_EMOJIS, LEAVE

REPLACEMENTS = {
    "&reg;": "",
    "&trade;": "",
    "_": "\_\_\_\_\_\_\_\_\_",
    "<br/>": "\n",
    "&quot;": "\"",
    "&amp;": "&",
    "<i>": "*",
    "</i>": "*",
    "<br>": "\n",
    "&uarr;": ":arrow_up: ",
    "&darr;": ":arrow_down: ",
    "&larr;": ":arrow_left: ",
    "&rarr;": ":arrow_right: ",
    "</br>": "\n"
}

class CardSubmission:

    def __init__(self, player, pick_max = 1):
        self._player = player
        self._cards = []
        self._pick_max = pick_max
    
    def get_player(self):
        return self._player
    
    def get_cards(self):
        return self._cards
    
    def add_card(self, card):
        self._cards.append(card)
    
    def can_submit(self):
        return len(self._cards) < self._pick_max

class Player:

    def __init__(self, member):
        
        self._member = member

        self._wins = 0

        self._submission = CardSubmission(self)
        self._white_cards = []
    
    def get_player(self):
        return self._member
    
    def get_wins(self):
        return self._wins
    
    def add_card(self, white_card, pick_max = 1):
        
        self._submission.add_card(white_card)
    
    def get_submission(self):
        return self._submission
    
    def give_cards(self, white_cards, number = 1, override = False):

        amt_to_give = (7 - len(self._white_cards)) if not override else (7 + number - len(self._white_cards))
        for number in range(amt_to_give):
            self.give_card(white_cards)
    
    def give_card(self, white_cards):

        white_card = white_cards.pop(randint(0, len(white_cards) - 1))
        for replacement in REPLACEMENTS:
            white_card = white_card.replace(replacement, REPLACEMENTS[replacement])

        self._white_cards.append(
            WhiteCard(white_card)
        )
    
    async def send(self, bot, game):

        # Send judge a message
        if game.get_judge() == self._member:

            await self._member.send(
                embed = discord.Embed(
                    title = "<:cah:540281486633336862> Cards Against Humanity - Round {}".format(game.get_round()),
                    description = "You are the judge this round! Just chillax until everyone submits their cards.\n\n{}".format(game._current_black_card.get_text()),
                    colour = PRIMARY_EMBED_COLOR
                ).add_field(
                    name = "*Scores*",
                    value = "\n".join([
                        "{} - {}".format(
                            player.get_player().mention,
                            player.get_wins()
                        )
                        for player in game.get_players()
                    ])
                )
            )

        else:

            # Setup embed
            embed = discord.Embed(
                title = "<:cah:540281486633336862> Cards Against Humanity - Round {}".format(game.get_round()),
                description = "**Judge**: {}\n\n{}".format(
                    game.get_judge(),
                    game._current_black_card.get_text()
                ),
                colour = PRIMARY_EMBED_COLOR
            )

            # Add fields (cards)
            count = 0
            for card in self._white_cards:
                embed.add_field(
                    name = NUMBER_EMOJIS[count],
                    value = card.get_text(),
                    inline = False
                )
                count += 1

            # Send message to player
            self._play_message = await self._member.send(
                embed = embed.add_field(
                    name = "*Scores*",
                    value = "\n".join([
                        "{} - {}".format(
                            player.get_player().mention,
                            player.get_wins()
                        )
                        for player in game.get_players()
                    ])
                )
            )

            # Add reactions
            for emoji in NUMBER_EMOJIS[:count]:
                await self._play_message.add_reaction(emoji)
            await self._play_message.add_reaction(LEAVE)
    
    async def send_cards(self, game):

        # Setup description for embeds
        description = ""
        for submission in game.get_submissions():
            description += "{}\n\n".format(
                "\n".join([card.get_text() for card in submission.get_cards()])
            )

        # Send message
        self._result_message = await self._member.send(
            embed = discord.Embed(
                title = "<:cah:540281486633336862> Cards Against Humanity - Round {}".format(game.get_round()),
                description = "**Judge**: {}\n\n**Black Card**\n\n{}\n\n{}".format(
                    game.get_judge().mention,
                    game._current_black_card.get_text(),
                    description
                ),
                colour = PRIMARY_EMBED_COLOR
            ).add_field(
                    name = "*Scores*",
                    value = "\n".join([
                        "{} - {}".format(
                            player.get_player().mention,
                            player.get_wins()
                        )
                        for player in game.get_players()
                    ])
                )
        )
    
    async def completed(self, winner, game):

        # Check if player won
        if winner.get_player().get_player() == self._member:
            won = True
            self._wins += 1
        
        # Player did not win
        else:
            won = False

        await self._result_message.edit(
            embed = discord.Embed(
                title = "<:cah:540281486633336862> Cards Against Humanity - Round {}".format(game.get_round()),
                description = "{} Won!\n\n{}\n\n{}\n".format(
                    winner.get_player().get_player().mention,
                    game._current_black_card.get_text(),
                    "\n\n".join([
                        "{}\n{}".format(
                            submission.get_player().get_player().mention,
                            "\n".join([
                                card.get_text()
                                for card in submission.get_cards()
                            ])
                        ) 
                        for submission in game.get_submissions()
                    ])
                ),
                colour = 0x00FF00 if won else (PRIMARY_EMBED_COLOR if self._member == game.get_judge() else 0xFF0000)
            ).add_field(
                    name = "*Scores*",
                    value = "\n".join([
                        "{} - {}".format(
                            player.get_player().mention,
                            player.get_wins()
                        )
                        for player in game.get_players()
                    ])
                )
        )

class BlackCard:

    def __init__(self, text, pick):
        self._text = text
        self._pick = pick
    
    def get_text(self):
        return self._text
    
    def get_pick(self):
        return self._pick

class WhiteCard:

    def __init__(self, text):
        self._text = text
    
    def get_text(self):
        return self._text

class CardsAgainstHumanity:

    def __init__(self, players, black_cards, channel, bot):
        self._players = [Player(player) for player in players]

        # Choose random number for judge
        self._judge = randint(0, len(players) - 1)
        self._round = 1

        self._submissions = []

        self._black_cards = black_cards
        self._current_black_card = None
        self._channel = channel

        self._bot = bot

        self._game_over = False

    async def choose_cards(self, white_cards):

        # Choose black card
        if len(self._black_cards) > 1:
            black_card = self._black_cards.pop(randint(0, len(self._black_cards) - 1))
            cards_to_pick = black_card["pick"]
            black_card = black_card["text"]
            for replacement in REPLACEMENTS:
                black_card = black_card.replace(replacement, REPLACEMENTS[replacement])
            
            self._current_black_card = BlackCard(black_card, cards_to_pick)
        
        # Not enough black cards, game is over
        else:
            return True
        
        # Give cards to players; Send message to players about the black card and the judge
        for player in self._players:

            if player.get_player() != self.get_judge():
                player.give_cards(white_cards, cards_to_pick, cards_to_pick > 1)

            # Send message to player listing their cards
            await player.send(self._bot, self)
        
        # Send message to channel
        await self._channel.send(
            embed = discord.Embed(
                title = "<:cah:540281486633336862> Cards Against Humanity - Round {}".format(self.get_round()),
                description = "{} is the judge...\n\n**Black Card**\n{}".format(
                    self.get_judge().mention,
                    self._current_black_card.get_text()
                ),
                colour = PRIMARY_EMBED_COLOR
            ).set_footer(
                text = "Cards Against Humanity"
            ).add_field(
                name = "*Scores*",
                value = "\n".join([
                    "{} - {}".format(
                        player.get_player().mention,
                        player.get_wins()
                    )
                    for player in self.get_players()
                ])
            )
        )
    
    async def wait_for_submissions(self):

        # Keep track of whether or not not enough players existed
        not_enough_players = False

        while not self.all_cards():

            # Wait for reactions
            def check_submit(reaction, user):

                # Check if player has submitted their cards already
                for submission in self._submissions:
                    if submission.get_player().get_player() == user:
                        return False
                
                return (str(reaction) in NUMBER_EMOJIS or str(reaction) == LEAVE) and reaction.message.id == self.get_player(user)._play_message.id and not user.bot
            
            done, pending = await asyncio.wait([
                self._bot.wait_for("reaction_add", check = check_submit),
                self._bot.wait_for("reaction_remove", check = check_submit)
            ], return_when = asyncio.FIRST_COMPLETED)
            reaction, user = done.pop().result()

            # Cancel all futures
            for future in pending:
                future.cancel()

            player = self.get_player(user)
            if len(player._submission.get_cards()) == 0:
                player._submission = CardSubmission(player, self._current_black_card.get_pick())

            # Check if player wants to leave
            if str(reaction) == LEAVE:
                
                # See if player was judge
                if self.get_judge() == user:

                    # Send message to all players
                    await self.new_judge()
                    continue
                
                # Player was not judge
                else:
                    await self.player_left(player.get_player())
                
                # Remove player
                self._players.remove(player)

                # See if there are less than 3 players
                if len(self._players) < 3:
                    not_enough_players = True
                    break

            # Get card and determine whether they've already added it or not
            card_index = NUMBER_EMOJIS.index(str(reaction))

            # Check if card index is not valid
            try:
                card = player._white_cards[card_index]

                # Check if card was already played
                if card in player.get_submission().get_cards():
                    
                    await user.send(
                        embed = errors.get_error_message(
                            "You've already chosen that card for this round."
                        ),
                        delete_after = 5
                    )

                # Add card to submission if possible
                elif player.get_submission().can_submit():
                    player.add_card(card)

                    cards_left = self._current_black_card.get_pick() - len(player.get_submission().get_cards())
                    if cards_left > 0:
                        await user.send(
                            "You can still choose {} more card{}.".format(cards_left, "s" if cards_left > 1 else ""),
                            delete_after = 10
                        )
                
                # Player cannot submit anymore; Submit to game
                if not player.get_submission().can_submit():

                    # Remove cards and submit
                    for card in player.get_submission().get_cards():
                        player._white_cards.remove(card)
                    self.submit_card(player.get_submission())

                    # Send message saying they've submitted their cards
                    await user.send(
                        embed = discord.Embed(
                            title = "Submitted! :white_check_mark:",
                            description = "Your Card{}:\n{}".format(
                                "s" if self._current_black_card.get_pick() > 1 else "",
                                "\n".join([card.get_text() for card in player.get_submission().get_cards()])
                            ),
                            colour = PRIMARY_EMBED_COLOR
                        ),
                        delete_after = 10
                    )
            
            # Card index is invalid
            except:
                await user.send(
                    embed = errors.get_error_message(
                        "There's no card assigned to that number."
                    )
                )
        
        # Send message to all players that there weren't enough players and to channel
        if not_enough_players:
            await self.not_enough_players()
        
    async def judge_choose(self):

        # Setup description for embeds
        description = ""
        shuffle(self._submissions)
        for submission in self._submissions:
            description += "{}\n\n".format(
                "\n".join([card.get_text() for card in submission.get_cards()])
            )

        # Send message to all players with all cards
        for player in self._players:

            # Don't send to judge, we wanna do that outside of the loop
            if self.get_judge() != player.get_player():
                await player.send_cards(self)

        # Send message
        self._channel_message = await self._channel.send(
            embed = discord.Embed(
                title = "<:cah:540281486633336862> Cards Against Humanity - Round {}".format(self.get_round()),
                description = "**Judge**: {}\n**Black Card**\n{}\n\n{}".format(
                    self.get_judge().mention,
                    self._current_black_card.get_text(),
                    description
                ),
                colour = PRIMARY_EMBED_COLOR
            ).add_field(
                name = "*Scores*",
                value = "\n".join([
                    "{} - {}".format(
                        player.get_player().mention,
                        player.get_wins()
                    )
                    for player in self.get_players()
                ])
            )
        )

        # Setup embed for judge
        embed = discord.Embed(
            title = "<:cah:540281486633336862> Cards Against Humanity - Round {}".format(self.get_round()),
            description = "Choose a {}\n\n**Black Card**\n{}".format(
                "set of cards" if self._current_black_card.get_pick() > 1 else "card",
                self._current_black_card.get_text()
            ),
            colour = PRIMARY_EMBED_COLOR
        ).add_field(
            name = "*Scores*",
            value = "\n".join([
                "{} - {}".format(
                    player.get_player().mention,
                    player.get_wins()
                )
                for player in self.get_players()
            ])
        )

        # Add cards
        count = 0
        for submission in self._submissions:
            embed.add_field(
                name = NUMBER_EMOJIS[count],
                value = "\n".join([card.get_text() for card in submission.get_cards()]),
                inline = False
            )
            count += 1

        # Send message to judge
        judge_message = await self.get_judge().send(
            embed = embed
        )

        # Add reactions
        for emoji in NUMBER_EMOJIS[:count]:
            await judge_message.add_reaction(emoji)
        
        # Wait for judge to react
        def check_judge(reaction, user):
            return self.get_judge() == user and reaction.message.id == judge_message.id and str(reaction) in NUMBER_EMOJIS[:count]
        reaction, user = await self._bot.wait_for("reaction_add", check = check_judge)

        # Find which submission won
        winner = self.get_submissions()[NUMBER_EMOJIS.index(str(reaction))]

        # Send complete message to players and channel played in
        # Also check if any players have won yet (7 points)
        for player in self.get_players():

            # Only send completed messages to round players; Not judge
            if player.get_player() != self.get_judge():
                await player.completed(winner, self)
                if player.get_wins() >= 7:
                    self._game_over = True
        
        # Edit complete message for judge
        await judge_message.edit(
            embed = discord.Embed(
                title = "<:cah:540281486633336862> Cards Against Humanity - Round {}".format(self.get_round()),
                description = "{} Won!\n\n{}\n\n{}\n".format(
                    winner.get_player().get_player().mention,
                    self._current_black_card.get_text(),
                    "\n\n".join([
                        "{}\n{}".format(
                            submission.get_player().get_player().mention,
                            "\n".join([
                                card.get_text()
                                for card in submission.get_cards()
                            ])
                        ) 
                        for submission in self.get_submissions()
                    ])
                ),
                colour = PRIMARY_EMBED_COLOR
            ).add_field(
                name = "*Scores*",
                value = "\n".join([
                    "{} - {}".format(
                        player.get_player().mention,
                        player.get_wins()
                    )
                    for player in self.get_players()
                ])
            )
        )
        
        # Send complete message to channel played in
        await self._channel_message.edit(
            embed = discord.Embed(
                title = "<:cah:540281486633336862> Cards Against Humanity - Round {}".format(self.get_round()),
                description = "{} Won!\n\n{}\n\n{}\n".format(
                    winner.get_player().get_player().mention,
                    self._current_black_card.get_text(),
                    "\n\n".join([
                        "{}\n{}".format(
                            submission.get_player().get_player().mention,
                            "\n".join([
                                card.get_text()
                                for card in submission.get_cards()
                            ])
                        ) 
                        for submission in self.get_submissions()
                    ])
                ),
                colour = PRIMARY_EMBED_COLOR
            ).add_field(
                name = "*Scores*",
                value = "\n".join([
                    "{} - {}".format(
                        player.get_player().mention,
                        player.get_wins()
                    )
                    for player in self.get_players()
                ])
            )
        )

        # Clear submissions and move to next judge
        self.clear_submissions()
        self.next_judge()
    
    async def new_judge(self):

        # Get new judge
        self._players.pop(self._judge)
        if self._judge >= len(self._players):
            self._judge = 0

        # Send message to all players that a new judge was chosen
        for player in self._players:
            await player.get_player().send(
                embed = discord.Embed(
                    title = "Judge left.",
                    description = "{} is the new judge!".format(self.get_judge()),
                    colour = PRIMARY_EMBED_COLOR
                )
            )
        
        # Send message to channel that new judge was chosen
        await self._channel.send(
            embed = discord.Embed(
                title = "Judge left.",
                description = "{} is the new judge!".format(self.get_judge()),
                colour = PRIMARY_EMBED_COLOR
            )
        )
    
    async def not_enough_players(self):

        # Send message to all players that there are too few people
        for player in self._players:
            await player.get_player().send(
                embed = discord.Embed(
                    title = "Not Enough People",
                    description = "There are less than 3 people so we gotta stop this game :frowning2:",
                    colour = PRIMARY_EMBED_COLOR
                )
            )
        
        # Send message to channel that there are too few people
        await self._channel.send(
            embed = discord.Embed(
                title = "Judge left.",
                description = "There are less than 3 people so we gotta stop this game :frowning2:",
                colour = PRIMARY_EMBED_COLOR
            )
        ) 
    
    async def player_left(self, member):

        # Send message to all players that there are too few people
        for player in self._players:
            await player.get_player().send(
                embed = discord.Embed(
                    title = "Someone left.",
                    description = "{} left the game :angry:".format(member.mention),
                    colour = PRIMARY_EMBED_COLOR
                )
            )
        
        # Send message to channel that there are too few people
        await self._channel.send(
            embed = discord.Embed(
                title = "Someone left.",
                description = "{} left the game :angry:".format(member.mention),
                colour = PRIMARY_EMBED_COLOR
            )
        ) 

    async def give_cards(self, white_cards):

        for player in self._players:
            await player.give_cards(white_cards)
        
    def get_players(self):
        return self._players
    
    def get_player(self, member):
        for player in self._players:
            if player.get_player() == member:
                return player
        return None
    
    def get_judge(self):
        return self._players[self._judge].get_player()
    
    def next_judge(self):
        self._judge += 1
        if self._judge >= len(self._players):
            self._judge = 0
        self._round += 1
    
    def get_round(self):
        return self._round

    def submit_card(self, card_submission):
        self._submissions.append(card_submission)
    
    def all_cards(self):
        return len(self._submissions) == len(self._players) - 1
    
    def get_submissions(self):
        return self._submissions
    
    def clear_submissions(self):
        self._submissions = []
        for player in self._players:
            player._submission = CardSubmission(player)