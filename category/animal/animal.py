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
        await self.animal_command("dog", ctx, data)
    
    @commands.command(
        name = "cat",
        aliases = ["kitty"],
        description = "Sends a random picture of a random cat from the internet.",
        cog_name = "animal"
    )
    async def cat(self, ctx, data = None):
        await self.animal_command("cat", ctx, data)
    
    @commands.command(
        name = "fox",
        description = "Sends a random picture of a random fox from the internet.",
        cog_name = "animal"
    )
    async def fox(self, ctx, data = None):
        await self.animal_command("fox", ctx, data)
    
    @commands.command(
        name = "penguin",
        description = "Sends a random picture of a random penguin from the internet.",
        cog_name = "animal"
    )
    async def penguin(self, ctx, data = None):
        await self.animal_command("penguin", ctx, data)
    
    @commands.command(
        name = "elephant",
        description = "Sends a random picture of a random elephant from the internet.",
        cog_name = "animal"
    )
    async def elephant(self, ctx, data = None):
        await self.animal_command("elephant", ctx, data)
    
    @commands.command(
        name = "sloth",
        description = "Sends a random picture of a random sloth from the internet.",
        cog_name = "animal"
    )
    async def sloth(self, ctx, data = None):
        await self.animal_command("sloth", ctx, data)
    
    @commands.command(
        name = "rabbit",
        description = "Sends a random picture of a random rabbit from the internet.",
        cog_name = "animal"
    )
    async def rabbit(self, ctx, data = None):
        await self.animal_command("rabbit", ctx, data)
    
    @commands.command(
        name = "hedgehog",
        description = "Sends a random picture of a random hedgehog from the internet.",
        cog_name = "animal"
    )
    async def hedgehog(self, ctx, data = None):
        await self.animal_command("hedgehog", ctx, data)

    @commands.command(
        name = "bat",
        description = "Sends a random picture of a random bat from the internet.",
        cog_name = "animal"
    )
    async def bat(self, ctx, data = None):
        await self.animal_command("bat", ctx, data)
    
    @commands.command(
        name = "squirrel",
        description = "Sends a random picture of a random squirrel from the internet.",
        cog_name = "animal"
    )
    async def squirrel(self, ctx, data = None):
        await self.animal_command("squirrel", ctx, data)
    
    @commands.command(
        name = "hamster",
        description = "Sends a random picture of a random hamster from the internet.",
        cog_name = "animal"
    )
    async def hamster(self, ctx, data = None):
        await self.animal_command("hamster", ctx, data)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def animal_command(self, animal, ctx, data = None):

        # Check if the data is not getting a fact
        if data != "fact":

            # Call the animal API for the animal
            result = await loop.run_in_executor(None,
                requests.get,
                ANIMAL_API.format(
                    animal,
                    "&baby=true" if data == "baby" else ""
                )
            )
            result = result.json()

            # Send the message with the animal
            await ctx.send(
                embed = discord.Embed(
                    title = "{} from the internet".format(
                        "Baby {}".format(
                            animal.lower()
                        ) if data == "baby" else animal.title()
                    ),
                    description = " ",
                    colour = await get_embed_color(ctx.author)
                ).set_image(
                    url = result["value"]
                )
            )
        
        # Check if getting an animal fact
        else:
            await ctx.send(
                embed = errors.get_error_message(
                    "This hasn't been implemented yet :("
                )
            )

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def setup(bot):
    bot.add_cog(Animal(bot))