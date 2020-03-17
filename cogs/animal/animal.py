from discord import Embed
from discord.ext.commands import Cog, group
from requests import get

from cogs.errors import UNIMPLEMENTED_ERROR
from cogs.globals import loop

from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

ANIMAL_API = "https://www.fellowhashbrown.com/api/animals?type={}"
BABY_ANIMAL_API = "https://www.fellowhashbrown.com/api/animals?type={}&baby=true"
ANIMAL_FACT_API = "https://www.fellowhashbrown.com/api/animals?type={}&fact=true"

DOG_FACT_API = "http://dog-api.kinduff.com/api/facts"

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class Animal(Cog, name = "animal"):
    """Animal pictures! and facts (soon)"""

    def __init__(self, bot):
        self.bot = bot

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @group(
        name = "dog", aliases = ["doggo"],
        description = "Get a picture of a random dog from the internet.",
        cog_name = "animal"
    )
    async def dog(self, ctx):
        if not ctx.invoked_subcommand:
            await self.animal_command(ctx, "dog")
    
    @dog.command(
        name = "baby", aliases = ["pupper"],
        description = "Get a picture of a random puppy from the internet.",
        cog_name = "animal"
    )
    async def dog_baby(self, ctx):
        await self.animal_command(ctx, "dog", baby = True)
    
    @dog.command(
        name = "fact",
        description = "Get a random fact about dogs from the internet.",
        cog_name = "animal"
    )
    async def dog_fact(self, ctx):
        await self.animal_command(ctx, "dog", fact = True)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @group(
        name = "cat",
        description = "Get a picture of a random cat from the internet.",
        cog_name = "animal"
    )
    async def cat(self, ctx):
        if not ctx.invoked_subcommand:
            await self.animal_command(ctx, "cat")
    
    @cat.command(
        name = "baby", aliases = ["kitty", "kitten"],
        description = "Get a picture of a random kitten from the internet.",
        cog_name = "animal"
    )
    async def cat_baby(self, ctx):
        await self.animal_command(ctx, "cat", baby = True)
    
    @cat.command(
        name = "fact",
        description = "Get a random fact about cats from the internet.",
        cog_name = "animal"
    )
    async def cat_fact(self, ctx):
        await self.animal_command(ctx, "cat", fact = True)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @group(
        name = "fox",
        description = "Get a picture of a random fox from the internet.",
        cog_name = "animal"
    )
    async def fox(self, ctx):
        if not ctx.invoked_subcommand:
            await self.animal_command(ctx, "fox")
    
    @fox.command(
        name = "baby",
        description = "Get a picture of a random baby fox from the internet.",
        cog_name = "animal"
    )
    async def fox_baby(self, ctx):
        await self.animal_command(ctx, "fox", baby = True)
    
    @fox.command(
        name = "fact",
        description = "Get a random fact about foxs from the internet.",
        cog_name = "animal"
    )
    async def fox_fact(self, ctx):
        await self.animal_command(ctx, "fox", fact = True)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @group(
        name = "penguin",
        description = "Get a picture of a random penguin from the internet.",
        cog_name = "animal"
    )
    async def penguin(self, ctx):
        if not ctx.invoked_subcommand:
            await self.animal_command(ctx, "penguin")
    
    @penguin.command(
        name = "baby",
        description = "Get a picture of a random baby penguin from the internet.",
        cog_name = "animal"
    )
    async def penguin_baby(self, ctx):
        await self.animal_command(ctx, "penguin", baby = True)
    
    @penguin.command(
        name = "fact",
        description = "Get a random fact about penguins from the internet.",
        cog_name = "animal"
    )
    async def penguin_fact(self, ctx):
        await self.animal_command(ctx, "penguin", fact = True)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @group(
        name = "elephant",
        description = "Get a picture of a random elephant from the internet.",
        cog_name = "animal"
    )
    async def elephant(self, ctx):
        if not ctx.invoked_subcommand:
            await self.animal_command(ctx, "elephant")
    
    @elephant.command(
        name = "baby",
        description = "Get a picture of a random baby elephant from the internet.",
        cog_name = "animal"
    )
    async def elephant_baby(self, ctx):
        await self.animal_command(ctx, "elephant", baby = True)
    
    @elephant.command(
        name = "fact",
        description = "Get a random fact about elephants from the internet.",
        cog_name = "animal"
    )
    async def elephant_fact(self, ctx):
        await self.animal_command(ctx, "elephant", fact = True)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @group(
        name = "sloth",
        description = "Get a picture of a random sloth from the internet.",
        cog_name = "animal"
    )
    async def sloth(self, ctx):
        if not ctx.invoked_subcommand:
            await self.animal_command(ctx, "sloth")
    
    @sloth.command(
        name = "baby",
        description = "Get a picture of a random baby sloth from the internet.",
        cog_name = "animal"
    )
    async def sloth_baby(self, ctx):
        await self.animal_command(ctx, "sloth", baby = True)
    
    @sloth.command(
        name = "fact",
        description = "Get a random fact about sloths from the internet.",
        cog_name = "animal"
    )
    async def sloth_fact(self, ctx):
        await self.animal_command(ctx, "sloth", fact = True)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @group(
        name = "rabbit",
        description = "Get a picture of a random rabbit from the internet.",
        cog_name = "animal"
    )
    async def rabbit(self, ctx):
        if not ctx.invoked_subcommand:
            await self.animal_command(ctx, "rabbit")
    
    @rabbit.command(
        name = "baby",
        description = "Get a picture of a random baby rabbit from the internet.",
        cog_name = "animal"
    )
    async def rabbit_baby(self, ctx):
        await self.animal_command(ctx, "rabbit", baby = True)
    
    @rabbit.command(
        name = "fact",
        description = "Get a random fact about rabbits from the internet.",
        cog_name = "animal"
    )
    async def rabbit_fact(self, ctx):
        await self.animal_command(ctx, "rabbit", fact = True)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @group(
        name = "hedgehog",
        description = "Get a picture of a random hedgehog from the internet.",
        cog_name = "animal"
    )
    async def hedgehog(self, ctx):
        if not ctx.invoked_subcommand:
            await self.animal_command(ctx, "hedgehog")
    
    @hedgehog.command(
        name = "baby",
        description = "Get a picture of a random baby hedgehog from the internet.",
        cog_name = "animal"
    )
    async def hedgehog_baby(self, ctx):
        await self.animal_command(ctx, "hedgehog", baby = True)
    
    @hedgehog.command(
        name = "fact",
        description = "Get a random fact about hedgehogs from the internet.",
        cog_name = "animal"
    )
    async def hedgehog_fact(self, ctx):
        await self.animal_command(ctx, "hedgehog", fact = True)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @group(
        name = "bat",
        description = "Get a picture of a random bat from the internet.",
        cog_name = "animal"
    )
    async def bat(self, ctx):
        if not ctx.invoked_subcommand:
            await self.animal_command(ctx, "bat")
    
    @bat.command(
        name = "baby",
        description = "Get a picture of a random baby bat from the internet.",
        cog_name = "animal"
    )
    async def bat_baby(self, ctx):
        await self.animal_command(ctx, "bat", baby = True)
    
    @bat.command(
        name = "fact",
        description = "Get a random fact about bats from the internet.",
        cog_name = "animal"
    )
    async def bat_fact(self, ctx):
        await self.animal_command(ctx, "bat", fact = True)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @group(
        name = "squirrel",
        description = "Get a picture of a random squirrel from the internet.",
        cog_name = "animal"
    )
    async def squirrel(self, ctx):
        if not ctx.invoked_subcommand:
            await self.animal_command(ctx, "squirrel")
    
    @squirrel.command(
        name = "baby",
        description = "Get a picture of a random baby squirrel from the internet.",
        cog_name = "animal"
    )
    async def squirrel_baby(self, ctx):
        await self.animal_command(ctx, "squirrel", baby = True)
    
    @squirrel.command(
        name = "fact",
        description = "Get a random fact about squirrels from the internet.",
        cog_name = "animal"
    )
    async def squirrel_fact(self, ctx):
        await self.animal_command(ctx, "squirrel", fact = True)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @group(
        name = "hamster",
        description = "Get a picture of a random hamster from the internet.",
        cog_name = "animal"
    )
    async def hamster(self, ctx):
        if not ctx.invoked_subcommand:
            await self.animal_command(ctx, "hamster")
    
    @hamster.command(
        name = "baby",
        description = "Get a picture of a random baby hamster from the internet.",
        cog_name = "animal"
    )
    async def hamster_baby(self, ctx):
        await self.animal_command(ctx, "hamster", baby = True)
    
    @hamster.command(
        name = "fact",
        description = "Get a random fact about hamsters from the internet.",
        cog_name = "animal"
    )
    async def hamster_fact(self, ctx):
        await self.animal_command(ctx, "hamster", fact = True)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def animal_command(self, ctx, animal, *, baby = False, fact = False):
        """Runs the animal API to get a random picture or fact of the specified animal"""

        # Check if getting any random image or baby image
        if not fact:
            result = await loop.run_in_executor(None,
                get, ANIMAL_API.format(animal) if not baby else BABY_ANIMAL_API.format(animal)
            )
            result = result.json()
            
            # Send the message with the picture
            await ctx.send(
                embed = Embed(
                    title = "{} from the internet".format(
                        "Baby {}".format(animal.lower()) if baby else animal.title()
                    ),
                    description = " ",
                    colour = await get_embed_color(ctx.author)
                ).set_image(
                    url = result["value"]
                )
            )

        # Check if getting an animal fact
        else:

            # Check if the animal is a dog
            if animal == "dog":
                response = await loop.run_in_executor(None,
                    get, DOG_FACT_API
                )
                response = response.json()
                if response["success"]:
                    embed = Embed(
                        title = "Dog fact",
                        description = response["facts"][0],
                        colour = await get_embed_color(ctx.author)
                    )
                else:
                    embed = Embed(
                        title = "Could not load a fact :(",
                        description = "_ _",
                        colour = await get_embed_color(ctx.author)
                    )
            
            # The fact is for an unimplemented animal fact
            else:
                embed = UNIMPLEMENTED_ERROR
            await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(Animal(bot))