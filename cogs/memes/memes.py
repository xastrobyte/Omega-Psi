from discord import Embed
from discord.ext.commands import Cog, command, group

from cogs.errors import UNIMPLEMENTED_ERROR

from .meme import Meme, TextLocation

# # # # # # # # # # # # # # # # # # # # # # # # #

LET_ME_IN = Meme(
    "https://i.imgur.com/rJjiiXm.jpg",
    person_text = TextLocation(190, 100, centered=True)
)

WHITEBOARD_ROBIN = Meme(
    "https://i.imgur.com/ePhhBSB.png",
    whiteboard_text = TextLocation(360, 490, centered=True)
)

PLANKTON = Meme(
    "https://i.imgur.com/HruGayy.jpg",
    text = TextLocation(30, 30)
)

SIDE_EYE_PUPPET = Meme(
    "https://i.imgur.com/FeB1EgN.jpg",
    text = TextLocation(30, 30)
)

CRYING_KID = Meme(
    "https://i.imgur.com/jcy9ZoR.png",
    text = TextLocation(30, 30, centered=False)
)

RIVER_OF_TEARS = Meme(
    "https://i.imgur.com/rG5tlEM.png",
    text = TextLocation(30, 30, centered=False)
)

GRUS_PLAN = Meme(
    "https://i.imgur.com/mEREPlZ.jpg",
    panel_1 = TextLocation(390, 190, centered=True),
    panel_2 = TextLocation(900, 190, centered=True),
    panel_3 = TextLocation(390, 530, centered=True),
    panel_4 = TextLocation(900, 530, centered=True)
)

OR_DRAW_25 = Meme(
    "https://i.imgur.com/kMW9tje.png",
    card_text   = TextLocation(430, 430, centered=True),
    person_text = TextLocation(1250, 530)
)

CAPTAIN_NOW = Meme(
    "https://i.imgur.com/JXn8R3n.jpg",
    captain_text = TextLocation(110, 140, centered=True),
    pirate_text  = TextLocation(480, 120, centered=True),
    lower_text   = TextLocation(304, 590, centered=True)
)

# # # # # # # # # # # # # # # # # # # # # # # # #

open_memes = {}

# # # # # # # # # # # # # # # # # # # # # # # # #

