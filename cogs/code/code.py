from base64 import b64encode, b64decode
from discord import Embed
from discord.ext.commands import command, Cog, group
from functools import partial
from os import environ
from requests import get, post
from urllib.parse import quote

from cogs.errors import get_error_message
from cogs.globals import loop, FIELD_THRESHOLD

from util.functions import get_embed_color

from cogs.code.base_converter import convert

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

LOGIC_API_CALL = "https://www.fellowhashbrown.com/api/logic?expression={}&table=true"
LOGIC_SIMPLIFY_API_CALL = "https://www.fellowhashbrown.com/api/logic?expression={}&simplify=true&wolframalpha=true"
LOGIC_RAW_API_CALL = "https://www.fellowhashbrown.com/api/logic?expression={}&raw=true"
QR_API_CALL = "https://api.qrserver.com/v1/create-qr-code/?size={0}x{0}&data={1}"
WOLFRAM_ALPHA_API_CALL = "https://api.wolframalpha.com/v2/query?input={}&appid={}&includepodid=LogicCircuit&output=json"

JUDGE_POST_API_CALL = "https://api.judge0.com/submissions/"
JUDGE_GET_API_CALL = "https://api.judge0.com/submissions/{}?fields=stdout,stderr,time,status"
JUDGE_GET_LANGUAGES_API_CALL = "https://api.judge0.com/languages"

