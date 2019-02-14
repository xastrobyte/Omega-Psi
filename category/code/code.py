import base64, discord, os, requests, typing
from discord.ext import commands

from category import errors
from database import loop

from .base_converter import convert
from .logic_parser import LogicTree

# # # # # # # # # # # # # # # # # # # # # # # # #

CODE_EMBED_COLOR = 0xEC7600

LOGIC_API_CALL = "https://www.fellowhashbrown.com/api/logic?expression={}&table=true"
MORSE_API_CALL = "https://www.fellowhashbrown.com/api/morse/{}?text={}"
QR_API_CALL = "https://api.qrserver.com/v1/create-qr-code/?size={0}x{0}&data={1}"

# # # # # # # # # # # # # # # # # # # # # # # # #
# Extension
# # # # # # # # # # # # # # # # # # # # # # # # #

class Code:
    def __init__(self, bot):
        self._bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @commands.command(
        name = "convert", 
        description = "Allows you to convert numbers from one base to another.",
        cog_name = "Code"
    )
    async def convert(self, ctx, start_base : int = None, end_base : int = None, number = None):

        # Check if start_base is None; Throw error message
        if start_base == None:
            embed = errors.get_error_message(
                "You need the `start_base` to convert from, `end_base` to convert to, and the `number` to convert."
            )
        
        # Check if end_base is None; Throw error message
        elif end_base == None:
            embed = errors.get_error_message(
                "You need the `end_base` to convert to and the `number` to convert."
            )
        
        # Check if number is None; Throw error message
        elif number == None:
            embed = errors.get_error_message(
                "You need the `number` to convert."
            )
        
        # Everything exists; Run the command
        else:

            # Make sure both numbers are between 2 and 64
            if start_base >= 2 and start_base <=64 and end_base >= 2 and end_base <= 64:
                
                start = number

                title = "Base-{} --> Base-{}".format(start_base, end_base)
                description = "`{} --> {}`".format(start, number)

                # Check if bases are different
                if start_base != end_base:
                    
                    # Check if number is not zero; Convert it
                    if number not in ["0", 0]:
                        number = convert(number, start_base, end_base)

                        # Check if number is None; Invalid number for a base
                        if number == None:
                            embed = errors.get_error_message(
                                "The number you gave is invalid for the start base."
                            )
                        
                        # Number is not None; Valid number for a base
                        else:
                            embed = discord.Embed(
                                title = title,
                                description = "`{} --> {}`".format(start, number),
                                colour = CODE_EMBED_COLOR
                            )
                    
                    # Number is zero; Send the number
                    else:
                        embed = discord.Embed(
                            title = title,
                            description = description,
                            colour = CODE_EMBED_COLOR
                        )
                
                # Bases are the same; Send the number
                else:
                    embed = discord.Embed(
                        title = title,
                        description = description,
                        colour = CODE_EMBED_COLOR
                    )
            
            # One of them is out of range
            else:
                if start_base < 2 or start_base > 64:
                    embed = errors.get_error_message(
                        "The start base you gave is not between 2 and 64."
                    )
                
                else:
                    embed = errors.get_error_message(
                        "The end base you gave is not between 2 and 64."
                    )

        # Send message
        await ctx.send(
            embed = embed
        )
            
    @commands.command(
        name = "base64", 
        aliases = ["b64"],
        description = "Allows you to encode/decode text into/from Base64 encoding.",
        cog_name = "Code"
    )
    async def base64(self, ctx, conversion = None, *, text : str = None):

        # Check if conversion is None; Throw error message
        if conversion == None:
            embed = errors.get_error_message(
                "You need to specify whether you want to encode or decode."
            )

        # Check if text is None; Throw error message
        elif text == None:
            embed = errors.get_error_message(
                "You need the `text` to convert."
            )
        
        else:

            # Check if conversion is valid
            if conversion in ["encode", "enc", "e"]:
                converted = base64.b64encode(text.encode()).decode()

                embed = discord.Embed(
                    title = "`{}` {} Base64".format(
                        text if len(text) < 180 else "[text is greater than 200 characters]",
                        "encoded to"
                    ),
                    description = converted,
                    colour = CODE_EMBED_COLOR
                )
            
            elif conversion in ["decode", "dec", "d"]:
                converted = base64.b64decode(text.encode()).decode()

                embed = discord.Embed(
                    title = "`{}` {} Base64".format(
                        text if len(text) < 180 else "[text is greater than 200 characters]",
                        "decoded from"
                    ),
                    description = converted,
                    colour = CODE_EMBED_COLOR
                )
            
            # Conversion is invalid
            else:
                embed = errors.get_error_message(
                    "The conversion method you gave is invalid."
                )
        
        # Send message
        await ctx.send(
            embed = embed
        )
    
    @commands.command(
        name = "morse",
        description = "Allows you to encode/decode text into/from Morse Code.",
        cog_name = "Code"
    )
    async def morse(self, ctx, conversion = None, *, text : str = None):

        # Check if conversion is None; Throw error message
        if conversion == None:
            embed = errors.get_error_message(
                "You need to specify whether you want to encode or decode."
            )

        # Check if text is None; Throw error message
        elif text == None:
            embed = errors.get_error_message(
                "You need the `text` to {}.".format(conversion)
            )
        
        else:
            valid = True
            
            # Check if conversion is valid
            if conversion in ["encode", "enc", "e"]:
                conversion = "encode"
            
            elif conversion in ["decode", "dec", "d"]:
                conversion = "decode"
            
            else:
                valid = False

            # Conversion parameter is valid
            if valid:
                response = await loop.run_in_executor(None,
                    requests.get,
                    MORSE_API_CALL.format(
                        conversion,
                        text
                    )
                )
                response = response.json()

                # Check if the API call was a success
                if response["success"]:
                    value = response["value"]
                else:
                    value = response["error"]
                
                embed = discord.Embed(
                    title = "{}".format(
                        "Text to Morse" if conversion == "encode" else "Morse to Text"
                    ) if response["success"] else "Failed to Convert",
                    description = "`{}`".format(value),
                    colour = CODE_EMBED_COLOR
                )

            else:
                embed = errors.get_error_message(
                    "The conversion method you gave is invalid."
                )
        
        # Send message
        await ctx.send(
            embed = embed
        )
    
    @commands.command(
        name = "qrCode", 
        aliases = ["qr"],
        description = "Allows you to create a QR code out of text.",
        cog_name = "Code"
    )
    async def qr_code(self, ctx, *, text : str = None):

        # Check if text is None; Throw error message
        if text == None:
            embed = errors.get_error_message(
                "You need the `text` to convert into a QR code."
            )
        
        else:
            
            # The size should be a function of the text's length
            # Use this --> size = 10(length // 20) + 200
            size = 10*(len(text) // 20) + 200

            embed = discord.Embed(
                title = " ",
                description = " ",
                colour = CODE_EMBED_COLOR
            ).set_image(
                url = QR_API_CALL.format(size, text.replace(" ", "+"))
            )
        
        # Send message
        await ctx.send(
            embed = embed
        )
    
    @commands.command(
        name = "logic",
        description = "Allows you to get a truth table for a logical expression.",
        cog_name = "Code"
    )
    async def logic(self, ctx, *, expression : str = None):

        # Check if expression is None; Throw error message
        if expression == None:
            content = None
            embed = errors.get_error_message(
                "You need the `expression` to parse."
            )
        
        else:

            # Call the Logic API
            response = await loop.run_in_executor(None,
                requests.get,
                LOGIC_API_CALL.format(
                    expression
                )
            )
            response = response.json()

            # See if an error existed
            if not response["success"]:
                embed = errors.get_error_message(
                    response["error"]
                )
                content = None
            
            # No error existed; Get the value
            else:
                truth_table = response["value"]
                content = "```\n{}\n```".format("\n".join(truth_table))
                embed = None
        
        # Check if the content is bigger than 2000
        if len(content) > 2000 or len(truth_table[0]) >= 140:

            # Remove backticks (`)
            content = content.replace("```", "")

            # Create file and send to author
            filename = "logic-{}-{}.txt".format(ctx.author.name, ctx.author.discriminator)
            temp = open(filename, "w")
            temp.write(content)
            temp.close()

            content = "{}, I couldn't send raw text so I put it in a nice little file for you.".format(
                ctx.author.mention
            )

            await ctx.send(
                content,
                file = discord.File(filename)
            )
            os.remove(filename)
        
        else:
            await ctx.send(
                content,
                embed = embed
            )

# # # # # # # # # # # # # # # # # # # # # # # # #
# Setup
# # # # # # # # # # # # # # # # # # # # # # # # #

def setup(bot):
    bot.add_cog(Code(bot))