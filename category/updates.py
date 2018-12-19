from util.file.database import omegaPsi
from util.file.omegaPsi import OmegaPsi
from util.file.server import Server

from util.utils.discordUtils import sendMessage, getErrorMessage

from supercog import Command, Category
import discord

reactions = ["⏪", "⬅", "➡", "⏩"]

class Updates(Category):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Errors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Constructor
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, client):
        super().__init__(
            client, 
            "Updates",
            description = "Anything having to do with updates goes here.",
            embed_color = 0xFF8040,
            bot_mod_error = OmegaPsi.getNoAccessError,
            locally_inactive_error = Server.getInactiveError,
            globally_inactive_error = OmegaPsi.getInactiveError,
            locally_active_check = Server.isCommandActive,
            globally_active_check = OmegaPsi.isCommandActive,
            bot_mod_check = OmegaPsi.isAuthorModerator
        )

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        self._update = Command(commandDict = {
            "alternatives": ["update"],
            "info": "Gets information about the most recent update to the bot.",
            "errors": {
                Updates.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get information about the most recent update to the bot, you don't need any parameters."
                    ]
                }
            },
            "command": self.update
        })

        self._pendingUpdate = Command(commandDict = {
            "alternatives": ["pendingUpdate", "pendUpdate", "pendingUpd", "pendUpd"],
            "info": "Gets information about the current pending update to the bot.",
            "errors": {
                Updates.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get information about the current pending update to the bot, you don't need any parameters."
                    ]
                }
            },
            "command": self.pendingUpdate
        })

        self._createUpdate = Command(commandDict = {
            "alternatives": ["createUpdate"],
            "info": "Creates a pending update to the bot.",
            "bot_moderator_only": True,
            "parameters": {
                "version": {
                    "info": "The version of the bot.",
                    "optional": False
                }
            },
            "errors": {
                Updates.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to create a pending update, you need the version name/number."
                    ]
                }
            },
            "command": self.createUpdate
        })

        self._createFix = Command(commandDict = {
            "alternatives": ["createFix"],
            "info": "Creates a fix to a pending update of the bot.",
            "bot_moderator_only": True,
            "parameters": {
                "fix": {
                    "info": "The description of the fix to the bot.",
                    "optional": False
                }
            },
            "errors": {
                Updates.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to create a fix to the bot, you need the description of the fix."
                    ]
                }
            },
            "command": self.createFix
        })

        self._createFeature = Command(commandDict = {
            "alternatives": ["createFeature"],
            "info": "Creates a feature to a pending update of the bot.",
            "bot_moderator_only": True,
            "parameters": {
                "feature": {
                    "info": "The description of the feature added to the bot.",
                    "optional": False
                }
            },
            "errors": {
                Updates.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to create a feature added to the bot, you need the description of the feature."
                    ]
                }
            },
            "command": self.createFeature
        })

        self._commitUpdate = Command(commandDict = {
            "alternatives": ["commitUpdate", "commit"],
            "info": "Commits the pending update to the bot as an update.",
            "bot_moderator_only": True,
            "parameters": {
                "description": {
                    "info": "A short description of the update to the bot.",
                    "optional": False
                }
            },
            "errors": {
                Updates.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to commit an update to the bot, you need a short description."
                    ]
                }
            },
            "command": self.commitUpdate
        })

        self.setCommands([
            self._update,
            self._pendingUpdate,

            self._createUpdate,
            self._createFix,
            self._createFeature,
            self._commitUpdate
        ])

        self._scrollEmbeds = {}

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def update(self, message, parameters):
        """
        """
        success = True
        
        # Check for too many parameters
        if len(parameters) > self._update.getMaxParameters():
            embed = getErrorMessage(self._update, Updates.TOO_MANY_PARAMETERS)
            success = False
        
        # There were the proper amount of parameters
        else:

            # Get all updates
            updates = await omegaPsi.getUpdates()
            self._scrollEmbeds[str(message.author.id)] = {
                "embeds": updates,
                "min": 0,
                "max": len(updates) - 1,
                "value": 0
            }

            # Create a discord embed out of it
            recentUpdate = updates[0]
            embed = discord.Embed(
                title = "Most Recent Update - {}".format(recentUpdate["version"]),
                description = recentUpdate["description"],
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            )

            fields = {
                "Fixes": "No new fixes were made." if len(recentUpdate["fixes"]) == 0 else "\n".join(recentUpdate["fixes"]),
                "Features": "No new features were added." if len(recentUpdate["features"]) == 0 else "\n".join(recentUpdate["features"])
            }

            for field in fields:
                embed.add_field(
                    name = field,
                    value = fields[field],
                    inline = False
                )

        msg = await sendMessage(
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

        if success:
            for reaction in reactions:
                await msg.add_reaction(reaction)
            self._scrollEmbeds[str(message.author.id)]["message"] = msg

    async def pendingUpdate(self, message, parameters):
        """
        """
        
        # Check for too many parameters
        if len(parameters) > self._pendingUpdate.getMaxParameters():
            embed = getErrorMessage(self._pendingUpdate, Updates.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            
            # Get the current pending update
            pendingUpdate = await omegaPsi.getPendingUpdate()

            # Only show pending update if one exists
            if len(pendingUpdate) != 0:

                # Create a discord embed out of it
                embed = discord.Embed(
                    title = "Current Pending Update - {}".format(pendingUpdate["version"]),
                    description = " ",
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                )

                fields = {
                    "Pending Fixes": "No new fixes have been made yet." if len(pendingUpdate["fixes"]) == 0 else "\n".join(pendingUpdate["fixes"]),
                    "Pending Features": "No new features have been added yet." if len(pendingUpdate["features"]) == 0 else "\n".join(pendingUpdate["features"])
                }

                for field in fields:
                    embed.add_field(
                        name = field,
                        value = fields[field],
                        inline = False
                    )
            
            # No pending update exists yet
            else:
                embed = discord.Embed(
                    title = "No Pending Update Yet",
                    description = " ",
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

    async def createUpdate(self, message, parameters):
        """
        """

        # Check for not enough parameters
        if len(parameters) < self._createUpdate.getMinParameters():
            embed = getErrorMessage(self._createUpdate, Updates.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._createUpdate.getMaxParameters():
            embed = getErrorMessage(self._createUpdate, Updates.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            version = " ".join(parameters)

            await omegaPsi.createPendingUpdate(version)

            embed = discord.Embed(
                title = "Update Created",
                description = "A pending update was created with the version of {}".format(version),
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

    async def createFix(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._createFix.getMinParameters():
            embed = getErrorMessage(self._createFix, Updates.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            fix = " ".join(parameters)

            await omegaPsi.createFix(fix)

            embed = discord.Embed(
                title = "Created Fix",
                description = fix,
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

    async def createFeature(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._createFeature.getMinParameters():
            embed = getErrorMessage(self._createFeature, Updates.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            feature = " ".join(parameters)

            await omegaPsi.createFeature(feature)

            embed = discord.Embed(
                title = "Feature Created",
                description = feature,
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

    async def commitUpdate(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._commitUpdate.getMinParameters():
            embed = getErrorMessage(self._commitUpdate, Updates.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            description = " ".join(parameters)

            await omegaPsi.commitPendingUpdate(description)
            update = await omegaPsi.getUpdate()

            embed = discord.Embed(
                title = "Update was Committed - {}".format(update["version"]),
                description = description,
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            )

            fields = {
                "Fixes": "No new fixes were made." if len(update["fixes"]) == 0 else "\n".join(update["fixes"]),
                "Features": "No new features were added." if len(update["features"]) == 0 else "\n".join(update["features"])
            }

            for field in fields:
                embed.add_field(
                    name = field,
                    value = fields[field],
                    inline = False
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

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Parsing
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def on_message(self, message):
        """Parses a message and runs an Updates Category command if it can.\n

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
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Reactions
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def manage_scrolling(self, reaction, member):
        """Manages the scrolling of any scroll embeds
        """

        # Check for message ID in scrollable embeds
        memberId = str(member.id)
        if memberId in self._scrollEmbeds:
            initial = self._scrollEmbeds[memberId]["value"]

            # Rewind reaction was added; Move to first field
            if str(reaction) == "⏪":
                self._scrollEmbeds[memberId]["value"] = self._scrollEmbeds[memberId]["min"]
            
            # Fast Forward reaction was added; Move to last field
            elif str(reaction) == "⏩":
                self._scrollEmbeds[memberId]["value"] = self._scrollEmbeds[memberId]["max"]
            
            # Arrow Left reaction was added; Move field left
            elif str(reaction) == "⬅":
                self._scrollEmbeds[memberId]["value"] -= 1
                if self._scrollEmbeds[memberId]["value"] < self._scrollEmbeds[memberId]["min"]:
                    self._scrollEmbeds[memberId]["value"] = self._scrollEmbeds[memberId]["min"]
            
            # Arrow Right reaction was added; Move field right
            elif str(reaction) == "➡":
                self._scrollEmbeds[memberId]["value"] += 1
                if self._scrollEmbeds[memberId]["value"] > self._scrollEmbeds[memberId]["max"]:
                    self._scrollEmbeds[memberId]["value"] = self._scrollEmbeds[memberId]["max"]
            
            # Update the scroll embed
            if self._scrollEmbeds[memberId]["value"] != initial and reaction.message.id == self._scrollEmbeds[memberId]["message"].id:
                value = self._scrollEmbeds[memberId]["value"]

                # Get the update at the index of the value
                update = self._scrollEmbeds[memberId]["embeds"][value]

                # Create a discord embed out of it
                embed = discord.Embed(
                    title = "{} - {}".format(
                        "Most Recent Update" if value == 0 else "Previous Update",
                        update["version"]
                    ),
                    description = update["description"],
                    colour = self.getEmbedColor() if reaction.message.guild == None else member.top_role.color
                )

                fields = {
                    "Fixes": "No new fixes were made." if len(update["fixes"]) == 0 else "\n".join(update["fixes"]),
                    "Features": "No new features were added." if len(update["features"]) == 0 else "\n".join(update["features"])
                }

                for field in fields:
                    embed.add_field(
                        name = field,
                        value = fields[field],
                        inline = False
                    )

                # Update the embed
                await self._scrollEmbeds[str(member.id)]["message"].edit(
                    embed = embed
                )

    async def on_reaction_add(self, reaction, member):
        """Determines which reaction was added to a message. Only reactions right now are

        :arrow_left: which tells the embed to scroll back a field.
        :arrow_right: which tells the embed to scroll forward a field.
        :rewind: which tells the embed to go back to the beginning.
        :fast_forward: which tells the embed to go to the end.
        """
        await self.manage_scrolling(reaction, member)
    
    async def on_reaction_remove(self, reaction, member):
        """Determines which reaction was removed from a message. Only reactions right now are

        :arrow_left: which tells the embed to scroll back a field.
        :arrow_right: which tells the embed to scroll forward a field.
        :rewind: which tells the embed to go back to the beginning.
        :fast_forward: which tells the embed to go to the end.
        """
        await self.manage_scrolling(reaction, member)

def setup(client):
    client.add_cog(Updates(client))