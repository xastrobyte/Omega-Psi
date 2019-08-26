import asyncio, discord, math

from random import randint, choice

from category.globals import PRIMARY_EMBED_COLOR, NUMBER_EMOJIS
from category.globals import GRADUATION, BRIEFCASE, SPIN, BUY_HOUSE, SELL_HOUSE, DO_NOTHING, LOANS, LEAVE, FAMILY, RISKY_ROAD
from category.globals import PAYDAY, PAYDAY_BONUS, GET_MONEY, PAY_MONEY, PET, ACTION, HOUSE, SPIN_TO_WIN, SPIN, BABY, LOAN, SUED, MARRIED, RETIRED

from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # #

def commafy(number):
    return "{:,}".format(number)

def display_career(card):
    return "```md\n{}\n  {}\n  {}\n```".format(
        "[Job Title][{}]".format(
            card["name"]
        ),
        "<Salary ${}>".format(
            commafy(card["salary"])
        ),
        "<Bonus {}>".format(
            card["bonus"]
        )
    )

def display_house(card):
    return "```md\n{}\n  {}\n{}\n  {}\n  {}\n```".format(
        "[House][{}]".format(card["name"]),
        "<Cost ${}>".format(commafy(card["purchase"])),
        "# When selling the house",
        "<Red ${}>".format(commafy(card["spin_red"])),
        "<Black ${}>".format(commafy(card["spin_black"]))
    )

def choose_house(player, *, buy = True, house_one = None, house_two = None):

    # Check if the player is buying a house
    if buy:

        # Check if the purchase prices are the same
        if house_one["purchase"] == house_two["purchase"]:

            # Check if the low sell prices are the same
            if house_one["spin_red"] == house_two["spin_red"]:

                # Check if the high sell prices are the same; Choose a house at random
                if house_one["spin_black"] == house_two["spin_black"]:
                    return choice([house_one, house_two])
                
                # Choose the higher high sell price
                return max([house_one, house_two], key = lambda house: house["spin_black"])
            
            # Choose the higher low sell price
            return max([house_one, house_two], key = lambda house: house["spin_red"])
        
        # If the player has enough money for the higher one, choose it
        # If not; choose the lower one as long as the player does not need to take out loans
        max_house = max([house_one, house_two], key = lambda house: house["purchase"])
        min_house = min([house_one, house_two], key = lambda house: house["purchase"])
        if player.get_cash() >= max_house["purchase"]:
            return max_house
        if player.get_cash() >= min_house["purchase"]:
            return min_house
        return None
    
    # The player is selling a house
    else:

        # Look through the player's houses for the highest low sell price
        highest_low = [player.get_houses()[0]]
        highest_sell = highest_low[0]["spin_red"]
        for house in player.get_houses():

            # Check if the house has a higher low sell than the previous
            if house["spin_red"] > highest_sell:
                highest_low = [house]
                highest_sell = house["spin_red"]
            
            # Check if the house has an equivalent low sell with previous houses
            elif house["spin_red"] == highest_sell:
                highest_low.append(house)
    
        # Look through the highest low sells for the highest high sell
        # # First, check if there is only 1 house
        if len(highest_low) == 1:
            return highest_low[0]
        
        # # There is more than 1 house, find the highest high sell
        else:
            highest_high = [highest_low[0]]
            highest_sell = highest_low[0]["spin_black"]
            for house in highest_low:

                # Check if the house has a higher high sell than the previous
                if house["spin_black"] > highest_sell:
                    highest_high = [house]
                    highest_sell = house["spin_black"]
                
                # Check if the house has an equivalent high sell with previous houses
                elif house["spin_black"] == highest_sell:
                    highest_high.append(house)
            
            # Choose a house at random from the list
            return choice(highest_high)

# # # # # # # # # # # # # # # # # # # # # # # # #

async def display_card(turn, card_type, card):

    # Check if the card is a pet card
    if card_type == "pet":
        await turn.add_action(
            "```md\n{}\n{}\n<\n{}\n>\n```".format(
                card["name"], 
                "=" * len(card["name"]),
                card["action_text"]
            )
        )

    # Check if the card is an action card
    elif card_type == "action":
        
        # Check if the card is a FIRED card
        if card["action"]["type"] == "fired":
            description = "{}{}{}{}".format(
                "{}".format(card["action"]["text"]) if card["action"]["text"] != None else "",
                "\n{}".format(card["spin"]["low"]),
                "\n{}".format(card["spin"]["medium"]),
                "\n{}".format(card["spin"]["high"])
            )
        
        # The card is a regular card
        else:
            description = "{}{}{}{}".format(
                "{}".format(card["action"]["text"]) if card["action"]["text"] != None else "",
                "\n{}".format(card["spin"]["low"]["text"]) if card["spin"]["low"] != None else "",
                "\n{}".format(card["spin"]["medium"]["text"]) if card["spin"]["medium"] != None else "",
                "\n{}".format(card["spin"]["high"]["text"]) if card["spin"]["high"] != None else ""
            )
        
        # Send the message to the channel that the game is being played in
        await turn.add_action(
            "```md\n{}\n{}\n<\n{}\n>\n```".format(
                card["name"], 
                "=" * len(card["name"]),
                description
            )
        )
    
    # Sleep for 3 seconds so players can read the card
    await asyncio.sleep(3)