LANGUAGES = {
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
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @command(
        name = "convert",
        description = "Let's you convert numbers from one base to another.",
        cog_name = "code"
    )
    async def convert(self, ctx, start_base : int = None, end_base : int = None, value : str = None):
        
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
        name = "base64",
        aliases = ["b64"],
        description = "Let's you encode or decode text in Base64 encoding.",
        cog_name = "code"
    )
    async def base_64(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send(embed = get_error_message("You must specify if you want to encode or decode text.\nTry running `ob.help base64` for more information."))
    
    @base_64.command(
        name = "encode",
        aliases = ["enc", "e"],
        description = "Encode regular text into Base64.",
        cog_name = "code"
    )
    async def base_64_encode(self, ctx, *, text : str = None):
        
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
    async def base_64_decode(self, ctx, *, text : str = None):
        
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
    
    @group(
        name = "morse",
        description = "Shows you a conversion chart for Morse code.",
        cog_name = "code"
    )
    async def morse(self, ctx):
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
    
    @morse.command(
        name = "encode",
        aliases = ["enc", "e"],
        description = "Encode regular text into Morse code.",
        cog_name = "code"
    )
    async def morse_encode(self, ctx, *, text : str = None):

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
    
    @morse.command(
        name = "decode",
        aliases = ["dec", "d"],
        description = "Decode Morse code into regular text.",
        cog_name = "code"
    )
    async def morse_decode(self, ctx, *, text : str = None):
        
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
    
    @command(
        name = "qrCode",
        aliases = ["qr"],
        description = "Create a QR code from given text.",
        cog_name = "code"
    )
    async def qr_code(self, ctx, *, text : str = None):
        
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
    async def logic(self, ctx, *, expression : str = None):

        # Check if no expression was given
        if not expression:
            await ctx.send(
                embed = get_error_message("You must specify the `expression` to parse")
            )
        
        # There was an expression given
        else:

            # Call the Logic api
            response = await loop.run_in_executor(None,
                get, LOGIC_API_CALL.format(quote(expression))
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

                # Check if the truth table exceeds the size of the description threshold (2000)
                if len(table) >= 2000 or len(truth_table[0]) >= 140:

                    # Send them to the raw webpage
                    await ctx.send(LOGIC_RAW_API_CALL.format(quote(expression)))
                
                # The truth table is within 2000 characters
                else:

                    # Call the WolframAlpha API to get a logical circuit from the expression
                    response = await loop.run_in_executor(None,
                        get, WOLFRAM_ALPHA_API_CALL.format(
                            simplification["wolframalpha"],
                            environ["WOLFRAM_ALPHA_API_KEY"]
                        )
                    )
                    response = response.json()

                    await ctx.send(
                        embed = Embed(
                            title = "Logical Expression",
                            description = table,
                            colour = await get_embed_color(ctx.author)
                        ).add_field(
                            name = "Simplified",
                            value = simplification["value"]
                        ).set_image(
                            url = response["queryresult"]["pods"][0]["subpods"][0]["img"]["src"]
                        ).set_footer(
                            text = "Logic Circuit from WolframAlpha",
                            icon_url = "https://cdn.iconscout.com/icon/free/png-256/wolfram-alpha-2-569293.png"
                        )
                    )
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    @group(
        name = "execute",
        aliases = ["exec", "evaluate", "eval"],
        description = "Let's you run code from a slew of languages.",
        cog_name = "code"
    )
    async def execute(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send(
                embed = get_error_message(
                    "You need to specify the language you want to execute in.\nRun `o.help execute` for a list of those languages."
                )
            )
    
    @execute.command(
        name = "bash",
        description = "Run code using the {} language.".format(LANGUAGES["bash"]["name"]),
        cog_name = "code"
    )
    async def execute_bash(self, ctx, *, code : str = None):
        await self.execute_code(ctx, code, language = "bash")
    
    @execute.command(
        name = "basic",
        description = "Run code using the {} language.".format(LANGUAGES["basic"]["name"]),
        cog_name = "code"
    )
    async def execute_basic(self, ctx, *, code : str = None):
        await self.execute_code(ctx, code, language = "basic")
    
    @execute.command(
        name = "c",
        description = "Run code using the {} language.".format(LANGUAGES["c"]["name"]),
        cog_name = "code"
    )
    async def execute_c(self, ctx, *, code : str = None):
        await self.execute_code(ctx, code, language = "c")
    
    @execute.command(
        name = "c++",
        description = "Run code using the {} language.".format(LANGUAGES["c++"]["name"]),
        cog_name = "code"
    )
    async def execute_cpp(self, ctx, *, code : str = None):
        await self.execute_code(ctx, code, language = "c++")
    
    @execute.command(
        name = "C#",
        description = "Run code using the {} language.".format(LANGUAGES["c#"]["name"]),
        cog_name = "code"
    )
    async def execute_csharp(self, ctx, *, code : str = None):
        await self.execute_code(ctx, code, language = "c#")
    
    @execute.command(
        name = "go",
        description = "Run code using the {} language.".format(LANGUAGES["go"]["name"]),
        cog_name = "code"
    )
    async def execute_go(self, ctx, *, code : str = None):
        await self.execute_code(ctx, code, language = "go")
    
    @execute.command(
        name = "haskell",
        description = "Run code using the {} language.".format(LANGUAGES["haskell"]["name"]),
        cog_name = "code"
    )
    async def execute_haskell(self, ctx, *, code : str = None):
        await self.execute_code(ctx, code, language = "haskell")
    
    @execute.command(
        name = "fortran",
        description = "Run code using the {} language.".format(LANGUAGES["fortran"]["name"]),
        cog_name = "code"
    )
    async def execute_fortran(self, ctx, *, code : str = None):
        await self.execute_code(ctx, code, language = "fortran")
    
    @execute.command(
        name = "java",
        description = "Run code using the {} language.".format(LANGUAGES["java"]["name"]),
        cog_name = "code"
    )
    async def execute_java(self, ctx, *, code : str = None):
        await self.execute_code(ctx, code, language = "java")
    
    @execute.command(
        name = "javascript",
        aliases = ["js", "nodejs", "node"],
        description = "Run code using the {} language.".format(LANGUAGES["javascript"]["name"]),
        cog_name = "code"
    )
    async def execute_javascript(self, ctx, *, code : str = None):
        await self.execute_code(ctx, code, language = "javascript")
    
    @execute.command(
        name = "pascal",
        description = "Run code using the {} language.".format(LANGUAGES["pascal"]["name"]),
        cog_name = "code"
    )
    async def execute_pascal(self, ctx, *, code : str = None):
        await self.execute_code(ctx, code, language = "pascal")
    
    @execute.command(
        name = "php",
        description = "Run code using the {} language.".format(LANGUAGES["php"]["name"]),
        cog_name = "code"
    )
    async def execute_php(self, ctx, *, code : str = None):
        await self.execute_code(ctx, code, language = "php")
    
    @execute.command(
        name = "prolog",
        description = "Run code using the {} language.".format(LANGUAGES["prolog"]["name"]),
        cog_name = "code"
    )
    async def execute_prolog(self, ctx, *, code : str = None):
        await self.execute_code(ctx, code, language = "prolog")
    
    @execute.command(
        name = "python",
        description = "Run code using the {} language.".format(LANGUAGES["python"]["name"]),
        cog_name = "code"
    )
    async def execute_python(self, ctx, *, code : str = None):
        await self.execute_code(ctx, code, language = "python")
    
    @execute.command(
        name = "ruby",
        description = "Run code using the {} language.".format(LANGUAGES["ruby"]["name"]),
        cog_name = "code"
    )
    async def execute_ruby(self, ctx, *, code : str = None):
        await self.execute_code(ctx, code, language = "ruby")
    
    @execute.command(
        name = "rust",
        description = "Run code using the {} language.".format(LANGUAGES["rust"]["name"]),
        cog_name = "code"
    )
    async def execute_rust(self, ctx, *, code : str = None):
        await self.execute_code(ctx, code, language = "rust")
    
    async def execute_code(self, ctx, code, *, language = None):
        """Executes the specified code in the specified language.

        Parameters
        ----------
            code : str
                The code to run
            language : str
                The language to run the code in
        """

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
                    "Content-Type": "application/json"
                }
            )
        )
        response = response.json()
        token = response["token"]

        # Call the Judge0 API until the previous submission has finished
        while True:
            response = await loop.run_in_executor(None,
                get,
                JUDGE_GET_API_CALL.format(token)
            )
            response = response.json()
            if response["status"]["id"] != 2: # ID 2 is processing the code
                break
        
        # Split up the STDOUT and STDERR into separate fields
        out = response["stdout"]
        err = response["stderr"]

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
    bot.add_cog(Code(bot))