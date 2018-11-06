from category.game import Game
from category.code import Code
from category.image import Image
from category.insult import Insult
from category.internet import Internet
from category.math import Math
from category.rank import Rank
from category.misc import Misc

from util.file.server import Server
from util.utils import sendMessage, getErrorMessage, run

from supercog import Category, Command
import discord

class ServerModerator(Category):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    DESCRIPTION = "Moderate your server with this. Owners have the only access to this at first."

    EMBED_COLOR = 0xAAAA00

    MAX_INVITE_AGE = 60 * 60 * 24 # 24 hours

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Errors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

    BOT_MISSING_PERMISSION = "BOT_MISSING_PERMISSION"
    MEMBER_MISSING_PERMISSION = "MEMBER_MISSING_PERMISSION"

    NO_ROLES = "NO_ROLE"
    NO_MEMBER = "NO_MEMBER"
    TOO_MANY_MEMBERS = "TOO_MANY_MEMBERS"

    INVALID_COMMAND = "INVALID_COMMAND"
    INVALID_LEVEL = "INVALID_LEVEL"
    INVALID_COLOR = "INVALID_COLOR"
    INVALID_ROLE = "INVALID_ROLE"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Constructor
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, client):
        super().__init__(client, "Server Moderator")

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Bot Commands
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        self._addMember = Command(commandDict = {
            "alternatives": ["addMember", "addM", "am"],
            "info": "Allows you to add a member, or members, to the server file manually.",
            "run_in_private": False,
            "server_moderator_only": True,
            "can_be_deactivated": False,
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
            }
        })

        self._removeMember = Command(commandDict = {
            "alternatives": ["removeMember", "removeM", "rm"],
            "info": "Allows you to remove a member, or members, from the server file manually.",
            "run_in_private": False,
            "server_moderator_only": True,
            "can_be_deactivated": False,
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
            }
        })

        self._addModerator = Command(commandDict = {
            "alternatives": ["addModerator", "addMod"],
            "info": "Allows you to add a moderator, or moderators, to the server (only for Omega Psi).",
            "run_in_private": False,
            "server_moderator_only": True,
            "can_be_deactivated": False,
            "parameters": {
                "member(s)...": {
                    "info": "The moderator(s) to add to the server.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to add a moderator, you need to mention them."
                    ]
                }
            }
        })

        self._removeModerator = Command(commandDict = {
            "alternatives": ["removeModerator", "removeMod", "remMod"],
            "info": "Allows you to remove a moderator, or moderators, from the server (only for Omega Psi).",
            "run_in_private": False,
            "server_moderator_only": True,
            "can_be_deactivated": False,
            "parameters": {
                "member(s)...": {
                    "info": "The moderator(s) to remove from the server.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to remove a moderator, you need to mention them."
                    ]
                }
            }
        })

        self._activate = Command(commandDict = {
            "alternatives": ["activate", "enable"],
            "info": "Allows you to activate a command, or commands, in the server.",
            "run_in_private": False,
            "server_moderator_only": True,
            "can_be_deactivated": False,
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
            }
        })

        self._deactivate = Command(commandDict = {
            "alternatives": ["deactivate", "disable"],
            "info": "Allows you to deactivate a command in the server.",
            "run_in_private": False,
            "server_moderator_only": True,
            "can_be_deactivated": False,
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
            }
        })

        self._toggleRanking = Command(commandDict = {
            "alternatives": ["toggleRanking", "toggleLeveling", "toggleRank", "toggleLevel", "togRank", "togLevel"],
            "info": "Allows you to toggle the ranking system in the server.",
            "run_in_private": False,
            "server_moderator_only": True,
            "can_be_deactivated": False,
            "errors": {
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You have too many parameters. You don't need any."
                    ]
                }
            }
        })

        self._toggleJoinMessage = Command(commandDict = {
            "alternatives": ["toggleJoinMessage", "toggleJoinMsg", "togJoinMessage", "togJoinMsg"],
            "info": "Allows you to toggle the join message in the server.",
            "run_in_private": False,
            "server_moderator_only": True,
            "can_be_deactivated": False,
            "errors": {
                Category.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You have too many parameters. You don't need any."
                    ]
                }
            }
        })

        self._setJoinMessageChannel = Command(commandDict = {
            "alternatives": ["setJoinMessageChannel", "setJoinMsgChannel", "setJoinMsgChan"],
            "info": "Allows you to set the channel that the Join Messages are sent in.",
            "run_in_private": False,
            "server_moderator_only": True,
            "can_be_deactivated": False,
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
            }
        })

        self._setLevel = Command(commandDict = {
            "alternatives": ["setLevel", "setLvl"],
            "info": "Allows you to set the level of a member, or members, in the server.",
            "run_in_private": False,
            "server_moderator_only": True,
            "can_be_deactivated": False,
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
            }
        })

        self._addPrefix = Command(commandDict = {
            "alternatives": ["addPrefix", "addPre"],
            "info": "Allows you to add a prefix for this server.",
            "run_in_private": False,
            "server_moderator_only": True,
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
            }
        })

        self._removePrefix = Command(commandDict = {
            "alternatives": ["removePrefix", "removePre", "remPre"],
            "info": "Allows you to remove a prefix from this server.",
            "run_in_private": False,
            "server_moderator_only": True,
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
            }
        })

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Server Commands
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        self._setServerName = Command(commandDict = {
            "alternatives": ["setServerName", "setSvrName"],
            "info": "Allows you to set the Server's name.",
            "restriction_info": "You and Omega Psi must have manage_server permissions.",
            "run_in_private": False,
            "server_moderator_only": True,
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
                        "The bot does not have the `manage_server` permission in this server."
                    ]
                },
                ServerModerator.MEMBER_MISSING_PERMISSION: {
                    "messages": [
                        "You do not have the `manage_server` permission in this server."
                    ]
                }
            }
        })

        self._createInvite = Command(commandDict = {
            "alternatives": ["createInvite", "createServerInvite", "getInvite", "getServerInvite"],
            "info": "Allows you to create an invite to this server.",
            "restriction_info": "You and Omega Psi must have create_instant_invite permissions.",
            "run_in_private": False,
            "server_moderator_only": True,
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
            }
        })

        self._addRole = Command(commandDict = {
            "alternatives": ["addRole"],
            "info": "Adds a role to the server.",
            "restriction_info": "You and Omega Psi must have manage_roles permissions.",
            "run_in_private": False,
            "server_moderator_only": True,
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
            }
        })

        self._removeRole = Command(commandDict = {
            "alternatives": ["removeRole"],
            "info": "Removes a role from the server.",
            "restriction_info": "You and Omega Psi must have manage_roles permissions.",
            "run_in_private": False,
            "server_moderator_only": True,
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
            }
        })

        self._kickMember = Command(commandDict = {
            "alternatives": ["kickMember", "kickMbr"],
            "info": "Kicks a member, or members, from the server.",
            "restriction_info": "You and Omega Psi must have kick_members permissions.",
            "run_in_private": False,
            "server_moderator_only": True,
            "parameters": {
                "member(s)...": {
                    "info": "The member(s) to kick.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to kick a member, or members, you need to mention them."
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
            }
        })

        self._banMember = Command(commandDict = {
            "alternatives": ["banMember", "banMbr"],
            "info": "Bans a member, or members, from the server.",
            "restriction_info": "You and Omega Psi must have ban_members permissions.",
            "run_in_private": False,
            "server_moderator_only": True,
            "parameters": {
                "member(s)...": {
                    "info": "The member(s) to ban.",
                    "optional": False
                }
            },
            "errors": {
                Category.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to ban a member, or members, you need to mention them."
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
            }
        })

        self._addMemberRole = Command(commandDict = {
            "alternatives": ["addMemberRole", "addMbrRole", "giveRole"],
            "info": "Gives a member the mentioned role(s).",
            "restriction_info": "You and Omega Psi must have manage_roles permissions.",
            "run_in_private": False,
            "server_moderator_only": True,
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
            }
        })

        self._removeMemberRole = Command(commandDict = {
            "alternatives": ["removeMemberRole", "removeMbrRole", "takeRole"],
            "info": "Removes the mentioned role(s) from a member.",
            "restriction_info": "You and Omega Psi must have manage_roles permissions.",
            "run_in_private": False,
            "server_moderator_only": True,
            "parameters": {
                "member": {
                    "info": "The member to take the roles from.",
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
            }
        })

        self._setMemberRoles = Command(commandDict = {
            "alternatives": ["setMemberRoles", "setMbrRoles", "setRoles"],
            "info": "Sets the roles for a member.",
            "restriction_info": "You and Omega Psi must have manage_roles permissions.",
            "run_in_private": False,
            "server_moderator_only": True,
            "parameters": {
                "member": {
                    "info": "The member to set the roles of.",
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
            }
        })

        self.setCommands([

            # Server Commands
            self._addMember,
            self._removeMember,
            self._addModerator,
            self._removeModerator,
            self._activate,
            self._deactivate,
            self._toggleRanking,
            self._toggleJoinMessage,
            self._setJoinMessageChannel,
            self._setLevel,
            self._addPrefix,
            self._removePrefix,

            # Bot Commands
            self._setServerName,
            self._createInvite,
            self._addRole,
            self._removeRole,
            self._kickMember,
            self._banMember,
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
            "Rank": Rank(None),
            "Misc": Misc(None)
        }
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods (Bot Commands)
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def addMember(self, discordServer, members):
        """Manually adds members mentioned to the specified Discord Server.\n

        discordServer - The Discord Server to manually add members to.\n
        members - The list of members to add.\n
        """

        # Iterate through each member
        result = ""
        for member in members:
            result += member.mention + (
                " was successfully added."
            ) if Server.updateMember(discordServer, member, Server.ADD_MEMBER) else (
                " already existed in files."
            )
        
        return discord.Embed(
            name = "Added Members",
            description = result,
            colour = ServerModerator.EMBED_COLOR
        )
    
    def removeMember(self, discordServer, members):
        """Manually removes members mentioned from the specified Discord Server.\n

        discordServer - The Discord Server to manually remove members from.\n
        members - The list of members to remove.\n
        """

        # Iterate through each member
        result = ""
        for member in members:
            result += member.mention + (
                " was successfully removed."
            ) if Server.removeMember(discordServer, member) else (
                " didn't exist in files."
            )
        
        return discord.Embed(
            name = "Removed Members",
            description = result,
            colour = ServerModerator.EMBED_COLOR
        )
    
    def addModerator(self, discordServer, members):
        """Manually adds moderators mentioned to the specified Discord Server.\n

        discordServer - The Discord Server to manually add moderators to.\n
        members - The list of moderators to add.\n
        """

        # Iterate through each member
        result = ""
        for member in members:
            result += member.mention + (
                " was successfully added as a moderator."
            ) if Server.addModerator(discordServer, member) else (
                " is already a moderator."
            )
        
        return discord.Embed(
            name = "Added Moderators",
            description = result,
            colour = ServerModerator.EMBED_COLOR
        )

    def removeModerator(self, discordServer, members):
        """Manually removes moderators mentioned from the specified Discord Server.\n

        discordServer - The Discord Server to manually remove moderators from.\n
        members - The list of moderators to remove.\n
        """

        # Iterate through each member
        result = ""
        for member in members:
            removeModInfo = Server.removeModerator(discordServer, member)
            result += removeModInfo["message"]
        
        return discord.Embed(
            name = "Removed Moderators",
            description = result,
            colour = ServerModerator.EMBED_COLOR
        )
    
    def activate(self, discordServer, commands):
        """Activates commands in the specified Discord Server.\n

        discordServer - The Discord Server to activate commands in.\n
        commands - The commands to activate.\n
        """
        
        # Open server file
        server = Server.openServer(discordServer)

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
                        commandObject.getAlternatives()[0]
                    )
                else:
                    result += "`{}` is already active.\n".format(
                        commandObject.getAlternatives()[0]
                    )
        
        # Activate all inactive commands
        else:
            result = ""
            for command in server["inactive_commands"]:
                result += "`{}` was activated.\n".format(command)
            server["inactive_commands"] = {}
        
        # Close server file
        Server.closeServer(server)
        
        return discord.Embed(
            name = "Activated",
            description = result,
            colour = ServerModerator.EMBED_COLOR
        )
    
    def deactivate(self, discordServer, command, reason = None):
        """Deactivates a command in the specified Discord Server.\n

        discordServer - The Discord Server to deactivate a command in.\n
        command - The command to deactivate.\n
        reason - The reason the command is being deactivated.\n
        """
        
        # Open server file
        server = Server.openServer(discordServer)

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
        Server.closeServer(server)

        return discord.Embed(
            name = "Deactivated",
            description = result,
            colour = ServerModerator.EMBED_COLOR
        )
    
    def toggleRanking(self, discordServer):
        """Toggles the ranking system in the specified Discord Server.\n

        discordServer - The Discord Server to toggle the ranking system in.\n
        """

        # Toggle ranking
        Server.toggleRanking(discordServer)

        if Server.isRankingActive(discordServer):
            result = "Ranking has been activated."
        else:
            result = "Ranking has been deactivated."
        
        return discord.Embed(
            name = "Ranking",
            description = result,
            colour = ServerModerator.EMBED_COLOR
        )
    
    def toggleJoinMessage(self, discordServer):
        """Toggles the join messaging in the specified Discord Server.\n

        discordServer - The Discord Server to toggle the join messaging in.\n
        """

        # Toggle join message
        Server.toggleJoinMessage(discordServer)

        if Server.isJoinMessageActive(discordServer):
            result = "The join message has been activated."
        else:
            result = "The join message has been deactivated."
        
        return discord.Embed(
            name = "Join Message",
            description = result,
            colour = ServerModerator.EMBED_COLOR
        )
    
    def setJoinMessageChannel(self, discordServer, discordChannel):
        """Sets the channel that the join message is sent to.\n

        discordServer - The Discord Server to set the channel of the join message.\n
        discordChannel - The Discord Channel to set where the join messages are sent to.\n
        """

        success = Server.setJoinMessageChannel(discordServer, discordChannel)

        return discord.Embed(
            title = "Channel {} Set".format(
                "Was" if success else "Was Not"
            ),
            description = "{} {} the join message channel.".format(
                discordChannel.mention,
                "was set as" if success else "is already"
            )
        )
    
    def getJoinMessage(self, discordServer):
        """Returns the info of join message in the specified Discord Server.\n

        discordServer - The Discord Server to get the channel of the join messages.\n
        """

        return discord.Embed(
            title = "Join Message",
            description = "{}\n<#{}>".format(
                "Active" if Server.isJoinMessageActive(discordServer) else "Inactive",
                Server.getJoinMessageChannel(discordServer)
            ),
            colour = ServerModerator.EMBED_COLOR
        )
    
    def setLevel(self, discordServer, level, members):
        """Sets the level of a member, or members, in the Discord Server.\n

        discordServer - The Discord Server to set member's levels in.\n
        level - The level to set.\n
        members - The members to set the level of.\n
        """

        # See if the level is an integer
        try:
            level = int(level)
        
        # Level is not an integer, return an error
        except:
            return getErrorMessage(self._setLevel, ServerModerator.INVALID_LEVEL)
        
        # Set the level of each member
        result = ""
        for member in members:
            result += Server.setLevel(discordServer, member, level) + "\n"
        
        return discord.Embed(
            name = "Result",
            description = result,
            colour = ServerModerator.EMBED_COLOR
        )
    
    def addPrefix(self, discordServer, prefixes):
        """Adds a prefix to the specified Discord Server.\n

        discordServer - The Discord Server to add the prefix to.\n
        prefixes - The prefix(es) to add.\n
        """

        # Iterate through the prefixes
        addPrefixes = ""
        addCount = 0
        for prefix in prefixes:
            temp = Server.addPrefix(discordServer, prefix)
            addPrefixes += temp["message"]
            addCount += temp["success_int"]
        
        return discord.Embed(
            title = "Prefix{} {} added.".format(
                "es" if addCount > 1 else "",
                "not" if addCount == 0 else ""
            ),
            description = addPrefixes if addCount > 0 else "No prefixes were added.",
            colour = ServerModerator.EMBED_COLOR
        )
    
    def removePrefix(self, discordServer, prefixes):
        """Removes a prefix from the specified Discord Server.\n

        discordServer - The Discord Server to remove the prefix from.\n
        prefixes - The prefix(es) to remove.\n
        """

        # No prefixes in list; Reset prefixes to default prefix
        if len(prefixes) == 0:
            Server.resetPrefixes(discordServer)

            return discord.Embed(
                title = "Prefixes Reset",
                description = "All prefixes have been removed and the default has been set.",
                colour = ServerModerator.EMBED_COLOR
            )
        
        # Prefixes are in list
        else:

            # Iterate through prefixes
            removePrefixes = ""
            removeCount = 0
            for prefix in prefixes:
                temp = Server.removePrefix(discordServer, prefix)
                removePrefixes += temp["message"]
                removeCount += temp["success_int"]
            
            return discord.Embed(
                title = "Prefix{} {} removed.".format(
                    "es" if removeCount > 1 else ""
                    "not" if removeCount == 0 else ""
                ),
                description = removePrefixes if removeCount > 0 else "No prefixes were removed.",
                colour = ServerModerator.EMBED_COLOR
            )
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods (Server Commands)
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def setServerName(self, author, discordServer, name):
        """Sets the name of the Discord Server.\n

        discordServer - The Discord Server to set the name of.\n
        name - The name to set.\n
        """

        # Only run if bot and author has permissions
        if author.top_role.permissions.manage_guild:
            try:

                # Get old name and set new name of server
                oldName = discordServer.name
                await discordServer.edit(
                    name = name
                )

                return discord.Embed(
                    title = "Changed Name",
                    description = "{} was changed to {}".format(
                        oldName, name
                    )
                )
            
            # Bot does not have permission
            except discord.Forbidden:
                return getErrorMessage(self._setServerName, ServerModerator.BOT_MISSING_PERMISSION)
        
        # Author does not have permission
        return getErrorMessage(self._setServerName, ServerModerator.MEMBER_MISSING_PERMISSION)
    
    async def createInvite(self, author, discordChannel, infinite):
        """Creates an Instant Invite for the Discord Server.\n
        
        discordChannel - The Discord Channel to create an Instant Invite for.\n
        infinite - Whether or not the invite expires.\n
        """

        # Only run if bot and author has permissions
        if author.top_role.permissions.create_instant_invite:
            try:

                # Create the invite
                infinite = infinite in self._createInvite.getAcceptedParameter("infinite", "True").getAlternatives()
                invite = await discordChannel.create_invite(
                    max_age = 0 if infinite else ServerModerator.MAX_INVITE_AGE
                )

                return str(invite)
            
            # Bot does not have permission
            except discord.Forbidden:
                return getErrorMessage(self._createInvite, ServerModerator.BOT_MISSING_PERMISSION)
        
        # Author does not have permission
        return getErrorMessage(self._createInvite, ServerModerator.MEMBER_MISSING_PERMISSION)
    
    async def addRole(self, author, discordServer, roleName, colorHex):
        """Adds a role to the specified Discord Server.\n

        author - The Discord Member who ran the command.\n
        discordServer - The Discord Server to add the Role to.\n
        roleName - The name of the Role to add.\n
        colorHex - The hex code of the color to set for the role.\n
        """

        # Only run if bot and author have permissions
        if author.top_role.permissions.manage_roles:
            try:

                # Try to set role color from hex
                try:
                    color = discord.Color(eval(colorHex))
                
                # Evaluation failed; Invalid color
                except:
                    return getErrorMessage(self._addRole, ServerModerator.INVALID_COLOR)

                # Create role
                role = await discordServer.create_role(
                    name = roleName,
                    hoist = True,
                    colour = color
                )

                # Bot had permission; Return success message
                return discord.Embed(
                    name = "Role Added",
                    description = "The role {} was added.".format(role.mention),
                    colour = ServerModerator.EMBED_COLOR
                )

            # Bot does not have permission
            except discord.Forbidden:
                return getErrorMessage(self._addRole, ServerModerator.BOT_MISSING_PERMISSION)
        
        # Author does not have permission
        return getErrorMessage(self._addRole, ServerModerator.MEMBER_MISSING_PERMISSION)
    
    async def removeRole(self, author, discordServer, role):
        """Removes a role from the specified Discord Server.\n

        discordServer - The Discord Server to remove the role from.\n
        role - The role to remove. Can either be a role name or a Discord Role.\n
        """

        # Only run if bot and author have permissions
        if author.top_role.permissions.manage_roles:
            try:

                # Role is not a Discord Role
                if type(role) == str:

                    # Search through member roles
                    for discordRole in discordServer.roles:
                        if discordRole.name == role:
                            role = discordRole
                            break
                
                # Remove the role
                await discordRole.delete()

                return discord.Embed(
                    name = "Role Deleted",
                    description = "The role {} was removed.".format(role.mention),
                    colour = ServerModerator.EMBED_COLOR
                )

            # Bot does not have permission
            except discord.Forbidden:
                return getErrorMessage(self._removeRole, ServerModerator.BOT_MISSING_PERMISSION)
        
        # Author does not have permission
        return getErrorMessage(self._removeRole, ServerModerator.MEMBER_MISSING_PERMISSION)

    async def kickMember(self, author, discordServer, discordMember):
        """Kicks the specified Discord Member from the Discord Server.\n

        discordServer - The Discord Server to kick the member from.\n
        discordMember - The Discord Member to kick.\n
        """

        # Only run if bot and author have permissions
        if author.top_role.permissions.kick_members:
            try:

                # Kick the member
                await discordServer.kick(discordMember)

                return discord.Embed(
                    title = "Member Kicked",
                    description = "{} ({}) was kicked from the server.".format(discordMember.name, discordMember.mention),
                    colour = ServerModerator.EMBED_COLOR
                )

            # Bot does not have permission
            except discord.Forbidden:
                return getErrorMessage(self._kickMember, ServerModerator.BOT_MISSING_PERMISSION)
        
        # Author does not have permission
        return getErrorMessage(self._kickMember, ServerModerator.MEMBER_MISSING_PERMISSION)

    async def banMember(self, author, discordServer, discordMember):
        """Bans the specified Discord Member from the Discord Server.\n

        discordServer - The Discord Server to ban the member from.\n
        discordMember - The Discord Member to ban.\n
        """

        # Only run if bot and author have permissions
        if author.top_role.permissions.ban_members:
            try:

                # Ban the member
                await discordServer.ban(discordMember)

                return discord.Embed(
                    title = "Member Banned",
                    description = "{} ({}) was banned from the server.".format(discordMember.name, discordMember.mention),
                    colour = ServerModerator.EMBED_COLOR
                )

            # Bot does not have permission
            except discord.Forbidden:
                return getErrorMessage(self._banMember, ServerModerator.BOT_MISSING_PERMISSION)
        
        # Author does not have permission
        return getErrorMessage(self._banMember, ServerModerator.MEMBER_MISSING_PERMISSION)
    
    async def addMemberRole(self, author, discordMember, discordRoles):
        """Adds the Discord Roles to the Discord Member.\n

        discordMember - The Discord Member to add the roles to.\n
        discordRoles - The Discord Roles to add.\n
        """

        # Only run if bot and author have permissions
        if author.top_role.permissions.manage_roles:
            try:

                # Add the roles to the member
                await discordMember.add_roles(discordRoles)

                # Keep track of added roles and current roles
                roles = {
                    "Added Roles": [],
                    "Current Roles": []
                }

                embed = discord.Embed(
                    title = "Roles Added",
                    description = "{} was given the following roles:\n".format(discordMember),
                    colour = ServerModerator.EMBED_COLOR
                )

                # Add roles based off of role type
                for roleType in roles:
                    if roleType == "Added Roles":
                        rolesType = discordRoles
                    else:
                        rolesType = discordMember.roles
                    
                    # Setup field text for fields
                    fieldText = ""
                    for role in rolesType:

                        discordRole = "{}\n".format(role.mention)

                        if len(fieldText) + len(discordRole) >= Server.MESSAGE_THRESHOLD:
                            roles[roleType].append(fieldText)
                            fieldText = ""
                        
                        fieldText += discordRole
                    
                    # Add trailing field text
                    if len(fieldText) > 0:
                        roles[roleType].append(fieldText)
                    
                    # Add fields to embed field
                    count = 0
                    for field in roles[roleType]:
                        count += 1
                        embed.add_field(
                            name = roleType + (
                                "({} / {})".format(
                                    count, len(roles[roleType])
                                ) if len(roles[roleType]) > 1 else ""
                            ),
                            field = field,
                            inline = False
                        )

                return embed

            # Bot does not have permission
            except discord.Forbidden:
                return getErrorMessage(self._addMemberRoles, ServerModerator.BOT_MISSING_PERMISSION)
        
        # Author does not have permission
        return getErrorMessage(self._addMemberRoles, ServerModerator.MEMBER_MISSING_PERMISSION)
    
    async def removeMemberRoles(self, author, discordMember, discordRoles):
        """Removes the Discord Roles from the Discord Member.\n

        discordMember - The Discord Member to remove roles from.\n
        discordRoles - The Discord Roles to remove.\n
        """

        # Only run if bot and author have permissions
        if author.top_role.permissions.manage_roles:
            try:

                # Remove the roles from the member
                await discordMember.remove_roles(discordRoles)

                # Keep track of roles removed and current roles
                roles = {
                    "Removed Roles": [],
                    "Current Roles": []
                }

                embed = discord.Embed(
                    title = "Roles Removed",
                    description = "{} had the following roles removed.".format(discordMember.name),
                    colour = ServerModerator.EMBED_COLOR
                )

                # Add roles based off of role type
                for roleType in roles:
                    if roleType == "Removed Roles":
                        rolesType = discordRoles
                    else:
                        rolesType = discordMember.roles
                    
                    # Setup field text for fields
                    fieldText = ""
                    for role in rolesType:

                        discordRole = "{}\n".format(role.mention)

                        if len(fieldText) + len(discordRole) >= Server.MESSAGE_THRESHOLD:
                            roles[roleType].append(fieldText)
                            fieldText = ""
                        
                        fieldText += discordRole
                    
                    # Add trailing field text
                    if len(fieldText) > 0:
                        roles[roleType].append(fieldText)
                    
                    # Add fields to embed field
                    count = 0
                    for field in roles[roleType]:
                        count += 1
                        embed.add_field(
                            name = roleType + (
                                "({} / {})".format(
                                    count, len(roles[roleType])
                                ) if len(roles[roleType]) > 1 else ""
                            ),
                            field = field,
                            inline = False
                        )

                return embed

            # Bot does not have permission
            except discord.Forbidden:
                return getErrorMessage(self._removeMemberRoles, ServerModerator.BOT_MISSING_PERMISSION)
        
        # Author does not have permission
        return getErrorMessage(self._removeMemberRoles, ServerModerator.MEMBER_MISSING_PERMISSION)
    
    async def setMemberRoles(self, author, discordMember, discordRoles):
        """Sets the Discord Roles to the Discord Member.\n

        discordMember - The Discord Member to set the Discord Roles of.\n
        discordRoles - The Discord Roles to set.\n
        """

        # Only run if bot and author have permissions
        if author.top_role.permissions.manage_roles:
            try:

                # Sets the roles of the member by removing and then adding the roles
                for role in discordMember.roles:
                    await role.delete()
                discordMember.add_roles(discordRoles)

                embed = discord.Embed(
                    title = "Roles Set",
                    description = "The roles of {} are now:".format(discordMember.name),
                    colour = ServerModerator.EMBED_COLOR
                )

                # Setup fields
                fields = []
                fieldText = ""
                for role in discordRoles:

                    discordRole = "<@{}>\n".format(role.name)

                    if len(fieldText) + len(discordRole) >= Server.MESSAGE_THRESHOLD:
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
                        name = "Current Roles {}".format(
                            "({} / {})".format(
                                count, len(fields)
                            ) if len(fields) > 0 else ""
                        ),
                        value = field,
                        inline = False
                    )
                
                return embed

            # Bot does not have permission
            except discord.Forbidden:
                return getErrorMessage(self._setMemberRoles, ServerModerator.BOT_MISSING_PERMISSION) 
        
        # Author does not have permission
        return getErrorMessage(self._setMemberRoles, ServerModerator.MEMBER_MISSING_PERMISSION)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Parsing
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def on_message(self, message):
        """Parses a message and runs a Server Moderator Category command if it can.\n

        message - The Discord Message to parse.\n
        """

        # Make sure message starts with the prefix
        if Server.startsWithPrefix(message.guild, message.content) and not message.author.bot:

            # Split up into command and parameters if possible
            command, parameters = Category.parseText(Server.getPrefixes(message.guild), message.content)

            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # Bot Commands
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            # Add Member Command
            if command in self._addMember.getAlternatives():

                # 0 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._addMember, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 1 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._addMember, self.addMember, message.guild, message.mentions)
                    )
                
            # Remove Member Command
            elif command in self._removeMember.getAlternatives():

                # 0 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._removeMember, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 1 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._removeMember, self.removeMember, message.guild, message.mentions)
                    )
                
            # Add Moderator Command
            elif command in self._addModerator.getAlternatives():

                # 0 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._addModerator, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 1 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._addModerator, self.addModerator, message.guild, message.mentions)
                    )
            
            # Remove Moderator Command
            elif command in self._removeModerator.getAlternatives():

                # 0 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._removeModerator, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 1 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._removeModerator, self.removeModerator, message.guild, message.mentions)
                    )
            
            # Activate Command
            elif command in self._activate.getAlternatives():

                # If parameters are empty, it will activate all inactive commands
                await sendMessage(
                    self.client,
                    message,
                    embed = await run(message, self._activate, self.activate, message.guild, parameters)
                )
            
            # Deactivate Command
            elif command in self._deactivate.getAlternatives():

                # 0 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._deactivate, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 1 or 2 Parameters Exist
                elif len(parameters) in [1, 2]:

                    reason = None
                    if len(parameters) == 2:
                        reason = parameters[1]

                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._deactivate, self.deactivate, message.guild, parameters[0], reason)
                    )
                
                # 3 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message, embed = getErrorMessage(self._deactivate, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Toggle Ranking Command
            elif command in self._toggleRanking.getAlternatives():

                # 0 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._toggleRanking, self.toggleRanking, message.guild)
                    )
                
                # 1 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._toggleRanking, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Toggle Join Message Command
            elif command in self._toggleJoinMessage.getAlternatives():

                # 0 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._toggleJoinMessage, self.toggleJoinMessage, message.guild)
                    )
                
                # 1 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._toggleJoinMessage, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Set Join Message Channel Command
            elif command in self._setJoinMessageChannel.getAlternatives():

                # 0 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._setJoinMessageChannel, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 1 Parameter Exists
                elif len(parameters) == 1:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._setJoinMessageChannel, self.setJoinMessageChannel, message.guild, message.channel_mentions[0])
                    )
                
                # 2 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._setJoinMessageChannel, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Set Level Command
            elif command in self._setLevel.getAlternatives():

                # Less than 2 Parameters Exist
                if len(parameters) < 2:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._setLevel, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 2 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._setLevel, self.setLevel, message.guild, parameters[0], message.mentions)
                    )
            
            # Add Prefix Command
            elif command in self._addPrefix.getAlternatives():

                # 0 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._addPrefix, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 1 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._addPrefix, self.addPrefix, message.guild, parameters)
                    )
                
            # Remove Prefix Command
            elif command in self._removePrefix.getAlternatives():
                await sendMessage(
                    self.client,
                    message,
                    embed = await run(message, self._removePrefix, self.removePrefix, message.guild, parameters)
                )
            
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
            # Server Commands
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            # Set Server Name Command
            elif command in self._setServerName.getAlternatives():

                # No Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._setServerName, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 1 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._setServerName, self.setServerName, message.author, message.guild, " ".join(parameters))
                    )
            
            # Create Invite Command
            elif command in self._createInvite.getAlternatives():

                # 0 or 1 Parameters Exist
                if len(parameters) in [0, 1]:
                    result = await run(message, self._createInvite, self.createInvite, message.author, message.channel, " ".join(parameters))

                    if type(result) == discord.Embed:
                        await sendMessage(
                            self.client,
                            message,
                            embed = result
                        )
                    
                    else:
                        await sendMessage(
                            self.client,
                            message,
                            message = result
                        )
                
                # 2 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._createInvite, Category.TOO_MANY_PARAMETERS)
                    )
                
            # Add Roles Command
            elif command in self._addRole.getAlternatives():

                # No Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._addRole, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 1 or 2 Parameters Exist
                elif len(parameters) in [1, 2]:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._addRole, self.addRole, message.author, message.guild, parameters[0], parameters[1])
                    )
                
                # More than 2 Parametes Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._addRole, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Remove Role Command
            elif command in self._removeRole.getAlternatives():

                # No Role was mentioned
                if len(message.role_mentions) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._removeRole, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # A role was mentioned
                elif len(message.role_mentions) == 1:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._removeRole, self.removeRole, message.author, message.guild, message.role_mentions[0])
                    )
                
                # More than 1 role was mentioned
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._removeRole, Category.TOO_MANY_PARAMETERS)
                    )
            
            # Kick Member Command
            elif command in self._kickMember.getAlternatives():

                # No member was mentioned
                if len(message.mentions) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._kickMember, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # Members were mentioned
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._kickMember, self.kickMember, message.author, message.guild, message.mentions)
                    )

            # Ban Member Command
            elif command in self._banMember.getAlternatives():
                
                # No member was mentioned
                if len(message.mentions) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._banMember, Category.NOT_ENOUGH_PARAMETERS)
                    )
                
                # Members were mentioned
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._banMember, self.banMember, message.author, message.guild, message.mentions)
                    )
        
            # Add Member Role Command
            elif command in self._addMemberRole.getAlternatives():
                
                # No member was mentioned
                if len(message.mentions) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._addMemberRole, ServerModerator.NO_MEMBER)
                    )
                
                # No roles were mentioned
                elif len(message.role_mentions) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._addMemberRole, ServerModerator.NO_ROLES)
                    )
                
                # A member and a role were mentioned
                elif len(message.mentions) == 1 and len(message.role_mentions) > 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._addMemberRole, self.addMemberRole, message.author, message.mentions[0], message.role_mentions)
                    )
                
                # More than 1 member was mentioned
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._addMemberRole, ServerModerator.TOO_MANY_MEMBERS)
                    )

            # Remove Member Role Command
            elif command in self._removeMemberRole.getAlternatives():
                
                # No member was mentioned
                if len(message.mentions) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._removeMemberRole, ServerModerator.NO_MEMBER)
                    )
                
                # No roles were mentioned
                elif len(message.role_mentions) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._removeMemberRole, ServerModerator.NO_ROLES)
                    )
                
                # A member and a role were mentioned
                elif len(message.mentions) == 1 and len(message.role_mentions) > 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._removeMemberRole, self.removeMemberRole, message.author, message.mentions[0], message.role_mentions)
                    )
                
                # More than 1 member was mentioned
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._removeMemberRole, ServerModerator.TOO_MANY_MEMBERS)
                    )

            # Set Member Roles Command
            elif command in self._setMemberRoles.getAlternatives():
                
                # No member was mentioned
                if len(message.mentions) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._setMemberRoles, ServerModerator.NO_MEMBER)
                    )
                
                # No roles were mentioned
                elif len(message.role_mentions) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._setMemberRoles, ServerModerator.NO_ROLES)
                    )
                
                # A member and a role were mentioned
                elif len(message.mentions) == 1 and len(message.role_mentions) > 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._setMemberRoles, self.setMemberRoles, message.author, message.mentions[0], message.role_mentions)
                    )
                
                # More than 1 member was mentioned
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._setMemberRoles, ServerModerator.TOO_MANY_MEMBERS)
                    )

def setup(client):
    client.add_cog(ServerModerator(client))
