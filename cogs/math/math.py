from discord import Embed
from discord.ext.commands import Cog, command
from requests import get
from urllib.parse import quote_plus

from cogs.errors import get_error_message
from cogs.globals import loop

from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # #

NEWTON_API_CALL = "https://newton.now.sh/{}/{}"


# # # # # # # # # # # # # # # # # # # # # # # # #


async def newton(ctx, operation, *, expression=None):
    """Accesses and returns the contents of a Newton API call

    :param ctx: The context of where the message was sent
    :param operation: The operation to use
    :param expression: The expression to evaluate
    """

    # Check if expression is None
    if expression is None:
        await ctx.send(
            embed=get_error_message(
                "In order to run the `{}` command, you need to specify an expression.".format(operation)
            )
        )

    # Expression is not None
    else:

        # Make expression URL-safe and call the API
        expression = quote_plus(expression.replace("/", "(over)").replace(" ", ""))
        response = await loop.run_in_executor(
            None, get, NEWTON_API_CALL.format(operation, expression)
        )
        response = response.json()

        # Create embed and send message
        await ctx.send(
            embed=Embed(
                title=operation,
                description="Result: `{}`".format(response["result"]),
                colour=await get_embed_color(ctx.author)
            )
        )


class Math(Cog, name="math"):
    """Mathematical stuff like calculus and basic algebra!"""

    def __init__(self, bot):
        self.bot = bot

    # # # # # # # # # # # # # # # # # # # # # # # # #

    @command(
        name="simplify",
        description="Simplifies a mathematical expression.",
        cog_name="math"
    )
    async def simplify(self, ctx, *, expression=None):
        """Allows a user to simplify an expression

        :param ctx: The context of where the message was sent
        :param expression: The expression to evaluate
        """
        await newton(ctx, "simplify", expression=expression)

    @command(
        name="factor",
        description="Attempts to factor a mathematical expression.",
        cog_name="math"
    )
    async def factor(self, ctx, *, expression=None):
        """Allows a user to factor an expression

        :param ctx: The context of where the message was sent
        :param expression: The expression to evaluate
        """
        await newton(ctx, "factor", expression=expression)

    @command(
        name="derivative",
        aliases=["derivate", "derive", "dv"],
        description="Attempts to take the derivative of a mathematical expression.",
        cog_name="math"
    )
    async def derivative(self, ctx, *, expression=None):
        """Allows a user to find the derivative of an expression

        :param ctx: The context of where the message was sent
        :param expression: The expression to evaluate
        """
        await newton(ctx, "derive", expression=expression)

    @command(
        name="integral",
        aliases=["integrate"],
        description="Attempts to integrate a mathematical expression.",
        cog_name="math"
    )
    async def integral(self, ctx, *, expression=None):
        """Allows a user to find the integral of an expression

        :param ctx: The context of where the message was sent
        :param expression: The expression to evaluate
        """
        await newton(ctx, "integrate", expression=expression)

    @command(
        name="zeroes",
        aliases=["zero"],
        description="Attempts to find the zeroes of a mathematical expression.",
        cog_name="math"
    )
    async def zeroes(self, ctx, *, expression=None):
        """Allows a user to get the zeroes of an expression

        :param ctx: The context of where the message was sent
        :param expression: The expression to evaluate
        """
        await newton(ctx, "zeroes", expression=expression)

    @command(
        name="cosine",
        aliases=["cos"],
        description="Attempts to get the cosine of a value.",
        cog_name="math"
    )
    async def cosine(self, ctx, *, value=None):
        """Allows a user to find the cosine of a value

        :param ctx: The context of where the message was sent
        :param value: The value to use
        """
        await newton(ctx, "cos", expression=value)

    @command(
        name="sine",
        aliases=["sin"],
        description="Attempts to get the sine of a value.",
        cog_name="math"
    )
    async def sine(self, ctx, *, value=None):
        """Allows a user to find the sine of a value

        :param ctx: The context of where the message was sent
        :param value: The value to use
        """
        await newton(ctx, "sin", expression=value)

    @command(
        name="tangent",
        aliases=["tan"],
        description="Attempts to get the tangent of a value.",
        cog_name="math"
    )
    async def tangent(self, ctx, *, value=None):
        """Allows a user to find the tangent of a value

        :param ctx: The context of where the message was sent
        :param value: The value to use
        """
        await newton(ctx, "tan", expression=value)

    @command(
        name="arccosine",
        aliases=["arccos"],
        description="Attempts to get the inverse cosine of a value.",
        cog_name="math"
    )
    async def arccosine(self, ctx, *, value=None):
        """Allows a user to find the arccosine of a value

        :param ctx: The context of where the message was sent
        :param value: The value to use
        """
        await newton(ctx, "arccos", expression=value)

    @command(
        name="arcsine",
        aliases=["arcsin"],
        description="Attempts to get the inverse sine of a value.",
        cog_name="math"
    )
    async def arcsine(self, ctx, *, value=None):
        """Allows a user to find the arcsine of a value

        :param ctx: The context of where the message was sent
        :param value: The value to use
        """
        await newton(ctx, "arcsin", expression=value)

    @command(
        name="arctangent",
        aliases=["arctan"],
        description="Attempts to get the inverse tangent of a value.",
        cog_name="math"
    )
    async def arctangent(self, ctx, *, value=None):
        """Allows a user to find the arctangent of a value

        :param ctx: The context of where the message was sent
        :param value: The value to use
        """
        await newton(ctx, "arctan", expression=value)

    @command(
        name="absolute",
        aliases=["abs"],
        description="Attempts to get the absolute value of a value.",
        cog_name="math"
    )
    async def absolute(self, ctx, *, value=None):
        """Allows a user to get the absolute value of a number

        :param ctx: The context of where the message was sent
        :param value: The value to use
        """
        await newton(ctx, "abs", expression=value)

    @command(
        name="tangentLine",
        aliases=["tanLine"],
        description="Attempts to find the tangent line of a function at a given value x.",
        cog_name="math"
    )
    async def tangent_line(self, ctx, x=None, *, expression=None):
        """Allows a user to find the tangent of an expression

        :param ctx: The context of where the message was sent
        :param x: The point to get the tangent line at
        :param expression: The expression to evaluate
        """

        # Check if x is None
        if x is None:
            await ctx.send(
                embed=get_error_message(
                    "In order to get the tangent line at a point, you need the x value."
                )
            )

        # Check if expression is None
        elif expression is None:
            await ctx.send(
                embed=get_error_message(
                    "In order to get the tangent line at x, you need the expression."
                )
            )

        # Neither are None; Call the API
        else:

            # Make expression URL-safe and call the API
            expression = quote_plus(
                "{}|{}".format(
                    x,
                    expression.replace("/", "(over)").replace(" ", "")
                )
            )
            response = await loop.run_in_executor(
                None, get, NEWTON_API_CALL.format("tangent", expression)
            )
            response = response.json()

            # Create embed and send message
            await ctx.send(
                embed=Embed(
                    title="Tangent Line",
                    description="Result: `{}`".format(response["result"]),
                    colour=await get_embed_color(ctx.author)
                )
            )

    @command(
        name="areaUnderCurve",
        aliases=["areaCurve", "area"],
        description="Attempts to find the area underneath a curve.",
        cog_name="math"
    )
    async def area_under_curve(self, ctx, x_start=None, x_end=None, *, expression=None):
        """Allows a user to find the area underneath a curve

        :param ctx: The context of where the message was sent
        :param x_start: The x value to start at
        :param x_end: The x value to end at
        :param expression: The expression to evaluate
        """

        # Check if x_start is None
        if x_start is None:
            await ctx.send(
                embed=get_error_message(
                    "In order to find the area underneath a curve, you need to specify the starting x point."
                )
            )

        # Check if x_end is None
        elif x_start is None:
            await ctx.send(
                embed=get_error_message(
                    "In order to find the area underneath a curve, you need to specify the ending x point."
                )
            )

        # Check if expression is None
        elif expression is None:
            await ctx.send(
                embed=get_error_message(
                    "In order to find the area underneath a curve, you need the expression."
                )
            )

        # Nothing is None; Call the API
        else:

            # Make expression URL-safe and call the API
            expression = quote_plus(
                "{}:{}|{}".format(
                    x_start, x_end,
                    expression.replace("/", "(over)").replace(" ", "")
                )
            )
            response = await loop.run_in_executor(None,
                                                  get,
                                                  NEWTON_API_CALL.format("area", expression)
                                                  )
            response = response.json()

            # Create embed and send message
            await ctx.send(
                embed=Embed(
                    title="Area under a curve",
                    description="Result: `{}`".format(response["result"]),
                    colour=await get_embed_color(ctx.author)
                )
            )

    @command(
        name="logarithm",
        aliases=["log"],
        description="Finds the logarithm of a number. Default base is 10",
        cog_name="math"
    )
    async def log(self, ctx, value=None, base: int = 10):
        """Allows a user to find the log of a number

        :param ctx: The context of where the message was sent
        :param value: The value to find the logarithm of
        :param base: The base of the logarithm
        """

        # Check if value is None
        if value is None:
            await ctx.send(
                embed=get_error_message(
                    "To get the logarithm of a number, you need to specify the number."
                )
            )

        else:

            # Make expression URL-safe and call the API
            expression = quote_plus(
                "{}|{}".format(
                    base,
                    value
                )
            )
            response = await loop.run_in_executor(None,
                                                  get,
                                                  NEWTON_API_CALL.format("log", expression)
                                                  )
            response = response.json()

            # Create embed and send message
            await ctx.send(
                embed=Embed(
                    title="Logarithm",
                    description="Result: `{}`".format(response["result"]),
                    colour=await get_embed_color(ctx.author)
                )
            )


def setup(bot):
    """Add's this cog to the bot

    :param bot: The bot to add the cog to
    """
    bot.add_cog(Math(bot))
