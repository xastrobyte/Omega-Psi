from util.code.code import convert
from util.file.database import loop
from util.file.server import Server
from util.file.omegaPsi import OmegaPsi
from util.utils.discordUtils import sendMessage, getErrorMessage
from util.utils.miscUtils import timeout

from supercog import Category, Command
import base64, discord, requests

scrollEmbeds = {}

class Code(Category):
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    MAX_BRAINFUCK_LENGTH = 2 ** 15 # 32736

    QR_API_CALL = "https://api.qrserver.com/v1/create-qr-code/?size={0}x{0}&data={1}"
    MORSE_API_CALL = "https://www.fellowhashbrown.com/api/morse/{}?text={}"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Errors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    BASE_MISMATCH = "BASE_MISMATCH"
    BASE_OUT_OF_RANGE = "BASE_OUT_OF_RANGE"

    INVALID_LANGUAGE = "INVALID_LANGUAGE"
    INVALID_BASE = "INVALID_BASE"
    INVALID_PARAMETER = "INVALID_PARAMETER"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Constructor
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, client):
        super().__init__(
            client, 
            "Code",
            description = "Commands that have to do with coding!",
            embed_color = 0xFFFF00,
            locally_inactive_error = Server.getInactiveError,
            globally_inactive_error = OmegaPsi.getInactiveError,
            locally_active_check = Server.isCommandActive,
            globally_active_check = OmegaPsi.isCommandActive
        )

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Commands
        self._brainfuck = Command(commandDict = {
            "alternatives": ["brainf", "bf"],
            "info": "Runs brainfuck code. Kinda confusing stuff at first glance.",
            "min_parameters": 1,
            "parameters": {
                "code": {
                    "optional": False,
                    "info": "The code to run."
                },
                "parameters": {
                    "optional": True,
                    "info": "The parameters to use in the code."
                }
            },
            "errors": {
                Code.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "The brainfuck command requires at least the brainfuck code."
                    ]
                },
                Code.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "The brainfuck command only needs the code and the parameters. Make sure you remove spaces from both."
                    ]
                }
            },
            "command": self.brainfuck
        })

        self._convert = Command(commandDict = {
            "alternatives": ["convert", "conversion", "baseConversion", "baseConverter"],
            "info": "Converts a number from one base to another base.",
            "min_parameters": 2,
            "max_parameters": 3,
            "parameters": {
                "startBase": {
                    "info": "The base the number starts at.",
                    "optional": True
                },
                "endBase": {
                    "info": "The base the number ends at.",
                    "optional": False
                },
                "number": {
                    "info": "The number to convert.",
                    "optional": False
                }
            },
            "errors": {
                Code.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "You need at least the end base and the number to convert."
                    ]
                },
                Code.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You only need the start base, the end base, and the number."
                    ]
                },
                Code.INVALID_BASE: {
                    "messages": [
                        "A base you entered is not a valid base."
                    ]
                },
                Code.BASE_MISMATCH: {
                    "messages": [
                        "The number you entered does not match the start base."
                    ]
                }
            },
            "command": self.convert
        })

        self._base64 = Command(commandDict = {
            "alternatives": ["base64", "b64"],
            "info": "Encodes or decodes text to base64.",
            "min_parameters": 2,
            "parameters": {
                "conversion": {
                    "info": "Whether to encode/decode text into/from base64.",
                    "optional": False,
                    "accepted_parameters": {
                        "encode": {
                            "alternatives": ["encode", "enc", "e"],
                            "info": "Encode text into base64."
                        },
                        "decode": {
                            "alternatives": ["decode", "dec", "d"],
                            "info": "Decode text from base64."
                        }
                    }
                },
                "text": {
                    "info": "The text to encode or decode.",
                    "optional": False
                }
            },
            "errors": {
                Code.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to encode or decode text, you need the conversion type and the text."
                    ]
                },
                Code.INVALID_PARAMETER: {
                    "messages": [
                        "That is not a valid conversion type."
                    ]
                }
            },
            "command": self.base64
        })

        self._morse = Command(commandDict = {
            "alternatives": ["morse", "m"],
            "info": "Encodes or decodes text to Morse code.",
            "parameters": {
                "conversion": {
                    "info": "Whether to encode/decode text into/from Morse Code.",
                    "optional": False,
                    "accepted": {
                        "encode": {
                            "alternatives": ["encode", "enc", "e"],
                            "info": "Encodes text into Morse Code."
                        },
                        "decode": {
                            "alternatives": ["decode", "dec", "d"],
                            "info": "Decodes text from Morse Code."
                        }
                    }
                },
                "text": {
                    "info": "The text to encode or decode.",
                    "optional": False
                }
            },
            "errors": {
                Code.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to encode or decode text, you need the conversion type and the text."
                    ]
                },
                Code.INVALID_PARAMETER: {
                    "messages": [
                        "That is not a valid conversion type."
                    ]
                }
            },
            "command": self.morse
        })

        self._qrCode = Command(commandDict = {
            "alternatives": ["qrCode", "qr"],
            "info": "Turns text into a QR code.",
            "parameters": {
                "data": {
                    "info": "The data to set for the QR code.",
                    "optional": False
                }
            },
            "errors": {
                Code.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to get the QR code for data, you need to type in the data."
                    ]
                }
            },
            "command": self.qrCode
        })

        self.setCommands([
            self._brainfuck,
            self._convert,
            self._base64,
            self._morse,
            self._qrCode
        ])
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @timeout()
    async def brainfuck(self, message, parameters):
        """Runs brainfuck code and returns the result.\n

        Parameters:
            code: The brainfuck code to run.\n
            parameters: The parameters to insert into the brainfuck code.\n
        """

        # Check for not enough parameters
        if len(parameters) < self._brainfuck.getMinParameters():
            embed = getErrorMessage(self._brainfuck, Code.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._brainfuck.getMaxParameters():
            embed = getErrorMessage(self._brainfuck, Code.TOO_MANY_PARAMETERS)
        
        # There were a proper amount of parameters
        else:

            code = parameters[0]
            if len(parameters) == 2:
                parameters = []

            # Remove all invalid symbols
            validSymbols = "<>+-.,[]"
            newCode = ""
            for char in code:
                if char in validSymbols:
                    newCode += char
            code = newCode

            # Keep track of pointers and data
            data = [0] * Code.MAX_BRAINFUCK_LENGTH
            dataPointer = 0
            paramPointer = 0
            output = ""
            loop = 0

            # Iterate through code
            char = 0
            while char < len(code):

                # char is > (move pointer right)
                if code[char] == ">":
                    dataPointer = 0 if dataPointer == Code.MAX_BRAINFUCK_LENGTH - 1 else dataPointer + 1
                
                # char is < (move pointer left)
                elif code[char] == "<":
                    dataPointer = Code.MAX_BRAINFUCK_LENGTH - 1 if dataPointer == 0 else dataPointer - 1
                
                # char is + (increase value at pointer)
                elif code[char] == "+":
                    data[dataPointer] += 1
                    if data[dataPointer] > 255:
                        data[dataPointer] -= 256
                
                # char is - (decrease value at pointer)
                elif code[char] == "-":
                    data[dataPointer] -= 1
                    if data[dataPointer] < 0:
                        data[dataPointer] += 256
                
                # char is . (add data to output)
                elif code[char] == ".":
                    output += str(chr(data[dataPointer]))
                
                # char is , (add data to input)
                elif code[char] == ",":
                    if paramPointer >= len(parameters):
                        data[dataPointer] = 0
                    else:
                        data[dataPointer] = ord(parameters[paramPointer])
                    paramPointer += 1
                
                # char is [ (open loop)
                elif code[char] == "[":
                    if data[dataPointer] == 0:
                        char += 1
                        while loop > 0 or code[char] != "]":
                            if code[char] == "[":
                                loop += 1
                            if code[char] == "]":
                                loop -= 1
                            char += 1
                
                # char is ] (close loop)
                elif code[char] == "]":
                    if data[dataPointer] != 0:
                        char -= 1
                        while loop > 0 or code[char] != "[":
                            if code[char] == "]":
                                loop += 1
                            if code[char] == "[":
                                loop -= 1
                            char -=1
                        char -= 1
                
                char += 1
            
            # Create and return embed for result
            embed = discord.Embed(
                title = "Result",
                description = output,
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            )
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def convert(self, message, parameters):
        """Converts a number from the start base to the end base.\n

        Parameters:
            startBase: The base to convert from.\n
            endBase: The base to convert to.\n
            number: The number to convert.\n
        """

        # Check for not enough parameters
        if len(parameters) < self._convert.getMinParameters():
            embed = getErrorMessage(self._convert, Code.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._convert.getMaxParameters():
            embed = getErrorMessage(self._convert, Code.TOO_MANY_PARAMETERS)

        # There were the proper amount of parameters
        else:

            startBase = "10"
            endBase = parameters[0]
            number = parameters[1]

            if len(parameters) == 3:
                startBase = parameters[0]
                endBase = parameters[1]
                number = parameters[2]
            
            # Only run if start base and end base are valid
            if startBase.isdigit() and endBase.isdigit():
                startBase = int(startBase)
                endBase = int(endBase)

                if startBase >= 2 and startBase <= 64 and endBase >=2 and endBase <=64:
                    # Try converting number from startBase to base-10
                    # Test to see if number is not zero
                    start = number
                    title = "Base-{} to Base-{}".format(startBase, endBase)
                    description = "`{} --> {}`".format(start, number)

                    # Check if number is not zero; Convert it
                    if number not in ["0", 0]:
                        number = convert(number, startBase, endBase)

                        # Check if number is None; Invalid number for a base
                        if number == None:
                            embed = getErrorMessage(self._convert, Code.BASE_MISMATCH)
                        
                        # Number is not None; Valid base
                        else:

                            # Return number
                            description = "`{} --> {}`".format(start, number)
                    
                            embed = discord.Embed(
                                title = title,
                                description = description,
                                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                            )
                    
                    # Number is zero; Just send that
                    else:

                        embed = discord.Embed(
                            title = title,
                            description = description,
                            colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                        )
                
                # Bases were not within range
                else:
                    embed = getErrorMessage(self._convert, Code.BASE_OUT_OF_RANGE)
            
            # Bases were not numbers
            else:
                embed = getErrorMessage(self._convert, Code.INVALID_BASE)
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def base64(self, message, parameters):
        """Encodes or decodes text to or from base64.\n

        Parameters:
            conversionType: Whether to encode or decode text.\n
            text: The text to encode or decode.\n
        """

        # Check for not enough parameters
        if len(parameters) < self._base64.getMinParameters():
            embed = getErrorMessage(self._base64, Code.NOT_ENOUGH_PARAMETERS)

        # There were enough parameters
        else:
        
            # Conversion type is first parameter; Text is all parameters after
            conversionType = parameters[0]
            text = " ".join(parameters[1:])

            # Conversion is Encode
            if conversionType in self._base64.getAcceptedParameter("conversion", "encode").getAlternatives():
                converted = base64.b64encode(text.encode()).decode()
                encoded = True

                embed = discord.Embed(
                    title = "`{}` {} Base64".format(
                        text if len(text) < 180 else "[text is greater than 200 characters]",
                        "encoded to" if encoded else "decoded from"
                    ),
                    description = converted,
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )
            
            # Conversion is Decode
            elif conversionType in self._base64.getAcceptedParameter("conversion", "decode").getAlternatives():
                converted = base64.b64decode(text.encode()).decode()
                encoded = False

                embed = discord.Embed(
                    title = "`{}` {} Base64".format(
                        text if len(text) < 180 else "[text is greater than 200 characters]",
                        "encoded to" if encoded else "decoded from"
                    ),
                    description = converted,
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )
            
            # Conversion is Invalid
            else:
                embed = getErrorMessage(self._base64, Code.INVALID_PARAMETER)
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def morse(self, message, parameters):
        """Turns text into/from morse code
        """

        # Check for not enough parameters
        if len(parameters) < self._morse.getMinParameters():
            embed = getErrorMessage(self._morse, Code.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            conversion = parameters[0]
            text = " ".join(parameters[1:])

            # Check if the conversion is valid
            valid = True
            if conversion in self._morse.getAcceptedParameter("conversion", "encode").getAlternatives():
                conversion = "encode"
            elif conversion in self._morse.getAcceptedParameter("conversion", "decode").getAlternatives():
                conversion = "decode"
            
            # Conversion is invalid
            else:
                embed = getErrorMessage(self._morse, Code.INVALID_PARAMETER)
                valid = False
            
            if valid:

                response = await loop.run_in_executor(None,
                    requests.get,
                    Code.MORSE_API_CALL.format(
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
                        "Text to Morse" if conversion == "encode" else "Morse To Text"
                    ) if response["success"] else "Failed to convert",
                    description = "`{}`".format(value),
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )

    async def qrCode(self, message, parameters):
        """Turns data into a QR code.
        """

        # Check for not enough parameters
        if len(parameters) < self._qrCode.getMinParameters():
            embed = getErrorMessage(self._qrCode, Code.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            data = " ".join(parameters)

            # The size should be a function of the data's length
            # Use this --> size = 10(length // 20) + 200
            size = 10*(len(data) // 20) + 200

            embed = discord.Embed(
                title = " ",
                description = " ",
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            ).set_image(
                url = Code.QR_API_CALL.format(size, data.replace(" ", "+"))
            )
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Parsing
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def on_message(self, message):
        """Parses a message and runs a Code Category command if it can

        Parameters:
            message: The Discord Message to parse.\n
        """

        # Make sure message starts with the prefix
        if await Server.startsWithPrefix(message.guild, message.content) and not message.author.bot:

            # Split up into command and parameters if possible
            command, parameters = Category.parseText(await Server.getPrefixes(message.guild), message.content)
            
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            # Iterate through commands
            for cmd in self.getCommands():
                if command in cmd.getAlternatives():
                    async with message.channel.typing():

                        # Run the command but don't try running others
                        await self.run(message, cmd, cmd.getCommand(), message, parameters)
                    break

def setup(client):
    client.add_cog(Code(client))