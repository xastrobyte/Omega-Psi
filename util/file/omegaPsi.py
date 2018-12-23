from util.file.database import omegaPsi
from util.utils.dictUtils import setDefault

from random import choice as choose
import discord, json, os

class OmegaPsi:

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    PREFIX = "omega "

    NO_ACCESS = "NO_ACCESS"
    INACTIVE = "INACTIVE"
    ACTIVE = "ACTIVE"
    IMPLEMENTING = "IMPLEMENTING"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"

    EMBED_COLOR = 0xCE6000

    MESSAGE_THRESHOLD = 1000

    PROCESS_ID = None

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Helper Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def openOmegaPsi():
        """Opens the JSON file that keeps track of Bot Moderators and
        globally inactive commands.
        """

        # Setup Default Values
        defaultValues = {
            "owner": str(os.environ["DISCORD_ME"]),
            "moderators": [str(os.environ["DISCORD_ME"])],
            "inactive_commands": {},
            "activity_type": discord.ActivityType.playing,
            "activity_name": OmegaPsi.PREFIX + "help",
            "todo": []
        }

        # Get Bot Information from database
        botDict = await omegaPsi.getBot()
        
        return setDefault(defaultValues, botDict)
    
    async def closeOmegaPsi(botDict):
        """Closes the JSON file that keeps track of Bot Moderators and
        globally inactive commands.
        """

        # Update bot information
        await omegaPsi.setBot(botDict)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def addModerator(discordUser):
        """Adds a bot moderator to the bot. Different from a Server moderator.

        Parameters:
            discordUser (discord.User): The Discord User to make a moderator.

        Returns:
            success (bool): Whether or not the addition of the moderator was a success.
        """
        
        # Open the OmegaPsi file
        omegaPsi = await OmegaPsi.openOmegaPsi()

        # Add the Discord User as a bot moderator if User is not already in
        success = False
        if str(discordUser.id) not in omegaPsi["moderators"]:
            omegaPsi["moderators"].append(str(discordUser.id))
            success = True

        # Close the OmegaPsi file
        await OmegaPsi.closeOmegaPsi(omegaPsi)

        return success
    
    async def removeModerator(discordUser):
        """Removes a bot moderator from the bot. Different from a Server moderator.

        Parameters:
            discordUser (discord.User): The Discord User to make a moderator.
        
        Returns:
            success (bool): Whether or not the removal of the moderator was a success.
        """
        
        # Open the OmegaPsi file
        omegaPsi = await OmegaPsi.openOmegaPsi()

        # Remove the Discord User as a bot moderator if User is already in
        success = False
        if str(discordUser.id) in omegaPsi["moderators"] and str(discordUser.id) != omegaPsi["owner"]:
            omegaPsi["moderators"].remove(str(discordUser.id))
            success = True

        # Close the OmegaPsi file
        await OmegaPsi.closeOmegaPsi(omegaPsi)

        return success
    
    async def getModerators():
        """Returns a list of the moderator ID's for Omega Psi.\n
        """
        
        # Open the Omega Psi file
        omegaPsi = await OmegaPsi.openOmegaPsi()

        # Get moderators
        moderators = omegaPsi["moderators"]

        # Close the Omega Psi file
        await OmegaPsi.closeOmegaPsi(omegaPsi)

        return moderators
    
    async def activate(commandObject):
        """Globally activates a command based off the commandObject given. Different from a Server activate.

        Parameters:
            commandObject (supercog.Command): The command to activate.

        Returns:
            success (bool): Whether or not a Command was activated.
        """
        
        # Open the OmegaPsi file
        omegaPsi = await OmegaPsi.openOmegaPsi()

        # Activate a command if the command is already inactive
        success = False
        if commandObject.getAlternatives()[0] in omegaPsi["inactive_commands"]:
            omegaPsi.pop(commandObject.getAlternatives()[0])
            success = True

        # Close the OmegaPsi file
        await OmegaPsi.closeOmegaPsi(omegaPsi)

        return success
    
    async def deactivate(commandObject, reason):
        """Globally deactivates a command based off the commandObject given. Different from a Server deactivate.\n

        commandObject - The command to deactivate.\n
        reason - The reason the command is being deactivated.\n

        Returns True if the command was deactivated.\n
        Returns False if the command was already inactive.\n
        """
        
        # Open the OmegaPsi file
        omegaPsi = await OmegaPsi.openOmegaPsi()

        # Deactivate a command if the command is still active
        success = False
        if commandObject.getAlternatives()[0] not in omegaPsi["inactive_commands"]:
            omegaPsi["inactive_commands"][commandObject.getAlternatives()[0]] = reason
            success = True

        # Close the OmegaPsi file
        await OmegaPsi.closeOmegaPsi(omegaPsi)

        return success

    async def setActivityType(activityType):
        """Sets the activity type for setting the presence of the bot.\n

        activityType - The type of activity to set.\n
        """

        # Open OmegaPsi file
        omegaPsi = await OmegaPsi.openOmegaPsi()

        # Get the activity type
        success = False
        if activityType != omegaPsi["activity_type"]:
            omegaPsi["activity_type"] = activityType
            success = True

        # Close OmegaPsi file
        await OmegaPsi.closeOmegaPsi(omegaPsi)

        return success
    
    async def setActivityName(activityName):
        """Sets the activity name for setting the presence of the bot.\n

        activityName - The name of the activity to set.\n
        """

        # Open OmegaPsi file
        omegaPsi = await OmegaPsi.openOmegaPsi()

        # Get the activity name
        success = False
        if activityName != omegaPsi["activity_name"]:
            omegaPsi["activity_name"] = activityName
            success = True

        # Close OmegaPsi file
        await OmegaPsi.closeOmegaPsi(omegaPsi)

        return success
    
    async def getActivityType():
        """Returns the activity type for setting the presence of the bot.\n
        """
        
        # Open OmegaPsi file
        omegaPsi = await OmegaPsi.openOmegaPsi()

        # Get the activity type
        activityType = omegaPsi["activity_type"]

        # Close OmegaPsi file
        await OmegaPsi.closeOmegaPsi(omegaPsi)

        return activityType
    
    async def getActivityName():
        """Returns the activity name for setting the presence of the bot.\n
        """
        
        # Open OmegaPsi file
        omegaPsi = await OmegaPsi.openOmegaPsi()

        # Get the activity name
        activityName = omegaPsi["activity_name"]

        # Close OmegaPsi file
        await OmegaPsi.closeOmegaPsi(omegaPsi)

        return activityName
    
    async def addToDo(todoItem, index):
        """Adds an item to the Bot's TODO list.
        
        Parameters:
            todoItem (str): The TODO item to add.
        """

        # Open OmegaPsi file
        omegaPsi = await OmegaPsi.openOmegaPsi()

        # Add the item
        value = {"success": False, "reason": "Unknown"}

        # Check if item already exists
        if todoItem in omegaPsi["todo"]:
            value = {"success": False, "reason": "`{}` is already on your TODO list.".format(todoItem)}
        
        # Item does not exist
        else:

            # Check if index is greater than 0
            if index > 0:

                # Check if index is within range of list
                if index - 1 < len(omegaPsi["todo"]):
                    omegaPsi["todo"].insert(index - 1, todoItem)
                    value = {"success": True, "reason": "`{}` was inserted into your TODO list.".format(todoItem)}
                
                # Index is not within range
                else:
                    value = {"success": False, "reason": "That index is out of range."}
                    
            # Index is less than or is 0
            else:

                # Index is 0
                if index == 0:
                    omegaPsi["todo"].append(todoItem)
                    value = {"success": True, "reason": "`{}` was added to your TODO list.".format(todoItem)}
                
                # Index is negative
                else:
                    value = {"success": False, "reason": "You cannot insert into a negative index."}

        # Close OmegaPsi file
        await OmegaPsi.closeOmegaPsi(omegaPsi)

        return value

    async def removeToDo(todoItem):
        """Removes an item from the Bot's TODO list.

        Parameters:
            todoItem (int | str): The TODO item to remove. Can be either the index or the item value.
        """

        # Open OmegaPsi file
        omegaPsi = await OmegaPsi.openOmegaPsi()

        value = {"success": False, "reason": "Unknown"}

        # See if the item index is in it
        if str(todoItem).isdigit():

            # Index is out of range
            if int(todoItem) - 1 >= len(omegaPsi["todo"]):
                value = {"success": False, "reason": "That is out of range."}
            
            else:
                removed = omegaPsi["todo"].pop(int(todoItem) - 1)
                value = {"success": True, "reason": "`{}` was removed from the TODO list.".format(removed)}
        
        # See if item is in it
        else:

            # See if item is not in list
            if todoItem not in omegaPsi["todo"]:
                value = {"success": False, "reason": "There is no item by that name."}

            else:
                removed = omegaPsi["todo"].remove(todoItem)
                value = {"success": True, "reason": "`{}` was removed from the TODO list.".format(removed)}    

        # Close OmegaPsi file
        await OmegaPsi.closeOmegaPsi(omegaPsi)

        return value
    
    async def getToDoList():
        """Returns the Bot's TODO list.
        """

        # Open OmegaPsi file
        omegaPsi = await OmegaPsi.openOmegaPsi()

        # ToDo list
        todo = omegaPsi["todo"]

        # Close OmegaPsi file
        await OmegaPsi.closeOmegaPsi(omegaPsi)

        return todo
    
    async def isAuthorModerator(discordUser):
        """Returns whether or not the Discord User is a bot moderator.\n

        discordUser - The Discord User to add as a bot moderator.\n
        """
        
        # Open the OmegaPsi file
        omegaPsi = await OmegaPsi.openOmegaPsi()

        # Check if author is a moderator
        moderator = str(discordUser.id) in omegaPsi["moderators"]

        # Close the OmegaPsi file
        await OmegaPsi.closeOmegaPsi(omegaPsi)

        return moderator
    
    async def isCommandActive(commandObject):
        """Returns whether or not the command given is active.\n

        commandObject - The Command to check if it's active.\n
        """
        
        # Open the OmegaPsi file
        omegaPsi = await OmegaPsi.openOmegaPsi()

        # Check if command is in inactive_commands
        active = commandObject.getAlternatives()[0] not in omegaPsi["inactive_commands"]

        # Close the OmegaPsi file
        await OmegaPsi.closeOmegaPsi(omegaPsi)

        return active
    
    async def getDeactivatedReason(commandObject):
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
            omegaPsi = await OmegaPsi.openOmegaPsi()

            # Get reason of command's inactivity
            reason = omegaPsi["inactive_commands"][commandObject.getAlternatives()[0]]

            # Close the OmegaPsi file
            await OmegaPsi.closeOmegaPsi(omegaPsi)

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
            OmegaPsi.NO_ACCESS: [
                "You do not have access to this."
            ],
            OmegaPsi.INACTIVE: [
                "This command is globally inactive right now."
            ],
            OmegaPsi.ACTIVE: [
                "This command is already globally active."
            ],
            OmegaPsi.IMPLEMENTING: [
                "This command is being implemented currently."
            ],
            OmegaPsi.TIMEOUT_ERROR: [
                "That seemed to have timed out. oof"
            ]
        }

        error = choose(errorMessages[errorType])

        return discord.Embed(
            title = "Error",
            description = error,
            colour = OmegaPsi.EMBED_COLOR
        )

    def getNoAccessError():
        return OmegaPsi.getErrorMessage(OmegaPsi.NO_ACCESS)
    
    def getInactiveError():
        return OmegaPsi.getErrorMessage(OmegaPsi.INACTIVE)
    
    def getActiveError():
        return OmegaPsi.getErrorMessage(OmegaPsi.ACTIVE)
    
    def getImplementingError():
        return OmegaPsi.getErrorMessage(OmegaPsi.IMPLEMENTING)
    
    def getTimeoutError():
        return OmegaPsi.getErrorMessage(OmegaPsi.TIMEOUT_ERROR)