async def ask_for_spin(game, turn = None, color = False, *, show_leave = False, part_of_turn = True, spin_to_win = False, player = None):

    # Determine if the player is given or not
    if player == None:
        player = turn.get_player()

    # Check if the player is an AI
    if player.is_ai():

        # Sleep for 2 seconds to simulate waiting to spin
        await asyncio.sleep(2)
    
    # The player is a real person
    else:
    
        # Send a message asking the player to spin
        spin_title = "{} is spinning!".format(player.get_name(title = True))
        spin_description = "{}, react with {} when you're ready to spin!{}".format(
            player.get_name(title = True), SPIN, 
            "\nIf you'd like to leave, react with {}".format(LEAVE) if show_leave else ""
        )

        # Update the turn message
        def check_reaction(reaction, user):
            return (
                reaction.message.id == turn.get_message().id and
                str(reaction) in (
                    [SPIN, LEAVE] if (part_of_turn and show_leave) else [SPIN]
                ) and
                user.id == player.get_member().id
            )
        
        if part_of_turn:
            await turn.add_action(
                "```md\n{}\n{}\n<\n{}\n>\n```".format(
                    spin_title,
                    "=" * len(spin_title),
                    spin_description
                )
            )
            await turn.get_message().add_reaction(SPIN)
            if show_leave:
                await turn.get_message().add_reaction(LEAVE)
        
        reaction, user = await game.get_bot().wait_for("reaction_add", check = check_reaction)

        # Clear the reactions and check them
        if part_of_turn:
            await turn.get_message().clear_reactions()

        # Check if the player is leaving
        if str(reaction) == LEAVE:
            return LEAVE
    
    # Choose a random number
    number = None
    for value in range(randint(1, 10)):
        number = randint(1, 10)
    is_black = number % 2 == 0
    
    # Check if the spinning is not for Spin to Win
    if not spin_to_win and part_of_turn:
        await turn.add_action(
            "{} {} spun {}".format(
                SPIN,
                player.get_name(),
                "{}".format(
                    "black" if is_black else "red"
                ) if color else "{} {}".format(
                    "a" if number != 8 else "an",
                    number
                )
            )
        )

    # Return the number
    return number

async def ask_for_career(game, turn, college = False, *, change = False):
    player = turn.get_player()

    # Check if the player is getting a college career
    if college:
        cards = game.get_college_career_cards()
    
    # The player is getting a regular career
    else:
        cards = game.get_career_cards()
    
    # Check if the player is an AI
    if player.is_ai():
        
        # Check if the AI is changing their career (night school)
        if change:

            # Choose one career card from the deck and the current career
            new_career = cards.pop(0)
            old_career = player.get_career()

            # If they both have the same salary, pick at random
            if new_career["salary"] == old_career["salary"]:
                chosen_career = choice([new_career, old_career])

            # If one salary is higher than the other, choose the higher one
            else:
                chosen_career = max([new_career, old_career], key = lambda value: value["salary"])

            # Check if the AI chose a new career
            chose_new = chosen_career == new_career
            player.set_career(chosen_career)
            if chose_new:
                cards.append(old_career)
            else:
                cards.append(new_career)

            # Send a message saying what career the AI chose
            await turn.add_action(
                "{} {} career!\n{}".format(
                    player.get_name(),
                    "chose a new" if chose_new else "kept their old",
                    display_career(player.get_career())
                )
            )
        
        # The AI is deciding between 2 careers (fired or new career)
        else:
            
            # Pull the first 2 careers
            card_one = cards.pop(0)
            card_two = cards.pop(0)

            # Check if both salaries are the same; The AI will choose a career at random
            if card_one["salary"] == card_two["salary"]:
                chosen_career = choice([card_one, card_two])
            
            # The salaries are different; The AI will choose the higher salary
            else:
                chosen_career = max([card_one, card_two], key = lambda value: value["salary"])
            
            # Set the AI's career and add the other card to the deck
            if chosen_career == card_one:
                player.set_career(card_one)
                cards.append(card_two)
            else:
                player.set_career(card_two)
                cards.append(card_one)

            # Send a message saying what career the AI chose
            await turn.add_action(
                "{} {} chose a career!\n{}".format(
                    BRIEFCASE,
                    player.get_name(),
                    display_career(player.get_career())
                )
            )
    
    # The player is a real person
    else:

        # Tell the player to check their DM's
        await game.get_channel().send(
            "{}, check your DM's for your career choices!".format(player.get_member().mention),
            delete_after = 10
        )
        
        # Check if the player is changing their career (night school)
        if change:
            
            # Pull the first career card and the player's career
            new_career = cards.pop(0)
            old_career = player.get_career()

            # Send the player a message with both careers lined out
            message = await player.get_member().send(
                embed = discord.Embed(
                    title = "Choose a career!",
                    description = "_ _",
                    colour = await get_embed_color(player.get_member())
                ).add_field(
                    name = NUMBER_EMOJIS[0],
                    value = display_career(new_career),
                    inline = False
                ).add_field(
                    name = NUMBER_EMOJIS[1],
                    value = display_career(old_career),
                    inline = False
                )
            )
            await message.add_reaction(NUMBER_EMOJIS[0])
            await message.add_reaction(NUMBER_EMOJIS[1])

            # Wait for the player to choose which career they want
            def check_reaction(reaction, user):
                return (
                    reaction.message.id == message.id and
                    str(reaction) in NUMBER_EMOJIS[:2] and
                    user.id == player.get_member().id
                )
            reaction, user = await game.get_bot().wait_for("reaction_add", check = check_reaction)
            chose_new = False

            # The player chose the new career
            #   Add the old career back to the deck
            if str(reaction) == NUMBER_EMOJIS[0]:
                chose_new = True
                player.set_career(new_career)
                cards.append(old_career)
            
            # The player chose their original career
            #   Add the new career back to the deck
            elif str(reaction) == NUMBER_EMOJIS[1]:
                cards.append(new_career)
            
            # Send a message to the game channel saying what career was chosen
            await message.delete()
            await turn.add_action(
                "{} {}\n{}".format(
                    BRIEFCASE,
                    "{} {} career!".format(
                        player.get_name(),
                        "chose a new" if chose_new else "kept their old"
                    ),
                    display_career(player.get_career())
                )
            )
        
        # The player is deciding between 2 careers (fired or new career)
        else:
            
            # Pull the first 2 careers
            card_one = cards.pop(0)
            card_two = cards.pop(0)

            # Send the player a message with both careers lined out
            message = await player.get_member().send(
                embed = discord.Embed(
                    title = "Choose a career!",
                    description = "_ _",
                    colour = await get_embed_color(player.get_member())
                ).add_field(
                    name = NUMBER_EMOJIS[0],
                    value = display_career(card_one),
                    inline = False
                ).add_field(
                    name = NUMBER_EMOJIS[1],
                    value = display_career(card_two),
                    inline = False
                )
            )
            await message.add_reaction(NUMBER_EMOJIS[0])
            await message.add_reaction(NUMBER_EMOJIS[1])

            # Wait for the player to choose which career they want
            def check_reaction(reaction, user):
                return (
                    reaction.message.id == message.id and
                    str(reaction) in NUMBER_EMOJIS[:2] and
                    user.id == player.get_member().id
                )
            reaction, user = await game.get_bot().wait_for("reaction_add", check = check_reaction)

            # The player chose the first career
            #   Add the second career back to the deck
            if str(reaction) == NUMBER_EMOJIS[0]:
                player.set_career(card_one)
                cards.append(card_two)
            
            # The player chose the second career
            #   Add the first career back to the deck
            elif str(reaction) == NUMBER_EMOJIS[1]:
                player.set_career(card_two)
                cards.append(card_one)
            
            # Send a message to the game channel saying what career was chosen
            await message.delete()
            await turn.add_action(
                "{} {}\n{}".format(
                    BRIEFCASE,
                    "{} chose a career!".format(
                        player.get_name(),
                    ),
                    display_career(player.get_career())
                )
            )

    return True

