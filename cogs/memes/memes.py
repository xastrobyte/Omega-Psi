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

TEAR_RIVERS = Meme(
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
        description="",
        cog_name="memes"
    )
    async def let_me_in(self, ctx, *, text=None):
        """Allows a user to generate the Let Me In meme made famous
        by Eric Andre

        :param ctx: The context of where the message was sent
        :param text: The text to place on Eric Andre
        """
        await ctx.send(embed = UNIMPLEMENTED_ERROR)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    @command(
        name="whiteboardRobin",
        description="",
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

    # # # # # # # # # # # # # # # # # # # # # # # # #

    # # # # # # # # # # # # # # # # # # # # # # # # #

    # # # # # # # # # # # # # # # # # # # # # # # # #

    # # # # # # # # # # # # # # # # # # # # # # # # #

    # # # # # # # # # # # # # # # # # # # # # # # # #

    # # # # # # # # # # # # # # # # # # # # # # # # #

def setup(bot):
    bot.add_cog(Memes(bot))