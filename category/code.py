from util.code.code import tenToNumber, numberToTen
from util.file.server import Server
from util.file.omegaPsi import OmegaPsi
from util.utils import sendMessage, getErrorMessage, timeout

from supercog import Category, Command
import base64, discord

class Code(Category):
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    MAX_BRAINFUCK_LENGTH = 2 ** 15 # 32736

    EMBED_COLOR = 0xFFFF00

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Errors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    START_BASE_MISMATCH = "START_BASE_MISMATCH"
    END_BASE_MISMATCH = "END_BASE_MISMATCH"

    INVALID_LANGUAGE = "INVALID_LANGUAGE"
    INVALID_START_BASE = "INVALID_START_BASE"
    INVALID_END_BASE = "INVALID_END_BASE"
    INVALID_PARAMETER = "INVALID_PARAMETER"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Constructor
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, client):
        super().__init__(
            client, 
            "Code",
            description = "Commands that have to do with coding!",
            locally_inactive_error = Server.getInactiveError,
            globally_inactive_error = OmegaPsi.getInactiveError,
            locally_active_check = Server.isCommandActive,
            globally_active_check = OmegaPsi.isCommandActive
        )

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Commands
        self._brainfuck = Command(commandDict = {
            "alternatives": ["brainfuck", "brainf", "bf"],
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
            },
            "command": self.base64
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
    def brainfuck(self, parameters):
        """Runs brainfuck code and returns the result.\n

        Parameters:
            code: The brainfuck code to run.\n
            parameters: The parameters to insert into the brainfuck code.\n
        """

        # Check for not enough parameters
        if len(parameters) < self._brainfuck.getMinParameters():
            return getErrorMessage(self._brainfuck, Code.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        if len(parameters) > self._brainfuck.getMaxParameters():
            return getErrorMessage(self._brainfuck, Code.TOO_MANY_PARAMETERS)
        
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
        return discord.Embed(
            title = "Result",
            description = output,
            colour = Code.EMBED_COLOR
        )
    
    def convert(self, parameters):
        """Converts a number from the start base to the end base.\n

        Parameters:
            startBase: The base to convert from.\n
            endBase: The base to convert to.\n
            number: The number to convert.\n
        """

        # Check for not enough parameters
        if len(parameters) < self._convert.getMinParameters():
            return getErrorMessage(self._convert, Code.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        if len(parameters) > self._convert.getMaxParameters():
            return getErrorMessage(self._convert, Code.TOO_MANY_PARAMETERS)

        startBase = 10
        endBase = parameters[0]
        number = parameters[1]

        if len(parameters) == 3:
            startBase = parameters[0]
            endBase = parameters[1]
            number = parameters[2]

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
    
    def base64(self, parameters):
        """Encodes or decodes text to or from base64.\n

        Parameters:
            conversionType: Whether to encode or decode text.\n
            text: The text to encode or decode.\n
        """

        # Check for not enough parameters
        if len(parameters) < self._base64.getMinParameters():
            return getErrorMessage(self._base64, Code.NOT_ENOUGH_PARAMETERS)
        
        # Conversion type is first parameter; Text is all parameters after
        conversionType = parameters[0]
        text = " ".join(parameters[1:])

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

            # Iterate through commands
            for cmd in self.getCommands():
                if command in cmd.getAlternatives():
                    await sendMessage(
                        self.client,
                        message,
                        embed = await self.run(message, cmd, cmd.getCommand(), parameters)
                    )

def setup(client):
    client.add_cog(Code(client))