async def sell_house(game, turn, house):
    player = turn.get_player()

    # Show everyone what house the player is selling
    await turn.add_action(
        "{} is selling the following house:\n{}\n".format(
            player.get_name(),
            display_house(house)
        )
    )
    
    # Ask the player to spin
    value = await ask_for_spin(game, turn, color = True)
    is_black = value % 2 == 0

    # Update the message on how much the house was sold for
    amount = house["spin_black" if is_black else "spin_red"]

    # Return the amount
    return amount
        
async def ask_for_house(game, turn, *, action = None):
    player = turn.get_player()

    # Only ask for the action if no action exists
    if action == None:

        # Check if the player is an AI
        if player.is_ai():

            # Determine if the AI will buy a house, sell a house, or do nothing
            actions = ["buy", "sell", "nothing"]
            action = choice(actions)
            while action == "sell" and len(player.get_houses()) == 0:
                action = choice(actions)
        
        # The player is a real person
        else:
            
            # Create the embed
            embed = discord.Embed(
                title = "What will you do?",
                description = "{}{}{}".format(
                    "If you want to buy a house, react with {}\n".format(BUY_HOUSE),
                    "If you want to sell a house, react with {}\n".format(SELL_HOUSE) if len(player.get_houses()) != 0 else "",
                    "If you want to do nothing, react with {}".format(DO_NOTHING)
                ),
                colour = await get_embed_color(player.get_member())
            )

            # Ask the player what they will do
            message = await game.get_channel().send(
                embed = embed
            )

            # Add the necessary reactions
            await message.add_reaction(BUY_HOUSE)
            if len(player.get_houses()) != 0:
                await message.add_reaction(SELL_HOUSE)
            await message.add_reaction(DO_NOTHING)

            # Wait for the player to react
            def check_reaction(reaction, user):
                return (
                    reaction.message.id == message.id and
                    str(reaction) in ([BUY_HOUSE, SELL_HOUSE, DO_NOTHING] if len(player.get_houses()) != 0 else [BUY_HOUSE, DO_NOTHING]) and
                    user.id == player.get_member().id
                )
            reaction, user = await game.get_bot().wait_for("reaction_add", check = check_reaction)

            # The reaction is to buy a house
            if str(reaction) == BUY_HOUSE:
                action = "buy"
            
            # The reaction is to sell a house
            elif str(reaction) == SELL_HOUSE:
                action = "sell"
            
            # The reaction is to do nothing
            elif str(reaction) == DO_NOTHING:
                action = "nothing"
            
            # Delete the message; The turn message will be updated in the buy, sell, or nothing action statements
            await message.delete()

    # The player will buy a house
    if action == "buy":

        # Update the turn message
        await turn.add_action(
            "{} {} is buying a house!".format(
                HOUSE,
                player.get_name()
            )
        )

        # Pull 2 houses from the house deck
        chosen_house = None
        take_loans = False
        cards = game.get_house_cards()
        house_one = cards.pop(0)
        house_two = cards.pop(0)

        # Check if the player is an AI
        if player.is_ai():

            # Sleep for 2 seconds to simulate a decision
            await asyncio.sleep(2)

            # Have the AI choose a house intelligently
            chosen_house = choose_house(player, house_one = house_one, house_two = house_two)
            take_loans = chosen_house != None
        
        # The player is a real person
        else:

            # Create the embed
            embed = discord.Embed(
                title = "Choose a house!",
                description = "_ _",
                colour = await get_embed_color(player.get_member())
            ).add_field(
                name = NUMBER_EMOJIS[0],
                value = display_house(house_one),
                inline = False
            ).add_field(
                name = NUMBER_EMOJIS[1],
                value = display_house(house_two),
                inline = False
            )

            # Ask the player which house they want to take
            message = await player.get_member().send(
                embed = embed
            )
            await message.add_reaction(NUMBER_EMOJIS[0])
            await message.add_reaction(NUMBER_EMOJIS[1])

            # Wait for the player to choose a house
            def check_reaction(reaction, user):
                return (
                    reaction.message.id == message.id and
                    str(reaction) in NUMBER_EMOJIS[:2] and
                    user.id == player.get_member().id
                )
            reaction, user = await game.get_bot().wait_for("reaction_add", check = check_reaction)

            # The player chose the first house
            if str(reaction) == NUMBER_EMOJIS[0]:
                chosen_house = house_one
            
            # The player chose the second house
            elif str(reaction) == NUMBER_EMOJIS[1]:
                chosen_house = house_two
            
            await message.delete()
            
            # Check if the player can buy the house without loans
            if chosen_house["purchase"] <= player.get_cash():
                
                # Add the other house back to the deck
                if str(reaction) == NUMBER_EMOJIS[0]:
                    cards.append(house_two)
                elif str(reaction) == NUMBER_EMOJIS[1]:
                    cards.append(house_one)
                
                # Update the turn message
                take_loans = True
            
            # The player needs to buy loans
            else:
                
                # Create the embed
                embed = discord.Embed(
                    title = "Loans Needed",
                    description = (
                        """
                        In order to buy that house, you need to take out some loans.
                        If you want to take loans out, react with {}.
                        If you want to cancel buying a house, react with {}.
                        """
                    ).format(LOANS, LEAVE),
                    colour = await get_embed_color(player.get_member())
                )

                # Ask the player to choose what to do
                message = await player.get_member().send(embed = embed)
                await message.add_reaction(LOANS)
                await message.add_reaction(LEAVE)

                # Wait for the player to react
                def check_reaction(reaction, user):
                    return (
                        reaction.message.id == message.id and
                        str(reaction) in [LOANS, LEAVE] and
                        user.id == player.get_member().id
                    )
                reaction, user = await game.get_bot().wait_for("reaction_add", check = check_reaction)
                take_loans = str(reaction) == LOANS

        # Check if the player still has to take loans out
        if take_loans:

            # If so, send a message saying the player pulled out loans
            loans_needed = math.ceil((chosen_house["purchase"] - player.get_cash()) / 50000)
            if loans_needed > 0:
                player.pull_out_loans(loans_needed)
            
            # Take cash from the player to purchase the house
            player.take_cash(chosen_house["purchase"])
            player.add_house(chosen_house)
            await turn.add_action(
                "{} {} bought a new house{}!\n{}".format(
                    HOUSE,
                    player.get_name(), 
                    " after taking out some loans" if loans_needed > 0 else "",
                    display_house(chosen_house)
                )
            )
        
        # The player does not want to take out loans
        else:

            # Send a message saying the player chose not to take out loans
            cards.append(house_one)
            cards.append(house_two)
            await turn.add_action(
                "{} {} did not want to take out any loans! They will not buy the house.".format(
                    ACTION,
                    player.get_name()
                )
            )
    
    # The player will sell a house
    elif action == "sell":

        # Update the turn message
        await turn.add_action(
            "{} {} is selling a house!".format(
                HOUSE,
                player.get_name()
            )
        )

        # Check if the player is an AI
        if player.is_ai():

            # Sleep for 2 seconds simulating a decision on what house to sell
            await asyncio.sleep(2)

            # Have the AI choose a house intelligently
            chosen_house = choose_house(player, buy = False)
            player.get_houses().remove(chosen_house)
        
        # The player is a real person
        else:
            
            # Create the embed
            embed = discord.Embed(
                title = "Choose a house to sell!",
                description = "_ _",
                colour = await get_embed_color(player.get_member())
            )

            # Add the houses as fields
            for index in range(len(player.get_houses())):
                house = player.get_houses()[index]
                embed.add_field(
                    name = NUMBER_EMOJIS[index],
                    value = display_house(house),
                    inline = False
                )
            
            # Ask the player to choose which house to sell
            message = await player.get_member().send(
                embed = embed
            )
            for emoji in NUMBER_EMOJIS[:len(player.get_houses())]:
                await message.add_reaction(emoji)
            
            # Wait for the player to react
            def check_reaction(reaction, user):
                return (
                    reaction.message.id == message.id and
                    str(reaction) in NUMBER_EMOJIS[:len(player.get_houses())] and
                    user.id == player.get_member().id
                )
            reaction, user = await game.get_bot().wait_for("reaction_add", check = check_reaction)
            await message.delete()

            # Get the house that the player wants to sell
            chosen_house = player.get_houses().pop(NUMBER_EMOJIS.index(str(reaction)))

        # Send a message to the game channel to show what house the AI is selling
        await turn.add_action(
            "{} {} is selling the following house:\n{}".format(
                HOUSE,
                player.get_name(), display_house(chosen_house)
            )
        )

        # Have the player spin to see how much they sell their house for
        value = await ask_for_spin(game, turn, color = True, player = player)
        is_black = value % 2 == 0
        amount = chosen_house["spin_black" if is_black else "spin_red"]

        # Send a message saying how much the house was sold for
        player.give_cash(amount)
        await turn.add_action(
            "{} {} sold their house for ${}".format(
                GET_MONEY,
                player.get_name(), commafy(amount)
            )
        )
        return amount
    
    # The player will do nothing
    elif action == "nothing":
        
        # Send a message saying the player did nothing
        await turn.add_action(
            "{} {} chose not to buy nor sell a house.".format(
                ACTION,
                player.get_name()
            )
        )

