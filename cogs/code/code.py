from base64 import b64encode, b64decode
from discord import Embed, File
from discord.ext.commands import command, Cog, group
from functools import partial
from io import BytesIO
from os import environ
from PIL import Image
from requests import get, post
from urllib.parse import quote
import json
from asyncio import wait_for, TimeoutError

from cogs.errors import get_error_message
from cogs.globals import loop, FIELD_THRESHOLD

from util.database.database import database
from util.functions import get_embed_color

from cogs.code.base_converter import convert
from cogs.code.brainf import compile_bf

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

MORSE_CHART = {
    "A": ".-", "B": "-...",
    "C": "-.-.", "D": "-..",
    "E": ".", "F": "..-.",
    "G": "--.", "H": "....",
    "I": "..", "J": ".---",
    "K": "-.-", "L": ".-..",
    "M": "--", "N": "-.",
    "O": "---", "P": ".--.",
    "Q": "--.-", "R": ".-.",
    "S": "...", "T": "-",
    "U": "..-", "V": "...-",
    "W": ".--", "X": "-..-",
    "Y": "-.--", "Z": "--..",
    " ": " ", "  ": "  ",
    "0": "-----", "1": ".----",
    "2": "..---", "3": "...--",
    "4": "....-", "5": ".....",
    "6": "-....", "7": "--...",
    "8": "---..", "9": "----."
}

PSEUDO = 0
CODE = 1
BOOLEAN = 2
BITWISE = 3
OPERATOR_CONVERSIONS = {
    "NOT": {
        "!": CODE,
        "~": BITWISE,
        "-": BOOLEAN,
        "NOT": PSEUDO,
        "not": PSEUDO
    },
    "AND": {
        "&&": CODE,
        "&": BITWISE,
        "*": BOOLEAN,
        "AND": PSEUDO,
        "and": PSEUDO
    },
    "OR": {
        "||": CODE,
        "|": BITWISE,
        "+": BOOLEAN,
        "OR": PSEUDO,
        "or": PSEUDO
    }
}
OPERATORS = [
    { "NOT ": "not ", "NOT": "not", "NAND": "nand", "XNOR": "xnor", "NOR": "nor",   "XOR": "xor", "AND": "and",   "OR": "or"  },
    { "NOT ": "!",    "NOT": "!",   "NAND": "!&&",  "XNOR": "!^",   "NOR": "!\|\|", "XOR": "^",   "AND": "&&",    "OR": "\|\|"  },
    { "NOT ": "-",    "NOT": "-",   "NAND": "-*",   "XNOR": "-^",   "NOR": "-+",    "XOR": "^",   "AND": "*",     "OR": "+"   },
    { "NOT ": "~",    "NOT": "~",   "NAND": "~&",   "XNOR": "~^",   "NOR": "~|",    "XOR": "^",   "AND": "&",     "OR": "|"   }
]

LOGIC_TRUTH_TABLE_API_CALL = "https://api.fellowhashbrown.com/logic/parse?expression={}&table=true&operator={}"
LOGIC_SIMPLIFY_API_CALL = "https://api.fellowhashbrown.com/logic/parse?expression={}&simplify=true"
LOGIC_RAW_API_CALL = "https://api.fellowhashbrown.com/logic/parse?expression={}&raw=true"
QR_API_CALL = "https://api.qrserver.com/v1/create-qr-code/?size={0}x{0}&data={1}"
WOLFRAM_ALPHA_API_CALL = "https://api.wolframalpha.com/v2/query?input={}&appid={}&includepodid=LogicCircuit&output=json"
WOLFRAM_ALPHA_ICON = "https://cdn.iconscout.com/icon/free/png-512/wolfram-alpha-2-569293.png"

JUDGE_POST_API_CALL = "https://judge0.p.rapidapi.com/submissions/"
JUDGE_GET_API_CALL = "https://judge0.p.rapidapi.com/submissions/{}?fields=stdout,stderr,time,status&base64_encoded=true"
JUDGE_GET_LANGUAGES_API_CALL = "https://judge0.p.rapidapi.com/languages"

