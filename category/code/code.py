import asyncio, base64, discord, os, requests
from discord.ext import commands
from functools import partial

from category import errors
from category.globals import FIELD_THRESHOLD, did_author_vote
from category.globals import get_embed_color, is_on_mobile
from database import loop

from .base_converter import convert

# # # # # # # # # # # # # # # # # # # # # # # # #

CODE_EMBED_COLOR = 0xEC7600

JUDGE_API_CALL = "https://api.judge0.com/submissions?wait=true"
LOGIC_API_CALL = "https://www.fellowhashbrown.com/api/logic?expression={}&table=true"
MORSE_API_CALL = "https://www.fellowhashbrown.com/api/morse/{}?text={}"
QR_API_CALL = "https://api.qrserver.com/v1/create-qr-code/?size={0}x{0}&data={1}"

LANGUAGES = {
    "Bash (4.4)": {
        "shortcuts": ["bash"],
        "id": 1,
        "code_block": "bash"
    },
    "Basic (fbc 1.05.0)": {
        "shortcuts": ["basic"],
        "id": 3,
        "code_block": "basic"
    },
    "C (gcc 7.2.0)": {
        "shortcuts": ["c"],
        "id": 4,
        "code_block": "c"
    },
    "C++ (g++ 7.2.0)": {
        "shortcuts": ["c++"],
        "id": 10,
        "code_block": "c"
    },
    "C# (mono 5.4.0.167)": {
        "shortcuts": ["c#"],
        "id": 16,
        "code_block": "c"
    },
    "Clojure (1.8.0)": {
        "shortcuts": ["clojure"],
        "id": 18,
        "code_block": "clojure"
    },
    "Crystal (0.23.1)": {
        "shortcuts": ["crystal"],
        "id": 19,
        "code_block": "crystal"
    },
    "Elixir (1.5.1)": {
        "shortcuts": ["elixir"],
        "id": 20,
        "code_block": "elixir"
    },
    "Erlang (OTP 20.0)": {
        "shortcuts": ["erlang"],
        "id": 21,
        "code_block": "erlang"
    },
    "Go (1.9)": {
        "shortcuts": ["go"],
        "id": 22,
        "code_block": "go"
    },
    "Haskell (ghc 8.2.1)": {
        "shortcuts": ["haskell"],
        "id": 23,
        "code_block": "haskell"
    },
    "Insect (5.0.0)": {
        "shortcuts": ["insect"],
        "id": 25,
        "code_block": ""
    },
    "Java (OpenJDK 9)": {
        "shortcuts": ["java9"],
        "id": 26,
        "code_block": "java"
    },
    "Java (OpenJDK 8)": {
        "shortcuts": ["java8"],
        "id": 27,
        "code_block": "java"
    },
    "Java (OpenJDK 7)": {
        "shortcuts": ["java7"],
        "id": 28,
        "code_block": "java"
    },
    "JavaScript (nodejs 8.5.0)": {
        "shortcuts": ["javascript", "js", "nodejs", "node"],
        "id": 29,
        "code_block": "javascript"
    },
    "OCaml (4.05.0)": {
        "shortcuts": ["ocaml"],
        "id": 31,
        "code_block": "ocaml"
    },
    "Octave (4.2.0)": {
        "shortcuts": ["octave"],
        "id": 32,
        "code_block": ""
    },
    "Pascal (fpc 3.0.0)": {
        "shortcuts": ["pascal"],
        "id": 33,
        "code_block": ""
    },
    "Python (3.6.0)": {
        "shortcuts": ["python", "python3"],
        "id": 34,
        "code_block": "python"
    },
    "Python (2.7.9)": {
        "shortcuts": ["python2"],
        "id": 36,
        "code_block": "python"
    },
    "Ruby (2.4.0)": {
        "shortcuts": ["ruby"],
        "id": 38,
        "code_block": "ruby"
    },
    "Rust (1.20.0)" :{
        "shortcuts": ["rust"],
        "id": 42,
        "code_block": "rust"
    }
}

SHORTCUTS = [
    shortcut
    for language in LANGUAGES
    for shortcut in LANGUAGES[language]["shortcuts"]
]

# # # # # # # # # # # # # # # # # # # # # # # # #
# Extension
# # # # # # # # # # # # # # # # # # # # # # # # #