async def choose_opponent(game, turn, is_lawsuit = False):
    player = turn.get_player()
    
    # Check if the player is an AI
    if player.is_ai():
        
        # Have the AI choose someone with the highest salary
        highest_salary = 0
        highest = None
        for temp_player in game.get_players():
            if temp_player.get_id() != player.get_id():

                # Check if the temp_player has a career
                if temp_player.get_career() != None:
                    if temp_player.get_career()["salary"] > highest_salary:
                        highest_salary = temp_player.get_career()["salary"]
                        highest = temp_player
        
        # The highest is still None, choose a player at random
        if highest == None:
            highest = choice(game.get_players())
            while highest.get_id() == player.get_id():
                highest = choice(game.get_players())

        # Sleep for 2 seconds to simulate a decision
        # Then send a message to the game channel saying who the AI chose
        await asyncio.sleep(2)
        if not is_lawsuit:
            await turn.add_action(
                "{} {} chose {}!".format(
                    ACTION,
                    player.get_name(),
                    highest.get_name()
                )
            )

        return highest
    
    # The player is a real person
    else:

        # Create the embed
        embed = discord.Embed(
            title = "Choose an opponent!",
            description = "_ _",
            colour = await get_embed_color(player.get_member())
        )

        # Add the opponents as fields to choose from
        opponents = []
        for index in range(len(game.get_players())):
            temp_player = game.get_players()[index]
            if temp_player.get_id() != player.get_id():
                opponents.append(temp_player)
                embed.add_field(
                    name = NUMBER_EMOJIS[index - 1],
                    value = temp_player.get_name(),
                    inline = False
                )
    
        # Send a message for the player to choose their opponent
        message = await game.get_channel().send(embed = embed)
        for emoji in NUMBER_EMOJIS[:len(opponents)]:
            await message.add_reaction(emoji)

        # Wait for the player to react with which opponent they choose
        def check_reaction(reaction, user):
            return (
                reaction.message.id == message.id and
                str(reaction) in NUMBER_EMOJIS[:len(opponents)] and
                user.id == player.get_member().id
            )
        reaction, user = await game.get_bot().wait_for("reaction_add", check = check_reaction)

        # Clear the reactions and update the message with which opponent was chosen
        opponent = opponents[NUMBER_EMOJIS.index(str(reaction))]
        await message.delete()
        await turn.add_action(
            "{} {} chose {}!".format(
                ACTION,
                player.get_name(),
                opponent.get_name()
            )
        )

        return opponent

