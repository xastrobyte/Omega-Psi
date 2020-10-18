from discord import Embed
from discord.ext.commands import CheckFailure

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class NotADeveloper(CheckFailure): pass
class NotAGuildManager(CheckFailure): pass
class NotInGuild(CheckFailure): pass
class CommandDisabled(CheckFailure): pass
class NotNSFWOrGuild(CheckFailure): pass

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def get_error_message(message):
    """Returns an error message in the form of an embed

    :param message: The error message to display
    
    :rtype: Embed
    """

    return Embed(
        title = "Error",
        description = message,
        colour = 0xFF0000
    )

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

UNIMPLEMENTED_ERROR = get_error_message("This hasn't been implemented yet :(")
NOT_A_DEVELOPER_ERROR = get_error_message("You are not a developer.")
NOT_A_GUILD_MANAGER_ERROR = get_error_message("You don't have `Manage Server` permissions ¯\_(ツ)_/¯")
NOT_IN_GUILD_ERROR = get_error_message("You must be in a server to run this command.")
COMMAND_FAILED_ERROR = lambda command: get_error_message("The `{}` command seems to have failed. All developers have been notified and it should be fixed soon.".format(command))
COMMAND_DISABLED_ERROR = lambda command: get_error_message("The `{}` command is currently disabled.".format(command))

# # # # # Game Cog Errors # # # # #

MEMBER_NOT_FOUND_ERROR = get_error_message("That member was not found in the server.")
NOT_NSFW_OR_GUILD_ERROR = lambda command: get_error_message("The `{}` command can only be run in NSFW channels in a server.".format(command))

# # # # # Insults Cog Errors # # # # #

NO_INSULT_ERROR = get_error_message("You must provide an insult to add to the bot.")
NO_COMPLIMENT_ERROR = get_error_message("You must provide a compliment to add to the bot.")