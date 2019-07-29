import asyncio, os, requests

from discord.ext import commands

from category import errors

from category.food.meal import parse_meal
from category.food.drink import parse_drink

from category.globals import FIRST_PAGE, LAST_PAGE, PREVIOUS_PAGE, NEXT_PAGE, LEAVE, SCROLL_REACTIONS
from category.globals import loop

from util.functions import add_scroll_reactions

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

MEAL_DB_API_CALL = "https://www.themealdb.com/api/json/v1/{}/random.php"
MEAL_DB_INGREDIENT_API_CALL = "https://www.themealdb.com/api/json/v1/{}/filter.php?i={}"
MEAL_DB_ID_API_CALL = "https://www.themealdb.com/api/json/v1/{}/lookup.php?i={}"

COCKTAIL_DB_API_CALL = "https://www.thecocktaildb.com/api/json/v1/{}/random.php"
COCKTAIL_DB_INGREDIENT_API_CALL = "https://www.thecocktaildb.com/api/json/v1/{}/filter.php?i={}"
COCKTAIL_DB_ID_API_CALL = "https://www.thecocktaildb.com/api/json/v1/{}/lookup.php?i={}"

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class Food(commands.Cog, name = "food"):
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @commands.command(
        name = "recipe",
        description = "Lets you look up recipes or random foods given an ingredient.",
        cog_name = "food"
    )
    async def food_recipe(self, ctx, *, ingredient = None):

        # Check if there is no ingredient, get a random recipe.
        if ingredient == None:
            
            # Call the Meal API
            recipe = await loop.run_in_executor(None,
                requests.get,
                MEAL_DB_API_CALL.format(
                    os.environ["MEAL_DB_API_KEY"]
                )
            )
            recipe = recipe.json()

            # Get the first meal (it should be the only meal)
            meal = recipe["meals"][0]

            # Send the message
            await ctx.send(
                embed = await parse_meal(ctx, meal)
            )
        
        # There is an ingredient, get a list of recipes that include it
        else:
            
            # Call the Meal API for ingredients
            recipe = await loop.run_in_executor(None,
                requests.get,
                MEAL_DB_INGREDIENT_API_CALL.format(
                    os.environ["MEAL_DB_API_KEY"],
                    ingredient
                )
            )
            recipe = recipe.json()

            # Check if there are no meals
            if recipe["meals"] == None:
                await ctx.send(
                    embed = errors.get_error_message(
                        "I couldn't find any meals with that ingredient."
                    )
                )
            
            # There are meals
            else:

                # Get a list of meals and convert them into their meal JSON objects
                meals = recipe["meals"]
                for meal in range(len(meals)):

                    # Call the Meal API
                    response = await loop.run_in_executor(None,
                        requests.get,
                        MEAL_DB_ID_API_CALL.format(
                            os.environ["MEAL_DB_API_KEY"],
                            meals[meal]["idMeal"]
                        )
                    )
                    response = response.json()

                    # Replace the meal
                    meals[meal] = response["meals"][0]
                
                # Get the first meal and parse it into an embed
                first_meal = await parse_meal(ctx, meals[0])
                msg = await ctx.send(
                    embed = first_meal
                )

                # Add the scrolling emojis
                await add_scroll_reactions(msg, meals)

                # Loop while the user wants to
                current = 0
                while True:

                    # Wait for next reaction from user
                    def check(reaction, user):
                        return str(reaction) in SCROLL_REACTIONS and reaction.message.id == msg.id and user == ctx.author

                    done, pending = await asyncio.wait([
                        self.bot.wait_for("reaction_add", check = check),
                        self.bot.wait_for("reaction_remove", check = check)
                    ], return_when = asyncio.FIRST_COMPLETED)

                    reaction, user = done.pop().result()

                    # Cancel any futures
                    for future in pending:
                        future.cancel()
                    
                    # Reaction is FIRST_PAGE
                    if str(reaction) == FIRST_PAGE:
                        current = 0
                    
                    # Reaction is LAST_PAGE
                    elif str(reaction) == LAST_PAGE:
                        current = len(meals) - 1
                    
                    # Reaction is PREVIOUS_PAGE
                    elif str(reaction) == PREVIOUS_PAGE:
                        current -= 1
                        if current < 0:
                            current = 0
                    
                    # Reaction is NEXT_PAGE
                    elif str(reaction) == NEXT_PAGE:
                        current += 1
                        if current > len(meals) - 1:
                            current = len(meals) - 1
                    
                    # Reaction is LEAVE
                    elif str(reaction) == LEAVE:
                        await msg.delete()
                        break
                    
                    # Update event
                    await msg.edit(
                        embed = await parse_meal(ctx, meals[current])
                    )
    
    @commands.command(
        name = "drink",
        description = "Lets you look up recipes or random drinks given an ingredient.",
        cog_name = "food"
    )
    async def drink_recipe(self, ctx, *, ingredient = None):

        # Check if there is no ingredient, get a random recipe.
        if ingredient == None:
            
            # Call the Drink API
            recipe = await loop.run_in_executor(None,
                requests.get,
                COCKTAIL_DB_API_CALL.format(
                    os.environ["COCKTAIL_DB_API_KEY"]
                )
            )
            recipe = recipe.json()

            # Get the first drink (it should be the only drink)
            drink = recipe["drinks"][0]

            # Send the message
            await ctx.send(
                embed = await parse_drink(ctx, drink)
            )
        
        # There is an ingredient, get a list of recipes that include it
        else:
            
            # Call the Drink API for ingredients
            recipe = await loop.run_in_executor(None,
                requests.get,
                COCKTAIL_DB_INGREDIENT_API_CALL.format(
                    os.environ["COCKTAIL_DB_API_KEY"],
                    ingredient
                )
            )
            recipe = recipe.json()

            # Check if there are no drinks
            if len(recipe["drinks"]) == 0:
                await ctx.send(
                    embed = errors.get_error_message(
                        "I couldn't find any drinks with that ingredient."
                    )
                )
            
            # There are drinks
            else:

                # Get a list of drinks and convert them into their drink JSON objects
                drinks = recipe["drinks"]
                for drink in range(len(drinks)):

                    # Call the Drink API
                    response = await loop.run_in_executor(None,
                        requests.get,
                        COCKTAIL_DB_ID_API_CALL.format(
                            os.environ["COCKTAIL_DB_API_KEY"],
                            drinks[drink]["idDrink"]
                        )
                    )
                    response = response.json()

                    # Replace the drink
                    drinks[drink] = response["drinks"][0]
                
                # Get the first drink and parse it into an embed
                first_drink = await parse_drink(ctx, drinks[0])
                msg = await ctx.send(
                    embed = first_drink
                )

                # Add the scrolling emojis
                await add_scroll_reactions(msg, drinks)

                # Loop while the user wants to
                current = 0
                while True:

                    # Wait for next reaction from user
                    def check(reaction, user):
                        return str(reaction) in SCROLL_REACTIONS and reaction.message.id == msg.id and user == ctx.author

                    done, pending = await asyncio.wait([
                        self.bot.wait_for("reaction_add", check = check),
                        self.bot.wait_for("reaction_remove", check = check)
                    ], return_when = asyncio.FIRST_COMPLETED)

                    reaction, user = done.pop().result()

                    # Cancel any futures
                    for future in pending:
                        future.cancel()
                    
                    # Reaction is FIRST_PAGE
                    if str(reaction) == FIRST_PAGE:
                        current = 0
                    
                    # Reaction is LAST_PAGE
                    elif str(reaction) == LAST_PAGE:
                        current = len(drinks) - 1
                    
                    # Reaction is PREVIOUS_PAGE
                    elif str(reaction) == PREVIOUS_PAGE:
                        current -= 1
                        if current < 0:
                            current = 0
                    
                    # Reaction is NEXT_PAGE
                    elif str(reaction) == NEXT_PAGE:
                        current += 1
                        if current > len(drinks) - 1:
                            current = len(drinks) - 1
                    
                    # Reaction is LEAVE
                    elif str(reaction) == LEAVE:
                        await msg.delete()
                        break
                    
                    # Update event
                    await msg.edit(
                        embed = await parse_drink(ctx, drinks[current])
                    )
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def setup(bot):
    bot.add_cog(Food(bot))