async def spin_to_win(game, turn):
    player = turn.get_player()

    # Keep track of the spots taken and the message
    spots = {}
    text = ""

    # Send a message saying it's a Spin to Win
    message = await game.get_channel().send(
        embed = discord.Embed(
            title = "Spin to Win!",
            description = "Everyone choose a spot!",
            colour = PRIMARY_EMBED_COLOR
        )
    )

    # Ask each player to choose their spots
    for temp_player in game.get_players():

        # Determine how many spots the player chooses
        spots_left = 2 if temp_player.get_id() == player.get_id() else 1

        # Let the player choose their spot(s)
        for i in range(spots_left):

            # Check if the player is an AI
            if temp_player.is_ai():
                
                # Sleep for 2 seconds to simulate a decision
                await asyncio.sleep(2)

                # Choose a spot; Make sure the spot wasn't already taken
                spot = choice(NUMBER_EMOJIS)
                while str(spot) in spots:
                    spot = choice(NUMBER_EMOJIS)
                spots[str(spot)] = temp_player

                # Update the message saying what spot was taken
                text += "{} chose {}!\n".format(temp_player.get_name(), str(spot))
                embed = discord.Embed(
                    title = "Spin to Win!",
                    description = text,
                    colour = PRIMARY_EMBED_COLOR
                )

                # The message does not exist yet, create it
                if message == None:
                    message = await game.get_channel().send(embed = embed)
                
                # The message does exist, update it
                else:
                    await message.edit(embed = embed)
            
            # The player is a real person
            else:

                # Send a message asking the user to choose their spot
                await message.edit(
                    embed = discord.Embed(
                        title = "Spin to Win!",
                        description = "{}\n{}, choose your spot{}!".format(
                            text,
                            temp_player.get_name(),
                            "s" if spots_left == 2 else ""
                        ),
                        colour = await get_embed_color(temp_player.get_member())
                    )
                )
                
                # Add the reactions and wait for the player to react
                for emoji in NUMBER_EMOJIS:
                    if str(emoji) not in spots:
                        await message.add_reaction(emoji)
                def check_reaction(reaction, user):
                    return (
                        reaction.message.id == message.id and
                        str(reaction) in NUMBER_EMOJIS and
                        str(reaction) not in spots and
                        user.id == temp_player.get_member().id
                    )
                reaction, user = await game.get_bot().wait_for("reaction_add", check = check_reaction)

                # Clear the reactions and update the text, then update the message
                await message.clear_reactions()
                text += "{} chose {}!\n".format(
                    temp_player.get_name(),
                    str(reaction)
                )
                spots[str(reaction)] = temp_player

                # Create the embed
                embed = discord.Embed(
                    title = "Spin to Win!",
                    description = text,
                    colour = await get_embed_color(temp_player.get_member())
                )

                # The message does not exist yet, create it
                if message == None:
                    message = await game.get_channel().send(embed = embed)
                
                # The message does exist, update it
                else:
                    await message.edit(embed = embed)
    
    # Clear the reactions from the message
    await message.clear_reactions()

    # Ask the player to spin until a token is matched
    winner = None
    while True:

        # Ask the player to spin on the spin to win message
        if player.is_ai():

            # Sleep for 2 seconds simulating a wait for spin
            await asyncio.sleep(2)
        
        # The player is a real person
        else:

            # Update the message asking the player to spin
            spin_description = "{}, react with {} when you're ready to spin!".format(
                player.get_name(), SPIN
            )
            await message.edit(
                embed = discord.Embed(
                    title = "Spin to Win!",
                    description = "{}\n{}".format(text, spin_description),
                    colour = await get_embed_color(player.get_member())
                )
            )
            await message.add_reaction(SPIN)

            # Wait for the player to react
            def check_reaction(reaction, user):
                return (
                    reaction.message.id == message.id and
                    user.id == player.get_member().id and
                    str(reaction) == SPIN
                )
            reaction, user = await game.get_bot().wait_for("reaction_add", check = check_reaction)

            # The only reaction is the spin reaction
            # Clear the reactions from the message
            await message.clear_reactions()
        
        # Choose a random number
        value = 0
        for i in range(randint(1, 10)):
            value = randint(1, 10)

        # Send a message saying what number was spun
        embed = discord.Embed(
            title = "Spin to Win!",
            description = "{}\n{} spun {} {}".format(
                text,
                player.get_name(),
                "a" if value != 8 else "an",
                value
            ),
            colour = PRIMARY_EMBED_COLOR if player.is_ai() else await get_embed_color(player.get_member())
        )

        # Check if the value spun was one with a token on it
        if NUMBER_EMOJIS[value - 1] in spots:
            winner = spots[NUMBER_EMOJIS[value - 1]]
            break
        
        # The value does not match a token; Respin
        else:

            # Send a message saying no one won
            await message.edit(
                embed = discord.Embed(
                    title = "Spin to Win!",
                    description = "{}\n{} spun {} {}\n{}".format(
                        text,
                        player.get_name(),
                        "a" if value != 8 else "an",
                        value,
                        "No one won that spin. Spin again."
                    ),
                    colour = PRIMARY_EMBED_COLOR if player.is_ai() else await get_embed_color(player.get_member())
                )
            )
        
        # Sleep for 2 seconds so players can read what happened
        await asyncio.sleep(2)
        
    # There was a winner, update the Spin to Win message to say who won
    winner.give_cash(200000)
    await message.edit(
        embed = discord.Embed(
            title = "{} won!".format(winner.get_name(title = True)),
            description = "{} won the Spin to Win and gets $200,000!".format(winner.get_name()),
            colour = PRIMARY_EMBED_COLOR if winner.is_ai() else await get_embed_color(winner.get_member())
        )
    )

