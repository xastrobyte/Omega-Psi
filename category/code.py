from category.category import Category

from util.command.command import Command, timeout
from util.file.omegaPsi import OmegaPsi
from util.utils import sendMessage

import discord

class Code(Category):
    
    DESCRIPTION = "Commands that have to do with coding!"

    MAX_BRAINFUCK_LENGTH = 2 ** 15 # 32736

    EMBED_COLOR = 0xFFFF00

    REPL_IT_URL = "https://repl.it/data/repls/35a0ee83-68a1-416e-bafb-c45c765060bb/gen_repl_token"
    REPL_IT_EVAL = "wss://eval.repl.it/ws"

    def __init__(self, client):
        super().__init__(client, "Code")

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Commands
        self._brainfuck = Command({
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

        self.setCommands([
            self._brainfuck
        ])
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @timeout()
    def brainfuck(self, code, parameters = []):
        """Runs brainfuck code and returns the result.\n

        code - The brainfuck code to run.\n
        parameters - The parameters to insert into the brainfuck code.\n
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
                    data[dataPointer] = parameters[paramPointer][0]
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

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Parsing
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def on_message(self, message):
        """Parses a message and runs a Code Category command if it can

        message - The Discord Message to parse.\n
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
                        embed = self.getErrorMessage(self._brainfuck, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 1 or 2 Parameters Exist (Code only or Code and Parameters)
                elif len(parameters) in [1, 2]:
                    await sendMessage(
                        self.client,
                        message,
                        embed = (
                            await self.run(message, self._brainfuck, self.brainfuck, parameters[0]) 
                            if len(parameters) == 1 else
                            await self.run(message, self._brainfuck, self.brainfuck, parameters[0], parameters[1])
                        )
                    )
                
                # 3 or More Parameters Exist (TOO_MANY_PARAMETERS)
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = self.getErrorMessage(self._brainfuck, Category.TOO_MANY_PARAMETERS)
                    )

def setup(client):
    client.add_cog(Code(client))
