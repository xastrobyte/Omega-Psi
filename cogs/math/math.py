from discord import Embed
from discord.ext.commands import Cog, command
from requests import get
from urllib.parse import quote_plus

from cogs.errors import get_error_message
from cogs.globals import loop

from util.functions import get_embed_color

from .matrix import Matrix, Vector, Scalar, SizeMismatchError, NotAnIntegerError

# # # # # # # # # # # # # # # # # # # # # # # # #

NEWTON_API_CALL = "https://newton.now.sh/api/v2/{}/{}"


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
        name="matrix",
        description="Gives you information about a matrix you enter. The format is tuples separated by semi-colons: (1, 2, 3); (4, 5, 6)",
        cog_name="math"
    )
    async def matrix(self, ctx, *, matrix_entry=None):
        """Allows a user to get information about a matrix
        they enter

        :param ctx: The context of where the message was sent
        :param matrix_entry: The vectors of the matrix
        """

        if matrix_entry is not None:

            try:

                # Check if the format of the matrix entry is valid
                #   by removing all whitespace from the entry
                new_entry = ""
                for c in matrix_entry:
                    if c != " ":
                        new_entry += c
            
                vectors = new_entry.split(";")
                new_vectors = []
                for i in range(len(vectors)):
                    if len(vectors[i]) != 0:
                        if vectors[i][0] != "(" and vectors[i][-1] != ")":
                            raise ValueError()
                        else:
                            vector = vectors[i][1:-1].split(",")
                            new_vectors.append([
                                s for s in vector if len(s) > 0
                            ])
                
                # Create the matrix and show the data
                vectors = []
                invalid = False
                for vector in new_vectors:
                    for scalar in vector:
                        if Scalar(scalar) >= 2 ** 16:
                            invalid = True
                            break
                    if invalid:
                        break
                
                # Only show the matrix if it is valid
                if invalid:
                    await ctx.send(embed = get_error_message(
                        "There are values too large to use in the matrix :("
                    ))
                    return None

                matrix = Matrix([
                    Vector([
                        Scalar(s)
                        for s in v
                    ])
                    for v in new_vectors
                ])
                if matrix.width * matrix.height > 25:
                    raise IndexError()

                # Setup the embed fields
                embed = Embed(
                    title = "Matrix",
                    description = f"```\n{str(matrix)}\n```",
                    colour = await get_embed_color(ctx.author)
                )
                fields = {
                    "REF": f"```\n{str(matrix.REF())}\n```",
                    "RREF": f"```\n{str(matrix.RREF())}\n```",
                    "Inverse": "N/A" if not matrix.is_square() else f"```\n{str(matrix.inverse())}\n```",

                    "Trace": "N/A" if not matrix.is_square() else str(matrix.trace()),
                    "Determinant": "N/A" if not matrix.is_square() else str(matrix.determinant()),
                    "Rank": str(matrix.rank()),
                    "Nullity": str(matrix.nullity()),

                    "Linearly Independent Vectors": f"```\n{str(Matrix([ matrix.vectors[i] for i in matrix.get_li_vectors() ]))}\n```",
                    "Linearly Dependent Vectors": "None" if len(matrix.get_ld_vectors()) == 0 else f"```\n{str(Matrix([ matrix.vectors[i] for i in matrix.get_ld_vectors() ]))}\n```",

                    "Rowspace": f"```\n{str(matrix.rowspace())}\n```",
                    "Colspace": f"```\n{str(matrix.columnspace())}\n```",
                    "Nullspace": "None" if len(matrix.get_ld_vectors()) == 0 else f"```\n{str(matrix.nullspace())}\n```",

                    "Orthogonal Bases": f"```\n{str(matrix.get_orthogonal_base())}\n```"
                }
                for field in fields:
                    embed.add_field(
                        name = field,
                        value = fields[field]
                    )

                await ctx.send(embed = embed)
            except ValueError:
                await ctx.send(embed = get_error_message(
                    "The matrix must follow the format of `({integers});({integers})`."
                ))
            except SizeMismatchError:
                await ctx.send(embed = get_error_message(
                    "The vectors are not all the same size :("
                ))
            except NotAnIntegerError:
                await ctx.send(embed = get_error_message(
                    "Matrices don't use text. Sorry try that again :)"
                ))
            except IndexError:
                await ctx.send(embed = get_error_message(
                    "There's a limit to the matrices of 25 entries. You passed that :("
                ))
        
        else:
            await ctx.send(embed = get_error_message(
                "There is no matrix. You must specify the matrix!"
            ))

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