async def compete(game, turn, compete_10k = False):
    player = turn.get_player()
        
    # Have the player choose an opponent
    opponent = await choose_opponent(game, turn)

    # Ask each player to spin while the spins are the same
    while True:

        # Get the spin for each player and show them in the turn actions
        value_player = await ask_for_spin(game, turn, player = player)
        value_opponent = await ask_for_spin(game, turn, player = opponent)

        # Check if the values are the same
        if value_player == value_opponent:
            await turn.add_action(
                "{} {} and {} both spun {}. They have to spin again!".format(
                    ACTION,
                    player.get_name(), opponent.get_name(),
                    value_player
                )
            )
            await asyncio.sleep(2)
        
        # The values are different
        else:

            winner = player if value_player > value_opponent else opponent
            await turn.add_action(
                "{} {} spun higher!".format(
                    ACTION, winner.get_name()
                )
            )
            await asyncio.sleep(2)

            # Check if the competition type is 10k x spin
            if compete_10k:
                return winner, max([value_player, value_opponent])
            
            # The competition type is a regular one
            return winner

async def process_pet_card(game, turn):
    player = turn.get_player()

    # Pull a card from the game's pet cards
    card = game.get_pet_cards().pop(0)
    await display_card(turn, "pet", card)
    player.add_pet_card()
    
    # Check if the player is collecting money
    if card["action"] == "collect":

        # Send a message to the game channel saying who collected money
        player.give_cash(card["amount"])
        await turn.add_action(
            "{} {} collected ${}!".format(
                GET_MONEY,
                player.get_name(), commafy(card["amount"])
            )
        )
    
    # Check if the player is collecting money for each pet
    elif card["action"] == "collect_for_each":

        # Give the player money for each pet they have
        total = 0
        for pet in range(player.get_pets()):
            total += card["amount"]
            player.give_cash(card["amount"])
        
        # Send a message to the game channel saying who collected money
        await turn.add_action(
            "{} {} collected ${} {}!".format(
                GET_MONEY,
                player.get_name(), commafy(card["amount"]),
                "for each pet for a total of ${}".format(
                    commafy(total)
                ) if total != card["amount"] else ""
            )
        )
    
    # Check if the player is collecting money from each player
    elif card["action"] == "collect_from_each":

        # Give the player money from every other player
        total = 0
        for temp_player in game.get_players():
            if player.get_id() != temp_player.get_id():
                total += card["amount"]
                temp_player.take_cash(card["amount"])
                player.give_cash(card["amount"])
        
        # Send a message to the game channel saying who collected money
        await turn.add_action(
            "{} {} collected ${} {}!".format(
                GET_MONEY,
                player.get_name(), commafy(card["amount"]),
                "from everyone for a total of ${}".format(
                    commafy(total)
                ) if total != card["amount"] else ""
            )
        )

    # Check if the player is paying money
    elif card["action"] == "pay":

        # Send a message to the game channel saying who collected money
        player.take_cash(card["amount"])
        await turn.add_action(
            "{} {} had to pay the bank ${}!".format(
                PAY_MONEY,
                player.get_name(), commafy(card["amount"])
            )
        )
    
    # Check if the player is paying money for each pet
    elif card["action"] == "pay_for_each":

        # Take money from the player for each pet they have
        total = 0
        for pet in range(player.get_pets()):
            total += card["amount"]
            player.take_cash(card["amount"])
        
        # Send a message to the game channel saying who collected money
        await turn.add_action(
            "{} {} had to pay the bank ${} {}!".format(
                PAY_MONEY,
                player.get_name(), commafy(card["amount"]),
                "for each pet for a total of ${}".format(
                    commafy(total)
                ) if total != card["amount"] else ""
            )
        )
    
    # Check if the player is competing against another player
    elif card["action"] == "compete":

        # Have the players compete against each other
        winner = await compete(game, turn)
        winner.give_cash(card["amount"])

        # Send a message to the game channel saying who collected money
        await turn.add_action(
            "{} {} collected ${} for spinning higher!".format(
                GET_MONEY,
                winner.get_name(), commafy(card["amount"])
            )
        )