class Memes(Cog, name="memes"):
    """Generate memes in this category :)"""
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @command(
        name="letMeIn",
        description=f"Generates a meme based on Eric Andre saying \"Let me in\". View the base meme here: {LET_ME_IN.base_image}",
        cog_name="memes"
    )
    async def let_me_in(self, ctx, *, person_text=None):
        """Allows a user to generate the Let Me In meme made famous
        by Eric Andre

        :param ctx: The context of where the message was sent
        :param text: The text to place on Eric Andre
        """
        await ctx.send(embed = UNIMPLEMENTED_ERROR)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    @command(
        name="whiteboardRobin",
        description=f"Generates a meme based on Robin, from Stranger Things, holding a whiteboard. View the base meme here: {WHITEBOARD_ROBIN.base_image}",
        cog_name="memes"
    )
    async def whiteboard_robin(self, ctx, *, whiteboard_text=None):
        """Allows a user to generate the Whiteboard Robin meme
        from Stranger Things season 3

        :param ctx: The context of where the message was sent
        :param text: The text to place on the whiteboard
        """
        await ctx.send(embed = UNIMPLEMENTED_ERROR)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    @command(
        name="plankton", aliases=["getThisFar"],
        description=f"Generates a meme based on Plankton, from Spongebob, saying \"I never thought I'd get this far\". View the base meme here: {PLANKTON.base_image}",
        cog_name="memes"
    )
    async def plankton(self, ctx, *, text=None):
        """Allows a user to generate a meme based on Plankton
        saying "I didn't think I'd get this far"

        :param ctx: The context of where the message was sent
        :param text: The string of text to place above the image of Plankton
        """
        await ctx.send(embed = UNIMPLEMENTED_ERROR)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    @command(
        name="sideEyePuppet", aliases=["sideEye"],
        description=f"Generates a meme based on an awkward-looking puppet that looks as if it's giving a side-eye. View the base meme here: {SIDE_EYE_PUPPET.base_image}",
        cog_name="memes"
    )
    async def side_eye_puppet(self, ctx, *, text=None):
        """Allows a user to generate a meme based on a puppet
        giving a side-eye

        :param ctx: The context of where the message was sent
        :param text: The string of text to place above the puppet images
        """
        await ctx.send(embed = UNIMPLEMENTED_ERROR)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    @command(
        name="cryingKid",
        description=f"Generates a meme based on a kid crying while holding a knife. View the base image here: {CRYING_KID.base_image}",
        cog_name="memes"
    )
    async def crying_kid(self, ctx, *, text=None):
        """Allows a user to generate a meme based on a kid
        crying while holding a knife

        :param ctx: The context of where the message was sent
        :param text: The string of text to place above the images of the kid crying
        """
        await ctx.send(embed = UNIMPLEMENTED_ERROR)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    @command(
        name="riverOfTears",
        description=f"Generates a meme based on someone saying \"This is a river of my tears\" while pointing to a river. View the base image here: {RIVER_OF_TEARS.base_image}",
        cog_name="memes"
    )
    async def river_of_tears(self, ctx, *, text=None):
        """Allows a user to generate a meme based on someone saying
        "This is a river of my tears" while pointing to a river

        :param ctx: The context of where the message was sent
        :param text: The string of text to place above the image
        """
        await ctx.send(embed = UNIMPLEMENTED_ERROR)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    @group(
        name="grusPlan",
        description="Helps to generate a meme based on a 4-panel image of Gru, from Despicable Me, coming up with a plan. View the base image here: {GRUS_PLAN.base_image}",
        cog_name="memes"
    )
    async def grus_plan(self, ctx):
        """Allows a user to begin creating a meme for grus plan

        :param ctx: The context of where the message was sent
        """
        await ctx.send(embed = UNIMPLEMENTED_ERROR)
    
    @grus_plan.command(
        name="panel1",
        description="Sets the text for panel1 of the Grus Plan meme",
        cog_name="memes"
    )
    async def grus_plan_panel_1(self, ctx, *, text=None):
        await ctx.send(embed = UNIMPLEMENTED_ERROR)
    
    @grus_plan.command(
        name="panel2",
        description="Sets the text for panel2 of the Grus Plan meme",
        cog_name="memes"
    )
    async def grus_plan_panel_2(self, ctx, *, text=None):
        await ctx.send(embed = UNIMPLEMENTED_ERROR)
    
    @grus_plan.command(
        name="panel34",
        description="Sets the text for the last 2 panels of the Grus Plan meme",
        cog_name="memes"
    )
    async def grus_plan_panel_3_4(self, ctx, *, text=None):
        await ctx.send(embed = UNIMPLEMENTED_ERROR)
    
    @grus_plan.command(
        name="finish",
        description="Sends the generated meme for Grus Plan",
        cog_name="memes"
    )
    async def grus_plan_finish(self, ctx):
        await ctx.send(embed = UNIMPLEMENTED_ERROR)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    @group(
        name="orDraw25",
        description=f"Helps to generate a meme based on the 2-panel image of a custom Uno card that ends with \"Or Draw 25\". View the base image here: {OR_DRAW_25.base_image}",
        cog_name="memes"
    )
    async def or_draw_25(self, ctx):
        await ctx.send(embed = UNIMPLEMENTED_ERROR)
    
    @or_draw_25.command(
        name="card",
        description="Sets the text on the Uno card",
        cog_name="memes"
    )
    async def or_draw_25_card(self, ctx, *, text=None):
        await ctx.send(embed = UNIMPLEMENTED_ERROR)
    
    @or_draw_25.command(
        name="person",
        description="Sets the text on top of the person holding the 25 uno cards",
        cog_name="memes"
    )
    async def or_draw_25_person(self, ctx, *, text=None):
        await ctx.send(embed = UNIMPLEMENTED_ERROR)
    
    @or_draw_25.command(
        name="finish",
        description="Sends the generated meme for Draw 25",
        cog_name="memes"
    )
    async def or_draw_25_finish(self, ctx):
        await ctx.send(embed = UNIMPLEMENTED_ERROR)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    @group(
        name="imTheCaptain",
        description=f"Helps to generate a meme based on the \"Captain Phillips\" movie scene where the pirate says \"Look at me. I'm the captain now\". View the base image here: {CAPTAIN_NOW.base_image}",
        cog_name="memes"
    )
    async def im_the_captain(self, ctx):
        await ctx.send(embed = UNIMPLEMENTED_ERROR)
    
    @im_the_captain.command(
        name="captain",
        description="Sets the text on top of the original captain",
        cog_name="memes"
    )
    async def im_the_captain_captain(self, ctx, *, text=None):
        await ctx.send(embed = UNIMPLEMENTED_ERROR)
    
    @im_the_captain.command(
        name="pirate",
        description="Sets the text on top of the pirate",
        cog_name="memes"
    )
    async def im_the_captain_pirate(self, ctx, *, text=None):
        await ctx.send(embed = UNIMPLEMENTED_ERROR)
    
    @im_the_captain.command(
        name="lowerText",
        description="Sets the text on the lower text where the quote is usually \"I'm the captain now\"",
        cog_name="memes"
    )
    async def im_the_captain_lower(self, ctx, *, text=None):
        await ctx.send(embed = UNIMPLEMENTED_ERROR)
    
    @im_the_captain.command(
        name="finish",
        description="Sends the generated meme for I'm The Captain",
        cog_name="memes"
    )
    async def im_the_captain_finish(self, ctx):
        await ctx.send(embed = UNIMPLEMENTED_ERROR)

    # # # # # # # # # # # # # # # # # # # # # # # # #

def setup(bot):
    bot.add_cog(Memes(bot))