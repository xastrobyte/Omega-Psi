from discord import Embed
from discord.ext.commands import Cog, command, group
from json import dumps
from requests import get
from urllib.parse import quote

from cogs.errors import get_error_message
from cogs.globals import loop
from cogs.predicates import get_prefix

from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # #

API_BASE_URL = "https://api.fellowhashbrown.com"

# # # # # # # # # # # # # # # # # # # # # # # # #

class API(Cog, name="api"):
    """Use these commands to test my APIs that I've written!"""

    def __init__(self, bot):
        self.bot = bot

    @group(
        name="apiMorse",
        description="Test the morse APIs here",
        cog_name="api"
    )
    async def api_morse(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send(
                embed = get_error_message(
                    "You must either do encode or decode! Try `{}.help apiMorse`".format(
                        await get_prefix(ctx.guild)
                    )
                )
            )
    
    @api_morse.command(
        name="encode",
        description="Test the encode morse API using this command",
        cog_name="api"
    )
    async def api_morse_encode(self, ctx, *, text=""):
        response = await loop.run_in_executor(
            None, get, API_BASE_URL + "/morse/encode", 
            {"text": quote(text)}
        )
        try:
            response = response.json()
            await ctx.send(
                embed = Embed(
                    title = "/morse/encode",
                    description = "```\n{}\n```".format(
                        dumps(response, indent = 4)
                    ),
                    colour = await get_embed_color(ctx.author)
                ).add_field(
                    name = "URL",
                    value = "{}{}?{}".format(
                        API_BASE_URL,
                        "/morse/encode",
                        "text=" + text
                    )
                )
            )
        except:
            await ctx.send(embed = get_error_message(
                "The response seems to not be in JSON :("
            ))
    
    @api_morse.command(
        name="decode",
        description="Test the decode morse API using this command",
        cog_name="api"
    )
    async def api_morse_decode(self, ctx, *, text: str=None):
        response = await loop.run_in_executor(
            None, get, API_BASE_URL + "/morse/decode", 
            {"text": quote(text)}
        )
        try:
            response = response.json()
            await ctx.send(
                embed = Embed(
                    title = "/morse/decode",
                    description = "```\n{}\n```".format(
                        dumps(response, indent = 4)
                    ),
                    colour = await get_embed_color(ctx.author)
                ).add_field(
                    name = "URL",
                    value = "{}{}?{}".format(
                        API_BASE_URL,
                        "/morse/decode",
                        "text=" + text
                    )
                )
            )
        except:
            await ctx.send(embed = get_error_message(
                "The response seems to not be in JSON :("
            ))

def setup(bot):
    bot.add_cog(API(bot))