LANGUAGES = {
    "assembly": {
        "name": "Assembly (NASM 2.14.02)",
        "id": 45,
        "code_black": "assembly"
    },
    "bash": {
        "name": "Bash (5.0.0)",
        "id": 46,
        "code_block": "bash"
    },
    "basic": {
        "name": "Basic (FBC 1.07.1)",
        "id": 47,
        "code_block": "basic"
    },
    "c": {
        "name": "C (GCC 9.2.0)",
        "id": 50,
        "code_block": "c"
    },
    "c++": {
        "name": "C++ (GCC 9.2.0)",
        "id": 54,
        "code_block": "c"
    },
    "c#": {
        "name": "C# (mono 6.6.0.161)",
        "id": 51,
        "code_block": "c"
    },
    "go": {
        "name": "Go (1.13.5)",
        "id": 60,
        "code_block": "go"
    },
    "fortran": {
        "name": "Fortran (GFortran 9.2.0)",
        "id": 59,
        "code_block": "fortran"
    },
    "haskell": {
        "name": "Haskell (GHC 8.8.1)",
        "id": 61,
        "code_block": "haskell"
    },
    "java": {
        "name": "Java (OpenJDK 13.0.1)",
        "id": 62,
        "code_block": "java"
    },
    "javascript": {
        "name": "JavaScript (nodejs 12.14.0)",
        "id": 63,
        "code_block": "javascript"
    },
    "pascal": {
        "name": "Pascal (FPC 3.0.4)",
        "id": 67,
        "code_block": ""
    },
    "php": {
        "name": "PHP (7.4.1)",
        "id": 68,
        "code_block": "php"
    },
    "prolog": {
        "name": "Prolog (GNU Prolog 1.4.5)",
        "id": 69,
        "code_block": ""
    },
    "python": {
        "name": "Python (3.8.1)",
        "id": 71,
        "code_block": "python"
    },
    "ruby": {
        "name": "Ruby (2.7.0)",
        "id": 72,
        "code_block": "ruby"
    },
    "rust": {
        "name": "Rust (1.40.0)",
        "id": 73,
        "code_block": "rust"
    }
}

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class Code(Cog, name = "code"):
    """All things having to do with coding go here"""
    def __init__(self, bot):
        self.bot = bot

        # Retrieve the most updated ID from each language
        languages = get(
            JUDGE_GET_LANGUAGES_API_CALL,
            headers = {
                "x-rapidapi-host": "judge0.p.rapidapi.com",
                "x-rapidapi-key": environ["RAPID_API_KEY"]
            }
        )
        languages = languages.json()
        for lang in languages:
            lang_id, lang_name = lang["id"], lang["name"]
            if lang_name.find("(") != -1:
                lang_short = lang_name[:lang_name.find("(") - 1]
            else:
                lang_short = lang_name
            if lang_short in LANGUAGES and LANGUAGES[lang_short]["id"] < lang_id:
                LANGUAGES[lang_short].update(
                    name = lang_name,
                    id = lang_id
                )
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @command(
        name = "brainf", aliases=["bf"],
        description = "Compiles and outputs brainf*** code. There is a timeout after 10 seconds so beware",
        cog_name = "code"
    )
    async def brainf(self, ctx, *, code=None):
        """Allows the user to compile and get output from 
        brainfuck code

        :param ctx: The context of where the message was sent
        :param code: The brainfuck code to execute"
        """

        # Check if there is no code given
        if code is None:
            await ctx.send(embed = get_error_message(
                "There was no brainf\*\*\* code supplied :("
            ))
        else:

            # Timeout after 5 seconds
            try:
                result = await wait_for(loop.run_in_executor(
                    None, compile_bf, code, 
                ), timeout = 10.0)
                await ctx.send(
                    embed = Embed(
                        title = "Brainf*** Output",
                        description = f"```\n{result}\n```" if len(result) > 0 else "There was no output",
                        colour = await get_embed_color(ctx.author)
                    )
                )
            except TimeoutError:
                await ctx.send(embed = get_error_message(
                    "That brainfuck code took a little too long to compile :("
                ))

    @group(
        name = "convert",
        description = "Let's you convert numbers from one base to another.",
        cog_name = "code"
    )
    async def convert(self, ctx, start_base=None, end_base=None, value=None):
        """Allows the user to convert numbers from one base to another

        :param ctx: The context of where the message was sent
        :param start_base: The base to convert the value from
        :param end_base: The base to convert the value to
        :param value: The value to convert
        """
        
        # Check if the start base and end bases are valid
        try:
            start_base = int(start_base)
            end_base = int(end_base)
            if start_base < 2 or start_base > 62 or end_base < 2 or end_base > 62:
                raise IndexError()
            
            # The bases are valid
            # Try to convert the number, if the conversion comes out as None
            #   the start base was invalid for the start value
            result = convert(value, start_base, end_base)
            if result:
                embed = Embed(
                    title = "Conversion",
                    description = "`{} base {}` -> `{} base {}`".format(
                        value, start_base,
                        result, end_base
                    ),
                    colour = await get_embed_color(ctx.author)
                )
            
            # The result was None, the start value was invalid for the start base
            else:
                embed = get_error_message("The value you gave was an invalid number in the start base you gave.")
            
        except:
            embed = get_error_message("Start base and end base must be a number between 2 and 62.")
        
        await ctx.send(embed = embed)
    
    @group(
        name = "textTo",
        description = "Converts text to some encoding options",
        cog_name = "code"
    )
    async def text_to(self, ctx):
        """Allows the user to convert text to other encodings

        :param ctx: The context of where the message was sent
        """
        if not ctx.invoked_subcommand:
            await ctx.send(
                embed = get_error_message(
                    "You must specify the type of conversion you want to do.\nTry running `{}help textTo`".format(
                        await database.guilds.get_prefix(ctx.guild) if ctx.guild else ""
                    )
                )
            )
    
    @text_to.group(
        name = "decimal",
        aliases = ["ascii"],
        description = "Lets you encode or decode text into decimal values",
        cog_name = "code"
    )
    async def text_to_decimal(self, ctx):
        """Allows the user to convert text into decimal values

        :param ctx: The context of where the message was sent
        """
        if not ctx.invoked_subcommand:
            await ctx.send(
                embed = get_error_message(
                    "You must specify if you want to encode or decode text.\nTry running `{}help textTo decimal`".format(
                        await database.guilds.get_prefix(ctx.guild) if ctx.guild else ""
                    )
                )
            )
    
    @text_to_decimal.command(
        name = "encode",
        aliases = ["enc", "e"],
        description = "Encodes text into decimal values using ASCII values",
        cog_name = "code"
    )
    async def text_to_decimal_encode(self, ctx, *, text=None):
        """Allows the user to convert text to its ASCII equivalent

        :param ctx: The context of where the message was sent
        :param text: The text to convert
        """

        # Check if there is no text given
        if text is None:
            embed = get_error_message("You must specify the text to encode!")
        
        # There is text given
        else:
            embed = Embed(
                title = "Text to Decimal",
                description = "_ _",
                colour = await get_embed_color(ctx.author)
            ).add_field(
                name = "Text",
                value = text
            ).add_field(
                name = "Decimal",
                value = " ".join([
                    str(ord(char))
                    for char in text
                ]),
                inline = False
            )

        await ctx.send(embed = embed)
    
    @text_to_decimal.command(
        name = "decode",
        aliases = ["dec", "d"],
        description = "Decodes decimal values into text using ASCII values",
        cog_name = "code"
    )
    async def text_to_decimal_decode(self, ctx, *, text=None):
        """Allows the user to convert ASCII values into text

        :param ctx: The context of where the message was sent
        :param text: The text to convert
        """

        # Check if there is no text given
        if text is None:
            embed = get_error_message("You must specify the text to decode!")
        
        # There is text given
        else:

            # Split the text by spaces and check if there are any values that exceed 255
            text_split = text.split()
            valid = True
            for i in range(len(text_split)):
                value = text_split[i]
                try:
                    value = int(value)
                    if value > 255:
                        raise
                    text_split[i] = value # If this line is reached, the value is valid
                except:
                    valid = False

            # The numbers are valid as a whole
            if valid:
                embed = Embed(
                    title = "Decimal to Text",
                    description = "_ _",
                    colour = await get_embed_color(ctx.author)
                ).add_field(
                    name = "Decimal",
                    value = text
                ).add_field(
                    name = "Text",
                    value = "".join([
                        chr(char)
                        for char in text_split
                    ]),
                    inline = False
                )
            
            # One of the values was not valid
            else:
                embed = get_error_message("One of the decimal values was either >255 or was not a valid decimal value.")

        await ctx.send(embed = embed)
    
    @text_to.group(
        name = "base64",
        aliases = ["b64"],
        description = "Let's you encode or decode text in Base64 encoding.",
        cog_name = "code"
    )
    async def base_64(self, ctx):
        """Allows the user to convert text into Base-64

        :param ctx: The context of where the message was sent
        """
        if not ctx.invoked_subcommand:
            await ctx.send(
                embed = get_error_message(
                    "You must specify if you want to encode or decode text.\nTry running `{}help textTo base64`".format(
                        await database.guilds.get_prefix(ctx.guild) if ctx.guild else ""
                    )
                )
            )
    
    @base_64.command(
        name = "encode",
        aliases = ["enc", "e"],
        description = "Encode regular text into Base64.",
        cog_name = "code"
    )
    async def base_64_encode(self, ctx, *, text: str=None):
        """Allows the user to convert text into Base-64

        :param ctx: The context of where the message was sent
        :param text: The text to convert
        """
        
        # Check if no text is given
        if not text:
            embed = get_error_message("You need to specify the text you want to encode.")
        
        # The text is given
        else:
            embed = Embed(
                title = "Encoded to Base64",
                description = b64encode(text.encode()).decode(),
                colour = await get_embed_color(ctx.author)
            )
        
        await ctx.send(embed = embed)
    
    @base_64.command(
        name = "decode",
        aliases = ["dec", "d"],
        description = "Decode Base64 text into regular text.",
        cog_name = "code"
    )
    async def base_64_decode(self, ctx, *, text: str=None):
        """Allows the user to convert text from Base-64

        :param ctx: The context of where the message was sent
        :param text: The text to convert
        """
        
        # Check if no text is given
        if not text:
            embed = get_error_message("You need to specify the text you want to encode.")
        
        # The text is given
        else:

            # Try to decode the text
            try:
                embed = Embed(
                    title = "Encoded to Base64",
                    description = b64decode(text.encode()).decode(),
                    colour = await get_embed_color(ctx.author)
                )
            except:
                embed = get_error_message("The given text was not properly formatted in Base64")
        
        await ctx.send(embed = embed)
    
    @text_to.group(
        name = "morse",
        description = "Shows you a conversion chart for Morse code or lets you encode/decode text and Morse code.",
        cog_name = "code"
    )
    async def text_to_morse(self, ctx):
        """Allows the user to convert text into Morse

        :param ctx: The context of where the message was sent
        """
        if not ctx.invoked_subcommand:

            # Find the longest conversion on the left side in order to
            #   left-justify it so the conversions on the right side
            #   are all placed similarly
            longest = 0
            count = 1
            for conversion in MORSE_CHART:

                # If count is odd at this point, this current conversion
                #   is on the left side and the length of the text must 
                #   be remembered if it was the longest one
                if count % 2 != 0:
                    text = "`{} -> {}`".format(
                        conversion, MORSE_CHART[conversion]
                    )
                    if len(text) > longest:
                        longest = len(text)
                count += 1
            
            # Iterate through the conversions again, adding the conversions
            #   in two columns and adding the newline after every other conversion
            #   that's on the right side
            count = 1
            chart = ""
            for conversion in MORSE_CHART:
                text = "{} {} {}".format(
                    conversion, 
                    "->" if len(conversion.strip()) > 0 else " ",
                    MORSE_CHART[conversion]
                )

                # Left justify the left text only
                if count % 2 != 0:
                    chart += text.ljust(longest, " ") + " "
                else:
                    chart += text + "\n"
                count += 1
            
            await ctx.send(
                embed = Embed(
                    title = "Conversion Chart",
                    description = "`{}`".format(chart),
                    colour = await get_embed_color(ctx.author)
                )
            )
    
    @text_to_morse.command(
        name = "encode",
        aliases = ["enc", "e"],
        description = "Encode regular text into Morse code.",
        cog_name = "code"
    )
    async def text_to_morse_encode(self, ctx, *, text: str=None):
        """Allows the user to convert text into Morse

        :param ctx: The context of where the message was sent
        :param text: The text to convert
        """

        # Call the Morse API
        result = await loop.run_in_executor(None,
            get,
            "https://fellowhashbrown.com/api/morse/encode?text={}".format(
                text
            )
        )
        result = result.json()
        
        # Check if the encoding was a success
        if result["success"]:
            embed = Embed(
                title = "Encoded Text",
                description = "`{}`".format(result["value"]),
                colour = await get_embed_color(ctx.author)
            )
        
        else:
            embed = get_error_message(result["error"])
    
        await ctx.send(embed = embed)
    
    @text_to_morse.command(
        name = "decode",
        aliases = ["dec", "d"],
        description = "Decode Morse code into regular text.",
        cog_name = "code"
    )
    async def text_to_morse_decode(self, ctx, *, text: str=None):
        """Allows the user to convert Morse into text

        :param ctx: The context of where the message was sent
        :param text: The text to convert
        """
        
        # Call the Morse API
        result = await loop.run_in_executor(None,
            get,
            "https://fellowhashbrown.com/api/morse/decode?text={}".format(
                text
            )
        )
        result = result.json()
        
        # Check if the encoding was a success
        if result["success"]:
            embed = Embed(
                title = "Decoded Text",
                description = "`{}`".format(result["value"]),
                colour = await get_embed_color(ctx.author)
            )
        
        else:
            embed = get_error_message(result["error"])
    
        await ctx.send(embed = embed)
    
    @text_to.group(
        name = "binary",
        aliases = ["bin"],
        description = "Lets you encode/decode text into binary.",
        cog_name = "code"
    )
    async def text_to_binary(self, ctx):
        """Allows the user to convert text into binary numbers

        :param ctx: The context of where the message was sent
        """
        if not ctx.invoked_subcommand:
            await ctx.send(
                embed = get_error_message(
                    "You must specify whether you want to encode or decode text! Try `{}help textTo binary`".format(
                        await database.guilds.get_prefix(ctx.guild) if ctx.guild else ""
                    )
                )
            )
    
    @text_to_binary.command(
        name = "encode",
        aliases = ["enc", "e"],
        description = "Encodes text into binary using ASCII values",
        cog_name = "code"
    )
    async def text_to_binary_encode(self, ctx, *, text: str=None):
        """Allows the user to convert text into binary

        :param ctx: The context of where the message was sent
        :param text: The text to convert
        """

        # Check if there is no text given
        if text is None:
            embed = get_error_message("You must specify the text to encode!")
        
        # There is text given
        else:
            embed = Embed(
                title = "Text to Binary",
                description = "_ _",
                colour = await get_embed_color(ctx.author)
            ).add_field(
                name = "Text",
                value = text
            ).add_field(
                name = "Binary",
                value = " ".join([
                    bin(ord(char))[2:].rjust(8, "0")
                    for char in text
                ]),
                inline = False
            )

        await ctx.send(embed = embed)
    
    @text_to_binary.command(
        name = "decode",
        aliases = ["dec", "d"],
        description = "Decodes binary into text using ASCII values",
        cog_name = "code"
    )
    async def text_to_binary_decode(self, ctx, *, text: str=None):
        """Allows the user to convert binary to text

        :param ctx: The context of where the message was sent
        :param text: The text to convert
        """

        # Check if there is no text given
        if text is None:
            embed = get_error_message("You must specify the text to decode!")
        
        # There is text given
        else:

            # Split the text by spaces and check if there are any values that exceed 255 (in decimal)
            text_split = text.split()
            valid = True
            for i in range(len(text_split)):
                value = text_split[i]
                try:
                    value = int(value, 2)
                    if value > 255:
                        raise
                    text_split[i] = value # If this line is reached, the value is valid
                except:
                    valid = False

            # The numbers are valid as a whole
            if valid:
                embed = Embed(
                    title = "Binary to Text",
                    description = "_ _",
                    colour = await get_embed_color(ctx.author)
                ).add_field(
                    name = "Binary",
                    value = text
                ).add_field(
                    name = "Text",
                    value = "".join([
                        chr(char)
                        for char in text_split
                    ]),
                    inline = False
                )
            
            # One of the values was not valid
            else:
                embed = get_error_message("One of the binary values was either >255 or was not a valid binary value.")

        await ctx.send(embed = embed)
    
    @text_to.group(
        name = "octal",
        aliases = ["oct"],
        description = "Lets you encode/decode text into octal.",
        cog_name = "code"
    )
    async def text_to_octal(self, ctx):
        """Allows the user to convert text into octal

        :param ctx: The context of where the message was sent
        """
        if not ctx.invoked_subcommand:
            await ctx.send(
                embed = get_error_message(
                    "You must specify if you want to encode or decode text.\nTry running `{}help textTo octal`".format(
                        await database.guilds.get_prefix(ctx.guild) if ctx.guild else ""
                    )
                )
            )
    
    @text_to_octal.command(
        name = "encode",
        aliases = ["enc", "e"],
        description = "Encodes text into octal using ASCII values",
        cog_name = "code"
    )
    async def text_to_octal_encode(self, ctx, *, text: str=None):
        """Allows the user to convert text into octal

        :param ctx: The context of where the message was sent
        :param text: The text to convert
        """

        # Check if there is no text given
        if text is None:
            embed = get_error_message("You must specify the text to encode!")
        
        # There is text given
        else:
            embed = Embed(
                title = "Text to Octal",
                description = "_ _",
                colour = await get_embed_color(ctx.author)
            ).add_field(
                name = "Text",
                value = text
            ).add_field(
                name = "Octal",
                value = " ".join([
                    oct(ord(char))[2:].rjust(3, "0")
                    for char in text
                ]),
                inline = False
            )

        await ctx.send(embed = embed)
    
    @text_to_octal.command(
        name = "decode",
        aliases = ["dec", "d"],
        description = "Decodes octal into text using ASCII values",
        cog_name = "code"
    )
    async def text_to_octal_decode(self, ctx, *, text: str=None):
        """Allows the user to convert octal into text

        :param ctx: The context of where the message was sent
        :param text: The text to convert
        """

        # Check if there is no text given
        if text is None:
            embed = get_error_message("You must specify the text to decode!")
        
        # There is text given
        else:

            # Split the text by spaces and check if there are any values that exceed 255 (in decimal)
            text_split = text.split()
            valid = True
            for i in range(len(text_split)):
                value = text_split[i]
                try:
                    value = int(value, 8)
                    if value > 255:
                        raise
                    text_split[i] = value # If this line is reached, the value is valid
                except:
                    valid = False

            # The numbers are valid as a whole
            if valid:
                embed = Embed(
                    title = "Octal to Text",
                    description = "_ _",
                    colour = await get_embed_color(ctx.author)
                ).add_field(
                    name = "Octal",
                    value = text
                ).add_field(
                    name = "Text",
                    value = "".join([
                        chr(char)
                        for char in text_split
                    ]),
                    inline = False
                )
            
            # One of the values was not valid
            else:
                embed = get_error_message("One of the octal values was either >255 or was not a valid octal value.")

        await ctx.send(embed = embed)

    @text_to.group(
        name = "hex",
        aliases = ["hexadecimal", "h"],
        description = "Lets you encode/decode text into hexadecimal",
        cog_name = "code"
    )
    async def text_to_hex(self, ctx):
        """Allows the user to convert text into hex

        :param ctx: The context of where the message was sent
        """
        if not ctx.invoked_subcommand:
            await ctx.send(
                embed = get_error_message(
                    "You must specify if you want to encode or decode text.\nTry running `{}help textTo hex`".format(
                        await database.guilds.get_prefix(ctx.guild) if ctx.guild else ""
                    )
                )
            )
    
    @text_to_hex.command(
        name = "encode",
        aliases = ["enc", "e"],
        description = "Encodes text into hex using ASCII values",
        cog_name = "code"
    )
    async def text_to_hex_encode(self, ctx, *, text: str=None):
        """Allows the user to convert text into hex

        :param ctx: The context of where the message was sent
        :param text: The text to convert
        """

        # Check if there is no text given
        if text is None:
            embed = get_error_message("You must specify the text to encode!")
        
        # There is text given
        else:
            embed = Embed(
                title = "Text to Hex",
                description = "_ _",
                colour = await get_embed_color(ctx.author)
            ).add_field(
                name = "Text",
                value = text
            ).add_field(
                name = "Hex",
                value = " ".join([
                    hex(ord(char))[2:].rjust(2, "0")
                    for char in text
                ]),
                inline = False
            )

        await ctx.send(embed = embed)
    
    @text_to_hex.command(
        name = "decode",
        aliases = ["dec", "d"],
        description = "Decodes hex into text using ASCII values",
        cog_name = "code"
    )
    async def text_to_hex_decode(self, ctx, *, text: str= None):
        """Allows the user to convert hex into text

        :param ctx: The context of where the message was sent
        :param text: The text to convert
        """

        # Check if there is no text given
        if text is None:
            embed = get_error_message("You must specify the text to decode!")
        
        # There is text given
        else:

            # Split the text by spaces and check if there are any values that exceed 255 (in decimal)
            text_split = text.split()
            valid = True
            for i in range(len(text_split)):
                value = text_split[i]
                try:
                    value = int(value, 16)
                    if value > 255:
                        raise
                    text_split[i] = value # If this line is reached, the value is valid
                except:
                    valid = False

            # The numbers are valid as a whole
            if valid:
                embed = Embed(
                    title = "Hex to Text",
                    description = "_ _",
                    colour = await get_embed_color(ctx.author)
                ).add_field(
                    name = "Hex",
                    value = text
                ).add_field(
                    name = "Text",
                    value = "".join([
                        chr(char)
                        for char in text_split
                    ]),
                    inline = False
                )
            
            # One of the values was not valid
            else:
                embed = get_error_message("One of the hex values was either >255 or was not a valid hex value.")

        await ctx.send(embed = embed)
    
    @command(
        name = "qrCode",
        aliases = ["qr"],
        description = "Create a QR code from given text.",
        cog_name = "code"
    )
    async def qr_code(self, ctx, *, text: str=None):
        """Allows the user to generate a QR code from text

        :param ctx: The context of where the message was sent
        :param text: The text to create a QR code from
        """
        
        # Check if there is no text
        if not text:
            embed = get_error_message("You must specify text to turn into a QR Code.")
        
        else:

            # The size of the QR code should be equivalent to:
            #   size = 10(length / 20) + 200
            size = 10 * (len(text) // 20) + 200

            embed = Embed(
                title = " ",
                description = " ",
                colour = await get_embed_color(ctx.author)
            ).set_image(
                url = QR_API_CALL.format(size, quote(text))
            )
        
        await ctx.send(embed = embed)
    
    @command(
        name = "logic",
        aliases = ["boolean"],
        description = "Allows you to get a truth table for a logical expression and the expression simplified.",
        cog_name = "code"
    )
    async def logic(self, ctx, *, expression: str=None):
        """Allows the user retrieve a truth table from a logical expression

        :param ctx: The context of where the message was sent
        :param expression: The text to convert
        """

        # Check if no expression was given
        if not expression:
            await ctx.send(
                embed = get_error_message("You must specify the `expression` to parse")
            )
        
        # There was an expression given
        else:

            # Find the first operator that shows up and set the operator type
            operator_type = PSEUDO
            for char in expression:
                if char in OPERATOR_CONVERSIONS["NOT"]:
                    operator_type = OPERATOR_CONVERSIONS["NOT"][char]
                    break
                elif char in OPERATOR_CONVERSIONS["AND"]:
                    operator_type = OPERATOR_CONVERSIONS["AND"][char]
                    break
                elif char in OPERATOR_CONVERSIONS["OR"]:
                    operator_type = OPERATOR_CONVERSIONS["OR"][char]
                    break

            # Call the Logic api
            response = await loop.run_in_executor(None,
                get, LOGIC_TRUTH_TABLE_API_CALL.format(
                    quote(expression),
                    operator_type
                )
            )
            truth_table = response.json()

            # Simplify the expression
            response = await loop.run_in_executor(None,
                get, LOGIC_SIMPLIFY_API_CALL.format(quote(expression))
            )
            simplification = response.json()

            # Check if there was an error in either response
            if not truth_table["success"]:
                await ctx.send(
                    embed = get_error_message(truth_table["error"])
                )
            elif not simplification["success"]:
                await ctx.send(
                    embed = get_error_message(simplification["error"])
                )
            
            # There was no error
            else:

                # Create the embed for the expression
                truth_table = truth_table["value"]
                table = "```\n{}\n```".format("\n".join(truth_table))
                for operator in OPERATORS[operator_type]:
                    table = table.replace(operator, OPERATORS[operator_type][operator])
                    
                    simplification["value"]["simplified"] = simplification["value"]["simplified"].replace(
                        operator, OPERATORS[operator_type][operator]
                    )

                # Check if the truth table exceeds the size of the description threshold (2000)
                if len(table) >= 2000 or len(truth_table[0]) >= 140:

                    # Send them to the raw webpage
                    await ctx.send(LOGIC_RAW_API_CALL.format(quote(expression)))
                
                # The truth table is within 2000 characters
                else:

                    # Call the WolframAlpha API to get a logical circuit from the expression
                    #   in the original form, the simplified form,
                    #   the nand form, and the nor form
                    original_form, simplified_form, nand_form, nor_form, and_form, or_form = (
                        await loop.run_in_executor(None,
                            get, WOLFRAM_ALPHA_API_CALL.format(
                                simplification["value"]["functional"],
                                environ["WOLFRAM_ALPHA_API_KEY"]
                            )
                        ),
                        await loop.run_in_executor(None,
                            get, WOLFRAM_ALPHA_API_CALL.format(
                                simplification["value"]["functional_simplified"],
                                environ["WOLFRAM_ALPHA_API_KEY"]
                            )
                        ),
                        await loop.run_in_executor(None,
                            get, WOLFRAM_ALPHA_API_CALL.format(
                                "{} nand form".format(simplification["value"]["functional"]),
                                environ["WOLFRAM_ALPHA_API_KEY"]
                            )
                        ),
                        await loop.run_in_executor(None,
                            get, WOLFRAM_ALPHA_API_CALL.format(
                                "{} NOR form".format(simplification["value"]["functional"]),
                                environ["WOLFRAM_ALPHA_API_KEY"]
                            )
                        ),
                        await loop.run_in_executor(None,
                            get, WOLFRAM_ALPHA_API_CALL.format(
                                "{} AND form".format(simplification["value"]["functional"]),
                                environ["WOLFRAM_ALPHA_API_KEY"]
                            )
                        ),
                        await loop.run_in_executor(None,
                            get, WOLFRAM_ALPHA_API_CALL.format(
                                "{} OR form".format(simplification["value"]["functional"]),
                                environ["WOLFRAM_ALPHA_API_KEY"]
                            )
                        )
                    )
                    original_form = original_form.json()
                    simplified_form = simplified_form.json()
                    nand_form = nand_form.json()
                    nor_form = nor_form.json()
                    and_form = and_form.json()
                    or_form = or_form.json()

                    # Get the images for the Original, Simplified, NAND, and NOR forms
                    #   if they exist
                    if "pods" in original_form["queryresult"]: original_form = original_form["queryresult"]["pods"][0]["subpods"][0]["img"]["src"]
                    else: original_form = None

                    if "pods" in simplified_form["queryresult"]: simplified_form = simplified_form["queryresult"]["pods"][0]["subpods"][0]["img"]["src"]
                    else: simplified_form = None

                    if "pods" in nand_form["queryresult"]: nand_form = nand_form["queryresult"]["pods"][0]["subpods"][0]["img"]["src"]
                    else: nand_form = None

                    if "pods" in nor_form["queryresult"]: nor_form = nor_form["queryresult"]["pods"][0]["subpods"][0]["img"]["src"]
                    else: nor_form = None

                    if "pods" in and_form["queryresult"]: and_form = and_form["queryresult"]["pods"][0]["subpods"][0]["img"]["src"]
                    else: nand_form = None

                    if "pods" in or_form["queryresult"]: or_form = or_form["queryresult"]["pods"][0]["subpods"][0]["img"]["src"]
                    else: or_form = None

                    # Combine the images into one using PIL and
                    #   and create a File object to send as a separate message
                    sources = [original_form, simplified_form, nand_form, nor_form, and_form, or_form]
                    images = []
                    for image in sources:
                        if image is not None:
                            img = await loop.run_in_executor(None,
                                get, image
                            )
                            image = Image.open(BytesIO(img.content))
                            images.append(image)
                    widths, heights = zip(*(image.size for image in images))
                    new_width = sum(widths)
                    new_height = max(heights)
                    new_image = Image.new("RGB", (new_width + len(images) - 1, new_height))
                    x_offset = 0
                    for image in images:
                        new_image.paste(image, (x_offset, 
                            (new_height - image.size[1]) // 2
                        ))
                        x_offset += image.size[0] + 1
                    
                    # Compress the image into PNG
                    image = BytesIO()
                    new_image.save(image, format = "png")
                    image = image.getvalue()

                    # Setup the Embed
                    embed = Embed(
                        title = "Logical Expression",
                        description = table,
                        colour = await get_embed_color(ctx.author)
                    ).add_field(
                        name = "Simplified",
                        value = simplification["value"]["simplified"]
                    ).add_field(
                        name = "Other Circuits",
                        value = "From left to right: `{}`".format(
                            ", ".join(
                                ["Original", "Simplified", "NAND", "NOR", "AND", "OR"][i]
                                for i in range(len(sources))
                                if sources[i] is not None
                            )
                        ),
                        inline = False
                    ).set_footer(
                        text = "Logic Circuits from Wolfram|Alpha",
                        icon_url = WOLFRAM_ALPHA_ICON
                    )
                    await ctx.send(embed = embed)
                    await ctx.send(file = File(BytesIO(image), filename = "circuits.png"))
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    @group(
        name = "execute",
        aliases = ["exec", "evaluate", "eval"],
        description = "Let's you run code from a slew of languages.",
        cog_name = "code"
    )
    async def execute(self, ctx):
        """Allows the user to run code from different languages

        :param ctx: The context of where the message was sent
        """
        if not ctx.invoked_subcommand:
            await ctx.send(
                embed = get_error_message(
                    "You need to specify the language you want to execute in.\nRun `{}help execute` for a list of those languages.".format(
                        await database.guilds.get_prefix(ctx.guild) if ctx.guild else ""
                    )
                )
            )
    
    @execute.command(
        name = "bash",
        description = "Run code using the {} language.".format(LANGUAGES["bash"]["name"]),
        cog_name = "code"
    )
    async def execute_bash(self, ctx, *, code: str=None):
        """Allows the user to execute Bash code

        :param ctx: The context of where the message was sent
        :param code: The code to execute
        """
        await self.execute_code(ctx, code, language = "bash")
    
    @execute.command(
        name = "basic",
        description = "Run code using the {} language.".format(LANGUAGES["basic"]["name"]),
        cog_name = "code"
    )
    async def execute_basic(self, ctx, *, code: str=None):
        """Allows the user to execute BASIC code

        :param ctx: The context of where the message was sent
        :param code: The code to execute
        """
        await self.execute_code(ctx, code, language = "basic")
    
    @execute.command(
        name = "c",
        description = "Run code using the {} language.".format(LANGUAGES["c"]["name"]),
        cog_name = "code"
    )
    async def execute_c(self, ctx, *, code: str=None):
        """Allows the user to execute C code

        :param ctx: The context of where the message was sent
        :param code: The code to execute
        """
        await self.execute_code(ctx, code, language = "c")
    
    @execute.command(
        name = "c++",
        description = "Run code using the {} language.".format(LANGUAGES["c++"]["name"]),
        cog_name = "code"
    )
    async def execute_cpp(self, ctx, *, code: str=None):
        """Allows the user to execute C++ code

        :param ctx: The context of where the message was sent
        :param code: The code to execute
        """
        await self.execute_code(ctx, code, language = "c++")
    
    @execute.command(
        name = "C#",
        description = "Run code using the {} language.".format(LANGUAGES["c#"]["name"]),
        cog_name = "code"
    )
    async def execute_csharp(self, ctx, *, code: str=None):
        """Allows the user to execute C# code

        :param ctx: The context of where the message was sent
        :param code: The code to execute
        """
        await self.execute_code(ctx, code, language = "c#")
    
    @execute.command(
        name = "go",
        description = "Run code using the {} language.".format(LANGUAGES["go"]["name"]),
        cog_name = "code"
    )
    async def execute_go(self, ctx, *, code: str=None):
        """Allows the user to execute Go code

        :param ctx: The context of where the message was sent
        :param code: The code to execute
        """
        await self.execute_code(ctx, code, language = "go")
    
    @execute.command(
        name = "haskell",
        description = "Run code using the {} language.".format(LANGUAGES["haskell"]["name"]),
        cog_name = "code"
    )
    async def execute_haskell(self, ctx, *, code: str=None):
        """Allows the user to execute Haskell code

        :param ctx: The context of where the message was sent
        :param code: The code to execute
        """
        await self.execute_code(ctx, code, language = "haskell")
    
    @execute.command(
        name = "fortran",
        description = "Run code using the {} language.".format(LANGUAGES["fortran"]["name"]),
        cog_name = "code"
    )
    async def execute_fortran(self, ctx, *, code: str=None):
        """Allows the user to execute Fortran code

        :param ctx: The context of where the message was sent
        :param code: The code to execute
        """
        await self.execute_code(ctx, code, language = "fortran")
    
    @execute.command(
        name = "java",
        description = "Run code using the {} language.".format(LANGUAGES["java"]["name"]),
        cog_name = "code"
    )
    async def execute_java(self, ctx, *, code: str=None):
        """Allows the user to execute Java code

        :param ctx: The context of where the message was sent
        :param code: The code to execute
        """
        await self.execute_code(ctx, code, language = "java")
    
    @execute.command(
        name = "javascript",
        aliases = ["js", "nodejs", "node"],
        description = "Run code using the {} language.".format(LANGUAGES["javascript"]["name"]),
        cog_name = "code"
    )
    async def execute_javascript(self, ctx, *, code: str=None):
        """Allows the user to execute JavaScript code

        :param ctx: The context of where the message was sent
        :param code: The code to execute
        """
        await self.execute_code(ctx, code, language = "javascript")
    
    @execute.command(
        name = "pascal",
        description = "Run code using the {} language.".format(LANGUAGES["pascal"]["name"]),
        cog_name = "code"
    )
    async def execute_pascal(self, ctx, *, code: str=None):
        """Allows the user to execute Pascal code

        :param ctx: The context of where the message was sent
        :param code: The code to execute
        """
        await self.execute_code(ctx, code, language = "pascal")
    
    @execute.command(
        name = "php",
        description = "Run code using the {} language.".format(LANGUAGES["php"]["name"]),
        cog_name = "code"
    )
    async def execute_php(self, ctx, *, code: str=None):
        """Allows the user to execute PHP code

        :param ctx: The context of where the message was sent
        :param code: The code to execute
        """
        await self.execute_code(ctx, code, language = "php")
    
    @execute.command(
        name = "prolog",
        description = "Run code using the {} language.".format(LANGUAGES["prolog"]["name"]),
        cog_name = "code"
    )
    async def execute_prolog(self, ctx, *, code: str=None):
        """Allows the user to execute Prolog code

        :param ctx: The context of where the message was sent
        :param code: The code to execute
        """
        await self.execute_code(ctx, code, language = "prolog")
    
    @execute.command(
        name = "python",
        description = "Run code using the {} language.".format(LANGUAGES["python"]["name"]),
        cog_name = "code"
    )
    async def execute_python(self, ctx, *, code: str=None):
        """Allows the user to execute Python code

        :param ctx: The context of where the message was sent
        :param code: The code to execute
        """
        await self.execute_code(ctx, code, language = "python")
    
    @execute.command(
        name = "ruby",
        description = "Run code using the {} language.".format(LANGUAGES["ruby"]["name"]),
        cog_name = "code"
    )
    async def execute_ruby(self, ctx, *, code: str=None):
        """Allows the user to execute Ruby code

        :param ctx: The context of where the message was sent
        :param code: The code to execute
        """
        await self.execute_code(ctx, code, language = "ruby")
    
    @execute.command(
        name = "rust",
        description = "Run code using the {} language.".format(LANGUAGES["rust"]["name"]),
        cog_name = "code"
    )
    async def execute_rust(self, ctx, *, code: str=None):
        """Allows the user to execute Rust code

        :param ctx: The context of where the message was sent
        :param code: The code to execute
        """
        await self.execute_code(ctx, code, language = "rust")
    
    async def execute_code(self, ctx, code, *, language = None):
        """Executes the specified code in the specified language.

        :param ctx: The context of where the message was sent
        :param code: The code to execute
        :param language: The language to execute the code in
        """

        if code is None:
            await ctx.send(embed = get_error_message(
                f"You need to specify code to run {language} code"
            ))
            return None

        # Get the language ID from the language
        lang_id = LANGUAGES[language]["id"]

        # Separate source code into lines
        #   remove any backticks made from the user in case they used them
        #   to more easily format their code
        code = code.split("\n")
        if code[0].find("`") != -1:
            code = code[1:]
        if code[-1].find("`") != -1:
            code = code[:-1]
        code = "\n".join(code)

        # Call the Judge0 API
        response = await loop.run_in_executor(None,
            partial(
                post,
                JUDGE_POST_API_CALL,
                json = {
                    "source_code": code,
                    "language_id": lang_id,
                    "cpu_time_limit": 10,
                    "cpu_extra_time": 2
                },
                headers = {
                    "Content-Type": "application/json",
                    "accept": "application/json",
                    "x-rapidapi-host": "judge0.p.rapidapi.com",
                    "x-rapidapi-key": environ["RAPID_API_KEY"]
                }
            )
        )
        response = response.json()
        token = response["token"]

        # Call the Judge0 API until the previous submission has finished
        while True:
            response = await loop.run_in_executor(None,
                partial(
                    get,
                    JUDGE_GET_API_CALL.format(token),
                    headers = {
                        "x-rapidapi-host": "judge0.p.rapidapi.com",
                        "x-rapidapi-key": environ["RAPID_API_KEY"]
                    }
                )
            )
            response = response.json()
            print(json.dumps(response), end = "\n\n")
            if "error" in response:
                await ctx.send(embed=get_error_message(
                    response["error"]
                ))
                return
            if response["status"]["id"] not in [1, 2]: # ID 1 and 2 is in queue and processing the code
                break
        
        # Split up the STDOUT and STDERR into separate fields
        out = err = None
        if response["stdout"] is not None:
            out = b64decode(response["stdout"]).decode()
        if response["stderr"] is not None:
            err = b64decode(response["stderr"]).decode()

        # Only split if out is not None
        out_threshold = False
        if out != None:
            if len(out) > FIELD_THRESHOLD:
                out_threshold = True
                out = out[:FIELD_THRESHOLD]

        # Only split if err is not None
        err_threshold = False
        if err != None:
            if len(err) > FIELD_THRESHOLD:
                err_threshold = True
                err = err[:FIELD_THRESHOLD]

        # Give all the necessary information about the code compilation
        embed = Embed(
            title = "Compilation Results",
            description = "_ _",
            colour = await get_embed_color(ctx.author)
        ).set_footer(
            text = "Ran in {}s".format(
                response["time"]
            )
        )

        # Add STDOUT field
        embed.add_field(
            name = "STDOUT {}".format(
                "Output Exceeded Limit" if out_threshold else ""
            ),
            value = "```{}\n{}\n```".format(
                LANGUAGES[language]["code_block"],
                out
            ),
            inline = False
        )

        # Add STDERR field
        embed.add_field(
            name = "STDERR {}".format(
                "Output Exceeded Limit" if err_threshold else ""
            ),
            value = "```{}\n{}\n```".format(
                LANGUAGES[language]["code_block"],
                err
            ),
            inline = False
        )
        
        # Send message
        await ctx.send(
            embed = embed
        )
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def setup(bot):
    """Add's this cog to the bot

    :param bot: The bot to add the cog to
    """
    bot.add_cog(Code(bot))