import discord, requests
from discord.ext import commands
from urllib.parse import quote_plus

import database
from category.errors import get_error_message
from category.globals import PRIMARY_EMBED_COLOR

# # # # # # # # # # # # # # # # # # # # # # # # #

NEWTON_API_CALL = "https://newton.now.sh/{}/{}"

# # # # # # # # # # # # # # # # # # # # # # # # #

class Math:
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    async def newton(self, ctx, operation, *, expression = None):

        # Check if expression is None
        if expression == None:
            await ctx.send(
                embed = get_error_message(
                    "In order to run the `{}` command, you need to specify an expression.".format(operation)
                )
            )
        
        # Expression is not None
        else:

            # Make expression URL-safe and call the API
            expression = quote_plus(expression.replace("/", "(over)").replace(" ", ""))
            response = await database.loop.run_in_executor(None,
                requests.get,
                NEWTON_API_CALL.format(operation, expression)
            )
            response = response.json()

            # Create embed and send message
            await ctx.send(
                embed = discord.Embed(
                    title = operation,
                    description = "Result: `{}`".format(response["result"]),
                    colour = PRIMARY_EMBED_COLOR
                )
            )

    @commands.command(
        name = "simplify",
        description = "Simplifies a mathematical expression.",
        cog_name = "Math"
    )
    async def simplify(self, ctx, *, expression = None):
        await self.newton(ctx, "simplify", expression = expression)
    
    @commands.command(
        name = "factor",
        description = "Attempts to factor a mathematical expression.",
        cog_name = "Math"
    )
    async def factor(self, ctx, *, expression = None):
        await self.newton(ctx, "factor", expression = expression)
    
    @commands.command(
        name = "derivative",
        aliases = ["derivate", "derive", "dv"],
        description = "Attempts to take the derivative of a mathematical expression.",
        cog_name = "Math"
    )
    async def derivative(self, ctx, *, expression = None):
        await self.newton(ctx, "derive", expression = expression)
    
    @commands.command(
        name = "integral",
        aliases = ["integrate"],
        description = "Attempts to integrate a mathematical expression.",
        cog_name = "Math"
    )
    async def integral(self, ctx, *, expression = None):
        await self.newton(ctx, "integrate", expression = expression)
    
    @commands.command(
        name = "zeroes",
        aliases = ["zero"],
        description = "Attempts to find the zeroes of a mathematical expression.",
        cog_name = "Math"
    )
    async def zeroes(self, ctx, *, expression = None):
        await self.newton(ctx, "zeroes", expression = expression)
    
    @commands.command(
        name = "cosine",
        aliases = ["cos"],
        description = "Attempts to get the cosine of a value.",
        cog_name = "Math"
    )
    async def cosine(self, ctx, *, value = None):
        await self.newton(ctx, "cos", expression = value)
    
    @commands.command(
        name = "sine",
        aliases = ["sin"],
        description = "Attempts to get the sine of a value.",
        cog_name = "Math"
    )
    async def sine(self, ctx, *, value = None):
        await self.newton(ctx, "sin", expression = value)
    
    @commands.command(
        name = "tangent",
        aliases = ["tan"],
        description = "Attempts to get the tangent of a value.",
        cog_name = "Math"
    )
    async def tangent(self, ctx, *, value = None):
        await self.newton(ctx, "tan", expression = value)
    
    @commands.command(
        name = "arccosine",
        aliases = ["arccos"],
        description = "Attempts to get the inverse cosine of a value.",
        cog_name = "Math"
    )
    async def arccosine(self, ctx, *, value = None):
        await self.newton(ctx, "arccos", expression = value)
    
    @commands.command(
        name = "arcsine",
        aliases = ["arcsin"],
        description = "Attempts to get the inverse sine of a value.",
        cog_name = "Math"
    )
    async def arcsine(self, ctx, *, value = None):
        await self.newton(ctx, "arcsin", expression = value)
    
    @commands.command(
        name = "arctangent",
        aliases = ["arctan"],
        description = "Attempts to get the inverse tangent of a value.",
        cog_name = "Math"
    )
    async def arctangent(self, ctx, *, value = None):
        await self.newton(ctx, "arctan", expression = value)
    
    @commands.command(
        name = "absolute",
        aliases = ["abs"],
        description = "Attempts to get the absolute value of a value.",
        cog_name = "Math"
    )
    async def absolute(self, ctx, *, value = None):
        await self.newton(ctx, "abs", expression = value)
    
    @commands.command(
        name = "tangentLine",
        aliases = ["tanLine"],
        description = "Attempts to find the tangent line of a function at a given value x.",
        cog_name = "Math"
    )
    async def tangent_line(self, ctx, x = None, *, expression = None):

        # Check if x is None
        if x == None:
            await ctx.send(
                embed = get_error_message(
                    "In order to get the tangent line at a point, you need the x value."
                )
            )
        
        # Check if expression is None
        elif expression == None:
            await ctx.send(
                embed = get_error_message(
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
            response = await database.loop.run_in_executor(None,
                requests.get,
                NEWTON_API_CALL.format("tangent", expression)
            )
            response = response.json()

            # Create embed and send message
            await ctx.send(
                embed = discord.Embed(
                    title = "Tangent Line",
                    description = "Result: `{}`".format(response["result"]),
                    colour = PRIMARY_EMBED_COLOR
                )
            )
    
    @commands.command(
        name = "areaUnderCurve",
        aliases = ["areaCurve", "area"],
        description = "Attempts to find the area underneath a curve.",
        cog_name = "Math"
    )
    async def area_under_curve(self, ctx, x_start = None, x_end = None, *, expression = None):

        # Check if x_start is None
        if x_start == None:
            await ctx.send(
                embed = get_error_message(
                    "In order to find the area underneath a curve, you need to specify the starting x point."
                )
            )
        
        # Check if x_end is None
        elif x_start == None:
            await ctx.send(
                embed = get_error_message(
                    "In order to find the area underneath a curve, you need to specify the ending x point."
                )
            )
        
        # Check if expression is None
        elif expression == None:
            await ctx.send(
                embed = get_error_message(
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
            response = await database.loop.run_in_executor(None,
                requests.get,
                NEWTON_API_CALL.format("area", expression)
            )
            response = response.json()

            # Create embed and send message
            await ctx.send(
                embed = discord.Embed(
                    title = "Area under a curve",
                    description = "Result: `{}`".format(response["result"]),
                    colour = PRIMARY_EMBED_COLOR
                )
            )

    @commands.command(
        name = "logarithm",
        aliases = ["log"],
        description = "Finds the logarithm of a number. Default base is 10",
        cog_name = "Math"
    )
    async def log(self, ctx, value = None, base : int = 10):

        # Check if value is None
        if value == None:
            await ctx.send(
                embed = get_error_message(
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
            response = await database.loop.run_in_executor(None,
                requests.get,
                NEWTON_API_CALL.format("log", expression)
            )
            response = response.json()

            # Create embed and send message
            await ctx.send(
                embed = discord.Embed(
                    title = "Logarithm",
                    description = "Result: `{}`".format(response["result"]),
                    colour = PRIMARY_EMBED_COLOR
                )
            )

def setup(bot):
    bot.add_cog(Math(bot))
