from discord import Embed
from discord.ext.commands import Cog, command, group

from cogs.errors import get_error_message

from util.database.database import database
from util.functions import get_embed_color

from .meme import Meme, TextLocation

# # # # # # # # # # # # # # # # # # # # # # # # #

LET_ME_IN = Meme("letMeIn",
    "https://i.imgur.com/O5COinv.jpg", 20,
    person_text = TextLocation(
        380, 180, # x, y
        (0, 0, 0),
        stroke = (255, 255, 255),
        stroke_width = 2,
        center_x = True, center_y = True)
)

WHITEBOARD_ROBIN = Meme("whiteboardRobin",
    "https://i.imgur.com/PbEf3wR.png", 25,
    whiteboard_text = TextLocation(
        360, 490, # x, y
        (0, 0, 0),
        center_x = True, center_y = True)
)

PLANKTON = Meme("plankton",
    "https://i.imgur.com/lOajuz4.jpg", 30,
    text = TextLocation(
        20, 20,
        (0, 0, 0))
)

SIDE_EYE_PUPPET = Meme("sideEyePuppet",
    "https://i.imgur.com/7bMCM2E.jpg", 35,
    text = TextLocation(
        30, 30,
        (0, 0, 0))
)

CRYING_KID = Meme("cryingKid",
    "https://i.imgur.com/70vCQ8V.png", 30,
    text = TextLocation(
        30, 30,
        (0, 0, 0))
)

RIVER_OF_TEARS = Meme("riverOfTears",
    "https://i.imgur.com/hAmhox6.png", 30,
    text = TextLocation(
        30, 30,
        (0, 0, 0))
)

CURE_FOR_DEPRESSION = Meme("cureForDepression",
    "https://i.imgur.com/Oym4DAy.png", 30,
    text = TextLocation(
        600, 600,
        (0, 0, 0),
        stroke = (255, 255, 255),
        stroke_width = 2,
        center_x = True, center_y = True)
)

SACRED_TEXTS = Meme("sacredTexts",
    "https://i.imgur.com/HUfLj9o.png", 25,
    text = TextLocation(
        620, 530,
        (0, 0, 0),
        center_x = True, center_y = True)
)

PASSING_NOTES = Meme("passingNotes",
    "https://i.imgur.com/hjyxlyR.png", 20,
    text = TextLocation(
        410, 460,
        (0, 0, 0),
        stroke_width = 0,
        center_x = True, center_y = True)
)

PUPIL_EXPAND = Meme("pupilExpand",
    "https://i.imgur.com/Fzu0WOk.png", 30,
    upper_text = TextLocation(
        200, 200,
        (0, 0, 0),
        center_x = True, center_y = True),
    lower_text = TextLocation(
        200, 550,
        (0, 0, 0),
        center_x = True, center_y = True)
)


GRUS_PLAN = Meme("grusPlan",
    "https://i.imgur.com/Kit2FFk.jpg", 25,
    panel_1 = TextLocation(
        390, 190, 
        (0, 0, 0),
        center_x = True, center_y = True),
    panel_2 = TextLocation(
        900, 190, 
        (0, 0, 0),
        center_x = True, center_y = True),
    panel_3 = TextLocation(
        390, 530, 
        (0, 0, 0),
        center_x = True, center_y = True),
    panel_4 = TextLocation(
        900, 530, 
        (0, 0, 0),
        center_x = True, center_y = True)
)

OR_DRAW_25 = Meme("orDraw25",
    "https://i.imgur.com/FYvozcC.png", 25,
    card_text   = TextLocation(
        220, 220, 
        (0, 0, 0),
        center_x = True, center_y = True),
    person_text = TextLocation(
        600, 220,
        (255, 255, 255),
        center_x = True, center_y = True)
)

CAPTAIN_NOW = Meme("imTheCaptain",
    "https://i.imgur.com/6fOAgBf.png", 25,
    captain_text = TextLocation(
        110, 140, 
        (0, 0, 0),
        center_x = True, center_y = True),
    pirate_text  = TextLocation(
        480, 120, 
        (0, 0, 0),
        stroke = (255, 255, 255),
        center_x = True, center_y = True),
    lower_text   = TextLocation(
        304, 560, 
        (0, 0, 0),
        stroke = (255, 255, 255),
        stroke_width = 2,
        center_x = True)
)

