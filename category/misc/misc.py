import asyncio, discord, pytz, requests, typing
from datetime import datetime
from discord.ext import commands
from functools import partial
from random import randint, choice

from category import errors
from category.globals import MESSAGE_THRESHOLD, SCROLL_REACTIONS, FIRST_PAGE, LAST_PAGE, PREVIOUS_PAGE, NEXT_PAGE, LEAVE, FIELD_THRESHOLD
from category.globals import get_embed_color
from category.predicates import guild_only

from database import loop
from database import database

from util.string import timestamp_to_datetime, datetime_to_string

# # # # # # # # # # # # # # # # # # # # # # # # #

ADVICE_URL = "https://api.adviceslip.com/advice"
CHUCK_NORRIS_URL = "https://api.chucknorris.io/jokes/random"
COIT_URL = "https://coit.pw/{}"
DAD_JOKE_API = "https://icanhazdadjoke.com"
NUMBER_FACT_RANDOM_URL = "http://numbersapi.com/random/trivia?json"
NUMBER_FACT_NUMBER_URL = "http://numbersapi.com/{}?json"
TODAY_HISTORY_URL = "https://history.muffinlabs.com/date/{}/{}"
TRONALD_DUMP_QUOTE = "https://api.tronalddump.io/random/quote"
LLAMAS_API = "https://www.fellowhashbrown.com/api/llamas?episode={}&fullScript={}"

TWITTER_ICON = "http://pngimg.com/uploads/twitter/twitter_PNG29.png"

