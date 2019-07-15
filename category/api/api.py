import discord, json, requests

from discord.ext import commands
from functools import partial

from category import errors
from category.globals import get_embed_color, FIELD_THRESHOLD

from database import loop

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

BASE_API_CALL = "https://www.fellowhashbrown.com/api/{}"
VALID_APIS = [
    "hangman", "scramble",
    "morse", "logic",
    "profanity",
    "llamas", "office"
]

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class API(commands.Cog, name = "api"):
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @commands.command(
        name = "apiHangman",
        description = "Allows you to test the Hangman API",
        cog_name = "api"
    )
    async def hangman_api(self, ctx):
        await self.call_api(ctx, "hangman")
    
    @commands.command(
        name = "apiScramble",
        description = "Allows you to test the Scramble API",
        cog_name = "api"
    )
    async def scramble_api(self, ctx):
        await self.call_api(ctx, "scramble")
    
    @commands.command(
        name = "apiMorse",
        description = "Allows you to test the Morse API",
        cog_name = "api"
    )
    async def morse_api(self, ctx, conversion = None, *, text = ""):
        
        # Check if the conversion doesn't exist or is invalid
        if conversion == None or conversion not in ["encode", "decode"]:
            await ctx.send(
                embed = errors.get_error_message(
                    "You must specify either `encode` or `decode` for the Morse API."
                )
            )
        
        # Conversion exists and is valid and text exists
        else:
            await self.call_api(
                ctx, "morse",
                data = {
                    "text": text
                },
                extra = conversion
            )

    @commands.command(
        name = "apiLogic",
        description = "Allows you to test the Logic API",
        cog_name = "api"
    )
    async def logic_api(self, ctx, *, expression = ""):
        await self.call_api(
            ctx, "logic",
            data = {
                "expression": "".join(expression)
            }
        )
    
    @commands.command(
        name = "apiProfanity",
        description = "Allows you to test the Profanity API",
        cog_name = "api"
    )
    async def profanity_api(self, ctx, text = ""):
        await self.call_api(ctx, "profanity", data = {"text": text})
    
    @commands.command(
        name = "apiLlamas",
        description = "Allows you to test the Llamas API",
        cog_name = "api"
    )
    async def llamas_api(self, ctx, episode: int = None, author = None, any_type: bool = False, script: bool = False):
        data = {
            "episode": episode,
            "author": author
        }
        if any_type:
            data["any"] = True
        if script:
            data["fullScript"] = True
        
        await self.call_api(ctx, "llamas", data = data)
    
    @commands.command(
        name = "apiOffice",
        description = "Allows you to test the Office API",
        cog_name = "api"
    )
    async def office_api(self, ctx, season: int = None, episode: int = None, type: str = "aired"):
        await self.call_api(
            ctx, "office",
            data = {
                "season": season,
                "episode": episode,
                "type": type
            }
        )

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def call_api(self, ctx, api, *, data = {}, extra = None):

        # Only run if api is valid
        if api in VALID_APIS:
            api_call = BASE_API_CALL

            # Special APIs
            if api == "morse":
                api_call = BASE_API_CALL + "/" + extra
            
            # Call the API
            response = await loop.run_in_executor(None,
                partial(
                    requests.get,
                    api_call.format(api),
                    params = data
                )
            )
            json_result = response.json()

            # Create the embed
            embed = discord.Embed(
                title = "API Result",
                description = "**API Call**: {}".format(
                    response.url
                ),
                colour = await get_embed_color(ctx.author)
            )

            # Add the response field(s)
            lines = json.dumps(json_result, indent = 4).split("\n")
            fields = []
            field_text = ""
            for line in lines:

                line += "\n"
                if len(field_text) + len(line) > FIELD_THRESHOLD:
                    fields.append(field_text)
                    field_text = ""
                
                field_text += line
            
            if len(field_text) > 0:
                fields.append(field_text)
            
            count = 0
            for field in fields:
                embed.add_field(
                    name = "Response `{}`".format(response.status_code) if count == 0 else "_ _",
                    value = "```py\n{}\n```".format(field),
                    inline = False
                )
                count += 1
            
            # Send the message
            await ctx.send(
                embed = embed
            )
        
        # API is invalid
        else:
            await ctx.send(
                embed = errors.get_error_message(
                    "That is not a valid API"
                )
            )

def setup(bot):
    bot.add_cog(API(bot))