SPIDER_MAN_2 = Meme("spiderman2",
    "https://i.imgur.com/StWLqml.png", 30,
    left_spiderman = TextLocation(
        220, 180,
        (255, 255, 255),
        center_x = True, center_y = True),
    right_spiderman = TextLocation(
        620, 200,
        (255, 255, 255),
        center_x = True, center_y = True)
)

SPIDER_MAN_3 = Meme("spiderman3",
    "https://i.imgur.com/jqPjErS.png", 30,
    left_spiderman = TextLocation(
        120, 270,
        (255, 255, 255),
        center_x = True, center_y = True),
    right_spiderman = TextLocation(
        500, 280,
        (255, 255, 255),
        center_x = True, center_y = True),
    back_spiderman = TextLocation(
        330, 130,
        (255, 255, 255),
        center_x = True, center_y = True)
)

SAME_PICTURE = Meme("samePicture",
    "https://i.imgur.com/ftkGTQ2.png", 35,
    left_picture = TextLocation(
        160, 120,
        (0, 0, 0),
        center_x = True, center_y = True),
    right_picture = TextLocation(
        460, 160,
        (0, 0, 0),
        center_x = True, center_y = True),
    person_text = TextLocation(
        390, 550,
        (0, 0, 0),
        stroke = (255, 255, 255),
        stroke_width = 2,
        center_x = True, center_y = True)
)

# # # # # # # # # # # # # # # # # # # # # # # # #

open_memes = {
    GRUS_PLAN.id: {},
    CAPTAIN_NOW.id: {},
    OR_DRAW_25.id: {},
    SPIDER_MAN_2.id: {},
    SPIDER_MAN_3.id: {},
    SAME_PICTURE.id: {},
    PUPIL_EXPAND.id: {}
}

