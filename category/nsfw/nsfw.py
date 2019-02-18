import discord, requests
from discord.ext import commands

import database
from category import errors
from category.globals import PRIMARY_EMBED_COLOR, FIELD_THRESHOLD
from category.predicates import is_nsfw_or_private
from util.string import split_text
from util.discord import get_reddit_post

# # # # # # # # # # # # # # # # # # # # # # # # #

URBAN_API_CALL = "https://api.urbandictionary.com/v0/define?term={}"
URBAN_ICON = "https://vignette.wikia.nocookie.net/creation/images/b/b7/Urban_dictionary_--_logo.jpg/revision/latest?cb=20161002212954"

# # # # # # # # # # # # # # # # # # # # # # # # #

class NSFW:
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @commands.command(
        name = "boobs",
        aliases = ["tits", "boobies"],
        description = "Sends a random picture of a nice set of tits.",
        cog_name = "NSFW"
    )
    @commands.check(is_nsfw_or_private)
    async def boobs(self, ctx):

        await ctx.send(
            embed = await get_reddit_post("boobs")
        )
    
    @commands.command(
        name = "booty",
        aliases= ["ass"],
        description = "Sends a random picture of a nice ass.",
        cog_name = "NSFW"
    )
    @commands.check(is_nsfw_or_private)
    async def booty(self, ctx):
        
        await ctx.send(
            embed = await get_reddit_post("booty")
        )
    
    @commands.command(
        name = "lesbian",
        aliases= ["lesbians"],
        description = "Get some of that lesbian action.",
        cog_name = "NSFW"
    )
    @commands.check(is_nsfw_or_private)
    async def lesbian(self, ctx):
        
        await ctx.send(
            embed = await get_reddit_post("lesbians")
        )
    
    @commands.command(
        name = "goneWild",
        aliases= ["wild"],
        description = "Girls gone wild.",
        cog_name = "NSFW"
    )
    @commands.check(is_nsfw_or_private)
    async def gone_wild(self, ctx):
        
        await ctx.send(
            embed = await get_reddit_post("gonewild")
        )
    
    @commands.command(
        name = "urban",
        description = "Gives you the top 5 urban dictionary entries for a term.",
        cog_name = "NSFW"
    )
    @commands.check(is_nsfw_or_private)
    async def urban(self, ctx, *, phrase = None):
        
        # Check if phrase is None; Throw error message
        if phrase == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need a phrase to look up on Urban Dictionary."
                )
            )
        
        # Phrase is not None; Search for term
        else:

            try:
                
                urban = await database.loop.run_in_executor(None,
                    requests.get,
                    URBAN_API_CALL.format(phrase.replace(" ", "+"))
                )
                urban = urban.json()

                # Get first 5 values (or values if there are less than 5)
                if len(urban["list"]) < 5:
                    definitions = urban["list"]
                else:
                    definitions = urban["list"][:5]
                
                # Create discord embed
                embed = discord.Embed(
                    title = "{} Results Of `{}`".format("Top 5" if len(definitions) > 5 else "", phrase),
                    description = " ",
                    colour = PRIMARY_EMBED_COLOR
                )

                # Add definitions
                defCount = 0
                for definition in definitions:
                    defCount += 1

                    # Get definition; Split up into multiple fields if necessary
                    definitionFields = split_text(definition["definition"], FIELD_THRESHOLD)

                    count = 0
                    for field in definitionFields:
                        count += 1
                        embed.add_field(
                            name = "Definition {} {}".format(
                                defCount,
                                "({} / {})".format(
                                    count, len(definitionFields)
                                ) if len(definitionFields) > 1 else ""
                            ),
                            value = field,
                            inline = False
                        )
                    
                await ctx.send(
                    embed = embed
                )

            except:
                await ctx.send(
                    embed = errors.get_error_message(
                        "There were no entries found for that phrase."
                    )
                )
    
    @boobs.error
    @booty.error
    @lesbian.error
    @gone_wild.error
    @urban.error
    async def nsfw_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(
                embed = errors.get_error_message(
                    "This command can only be run in an NSFW channel or a private channel."
                )
            )

def setup(bot):
    bot.add_cog(NSFW(bot))