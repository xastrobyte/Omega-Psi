from util.code.code import tenToNumber, numberToTen
from util.file.server import Server
from util.utils import sendMessage, getErrorMessage, run, timeout

from supercog import Category, Command
import discord, base64

class Code(Category):
    """Creates a Code extension.

    This class holds commands that are used often in coding or computer science.

    Parameters:
        client (discord.ClientUser): The Discord Client to use for sending messages.
    """
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    DESCRIPTION = "Commands that have to do with coding!"

    MAX_BRAINFUCK_LENGTH = 2 ** 15 # 32736

    EMBED_COLOR = 0xFFFF00

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Errors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    START_BASE_MISMATCH = "START_BASE_MISMATCH"
    END_BASE_MISMATCH = "END_BASE_MISMATCH"

    INVALID_START_BASE = "INVALID_START_BASE"
    INVALID_END_BASE = "INVALID_END_BASE"
    INVALID_PARAMETER = "INVALID_PARAMETER"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Constructor
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, client):
        """Creates a Code extension.

        This class holds commands that are used often in coding or computer science.

        Parameters:
            client (discord.ClientUser): The Discord Client to use for sending messages.
        """
        super().__init__(client, "Code")

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Commands
        self._brainfuck = Command(commandDict = {
            "alternatives": ["brainfuck", "brainf", "bf"],
            "info": "Runs brainfuck code. Kinda confusing stuff at first glance.",
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
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "The brainfuck command requires at least the brainfuck code."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "The brainfuck command only needs the code and the parameters. Make sure you remove spaces from both."
                    ]
                }
            }
        })

        self._convert = Command(commandDict = {
            "alternatives": ["convert", "conversion", "baseConversion", "baseConverter"],
            "info": "Converts a number from one base to another base.",
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
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "You need at least the end base and the number to convert."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You only need the start base, the end base, and the number."
                    ]
                },
                Code.INVALID_START_BASE: {
                    "messages": [
                        "The start base you entered is not a valid base."
                    ]
                },
                Code.INVALID_END_BASE: {
                    "messages": [
                        "The end base you entered is not a valid base."
                    ]
                },
                Code.START_BASE_MISMATCH: {
                    "messages": [
                        "The number you entered does not match the start base."
                    ]
                },
                Code.END_BASE_MISMATCH: {
                    "messages": [
                        "The number you entered does not match the end base."
                    ]
                }
            }
        })

        self._base64 = Command(commandDict = {
            "alternatives": ["base64", "b64"],
            "info": "Encodes or decodes text to base64.",
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
                    "info": "The text to encode.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to encode or decode text, you need the conversion type and the text."
                    ]
                },
                Code.INVALID_PARAMETER: {
                    "messages": [
                        "That is not a valid conversion type."
                    ]
                }
            }
        })

        self.setCommands([
            self._brainfuck,
            self._convert,
            self._base64
        ])
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @timeout()
    def brainfuck(self, code, parameters = []):
        """Runs brainfuck code and returns the result.\n

        Parameters:
            code: The brainfuck code to run.\n
            parameters: The parameters to insert into the brainfuck code.\n
        """

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
        return discord.Embed(
            title = "Result",
            description = output,
            colour = Code.EMBED_COLOR
        )
    
    def convert(self, startBase, endBase, number):
        """Converts a number from the start base to the end base.\n

        Parameters:
            startBase: The base to convert from.\n
            endBase: The base to convert to.\n
            number: The number to convert.\n
        """

        # Try converting startBase and endBase to numbers
        try:
            startBase = int(startBase)
            if startBase > 64 or startBase < 2:
                raise Exception()
        except:
            return getErrorMessage(self._convert, Category.INVALID_START_BASE)

        try:
            endBase = int(endBase)
            if endBase > 64 or endBase < 2:
                raise Exception()
        except:
            return getErrorMessage(self._convert, Category.INVALID_END_BASE)

        # Try converting number from startBase to base-10
        # Test to see if number is not zero
        start = number
        title = "Base-{} to Base-{}".format(startBase, endBase)
        description = "`{} --> {}`".format(start, number)

        if number not in ["0", 0]:
            number = numberToTen(number, startBase)

            # Check if number is None; Invalid number for base
            if number == None:
                return getErrorMessage(self._convert, Category.START_BASE_MISMATCH)
            
            # Try converting base-10 to endBase
            number = tenToNumber(number, endBase)

            # Check if number is None; Invalid base
            if number == None:
                return getErrorMessage(self._convert, Category.END_BASE_MISMATCH)
            
            # Return number
            description = "`{} --> {}`".format(start, number)
        
        return discord.Embed(
            title = title,
            description = description,
            colour = Code.EMBED_COLOR
        )
    
    def base64(self, conversionType, text):
        """Encodes or decodes text to or from base64.\n

        Parameters:
            conversionType: Whether to encode or decode text.\n
            text: The text to encode or decode.\n
        """

        # Conversion is Encode
        if conversionType in self._base64.getAcceptedParameter("conversion", "encode").getAlternatives():
            converted = base64.b64encode(text.encode()).decode()
            encoded = True
        
        # Conversion is Decode
        elif conversionType in self._base64.getAcceptedParameter("conversion", "decode").getAlternatives():
            converted = base64.b64decode(text.encode()).decode()
            encoded = False
        
        # Conversion is Invalid
        else:
            return getErrorMessage(self._base64, Category.INVALID_PARAMETER)
        
        # Return conversion
        return discord.Embed(
            title = "`{}` {} Base64".format(
                text if len(text) < 180 else "[text is greater than 200 characters]",
                "encoded to" if encoded else "decoded from"
            ),
            description = converted,
            colour = Code.EMBED_COLOR
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
        if Server.startsWithPrefix(message.guild, message.content) and not message.author.bot:

            # Split up into command and parameters if possible
            command, parameters = Category.parseText(Server.getPrefixes(message.guild), message.content)
            
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            # Brainfuck Command
            if command in self._brainfuck.getAlternatives():

                # 0 Parameters Exist (NOT_ENOUGH_PARAMETERS)
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._brainfuck, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 1 or 2 Parameters Exist (Code only or Code and Parameters)
                elif len(parameters) in [1, 2]:
                    await sendMessage(
                        self.client,
                        message,
                        embed = (
                            await run(message, self._brainfuck, self.brainfuck, parameters[0]) 
                            if len(parameters) == 1 else
                            await run(message, self._brainfuck, self.brainfuck, parameters[0], parameters[1])
                        )
                    )
                
                # 3 or More Parameters Exist (TOO_MANY_PARAMETERS)
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._brainfuck, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Convert Command
            elif command in self._convert.getAlternatives():

                # Less than 2 Parameters Exist
                if len(parameters) < 2:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._convert, Category.NOT_ENOUGH_PARAMETERS)
                    )

                # 2 or 3 Parameters Exist
                elif len(parameters) in [2, 3]:

                    if len(parameters) == 3:
                        startBase = parameters[0]
                        endBase = parameters[1]
                        number = parameters[2]
                    else:
                        startBase = 10
                        endBase = parameters[0]
                        number = parameters[1]

                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._convert, self.convert, startBase, endBase, number)
                    )
                
                # More than 3 Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._convert, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Base64 Command
            elif command in self._base64.getAlternatives():

                # Less than 2 Parameters
                if len(parameters) < 2:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._base64, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 2 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._base64, self.base64, parameters[0], " ".join(parameters[1:]))
                    )

def setup(client):
    client.add_cog(Code(client))
