import discord, requests

from discord.ext import commands

from category import errors

from category.globals import loop

from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

ANIMAL_API = "https://www.fellowhashbrown.com/api/animals?type={}{}"

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
    async def dog(self, ctx, data = None):
        
        # Check if the data is not getting a fact
        if data != "fact":

            # Call the animal API for dog
            result = await loop.run_in_executor(None,
                requests.get,
                ANIMAL_API.format(
                    "dog",
                    "&baby=true" if data == "baby" else ""
                )
            )
            result = result.json()

            # Send the message with the dog
            await ctx.send(
                embed = discord.Embed(
                    title = "{} from the internet".format(
                        "Baby dog" if data == "baby" else "Dog"
                    ),
                    description = " ",
                    colour = await get_embed_color(ctx.author)
                ).set_image(
                    url = result["value"]
                )
            )
        
        # Check if getting a dog fact
        else:
            await ctx.send(
                embed = errors.get_error_message(
                    "This hasn't been implemented yet :("
                )
            )
    
    @commands.command(
        name = "cat",
        aliases = ["kitty"],
        description = "Sends a random picture of a random cat from the internet.",
        cog_name = "animal"
    )
    async def cat(self, ctx, data = None):
        
        # Check if the data is not getting a fact
        if data != "fact":

            # Call the animal API for cat
            result = await loop.run_in_executor(None,
                requests.get,
                ANIMAL_API.format(
                    "cat",
                    "&baby=true" if data == "baby" else ""
                )
            )
            result = result.json()

            # Send the message with the cat
            await ctx.send(
                embed = discord.Embed(
                    title = "{} from the internet".format(
                        "Baby cat" if data == "baby" else "Cat"
                    ),
                    description = " ",
                    colour = await get_embed_color(ctx.author)
                ).set_image(
                    url = result["value"]
                )
            )
        
        # Check if getting a cat fact
        else:
            await ctx.send(
                embed = errors.get_error_message(
                    "This hasn't been implemented yet :("
                )
            )
    
    @commands.command(
        name = "fox",
        description = "Sends a random picture of a random fox from the internet.",
        cog_name = "animal"
    )
    async def fox(self, ctx, data = None):
        
        # Check if the data is not getting a fact
        if data != "fact":

            # Call the animal API for fox
            result = await loop.run_in_executor(None,
                requests.get,
                ANIMAL_API.format(
                    "fox",
                    "&baby=true" if data == "baby" else ""
                )
            )
            result = result.json()

            # Send the message with the fox
            await ctx.send(
                embed = discord.Embed(
                    title = "{} from the internet".format(
                        "Baby fox" if data == "baby" else "Fox"
                    ),
                    description = " ",
                    colour = await get_embed_color(ctx.author)
                ).set_image(
                    url = result["value"]
                )
            )
        
        # Check if getting a fox fact
        else:
            await ctx.send(
                embed = errors.get_error_message(
                    "This hasn't been implemented yet :("
                )
            )
    
    @commands.command(
        name = "penguin",
        description = "Sends random picture of penguins from the internet.",
        cog_name = "animal"
    )
    async def penguin(self, ctx, data = None):

        # Check if the data is not getting a fact
        if data != "fact":

            # Call the animal API for penguin
            result = await loop.run_in_executor(None,
                requests.get,
                ANIMAL_API.format(
                    "penguin",
                    "&baby=true" if data == "baby" else ""
                )
            )
            result = result.json()

            # Send the message with the penguin
            await ctx.send(
                embed = discord.Embed(
                    title = "{} from the internet".format(
                        "Baby penguin" if data == "baby" else "Penguin"
                    ),
                    description = " ",
                    colour = await get_embed_color(ctx.author)
                ).set_image(
                    url = result["value"]
                )
            )
        
        # Check if getting a penguin fact
        else:
            await ctx.send(
                embed = errors.get_error_message(
                    "This hasn't been implemented yet :("
                )
            )
    
    @commands.command(
        name = "elephant",
        description = "Sends random picture of elephants from the internet.",
        cog_name = "animal"
    )
    async def elephant(self, ctx, data = None):

        # Check if the data is not getting a fact
        if data != "fact":

            # Call the animal API for elephant
            result = await loop.run_in_executor(None,
                requests.get,
                ANIMAL_API.format(
                    "elephant",
                    "&baby=true" if data == "baby" else ""
                )
            )
            result = result.json()

            # Send the message with the elephant
            await ctx.send(
                embed = discord.Embed(
                    title = "{} from the internet".format(
                        "Baby elephant" if data == "baby" else "Elephant"
                    ),
                    description = " ",
                    colour = await get_embed_color(ctx.author)
                ).set_image(
                    url = result["value"]
                )
            )
        
        # Check if getting a elephant fact
        else:
            await ctx.send(
                embed = errors.get_error_message(
                    "This hasn't been implemented yet :("
                )
            )
    
    @commands.command(
        name = "sloth",
        description = "Sends random picture of sloths from the internet.",
        cog_name = "animal"
    )
    async def sloth(self, ctx, data = None):

        # Check if the data is not getting a fact
        if data != "fact":

            # Call the animal API for sloth
            result = await loop.run_in_executor(None,
                requests.get,
                ANIMAL_API.format(
                    "sloth",
                    "&baby=true" if data == "baby" else ""
                )
            )
            result = result.json()

            # Send the message with the sloth
            await ctx.send(
                embed = discord.Embed(
                    title = "{} from the internet".format(
                        "Baby sloth" if data == "baby" else "Sloth"
                    ),
                    description = " ",
                    colour = await get_embed_color(ctx.author)
                ).set_image(
                    url = result["value"]
                )
            )
        
        # Check if getting a sloth fact
        else:
            await ctx.send(
                embed = errors.get_error_message(
                    "This hasn't been implemented yet :("
                )
            )
    
    @commands.command(
        name = "rabbit",
        description = "Sends random picture of rabbits from the internet.",
        cog_name = "animal"
    )
    async def rabbit(self, ctx, data = None):

        # Check if the data is not getting a fact
        if data != "fact":

            # Call the animal API for rabbit
            result = await loop.run_in_executor(None,
                requests.get,
                ANIMAL_API.format(
                    "rabbit",
                    "&baby=true" if data == "baby" else ""
                )
            )
            result = result.json()

            # Send the message with the rabbit
            await ctx.send(
                embed = discord.Embed(
                    title = "{} from the internet".format(
                        "Baby rabbit" if data == "baby" else "Rabbit"
                    ),
                    description = " ",
                    colour = await get_embed_color(ctx.author)
                ).set_image(
                    url = result["value"]
                )
            )
        
        # Check if getting a rabbit fact
        else:
            await ctx.send(
                embed = errors.get_error_message(
                    "This hasn't been implemented yet :("
                )
            )

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def setup(bot):
    bot.add_cog(Animal(bot))