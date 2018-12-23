from category.game import Game
from category.code import Code
from category.image import Image
from category.insult import Insult
from category.internet import Internet
from category.math import Math
from category.meme import Meme
from category.misc import Misc
from category.nsfw import NSFW
from category.rank import Rank
from category.updates import Updates

from util.file.omegaPsi import OmegaPsi
from util.file.server import Server
from util.utils.discordUtils import sendMessage, getErrorMessage

from supercog import Category, Command
import discord


class ServerModerator(Category):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    MAX_INVITE_AGE = 60 * 60 * 24 # 24 hours

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Errors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

    BOT_MISSING_PERMISSION = "BOT_MISSING_PERMISSION"
    MEMBER_MISSING_PERMISSION = "MEMBER_MISSING_PERMISSION"

    NUMBER_TOO_LARGE = "NUMBER_TOO_LARGE"

    NO_ROLES = "NO_ROLE"
    NO_MEMBER = "NO_MEMBER"
    TOO_MANY_MEMBERS = "TOO_MANY_MEMBERS"

    INVALID_COMMAND = "INVALID_COMMAND"
    INVALID_LEVEL = "INVALID_LEVEL"
    INVALID_COLOR = "INVALID_COLOR"
    INVALID_ROLE = "INVALID_ROLE"
    INVALID_CATEGORY = "INVALID_CATEGORY"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Constructor
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, client):
        super().__init__(
            client, 
            "Server Moderator",
            description = "Moderate your server with this.",
            embed_color = 0xAAAA00,
            restriction_info = "In order to use these commands, you must have the Manage Server permissions.",
            server_category = True,
            server_mod_category = True,
            server_mod_error = Server.getNoAccessError,
            locally_inactive_error = Server.getInactiveError,
            globally_inactive_error = OmegaPsi.getInactiveError,
            locally_active_check = Server.isCommandActive,
            globally_active_check = OmegaPsi.isCommandActive,
            server_mod_check = Server.isAuthorModerator
        )

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Bot Commands
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        self._addMember = Command(commandDict = { 
            "alternatives": ["addMember", "addM", "am"],
            "info": "Allows you to add a member, or members, to the server file manually.",
            "run_in_private": False,
            "server_moderator_only": True,
            "can_be_deactivated": False,
            "min_parameters": 1,
            "parameters": {
                "member(s)...": {
                    "info": "The member(s) to add.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to add a member, you need to mention them."
                    ]
                }
            },
            "command": self.addMember
        })

        self._removeMember = Command(commandDict = {
            "alternatives": ["removeMember", "removeM", "rm"],
            "info": "Allows you to remove a member, or members, from the server file manually.",
            "run_in_private": False,
            "server_moderator_only": True,
            "can_be_deactivated": False,
            "min_parameters": 1,
            "parameters": {
                "member(s)...": {
                    "info": "The member(s) to remove.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to remove a member, you need to mention them."
                    ]
                }
            },
            "command": self.removeMember
        })

        self._activate = Command(commandDict = {
            "alternatives": ["activate", "enable"],
            "info": "Allows you to activate a command, or commands, in the server.",
            "run_in_private": False,
            "server_moderator_only": True,
            "can_be_deactivated": False,
            "min_parameters": 1,
            "parameters": {
                "command": {
                    "info": "The command(s) to activate.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to activate a command, you need to type it in."
                    ]
                },
                ServerModerator.ACTIVE: {
                    "messages": [
                        "This command is already active."
                    ]
                },
                ServerModerator.INVALID_COMMAND: {
                    "messages": [
                        "That is not a valid command."
                    ]
                }
            },
            "command": self.activate
        })

        self._deactivate = Command(commandDict = {
            "alternatives": ["deactivate", "disable"],
            "info": "Allows you to deactivate a command in the server.",
            "run_in_private": False,
            "server_moderator_only": True,
            "can_be_deactivated": False,
            "min_parameters": 1,
            "parameters": {
                "command": {
                    "info": "The command to deactivate.",
                    "optional": False
                },
                "reason": {
                    "info": "The reason the command is inactive.",
                    "optional": True
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to deactivate a command, you need to type it in."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You have too many parameters. Make sure you put the reason in quotes (\")."
                    ]
                },
                ServerModerator.INACTIVE: {
                    "messages": [
                        "This command is already inactive."
                    ]
                },
                ServerModerator.INVALID_COMMAND: {
                    "messages": [
                        "That is not a valid command."
                    ]
                }
            },
            "command": self.deactivate
        })

        self._toggleRanking = Command(commandDict = {
            "alternatives": ["toggleRanking", "toggleLeveling", "toggleRank", "toggleLevel", "togRank", "togLevel"],
            "info": "Allows you to toggle the ranking system in the server.",
            "run_in_private": False,
            "server_moderator_only": True,
            "can_be_deactivated": False,
            "max_parameters": 0,
            "errors": {
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You have too many parameters. You don't need any."
                    ]
                }
            },
            "command": self.toggleRanking
        })

        self._toggleWelcomeMessage = Command(commandDict = {
            "alternatives": ["toggleWelcomeMessage", "toggleWelcomeMsg", "togWelcomeMessage", "togWelcomeMsg"],
            "info": "Allows you to toggle the welcome message in the server.",
            "run_in_private": False,
            "server_moderator_only": True,
            "can_be_deactivated": False,
            "max_parameters": 0,
            "errors": {
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You have too many parameters. You don't need any."
                    ]
                }
            },
            "command": self.toggleWelcomeMessage
        })

        self._setWelcomeMessageChannel = Command(commandDict = {
            "alternatives": ["setWelcomeMessageChannel", "setWelcomeMsgChannel", "setWelcomeMsgChan"],
            "info": "Allows you to set the channel that the Join Messages are sent in.",
            "run_in_private": False,
            "server_moderator_only": True,
            "can_be_deactivated": False,
            "min_parameters": 1,
            "max_parameters": 1,
            "parameters": {
                "channel": {
                    "info": "The channel the Join Messages are sent in.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "You need a channel to set for the Join Messages to be sent in."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You can only have 1 channel set for the Join Messages to be sent in."
                    ]
                }
            },
            "command": self.setWelcomeMessageChannel
        })

        self._toggleWelcomeFail = Command(commandDict = {
            "alternatives": ["toggleWelcomeFail", "togWelcomeFail", "togWelcFail"],
            "info": "Toggles whether or not you receive a message if the welcome message fails.",
            "run_in_private": False,
            "server_moderator_only": True,
            "errors": {
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You have too many parameters. You don't need any."
                    ]
                },
                ServerModerator.MEMBER_MISSING_PERMISSION: {
                    "messages": [
                        "You do not have the `manage_roles` permission in this server."
                    ]
                }
            },
            "command": self.toggleWelcomeFail
        })

        self._toggleProfanity = Command(commandDict = {
            "alternatives": ["toggleProfanity", "togProfanity", "toggleProfane", "togProfane"],
            "info": "Toggles the profanity filter.",
            "run_in_private": False,
            "server_moderator_only": True,
            "errors": {
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You have too many parameters. You don't need any."
                    ]
                },
                ServerModerator.MEMBER_MISSING_PERMISSION: {
                    "messages": [
                        "You do not have the `manage_roles` permission in this server."
                    ]
                }
            },
            "command": self.toggleProfanity
        })

        self._toggleProfanityFail = Command(commandDict = {
            "alternatives": ["toggleProfanityFail", "togProfaneFail"],
            "info": "Toggles whether or not you receive a message if the profanity filter fails.",
            "run_in_private": False,
            "server_moderator_only": True,
            "errors": {
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You have too many parameters. You don't need any."
                    ]
                }
            },
            "command": self.toggleProfanityFail
        })

        self._setAutorole = Command(commandDict = {
            "alternatives": ["setAutorole", "autorole"],
            "info": "Sets the role that will be given when someone joins the server.",
            "run_in_private": False,
            "server_moderator_only": True,
            "parameters": {
                "role": {
                    "info": "The role to give when someone joins the server.",
                    "optional": False
                }
            },
            "errors": {
                ServerModerator.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "You need the role to give when someone joins the server."
                    ]
                },
                ServerModerator.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You only need the role to give when someone joins the server."
                    ]
                }
            },
            "command": self.setAutorole
        })

        self._toggleAutorole = Command(commandDict = {
            "alternatives": ["toggleAutorole", "togAutorole", "toggleAuto", "togAuto"],
            "info": "Toggles the autorole feature in the server.",
            "run_in_private": False,
            "server_moderator_only": True,
            "errors": {
                ServerModerator.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You don't need any parameters to toggle the autorole feature."
                    ]
                }
            },
            "command": self.toggleAutorole
        })

        self._toggleAutoroleFail = Command(commandDict = {
            "alternatives": ["toggleAutoroleFail", "toggleAutoFail", "togAutoroleFail", "togAutoFail"],
            "info": "Toggles whether or not you receive a message if the autorole feature fails.",
            "run_in_private": False,
            "server_moderator_only": True,
            "errors": {
                ServerModerator.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You have too many parameters. You don't need any."
                    ]
                }
            },
            "command": self.toggleAutoroleFail
        })

        self._setLevel = Command(commandDict = {
            "alternatives": ["setLevel", "setLvl"],
            "info": "Allows you to set the level of a member, or members, in the server.",
            "run_in_private": False,
            "server_moderator_only": True,
            "can_be_deactivated": False,
            "min_parameters": 2,
            "parameters": {
                "level": {
                    "info": "The level to set for the member(s).",
                    "optional": False
                },
                "member...": {
                    "info": "The member(s) to set the level of.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to set the level of member(s), you need the level and the member(s)."
                    ]
                },
                ServerModerator.INVALID_LEVEL: {
                    "messages": [
                        "That doesn't seem to be a number. Try again."
                    ]
                }
            },
            "command": self.setLevel
        })

        self._addPrefix = Command(commandDict = {
            "alternatives": ["addPrefix", "addPre"],
            "info": "Allows you to add a prefix for this server.",
            "run_in_private": False,
            "server_moderator_only": True,
            "min_parameters": 1,
            "parameters": {
                "prefix": {
                    "info": "The prefix to add to this server.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to add a prefix to this server, you need to enter it in."
                    ]
                }
            },
            "command": self.addPrefix
        })

        self._removePrefix = Command(commandDict = {
            "alternatives": ["removePrefix", "removePre", "remPre"],
            "info": "Allows you to remove a prefix from this server.",
            "run_in_private": False,
            "server_moderator_only": True,
            "min_parameters": 1,
            "parameters": {
                "prefix": {
                    "info": "The prefix to remove from this server.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to remove a prefix from this server, you need to enter it in."
                    ]
                }
            },
            "command": self.removePrefix
        })

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Server Commands
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        self._setServerName = Command(commandDict = {
            "alternatives": ["setServerName", "setSvrName"],
            "info": "Allows you to set the Server's name.",
            "restriction_info": "You and Omega Psi must have manage_guild permissions.",
            "run_in_private": False,
            "server_moderator_only": True,
            "min_parameters": 1,
            "parameters": {
                "name": {
                    "info": "The new name of the Server.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to set the name of the Server, you must type in the name."
                    ]
                },
                ServerModerator.BOT_MISSING_PERMISSION: {
                    "messages": [
                        "The bot does not have the `manage_guild` permission in this server."
                    ]
                },
                ServerModerator.MEMBER_MISSING_PERMISSION: {
                    "messages": [
                        "You do not have the `manage_guild` permission in this server."
                    ]
                }
            },
            "command": self.setServerName
        })

        self._setChannelName = Command(commandDict = {
            "alternatives": ["setChannelName", "setChnlName"],
            "info": "Allows you to set the current channel's name.",
            "restriction_info": "You and Omega Psi must have manage_channels permissions.",
            "run_in_private": False,
            "server_moderator_only": True,
            "min_parameters": 1,
            "parameters": {
                "name": {
                    "info": "The new name of the Channel.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to set the name of the Channel, you must type in the name."
                    ]
                },
                ServerModerator.BOT_MISSING_PERMISSION: {
                    "messages": [
                        "The bot does not have the `manage_channels` permission in this server."
                    ]
                },
                ServerModerator.MEMBER_MISSING_PERMISSION: {
                    "messages": [
                        "You do not have the `manage_channels` permission in this server."
                    ]
                }
            },
            "command": self.setChannelName
        })

        self._setChannelTopic = Command(commandDict = {
            "alternatives": ["setChannelTopic", "setChnlTopic"],
            "info": "Allows you to set the current Channel's topic.",
            "restriction_info": "You and Omega Psi must have manage_channels permissions.",
            "run_in_private": False,
            "server_moderator_only": True,
            "parameters": {
                "name": {
                    "info": "The new topic of the Channel.",
                    "optional": True
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to set the topic of the Channel, you must type in the topic."
                    ]
                },
                ServerModerator.BOT_MISSING_PERMISSION: {
                    "messages": [
                        "The bot does not have the `manage_channels` permission in this server."
                    ]
                },
                ServerModerator.MEMBER_MISSING_PERMISSION: {
                    "messages": [
                        "You do not have the `manage_channels` permission in this server."
                    ]
                }
            },
            "command": self.setChannelTopic
        })

        self._createInvite = Command(commandDict = {
            "alternatives": ["createInvite", "createServerInvite", "getInvite", "getServerInvite"],
            "info": "Allows you to create an invite to this server.",
            "restriction_info": "You and Omega Psi must have create_instant_invite permissions.",
            "run_in_private": False,
            "server_moderator_only": True,
            "max_parameters": 1,
            "parameters": {
                "infinite": {
                    "info": "Whether or not to make the invite an infinite invite.",
                    "optional": True,
                    "accepted_parameters": {
                        "True": {
                            "alternatives": ["True", "true", "T", "t", "Yes", "yes", "Y", "y"],
                            "info": "Set the server invite to never expire."
                        },
                        "False": {
                            "alternatives": ["False", "false", "F", "f", "No", "no", "N", "n"],
                            "info": "Set the server invite to expire."
                        }
                    }
                }
            },
            "errors": {
                Category.INVALID_PARAMETER: {
                    "messages": [
                        "That is not a valid parameter."
                    ]
                },
                ServerModerator.BOT_MISSING_PERMISSION: {
                    "messages": [
                        "The bot does not have the `create_instant_invite` permission in this server."
                    ]
                },
                ServerModerator.MEMBER_MISSING_PERMISSION: {
                    "messages": [
                        "You do not have the `create_instant_invite` permission in this server."
                    ]
                }
            },
            "command": self.createInvite
        })

        self._purge = Command(commandDict = {
            "alternatives": ["purge"],
            "info": "Purges messages in a channel.",
            "restriction_info": "You and Omega Psi must have manage_messages permissions.",
            "run_in_private": False,
            "server_moderator_only": True,
            "min_parameters": 1,
            "max_parameters": 1,
            "parameters": {
                "amount": {
                    "info": "The amount of messages to delete in the channel.",
                    "optional": False
                }
            },
            "errors": {
                ServerModerator.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to purge this channel, you need the amount of messages to delete."
                    ]
                },
                ServerModerator.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to purge this channel, you only need the amount of messages to delete and nothing more."
                    ]
                },
                ServerModerator.BOT_MISSING_PERMISSION: {
                    "messages": [
                        "The bot does not have the `manage_messages` permission in this server."
                    ]
                },
                ServerModerator.MEMBER_MISSING_PERMISSION: {
                    "messages": [
                        "You do not have the `manage_messages` permission in this server."
                    ]
                },
                ServerModerator.INVALID_PARAMETER: {
                    "messages": [
                        "The amount you entered is not a number."
                    ]
                },
                ServerModerator.NUMBER_TOO_LARGE: {
                    "messages": [
                        "The amount you entered is too high. Must be max of 100."
                    ]
                }
            },
            "command": self.purge
        })

        self._addRole = Command(commandDict = {
            "alternatives": ["addRole"],
            "info": "Adds a role to the server.",
            "restriction_info": "You and Omega Psi must have manage_roles permissions.",
            "run_in_private": False,
            "server_moderator_only": True,
            "min_parameters": 1,
            "max_parameters": 2,
            "parameters": {
                "name": {
                    "info": "The name of the role.",
                    "optional": False
                },
                "colour": {
                    "info": "The hex color of the role.",
                    "optional": True
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to add a role, you need to type in the name of the role."
                    ]
                },
                ServerModerator.INVALID_COLOR: {
                    "messages": [
                        "That is not a valid color."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to add a role, you only need a name and the color. Nothing more."
                    ]
                },
                ServerModerator.BOT_MISSING_PERMISSION: {
                    "messages": [
                        "The bot does not have the `manage_roles` permission in this server."
                    ]
                },
                ServerModerator.MEMBER_MISSING_PERMISSION: {
                    "messages": [
                        "You do not have the `manage_roles` permission in this server."
                    ]
                }
            },
            "command": self.addRole
        })

        self._removeRole = Command(commandDict = {
            "alternatives": ["removeRole"],
            "info": "Removes a role from the server.",
            "restriction_info": "You and Omega Psi must have manage_roles permissions.",
            "run_in_private": False,
            "server_moderator_only": True,
            "min_parameters": 1,
            "max_parameters": 1,
            "parameters": {
                "name": {
                    "info": "The name of the role to remove.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to remove a role, you need to tag it."
                    ]
                },
                ServerModerator.INVALID_ROLE: {
                    "messages": [
                        "The role you tagged does not seem to be a valid role."
                    ]
                },
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to remove a role, you can only mention one."
                    ]
                },
                ServerModerator.BOT_MISSING_PERMISSION: {
                    "messages": [
                        "The bot does not have the `manage_roles` permission in this server."
                    ]
                },
                ServerModerator.MEMBER_MISSING_PERMISSION: {
                    "messages": [
                        "You do not have the `manage_roles` permission in this server."
                    ]
                }
            },
            "command": self.removeRole
        })

        self._kickMember = Command(commandDict = {
            "alternatives": ["kickMember", "kickMbr"],
            "info": "Kicks a member from the server.",
            "restriction_info": "You and Omega Psi must have kick_members permissions.",
            "run_in_private": False,
            "server_moderator_only": True,
            "min_parameters": 1,
            "parameters": {
                "member": {
                    "info": "The member to kick.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to kick a member you need to mention them."
                    ]
                },
                ServerModerator.BOT_MISSING_PERMISSION: {
                    "messages": [
                        "The bot does not have the `kick_members` permission in this server."
                    ]
                },
                ServerModerator.MEMBER_MISSING_PERMISSION: {
                    "messages": [
                        "You do not have the `kick_members` permission in this server."
                    ]
                }
            },
            "command": self.kickMember
        })

        self._banMember = Command(commandDict = {
            "alternatives": ["banMember", "banMbr", "ban"],
            "info": "Bans a member from the server.",
            "restriction_info": "You and Omega Psi must have ban_members permissions.",
            "run_in_private": False,
            "server_moderator_only": True,
            "min_parameters": 1,
            "parameters": {
                "member": {
                    "info": "The memberto ban.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to ban a member you need to mention them."
                    ]
                },
                ServerModerator.BOT_MISSING_PERMISSION: {
                    "messages": [
                        "The bot does not have the `ban_members` permission in this server."
                    ]
                },
                ServerModerator.MEMBER_MISSING_PERMISSION: {
                    "messages": [
                        "You do not have the `ban_members` permission in this server."
                    ]
                }
            },
            "command": self.banMember
        })

        self._unbanMember = Command(commandDict = {
            "alternatives": ["unbanMember", "unbanMbr", "unban"],
            "info": "Unbans a member in the server.",
            "restriction_info": "You and Omega Psi must have ban_members permissions.",
            "run_in_private": False,
            "server_moderator_only": True,
            "min_parameters": 1,
            "parameters": {
                "member": {
                    "info": "The member to unban.",
                    "optional": False
                }
            }   ,
            "errors": {
                ServerModerator.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to unban a member you need to mention them."
                    ]
                },
                ServerModerator.BOT_MISSING_PERMISSION: {
                    "messages": [
                        "The bot does not have `ban_members` permission in this server."
                    ]
                },
                ServerModerator.MEMBER_MISSING_PERMISSION: {
                    "messages": [
                        "You do not have the `ban_members` permission in this server."
                    ]
                }
            },
            "command": self.unbanMember
        })

        self._muteMember = Command(commandDict = {
            "alternatives": ["muteMember", "muteMbr", "mute"],
            "info": "Mutes a member in the server.",
            "restriction_info": "You and Omega Psi must have manage_server permissions.",
            "run_in_private": False,
            "server_moderator_only": True,
            "min_parameters": 1,
            "parameters": {
                "member": {
                    "info": "The member to mute.",
                    "optional": False
                }
            }   ,
            "errors": {
                ServerModerator.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to mute a member you need to mention them."
                    ]
                },
                ServerModerator.BOT_MISSING_PERMISSION: {
                    "messages": [
                        "The bot does not have `manage_server` permission in this server."
                    ]
                },
                ServerModerator.MEMBER_MISSING_PERMISSION: {
                    "messages": [
                        "You do not have the `manage_server` permission in this server."
                    ]
                }
            },
            "command": self.muteMember
        })

        self._unmuteMember = Command(commandDict = {
            "alternatives": ["unmuteMember", "unmuteMbr", "unmute"],
            "info": "Unmutes a member in the server.",
            "restriction_info": "You and Omega Psi must have manage_server permissions.",
            "run_in_private": False,
            "server_moderator_only": True,
            "min_parameters": 1,
            "parameters": {
                "member": {
                    "info": "The member to unmute.",
                    "optional": False
                }
            }   ,
            "errors": {
                ServerModerator.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to unmute a member you need to mention them."
                    ]
                },
                ServerModerator.BOT_MISSING_PERMISSION: {
                    "messages": [
                        "The bot does not have `manage_server` permission in this server."
                    ]
                },
                ServerModerator.MEMBER_MISSING_PERMISSION: {
                    "messages": [
                        "You do not have the `manage_server` permission in this server."
                    ]
                }
            },
            "command": self.unmuteMember
        })

        self._addMemberRole = Command(commandDict = {
            "alternatives": ["addMemberRole", "addMbrRole", "giveRole"],
            "info": "Gives a member the mentioned role(s).",
            "restriction_info": "You and Omega Psi must have manage_roles permissions.",
            "run_in_private": False,
            "server_moderator_only": True,
            "min_parameters": 2,
            "parameters": {
                "member": {
                    "info": "The member to give the role(s) to.",
                    "optional": False
                },
                "role(s)...": {
                    "info": "The role(s) to give to the member.",
                    "optional": False
                }
            },
            "errors": {
                ServerModerator.NO_MEMBER: {
                    "messages": [
                        "In order to add the role(s) to a member, you need to mention the member."
                    ]
                },
                ServerModerator.NO_ROLES: {
                    "messages": [
                        "In order to add roles to a member, you need to mention at least one role."
                    ]
                },
                ServerModerator.TOO_MANY_MEMBERS: {
                    "messages": [
                        "You can't mention more than one member at a time."
                    ]
                },
                ServerModerator.BOT_MISSING_PERMISSION: {
                    "messages": [
                        "The bot does not have the `manage_roles` permission in this server."
                    ]
                },
                ServerModerator.MEMBER_MISSING_PERMISSION: {
                    "messages": [
                        "You do not have the `manage_roles` permission in this server."
                    ]
                }
            },
            "command": self.addMemberRole
        })

        self._removeMemberRole = Command(commandDict = {
            "alternatives": ["removeMemberRole", "removeMbrRole", "takeRole"],
            "info": "Removes the mentioned role(s) from a member.",
            "restriction_info": "You and Omega Psi must have manage_roles permissions.",
            "run_in_private": False,
            "server_moderator_only": True,
            "min_parameters": 2,
            "parameters": {
                "member": {
                    "info": "The member to take the role(s) from.",
                    "optional": False
                },
                "role(s)...": {
                    "info": "The role(s) to take from the member.",
                    "optional": False
                }
            },
            "errors": {
                ServerModerator.NO_MEMBER: {
                    "messages": [
                        "In order to remove the role(s) from a member, you need to mention the member."
                    ]
                },
                ServerModerator.NO_ROLES: {
                    "messages": [
                        "In order to remove roles from a member, you need to mention the roles."
                    ]
                },
                ServerModerator.TOO_MANY_MEMBERS: {
                    "messages": [
                        "You can't mention more than one member at a time."
                    ]
                },
                ServerModerator.BOT_MISSING_PERMISSION: {
                    "messages": [
                        "The bot does not have the `manage_roles` permission in this server."
                    ]
                },
                ServerModerator.MEMBER_MISSING_PERMISSION: {
                    "messages": [
                        "You do not have the `manage_roles` permission in this server."
                    ]
                }
            },
            "command": self.removeMemberRole
        })

        self._setMemberRoles = Command(commandDict = {
            "alternatives": ["setMemberRoles", "setMbrRoles", "setRoles"],
            "info": "Sets the roles for a member.",
            "restriction_info": "You and Omega Psi must have manage_roles permissions.",
            "run_in_private": False,
            "server_moderator_only": True,
            "min_parameters": 2,
            "parameters": {
                "member": {
                    "info": "The member to set the role(s) of.",
                    "optional": False
                },
                "role(s)...": {
                    "info": "The role(s) to set for the member.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to set the role, or roles, of a member, you need to mention the member and mention the roles."
                    ]
                },
                ServerModerator.BOT_MISSING_PERMISSION: {
                    "messages": [
                        "The bot does not have the `manage_roles` permission in this server."
                    ]
                },
                ServerModerator.MEMBER_MISSING_PERMISSION: {
                    "messages": [
                        "You do not have the `manage_roles` permission in this server."
                    ]
                }
            },
            "command": self.setMemberRoles
        })

        self.setCommands([

            # Server Commands
            self._addMember,
            self._removeMember,
            self._activate,
            self._deactivate,
            self._toggleRanking,
            self._toggleWelcomeMessage,
            self._setWelcomeMessageChannel,
            self._toggleWelcomeFail,
            self._toggleProfanity,
            self._toggleProfanityFail,
            self._setAutorole,
            self._toggleAutorole,
            self._toggleAutoroleFail,
            self._setLevel,
            self._addPrefix,
            self._removePrefix,

            # Bot Commands
            self._setServerName,
            self._setChannelName,
            self._setChannelTopic,
            self._createInvite,
            self._purge,
            self._addRole,
            self._removeRole,
            self._kickMember,
            self._banMember,
            self._unbanMember,
            self._muteMember,
            self._unmuteMember,
            self._addMemberRole,
            self._removeMemberRole,
            self._setMemberRoles
        ])

        self._categories = {
            "Code": Code(None),
            "Game": Game(None),
            "Image": Image(None),
            "Insult": Insult(None),
            "Internet": Internet(None),
            "Math": Math(None),
            "Meme": Meme(None),
            "Misc": Misc(None),
            "NSFW": NSFW(None),
            "Rank": Rank(None),
            "Updates": Updates(None)
        }
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods (Bot Commands)
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def addMember(self, message, parameters):
        """Manually adds members mentioned to the specified Discord Server.\n

        discordServer - The Discord Server to manually add members to.\n
        members - The list of members to add.\n
        """

        author = message.author
        server = message.guild
        mentions = message.mentions

        # Check if there are no mentions
        if len(mentions) == 0:
            embed = getErrorMessage(self._addMember, ServerModerator.NOT_ENOUGH_PARAMETERS)
        
        # There was at least one mention
        else:

            if author.guild_permissions.manage_guild or await OmegaPsi.isAuthorModerator(author):

                # Iterate through each member
                result = ""
                for member in mentions:
                    result += member.mention + (
                        " was successfully added."
                    ) if await Server.updateMember(server, member, action = Server.ADD_MEMBER) else (
                        " already existed in files."
                    )
                
                embed = discord.Embed(
                    name = "Added Members",
                    description = result,
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )
            
            else:
                embed = getErrorMessage(self._addMember, ServerModerator.MEMBER_MISSING_PERMISSION)
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def removeMember(self, message, parameters):
        """Manually removes members mentioned from the specified Discord Server.\n

        discordServer - The Discord Server to manually remove members from.\n
        members - The list of members to remove.\n
        """

        author = message.author
        server = message.guild
        mentions = message.mentions

        # Check if there are no mentions
        if len(mentions) == 0:
            embed = getErrorMessage(self._removeMember, ServerModerator.NOT_ENOUGH_PARAMETERS)

        # There was at least one mention
        else:

            if author.guild_permissions.manage_guild or await OmegaPsi.isAuthorModerator(author):

                # Iterate through each member
                result = ""
                for member in mentions:
                    result += member.mention + (
                        " was successfully removed."
                    ) if await Server.removeMember(server, member) else (
                        " didn't exist in files."
                    )
                
                embed = discord.Embed(
                    name = "Removed Members",
                    description = result,
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )
            
            else:
                embed = getErrorMessage(self._removeMember, ServerModerator.MEMBER_MISSING_PERMISSION)
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def activate(self, message, parameters):
        """Activates commands in the specified Discord Server.\n

        discordServer - The Discord Server to activate commands in.\n
        commands - The commands to activate.\n
        """

        author = message.author
        server = message.guild

        # Check if there are commands to activate
        if len(parameters) == 0:
            embed = getErrorMessage(self._activate, ServerModerator.NOT_ENOUGH_PARAMETERS)
        
        # There were commands to activate
        else:

            commands = parameters

            if author.guild_permissions.manage_guild or await OmegaPsi.isAuthorModerator(author):
            
                # Open server file
                server = await Server.openServer(server)

                # Iterate through commands if commands are not empty
                if len(commands) > 0:
                    result = ""
                    acCommands = []
                    for command in commands:

                        # Iterate through categories
                        added = False
                        for category in self._categories:

                            # Check if command was part of category
                            commandObject = self._categories[category].getCommand(command)
                            if commandObject != None:
                                acCommands.append(commandObject)
                                added = True
                            
                        if not added:
                            result += "`{}` is not a valid command.\n".format(
                                command
                            )
                    
                    # Activate commands
                    for command in acCommands:
                        if command.getAlternatives()[0] in server["inactive_commands"]:
                            server["inactive_commands"].pop(command.getAlternatives()[0])
                            result += "`{}` was activated.\n".format(
                                command.getAlternatives()[0]
                            )
                        else:
                            result += "`{}` is already active.\n".format(
                                command.getAlternatives()[0]
                            )
                
                # Activate all inactive commands
                else:
                    result = ""
                    for command in server["inactive_commands"]:
                        result += "`{}` was activated.\n".format(command)
                    server["inactive_commands"] = {}
                
                # Close server file
                await Server.closeServer(server)
                
                embed = discord.Embed(
                    name = "Activated",
                    description = result,
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )
            
            else:
                embed = getErrorMessage(self._activate, ServerModerator.MEMBER_MISSING_PERMISSION)
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def deactivate(self, message, parameters):
        """Deactivates a command in the specified Discord Server.\n

        discordServer - The Discord Server to deactivate a command in.\n
        command - The command to deactivate.\n
        reason - The reason the command is being deactivated.\n
        """

        author = message.author
        server = message.guild

        # Check for not enough parameters
        if len(parameters) < self._deactivate.getMinParameters():
            embed = getErrorMessage(self._deactivate, ServerModerator.NOT_ENOUGH_PARAMETERS)
        
        # There were enough parameters
        else:

            command = parameters[0]
            reason = " ".join(parameters[1:])

            if author.guild_permissions.manage_guild or await OmegaPsi.isAuthorModerator(author):
            
                # Open server file
                server = await Server.openServer(server)

                # Check if command is valid
                commandObject = None
                for category in self._categories:
                    commandObject = self._categories[category].getCommand(command)
                    if commandObject != None:
                        break
                if commandObject == None:
                    result = "`{}` is not a valid command.".format(
                        command
                    )
                else:
                    server["inactive_commands"][commandObject.getAlternatives()[0]] = reason
                    result = "`{}` was deactivated.\nReason: {}".format(
                        commandObject.getAlternatives()[0],
                        reason
                    )
                
                # Close server file
                await Server.closeServer(server)

                embed = discord.Embed(
                    name = "Deactivated",
                    description = result,
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )
            
            else:
                embed = getErrorMessage(self._deactivate, ServerModerator.MEMBER_MISSING_PERMISSION)
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def toggleRanking(self, message, parameters):
        """Toggles the ranking system in the specified Discord Server.\n

        discordServer - The Discord Server to toggle the ranking system in.\n
        """

        author = message.author
        server = message.guild

        # Check for too many parameters
        if len(parameters) > self._toggleRanking.getMaxParameters():
            embed = getErrorMessage(self._toggleRanking, ServerModerator.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            if author.guild_permissions.manage_guild or await OmegaPsi.isAuthorModerator(author):

                # Toggle ranking
                await Server.toggleRanking(server)

                if await Server.isRankingActive(server):
                    result = "Ranking has been activated."
                else:
                    result = "Ranking has been deactivated."
                
                embed = discord.Embed(
                    name = "Ranking",
                    description = result,
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )
            
            else:
                embed = getErrorMessage(self._toggleRanking, ServerModerator.MEMBER_MISSING_PERMISSION)
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def toggleWelcomeMessage(self, message, parameters):
        """Toggles the join messaging in the specified Discord await Server.\n

        discordServer - The Discord Server to toggle the welcome messaging in.\n
        """

        author = message.author
        server = message.guild

        # Check for too many parameters
        if len(parameters) > self._toggleWelcomeMessage.getMaxParameters():
            embed = getErrorMessage(self._toggleWelcomeMessage, ServerModerator.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            if author.guild_permissions.manage_guild or await OmegaPsi.isAuthorModerator(author):

                # Toggle join message
                await Server.toggleWelcomeMessage(server)

                if await Server.isWelcomeMessageActive(server):
                    result = "The welcome message has been activated."
                else:
                    result = "The welcome message has been deactivated."
                
                embed = discord.Embed(
                    name = "Welcome Message",
                    description = result,
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )
            
            else:
                embed = getErrorMessage(self._toggleWelcomeMessage, ServerModerator.MEMBER_MISSING_PERMISSION)
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def setWelcomeMessageChannel(self, message, parameters):
        """Sets the channel that the join message is sent to.\n

        discordServer - The Discord Server to set the channel of the join message.\n
        discordChannel - The Discord Channel to set where the join messages are sent to.\n
        """

        author = message.author
        server = message.guild
        channels = message.channel_mentions

        # Check for not enough parameters
        if len(channels) < self._setWelcomeMessageChannel.getMinParameters():
            embed = getErrorMessage(self._setWelcomeMessageChannel, ServerModerator.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(channels) > self._setWelcomeMessageChannel.getMaxParameters():
            embed = getErrorMessage(self._setWelcomeMessageChannel, ServerModerator.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            channel = channels[0]

            if author.guild_permissions.manage_guild or await OmegaPsi.isAuthorModerator(author):

                success = await Server.setWelcomeMessageChannel(server, channel)

                embed = discord.Embed(
                    title = "Channel {} Set".format(
                        "Was" if success else "Was Not"
                    ),
                    description = "{} {} the welcome message channel.".format(
                        channel.mention,
                        "was set as" if success else "is already"
                    )
                )
            
            else:
                embed = getErrorMessage(self._setWelcomeMessageChannel, ServerModerator.MEMBER_MISSION_PERMISSION)
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )

    async def toggleWelcomeFail(self, message, parameters):
        """
        """
        
        # Check for too many parameters
        if len(parameters) > self._toggleWelcomeFail.getMaxParameters():
            embed = getErrorMessage(self._toggleWelcomeFail, Category.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Check if the author has manage server permissions
            # Don't include bot moderator because that isn't up to a bot moderator, only the server owner
            #  FUTURE: Maybe add a way to have specific people messaged
            if message.author.guild_permissions.manage_guild:

                await Server.toggleWelcomeFail(message.guild)

                active = await Server.dmOwnerOnWelcomeFail(message.guild)

                embed = discord.Embed(
                    title = "Active" if active else "Inactive",
                    description = "You will {} receive messages if the Welcome Message fails.".format(
                        "now" if active else "not"
                    ),
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )
            
            else:
                embed = getErrorMessage(self._toggleWelcomeFail, ServerModerator.MEMBER_MISSING_PERMISSION)

        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )        
    
    async def toggleProfanity(self, message, parameters):
        """
        """
        
        # Check for too many parameters
        if len(parameters) > self._toggleProfanity.getMaxParameters():
            embed = getErrorMessage(self._toggleProfanity, ServerModerator.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Check if the author has manage server permissions or is a bot moderator
            if message.author.guild_permissions.manage_guild or await OmegaPsi.isAuthorModerator(message.author):

                await Server.toggleProfanityFilter(message.guild)

                active = await Server.isProfanityFilterActive(message.guild)

                embed = discord.Embed(
                    title = "Active" if active else "Inactive",
                    description = "The Profanity Filter was {} in this server.".format(
                        "activated" if active else "deactivated"
                    ),
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )
            
            else:
                embed = getErrorMessage(self._toggleProfanity, ServerModerator.MEMBER_MISSION_PERMISSION)
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def toggleProfanityFail(self, message, parameters):
        """
        """
        
        # Check for too many parameters
        if len(parameters) > self._toggleProfanityFail.getMaxParameters():
            embed = getErrorMessage(self._toggleProfanityFail, Category.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Check if the author has manage server permissions
            # Don't include bot moderator because that isn't up to a bot moderator, only the server owner
            #  FUTURE: Maybe add a way to have specific people messaged
            if message.author.guild_permissions.manage_guild:

                await Server.toggleProfanityFail(message.guild)

                active = await Server.dmOwnerOnProfanityFail(message.guild)

                embed = discord.Embed(
                    title = "Active" if active else "Inactive",
                    description = "You will {} receive messages if the Profanity Filter fails.".format(
                        "now" if active else "not"
                    ),
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )
            
            else:
                embed = getErrorMessage(self._toggleProfanityFail, ServerModerator.MEMBER_MISSING_PERMISSION)

        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )  
    
    async def setLevel(self, message, parameters):
        """Sets the level of a member, or members, in the Discord Server.\n

        discordServer - The Discord Server to set member's levels in.\n
        level - The level to set.\n
        members - The members to set the level of.\n
        """

        author = message.author
        server = message.guild
        mentions = message.mentions

        # Check if there are no parameters or no mentions
        if len(mentions) == 0 or len(parameters) < self._setLevel.getMinParameters():
            embed = getErrorMessage(self._setLevel, ServerModerator.NOT_ENOUGH_PARAMETERS)
        
        # Check if there are too many parameters
        elif len(parameters) > self._setLevel.getMaxParameters():
            embed = getErrorMessage(self._setLevel, ServerModerator.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Check if the level is an integer
            try:
                level = int(parameters[0])

                if author.guild_permissions.manage_guild or await OmegaPsi.isAuthorModerator(author):
                    
                    # Set the level of each member
                    result = ""
                    for member in mentions:
                        result += await Server.setLevel(server, member, level) + "\n"
                    
                    embed = discord.Embed(
                        name = "Result",
                        description = result,
                        colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                    )
                
                else:
                    embed = getErrorMessage(self._setLevel, ServerModerator.MEMBER_MISSING_PERMISSION)
            
            except:
                embed = getErrorMessage(self._setLevel, ServerModerator.INVALID_LEVEL)
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def addPrefix(self, message, parameters):
        """Adds a prefix to the specified Discord Server.\n

        discordServer - The Discord Server to add the prefix to.\n
        prefixes - The prefix(es) to add.\n
        """

        author = message.author
        server = message.guild

        # Check for not enough parameters
        if len(parameters) < self._addPrefix.getMinParameters():
            embed = getErrorMessage(self._addPrefix, ServerModerator.NOT_ENOUGH_PARAMETERS)
        
        # There were enough parameters
        else:

            prefixes = parameters

            if author.guild_permissions.manage_guild or await OmegaPsi.isAuthorModerator(author):

                # Iterate through the prefixes
                addPrefixes = ""
                addCount = 0
                for prefix in prefixes:
                    temp = await Server.addPrefix(server, prefix)
                    addPrefixes += temp["message"]
                    addCount += temp["success_int"]
                
                embed = discord.Embed(
                    title = "Prefix{} {} added.".format(
                        "es" if addCount > 1 else "",
                        "not" if addCount == 0 else ""
                    ),
                    description = addPrefixes if addCount > 0 else "No prefixes were added.",
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )
            
            else:
                embed = getErrorMessage(self._addPrefix, ServerModerator.MEMBER_MISSING_PERMISSION)
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def removePrefix(self, message, parameters):
        """Removes a prefix from the specified Discord Server.\n

        discordServer - The Discord Server to remove the prefix from.\n
        prefixes - The prefix(es) to remove.\n
        """

        author = message.author
        server = message.guild

        prefixes = parameters

        if author.guild_permissions.manage_guild or await OmegaPsi.isAuthorModerator(author):

            # No prefixes in list; Reset prefixes to default prefix
            if len(prefixes) == 0:
                await Server.resetPrefixes(server)

                embed = discord.Embed(
                    title = "Prefixes Reset",
                    description = "All prefixes have been removed and the default has been set.",
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )
            
            # Prefixes are in list
            else:

                # Iterate through prefixes
                removePrefixes = ""
                removeCount = 0
                for prefix in prefixes:
                    temp = await Server.removePrefix(server, prefix)
                    removePrefixes += temp["message"]
                    removeCount += temp["success_int"]
                
                embed = discord.Embed(
                    title = "Prefix{} {} removed.".format(
                        "es" if removeCount > 1 else ""
                        "not" if removeCount == 0 else ""
                    ),
                    description = removePrefixes if removeCount > 0 else "No prefixes were removed.",
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )
        
        else:
            embed = getErrorMessage(self._removePrefix, ServerModerator.MEMBER_MISSING_PERMISSION)

        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods (Server Commands)
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def setServerName(self, message, parameters):
        """Sets the name of the Discord Server.\n

        discordServer - The Discord Server to set the name of.\n
        name - The name to set.\n
        """

        author = message.author
        server = message.guild

        # Check for not enough parameters
        if len(parameters) < self._setServerName.getMinParameters():
            embed = getErrorMessage(self._setServerName, ServerModerator.NOT_ENOUGH_PARAMETERS)
        
        # There were enough parameters
        else:

            # Only run if bot and author has permissions
            if author.guild_permissions.manage_guild or await OmegaPsi.isAuthorModerator(author):
                try:

                    name = " ".join(parameters)

                    # Get old name and set new name of server
                    oldName = server.name
                    await server.edit(
                        name = name
                    )

                    embed = discord.Embed(
                        title = "Changed Name",
                        description = "{} was changed to {}".format(
                            oldName, name
                        ),
                        colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                    )
                
                # Bot does not have permission
                except discord.Forbidden:
                    embed = getErrorMessage(self._setServerName, ServerModerator.BOT_MISSING_PERMISSION)
            
            # Author does not have permission
            else:
                embed = getErrorMessage(self._setServerName, ServerModerator.MEMBER_MISSING_PERMISSION)
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )

    async def setChannelName(self, message, parameters):
        """
        """

        author = message.author
        channel = message.channel

        # Check for not enough parameters
        if len(parameters) < self._setChannelName.getMinParameters():
            embed = getErrorMessage(self._setChannelName, ServerModerator.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Only run if bot and author has permissions
            if author.guild_permissions.manage_channels or await OmegaPsi.isAuthorModerator(author):
                try:

                    name = " ".join(parameters)

                    # Change the name
                    oldName = channel.name
                    await channel.edit(
                        name = name
                    )

                    embed = discord.Embed(
                        title = "Changed Name",
                        description = "{} was changed to {}".format(
                            oldName, name
                        ),
                        colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                    )
                
                # Bot does not have permission
                except:
                    embed = getErrorMessage(self._setChannelName, ServerModerator.BOT_MISSING_PERMISSION)
            
            # Author does not have permission
            else:
                embed = getErrorMessage(self._setChannelName, ServerModerator.AUTHOR_MISSING_PERMISSION)
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def setChannelTopic(self, message, parameters):
        """
        """

        author = message.author
        channel = message.channel

        # Only run if bot and author has permissions
        if author.guild_permissions.manage_channels or await OmegaPsi.isAuthorModerator(author):
            try:

                topic = " ".join(parameters)

                # Change the topic
                oldTopic = channel.topic
                await channel.edit(
                    topic = topic
                )

                embed = discord.Embed(
                    title = "Changed Topic",
                    description = " ",
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                ).add_field(
                    name = "Old Topic",
                    value = oldTopic,
                    inline = False
                ).add_field(
                    name = "New Topic",
                    value = topic,
                    inline = False
                )
            
            # Bot does not have permission
            except:
                embed = getErrorMessage(self._setChannelName, ServerModerator.BOT_MISSING_PERMISSION)
        
        # Author does not have permission
        else:
            embed = getErrorMessage(self._setChannelName, ServerModerator.AUTHOR_MISSING_PERMISSION)
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def createInvite(self, message, parameters):
        """Creates an Instant Invite for the Discord Server.\n
        
        discordChannel - The Discord Channel to create an Instant Invite for.\n
        infinite - Whether or not the invite expires.\n
        """

        author = message.author
        channel = message.channel

        # Check for too many parameters
        if len(parameters) > self._createInvite.getMaxParameters():
            embed = getErrorMessage(self._createInvite, ServerModerator.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Only run if bot and author has permissions
            if author.guild_permissions.create_instant_invite or await OmegaPsi.isAuthorModerator(author):
                try:

                    infinite = parameters[0]

                    # Create the invite
                    infinite = infinite in self._createInvite.getAcceptedParameter("infinite", "True").getAlternatives()
                    invite = await channel.create_invite(
                        max_age = 0 if infinite else ServerModerator.MAX_INVITE_AGE
                    )

                    embed = discord.Embed(
                        title = "Invite Created",
                        description = "[Copy Me!]({})".format(
                            invite
                        ),
                        colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                    )
                
                # Bot does not have permission
                except discord.Forbidden:
                    embed = getErrorMessage(self._createInvite, ServerModerator.BOT_MISSING_PERMISSION)
            
            # Author does not have permission
            else:
                embed = getErrorMessage(self._createInvite, ServerModerator.MEMBER_MISSING_PERMISSION)

        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def purge(self, message, parameters):
        """
        """

        author = message.author
        channel = message.channel

        # Check for not enough parameters
        if len(parameters) < self._purge.getMinParameters():
            embed = getErrorMessage(self._purge, ServerModerator.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._purge.getMaxParameters():
            embed = getErrorMessage(self._purge, ServerModerator.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Check if amount is a number
            try:
                amount = int(parameters[0])

                # Make sure amount is within 100
                if amount <= 100:

                    # Only run if bot and author have permissions
                    if author.guild_permissions.manage_messages or await OmegaPsi.isAuthorModerator(author):
                        try:

                            # Get list of messages to delete
                            messages = []
                            async for target in channel.history(limit = amount):
                                messages.append(target)
                            
                            # Delete Original Message
                            await message.delete()

                            # Delete list of message
                            await channel.delete_messages(messages)

                            embed = discord.Embed(
                                title = "Purged",
                                description = "{} message{} {} purged from this channel.".format(
                                    amount, 
                                    "" if amount == 1 else "s",
                                    "was" if amount == 1 else "were"
                                ),
                                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                            )

                        except:
                            embed = getErrorMessage(self._purge, ServerModerator.BOT_MISSING_PERMISSION)
            
                    # Author does not have permissions
                    else:
                        embed = getErrorMessage(self._purge, ServerModerator.MEMBER_MISSING_PERMISSION)
                
                # Amount is greater than 100
                else:
                    embed = getErrorMessage(self._purge, ServerModerator.NUMBER_TOO_LARGE)
            
            # Amount is not a number
            except:
                embed = getErrorMessage(self._purge, ServerModerator.INVALID_PARAMETER)
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def addRole(self, message, parameters):
        """Adds a role to the specified Discord Server.\n

        author - The Discord Member who ran the command.\n
        discordServer - The Discord Server to add the Role to.\n
        roleName - The name of the Role to add.\n
        colorHex - The hex code of the color to set for the role.\n
        """

        author = message.author
        server = message.guild

        # Check for not enough parameters
        if len(parameters) < self._addRole.getMinParameters():
            embed = getErrorMessage(self._addRole, ServerModerator.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._addRole.getMaxParameters():
            embed = getErrorMessage(self._addRole, ServerModerator.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Only run if bot and author have permissions
            if author.guild_permissions.manage_roles or await OmegaPsi.isAuthorModerator(author):
                try:

                    roleName = parameters[0]
                    colorHex = parameters[1]

                    # Try to set role color from hex
                    try:
                        color = discord.Color(eval(colorHex))

                        # Create role
                        role = await server.create_role(
                            name = roleName,
                            hoist = True,
                            colour = color,
                            mentionable = True
                        )

                        # Bot had permission; Return success message
                        embed = discord.Embed(
                            name = "Role Added",
                            description = "The role {} was added.".format(role.mention),
                            colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                        )
                    
                    # Evaluation failed; Invalid color
                    except:
                        embed = getErrorMessage(self._addRole, ServerModerator.INVALID_COLOR)

                # Bot does not have permission
                except discord.Forbidden:
                    embed = getErrorMessage(self._addRole, ServerModerator.BOT_MISSING_PERMISSION)
            
            # Author does not have permission
            else:
                embed = getErrorMessage(self._addRole, ServerModerator.MEMBER_MISSING_PERMISSION)

        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def removeRole(self, message, parameters):
        """Removes a role from the specified Discord Server.\n

        discordServer - The Discord Server to remove the role from.\n
        role - The role to remove. Can either be a role name or a Discord Role.\n
        """

        author = message.author
        server = message.guild
        roles = message.role_mentions

        if len(roles) == 0:
            roles = parameters

        # Check to see if there are not enough parameters
        if len(roles) < self._removeRole.getMinParameters():
            embed = getErrorMessage(self._removeRole, ServerModerator.NOT_ENOUGH_PARAMETERS)

        # Check to see if there are too many parameters
        elif len(roles) > self._removeRole.getMaxParameters():
            embed = getErrorMessage(self._removeRole, ServerModerator.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Only run if bot and author have permissions
            if author.guild_permissions.manage_roles or await OmegaPsi.isAuthorModerator(author):
                try:

                    role = roles[0]

                    # Role is not a Discord Role
                    if type(role) == str:

                        # Search through member roles
                        for discordRole in server.roles:
                            if discordRole.name == role:
                                role = discordRole
                                break
                    
                    # Remove the role
                    await role.delete()

                    embed = discord.Embed(
                        name = "Role Deleted",
                        description = "The role `{}` was removed.".format(role.name),
                        colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                    )

                # Bot does not have permission
                except discord.Forbidden:
                    embed = getErrorMessage(self._removeRole, ServerModerator.BOT_MISSING_PERMISSION)
            
            # Author does not have permission
            else:
                embed = getErrorMessage(self._removeRole, ServerModerator.MEMBER_MISSING_PERMISSION)

        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def setAutorole(self, message, parameters):
        """
        """

        guild = message.guild
        author = message.author
        roles = message.role_mentions

        # Check for not enough parameters
        if len(roles) < self._setAutorole.getMinParameters():
            embed = getErrorMessage(self._setAutorole, ServerModerator.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(roles) > self._setAutorole.getMaxParameters():
            embed = getErrorMessage(self._setAutorole, ServerModerator.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            role = roles[0]

            # Set the autorole in the server
            await Server.setAutorole(guild, role)

            # Create success embed
            embed = discord.Embed(
                title = "Autorole Set",
                description = "{} has been set as the role to be given automatically.".format(role.mention),
                colour = self.getEmbedColor() if guild == None else author.top_role.color
            )

        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    author.name,
                    author.discriminator
                ),
                icon_url = author.avatar_url
            )
        )
    
    async def toggleAutorole(self, message, parameters):
        """
        """
        
        # Check for too many parameters
        if len(parameters) > self._setAutorole.getMaxParameters():
            embed = getErrorMessage(self._setAutorole, ServerModerator.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Toggle the autorole
            await Server.toggleAutorole(message.guild)
            active = await Server.isAutoroleActive(message.guild)

            # Create embed
            embed = discord.Embed(
                title = "Activated" if active else "Deactivated",
                description = "The Autorole feature was {}".format(
                    "activated" if active else "deactivated"
                ),
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            )

        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def toggleAutoroleFail(self, message, parameters):
        """
        """
        
        # Check for too many parameters
        if len(parameters) > self._toggleAutoroleFail.getMaxParameters():
            embed = getErrorMessage(self._toggleAutoroleFail, ServerModerator.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Toggle the autorole
            await Server.toggleAutoroleFail(message.guild)
            active = await Server.dmOwnerOnAutoroleFail(message.guild)

            # Create embed
            embed = discord.Embed(
                title = "Activated" if active else "Deactivated",
                description = "You will {} be notified if the autorole feature fails".format(
                    "now" if active else "not"
                ),
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            )

        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )

    async def kickMember(self, message, parameters):
        """Kicks the specified Discord Member from the Discord Server.\n

        discordServer - The Discord Server to kick the member from.\n
        discordMember - The Discord Member to kick.\n
        """

        author = message.author
        server = message.guild
        mentions = message.mentions

        # Check for not enough parameters
        if len(mentions) < self._kickMember.getMinParameters():
            embed = getErrorMessage(self._kickMember, ServerModerator.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            member = mentions[0]

            # Only run if bot and author have permissions
            if author.guild_permissions.kick_members or await OmegaPsi.isAuthorModerator(author):
                try:

                    # Kick the member
                    await server.kick(member)

                    embed = discord.Embed(
                        title = "Member Kicked",
                        description = "{}#{} was kicked from the server.".format(member.name, member.discriminator),
                        colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                    )

                # Bot does not have permission
                except discord.Forbidden:
                    embed = getErrorMessage(self._kickMember, ServerModerator.BOT_MISSING_PERMISSION)
            
            # Author does not have permission
            else:
                embed = getErrorMessage(self._kickMember, ServerModerator.MEMBER_MISSING_PERMISSION)

        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )

    async def banMember(self, message, parameters):
        """Bans the specified Discord Member from the Discord Server.\n

        discordServer - The Discord Server to ban the member from.\n
        discordMember - The Discord Member to ban.\n
        """

        author = message.author
        server = message.guild
        mentions = message.mentions

        # Check for not enough parameters
        if len(mentions) < self._banMember.getMinParameters():
            embed = getErrorMessage(self._banMember, ServerModerator.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Only run if bot and author have permissions
            if author.guild_permissions.ban_members or await OmegaPsi.isAuthorModerator(author):
                try:

                    member = mentions[0]

                    # Ban the member
                    await server.ban(member)

                    embed = discord.Embed(
                        title = "Member Banned",
                        description = "{}#{} was banned from the server.".format(member.name, member.discriminator),
                        colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                    )

                # Bot does not have permission
                except discord.Forbidden:
                    embed = getErrorMessage(self._banMember, ServerModerator.BOT_MISSING_PERMISSION)
            
            # Author does not have permission
            else:
                embed = getErrorMessage(self._banMember, ServerModerator.MEMBER_MISSING_PERMISSION)

        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def unbanMember(self, message, parameters):
        """
        """

        author = message.author
        server = message.guild
        mentions = message.mentions

        # Check for not enough parameters
        if len(mentions) < self._unbanMember.getMinParameters():
            embed = getErrorMessage(self._unbanMember, ServerModerator.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Only run if bot and author have permissions
            if author.guild_permissions.ban_members or await OmegaPsi.isAuthorModerator(author):
                try:

                    member = mentions[0]

                    # Ban the member
                    await server.unban(member)

                    embed = discord.Embed(
                        title = "Member Unbanned",
                        description = "{}#{} was unbanned in the server.".format(member.name, member.discriminator),
                        colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                    )

                # Bot does not have permission
                except discord.Forbidden:
                    embed = getErrorMessage(self._unbanMember, ServerModerator.BOT_MISSING_PERMISSION)
            
            # Author does not have permission
            else:
                embed = getErrorMessage(self._unbanMember, ServerModerator.MEMBER_MISSING_PERMISSION)

        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def muteMember(self, message, parameters):
        """
        """
        
        author = message.author
        server = message.guild
        mentions = message.mentions

        # Check for not enough parameters
        if len(mentions) < self._muteMember.getMinParameters():
            embed = getErrorMessage(self._muteMember, ServerModerator.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Only run if bot and author have permissions
            if author.guild_permissions.manage_guild or await OmegaPsi.isAuthorModerator(author):
                try:
                    
                    # Eventually add support for multiple members
                    member = mentions[0]

                    # Create Muted role if it doesn't exist
                    mutedRole = None
                    for role in server.roles:
                        if role.name == "Muted":
                            mutedRole = role
                            break
                    
                    if not mutedRole:
                        mutedRole = await server.create_role(
                            name = "Muted"
                        )
                        for channel in server.channels:
                            if member.permissions_in(channel) != 0:
                                await channel.set_permissions(
                                    mutedRole,
                                    send_messages = False, read_messages = True,
                                    add_reactions = False, connect = True,
                                    speak = False
                                )
                    
                    await member.add_roles(mutedRole)

                    embed = discord.Embed(
                        title = "Member Muted",
                        description = "{}#{} was muted in the server.".format(member.name, member.discriminator),
                        colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                    )

                # Bot does not have permission
                except discord.Forbidden:
                    embed = getErrorMessage(self._muteMember, ServerModerator.BOT_MISSING_PERMISSION)
            
            # Author does not have permission
            else:
                embed = getErrorMessage(self.muteMember, ServerModerator.MEMBER_MISSING_PERMISSION)

        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def unmuteMember(self, message, parameters):
        """
        """
        
        author = message.author
        server = message.guild
        mentions = message.mentions

        # Check for not enough parameters
        if len(mentions) < self._muteMember.getMinParameters():
            embed = getErrorMessage(self._muteMember, ServerModerator.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Only run if bot and author have permissions
            if author.guild_permissions.manage_guild or await OmegaPsi.isAuthorModerator(author):
                try:

                    # Eventually add support for multiple members
                    member = mentions[0]

                    # Check if member is muted
                    mutedRole = None
                    for role in server.roles:
                        if role.name == "Muted":
                            mutedRole = role
                            break
                    
                    if not mutedRole:
                        embed = discord.Embed(
                            title = "Member not Muted",
                            description = "{}#{} is not muted in the server.".format(member.name, member.discriminator),
                            colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                        )
                    
                    else:
                        await member.remove_roles(mutedRole)

                        embed = discord.Embed(
                            title = "Member Unmuted",
                            description = "{}#{} was unmuted in the server.".format(member.name, member.discriminator),
                            colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                        )

                # Bot does not have permission
                except discord.Forbidden:
                    embed = getErrorMessage(self._muteMember, ServerModerator.BOT_MISSING_PERMISSION)
            
            # Author does not have permission
            else:
                embed = getErrorMessage(self.muteMember, ServerModerator.MEMBER_MISSING_PERMISSION)

        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def addMemberRole(self, message, parameters):
        """Adds the Discord Roles to the Discord Member.\n

        discordMember - The Discord Member to add the roles to.\n
        discordRoles - The Discord Roles to add.\n
        """

        author = message.author
        mentions = message.mentions
        roles = message.role_mentions

        # Check if there were no members mentioned
        if len(mentions) == 0:
            embed = getErrorMessage(self._addMemberRole, ServerModerator.NO_MEMBER)
        
        # Check if there were no roles mentioned
        elif len(roles) == 0:
            embed = getErrorMessage(self._addMemberRole, ServerModerator.NO_ROLES)
        
        # There were enough parameters
        else:

            # Only run if bot and author have permissions
            if author.guild_permissions.manage_roles or await OmegaPsi.isAuthorModerator(author):
                try:

                    # Iterate through members
                    for member in mentions:

                        # Add the roles to the member
                        await member.add_roles(roles)

                    members = [member.mention for member in mentions]

                    embed = discord.Embed(
                        title = "Roles Added",
                        description = "{} {} given the following roles:\n".format(
                            ", ".join(members),
                            "was" if len(members) == 1 else "were"
                        ),
                        colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                    )

                    # Add roles that were added
                    fields = []
                    fieldText = ""
                    for role in roles:
                        
                        roleText = role.mention + "\n"

                        if len(fieldText) + len(roleText) > OmegaPsi.MESSAGE_THRESHOLD:
                            fields.append(fieldText)
                            fieldText = ""
                        
                        fieldText += roleText
                    
                    if len(roleText) > 0:
                        fields.append(roleText)
                    
                    count = 0
                    for field in fields:
                        count += 1
                        embed.add_field(
                            name = "{}".format(
                                "({} / {})".format(
                                    count, len(fields)
                                ) if len(fields) > 1 else ""
                            )
                        )

                # Bot does not have permission
                except discord.Forbidden:
                    embed = getErrorMessage(self._addMemberRoles, ServerModerator.BOT_MISSING_PERMISSION)
            
            # Author does not have permission
            else:
                embed = getErrorMessage(self._addMemberRoles, ServerModerator.MEMBER_MISSING_PERMISSION)

        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def removeMemberRole(self, message, parameters):
        """Removes the Discord Roles from the Discord Member.\n

        discordMember - The Discord Member to remove roles from.\n
        discordRoles - The Discord Roles to remove.\n
        """

        author = message.author
        mentions = message.mentions
        roles = message.role_mentions

        # Check if there were no members mentioned
        if len(mentions) == 0:
            embed = getErrorMessage(self._addMemberRole, ServerModerator.NO_MEMBER)
        
        # Check if there were no roles mentioned
        elif len(roles) == 0:
            embed = getErrorMessage(self._addMemberRole, ServerModerator.NO_ROLES)
        
        # There were the proper amount of parameters
        else:

            # Only run if bot and author have permissions
            if author.guild_permissions.manage_roles or await OmegaPsi.isAuthorModerator(author):
                try:

                    for member in mentions:

                        # Remove the roles from the member
                        await member.remove_roles(roles)
                    
                    members = [member.mention for member in mentions]

                    embed = discord.Embed(
                        title = "Roles Removed",
                        description = "{} had the following roles removed:\n".format(
                            ", ".join(members)
                        ),
                        colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                    )

                    # Add roles that were removed
                    fields = []
                    fieldText = ""
                    for role in roles:
                        
                        roleText = role.mention + "\n"

                        if len(fieldText) + len(roleText) > OmegaPsi.MESSAGE_THRESHOLD:
                            fields.append(fieldText)
                            fieldText = ""
                        
                        fieldText += roleText
                    
                    if len(roleText) > 0:
                        fields.append(roleText)
                    
                    count = 0
                    for field in fields:
                        count += 1
                        embed.add_field(
                            name = "{}".format(
                                "({} / {})".format(
                                    count, len(fields)
                                ) if len(fields) > 1 else ""
                            )
                        )

                # Bot does not have permission
                except discord.Forbidden:
                    embed = getErrorMessage(self._removeMemberRoles, ServerModerator.BOT_MISSING_PERMISSION)
            
            # Author does not have permission
            else:
                embed = getErrorMessage(self._removeMemberRoles, ServerModerator.MEMBER_MISSING_PERMISSION)

        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def setMemberRoles(self, message, parameters):
        """Sets the Discord Roles to the Discord Member.\n

        discordMember - The Discord Member to set the Discord Roles of.\n
        discordRoles - The Discord Roles to set.\n
        """

        author = message.author
        mentions = message.mentions
        roles = message.role_mentions

        # Check if there were no members mentioned
        if len(mentions) == 0:
            embed = getErrorMessage(self._addMemberRole, ServerModerator.NO_MEMBER)
        
        # Check if there were no roles mentioned
        elif len(roles) == 0:
            embed = getErrorMessage(self._addMemberRole, ServerModerator.NO_ROLES)
        
        # There were the proper amount of parameters
        else:

            # Only run if bot and author have permissions
            if author.guild_permissions.manage_roles or await OmegaPsi.isAuthorModerator(author):
                try:

                    for member in mentions:

                        # Sets the roles of the member by removing and then adding the roles
                        for role in member.roles:
                            await role.delete()

                        member.add_roles(roles)
                    
                    members = [member.mention for member in mentions]

                    embed = discord.Embed(
                        title = "Roles Set",
                        description = "The roles of {} are now:\n".format(
                            ", ".join(members)
                        ),
                        colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                    )

                    # Setup fields
                    fields = []
                    fieldText = ""
                    for role in roles:

                        discordRole = role.mention + "\n"

                        if len(fieldText) + len(discordRole) >= OmegaPsi.MESSAGE_THRESHOLD:
                            fields.append(fieldText)
                            fieldText = ""
                        
                        fieldText += discordRole
                    
                    if len(fieldText) > 0:
                        fields.append(fieldText)

                    # Add fields
                    count = 0
                    for field in fields:
                        count += 1
                        embed.add_field(
                            name = "{}".format(
                                "({} / {})".format(
                                    count, len(fields)
                                ) if len(fields) > 1 else ""
                            ),
                            value = field,
                            inline = False
                        )

                # Bot does not have permission
                except discord.Forbidden:
                    embed = getErrorMessage(self._setMemberRoles, ServerModerator.BOT_MISSING_PERMISSION) 
            
            # Author does not have permission
            else:
                embed = getErrorMessage(self._setMemberRoles, ServerModerator.MEMBER_MISSING_PERMISSION)

        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Parsing
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def on_message(self, message):
        """Parses a message and runs a Server Moderator Category command if it can.\n

        message - The Discord Message to parse.\n
        """

        # Make sure message starts with the prefix
        if await Server.startsWithPrefix(message.guild, message.content) and not message.author.bot:

            # Split up into command and parameters if possible
            command, parameters = Category.parseText(await Server.getPrefixes(message.guild), message.content)

            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            # Iterate through commands
            for cmd in self.getCommands():
                if command in cmd.getAlternatives():
                    async with message.channel.typing():

                        # Run the command but don't try running others
                        await self.run(message, cmd, cmd.getCommand(), message, parameters)
                    break

def setup(client):
    client.add_cog(ServerModerator(client))