class Code(commands.Cog, name = "Code"):
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @commands.command(
        name = "execute",
        aliases = ["exec", "evaluate", "eval"],
        description = "Allows you to run code from a slew of languages. There are no parameters. You just run the command.",
        cog_name = "Code"
    )
    async def execute(self, ctx):

        # Check if author voted first
        if await did_author_vote(ctx.author.id):

            # Ask which language the user wants to write code for
            fields = []
            field_text = ""
            for language in LANGUAGES:

                language = "{} (`{}`)\n".format(
                    language,
                    ", ".join(LANGUAGES[language]["shortcuts"])
                )

                if len(field_text) + len(language) > FIELD_THRESHOLD:
                    fields.append(field_text)
                    field_text = ""
                
                field_text += language
            
            if len(field_text) > 0:
                fields.append(field_text)
            
            # Add fields to embed
            embed = discord.Embed(
                title = "Available Languages",
                description = "Below is a list of available languages and their shortcuts.",
                colour = await get_embed_color(ctx.author)
            )

            for field in fields:
                embed.add_field(
                    name = "_ _",
                    value = field
                )
            
            # Send message and ask user which language they want to evaluate
            await ctx.send(
                embed = embed
            )

            def check_language(message):
                return message.channel.id == ctx.channel.id and message.author.id == ctx.author.id and message.content.lower() in SHORTCUTS
            
            try:
                message = await self.bot.wait_for("message", check = check_language, timeout = 30)
                language = message.content.lower()
                code_block = ""

                # Get language
                for lang in LANGUAGES:
                    if language in LANGUAGES[lang]["shortcuts"]:
                        language = LANGUAGES[lang]["id"]
                        code_block = LANGUAGES[lang]["code_block"]
                        break
                
                # Tell user to write their source code
                await ctx.send(
                    embed = discord.Embed(
                        title = "Source Code!",
                        description = "Now write your source code! There's a maximum of 10 minutes until it times out.",
                        colour = await get_embed_color(ctx.author)
                    )
                )

                def check_source(message):
                    return message.channel.id == ctx.channel.id and message.author.id == ctx.author.id

                message = await self.bot.wait_for("message", check = check_source, timeout = 600)
                source_code = message.content

                # Separate source code into lines
                # If backticks are found at beginning and end, remove them
                source_code = source_code.split("\n")
                if source_code[0].find("`") != -1:
                    source_code = source_code[1:]
                if source_code[-1].find("`") != -1:
                    source_code = source_code[:-1]
                source_code = "\n".join(source_code)

                # Call judge0 API
                response = await loop.run_in_executor(None,
                    partial(
                        requests.post,
                        JUDGE_API_CALL,
                        json = {
                            "source_code": source_code,
                            "language_id": language,
                            "cpu_time_limit": 10,
                            "cpu_extra_time": 2
                        },
                        headers = {
                            "Content-Type": "application/json"
                        }
                    )
                )
                response = response.json()

                # Split up the stdout and stderr in multiple fields if necessary
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
                embed = discord.Embed(
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
                        code_block,
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
                        code_block,
                        err
                    ),
                    inline = False
                )
                
                # Send message
                await ctx.send(
                    embed = embed
                )

            # User did not choose a language or write source code in time; Don't hang
            except asyncio.TimeoutError:
                await ctx.send(
                    embed = errors.get_error_message(
                        "Oh no! It seems you've timed out."
                    )
                )
        
        # Author did not vote
        else:
            await ctx.send(
                embed = discord.Embed(
                    title = "Vote!",
                    description = "In order to use this command, I ask that you vote real quick!\n{}".format(
                        "https://discordbots.org/bot/535587516816949248/vote"
                    ),
                    colour = await get_embed_color(ctx.author)
                )
            )

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

        # Check if on mobile
        on_mobile = await is_on_mobile(ctx)

        # Check if expression is None; Throw error message
        if expression == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need the `expression` to parse."
                )
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
                await ctx.send(
                    embed = errors.get_error_message(
                        response["error"]
                    )
                )
            
            # No error existed; Get the value
            else:

                truth_table = response["value"]
                content = "```\n{}\n```".format("\n".join(truth_table))

                # Check if on mobile, send a file
                if on_mobile:

                    # Remove backticks (`)
                    content = content.replace("`", "")

                    # Create file and send to author
                    filename = "logic-{}-{}.txt".format(ctx.author.name, ctx.author.discriminator)
                    temp = open(filename, "w")
                    temp.write(content)
                    temp.close()

                    content = "{}, here is a file for you!".format(
                        ctx.author.mention
                    )

                    await ctx.send(
                        content,
                        file = discord.File(filename)
                    )
                    os.remove(filename)
                
                # Check if the content is bigger than 2000
                elif len(content) > 2000 or len(truth_table[0]) >= 140:

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
                
                # Content is good, send it
                else:

                    await ctx.send(
                        content
                    )

# # # # # # # # # # # # # # # # # # # # # # # # #
# Setup
# # # # # # # # # # # # # # # # # # # # # # # # #

def setup(bot):
    bot.add_cog(Code(bot))
