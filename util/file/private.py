from random import choice as choose
import discord, json

class Private:

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    USER_FILE = "data/users/{}.json"

    CANT_BE_RUN = "CANT_BE_RUN"

    EMBED_COLOR = 0xCCEB0F

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Helper Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def openUser(discordUser):
        """Opens the file for the Discord User given.\n

        discordUser - The Discord User to load.\n
        """
        
        # Set default values
        defaultValues = {
            "id": discordUser.id,
            "name": discordUser.name,
            "nsfw": False
        }

        # Try to open file
        try:

            # Open file
            with open(Private.USER_FILE.format(discordUser.id), "r") as userFile:
                userDict = json.load(userFile)
            
            # See if default values are missing
            for value in defaultValues:

                # Check if value is not in user dictionary; Set default value
                if value not in userDict:
                    userDict[value] = defaultValues[value]
                
            return userDict
            
        # File did not exist; Create file
        except IOError:
            userDict = defaultValues
            Private.closeUser(userDict)
            return userDict
    
    def closeUser(userDict):
        """Closes the file for the Discord User given.\n

        userDict - The Discord User to load.\n
        """
        
        # Open file
        with open(Private.USER_FILE.format(userDict["id"]), "w") as userFile:
            userFile.write(json.dumps(userDict, sort_keys = True, indent = 4))

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def canBeRun(commandObject):
        """Determines whether or not the Command given can be run in a private channel

        commandObject - The Command to test if it can be run.\n
        """
        
        # Check if command is in disabled user commands
        return commandObject.canBeRunInPrivate()
    
    def getErrorMessage(errorType):
        """Returns an error message based off the error type given.\n

        errorType - The type of error message to return.\n
        """
        
        # Keep a dictionary of errors and error messages
        errorMessages = {
            Private.CANT_BE_RUN: [
                "This command cannot be run in a private channel."
            ]
        }

        error = choose(errorMessages[errorType])

        return discord.Embed(
            title = "Error",
            description = error,
            colour = Private.EMBED_COLOR
        )