EMOJI_DIGITS = [
    ":zero:",
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

class Misc(commands.Cog, name = "Misc"):
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
        advice = await loop.run_in_executor(None,
            requests.get,
            ADVICE_URL
        )
        advice = advice.json()

        await ctx.send(
            embed = discord.Embed(
                title = "Advice Number {}".format(advice["slip"]["slip_id"]),
                description = advice["slip"]["advice"],
                colour = await get_embed_color(ctx.author),
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
        chuckNorrisJson = await loop.run_in_executor(None,
            requests.get,
            CHUCK_NORRIS_URL
        )
        chuckNorrisJson = chuckNorrisJson.json()

        await ctx.send(
            embed = discord.Embed(
                name = "Chuck Norris",
                description = chuckNorrisJson["value"],
                colour = await get_embed_color(ctx.author),
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
        description = "Gives you the information about a color given the HEX code.",
        cog_name = "Misc"
    )
    async def color(self, ctx, hex_code = None):

        # Check if hex_code is None; Throw error message
        if hex_code == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need to specify the hex code for the color."
                ),
                delete_after = 5
            )
        
        # Check if hex_code is not valid hex
        elif len(hex_code) > 8 or len([char for char in hex_code if char not in "0123456789abcdef"]) > 0:
            await ctx.send(
                embed = errors.get_error_message(
                    "The hex code you gave is an invalid hex code."
                )
            )

        # Color is valid
        else:
            embed = discord.Embed(
                title = "#{}".format(hex_code.upper()),
                description = "_ _",
                colour = eval("0x{}".format(hex_code[:6])) # only get first 6 hex digits for embed color
            ).set_image(
                url = COIT_URL.format(hex_code)
            )
        
            await ctx.send(
                embed = embed
            )
        
    @commands.command(
        name = "dadJoke",
        aliases = ["dad"],
        description = "Gives you a random dad joke.",
        cog_name = "Misc"
    )
    async def dad_joke(self, ctx):

        # Call dad joke API
        response = await loop.run_in_executor(None,
            partial(
                requests.get,
                DAD_JOKE_API,
                headers = {
                    "User-Agent": "Omega Psi (https://repl.it/@FellowHashbrown/Omega-Psi)",
                    "Accept": "application/json"
                }
            )
        )
        response = response.json()

        await ctx.send(
            embed = discord.Embed(
                title = "Dad Joke",
                description = response["joke"],
                colour = await get_embed_color(ctx.author)
            )
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
                    result += EMOJI_DIGITS[int(char)]
                elif char in SYMBOLS:
                    result += SYMBOLS[char]
                else:
                    result += char
                
            await ctx.send(
                result
            )
    
    @commands.command(
        name = "todayInHistory",
        aliases = ["todayHistory", "today"],
        description = "Shows you a random fact about something that happened today in history.",
        cog_name = "Misc"
    )
    async def today(self, ctx):

        # Get today's date (Mountain Timezone)
        today = datetime.now().astimezone(pytz.timezone("US/Mountain"))
        month = today.month
        day = today.day

        # Call API
        response = await loop.run_in_executor(None,
            requests.get,
            TODAY_HISTORY_URL.format(
                month, day
            )
        )
        response = response.json()

        # Get wikipedia entry url
        url = response["url"]
        date = response["date"]

        # Get a random death, random birth, and a random event
        event = choice(response["data"]["Events"])
        birth = choice(response["data"]["Births"])
        death = choice(response["data"]["Deaths"])

        fields = {
            "Event": "[**{}**]({})\n{}".format(
                event["year"],
                event["links"][0]["link"],
                event["text"]
            ),
            "Birth": "[**{}**]({})\n{}".format(
                birth["year"],
                birth["links"][0]["link"],
                birth["text"]
            ),
            "Death": "[**{}**]({})\n{}".format(
                death["year"],
                death["links"][0]["link"],
                death["text"]
            )
        }

        # Add data to an embed
        embed = discord.Embed(
            title = date,
            description = "_ _",
            colour = await get_embed_color(ctx.author),
            url = url
        )

        for field in fields:
            embed.add_field(
                name = field,
                value = fields[field]
            )
        
        await ctx.send(
            embed = embed
        )
    
    @commands.command(
        name = "llamas",
        description = "Gives you a random quote from Llamas With Hats. You can also get the full script of an episode by adding \"script\" to the end of the command.",
        cog_name = "Misc"
    )
    async def llamas(self, ctx, episode : int = None, script = None):
        
        # Check if episode is none; Choose random episode
        if episode == None:
            episode = randint(1, 12)
        
        # Check if episode is valid
        if episode >= 1 and episode <= 12:
            script = False if script == None else (script in ["full", "script", "yes", "true", "t"])

            # Make API call
            response = await loop.run_in_executor(None,
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
                    colour = await get_embed_color(ctx.author)
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
                    colour = await get_embed_color(ctx.author)
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
                        colour = await get_embed_color(ctx.author)
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
        number_fact = await loop.run_in_executor(None,
            requests.get,
            target_url
        )
        number_fact = number_fact.json()

        await ctx.send(
            embed = discord.Embed(
                title = "Fact about the number *{}*".format(number_fact["number"]),
                description = number_fact["text"],
                colour = await get_embed_color(ctx.author),
                timestamp = datetime.now()
            ).set_footer(
                text = "NumbersAPI"
            )
        )
    
    @commands.command(
        name = "setEmbedColor",
        aliases = ["setColor", "setEmbed", "embedColor", "embed"],
        description = "Sets the color of the embed for all embeds that are sent. If you call the command with no HEX code, the color will be reset to the default.",
        cog_name = "Misc"
    )
    async def set_embed_color(self, ctx, hex_code = None):

        # Check if resetting
        if hex_code == None:
            await database.users.set_embed_color(ctx.author, None)

            await ctx.send(
                embed = discord.Embed(
                    title = "Embed Color Reset!",
                    description = "Your embed color was reset to the default.",
                    colour = await get_embed_color(ctx.author)
                )
            )

        # Not resetting, setting color
        else:

            # Check if color is a valid HEX color
            if len(hex_code) == 6 and len([char for char in hex_code.lower() if char not in "0123456789abcdef"]) == 0:
                await database.users.set_embed_color(ctx.author, eval("0x{}".format(hex_code)))

                await ctx.send(
                    embed = discord.Embed(
                        title = "Embed Color Set!",
                        description = "Your embed color was set to #{}".format(hex_code),
                        colour = await get_embed_color(ctx.author)
                    )
                )
            
            # Color is not valid
            else:
                await ctx.send(
                    embed = errors.get_error_message(
                        "That is not a valid HEX color code."
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
        quote = await loop.run_in_executor(None,
            requests.get,
            TRONALD_DUMP_QUOTE
        )
        quote = quote.json()

        # Create embed
        await ctx.send(
            embed = discord.Embed(
                title = "Donald Trump Quote",
                description = quote["value"],
                colour = await get_embed_color(ctx.author),
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
            colour = await get_embed_color(ctx.author)
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
                colour = await get_embed_color(ctx.author)
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