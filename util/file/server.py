from util.file.omegaPsi import OmegaPsi

from datetime import datetime
from random import choice as choose

import discord, json, math, os

class Server:
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # File Sources
    SERVER_FILE = "data/servers/{}.json"
    XP_CARD_IMAGE = "util/rank/CARD_{}_{}.png"
    XP_ICON_SOURCE = "https://cdn.discordapp.com/avatars/{}/{}.png?size=1024"

    # Update Member Actions
    UPDATE_MEMBER = 0
    ADD_MEMBER = 1
    UPDATE_SERVER = 2

    # Errors
    INACTIVE = "INACTIVE"
    ACTIVE = "ACTIVE"
    NSFW_CHANNEL = "NSFW_CHANNEL"
    NO_ACCESS = "NO_ACCESS"
    NO_ACCESS_CATEGORY = "NO_ACCESS_CATEGORY"

    # Bot Invite / Misc
    EMBED_COLOR = 0x56A0B0
    BOT_INVITE = "https://discordapp.com/oauth2/authorize?scope=bot&client_id=503804826187071501&permissions={}"
    PERMISSIONS = {
        # General Permissions
        "administrator": 8,
        "viewAuditLog": 128,
        "manageServer": 32,
        "manageRoles": 268435456,
        "manageChannels": 16,
        "kickMembers": 2,
        "banMembers": 4,
        "createInstantInvite": 1,
        "changeNickname": 67108864,
        "manageNicknames": 134217728,
        "manageEmojis": 1073741824,
        "manageWebhooks": 536870912,
        "viewChannels": 1024,
        
        # Text Permissions
        "sendMessages": 2048,
        "sendTtsMessages": 4096,
        "manageMessages": 8192,
        "embedLinks": 16384,
        "attachFiles": 32768,
        "readMessageHistory": 65536,
        "mentionEveryone": 131072,
        "useExternalEmojis": 262144,
        "addReactions": 64,

        # Voice Permissions
        "connect": 1048576,
        "speak": 2097152,
        "muteMembers": 4194304,
        "deafenMembers": 8388608,
        "useMembers": 16777216,
        "useVoiceActivity": 33554432,
        "prioritySpeaker": 256
    }

    JOIN_MESSAGES = [
        "{} has joined this wonderful server!",
        "Let us all welcome {} to this server!",
        "Welcome {}!",
        "Hola {}! Thank you for joining!"
    ]

    # Member XP
    PROFANE_WORDS = [
        "asshole", "bastard", "bitch", "cock", "dick", "cunt", "pussy",
        "fuck", "shit", "chode", "choad", "wanker", "twat", "nigger", "nigga",
        "tits", "jizz", "dildo", "douche"
    ]

    INTERVAL = 5 # Message Send Interval
    NORMAL_XP = 3
    REACTION_XP = 6
    PROFANE_XP = 10

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Helper Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def openServer(discordServer):
        """Opens the file for the Discord Server given.\n

        discordServer - The Discord Server to load.\n
        """

        # Setup default values
        defaultValues = {
            "prefixes": [OmegaPsi.PREFIX],
            "id": discordServer.id,
            "ranking": False,
            "join_message": {
                "active": False,
                "channel": None,
                "messages": Server.JOIN_MESSAGES
            },
            "inactive_commands": {},
            "members": {}
        }

        # Try to open file
        try:

            # Check if servers folder exists
            if not os.path.exists("data/servers"):
                os.mkdir("data/servers")

            # Open file
            with open(Server.SERVER_FILE.format(discordServer.id), "r") as serverFile:
                tempFile = serverFile.read()
            serverDict = json.loads(tempFile)
            
            # See if default values are missing
            for value in defaultValues:

                # Check if value is not in server dictionary; Set default value
                if value not in serverDict:
                    serverDict[value] = defaultValues[value]
            
            return serverDict
            
        # File did not exist, create it
        except IOError:
            serverDict = defaultValues 
            Server.closeServer(serverDict)

            return Server.openServer(discordServer)
    
    def closeServer(serverDict):
        """Closes the file for the Discord Server.\n

        serverDict - The Discord Server to save.\n
        """

        # Open file
        with open(Server.SERVER_FILE.format(serverDict["id"]), "w") as serverFile:
            serverFile.write(json.dumps(serverDict, sort_keys = True, indent = 4))
    
    def getLevelFromExp(experience):
        """Returns the level that the given experience represents.\n

        experience - The amount of experience.\n

        The equation for the ranking system is: sqrt(x/10)\n
        """
        return int(math.sqrt(experience / 10))
    
    def getExpFromLevel(level):
        """Returns the amount of experience that the given level requires.\n

        level - The level.\n

        The equation for the ranking system is: 10x^2\n
        """
        return int(10 * level ** 2)
    
    def datetimeToDict(datetime):
        """Returns a dictionary representation of a datetime object

        datetime - The datetime object to retrieve the dictionary representation of 
        """
        return {
            "month": datetime.month, "day": datetime.day, "year": datetime.year,
            "hour": datetime.hour, "minute": datetime.minute, "second": datetime.second
        }

    def dictToDatetime(ddict):
        """Returns a datetime object from a dictionary representation

        ddict - The dictionary representation of the datetime object
        """
        return datetime(
            ddict["year"], ddict["month"], ddict["day"],
            ddict["hour"], ddict["minute"], ddict["second"]
        )
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def startsWithPrefix(discordServer, message):
        """Returns whether or not the message is a prefix for the specified Discord Server.\n

        discordServer - The Discord Server to get the prefixes for.\n
        message - The message to test.\n
        """

        # Get prefixes
        prefixes = Server.getPrefixes(discordServer)

        # See if message starts with any prefix
        for prefix in prefixes:
            if message.startswith(prefix):
                return True

        return False

    def getPrefixes(discordServer):
        """Returns the prefix for the specified Discord Server.\n

        discordServer - The Discord Server to get the prefix of.\n
        """

        # Make sure discordServer is not None
        if discordServer != None:

            # Open server file
            server = Server.openServer(discordServer)

            # Get prefixes; Add spaces to any that are only alphas
            prefixes = server["prefixes"]
            for prefix in range(len(prefixes)):
                if prefixes[prefix].isalpha() and not prefixes[prefix].endswith(" ") and len(prefixes[prefix]) > 1:
                    prefixes[prefix] += " "

            # Close server file
            Server.closeServer(server)

            return prefixes
        
        # Return default prefix
        return [OmegaPsi.PREFIX]
    
    def resetPrefixes(discordServer): 
        """Resest the prefixes in the specified Discord Server and sets it to the default.\n

        discordServer - The Discord Server to reset the prefixes of.\n
        """

        # Open server file
        server = Server.openServer(discordServer)

        # Remove all prefixes
        server["prefixes"] = [OmegaPsi.PREFIX]

        # Close server file
        Server.closeServer(server)
    
    def addPrefix(discordServer, prefix):
        """Adds a prefix to the specified Discord Server.\n

        discordServer - The Discord Server to add the prefix to.\n
        prefix - The prefix to add.\n
        """

        # Open server file
        server = Server.openServer(discordServer)
        
        # Only add if prefix does not already exist
        if prefix not in server["prefixes"]:
            server["prefixes"].append(prefix)
            successInt = 1
            successMessage = "`{}` was added as a prefix."
        else:
            successInt = 0
            successMessage = "`{}` could not be added as a prefix. It already exists."

        # Close server file
        Server.closeServer(server)

        return {"success_int": successInt, "message": successMessage.format(prefix) + "\n"}
    
    def removePrefix(discordServer, prefix):
        """Removes a prefix from the specified Discord Server.\n

        discordServer - The Discord Server to remove the prefix from.\n
        prefix - The prefix to remove.\n
        """

        # Open server file
        server = Server.openServer(discordServer)

        # Add space if it is an alpha prefix and len is greater than 1
        if len(prefix) > 1 and prefix.isalpha():
            prefix += " "

        # See if prefix is in the server prefixes
        if prefix in server["prefixes"]:

            if prefix == OmegaPsi.PREFIX:
                successInt = 0
                successMessage = "`{}` was not removed as a prefix. You cannot remove the default prefix."
            else:
                successInt = 1
                successMessage = "`{}` was removed as a prefix."
        
        else:
            successInt = 0
            successMessage = "`{}` was not a prefix."
        
        # Only remove if the successInt is 1
        if successInt == 1:
            server["prefixes"].remove(prefix)

        # Close server file
        Server.closeServer(server)

        return {"success_int": successInt, "message": successMessage.format(prefix) + "\n"}

    def updateMember(discordServer, discordMember, *, action = UPDATE_MEMBER):
        """Updates the Discord Member that belongs the Discord Server given.\n

        discordServer - The Discord Server to update the Discord Member in.\n
        discordMember - The Discord Member to update.\n

        If the Discord Member is not saved in the files,
        this method will automatically handle them being added.\n
        """

        # Setup default values
        defaultValues = {
            "id": discordMember.id,
            "moderator": False,
            "experience": 0,
            "level": 1,
            "last_message": Server.datetimeToDict(datetime.now())
        }

        # Open server file
        server = Server.openServer(discordServer)

        # Check if member is not in server file; Create empty dictionary
        addMemberSuccess = False
        if str(discordMember.id) not in server["members"]:
            server["members"][str(discordMember.id)] = {}
            addMemberSuccess = True

        # Iterate through keys in member dictionary
        member = server["members"][str(discordMember.id)]
        for value in defaultValues:

            # Check if value is not in member dictionary; Set default value
            if value not in member:
                member[value] = defaultValues[value]
        
        # Close server file
        Server.closeServer(server)

        if action == Server.ADD_MEMBER:
            return addMemberSuccess

    def removeMember(discordServer, discordMember):
        """Removes a Discord Member from a Discord Server.\n

        discordServer - The Discord Server to remove the Discord Member from.\n
        discordMember - The Discord Member to remove.\n
        """

        # Open server file
        server = Server.openServer(discordServer)

        # Check if member is in server
        success = False
        if str(discordMember.id) in server["members"]:
            server["members"].pop(str(discordMember.id))
            success = True
        
        # Close server file
        Server.closeServer(server)

        return success

    def activate(discordServer, commandObject):
        """Activates a Command in the Discord Server.\n

        discordServer - The Discord Server to activate the Command in.\n
        commandObject - The Command to activate.\n
        """

        # Open server file
        server = Server.openServer(discordServer)

        # Check if command is in inactive commands
        success = False
        if commandObject.getAlternatives()[0] in server["inactive_commands"]:
            server["inactive_commands"].pop(commandObject.getAlternatives()[0])
            success = True
        
        # Close server file
        Server.closeServer(server)

        return success
    
    def deactivate(discordServer, commandObject, reason):
        """Deactivates a Command in the Discord Server.\n

        discordServer - The Discord Server to deactivate the Command in.\n
        commandObject - The Command to deactivate.\n
        reason - The reason the Command is being deactivated.\n
        """

        # Open server file
        server = Server.openServer(discordServer)

        # Check if command is not in inactive commands
        success = False
        if commandObject.getAlternatives()[0] not in server["inactive_commands"]:
            server["inactive_commands"][commandObject.getAlternatives()[0]] = reason
            success = True
        
        # Close server file
        Server.closeServer(server)

        return success
    
    def toggleRanking(discordServer):
        """Toggles the ranking/leveling system in the Discord Server.\n

        discordServer - The Discord Server to toggle the ranking in.\n
        """

        # Open server file
        server = Server.openServer(discordServer)

        # Toggle the ranking system
        server["ranking"] = not server["ranking"]

        # Close server file
        Server.closeServer(server)

        return server["ranking"]
    
    def toggleJoinMessage(discordServer):
        """Toggles the message that the bot will say whenever someone new joins the Discord Server.\n

        discordServer - The Discord Server to toggle the join message in.\n
        """

        # Open server file
        server = Server.openServer(discordServer)

        # Toggle the join messaging
        server["join_message"]["active"] = not server["join_message"]["active"]

        # Close server file
        Server.closeServer(server)

        return server["join_message"]["active"]
    
    def setLevel(discordServer, discordMember, level):
        """Sets the ranking level of the Discord Member in the Discord Server.\n

        discordServer - The Discord Server to set the level of the Discord Member in.\n
        discordMember - The Discord Member to set the level of.\n
        level - The level to set.\n
        """

        # Open server file
        server = Server.openServer(discordServer)

        # Set level and experience
        server["members"][str(discordMember.id)]["level"] = level
        server["members"][str(discordMember.id)]["experience"] = Server.getExpFromLevel(level)

        # Close server file
        Server.closeServer(server)

        return "{} was set to Level {}".format(
            discordMember.name if discordMember.nick == None else discordMember.nick,
            level
        )
    
    def updateExperience(discordMessage):
        """Updates the experience for the Discord Member in the Discord Server given the Discord Message.\n

        discordMessage - The Discord Message to use in order to figure out how much experience is earned.\n
        """

        # Only run if message was sent in a server
        if discordMessage.guild != None:

            # Get the server and author the message was sent in
            discordServer = discordMessage.guild
            discordMember = discordMessage.author

            # Only run if ranking is active and message is not from a bot
            if Server.isRankingActive(discordServer) and not discordMember.bot:

                # Update member
                Server.updateMember(discordServer, discordMember)

                # Open server file
                server = Server.openServer(discordServer)

                # Update experience; Make sure last message was over the interval
                previous = Server.dictToDatetime(server["members"][str(discordMember.id)]["last_message"])
                current = datetime.now()
                difference = (current - previous).total_seconds()
                if difference >= Server.INTERVAL:

                    # Get amount of experience to add from discordMessage
                    message = discordMessage.content.lower()
                    totalExperience = Server.NORMAL_XP

                    # Check for profanity
                    profanityUsed = [profane for profane in Server.PROFANE_WORDS if profane in message]
                    totalExperience += Server.PROFANE_XP * len(profanityUsed)

                    # Update experience
                    server["members"][str(discordMember.id)]["experience"] += totalExperience

                    # Update last message
                    server["members"][str(discordMember.id)]["last_message"] = Server.datetimeToDict(current)
                
                # Update level
                message = Server.updateLevel(server, discordMember)

                # Close server file
                Server.closeServer(server)

                return message

        return None
    
    def updateLevel(serverDict, discordMember):
        """Updates the level for a member in a discord server.\n

        serverDict - The server dictionary to use for updating a member's level.\n
        discordMember - The Discord Member to update the level of.\n
        """

        # Get current experience, current level, and next level
        currentExperience = serverDict["members"][str(discordMember.id)]["experience"]
        currentLevel = serverDict["members"][str(discordMember.id)]["level"]
        nextLevel = Server.getLevelFromExp(currentExperience)

        # Check if next level is greater than current level
        if currentLevel < nextLevel:
            serverDict["members"][str(discordMember.id)]["level"] = nextLevel

            # Return a level up text
            return choose([
                "{} has leveled up to Level {}!",
                "{}: Level {}.",
                "Nice {}, you've leveled up to Level {}."
            ]).format(discordMember.mention, nextLevel)
        
        return None
    
    def getMember(discordServer, discordMember):
        """Returns the dictionary of the Discord Member in the Discord Server.\n

        discordServer - The Discord Server to use to get the Discord Member's dictionary.\n
        discordMember - The Discord Member to get the dictionary of.\n
        """

        # Update member if not in server
        Server.updateMember(discordServer, discordMember)

        # Open the server file
        server = Server.openServer(discordServer)

        # Get the members information
        member = server["members"][str(discordMember.id)]

        # Close the server file
        Server.closeServer(server)

        return member
    
    def isRankingActive(discordServer):
        """Returns whether or not the ranking system is active in the Discord Server.\n

        discordServer - The Discord Server to check if ranking is active.\n
        """

        # Open the server file
        server = Server.openServer(discordServer)

        # Get the ranking status
        active = server["ranking"]

        # Close the server file
        Server.closeServer(server)

        return active
    
    def isJoinMessageActive(discordServer):
        """Returns whether or not the join message is active in the Discord Server.\n

        discordServer - The Discord Server to check if the join message is active.\n
        """
        
        # Open the server file
        server = Server.openServer(discordServer)

        # Get the join message active status
        active = server["join_message"]["active"]

        # Close the server file
        Server.closeServer(server)
        
        return active
    
    def getJoinMessageChannel(discordServer):
        """Returns the channel that the join message is sent to.\n

        discordServer - The Discord Server to get the join message channel of.\n
        """

        # Open the server file
        server = Server.openServer(discordServer)

        # Get the join message channel
        channelId = server["join_message"]["channel"]

        # Close the server file
        Server.closeServer(server)

        return channelId
    
    def getJoinMessage(discordServer):
        """Returns a random join message for the server.
        """

        # Open the server file
        server = Server.openServer(discordServer)

        # Choose a join message
        if "messages" not in server["join_message"]:
            server["join_message"]["messages"] = Server.JOIN_MESSAGES
        message = choose(server["join_message"]["messages"])

        # Close the server file
        Server.closeServer(server)

        return message
    
    def setJoinMessageChannel(discordServer, discordChannel):
        """Sets the Discord Channel that join messages are sent to in a Discord Server.\n

        discordServer - The Discord Server that the join message channel is being set in.\n
        discordChannel - The Discord Channel that will be set as the join message channel.\n
        """

        # Open the server file
        server = Server.openServer(discordServer)

        # Set the join message channel
        success = False
        if discordChannel.id != server["join_message"]["channel"]:
            server["join_message"]["channel"] = discordChannel.id
            success = True
        
        # Close the server file
        Server.closeServer(server)

        return success
    
    def isAuthorModerator(discordServer, discordMember):
        """Returns whether or not the Discord Member is a moderator in the Discord Server.\n

        discordServer - The Discord Server to check if the Discord Member is a moderator in.\n
        discordMember - The Discord Member to check if they are a moderator.\n
        """

        return discordMember.guild_permissions.manage_guild
    
    def isCommandActive(discordServer, commandObject):
        """Returns whether or not the command given is active.\n

        discordServer - The Discord Server to check if the Command is active.\n
        commandObject - The Command to check if it's active.\n
        """
        
        # Open the server file
        server = Server.openServer(discordServer)

        # Check if command is in inactive_commands
        active = commandObject.getAlternatives()[0] not in server["inactive_commands"]

        # Close the server file
        Server.closeServer(server)

        return active
    
    def getDeactivatedReason(discordServer, commandObject):
        """Returns the reason the command given is inactive.\n

        discordServer - The Discord Server to check the Command's inactive reason in.\n
        commandObject - The Command to get the inactive reason for.\n

        If the command is active, it will return a message saying it's active.\n
        """
        
        # Check if command is active
        if Server.isCommandActive(discordServer, commandObject):
            return Server.getErrorMessage(Server.ACTIVE)
        
        # Command must be inactive, get the reason
        else:

            # Open the server file
            server = Server.openServer(discordServer)

            # Get reason of command's inactivity
            reason = server["inactive_commands"][commandObject.getAlternatives()[0]]

            # Close the server file
            Server.closeServer(server)

            return discord.Embed(
                title = commandObject.getAlternatives()[0],
                description = (
                    "{}\n" +
                    "Reason: {}"
                ).format(
                    Server.getErrorMessage(Server.INACTIVE),
                    reason
                ),
                colour = Server.EMBED_COLOR
            )
    
    def getErrorMessage(errorType):
        """Returns an error message based off the error type given.\n

        errorType - The type of error message to return.\n
        """

        # Keep a dictionary of errors and error messages
        errorMessages = {
            Server.NSFW_CHANNEL: [
                "You can only run NSFW commands in an NSFW channel."
            ],
            Server.INACTIVE: [
                "This command is inactive in this server right now."
            ],
            Server.ACTIVE: [
                "This command is already active in this server."
            ],
            Server.NO_ACCESS: [
                "You do not have access to this command in this server."
            ],
            Server.NO_ACCESS_CATEGORY: [
                "You do not have access to this category in this server."
            ]
        }

        error = choose(errorMessages[errorType])

        return discord.Embed(
            title = "Error",
            description = error,
            colour = Server.EMBED_COLOR
        )
    
    def getNSFWChannelError():
        return Server.getErrorMessage(Server.NSFW_CHANNEL)
    
    def getInactiveError():
        return Server.getErrorMessage(Server.INACTIVE)
    
    def getActiveError():
        return Server.getErrorMessage(Server.ACTIVE)
    
    def getNoAccessError():
        return Server.getErrorMessage(Server.NO_ACCESS)
    
    def getNoAccessCategory():
        return Server.getErrorMessage(Server.NO_ACCESS_CATEGORY)