async def process_action_card(game, turn):
    player = turn.get_player()
    
    # Pull a card from the game's action cards
    index = 0
    action_cards = game.get_action_cards()
    card = action_cards[index]

    # Don't give the player a card that says they were fired if they don't have a career yet (college)
    while card["action"]["type"] == "fired" and player.get_career() == None:
        index += 1
        card = action_cards[index]
    
    # Pull the card from the action cards and give the player that card
    card = action_cards.pop(index)
    await display_card(turn, "action", card)
    player.add_action_card()

    # Check if the player is collecting money
    if card["action"]["type"] == "collect":

        # Check if there is a spin type
        if card["spin"]["type"] != None:

            # Check if the spin type is by color
            amount = None
            if card["spin"]["type"] == "color":

                # Ask the player to spin
                value = await ask_for_spin(game, turn, color = True)
                is_black = value % 2 == 0
                amount = card["spin"]["high" if is_black else "low"]["amount"]
            
            # Check if the spin type is by number
            else:

                # Ask the player to spin
                value = await ask_for_spin(game, turn)

                # Get the low values
                if card["spin"]["low"] != None:
                    low = card["spin"]["low"]["low"]
                    high = card["spin"]["low"]["high"]
                    if value >= low and value <= high:
                        amount = card["spin"]["low"]["amount"]
                
                # Get the medium values
                if card["spin"]["medium"] != None and amount == None:
                    low = card["spin"]["medium"]["low"]
                    high = card["spin"]["medium"]["high"]
                    if value >= low and value <= high:
                        amount = card["spin"]["medium"]["amount"]
                    
                # Get the high values
                if card["spin"]["high"] != None and amount == None:
                    low = card["spin"]["high"]["low"]
                    high = card["spin"]["high"]["high"]
                    if value >= low and value <= high:
                        amount = card["spin"]["high"]["amount"]

            # Send a message to the game channel saying who collected money
            player.give_cash(amount)
            await turn.add_action(
                "{} {} collected ${}!".format(
                    GET_MONEY,
                    player.get_name(), commafy(amount)
                )
            )
        
        # There is no spin type
        else:

            # Send a message to the game channel saying who collected money
            player.give_cash(card["spin"]["amount"])
            await turn.add_action(
                "{} {} collected ${}!".format(
                    GET_MONEY,
                    player.get_name(), commafy(card["spin"]["amount"])
                )
            )
    
    # Check if the player is collecting money x 10k
    elif card["action"]["type"] == "collect_10k":

        # Ask the player to spin
        value = await ask_for_spin(game, turn)

        # Send a message to the game channel saying who collected money
        player.give_cash(value * card["spin"]["amount"])
        await turn.add_action(
            "{} {} collected ${}!".format(
                GET_MONEY,
                player.get_name(), commafy(value * card["spin"]["amount"])
            )
        )
    
    # Check if the player is collecting a lawsuit
    elif card["action"]["type"] == "collect_lawsuit":

        # Have the player choose someone to give them money
        opponent = await choose_opponent(game, turn, is_lawsuit = True)
        opponent.take_cash(card["spin"]["amount"])
        player.give_cash(card["spin"]["amount"])

        # Send a message to the game channel saying who sued who for money
        await turn.add_action(
            "{} {} sued {} for ${}!".format(
                SUED,
                player.get_name(), opponent.get_name(), commafy(card["spin"]["amount"])
            )
        )
    
    # Check if all players are spinning
    elif card["action"]["type"] == "collect_all":

        # Have each player spin
        for temp_player in game.get_players():

            # Ask for their spin
            value = await ask_for_spin(game, turn, player = temp_player)
            amount = None

            # Get the low values
            if card["spin"]["low"] != None:
                low = card["spin"]["low"]["low"]
                high = card["spin"]["low"]["high"]
                if value >= low and value <= high:
                    amount = card["spin"]["low"]["amount"]
            
            # Get the medium values
            if card["spin"]["medium"] != None and amount == None:
                low = card["spin"]["medium"]["low"]
                high = card["spin"]["medium"]["high"]
                if value >= low and value <= high:
                    amount = card["spin"]["medium"]["amount"]
                
            # Get the high values
            if card["spin"]["high"] != None and amount == None:
                low = card["spin"]["high"]["low"]
                high = card["spin"]["high"]["high"]
                if value >= low and value <= high:
                    amount = card["spin"]["high"]["amount"]
            
            # Send a message saying how much the player got
            temp_player.give_cash(amount)
            await turn.add_action(
                "{} {} collected ${}!".format(
                    GET_MONEY,
                    temp_player.get_name(), commafy(amount)
                )
            )
    
    # Check if the player is competing against another player
    elif card["action"]["type"] == "compete":

        # Have the players compete against each other
        winner = await compete(game, turn)

        # Send a message saying who won
        winner.give_cash(card["spin"]["amount"])
        await turn.add_action(
            "{} {} won and collected ${}".format(
                GET_MONEY,
                winner.get_name(), commafy(card["spin"]["amount"])
            )
        )
    
    # Check if the player is competing against another player but 10k x spin
    elif card["action"]["type"] == "compete_10k":

        # Have the players compete against each other
        winner, value = await compete(game, turn, compete_10k = True)

        # Send a message saying who won
        winner.give_cash(value * card["spin"]["amount"])
        await turn.add_action(
            "{} {} won and collected ${}".format(
                GET_MONEY,
                winner.get_name(), commafy(value * card["spin"]["amount"])
            )
        )
    
    # Check if the player is paying
    elif card["action"]["type"] == "pay":

        # Send a message to the game channel saying who paid
        player.take_cash(card["spin"]["amount"])
        await turn.add_action(
            "{} {} had to pay the bank ${}!".format(
                PAY_MONEY,
                player.get_name(), commafy(card["spin"]["amount"])
            )
        )
    
    # Check if the card is a special type
    elif card["action"]["type"] == "fired":

        # Put the career card back into the deck
        if player.is_college():
            cards = game.get_college_career_cards()
        else:
            cards = game.get_career_cards()
        cards.append(player.get_career())
        player.set_career(None)

        # Have the player choose a new career
        await ask_for_career(game, turn, player.is_college())

async def process_graduation(game, turn):

    # Ask for a change of career
    await ask_for_career(game, turn, True)

async def process_married(game, turn):
    player = turn.get_player()
    
    # Send a message saying the player got married
    await turn.add_action(
        "{0} {1} got married!\n{1}, spin for gifts from everyone!".format(
            MARRIED,
            player.get_name()
        )
    )

    # Ask the player to spin for gifts from everyone
    value = await ask_for_spin(game, turn, color = True)
    is_black = value % 2 == 0
    amount = 100000 if is_black else 50000

    # Have each player give the gift amount
    total = 0
    for temp_player in game.get_players():
        if temp_player.get_id() != player.get_id():
            total += amount
            temp_player.take_cash(amount)
    player.give_cash(total)

    # Send a message saying how much money the player got in total
    await asyncio.sleep(2)
    await turn.add_action(
        "{} {} collected ${} {}".format(
            GET_MONEY,
            player.get_name(), commafy(amount),
            "from everyone for a total of ${}".format(
                 commafy(total)
            ) if amount != total else ""
        )
    )

async def process_spin_for_babies(game, turn, space):
    player = turn.get_player()

    # Send a message saying the player is spinning for babies
    await turn.add_action(
        "{} {} is spinning to see if they have any more babies!".format(
            BABY,
            player.get_name()
        )
    )
    
    # Ask the player to spin
    value = await ask_for_spin(game, turn)
    for baby_peg in range(space["spin"][str(value)]):
        player.has_baby()
    
    # Send a message saying how many babies the player got
    await turn.add_action(
        "{} {} had {} bab{}!".format(
            BABY,
            player.get_name(),
            space["spin"][str(value)],
            "ies" if space["spin"][str(value)] != 1 else "y"
        )
    )

