from category.category import Category

from util.command.command import Command
from util.file.omegaPsi import OmegaPsi
from util.utils import sendMessage

from random import choice as choose

import discord, os

class Insult(Category):

    INSULTS_LOCATION = "data/insults/{}.txt"

    EMBED_COLOR = 0x800000

    def __init__(self, client):
        super().__init__(client, "Insult")

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Commands
        self._insult = Command({
            "alternatives": ["insult", "i"],
            "info": "Sends you an insult.",
            "parameters": {
                "insultLevel": {
                    "optional": True,
                    "info": "The level of insult to send.",
                    "accepted": {
                        "touchy": {
                            "alternatives": ["touchy", "t"],
                            "info": "Soft insults for a soft person.",
                        },
                        "remorseful": {
                            "alternatives": ["remorseful", "remorse", "r"],
                            "info": "Harder insults. Might offend you."
                        },
                        "noRemorse": {
                            "alternatives": ["noRemorse", "noremorse", "nr"],
                            "info": "Hardcore insults. And I mean it."
                        }
                    }
                }
            },
            "errors": {
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "Whoa man. The insult command doesn't take more than a single parameter."
                    ]
                },
                Category.INVALID_INSULT_LEVEL: {
                    "messages": [
                        "That is not a valid insult level. Try `{}help insult` to see the insult levels.".format(OmegaPsi.PREFIX)
                    ]
                }
            }
        })

        self._add = Command({
            "alternatives": ["addInsult", "addI", "add"],
            "info": "Allows you to add your own insult.",
            "parameters": {
                "insultLevel": {
                    "optional": False,
                    "info": "The level of insult to add.",
                    "accepted": {
                        "touchy": {
                            "alternatives": ["touchy", "t"],
                            "info": "Soft insults for a soft person.",
                        },
                        "remorseful": {
                            "alternatives": ["remorseful", "remorse", "r"],
                            "info": "Harder insults. Might offend you."
                        },
                        "noRemorse": {
                            "alternatives": ["noRemorse", "noremorse", "nr"],
                            "info": "Hardcore insults. And I mean it."
                        }
                    }
                },
                "insult": {
                    "optional": False,
                    "info": "The insult to add."
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "If only you had enough parameters, you could actually add your own insult."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "Whoa man. The add insult command doesn't take more than two parameters."
                    ]
                },
                Category.INVALID_INSULT_LEVEL: {
                    "messages": [
                        "That is not a valid insult level. Try `!help addInsult` to see the insult levels."
                    ]
                }
            }
        })

        self._list = Command({
            "alternatives": ["listInsults", "list", "l"],
            "info": "Lists the insults that can be sent.",
            "parameters": {
                "insultLevel": {
                    "optional": True,
                    "info": "The level of insult to send.",
                    "accepted": {
                        "touchy": {
                            "alternatives": ["touchy", "t"],
                            "info": "Soft insults for a soft person.",
                        },
                        "remorseful": {
                            "alternatives": ["remorseful", "remorse", "r"],
                            "info": "Harder insults. Might offend you."
                        },
                        "noRemorse": {
                            "alternatives": ["noRemorse", "noremorse", "nr"],
                            "info": "Hardcore insults. And I mean it."
                        }
                    }
                }
            },
            "errors": {
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "Whoa man. The list command doesn't take more than a single parameter."
                    ]
                },
                Category.INVALID_INSULT_LEVEL: {
                    "messages": [
                        "That is not a valid insult level. Try `!help listInsults` to see the insult levels."
                    ]
                }
            }
        })

        self._insultLevelNames = ["touchy", "remorseful", "noRemorse"]
        self._insultLevels = (
            self._insult.getParameter("insultLevel").getAcceptedParameter("touchy").getAlternatives() +
            self._insult.getParameter("insultLevel").getAcceptedParameter("remorseful").getAlternatives() +
            self._insult.getParameter("insultLevel").getAcceptedParameter("noRemorse").getAlternatives()
        )

        self.setCommands([
            self._insult,
            self._add,
            self._list
        ])
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def insult(self, insultLevel = None, isNSFW = False):
        """Returns a random insult from the specified insult level or from any insult level.\n

        Keyword Arguments:\n
         - insultLevel - The level of insult to get.\n
         - isNSFW - Whether or not to allow an NSFW insult.\n
        """

        # Check if insult level is None; Generate random insult level
        if insultLevel == None:
            insultLevel = choose(self._insultLevelNames)
        
        # Check if insult level is touchy
        if insultLevel in self._insult.getAcceptedParameter("insultLevel", "touchy").getAlternatives():
            insultLevel = "touchy"
        
        # Check if insult level is remorseful
        elif insultLevel in self._insult.getAcceptedParameter("insultLevel", "remorseful").getAlternatives():
            insultLevel = "remorseful"
        
        # Check if insult level is noRemorse
        elif insultLevel in self._insult.getAcceptedParameter("insultLevel", "noRemorse").getAlternatives():
            insultLevel = "noRemorse"
        
        # Insult level was invalid
        else:
            return self.getErrorMessage(self._insult, Category.INVALID_INSULT_LEVEL)
        
        # Load insults file for insult level
        temp = open(Insult.INSULTS_LOCATION.format(insultLevel), "r")
        insults = temp.readlines()
        temp.close()

        # Choose insult
        target = choose(insults)

        # Regenerate as long as isNSFW is False and result is NSFW
        while not isNSFW and target.find("NSFW") != -1:
            target = choose(insults)
        
        # Remove NSFW tag from end if isNSFW
        if target.find("NSFW") != -1:
            target = target[:target.find("NSFW")]
        
        return discord.Embed(
            name = "Result",
            description = target,
            colour = Insult.EMBED_COLOR
        )
    
    def addInsult(self, insultLevel, insult):
        """Adds the specified insult to the specified insult level.\n

        insultLevel - The level of the insult to add to.\n
        insult - The insult to add.\n
        """

        # Check if the insult level is touchy
        if insultLevel in self._add.getAcceptedParameter("insultLevel", "touchy").getAlternatives():
            insultLevel = "touchy"
        
        # Check if the insult level is remorseful
        elif insultLevel in self._add.getAcceptedParameter("insultLevel", "remorseful").getAlternatives():
            insultLevel = "remorseful"
        
        # Check if the insult level is noRemorse
        elif insultLevel in self._add.getAcceptedParameter("insultLevel", "noRemorse").getAlternatives():
            insultLevel = "noRemorse"
        
        # Insult level is invalid
        else:
            return self.getErrorMessage(self._add, Category.INVALID_INSULT_LEVEL)
        
        # Load insults file for insult level
        temp = open(Insult.INSULTS_LOCATION.format(insultLevel), "a")
        temp.write(insult + "\n")
        temp.close()

        return discord.Embed(
            title = "Insult Added",
            description = "Your insult: {}".format(insult),
            colour = Insult.EMBED_COLOR
        )
    
    def listInsults(self, insultLevel = None, recursive = False):
        """Returns a list of insults that can be sent.\n

        Keyword Arguments:\n
         - insultLevel - The level of insult to return a list of insults from.\n
         - recursive = Whether or not the insults are being added to a list rather than returned in an embed.\n
        """

        # Check if insult level is None; Add each insult level
        if insultLevel == None:

            # Setup insults embed
            embed = discord.Embed(
                title = "Insults",
                description = "A list of insults that can be sent.",
                colour = Insult.EMBED_COLOR
            )

            # Add each insult level
            for level in self._insultLevelNames:

                # Field list comes from recursive definition
                fields = self.listInsults(level, True)

                # Add each field
                count = 0
                for field in fields:
                    count += 1
                    embed.add_field(
                        name = "{} Insults {}".format(
                            level,
                            "({} / {})".format(
                                count, len(fields)
                            ) if len(fields) > 1 else ""
                        ),
                        value = field
                    )
            
            return embed
        
        # Check if insult level is a valid insult level
        elif insultLevel in self._insultLevels:

            # Change insult level into something readable
            if insultLevel in self._list.getAcceptedParameter("insultLevel", "touchy").getAlternatives():
                insultLevel = "touchy"
            
            elif insultLevel in self._list.getAcceptedParameter("insultLevel", "remorseful").getAlternatives():
                insultLevel = "remorseful"

            elif insultLevel in self._list.getAcceptedParameter("insultLevel", "noRemorse").getAlternatives():
                insultLevel = "noRemorse"
            
            # Open insult file
            temp = open(Insult.INSULTS_LOCATION.format(insultLevel), "r")
            insults = temp.readlines()
            temp.close()

            # Setup insults text
            insultsFields = []
            insultsText = ""

            # Iterate through insults
            for insult in insults:

                # Add newline to insult if there is no newline
                if not insult.endswith("\n"):
                    insult += "\n"
                
                # Check if adding insult will exceed message threshold
                if len(insultsText) + len(insult) >= int(os.environ["MESSAGE_THRESHOLD"]):
                    insultsFields.append(insultsText)
                    insultsText = ""
                
                insultsText += insult
            
            if len(insultsText) > 0:
                insultsFields.append(insultsText)
            
            # Return fields if recursive
            if recursive:
                return insultsFields
            
            # Return embed if not recursive
            else:

                 # Setup embed and add fields
                embed = discord.Embed(
                    title = "{} Insults".format(insultLevel),
                    description = "A list of insults in the {} category.\n".format(insultLevel),
                    colour = Insult.EMBED_COLOR
                )

                count = 0
                for field in insultsFields:
                    count += 1
                    embed.add_field(
                        name = "{} Insults {}".format(
                            insultLevel,
                            "({} / {})".format(
                                count, len(fields)
                            ) if len(fields) > 1 else ""
                        ),
                        value = field
                    )
                
                return embed
        
        # Insult level is invalid
        else:
            return self.getErrorMessage(self._list, Category.INVALID_INSULT_LEVEL)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Parsing
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def on_message(self, message):
        """Parses a message and runs an Insult Category command if it can.\n

        message - The Discord Message to parse.\n
        """

        # Make sure message starts with the prefix
        if message.content.startswith(OmegaPsi.PREFIX) and not message.author.bot:

            # Split up into command and parameters if possible
            command, parameters = Category.parseText(message.content)
            
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            # Insult Command
            if command in self._insult.getAlternatives():

                # 0 or 1 Parameters Exist (Insult)
                if len(parameters) in [0, 1]:

                    try:
                        isNSFW = message.channel.is_nsfw()
                    except:
                        isNSFW = True

                    await sendMessage(
                        self.client,
                        message,
                        embed = await self.run(
                            message, self._insult, self.insult,
                            None if len(parameters) == 0 else parameters[0],
                            isNSFW
                        )
                    )
                
                # 2 or More Parameters Exist (TOO_MANY_PARAMETERS)
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = self.getErrorMessage(self._insult, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Add Insult Command
            elif command in self._add.getAlternatives():

                # Less than 2 Parameters Exist (NOT_ENOUGH_PARAMETERS)
                if len(parameters) < 2:
                    await sendMessage(
                        self.client,
                        message,
                        embed = self.getErrorMessage(self._add, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 2 Parameters Exist (Add Insult)
                elif len(parameters) == 2:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await self.run(
                            message, self._add, self.addInsult,
                            parameters[0], parameters[1]
                        )
                    )
                
                # 3 or More Parameters Exist (TOO_MANY_PARAMETERS)
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = self.getErrorMessage(self._add, Category.TOO_MANY_PARAMETERS)
                    )
            
            # List Insults Command
            elif command in self._list.getAlternatives():

                # 0 or 1 Parameters Exist (List Insults)
                if len(parameters) in [0, 1]:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await self.run(
                            message, self._list, self.listInsults,
                            None if len(parameters) == 0 else parameters[0]
                        )
                    )
                
                # 2 or More Parameters Exist (TOO_MANY_PARAMETERS)
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = self.getErrorMessage(self._list, Category.TOO_MANY_PARAMETERS)
                    )

def setup(client):
    client.add_cog(Insult(client))