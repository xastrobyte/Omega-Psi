from asyncio import wait, FIRST_COMPLETED
from discord import Embed, Status, Activity, Member
from discord.ext.commands import Cog, group, command
from os import environ, execv
from sys import executable, argv
from typing import Union

from cogs.errors import (
    NotADeveloper, NotAGuildManager, NotInGuild,
    NOT_A_DEVELOPER_ERROR, NOT_A_GUILD_MANAGER_ERROR, NOT_IN_GUILD_ERROR,
    get_error_message
)
from cogs.globals import FIRST_PAGE, LAST_PAGE, PREVIOUS_PAGE, NEXT_PAGE, LEAVE, SCROLL_REACTIONS
from cogs.globals import OMEGA_PSI_CREATION
from cogs.predicates import is_developer, guild_manager, guild_only

from util.database.database import database

from util.discord import send_webhook
from util.functions import get_embed_color, create_fields, add_fields, add_scroll_reactions
from util.string import datetime_to_string, datetime_to_length

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

WEBSITE = "🌐"
BOT = "🤖"

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class Bot(Cog, name = "bot"):
    """Primary bot-related commands like bugs and suggestions"""
    def __init__(self, bot):
        self.bot = bot

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @command(
        name = "bug", aliases = ["issue"],
        description = "Allows you to report a bug found in Omega Psi.",
        cog_name = "bot"
    )
    async def bug(self, ctx):

        # Ask the user what kind of bug they are reporting. Or give them an option to cancel reporting the bug
        message = await ctx.send(
            embed = Embed(
                title = "Bug Source",
                description = "If the bug is on the website, react with {}\nIf it's in the bot, react with {}".format(
                    WEBSITE, BOT
                ),
                colour = await get_embed_color(ctx.author)
            )
        )
        await message.add_reaction(WEBSITE)
        await message.add_reaction(BOT)
        await message.add_reaction(LEAVE)

        # Wait for the user to react
        reaction, user = await self.bot.wait_for("reaction_add", check = lambda reaction, user: (
            reaction.message.id == message.id and
            user.id == ctx.author.id and
            str(reaction) in [WEBSITE, BOT, LEAVE]
        ))
        
        # Check if the user wants to stop reporting the bug
        if str(reaction) == LEAVE:
            await message.delete()
            await ctx.send(
                embed = Embed(
                    title = "Bug Report Canceled",
                    description = "_ _",
                    colour = await get_embed_color(ctx.author)
                )
            )
        
        # The user wants to report the bug
        else:

            # If the reaction is WEBSITE, ask the user where on the website the bug happened
            if str(reaction) == WEBSITE:
                question = "Where on the website did the bug occur?"
                source_type = "website"

            # If the reaction is BOT, ask the user what command the bug happened on
            else:
                question = "What command did the bug occur on?"
                source_type = "bot"
            
            # Wait for the user to reply with the source of the bug
            await message.clear_reactions()
            await message.edit(
                embed = Embed(
                    title = "Bug Source",
                    description = question,
                    colour = await get_embed_color(ctx.author)
                )
            )
            msg = await self.bot.wait_for("message", check = lambda msg: (
                msg.author.id == ctx.author.id and
                msg.channel.id == ctx.channel.id
            ))
            source = msg.content
            await msg.delete()

            # Wait for the user to type out and send the bug report.
            await message.edit(
                embed = Embed(
                    title = "Type your bug report",
                    description = "Give a decent description of the bug, including steps to reproduce, if applicable, and any important things concerning the bug. If you don't want to report the bug, react with {}".format(LEAVE),
                    colour = await get_embed_color(ctx.author)
                )
            )
            await message.add_reaction(LEAVE)
            
            done, pending = await wait([
                self.bot.wait_for("message", check = lambda msg: (
                    msg.author.id == ctx.author.id and
                    msg.channel.id == ctx.channel.id
                )),
                self.bot.wait_for("reaction_add", check = lambda reaction, user: (
                    reaction.message.id == message.id and
                    user.id == ctx.author.id and
                    str(reaction) == LEAVE
                ))
            ], return_when = FIRST_COMPLETED)
            result = done.pop().result()
            for future in pending:
                future.cancel()

            # Check if the length of the result is 2, the user reacted with LEAVE
            if isinstance(result, tuple):
                await message.delete()
                await ctx.send(
                    embed = Embed(
                        title = "Bug Report Canceled",
                        description = "_ _",
                        colour = await get_embed_color(ctx.author)
                    )
                )
            
            # The length of the result is 1, the user reported the bug
            else:
                bug_description = result.content
                await result.delete()
                    
                # Save the bug data into the database and any images on Imgur
                bug_number = await database.case_numbers.get_bug_number()
                await database.case_numbers.add_bug(
                    source_type, source,
                    str(ctx.author.id), 
                    bug_description
                )

                # Create an embed that will be sent to the developers and 
                # as a confirmation message to the reporter
                embed = Embed(
                    title = "Bug Reported (#{})".format(bug_number),
                    description = "Reported by {}".format(str(ctx.author)),
                    colour = await get_embed_color(ctx.author)
                ).add_field(
                    name = "Source",
                    value = "`{}` - {}".format(source_type, source)
                ).add_field(
                    name = "Description",
                    value = bug_description,
                    inline = False
                )

                # Send a message to all developers
                for dev in await database.bot.get_developers():
                    dev = self.bot.get_user(int(dev))
                    try: await dev.send(embed = embed)
                    except: pass

                # Send a confirmation message to the user
                await ctx.send(embed = embed)
            
                # Send a message to the bug channel
                await send_webhook(environ["BUG_WEBHOOK"], embed)
    
    @command(
        name = "suggest", aliases = ["suggestion"],
        description = "Allows you to make a suggestion for a feature or idea in Omega Psi.",
        cog_name = "bot"
    )
    async def suggest(self, ctx, *, suggestion = None):
        
        # Save the suggestion into the database
        suggestion_number = await database.case_numbers.get_suggestion_number()
        await database.case_numbers.add_suggestion(ctx.author, suggestion)

        # Create an embed that will be sent to the developers and
        # as a confirmation message to the suggestor
        embed = Embed(
            title = "Suggestion Made (#{})".format(suggestion_number),
            description = "Submitted by {}".format(str(ctx.author)),
            colour = await get_embed_color(ctx.author)
        ).add_field(
            name = "Suggestion",
            value = suggestion,
            inline = False
        )

        # Send a message to all developers
        for dev in await database.bot.get_developers():
            dev = self.bot.get_user(int(dev))
            try: await dev.send(embed = embed)
            except: pass

        # Send a confirmation message to the user
        await ctx.send(embed = embed)

        # Send a message to the suggestion channel
        await send_webhook(environ["SUGGESTION_WEBHOOK"], embed)
    
    @command(
        name = "pendingUpdate", 
        aliases = ["pending"],
        description = "Shows you information about the current pending update to Omega Psi.",
        cog_name = "bot"
    )
    async def pending_update(self, ctx):

        # Check if there is a pending update
        pending_update = await database.bot.get_pending_update()

        # There is no pending update
        if len(pending_update) == 0:
            embed = Embed(
                title = "Pending Update",
                description = "No Pending Update Yet",
                colour = await get_embed_color(ctx.author)
            )
        
        # There is a pending update
        else:
            embed = Embed(
                title = "Pending Update",
                description = "_ _",
                colour = await get_embed_color(ctx.author)
            )

            # Iterate through the features dict to get each feature
            #   also sort them by the time field
            features = [
                pending_update["features"][feature]
                for feature in pending_update["features"]
            ]

            # Create the fields for features
            feature_fields = create_fields(features, key = lambda feature: (
                "`{}` - {}".format(feature["type"], feature["feature"])
            ))

            # Add the fields to the embed
            if len(feature_fields) == 0:
                embed.add_field(
                    name = "Changes",
                    value = "No Changes",
                    inline = False
                )
            else:
                for value in range(len(feature_fields)):
                    field = feature_fields[value]
                    embed.add_field(
                        name = "Changes {}".format(
                            "{} / {}".format(
                                value + 1, len(feature_fields)
                            ) if len(feature_fields) > 1 else ""
                        ),
                        value = field,
                        inline = False
                    )
            
        # Send the embed to the user
        await ctx.send(embed = embed)
    
    @group(
        name = "update",
        description = "Shows you information about updates to Omega Psi.",
        cog_name = "bot"
    )
    async def update(self, ctx):
        if not ctx.invoked_subcommand:
            
            # Get the recent update data
            recent_update = await database.bot.get_recent_update()

            # Create the embed
            embed = Embed(
                title = "Updates",
                description = "Here's the most recent update to Omega Psi.",
                colour = await get_embed_color(ctx.author)
            )

            fields = {
                "Release Date": recent_update["date"],
                "Version": recent_update["version"],
                "Description": recent_update["description"],
                "Changes": "\n".join([
                    "`{}` | {}".format(
                        feature["type"],
                        feature["feature"]
                    )
                    for feature in recent_update["features"]
                ]) if len(recent_update["features"]) > 0 else ""
            }

            # Add all fields to embed
            for field in fields:
                sub_fields = create_fields(fields[field])
                add_fields(embed, field, sub_fields)
            
            await ctx.send(embed = embed)
        
    @update.command(
        name = "all",
        description = "Shows you a list of past updates to Omega Psi.",
        cog_name = "bot"
    )
    async def update_all(self, ctx):
        
        # Get all the updates
        updates = await database.bot.get_updates()

        # Create the embed
        embed = Embed(
            title = "Updates",
            description = "Here's a list of updates to Omega Psi in order of most recent to oldest.",
            colour = await get_embed_color(ctx.author)
        )

        # Setup fields
        current = 0
        fields = {
            "Release Date": updates[current]["date"],
            "Version": updates[current]["version"],
            "Description": updates[current]["description"],
            "Changes": "\n".join([
                "`{}` | {}".format(
                    feature["type"],
                    feature["feature"]
                )
                for feature in updates[current]["features"]
            ]) if len(updates[current]["features"]) > 0 else ""
        }

        # Add all fields to embed
        for field in fields:
            sub_fields = create_fields(fields[field])
            add_fields(embed, field, sub_fields)
        
        # Send the message and add the scroll reactions
        message = await ctx.send(embed = embed)
        await add_scroll_reactions(message, updates)
        while True:

            # Wait for reactions
            def check(reaction, user):
                return reaction.message.id == message.id and user.id == ctx.author.id and str(reaction) in SCROLL_REACTIONS
            
            done, pending = await wait([
                self.bot.wait_for("reaction_add", check = check),
                self.bot.wait_for("reaction_remove", check = check)
            ], return_when = FIRST_COMPLETED)
            reaction, user = done.pop().result()

            # Cancel all futures
            for future in pending:
                future.cancel()
            
            # Reaction is first page
            if str(reaction) == FIRST_PAGE:
                current = 0
            
            # Reaction is last page
            elif str(reaction) == LAST_PAGE:
                current = len(updates) - 1
            
            # Reaction is previous page
            elif str(reaction) == PREVIOUS_PAGE:
                current -= 1
                if current < 0:
                    current = 0
            
            # Reaction is next page
            elif str(reaction) == NEXT_PAGE:
                current += 1
                if current > len(updates) - 1:
                    current = len(updates) - 1
            
            # Reaction is leave
            elif str(reaction) == LEAVE:
                await message.delete()
                break
            
            # Update the fields and embeds
            embed = Embed(
                title = "Updates",
                description = "Here's a list of updates to Omega Psi in order of most recent to oldest.",
                colour = await get_embed_color(ctx.author)
            )
            fields = {
                "Release Date": updates[current]["date"],
                "Version": updates[current]["version"],
                "Description": updates[current]["description"],
                "Changes": "\n".join([
                    "`{}` | {}".format(
                        feature["type"],
                        feature["feature"]
                    )
                    for feature in updates[current]["features"]
                ]) if len(updates[current]["features"]) > 0 else ""
            }
            for field in fields:
                sub_fields = create_fields(fields[field])
                add_fields(embed, field, sub_fields)
            await message.edit(embed = embed)
    
    @group(
        name = "tasks",
        description = "Shows you a list of tasks that developers have made to modify Omega Psi.",
        cog_name = "bot"
    )
    async def tasks(self, ctx):
        if not ctx.invoked_subcommand:
            
            # Get the tasks from the database and put them into a large string
            task_list = await database.bot.get_tasks()

            # There are tasks, build the string
            task_string = ""
            if len(task_list) > 0:
                count = 0
                for task_id in task_list:
                    task = task_list[task_id]
                    task_string += "**{}.)** *{}*\n".format(count + 1, task)
                    count += 1
            
            # There are no tasks
            else:
                task_string = "There are currently no tasks."

            # Create the embed and send the message
            await ctx.send(
                embed = Embed(
                    title = "Tasklist",
                    description = task_string,
                    colour = await get_embed_color(ctx.author)
                )
            )
    
    @command(
        name = "botInfo", aliases = ["bi"],
        description = "Shows you information about Omega Psi.",
        cog_name = "bot"
    )
    async def botinfo(self, ctx):
        
        # Get the bot application information
        bot_info = await self.bot.application_info()
        owner = bot_info.owner
        developers = [self.bot.get_user(int(dev)) if self.bot.get_user(int(dev)) != None else dev for dev in await database.bot.get_developers()]

        # Setup the embed fields
        globally_disabled = await database.bot.get_disabled_commands()
        fields = {
            "Owner": "{}".format(str(owner)),
            "Developers": "\n".join([
                dev if type(dev) == str else "{} ({})".format(
                    dev.mention, dev
                )
                for dev in developers
            ]),
            "Globally Disabled Commands": "\n".join([
                "`{}`".format(command)
                for command in globally_disabled
            ]) if len(globally_disabled) > 0 else "No Globally Disabled Commands",
        }

        # Create the embed and send the message
        embed = Embed(
            title = "Omega Psi Info",
            description = "Here's some information about me!",
            colour = await get_embed_color(ctx.author)
        ).set_image(
            url = "https://discordbots.org/api/widget/535587516816949248.png?topcolor={1}&avatarbg={1}&datacolor={1}&highlightcolor={0}&middlecolor={0}&usernamecolor={0}&labelcolor={2}".format(
                "293134", "ec7600", "808080"
            )
        ).set_footer(
            text = "Created on {}. Omega Psi is {} old.".format(
                datetime_to_string(OMEGA_PSI_CREATION, short = True),
                datetime_to_length(OMEGA_PSI_CREATION)
            )
        )

        for field in fields:
            sub_fields = create_fields(fields[field])
            add_fields(embed, field, sub_fields)
        
        await ctx.send(embed = embed)
    
    @command(
        name = "guildInfo",
        aliases = ["gi"],
        description = "Gives you information about this server.",
        cog_name = "misc"
    )
    @guild_only()
    async def guild_info(self, ctx):

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
                len([ member for member in ctx.guild.members if member.status == Status.online ]),
                len([ member for member in ctx.guild.members if member.bot ]),
                len([ member for member in ctx.guild.members if not member.bot ])
            )
        }
        
        # Create the embed for the guild info
        embed = Embed(
            name = "Guild Info",
            description = "_ _",
            colour = await get_embed_color(ctx.author)
        ).set_footer(
            text = "Server Name: {} | Server ID: {}".format(ctx.guild.name, ctx.guild.id)
        ).set_thumbnail(
            url = ctx.guild.icon_url
        )
        for field in fields:
            embed.add_field(
                name = field,
                value = fields[field]
            )

        # Create roles fields
        roles = create_fields(ctx.guild.roles[::-1], key = lambda role: role.mention, new_line = False)
        for i in range(len(roles)):
            embed.add_field(
                name = "Roles {}".format(
                    "({} / {})".format(
                        i + 1, len(roles)
                    ) if len(roles) > 1 else ""
                ),
                value = roles[i],
                inline = False
            )
        
        await ctx.send(embed = embed)
    
    @command(
        name = "userInfo",
        aliases = ["ui"],
        description = "Gives you info about a member in this guild.",
        cog_name = "misc"
    )
    @guild_only()
    async def user_info(self, ctx, *, user : Union[Member, str] = None):
        
        # Check if getting info for specific user
        if user != None:

            # Try to find user if not already converted to member
            if type(user) != Member:

                # Iterate through members
                found = False
                for member in ctx.guild.members:

                    # Get a list of possible aliases
                    check_list = [member.name.lower(), member.display_name.lower()]
                    if member.nick != None:
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
        if user != None:
        
            # Send user data
            permissions = ", ".join([
                perm.replace("_", " ").title()
                for perm, has_perm in list(ctx.channel.permissions_for(user))
                if has_perm == True
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
                name = "User Info",
                description = " ",
                colour = await get_embed_color(ctx.author)
            ).set_thumbnail(
                url = user.avatar_url
            ).set_footer(
                text = "User Name: {} | User ID: {}".format(
                    "{}#{}".format(
                        user.name, user.discriminator
                    ),
                    user.id
                )
            )

            for field in fields:
                embed.add_field(
                    name = field,
                    value = fields[field],
                    inline = False
                )
            
            await ctx.send(
                embed = embed
            )
        
        # user is none
        else:
            await ctx.send(
                embed = get_error_message(
                    "There was no member found with that name."
                )
            )
    
    @command(
        name = "support", aliases = ["discord"],
        description = "Gives you an invite link to my Discord server.",
        cog_name = "bot"
    )
    async def support(self, ctx):
        await ctx.send("discord.gg/W8yVrHt")
    
    @command(
        name = "website",
        description = "Gives you the link to my personal website.",
        cog_name = "bot"
    )
    async def website(self, ctx):
        await ctx.send("https://fellowhashbrown.com")
    
    @command(
        name = "botSite",
        description = "Gives you the link to Omega Psi's website.",
        cog_name = "bot"
    )
    async def botsite(self, ctx):
        await ctx.send("https://omegapsi.fellowhashbrown.com")
    
    @command(
        name = "source", aliases = ["src", "replit", "repl"],
        description = "Gives you the links to Omega Psi's source code.",
        cog_name = "bot"
    )
    async def source(self, ctx):
        await ctx.send(
            "https://repl.it/@FellowHashbrown/OmegaPsi\nhttps://github.com/FellowHashbrown/Omega-Psi"
        )
    
    @command(
        name = "invite",
        description = "Gives you the invite link to invite me to your own server.",
        cog_name = "bot"
    )
    async def invite(self, ctx):
        await ctx.send(
            "https://discordapp.com/oauth2/authorize?client_id=535587516816949248&scope=bot&permissions=519232"
        )
    
    @command(
        name = "ping",
        description = "pong",
        cog_name = "bot"
    )
    async def ping(self, ctx):
        await ctx.send(
            "Pong! `{}ms`".format(int(self.bot.latency * 1000))
        )

    @command(
        name = "prefix", aliases = ["pre"],
        description = "Changes the prefix for this server.",
        cog_name = "bot"
    )
    @guild_only()
    @guild_manager()
    async def prefix(self, ctx, *, prefix : str = None):
        
        # Check if prefix is None (didn't enter it in)
        if prefix == None:
            await ctx.send(
                embed = get_error_message(
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
                embed = Embed(
                    title = "Prefix Changed",
                    description = f"This server's prefix is now `{prefix}`",
                    colour = await get_embed_color(ctx.author)
                )
            )
    
    @command(
        name = "enableCommand",
        description = "Enables a specified command in this server.",
        cog_name = "developer"
    )
    @guild_only()
    @guild_manager()
    async def enable_command(self, ctx, cmd = None):

        # Check if there is no command to enable
        if not cmd:
            await ctx.send(
                embed = get_error_message("You need to specify the command to enable.")
            )
        
        # There is a command to enable
        else:

            # Check that it's a valid command in the bot
            cmd = self.bot.get_command(cmd)
            if not cmd:
                await ctx.send(
                    embed = get_error_message("That command does not exist!")
                )
            
            # The command is valid, enable it if possible
            else:
                enabled = await database.guilds.enable_command(ctx.guild, cmd.qualified_name)
                if not enabled:
                    await ctx.send(
                        embed = get_error_message("That command is already enabled!")
                    )
                
                else:
                    await ctx.send(
                        embed = Embed(
                            title = "Command Enabled",
                            description = "`{}` has been enabled".format(cmd.qualified_name),
                            colour = await get_embed_color(ctx.author)
                        )
                    )
    
    @command(
        name = "disableCommand",
        description = "Disables a specified command in this server.",
        cog_name = "developer"
    )
    @guild_only()
    @guild_manager()
    async def disable_command(self, ctx, cmd = None):

        # Check if there is no command to disable
        if not cmd:
            await ctx.send(
                embed = get_error_message("You need to specify the command to disable.")
            )
        
        # There is a command to disable
        else:

            # Check that it's a valid command in the bot
            cmd = self.bot.get_command(cmd)
            if not cmd:
                await ctx.send(
                    embed = get_error_message("That command does not exist!")
                )
            
            # The command is valid, disable it if possible
            else:
                disabled = await database.guilds.disable_command(ctx.guild, cmd.qualified_name)
                if not disabled:
                    await ctx.send(
                        embed = get_error_message("That command is already disabled!")
                    )
                
                else:
                    await ctx.send(
                        embed = Embed(
                            title = "Command disabled",
                            description = "`{}` has been disabled".format(cmd.qualified_name),
                            colour = await get_embed_color(ctx.author)
                        )
                    )

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @command(
        name = "restart",
        description = "Restarts the bot.",
        cog_name = "bot"
    )
    @is_developer()
    async def restart(self, ctx):
        
        # Change the bot presence to say "Reloading..."
        await self.bot.change_presence(
            status = Status.online,
            activity = Activity(
                name = "Restarting...",
                type = 0,
                url = "https://twitch.tv/FellowHashbrown"
            )
        )

        # Set the restart data in the database
        await database.bot.set_restart({
            "send": True,
            "channel_id": str(ctx.channel.id) if ctx.channel != None else None,
            "author_id": str(ctx.author.id)
        })

        # Actually restart
        await ctx.send(
            "{}, I will be right back!".format(ctx.author.mention)
        )

        execv(executable, ["python"] + argv)

        await self.bot.logout()

    @tasks.command(
        name = "add",
        description = "Adds a new task to the tasklist.",
        cog_name = "bot"
    )
    @is_developer()
    async def tasks_add(self, ctx, *, task = None):
        await database.bot.add_task(task)
        await ctx.send(
            embed = Embed(
                title = "Task Added",
                description = "*{}* was added to the tasklist".format(task),
                colour = await get_embed_color(ctx.author)
            )
        )
    
    @tasks.command(
        name = "remove",
        description = "Removes an existing task from the tasklist.",
        cog_name = "bot"
    )
    @is_developer()
    async def tasks_remove(self, ctx, *, task_number = None):

        # Check that the task number is a number
        try: 
            task_number = int(task_number)
            tasks = await database.bot.get_tasks()
            if task_number < 1 or task_number > len(tasks):
                raise Exception()
            task_id = list(tasks.keys())[task_number - 1]
            removed = await database.bot.remove_task(task_id)
        except: removed = None
        await ctx.send(
            embed = Embed(
                title = "Task Removed" if removed else "No Task Removed",
                description = "*{}* was removed from the tasklist".format(
                    removed["task"]
                ) if removed else "That task number is invalid.",
                colour = await get_embed_color(ctx.author)
            )
        )

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @tasks_add.error
    @tasks_remove.error
    @prefix.error
    @guild_info.error
    @user_info.error
    async def error_handling(self, ctx, error):

        # Check if the user who called the commands is not a developer
        if isinstance(error, NotADeveloper):
            await ctx.send(embed = NOT_A_DEVELOPER_ERROR)
        
        # Check if the user who called the commands can't manage the guild
        elif isinstance(error, NotAGuildManager):
            await ctx.send(embed = NOT_A_GUILD_MANAGER_ERROR)
        
        # Check if the command cannot run in a private message
        elif isinstance(error, NotInGuild):
            await ctx.send(embed = NOT_IN_GUILD_ERROR)

def setup(bot):
    bot.add_cog(Bot(bot))