import asyncio, discord, requests, typing
from datetime import datetime
from discord.ext import commands
from random import randint

import database
from category import errors
from category.globals import PRIMARY_EMBED_COLOR, MESSAGE_THRESHOLD, SCROLL_REACTIONS, FIRST_PAGE, LAST_PAGE, PREVIOUS_PAGE, NEXT_PAGE, LEAVE, FIELD_THRESHOLD
from category.predicates import guild_only

from util.string import timestamp_to_datetime, datetime_to_string

from .color import process_color

# # # # # # # # # # # # # # # # # # # # # # # # #

ADVICE_URL = "https://api.adviceslip.com/advice"
CHUCK_NORRIS_URL = "https://api.chucknorris.io/jokes/random"
COLOR_HEX_URL = "http://thecolorapi.com/id?hex={}&format=json"
COLOR_RGB_URL = "http://thecolorapi.com/id?rgb={},{},{}&format=json"
COLOR_HSL_URL = "http://thecolorapi.com/id?hsl={},{}%,{}%&format=json"
COLOR_CMYK_URL = "http://thecolorapi.com/id?cmyk={},{},{},{}&format=json"
NUMBER_FACT_RANDOM_URL = "http://numbersapi.com/random/trivia?json"
NUMBER_FACT_NUMBER_URL = "http://numbersapi.com/{}?json"
TRONALD_DUMP_QUOTE = "https://api.tronalddump.io/random/quote"
LLAMAS_API = "https://www.fellowhashbrown.com/api/llamas?episode={}&fullScript={}"

TWITTER_ICON = "http://pngimg.com/uploads/twitter/twitter_PNG29.png"

EMOJI_DIGITS = [
    "1\u20e3",
    "2\u20e3",
    "3\u20e3",
    "4\u20e3",
    "5\u20e3",
    "6\u20e3",
    "7\u20e3",
    "8\u20e3",
    "9\u20e3",
    '\U0001f51f'
]

SYMBOLS = {
    "?": "❓",
    "!": "❗",
    "+": "➕",
    "*": "✖",
    "-": "➖",
    "/": "➗",
    "$": "💲"
}

# # # # # # # # # # # # # # # # # # # # # # # # #

