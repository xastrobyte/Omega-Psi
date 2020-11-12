from discord import Embed, Member, Status
from discord.ext.commands import Cog, command, group, Greedy
from typing import Union

from cogs.errors import get_error_message, NotAGuildManager, NotInGuild, NOT_A_GUILD_MANAGER_ERROR, NOT_IN_GUILD_ERROR
from cogs.predicates import guild_only, guild_manager

from util.database.database import database

from util.functions import get_embed_color, create_fields
from util.string import datetime_to_string


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class Server(Cog, name="server"):
    """Commands that pertain to server management or user management will show up here :)"""

    def __init__(self, bot):
        self.bot = bot

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @command(
        name="guildInfo",
        aliases=["gi"],
        description="Gives you information about this server.",
        cog_name="server"
    )
    @guild_only()
    async def guild_info(self, ctx):
        """Allows a user to retrieve information from a guild

        :param ctx: The context of where the message was sent
        """

        # Create the fields for the guild data
        globally_disabled = await database.bot.get_disabled_commands()
        guild_disabled = await database.guilds.get_disabled_commands(ctx.guild)
        fields = {
            "Owner": ctx.guild.owner.mention,
            "Created At": datetime_to_string(ctx.guild.created_at),
            "Globally Disabled Commands": "\n".join([
                "`{}`".format(command)
                for command in globally_disabled
            ]) if len(globally_disabled) > 0 else "No Globally Disabled Commands",
            "Disabled Commands in this Guild": "\n".join([
                "`{}`".format(command)
                for command in guild_disabled
            ]) if len(guild_disabled) > 0 else "No Disabled Commands in this server",
            "Members": "{} Members\n{} Online\n{} Bots\n{} People".format(
                len(ctx.guild.members),
                len([member for member in ctx.guild.members if member.status == Status.online]),
                len([member for member in ctx.guild.members if member.bot]),
                len([member for member in ctx.guild.members if not member.bot])
            )
        }

        # Create the embed for the guild info
        embed = Embed(
            name="Guild Info",
            description="_ _",
            colour=await get_embed_color(ctx.author)
        ).set_footer(
            text="Server Name: {} | Server ID: {}".format(ctx.guild.name, ctx.guild.id)
        ).set_thumbnail(
            url=ctx.guild.icon_url
        )
        for field in fields:
            embed.add_field(
                name=field,
                value=fields[field]
            )

        # Create roles fields
        roles = create_fields(ctx.guild.roles[::-1], key=lambda role: role.mention, new_line=False)
        for i in range(len(roles)):
            embed.add_field(
                name="Roles {}".format(
                    "({} / {})".format(
                        i + 1, len(roles)
                    ) if len(roles) > 1 else ""
                ),
                value=roles[i],
                inline=False
            )

        await ctx.send(embed=embed)

    @command(
        name="userInfo",
        aliases=["ui"],
        description="Gives you info about a member in this guild.",
        cog_name="server"
    )
    @guild_only()
    async def user_info(self, ctx, *, user: Union[Member, str]=None):
        """Allows a user to retrieve info on a user or themselves

        :param ctx: The context of where the message was sent
        :param user: The user to get info on
        """

        # Check if getting info for specific user
        if user is not None:

            # Try to find user if not already converted to member
            if type(user) != Member:

                # Iterate through members
                found = False
                for member in ctx.guild.members:

                    # Get a list of possible aliases
                    check_list = [member.name.lower(), member.display_name.lower()]
                    if member.nick is not None:
                        check_list.append(member.nick.lower())

                    # See if the user is equivalent 
                    if user.lower() in check_list:
                        user = member
                        found = True
                        break

                # User was not found
                if not found:
                    user = None

        # Getting info for self
        else:
            user = ctx.author

        # Make sure user is not none
        if user is not None:

            # Send user data
            permissions = ", ".join([
                perm.replace("_", " ").title()
                for perm, has_perm in list(ctx.channel.permissions_for(user))
                if has_perm is True
            ]) if not ctx.channel.permissions_for(user).administrator else "Administrator"

            fields = {
                "Member": "{} ({}#{})".format(
                    user.mention,
                    user.name, user.discriminator
                ),
                "Created At": datetime_to_string(user.created_at),
                "Joined At": datetime_to_string(user.joined_at),
                "Permissions": permissions if len(permissions) > 0 else "None",
                "Status": str(user.status)
            }

            # Create embed
            embed = Embed(
                name="User Info",
                description=" ",
                colour=await get_embed_color(ctx.author)
            ).set_thumbnail(
                url=user.avatar_url
            ).set_footer(
                text="User Name: {} | User ID: {}".format(
                    "{}#{}".format(
                        user.name, user.discriminator
                    ),
                    user.id
                )
            )

            for field in fields:
                embed.add_field(
                    name=field,
                    value=fields[field],
                    inline=False
                )

            await ctx.send(
                embed=embed
            )

        # user is none
        else:
            await ctx.send(
                embed=get_error_message(
                    "There was no member found with that name."
                )
            )

    @command(
        name="prefix", aliases=["pre"],
        description="Changes the prefix for this server.",
        cog_name="server"
    )
    @guild_only()
    @guild_manager()
    async def prefix(self, ctx, *, prefix: str=None):
        """Allows a user to change the prefix for a server
        only if they're a guild manager

        :param ctx: The context of where the message was sent
        :param prefix: The prefix to change to
        """

        # Check if prefix is None (didn't enter it in)
        if prefix is None:
            await ctx.send(
                embed=get_error_message(
                    "You must clarify the new prefix!"
                )
            )

        # There is a prefix specified
        else:

            # Check if prefix ends with letter or digit
            if prefix[-1].isdigit() or prefix[-1].isalpha():
                prefix += " "

            # Change prefix for guild
            await database.guilds.set_prefix(ctx.guild, prefix)

            # Send message
            await ctx.send(
                embed=Embed(
                    title="Prefix Changed",
                    description=f"This server's prefix is now `{prefix}`",
                    colour=await get_embed_color(ctx.author)
                )
            )

    @command(
        name="enableCommand",
        description="Enables a specified command in this server.",
        cog_name="server"
    )
    @guild_only()
    @guild_manager()
    async def enable_command(self, ctx, cmd: str=None):
        """Allows a user to enable a command in the guild
        if they're a guild manager

        :param ctx: The context of where the message was sent
        :param cmd: The command to enable
        """

        # Check if there is no command to enable
        if not cmd:
            await ctx.send(
                embed=get_error_message("You need to specify the command to enable.")
            )

        # There is a command to enable
        else:

            # Check that it's a valid command in the bot
            cmd = self.bot.get_command(cmd)
            if not cmd:
                await ctx.send(
                    embed=get_error_message("That command does not exist!")
                )

            # The command is valid, enable it if possible
            else:
                enabled = await database.guilds.enable_command(ctx.guild, cmd.qualified_name)
                if not enabled:
                    await ctx.send(
                        embed=get_error_message("That command is already enabled!")
                    )

                else:
                    await ctx.send(
                        embed=Embed(
                            title="Command Enabled",
                            description="`{}` has been enabled".format(cmd.qualified_name),
                            colour=await get_embed_color(ctx.author)
                        )
                    )

    @command(
        name="disableCommand",
        description="Disables a specified command in this server.",
        cog_name="server"
    )
    @guild_only()
    @guild_manager()
    async def disable_command(self, ctx, cmd: str=None):
        """Allows a user to disable a command in the guild
        as long as they're a guild manager

        :param ctx: The context of where the message was sent
        :param cmd: The command to disable
        """

        # Check if there is no command to disable
        if not cmd:
            await ctx.send(
                embed=get_error_message("You need to specify the command to disable.")
            )

        # There is a command to disable
        else:

            # Check that it's a valid command in the bot
            cmd = self.bot.get_command(cmd)
            if not cmd:
                await ctx.send(
                    embed=get_error_message("That command does not exist!")
                )

            # The command is valid, disable it if possible
            else:
                disabled = await database.guilds.disable_command(ctx.guild, cmd.qualified_name)
                if not disabled:
                    await ctx.send(
                        embed=get_error_message("That command is already disabled!")
                    )

                else:
                    await ctx.send(
                        embed=Embed(
                            title="Command disabled",
                            description="`{}` has been disabled".format(cmd.qualified_name),
                            colour=await get_embed_color(ctx.author)
                        )
                    )

    @group(
        name="notify",
        description="Allows you to view or change your notification settings.",
        cog_name="server"
    )
    async def notify(self, ctx):
        """Allows a user to view or change notification settings

        :param ctx: The context of where the message was sent
        """
        if not ctx.invoked_subcommand:
            # Get all the user's notification data and put it into an embed
            notification_data = await database.users.get_notifications(ctx.author)
            await ctx.send(
                embed=Embed(
                    title="Notification Settings",
                    description="\n".join([
                        "**{}**: `{}`".format(
                            notification.replace("_", " ").title(),
                            "Active" if notification_data[notification]["active"] else "Inactive"
                        )
                        for notification in notification_data
                        if notification != "target"
                    ]),
                    colour=await get_embed_color(ctx.author)
                )
            )

    @notify.command(
        name="update",
        description="Toggles whether or not you want to receive update notifications.",
        cog_name="server"
    )
    async def notify_update(self, ctx):
        """Allows a user toggle their update notification settings

        :param ctx: The context of where the message was sent
        """

        # Toggle the user's update notifications and add/remove them from the bot updates
        activated = await database.users.toggle_update_notification(ctx.author)
        await database.bot.manage_notifications("update", ctx.author, activated)
        await ctx.send(
            embed=Embed(
                title="Update Notifications {}".format(
                    "Activated" if activated else "Deactivated"
                ),
                description="You will {} receive notifications when Omega Psi is updated".format(
                    "now" if activated else "not"
                ),
                colour=await get_embed_color(ctx.author)
            )
        )

    @notify.command(
        name="newFeature",
        aliases=["feature"],
        description="Toggles whether or not you want to receive new feature notifications.",
        cog_name="server"
    )
    async def notify_new_feature(self, ctx):
        """Allows a user toggle their new feature notification settings

        :param ctx: The context of where the message was sent
        """

        # Toggle the user's new feature notifications
        activated = await database.users.toggle_new_feature_notification(ctx.author)
        await database.bot.manage_notifications("new_feature", ctx.author, activated)
        await ctx.send(
            embed=Embed(
                title="New Feature Notifications {}".format(
                    "Activated" if activated else "Deactivated"
                ),
                description=(
                    "You will {} receive notifications when a new feature is " +
                    "added to a pending update in Omega Psi"
                ).format("now" if activated else "not"),
                colour=await get_embed_color(ctx.author)
            )
        )
    
    @notify.command(
        name="tasks",
        description="Toggles whether or not you want to receive notifications when a task is added or removed.",
        cog_name="server"
    )
    async def notify_tasks(self, ctx):
        """Allows a user to toggle their task notification settings

        :param ctx: The context of where the message was sent
        """

        # Toggle the user's task notifications
        activated = await database.users.toggle_tasks_notification(ctx.author)
        await database.bot.manage_notifications("tasks", ctx.author, activated)
        await ctx.send(
            embed=Embed(
                title = "Task Notifications {}".format(
                    "Activated" if activated else "Deactivated"
                ),
                description = "You will {} receive notifications when a task is added or removed by a developer".format(
                    "now" if activated else "not"
                ),
                colour=await get_embed_color(ctx.author)
            )
        )

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @prefix.error
    @guild_info.error
    @user_info.error
    async def error_handling(self, ctx, error):
        """Handles errors that pertain to guild manager erors

        :param ctx: The context of where the error occurred
        :param error: The error that occurred
        """

        # Check if the user who called the commands can't manage the guild
        if isinstance(error, NotAGuildManager):
            await ctx.send(embed=NOT_A_GUILD_MANAGER_ERROR)

        # Check if the command cannot run in a private message
        elif isinstance(error, NotInGuild):
            await ctx.send(embed=NOT_IN_GUILD_ERROR)


def setup(bot):
    """Add's this cog to the bot

    :param bot: The bot to add the cog to
    """
    bot.add_cog(Server(bot))
