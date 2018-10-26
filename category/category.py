from util.file.omegaPsi import OmegaPsi
from util.file.server import Server
from util.file.private import Private

from util.utils import censor

import asyncio, discord, inspect, shlex

class Category:

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Errors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # Global Errors
    NOT_ENOUGH_PARAMETERS = "NOT_ENOUGH_PARAMETERS"
    TOO_MANY_PARAMETERS = "TOO_MANY_PARAMETERS"

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    CANT_BE_DEACTIVATED = "CANT_BE_DEACTIVATED"

    INVALID_PARAMETER = "INVALID_PARAMETER"
    INVALID_COMMAND = "INVALID_COMMAND"
    INVALID_MEMBER = " INVALID_MEMBER"
    INVALID_INQUIRY = "INVALID_INQUIRY"
    
    # Code Errors
    INVALID_LANGUAGE = "INVALID_LANGUAGE"

    # Gif Errors
    NO_GIFS_FOUND = "NO_GIFS_FOUND"

    # Help Errors

    # Insult Errors
    INVALID_INSULT_LEVEL = "INVALID_INSULT_LEVEL"

    # Math Errors
    NO_VARIABLES = "NO_VARIABLES"

    INVALID_EXPRESSION = "INVALID_EXPRESSION"

    # Music Errors
    NOT_IN_VOICE_CHANNEL = "NOT_IN_VOICE_CHANNEL"

    # Rank Errors

    # Server Moderator Errors
    NOT_ENOUGH_MEMBERS = "NOT_ENOUGH_MEMBERS"
    NOT_ENOUGH_ROLES = "NOT_ENOUGH_ROLES"
    NO_MEMBER = "NO_MEMBER"
    NO_ROLES = "NO_ROLES"
    TOO_MANY_MEMBERS = "TOO_MANY_MEMBERS"

    INVALID_LEVEL = "INVALID_LEVEL"
    INVALID_COLOR = "INVALID_COLOR"
    INVALID_ROLE = "INVALID_ROLE"

    # Bot Moderator Errors
    BOT_MISSING_PERMISSION = "BOT_MISSING_PERMISSION"
    MEMBER_MISSING_PERMISSION = "MEMBER_MISSING_PERMISSION"

    INVALID_ACTIVITY = "INVALID_ACTIVITY"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Static Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def parseText(text):
        """Parses text and splits it into a command and parameters.\n

        text - The text to parse and split.\n
        """

        # Try splitting text
        try:
            # Remove the prefix; This function will only be called in on_message
            text = text[len(OmegaPsi.PREFIX):]
            split = shlex.split(text)

            # Command is first index ; Parameters are everything after
            command = split[0]
            parameters = split[1:]

            return command, parameters
        
        # Shlex splitting failed, return empty text for both
        except:
            return "", []

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Instance Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, client, category, *, commands = []):
        """A Base class for a Category that goes directly in the Discord Bot.\n

        client - The Discord Client to keep it under.\n
        category - The name of the Category.\n

        Keyword Arguments:\n
         - commands - The Commands that are in the category of Commands.\n
        """
        self.client = client
        self._category = category
        self._commands = commands
    
    def setCommands(self, commands):
        """Sets the Commands in the Category

        commands - The Commands in the Category
        """
        self._commands = commands
    
    def getCommands(self):
        """Returns the Commands in the Category.\n
        """
        return self._commands
    
    def getCommand(self, commandString):
        """Returns the specific Command given by a command string.\n

        commandString - The command string, or an alternative string, of the Command to get.\n
        """
        
        # Iterate through Category Commands
        for command in self._commands:
            if commandString in command.getAlternatives():
                return command
        
        return None
    
    def isCommand(self, commandString):
        """Returns whether or not a Command is in this Category given by a command string.\n

        commandString - The command string, or an alternative string, of the Command to get.\n
        """
        return self.getCommand(commandString) != None
    
    def getErrorMessage(self, commandObject, errorType, *, isNSFW = False):
        """Returns an error message for the given Command.\n

        commandObject - The Command that the error originated in.\n
        errorType - The type of error.\n

        Keyword Arguments:\n
         - isNSFW - Whether or not to return an NSFW result.\n
        """

        error = commandObject.getError(errorType).getMessage()
        
        return discord.Embed(
            title = "Error",
            description = censor(error) if not isNSFW else error,
            colour = 0xFF0000
        )
    
    def getHelp(self, command = None, *, inServer = False, isNSFW = False):
        """Returns help for commands so the user understands the commands.\n

        command - The specific command to get help with.\n

        Keyword Arguments:\n
         - inServer - Whether or not the help menu is being sent in a server or a private channel.\n
         - isNSFW - Whether or not to return an NSFW result.\n
        """

        # Check if command is None; Get help for all commands
        if command == None:

            # Setup Field list
            fields = []
            fieldText = ""
            for cmd in self._commands:

                # Only add command if command can't be run in private
                if (not inServer and cmd.canBeRunInPrivate()) or (inServer):

                    # Get help text and censor it need be
                    cmd = cmd.getHelp(isNSFW = isNSFW)

                    # Make sure field text does not exceed message threshold (set to 1000 by default)
                    if len(fieldText) + len(cmd) >= OmegaPsi.MESSAGE_THRESHOLD:
                        fields.append(fieldText)
                        fieldText = ""
                    
                    fieldText += cmd
            
            # Add any remaining text
            if len(fieldText) > 0:
                fields.append(fieldText)
            
            return fields
        
        # Help for specific command
        for cmd in self._commands:
            if command in cmd.getAlternatives():
                return cmd.getHelp(inDepth = True, isNSFW = isNSFW)
    
    def getHTML(self):
        """Returns the HTML render text for HTML rendering
        """

        # Setup HTML Text
        html = (
            "<tr>\n" +
                "<td id=\"categoryBorder\" style=\"width: 185px; text-align: center;\" colspan=\"3\">\n" +
                    "<h3><strong><em>{} Commands</em></strong></h3>\n" +
                "</td>\n" +
            "</tr>\n\n"
        ).format(
            self._category
        )
        
        # Iterate through commands
        for cmd in self._commands:
            html += cmd.getHTML() + "\n"
        
        return html

    async def run(self, discordMessage, commandObject, func, *args, **kwargs):
        """Runs a command while testing if the Command is globally or locally inactive.\n

        discordMessage - The Discord Message that determines who ran the command and where it is being sent to.\n
        commandObject - The Command that is being run.\n
        func - The function that runs the actual code behind a Command.\n
        *args - The arguments to put into the function.\n
        **kwargs - The keyword arguments to put into the function.\n
        """

        # Emulate Typing
        async with discordMessage.channel.typing():

            # Command is globally active
            if OmegaPsi.isCommandActive(commandObject):

                # Command is a Bot Moderator Command
                if commandObject.isBotModeratorCommand():

                    # Author is a Bot Moderator
                    if OmegaPsi.isAuthorModerator(discordMessage.author):
                        
                        # Try running asynchronous function
                        if inspect.iscoroutinefunction(func):
                            return await func(*args, **kwargs)
                        
                        # Function is synchronous
                        else:
                            return func(*args, **kwargs) # All functions must return an embed
                    
                    # Author is not a Bot Moderator
                    else:
                        return OmegaPsi.getErrorMessage(OmegaPsi.NO_ACCESS)

                # Command is being run in a Server
                elif discordMessage.guild != None:
                    
                    # Command is locally active
                    if Server.isCommandActive(discordMessage.guild, commandObject):

                        # Command is a Server Moderator Command
                        if commandObject.isServerModeratorCommand():

                            # Author is a Server Moderator
                            if Server.isAuthorModerator(discordMessage.guild, discordMessage.author):

                                # Try running asynchronous function
                                if inspect.iscoroutinefunction(func):
                                    return await func(*args, **kwargs)
                                
                                # Function is synchronous
                                else:
                                    return func(*args, **kwargs) # All functions must return an embed
                            
                            # Author is not a Server Moderator
                            else:
                                return Server.getErrorMessage(Server.NO_ACCESS)
                        
                        # Command is not a Server Moderator Command
                        else:

                            # Try running asynchronous function
                            if inspect.iscoroutinefunction(func):
                                return await func(*args, **kwargs)
                            
                            # Function is synchronous
                            else:
                                return func(*args, **kwargs) # All functions must return an embed
                    
                    # Command is locally inactive
                    else:
                        return Server.getErrorMessage(Server.INACTIVE) # Returns Embed
                
                # Command is being run in a Private Message
                else:
                    
                    # Command can be run in Private
                    if commandObject.canBeRunInPrivate():

                        # Try running asynchronous function
                        if inspect.iscoroutinefunction(func):
                            return await func(*args, **kwargs)
                        
                        # Function is synchronous
                        else:
                            return func(*args, **kwargs) # All functions must return an embed
                    
                    # Command cannot be run in Private
                    else:
                        return Private.getErrorMessage(Private.CANT_BE_RUN) # Returns Embed
            
            # Command is globally inactive
            else:
                return OmegaPsi.getErrorMessage(OmegaPsi.INACTIVE) # Returns Embed