class Misc:
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @commands.command(
        name = "advice",
        description = "Gives you a random piece of advice.",
        cog_name = "Misc"
    )
    async def advice(self, ctx):
        
        # Get the advice
        advice = await database.loop.run_in_executor(None,
            requests.get,
            ADVICE_URL
        )
        advice = advice.json()

        await ctx.send(
            embed = discord.Embed(
                title = "Advice Number {}".format(advice["slip"]["slip_id"]),
                description = advice["slip"]["advice"],
                colour = PRIMARY_EMBED_COLOR,
                timestamp = datetime.now()
            ).set_footer(
                text = "Advice Slip API"
            )
        )
    
    @commands.command(
        name = "chuckNorris",
        description = "Gives you a random Chuck Norris joke.",
        cog_name = "Misc"
    )
    async def chuck_norris(self, ctx):
        
        # Get the joke; and URL
        chuckNorrisJson = await database.loop.run_in_executor(None,
            requests.get,
            CHUCK_NORRIS_URL
        )
        chuckNorrisJson = chuckNorrisJson.json()

        await ctx.send(
            embed = discord.Embed(
                name = "Chuck Norris",
                description = chuckNorrisJson["value"],
                colour = PRIMARY_EMBED_COLOR,
                timestamp = datetime.now()
            ).set_author(
                name = "Chuck Norris Joke",
                icon_url = chuckNorrisJson["icon_url"]
            ).set_footer(
                text = "Chuck Norris API"
            )
        )
    
    @commands.command(
        name = "color",
        description = "Gives you the information about a color given either the HEX, RGB, HSL, or CMYK.",
        cog_name = "Misc"
    )
    async def color(self, ctx, color_type = None, data1 = None, data2 = None, data3 = None, data4 = None):

        # Check if color type is not valid; Throw error message
        if color_type.lower() not in ["hex", "rgb", "hsl", "cmyk"]:
            await ctx.send(
                embed = errors.get_error_message(
                    "The color type you gave was invalid."
                ),
                delete_after = 5
            )

        # Color type is valid
        else:
            
            # HEX Color Type
            if color_type == "hex":

                # HEX has only 1 parameter
                if data1 == None:
                    embed = errors.get_error_message(
                        "You need the HEX code for this color."
                    )

                else:
                    response = await database.loop.run_in_executor(None,
                        requests.get,
                        COLOR_HEX_URL.format(
                            data1
                        )
                    )
                    response = response.json()

                    embed = process_color(response)

            # RGB Color Type
            elif color_type == "rgb":

                # RGB has only 3 parameters
                if data1 == data2 == data3 == None:
                    embed = errors.get_error_message(
                        "You need the rgb value for this color."
                    )

                else:
                    response = await database.loop.run_in_executor(None,
                        requests.get,
                        COLOR_RGB_URL.format(
                            data1, data2, data3
                        )
                    )
                    response = response.json()

                    embed = process_color(response)
            
            # HSL Color Type
            elif color_type == "hsl":

                # HSL has only 3 parameters
                if data1 == data2 == data3 == None:
                    embed = errors.get_error_message(
                        "You need the hsl value for this color."
                    )

                else:
                    response = await database.loop.run_in_executor(None,
                        requests.get,
                        COLOR_HSL_URL.format(
                            data1, data2, data3
                        )
                    )
                    response = response.json()

                    embed = process_color(response)
            
            # CMYK Color Type
            elif color_type == "cmyk":

                # CMYK has only 4 parameters
                if data1 == data2 == data3 == data4 == None:
                    embed = errors.get_error_message(
                        "You need the cmyk value for this color."
                    )
                
                else:
                    response = await database.loop.run_in_executor(None,
                        requests.get,
                        COLOR_CMYK_URL.format(
                            data1, data2, data3, data4
                        )
                    )
                    response = response.json()

                    embed = process_color(response)
        
            await ctx.send(
                embed = embed
            )
    
    @commands.command(
        name = "emojify",
        aliases = ["emoji", "emj"],
        description = "Gives you text but in Emoji style.",
        cog_name = "Misc"
    )
    async def emojify(self, ctx, *, text = None):
        
        # Check if text is None; Throw error message
        if text == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need text to emojify."
                )
            )
        
        # Text is not None; Emojify it
        else:
            result = ""
            for char in text.lower():
                if char.isalpha():
                    result += ":regional_indicator_{}:".format(char)
                elif char.isdigit():
                    result += EMOJI_DIGITS[int(char) - 1]
                elif char in SYMBOLS:
                    result += SYMBOLS[char]
                else:
                    result += char
                
            await ctx.send(
                result
            )
    
    @commands.command(
        name = "llamas",
        description = "Gives you a random quote from Llamas With Hats. You can also get the full script of an episode.",
        cog_name = "Misc"
    )
    async def llamas(self, ctx, episode : int = None, script = None):
        
        # Check if episode is none; Choose random episode
        if episode == None:
            episode = randint(1, 12)
        
        # Check if episode is valid
        if episode >= 1 and episode <= 12:
            script = False if script == None else (script in ["full", "script", "yes"])

            # Make API call
            response = await database.loop.run_in_executor(None,
                requests.get,
                LLAMAS_API.format(
                    episode, script if script else ""
                )
            )
            response = response.json()

            image = response["image"]

            # Create embed
            if not script:
                description = "**{}** {}".format(
                    (response["author"] + ":") if len(response["author"]) > 0 else "",
                    response["value"]
                )

                embed = discord.Embed(
                    title = "Episode {}".format(episode),
                    description = description,
                    colour = PRIMARY_EMBED_COLOR
                )

                if image != None:
                    embed.set_thumbnail(
                        url = image
                    )

                await ctx.send(
                    embed = embed
                )
            
            else:
                fields = []
                fieldText = ""
                for quote in response["quotes"]:
                    line = "**{}** {}\n".format(
                        (quote["author"] + ":") if len(quote["author"]) > 0 else "",
                        quote["value"]
                    )

                    if len(fieldText) + len(line) > MESSAGE_THRESHOLD:
                        fields.append(fieldText)
                        fieldText = ""
                    
                    fieldText += line
                
                if len(fieldText) > 0:
                    fields.append(fieldText)

                embed = discord.Embed(
                    title = "Episode {} - Script {}".format(
                        episode,
                        "({} / {})".format(
                            1, len(fields)
                        ) if len(fields) > 1 else ""
                    ),
                    description = fields[0],
                    colour = PRIMARY_EMBED_COLOR
                )

                if image != None:
                    embed.set_thumbnail(
                        url = image
                    )
                
                # Run the navigation of the script until the user leaves out of it
                msg = await ctx.send(
                    embed = embed
                )

                if len(fields) > 1:

                    if len(fields) > 2:
                        await msg.add_reaction(FIRST_PAGE)
                    
                    await msg.add_reaction(PREVIOUS_PAGE)
                    await msg.add_reaction(NEXT_PAGE)
                    
                    if len(fields) > 2:
                        await msg.add_reaction(LAST_PAGE)

                await msg.add_reaction(LEAVE)

                current = 0
                while True:

                    # Wait for reaction
                    def check(reaction, user):
                        return str(reaction) in SCROLL_REACTIONS and reaction.message.id == msg.id and user == ctx.author
                    
                    done, pending = await asyncio.wait([
                        self.bot.wait_for("reaction_add", check = check),
                        self.bot.wait_for("reaction_remove", check = check)
                    ], return_when = asyncio.FIRST_COMPLETED)

                    reaction, user = done.pop().result()

                    # Cancel all futures
                    for future in pending:
                        future.cancel()
                    
                    # Reaction is first page
                    if str(reaction) == FIRST_PAGE:
                        current = 0
                    
                    # Reaction is last page
                    elif str(reaction) == LAST_PAGE:
                        current = len(fields) - 1
                    
                    # Reaction is previous
                    elif str(reaction) == PREVIOUS_PAGE:
                        current -= 1
                        if current < 0:
                            current = 0
                    
                    # Reaction is next page
                    elif str(reaction) == NEXT_PAGE:
                        current += 1
                        if current >= len(fields):
                            current = len(fields) - 1
                    
                    # Reaction is leave
                    elif str(reaction) == LEAVE:
                        await msg.delete()
                        break
                    
                    # Update embed
                    embed = discord.Embed(
                        title = "Episode {} - Script {}".format(
                            episode,
                            "({} / {})".format(
                                current + 1, len(fields)
                            ) if len(fields) > 1 else ""
                        ),
                        description = fields[current],
                        colour = PRIMARY_EMBED_COLOR
                    )

                    if image != None:
                        embed.set_thumbnail(
                            url = image
                        )
                    
                    await msg.edit(
                        embed = embed
                    )

    
    @commands.command(
        name = "numberFact",
        aliases = ["number"],
        description = "Gives you a fact about a number.",
        cog_name = "Misc"
    )
    async def number_fact(self, ctx, number : int = None):
        
        # Check if number is none; Choose random number
        if number == None:
            target_url = NUMBER_FACT_RANDOM_URL
        
        # Number is not none; Use it
        else:
            target_url = NUMBER_FACT_NUMBER_URL.format(number)
        
        # Get the number fact
        number_fact = await database.loop.run_in_executor(None,
            requests.get,
            target_url
        )
        number_fact = number_fact.json()

        await ctx.send(
            embed = discord.Embed(
                title = "Fact about the number *{}*".format(number_fact["number"]),
                description = number_fact["text"],
                colour = PRIMARY_EMBED_COLOR,
                timestamp = datetime.now()
            ).set_footer(
                text = "NumbersAPI"
            )
        )
    
    @commands.command(
        name = "tronaldDumpQuote",
        aliases = ["tronaldQuote"],
        description = "Gives you a random quote from Donald Trump.",
        cog_name = "Misc"
    )
    async def tronald_dump_quote(self, ctx):
        
        # Get the quote
        quote = await database.loop.run_in_executor(None,
            requests.get,
            TRONALD_DUMP_QUOTE
        )
        quote = quote.json()

        # Create embed
        await ctx.send(
            embed = discord.Embed(
                title = "Donald Trump Quote",
                description = quote["value"],
                colour = PRIMARY_EMBED_COLOR,
                timestamp = timestamp_to_datetime(quote["appeared_at"]),
                url = quote["_embedded"]["source"][0]["url"]
            ).set_author(
                name = quote["_embedded"]["author"][0]["name"],
                icon_url = TWITTER_ICON
            )
        )
    
    @commands.command(
        name = "guildInfo",
        aliases = ["gi"],
        description = "Gives you info about this guild.",
        cog_name = "Misc"
    )
    @commands.check(guild_only)
    async def guild_info(self, ctx):
        
        # Send the guild data
        fields = {
            "Owner": ctx.guild.owner.mention,
            "Created At": datetime_to_string(ctx.guild.created_at),
            "Members": "{} Members\n{} Online\n{} Bots\n{} People".format(
                len(ctx.guild.members),
                len([member for member in ctx.guild.members if member.status == discord.Status.online]),
                len([member for member in ctx.guild.members if member.bot]),
                len([member for member in ctx.guild.members if not member.bot])
            )
        }

        # Create embed
        embed = discord.Embed(
            name = "Guild Info",
            description = " ",
            colour = PRIMARY_EMBED_COLOR
        ).set_footer(
            text = "Server Name: {} | Server ID: {}".format(ctx.guild.name, ctx.guild.id)
        ).set_thumbnail(
            url = ctx.guild.icon_url
        )

        for field in fields:
            embed.add_field(
                name = field,
                value = fields[field]
            )
        
        # Add roles field
        role_fields = []
        role_text = ""
        for role in ctx.guild.roles[::-1]:

            text = role.mention + " "

            if len(role_text) + len(text) > FIELD_THRESHOLD:
                role_fields.append(role_text)
                role_text = ""
            
            role_text += text
        
        if len(role_text) > 0:
            role_fields.append(role_text)
        
        count = 0
        for field in role_fields:
            count += 1
            embed.add_field(
                name = "Roles {}".format(
                    "({} / {})".format(
                        count, len(role_fields)
                    ) if len(role_fields) > 1 else ""
                ),
                value = field,
                inline = False
            )
        
        # Send message
        await ctx.send(
            embed = embed
        )
    
    @commands.command(
        name = "userInfo",
        aliases = ["ui"],
        description = "Gives you info about a member in this guild.",
        cog_name = "Misc"
    )
    @commands.check(guild_only)
    async def user_info(self, ctx, *, user : typing.Union[discord.Member, str] = None):

        # Check if getting info for specific user
        if user != None:

            # Try to find user if not already converted to member
            if type(user) != discord.Member:

                # Iterate through members
                found = False
                for member in ctx.guild.members:
                    if user.lower() in [member.name.lower(), member.nick.lower(), member.display_name.lower()]:
                        user = member
                        found = True
                        break
        
                # User was not found
                if not found:
                    user = None
        
        # Getting info for self
        else:
            user = ctx.author

        # Make sure user is not none
        if user != None:
        
            # Send user data
            fields = {
                "Member": "{} ({}#{})".format(
                    user.mention, 
                    user.name, user.discriminator
                ),
                "Created At": datetime_to_string(user.created_at),
                "Joined At": datetime_to_string(user.joined_at),
                "Permissions": ", ".join([
                    perm.replace("_", " ").title()
                    for perm, has_perm in list(ctx.channel.permissions_for(user))
                    if has_perm == True
                ]) if not ctx.channel.permissions_for(user).administrator else "Administrator",
                "Status": str(user.status)
            }

            # Create embed
            embed = discord.Embed(
                name = "User Info",
                description = " ",
                colour = PRIMARY_EMBED_COLOR
            ).set_thumbnail(
                url = user.avatar_url
            ).set_footer(
                text = "User Name: {} | User ID: {}".format(
                    "{}#{}".format(
                        user.name, user.discriminator
                    ),
                    user.id
                )
            )

            for field in fields:
                embed.add_field(
                    name = field,
                    value = fields[field]
                )
            
            await ctx.send(
                embed = embed
            )
        
        # user is none
        else:
            await ctx.send(
                embed = errors.get_error_message(
                    "There was no member found with that name."
                )
            )
        
    @guild_info.error
    @user_info.error
    async def guild_only_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(
                embed = errors.get_error_message(
                    "This command can only be run in guilds."
                )
            )

def setup(bot):
    bot.add_cog(Misc(bot))
