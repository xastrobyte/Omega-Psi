from random import choice as choose
import discord, json, os

class OmegaPsi:

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    PREFIX = "omega "

    BOT_FILE = "data/omegaPsi.json"

    NO_ACCESS = "NO_ACCESS"
    INACTIVE = "INACTIVE"
    ACTIVE = "ACTIVE"

    EMBED_COLOR = 0xCE6000

    MESSAGE_THRESHOLD = 1000

    BOT_SHEET = 0
    SERVER_SHEET = 1
    USER_SHEET = 2

    SHEET_JSON = {
        "type": os.environ["TYPE"],
        "project_id": os.environ["PROJECT_ID"],
        "private_key_id": os.environ["PRIVATE_KEY_ID"],
        "private_key": os.environ["PRIVATE_KEY"],
        "client_email": os.environ["CLIENT_EMAIL"],
        "client_id": os.environ["CLIENT_ID"],
        "auth_uri": os.environ["AUTH_URI"],
        "token_uri": os.environ["TOKEN_URI"],
        "auth_provider_x509_cert_url": os.environ["AUTH_PROVIDER_X509_CERT_URL"],
        "client_x509_cert_url": os.environ["CLIENT_X509_CERT_URL"]
    }

    SCOPES = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Helper Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def openOmegaPsi():
        """Opens the JSON file that keeps track of Bot Moderators and
        globally inactive commands.
        """

        # Setup Default Values
        defaultValues = {
            "owner": int(os.environ["DISCORD_ME"]),
            "moderators": [int(os.environ["DISCORD_ME"])],
            "inactive_commands": {},
            "activity_type": discord.ActivityType.playing,
            "activity_name": OmegaPsi.PREFIX + "help"
        }
        
        # Try to open file
        try:

            # Open file
            with open(OmegaPsi.BOT_FILE, "r") as botFile:
                botDict = json.load(botFile)
            
            # See if default values are missing
            for value in defaultValues:
                if value not in botDict:
                    botDict[value] = defaultValues[value]
            
            return botDict
            
        # File did not exist, create it
        except IOError:
            botDict = defaultValues
            OmegaPsi.closeOmegaPsi(botDict)
            return botDict
    
    def closeOmegaPsi(botDict):
        """Closes the JSON file that keeps track of Bot Moderators and
        globally inactive commands.
        """
        
        # Open file
        with open(OmegaPsi.BOT_FILE, "w") as botFile:
            botFile.write(json.dumps(botDict, sort_keys = True, indent = 4))

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def addModerator(discordUser):
        """Adds a bot moderator to the bot. Different from a Server moderator.\n

        discordUser - The Discord User to make a moderator.\n

        Returns True if the User was added as a moderator. \n
        Returns False if the User was already a moderator.\n
        """
        
        # Open the OmegaPsi file
        omegaPsi = OmegaPsi.openOmegaPsi()

        # Add the Discord User as a bot moderator if User is not already in
        success = False
        if discordUser.id not in omegaPsi["moderators"]:
            omegaPsi["moderators"].append(discordUser.id)
            success = True

        # Close the OmegaPsi file
        OmegaPsi.closeOmegaPsi(omegaPsi)

        return success
    
    def removeModerator(discordUser):
        """Removes a bot moderator from the bot. Different from a Server moderator.\n

        discordUser - The Discord User to remove as a moderator.\n

        Returns True if the User was removed as a moderator.\n
        Returns False if the User wasn't a moderator.\n
        """
        
        # Open the OmegaPsi file
        omegaPsi = OmegaPsi.openOmegaPsi()

        # Remove the Discord User as a bot moderator if User is already in
        success = False
        if discordUser.id in omegaPsi["moderators"] and discordUser.id != omegaPsi["owner"]:
            omegaPsi["moderators"].remove(discordUser.id)
            success = True

        # Close the OmegaPsi file
        OmegaPsi.closeOmegaPsi(omegaPsi)

        return success
    
    def getModerators():
        """Returns a list of the moderator ID's for Omega Psi.\n
        """
        
        # Open the Omega Psi file
        omegaPsi = OmegaPsi.openOmegaPsi()

        # Get moderators
        moderators = omegaPsi["moderators"]

        # Close the Omega Psi file
        OmegaPsi.closeOmegaPsi(omegaPsi)

        return moderators
    
    def activate(commandObject):
        """Globally activates a command based off the commandObject given. Different from a Server activate.\n

        commandObject - The command to activate.\n

        Returns True if the command was activated.\n
        Returns False if the command was already active.\n
        """
        
        # Open the OmegaPsi file
        omegaPsi = OmegaPsi.openOmegaPsi()

        # Activate a command if the command is already inactive
        success = False
        if commandObject.getAlternatives()[0] in omegaPsi["inactive_commands"]:
            omegaPsi.pop(commandObject.getAlternatives()[0])
            success = True

        # Close the OmegaPsi file
        OmegaPsi.closeOmegaPsi(omegaPsi)

        return success
    
    def deactivate(commandObject, reason):
        """Globally deactivates a command based off the commandObject given. Different from a Server deactivate.\n

        commandObject - The command to deactivate.\n
        reason - The reason the command is being deactivated.\n

        Returns True if the command was deactivated.\n
        Returns False if the command was already inactive.\n
        """
        
        # Open the OmegaPsi file
        omegaPsi = OmegaPsi.openOmegaPsi()

        # Deactivate a command if the command is still active
        success = False
        if commandObject.getAlternatives()[0] not in omegaPsi["inactive_commands"]:
            omegaPsi["inactive_commands"][commandObject.getAlternatives()[0]] = reason
            success = True

        # Close the OmegaPsi file
        OmegaPsi.closeOmegaPsi(omegaPsi)

        return success

    def setActivityType(activityType):
        """Sets the activity type for setting the presence of the bot.\n

        activityType - The type of activity to set.\n
        """

        # Open OmegaPsi file
        omegaPsi = OmegaPsi.openOmegaPsi()

        # Get the activity type
        success = False
        if activityType != omegaPsi["activity_type"]:
            omegaPsi["activity_type"] = activityType
            success = True

        # Close OmegaPsi file
        OmegaPsi.closeOmegaPsi(omegaPsi)

        return success
    
    def setActivityName(activityName):
        """Sets the activity name for setting the presence of the bot.\n

        activityName - The name of the activity to set.\n
        """

        # Open OmegaPsi file
        omegaPsi = OmegaPsi.openOmegaPsi()

        # Get the activity name
        success = False
        if activityName != omegaPsi["activity_name"]:
            omegaPsi["activity_name"] = activityName
            success = True

        # Close OmegaPsi file
        OmegaPsi.closeOmegaPsi(omegaPsi)

        return success
    
    def getActivityType():
        """Returns the activity type for setting the presence of the bot.\n
        """
        
        # Open OmegaPsi file
        omegaPsi = OmegaPsi.openOmegaPsi()

        # Get the activity type
        activityType = omegaPsi["activity_type"]

        # Close OmegaPsi file
        OmegaPsi.closeOmegaPsi(omegaPsi)

        return activityType
    
    def getActivityName():
        """Returns the activity name for setting the presence of the bot.\n
        """
        
        # Open OmegaPsi file
        omegaPsi = OmegaPsi.openOmegaPsi()

        # Get the activity name
        activityName = omegaPsi["activity_name"]

        # Close OmegaPsi file
        OmegaPsi.closeOmegaPsi(omegaPsi)

        return activityName
    
    def isAuthorModerator(discordUser):
        """Returns whether or not the Discord User is a bot moderator.\n

        discordUser - The Discord User to add as a bot moderator.\n
        """
        
        # Open the OmegaPsi file
        omegaPsi = OmegaPsi.openOmegaPsi()

        # Check if author is a moderator
        moderator = discordUser.id in omegaPsi["moderators"]

        # Close the OmegaPsi file
        OmegaPsi.closeOmegaPsi(omegaPsi)

        return moderator
    
    def isCommandActive(commandObject):
        """Returns whether or not the command given is active.\n

        commandObject - The Command to check if it's active.\n
        """
        
        # Open the OmegaPsi file
        omegaPsi = OmegaPsi.openOmegaPsi()

        # Check if command is in inactive_commands
        active = commandObject.getAlternatives()[0] not in omegaPsi["inactive_commands"]

        # Close the OmegaPsi file
        OmegaPsi.closeOmegaPsi(omegaPsi)

        return active
    
    def getDeactivatedReason(commandObject):
        """Returns the reason the command given is inactive.\n

        commandObject - The Command to get the inactive reason for.\n

        If the command is active, it will return a message saying it's active.\n
        """
        
        # Check if command is active
        if OmegaPsi.isCommandActive(commandObject):
            return OmegaPsi.getErrorMessage(OmegaPsi.ACTIVE)
        
        # Command must be inactive, get the reason
        else:

            # Open the OmegaPsi file
            omegaPsi = OmegaPsi.openOmegaPsi()

            # Get reason of command's inactivity
            reason = omegaPsi["inactive_commands"][commandObject.getAlternatives()[0]]

            # Close the OmegaPsi file
            OmegaPsi.closeOmegaPsi(omegaPsi)

            return discord.Embed(
                title = commandObject.getAlternatives()[0],
                description = (
                    "{}\n" +
                    "Reason: {}"
                ).format(
                    OmegaPsi.getErrorMessage(OmegaPsi.INACTIVE),
                    reason
                ),
                colour = OmegaPsi.EMBED_COLOR
            )
    
    def getErrorMessage(errorType):
        """Returns an error message based off the error type given.\n

        errorType - The type of error message to return.\n
        """

        # Keep a dictionary of errors and error messages
        errorMessages = {
            OmegaPsi.INACTIVE: [
                "This command is globally inactive right now."
            ],
            OmegaPsi.ACTIVE: [
                "This command is already globally active."
            ]
        }

        error = choose(errorMessages[errorType])

        return discord.Embed(
            title = "Error",
            description = error,
            colour = OmegaPsi.EMBED_COLOR
        )
