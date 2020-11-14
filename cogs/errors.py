from discord import Embed
from discord.ext.commands import CheckFailure

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class NotADeveloper(CheckFailure): pass
class NotATester(CheckFailure): pass
class NotAGuildManager(CheckFailure): pass
class NotInGuild(CheckFailure): pass
class CommandDisabled(CheckFailure): pass
class NotNSFWOrGuild(CheckFailure): pass
class NotInVoiceChannel(CheckFailure): pass

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
NOT_A_TESTER_ERROR = get_error_message("You are not a tester.")
NOT_A_GUILD_MANAGER_ERROR = get_error_message("You don't have `Manage Server` permissions ¯\_(ツ)_/¯")
NOT_IN_GUILD_ERROR = get_error_message("You must be in a server to run this command.")
COMMAND_FAILED_ERROR = lambda command: get_error_message("The `{}` command seems to have failed. There must be an issue or a bug. Report it using the `bug` command!".format(command))
COMMAND_DISABLED_ERROR = lambda command: get_error_message("The `{}` command is currently disabled.".format(command))

# # # # # Game Cog Errors # # # # #

MEMBER_NOT_FOUND_ERROR = get_error_message("That member was not found in the server.")
NOT_NSFW_OR_GUILD_ERROR = lambda command: get_error_message("The `{}` command can only be run in NSFW channels in a server.".format(command))

# # # # # Insults Cog Errors # # # # #

NO_INSULT_ERROR = get_error_message("You must provide an insult to add to the bot.")
NO_COMPLIMENT_ERROR = get_error_message("You must provide a compliment to add to the bot.")

# # # # # Insults Cog Errors # # # # #

NOT_IN_VOICE_CHANNEL_ERROR = get_error_message("You must be in a voice channel to Omega Psi to join!")
ALREADY_IN_VOICE_CHANNEL_ERROR = get_error_message("Omega Psi is already in a voice channel!")
NOTHING_PLAYING_ERROR = get_error_message("\*crickets\* ... there is nothing playing")
ALREADY_VOTED_ERROR = get_error_message("You've already voted!")
EMPTY_QUEUE_ERROR = get_error_message("There is nothing in the queue!")
INVALID_VOLUME_ERROR = lambda volume: get_error_message(
    "You can't set the volume to {}. That's too {}!".format(
        volume, "low" if volume < 0 else "high"
    )
)
MUSIC_NOT_FOUND_ERROR = lambda source: get_error_message(
    f"I couldn't find {source} :pensive: Try again maybe?"
)