async def process_night_school(game, turn):
    player = turn.get_player()

    # Check if the player is an AI
    night_school = False
    if player.is_ai():
        
        # Determine if the AI will go to night school or not
        night_school = randint(1, 10) % 2 == 0
    
    # The player is a real person
    else:
        
        # Create the embed
        embed = discord.Embed(
            title = "Night School?",
            description = (
                """
                If you want to go to Night School, react with {}.
                If you don't want to, react with {}.
                """
            ).format(GRADUATION, SPIN),
            colour = await get_embed_color(player.get_member())
        )

        # Ask the player if they want to go to night school
        message = await game.get_channel().send(
            embed = embed
        )
        await message.add_reaction(GRADUATION)
        await message.add_reaction(SPIN)

        # Wait for the player to react
        def check_reaction(reaction, user):
            return (
                reaction.message.id == message.id and
                str(reaction) in [GRADUATION, SPIN] and
                user.id == player.get_member().id
            )
        reaction, user = await game.get_bot().wait_for("reaction_add", check = check_reaction)
        night_school = str(reaction) == GRADUATION
        await message.delete()
    
    # Make sure the player moves in the correct path
    player.modify_move(night_school)
    
    # The player wants to go to night school
    if night_school:

        # Send a message saying the player is going to night school
        player.take_cash(100000)
        await turn.add_action(
            "{} {} had to pay ${} to go to Night School!".format(
                PAY_MONEY,
                player.get_name(), commafy(100000)
            )
        )

        # Ask for career
        await ask_for_career(game, turn, True, change = True)
    
    # The player does not want to go to night school
    else:
        await turn.add_action(
            "{} {} chose not to go to Night School!".format(
                ACTION,
                player.get_name()
            )
        )

async def process_family_path(game, turn):
    player = turn.get_player()
    
    # Check if the player is an AI
    if player.is_ai():
        
        # Sleep for 2 seconds to simulate a decision
        await asyncio.sleep(2)
        player.modify_move(randint(1, 10) % 2 == 0)

    # The player is real
    else:

        # Ask the player if they want to go on the family path or not
        msg = await game.get_channel().send(
            embed = discord.Embed(
                title = "Family Path?",
                description = (
                    """
                    If you want to go on the family path, react with {}
                    If you don't want to, react with {}
                    """
                ).format(FAMILY, SPIN),
                colour = PRIMARY_EMBED_COLOR if player.is_ai() else await get_embed_color(player.get_member())
            )
        )
        await msg.add_reaction(FAMILY)
        await msg.add_reaction(SPIN)

        # Wait for the user to react with which way they want to go
        def check_reaction(reaction, user):
            return reaction.message.id == msg.id and str(reaction) in [FAMILY, SPIN] and user.id == player.get_member().id
        reaction, user = await game.get_bot().wait_for("reaction_add", check = check_reaction)
        await msg.delete()
        player.modify_move(str(reaction) == FAMILY)

    # Send a message to the channel about their decision
    await turn.add_action(
        "{} {} is{} going down the Family Path!".format(
            BABY if player._move_modify else ACTION,
            player.get_name(),
            "" if player._move_modify else " not"
        )
    )

async def process_baby_space(game, turn, space):
    player = turn.get_player()

    # Determine what action the baby space is
    action = space["type"]
    if action == "baby":
        description = "{} {} had a baby!"
        player.has_baby()
    elif action == "twins":
        description = "{} {} had twins!"
        for i in range(2):
            player.has_baby()
    else:
        description = "{} {} had triplets!"
        for i in range(3):
            player.has_baby()
    
    # Update the turn message
    await turn.add_action(
        description.format(
            BABY,
            player.get_name()
        )
    )

async def process_risky_road(game, turn):
    player = turn.get_player()
    
    # Check if the player is an AI
    if player.is_ai():
        player.modify_move(randint(1, 10) % 2 == 0)

    # The player is real
    else:

        # Ask the player if they want to go on the risky road or not
        msg = await game.get_channel().send(
            embed = discord.Embed(
                title = "Risky Road?",
                description = (
                    """
                    If you want to go on the risky road, react with {}
                    If you don't want to, react with {}
                    """
                ).format(RISKY_ROAD, SPIN),
                colour = PRIMARY_EMBED_COLOR if player.is_ai() else await get_embed_color(player.get_member())
            )
        )
        await msg.add_reaction(RISKY_ROAD)
        await msg.add_reaction(SPIN)

        # Wait for the user to react with which way they want to go
        def check_reaction(reaction, user):
            return (
                reaction.message.id == msg.id and 
                str(reaction) in [RISKY_ROAD, SPIN] 
                and user.id == player.get_member().id
            )
        reaction, user = await game.get_bot().wait_for("reaction_add", check = check_reaction)
        player.modify_move(str(reaction) == RISKY_ROAD)
        await msg.delete()

    # Send a message to the channel about their decision
    await turn.add_action(
        "{} {} is{} going down the Risky Road!".format(
            RISKY_ROAD if player._move_modify else ACTION,
            player.get_name(),
            "" if player._move_modify else " not"
        )
    )

async def process_stop_space(game, turn, space_type, space):
    player = turn.get_player()
    
    # Check if the player is graduating
    if space_type == "graduation":
        await process_graduation(game, turn)
    
    # Check if the player is getting married
    elif space_type == "married":
        await process_married(game, turn)
    
    # Check if the player is spinning for babies
    elif space_type == "spin_for_babies":
        await process_spin_for_babies(game, turn, space)
    
    # Check if the player is deciding on night school
    elif space_type == "night_school":
        await process_night_school(game, turn)
    
    # Check if the player is deciding on the family path
    elif space_type == "family_path":
        await process_family_path(game, turn)
    
    # Check if the player is deciding on risky road
    elif space_type == "risky_road":
        await process_risky_road(game, turn)
    
    # Check if the player is retiring
    elif space_type == "retirement":

        # Give the player their retirement money
        amount = 100000 * (5 - len(game.get_retired()))
        player.give_cash(amount)
        player.retire()

        # Update the turn message
        await turn.add_action(
            "{} {} has retired and collected ${}!".format(
                RETIRED,
                player.get_name(), commafy(amount)
            )
        )
    
    # The player takes another turn if the space was not retirement
    if space_type != "retirement":
        turn.get_player().extra_turn()