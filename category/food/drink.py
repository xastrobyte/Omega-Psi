import discord

from category.globals import FIELD_THRESHOLD

from util.functions import get_embed_color

async def parse_drink(ctx, drink):
    """Parses the JSON object that holds the drink data
    and turns it into a Discord Embed
    """
    
    # Iterate through the ingredients and the amount
    ingredients = {}
    for ing_num in range(1, 21):
        ing_str = "strIngredient{}".format(ing_num)
        measure_str = "strMeasure{}".format(ing_num)
        if ing_str in drink:
            if drink[ing_str] != "":
                ingredients[drink[ing_str]] = drink[measure_str]
    
    # Create the embed
    embed = discord.Embed(
        title = drink["strDrink"] + " - " + drink["strAlcoholic"],
        description = (
            "**Type**: {}\n".format(drink["strCategory"]) +
            "**Tags**: {}\n".format(drink["strTags"])
        ),
        colour = await get_embed_color(ctx.author)
    ).set_image(
        url = drink["strDrinkThumb"]
    )

    # Create the ingredient fields
    ingredient_fields = []
    field_text = ""
    for ing in ingredients:

        ing = "{} {}\n".format(
            ingredients[ing], ing
        )

        if len(ing) + len(field_text) > FIELD_THRESHOLD:
            ingredient_fields.append(field_text)
            field_text = ""
        
        field_text += ing
    
    if len(field_text) > 0:
        ingredient_fields.append(field_text)

    # Create the instruction fields
    instruction_fields = []
    field_text = ""
    for step in drink["strInstructions"].split("\n"):

        step = step.replace("\r", "") + "\n"

        if len(step) + len(field_text) > FIELD_THRESHOLD:
            instruction_fields.append(field_text)
            field_text = ""
        
        field_text += step
    
    if len(field_text) > 0:
        instruction_fields.append(step)

    # Create the other link fields
    other_links = {
        "strYoutube": "Youtube",
        "strSource": "Source"
    }
    other_link_fields = []
    field_text = ""
    for other_link in other_links:
        if other_link in drink:
            if drink[other_link] != None:
                
                other_link = "[**{}**]({})\n".format(
                    other_links[other_link],
                    drink[other_link]
                )

                if len(other_link) + len(field_text) > FIELD_THRESHOLD:
                    other_link_fields.append(field_text)
                    field_text = ""
                
                field_text += other_link
        
    if len(field_text) > 0:
        other_link_fields.append(field_text)

    # Add all the fields to the embed
    count = 0
    for field in ingredient_fields:
        count += 1
        embed.add_field(
            name = "Ingredients {}".format(
                "({} / {})".format(
                    count, len(ingredient_fields)
                ) if len(ingredient_fields) > 1 else ""
            ),
            value = field,
            inline = False
        )
    
    count = 0
    for field in instruction_fields:
        count += 1
        embed.add_field(
            name = "Instructions {}".format(
                "({} / {})".format(
                    count, len(instruction_fields)
                ) if len(instruction_fields) > 1 else ""
            ),
            value = field,
            inline = False
        )
    
    count = 0
    for field in other_link_fields:
        count += 1
        embed.add_field(
            name = "Other Links {}".format(
                "({} / {})".format(
                    count, len(other_link_fields)
                ) if len(other_link_fields) > 1 else ""
            ),
            value = field,
            inline = False
        )
    
    return embed