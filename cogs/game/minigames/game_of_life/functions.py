from random import choice

def choose_house(player, *, buy = True, house_one = None, house_two = None):
    """Has the AI intelligently choose a house depending on the purchase prices
    and the sell prices

    :param player: The player object that must choose between two houses
    :param buy: Whether or not to decide 
    :param house_one: The first house card the player must decide on
        Note: this is only used when deciding on buying a house
    :param house_two: The second house card the player must decide on
        Note: this is only used when deciding on buying a house
    """

    # Check if the player is choosing between 2 houses
    if buy:

        # Check if the purchase prices are the same
        if house_one.purchase == house_two.purchase:

            # Check if the low sell prices are the same
            if house_one.spin_black == house_two.spin_black:

                # Check if the high sell prices are the same
                #   if so, choose a random house
                if house_one.spin_red == house_two.spin_red:
                    return choice([house_one, house_two])
                
                # Choose the higher high sell price
                return max([house_one, house_two], key = lambda house: house.spin_black)

            # Choose the higher low sell price
            return max([house_one, house_two], key = lambda house: house.spin_red)
        
        # If the player has enough money for the higher one, choose it
        #   if not, choose the lower one as long as the player does
        #   not need to take out any loans
        max_house = max([house_one, house_two], key = lambda house: house.purchase)
        min_house = min([house_one, house_two], key = lambda house: house.purchase)
        if player.cash >= max_house.purchase:
            return max_house
        if player.cash >= min_house.purchase:
            return min_house
        return None
    
    # The player is selling a house
    else:
        
        # Look through the player's houses for the highest low sell price
        highest_low = [player.house_cards[0]]
        highest_sell = highest_low[0].spin_red
        for house in player.house_cards:

            # Check if the house has a higher low sell than the previous
            if house.spin_red > highest_sell:
                highest_low = [house]
                highest_sell = house.spin_red
            
            # Check if the house has an equivalent low sell with previous houses
            elif house.spin_red == highest_sell:
                highest_low.append(house)
    
        # Look through the highest low sells for the highest high sell
        # # First, check if there is only 1 house
        if len(highest_low) == 1:
            return highest_low[0]
        
        # # There is more than 1 house, find the highest high sell
        else:
            highest_high = [highest_low[0]]
            highest_sell = highest_low[0].spin_black
            for house in highest_low:

                # Check if the house has a higher high sell than the previous
                if house.spin_black > highest_sell:
                    highest_high = [house]
                    highest_sell = house.spin_black
                
                # Check if the house has an equivalent high sell with previous houses
                elif house.spin_black == highest_sell:
                    highest_high.append(house)
            
            # Choose a house at random from the list
            return choice(highest_high)