THUMBS_UP = "👍"

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
        if person_text is None:
            await ctx.send(embed = get_error_message(
                "You must specify the text to place on the image!"
            ))
        else:
            await ctx.send(
                file = LET_ME_IN.generate(
                    str(ctx.author.id),
                    person_text = person_text))

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
        if whiteboard_text is None:
            await ctx.send(embed = get_error_message(
                "You must specify the text to place on the image!"
            ))
        else:
            await ctx.send(
                file = WHITEBOARD_ROBIN.generate(
                    str(ctx.author.id),
                    whiteboard_text = whiteboard_text))

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
        if text is None:
            await ctx.send(embed = get_error_message(
                "You must specify the text to place on the image!"
            ))
        else:
            await ctx.send(
                file = PLANKTON.generate(
                    str(ctx.author.id),
                    text = text))

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
        if text is None:
            await ctx.send(embed = get_error_message(
                "You must specify the text to place on the image!"
            ))
        else:
            await ctx.send(
                file = SIDE_EYE_PUPPET.generate(
                    str(ctx.author.id),
                    text = text))

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
        if text is None:
            await ctx.send(embed = get_error_message(
                "You must specify the text to place on the image!"
            ))
        else:
            await ctx.send(
                file = CRYING_KID.generate(
                    str(ctx.author.id),
                    text = text))

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
        if text is None:
            await ctx.send(embed = get_error_message(
                "You must specify the text to place on the image!"
            ))
        else:
            await ctx.send(
                file = RIVER_OF_TEARS.generate(
                    str(ctx.author.id),
                    text = text))
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @command(
        name="passingNotes",
        description=f"Generates a meme based on 2 people passing notes. View the base image here: {PASSING_NOTES.base_image}",
        cog_name="memes"
    )
    async def passing_notes(self, ctx, *, text=None):
        """Allows a user to generate a meme based on someone passing a note
        to another person

        :param ctx: The context of where the message was sent
        :param text: The string of text to place on the note
        """
        if text is None:
            await ctx.send(embed = get_error_message(
                "You must specify the text to place on the image!"
            ))
        else:
            await ctx.send(
                file = PASSING_NOTES.generate(
                    str(ctx.author.id),
                    text = text))
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @command(
        name="cureForDepression",
        description=f"Generates a meme based on someone saying they found they cure for depression. View the base image here: {CURE_FOR_DEPRESSION.base_image}",
        cog_name="memes"
    )
    async def cure_for_depression(self, ctx, *, text=None):
        """Allows a user to generate a meme based on someone saying
        they found the cure for depression

        :param ctx: The context of where the message was sent
        :param text: The string of text to place on the note
        """
        if text is None:
            await ctx.send(embed = get_error_message(
                "You must specify the text to place on the image!"
            ))
        else:
            await ctx.send(
                file = CURE_FOR_DEPRESSION.generate(
                    str(ctx.author.id),
                    text = text))
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @command(
        name="sacredTexts",
        description=f"Generates a meme based on someone saying they found sacred texts that bring happiness. View the base image here: {SACRED_TEXTS.base_image}",
        cog_name="memes"
    )
    async def sacred_texts(self, ctx, *, text=None):
        """Allows a user to generate a meme based on someone saying
        they found sacred texts that bring happiness and peace

        :param ctx: The context of where the message was sent
        :param text: The string of text to place on the note
        """
        if text is None:
            await ctx.send(embed = get_error_message(
                "You must specify the text to place on the image!"
            ))
        else:
            await ctx.send(
                file = SACRED_TEXTS.generate(
                    str(ctx.author.id),
                    text = text))
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @group(
        name="pupilExpand",
        description=f"Helps to generate a meme based on the pupil expanding when seeing something you love. View the base image here: {PUPIL_EXPAND.base_image}",
        cog_name="memes"
    )
    async def pupil_expand(self, ctx):
        """Allows a user to generate a meme based on the pupil expanding
        when you see something you love

        :param ctx: The context of where the message was sent
        """
        if not ctx.invoked_subcommand:
            await self.create_meme(
                ctx, PUPIL_EXPAND,
                "Pupil Expanding", {
                    "upper_text": "",
                    "lower_text": ""
                }
            )
    
    @pupil_expand.command(
        name="upperText", aliases=["uppertext", "upper"],
        description="Sets the text on the upper panel of the pupil expand meme",
        cog_name="memes"
    )
    async def pupil_expand_upper(self, ctx, *, text=None):
        """Allows a user to add text to the current pupil expand meme
        on the upper panel

        :param ctx: The context of where the message was sent
        :param text: The string of text to place on the upper panel
        """
        await self.add_text_to_meme(ctx, PUPIL_EXPAND, "upper_text", text)
    
    @pupil_expand.command(
        name="lowerText", aliases=["lowertext", "lower"],
        description="Sets the text on the lower panel of the pupil expand meme",
        cog_name="memes"
    )
    async def pupil_expand_lower(self, ctx, *, text=None):
        """Allows a user to add text to the current pupil expand meme
        on the lower panel

        :param ctx: The context of where the message was sent
        :param text: The string of text to place on the lower panel
        """
        await self.add_text_to_meme(ctx, PUPIL_EXPAND, "lower_text", text)
    
    @pupil_expand.command(
        name="finish",
        description="Sends the generated meme for Pupils Expanding",
        cog_name="memes"
    )
    async def pupil_expand_finish(self, ctx):
        """Allows a user to finish creating the pupil expand meme

        :param ctx: The context of where the message was sent
        """
        await self.finish_meme(ctx, PUPIL_EXPAND)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    @group(
        name="grusPlan",
        description=f"Helps to generate a meme based on a 4-panel image of Gru, from Despicable Me, coming up with a plan (Hint: run this command first). View the base image here: {GRUS_PLAN.base_image}",
        cog_name="memes"
    )
    async def grus_plan(self, ctx):
        """Allows a user to begin creating a meme for grus plan

        :param ctx: The context of where the message was sent
        """
        if not ctx.invoked_subcommand:
            await self.create_meme(
                ctx, GRUS_PLAN,
                "Gru's Plan", {
                    "panel_1": "",
                    "panel_2": "",
                    "panel_3": "",
                    "panel_3": ""
                }
            )
    
    @grus_plan.command(
        name="firstPanel", aliases=["panel1"],
        description="Sets the text for the first panel of the Grus Plan meme",
        cog_name="memes"
    )
    async def grus_plan_panel_1(self, ctx, *, text=None):
        """Allows the user to set the first panel of Grus Plan

        :param ctx: The context of where the message was sent
        :param text: The text to place on the meme
        """
        await self.add_text_to_meme(ctx, GRUS_PLAN, "panel_1", text)
    
    @grus_plan.command(
        name="secondPanel", aliases=["panel2"],
        description="Sets the text for panel2 of the Grus Plan meme",
        cog_name="memes"
    )
    async def grus_plan_panel_2(self, ctx, *, text=None):
        """Allows the user to set the second panel of Grus Plan

        :param ctx: The context of where the message was sent
        :param text: The text to place on the meme
        """
        await self.add_text_to_meme(ctx, GRUS_PLAN, "panel_2", text)
    
    @grus_plan.command(
        name="lastPanels", aliases=["panel34"],
        description="Sets the text for the last 2 panels of the Grus Plan meme",
        cog_name="memes"
    )
    async def grus_plan_panel_3_4(self, ctx, *, text=None):
        """Allows the user to set the last two panels of Grus Plan

        :param ctx: The context of where the message was sent
        :param text: The text to place on the meme
        """
        await self.add_text_to_meme(ctx, GRUS_PLAN, "panel_3", text)
        await self.add_text_to_meme(ctx, GRUS_PLAN, "panel_4", text)
    
    @grus_plan.command(
        name="finish",
        description="Sends the generated meme for Grus Plan",
        cog_name="memes"
    )
    async def grus_plan_finish(self, ctx):
        await self.finish_meme(ctx, GRUS_PLAN)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    @group(
        name="orDraw25",
        description=f"Helps to generate a meme based on the 2-panel image of a custom Uno card that ends with \"Or Draw 25\". View the base image here: {OR_DRAW_25.base_image}",
        cog_name="memes"
    )
    async def or_draw_25(self, ctx):
        """Allows a user to begin creating a meme for Or Draw 25

        :param ctx: The context of where the message was sent
        """
        if not ctx.invoked_subcommand:
            await self.create_meme(
                ctx, OR_DRAW_25,
                "Or Draw 25", {
                    "card_text": "",
                    "person_text": ""
                }
            )
    
    @or_draw_25.command(
        name="card",
        description="Sets the text on the Uno card",
        cog_name="memes"
    )
    async def or_draw_25_card(self, ctx, *, text=None):
        await self.add_text_to_meme(ctx, OR_DRAW_25, "card_text", text)
    
    @or_draw_25.command(
        name="person",
        description="Sets the text on top of the person holding the 25 uno cards",
        cog_name="memes"
    )
    async def or_draw_25_person(self, ctx, *, text=None):
        await self.add_text_to_meme(ctx, OR_DRAW_25, "person_text", text)
    
    @or_draw_25.command(
        name="finish",
        description="Sends the generated meme for Draw 25",
        cog_name="memes"
    )
    async def or_draw_25_finish(self, ctx):
        await self.finish_meme(ctx, OR_DRAW_25)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    @group(
        name="imTheCaptain", aliases=["captainNow"],
        description=f"Helps to generate a meme based on the \"Captain Phillips\" movie scene where the pirate says \"Look at me. I'm the captain now\". View the base image here: {CAPTAIN_NOW.base_image}",
        cog_name="memes"
    )
    async def im_the_captain(self, ctx):
        """Allows a user to begin creating a meme for I'm the Captain

        :param ctx: The context of where the message was sent
        """
        if not ctx.invoked_subcommand:
            await self.create_meme(
                ctx, CAPTAIN_NOW,
                "I'm the Captain", {
                    "captain_text": "",
                    "pirate_text": "",
                    "lower_text": ""
                }
            )
    
    @im_the_captain.command(
        name="captain",
        description="Sets the text on top of the original captain",
        cog_name="memes"
    )
    async def im_the_captain_captain(self, ctx, *, text=None):
        await self.add_text_to_meme(ctx, CAPTAIN_NOW, "captain_text", text)
    
    @im_the_captain.command(
        name="pirate",
        description="Sets the text on top of the pirate",
        cog_name="memes"
    )
    async def im_the_captain_pirate(self, ctx, *, text=None):
        await self.add_text_to_meme(ctx, CAPTAIN_NOW, "pirate_text", text)
    
    @im_the_captain.command(
        name="lowerText",
        description="Sets the text on the lower text where the quote is usually \"I'm the captain now\"",
        cog_name="memes"
    )
    async def im_the_captain_lower(self, ctx, *, text=None):
        await self.add_text_to_meme(ctx, CAPTAIN_NOW, "lower_text", text)
    
    @im_the_captain.command(
        name="finish",
        description="Sends the generated meme for I'm The Captain",
        cog_name="memes"
    )
    async def im_the_captain_finish(self, ctx):
        def default_lower_text():
            if len(open_memes[CAPTAIN_NOW.id][str(ctx.author.id)]["lower_text"]) == 0:
                open_memes[CAPTAIN_NOW.id][str(ctx.author.id)]["lower_text"] = "I'm the captain now"
        await self.finish_meme(ctx, CAPTAIN_NOW, default_lower_text)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    @group(
        name="spiderman2",
        description=f"Helps to generate a meme based on 2 spidermen pointing at each other. View the base image here: {SPIDER_MAN_2.base_image}",
        cog_name="memes"
    )
    async def spiderman_2(self, ctx):
        if not ctx.invoked_subcommand:
            await self.create_meme(
                ctx, SPIDER_MAN_2,
                "2 Spidermen pointing at each other", {
                    "left_spiderman": "",
                    "right_spiderman": ""
                }
            )
    
    @spiderman_2.command(
        name="leftSpiderman", aliases=["leftspiderman", "left"],
        description="",
        cog_name="memes"
    )
    async def spiderman_2_left(self, ctx, *, text=None):
        await self.add_text_to_meme(ctx, SPIDER_MAN_2, "left_spiderman", text)
    
    @spiderman_2.command(
        name="rightSpiderman", aliases=["rightspiderman", "right"],
        description="",
        cog_name="memes"
    )
    async def spiderman_2_right(self, ctx, *, text=None):
        await self.add_text_to_meme(ctx, SPIDER_MAN_2, "right_spiderman", text)
    
    @spiderman_2.command(
        name="finish",
        description="",
        cog_name="memes"
    )
    async def spiderman_2_finish(self, ctx):
        await self.finish_meme(ctx, SPIDER_MAN_2)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    @group(
        name="spiderman3",
        description=f"Helps to generate a meme based on 3 spidermen pointing at each other. View the base image here: {SPIDER_MAN_3.base_image}",
        cog_name="memes"
    )
    async def spiderman_3(self, ctx):
        if not ctx.invoked_subcommand:
            await self.create_meme(
                ctx, SPIDER_MAN_3,
                "3 Spidermen pointing at each other", {
                    "left_spiderman": "",
                    "right_spiderman": "",
                    "back_spiderman": ""
                }
            )
    
    @spiderman_3.command(
        name="leftSpiderman", aliases=["leftspiderman", "left"],
        description="",
        cog_name="memes"
    )
    async def spiderman_3_left(self, ctx, *, text=None):
        await self.add_text_to_meme(ctx, SPIDER_MAN_3, "left_spiderman", text)
    
    @spiderman_3.command(
        name="rightSpiderman", aliases=["rightspiderman", "right"],
        description="",
        cog_name="memes"
    )
    async def spiderman_3_right(self, ctx, *, text=None):
        await self.add_text_to_meme(ctx, SPIDER_MAN_3, "right_spiderman", text)
    
    @spiderman_3.command(
        name="backSpiderman", aliases=["backspiderman", "back"],
        description="",
        cog_name="memes"
    )
    async def spiderman_3_back(self, ctx, *, text=None):
        await self.add_text_to_meme(ctx, SPIDER_MAN_3, "back_spiderman", text)
    
    @spiderman_3.command(
        name="finish",
        description="",
        cog_name="memes"
    )
    async def spiderman_3_finish(self, ctx):
        await self.finish_meme(ctx, SPIDER_MAN_3)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    @group(
        name="samePicture",
        description=f"Helps to generate a meme based on Pam, from The Office, giving a character 2 pictures that are identical and saying that they're the same picture. View the base image here: {SAME_PICTURE.base_image}",
        cog_name="memes"
    )
    async def same_picture(self, ctx):
        if not ctx.invoked_subcommand:
            await self.create_meme(
                ctx, SAME_PICTURE,
                "the Same Picture meme", {
                    "left_picture": "",
                    "right_picture": "",
                    "person_text": ""
                }
            )
    
    @same_picture.command(
        name="leftPicture", aliases=["leftpicture", "left"],
        description="",
        cog_name="memes"
    )
    async def same_picture_left(self, ctx, *, text=None):
        await self.add_text_to_meme(ctx, SAME_PICTURE, "left_picture", text)
    
    @same_picture.command(
        name="rightPicture", aliases=["rightpicture", "right"],
        description="",
        cog_name="memes"
    )
    async def same_picture_right(self, ctx, *, text=None):
        await self.add_text_to_meme(ctx, SAME_PICTURE, "right_picture", text)
    
    @same_picture.command(
        name="person",
        description="",
        cog_name="memes"
    )
    async def same_picture_person(self, ctx, *, text=None):
        await self.add_text_to_meme(ctx, SAME_PICTURE, "person_text", text)
    
    @same_picture.command(
        name="finish",
        description="",
        cog_name="memes"
    )
    async def same_picture_finish(self, ctx):
        await self.finish_meme(ctx, SAME_PICTURE)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    async def create_meme(self, ctx, meme: Meme, meme_name: str, initial_json: dict):
        """Handles creating a new meme

        :param ctx: The context of where the message was sent
        :param meme: The Meme object that is being started
        :param meme_name: The name of the meme
        :param initial_json: The initial JSON object to set the open_memes
            variable with to keep track of the text on the meme
        """

        # Check if the user is already creating a meme
        if str(ctx.author.id) in open_memes[meme.id]:
            await ctx.send(
                embed = get_error_message(
                    f"You are already creating a meme for {meme_name}! Here is what it looks like so far"),
                file = meme.generate(
                    str(ctx.author.id),
                    **open_memes[meme.id][str(ctx.author.id)]))
    
        else:
            open_memes[meme.id][str(ctx.author.id)] = initial_json
            await ctx.send(
                embed = Embed(
                    title = "Meme Ready to Create!",
                    description = "Do `{}help {}` to see how to set the commands.".format(
                        await database.guilds.get_prefix(ctx.guild),
                        meme.id
                    ),
                    colour = await get_embed_color(ctx.author)
                )
            )
    
    async def add_text_to_meme(self, ctx, meme: Meme, key, value):
        """Adds a piece of text to the given meme

        :param ctx: The context of where the message was sent
        :param meme: The Meme object to add the text to
        :param key: The key to set the text for
        :param value: The text to add to the meme
        """
        if str(ctx.author.id) not in open_memes[meme.id]:
            await ctx.send(embed = get_error_message(
                "You must run `{}{}` prior to setting the text for this part of the meme!".format(
                    await database.guilds.get_prefix(ctx.guild),
                    meme.id
                )
            ))
        elif value is None:
            await ctx.send(embed = get_error_message(
                "You must specify the text to add to the meme!"
            ))
        else:
            open_memes[meme.id][str(ctx.author.id)][key] = value
            await ctx.message.add_reaction(THUMBS_UP)
    
    async def finish_meme(self, ctx, meme: Meme, default_text_function=None):
        """Handles finishing the creation of a meme

        :param ctx: The context of where the message was sent
        :param meme: The Meme object to create
        :param default_text_function: The function to default any text that doesn't exist
            in the open memes
        """

        if str(ctx.author.id) not in open_memes[meme.id]:
            await ctx.send(embed = get_error_message(
                "You haven't started to generate this meme yet!"
            ))
        else:

            # Check if none of the text was occupied
            any_occupied = False
            for key in open_memes[meme.id][str(ctx.author.id)]:
                if len(open_memes[meme.id][str(ctx.author.id)][key]) > 0:
                    any_occupied = True
                    break
            if any_occupied:
                if default_text_function is not None:
                    default_text_function()
                await ctx.send(
                    file = meme.generate(
                        str(ctx.author.id),
                        **open_memes[meme.id][str(ctx.author.id)]))
            else:
                await ctx.send(embed = get_error_message(
                    "You didn't specify any text for this meme so the creation has been canceled."
                ))
            open_memes[meme.id].pop(str(ctx.author.id))

    # # # # # # # # # # # # # # # # # # # # # # # # #

def setup(bot):
    bot.add_cog(Memes(bot))