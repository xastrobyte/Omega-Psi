import discord, os, requests

from discord.ext import commands
from functools import partial

from category.globals import get_embed_color

from database import loop

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

DOG_API = "https://dog.ceo/api/breeds/image/random"
CAT_API = "https://api.thecatapi.com/v1/images/search"
FOX_API = "https://randomfox.ca/floof/"

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class Animal(commands.Cog, name = "animal"):
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @commands.command(
        name = "dog",
        aliases = ["doggy"],
        description = "Sends a random picture of a random dog from the internet.",
        cog_name = "animal"
    )
    async def dog(self, ctx):
        
        # Call the dog api
        result = await loop.run_in_executor(None,
            requests.get,
            DOG_API
        )
        result = result.json()

        # Send the message with the dog
        await ctx.send(
            embed = discord.Embed(
                title = "Dog from the internet",
                description = " ",
                colour = await get_embed_color(ctx.author)
            ).set_image(
                url = result["message"]
            )
        )
    
    @commands.command(
        name = "cat",
        aliases = ["kitty"],
        description = "Sends a random picture of a random cat from the internet.",
        cog_name = "animal"
    )
    async def cat(self, ctx):
        
        # Call that cat api
        result = await loop.run_in_executor(None,
            partial(
                requests.get,
                CAT_API,
                headers = {
                    "x-api-key": os.environ["CAT_API_KEY"]
                }
            )
        )
        result = result.json()

        # Send the message with the cat
        await ctx.send(
            embed = discord.Embed(
                title = "Cat from the internet",
                description = " ",
                colour = await get_embed_color(ctx.author)
            ).set_image(
                url = result[0]["url"]
            )
        )
    
    @commands.command(
        name = "fox",
        description = "Sends a random picture of a random fox from the internet.",
        cog_name = "animal"
    )
    async def fox(self, ctx):
        
        # Call that fox api
        result = await loop.run_in_executor(None,
            requests.get,
            FOX_API
        )
        result = result.json()

        # Send the message with the fox
        await ctx.send(
            embed = discord.Embed(
                title = "Fox from the internet",
                description = " ",
                colour = await get_embed_color(ctx.author)
            ).set_image(
                url = result["image"]
            )
        )
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def setup(bot):
    bot.add_cog(Animal(bot))