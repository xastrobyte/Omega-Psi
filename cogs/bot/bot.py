from asyncio import wait, FIRST_COMPLETED
from datetime import datetime
from discord import Embed
from discord.ext.commands import Cog, group, command
from os import environ

from cogs.errors import get_error_message

from cogs.globals import FIRST_PAGE, LAST_PAGE, PREVIOUS_PAGE, NEXT_PAGE, LEAVE, SCROLL_REACTIONS
from cogs.globals import OMEGA_PSI_CREATION
from cogs.predicates import is_developer

from util.database.database import database

from util.discord import process_scrolling
from util.functions import get_embed_color, create_fields, add_fields, add_scroll_reactions
from util.string import datetime_to_string, datetime_to_length, dict_to_datetime

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

WEBSITE = "🌐"
BOT = "🤖"


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class Bot(Cog, name="bot"):
    """Primary bot-related commands like bugs and suggestions"""

    def __init__(self, bot):
        self.bot = bot

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @command(
        name="bug", aliases=["issue"],
        description="Allows you to report a bug found in Omega Psi.",
        cog_name="bot"
    )
    async def bug(self, ctx):
        """Allows a user to submit a bug report found in the bot
        or on the website of the bot.

        :param ctx: The context of where the message was sent
        """

        # Ask the user what kind of bug they are reporting. Or give them an option to cancel reporting the bug
        message = await ctx.send(
            embed=Embed(
                title="Bug Source",
                description="If the bug is on the website, react with {}\nIf it's in the bot, react with {}".format(
                    WEBSITE, BOT
                ),
                colour=await get_embed_color(ctx.author)
            )
        )
        await message.add_reaction(WEBSITE)
        await message.add_reaction(BOT)
        await message.add_reaction(LEAVE)

        # Wait for the user to react
        reaction, user = await self.bot.wait_for("reaction_add", check=lambda r, u: (
                r.message.id == message.id and
                u.id == ctx.author.id and
                str(r) in [WEBSITE, BOT, LEAVE]
        ))

        # Check if the user wants to stop reporting the bug
        if str(reaction) == LEAVE:
            await message.delete()
            await ctx.send(
                embed=Embed(
                    title="Bug Report Canceled",
                    description="_ _",
                    colour=await get_embed_color(ctx.author)
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
                embed=Embed(
                    title="Bug Source",
                    description=question,
                    colour=await get_embed_color(ctx.author)
                )
            )
            msg = await self.bot.wait_for("message", check=lambda m: (
                    m.author.id == ctx.author.id and
                    m.channel.id == ctx.channel.id
            ))
            source = msg.content
            await msg.delete()

            # Wait for the user to type out and send the bug report.
            await message.edit(
                embed=Embed(
                    title="Type your bug report",
                    description=(
                            "Give a decent description of the bug, including steps to reproduce, " +
                            "if applicable, and any important things concerning the bug. " +
                            "If you don't want to report the bug, react with {}".format(
                                LEAVE)),
                    colour=await get_embed_color(ctx.author)
                )
            )
            await message.add_reaction(LEAVE)

            done, pending = await wait([
                self.bot.wait_for("message", check=lambda m: (
                        m.author.id == ctx.author.id and
                        m.channel.id == ctx.channel.id
                )),
                self.bot.wait_for("reaction_add", check=lambda r, u: (
                        r.message.id == message.id and
                        u.id == ctx.author.id and
                        str(r) == LEAVE
                ))
            ], return_when=FIRST_COMPLETED)
            result = done.pop().result()
            for future in pending:
                future.cancel()

            # Check if the length of the result is 2, the user reacted with LEAVE
            if isinstance(result, tuple):
                await message.delete()
                await ctx.send(
                    embed=Embed(
                        title="Bug Report Canceled",
                        description="_ _",
                        colour=await get_embed_color(ctx.author)
                    )
                )

            # The length of the result is 1, the user reported the bug
            else:
                bug_description = result.content
                await result.delete()

                # Save the bug data into the database
                bug_number = await database.case_numbers.get_bug_number()

                # Create an embed that will be sent to the developers and 
                # as a confirmation message to the reporter
                embed = Embed(
                    title="Bug (#{})".format(bug_number),
                    description="_ _",
                    colour=await get_embed_color(ctx.author),
                    timestamp=datetime.now()
                ).add_field(
                    name="User",
                    value=str(ctx.author)
                ).add_field(
                    name="Source Type",
                    value=source_type
                ).add_field(
                    name="Source",
                    value=source
                ).add_field(
                    name="Bug",
                    value=bug_description,
                    inline=False
                ).add_field(
                    name="Seen?",
                    value="No"
                ).add_field(
                    name="Fixed?",
                    value="No"
                )

                # Send a message to all developers
                for dev in await database.bot.get_developers():
                    dev = self.bot.get_user(int(dev))
                    try:
                        await dev.send(embed=embed)
                    except Exception as _:
                        pass

                # Send a confirmation message to the user
                await ctx.send(embed=embed)

                # Send a message to the bug channel and save the bug into the database
                channel = self.bot.get_channel(int(environ["BUG_CHANNEL"]))
                msg = await channel.send(embed=embed)
                await database.case_numbers.add_bug(
                    source_type, source,
                    str(ctx.author.id),
                    bug_description,
                    str(msg.id)
                )

    @command(
        name="suggest", aliases=["suggestion"],
        description="Allows you to make a suggestion for a feature or idea in Omega Psi.",
        cog_name="bot"
    )
    async def suggest(self, ctx, *, suggestion=None):
        """Allows a user to submit a suggestion for the bot or the
        website of the bot.

        :param ctx: The context of where the message was sent
        :param suggestion: The suggestion the user is submitting
        """

        # Check if a suggestion does not exist
        if suggestion is None:
            embed = get_error_message("You must specify the suggestion you want to submit!")

        # The suggestion exists
        else:

            # Save the suggestion into the database
            suggestion_number = await database.case_numbers.get_suggestion_number()

            # Create an embed that will be sent to the developers and
            # as a confirmation message to the suggestor
            embed = Embed(
                title="Suggestion (#{})".format(suggestion_number),
                description="_ _",
                colour=await get_embed_color(ctx.author),
                timestamp=datetime.now()
            ).add_field(
                name="User",
                value=str(ctx.author)
            ).add_field(
                name="Suggestion",
                value=suggestion,
                inline=False
            ).add_field(
                name="Seen?",
                value="No"
            ).add_field(
                name="Considered?",
                value="Not Yet"
            )

            # Send a message to all developers
            for dev in await database.bot.get_developers():
                dev = self.bot.get_user(int(dev))
                try:
                    await dev.send(embed=embed)
                except Exception as _:
                    pass

            # Send a message to the suggestion channel
            channel = self.bot.get_channel(int(environ["SUGGESTION_CHANNEL"]))
            msg = await channel.send(embed=embed)
            await database.case_numbers.add_suggestion(ctx.author, suggestion, msg.id)

        # Send a confirmation message to the user
        await ctx.send(embed=embed)

    @command(
        name="myBugs",
        description="Allows you to view a list of bugs you have reported and their current status",
        cog_name="bot"
    )
    async def my_bugs(self, ctx):
        """Allows the user to view which bugs they have submitted

        :param ctx: The context of where the message was sent
        """

        # Get the bug case numbers the author has reported
        cases = await database.case_numbers.get_bug_cases(
            key=lambda c: c["author"] == str(ctx.author.id)
        )
        cases = cases["cases"]

        # Check if there are no case_numbers
        if len(cases) == 0:
            await ctx.send(embed=Embed(
                title="No Bugs",
                description="You haven't reported any bugs!",
                colour=await get_embed_color(ctx.author)
            ))

        # There is at least 1 case_number
        else:
            bugs = []
            for case_number in cases:
                case = cases[case_number]
                seen_dev = self.bot.get_user(int(case["seen"])) if case["seen"] is not None else None
                embed = Embed(
                    title="Bug (#{})".format(str(case_number)),
                    description="_ _",
                    colour=await get_embed_color(ctx.author),
                    timestamp=dict_to_datetime(case["time"])
                ).add_field(
                    name="Source Type",
                    value=case["source_type"]
                ).add_field(
                    name="Source",
                    value=case["source"]
                ).add_field(
                    name="Bug",
                    value=case["bug"],
                    inline=False
                ).add_field(
                    name="Seen?",
                    value="No" if seen_dev is None else "Yes, by {}".format(str(seen_dev))
                ).add_field(
                    name="Fixed?",
                    value="No" if not case["fixed"] else "Yes"
                )
                bugs.append(embed)

            # Allow the user to scroll through the bugs
            await process_scrolling(ctx, self.bot, pages=bugs)

    @command(
        name="mySuggestions",
        description="Allows you to view a list of suggestions you have submitted and their current status",
        cog_name="bot"
    )
    async def my_suggestions(self, ctx):
        """Allows the user to view which suggestions they have submitted.

        :param ctx: The context of where the message was sent
        """

        # Get the suggestion case numbers the author has reported
        cases = await database.case_numbers.get_suggestion_cases(
            key=lambda c: str(c["author"]) == str(ctx.author.id)
        )
        cases = cases["cases"]

        # Check if there are no case_numbers
        if len(cases) == 0:
            await ctx.send(embed=Embed(
                title="No Suggestions",
                description="You haven't submitted any suggestions!",
                colour=await get_embed_color(ctx.author)
            ))

        # There is at least 1 case_number
        else:
            suggestions = []
            for case_number in cases:
                case = cases[case_number]
                seen_dev = self.bot.get_user(int(case["seen"])) if case["seen"] is not None else None
                embed = Embed(
                    title="Suggestion (#{})".format(str(case_number)),
                    description="_ _",
                    colour=await get_embed_color(ctx.author),
                    timestamp=dict_to_datetime(case["time"])
                ).add_field(
                    name="Suggestion",
                    value=case["suggestion"],
                    inline=False
                ).add_field(
                    name="Seen?",
                    value="No" if seen_dev is None else "Yes, by {}".format(str(seen_dev))
                ).add_field(
                    name="Considered?",
                    value="Not Yet" if case["consideration"] is None else (
                        "No\n**Reason**: {}".format(case["consideration"]["reason"])
                        if not case["consideration"]["considered"] else "Yes"
                    )
                )
                suggestions.append(embed)

            # Allow the user to scroll through the suggestions
            await process_scrolling(ctx, self.bot, pages=suggestions)

    @command(
        name="pendingUpdate",
        aliases=["pending"],
        description="Shows you information about the current pending update to Omega Psi.",
        cog_name="bot"
    )
    async def pending_update(self, ctx):
        """Allows the user to view the current pending update
        to the bot.

        :param ctx: The context of where the message was sent
        """

        # Check if there is a pending update
        pending_update = await database.bot.get_pending_update()

        # There is no pending update
        if len(pending_update) == 0:
            embed = Embed(
                title="Pending Update",
                description="No Pending Update Yet",
                colour=await get_embed_color(ctx.author)
            )

        # There is a pending update
        else:
            embed = Embed(
                title="Pending Update",
                description="_ _",
                colour=await get_embed_color(ctx.author)
            )

            # Iterate through the features dict to get each feature
            #   also sort them by the time field
            features = [
                pending_update["features"][feature]
                for feature in pending_update["features"]
            ]

            # Create the fields for features
            feature_fields = create_fields(features, key=lambda feature: (
                "`{}` - {}".format(feature["type"], feature["feature"])
            ))

            # Add the fields to the embed
            if len(feature_fields) == 0:
                embed.add_field(
                    name="Changes",
                    value="No Changes",
                    inline=False
                )
            else:
                for value in range(len(feature_fields)):
                    field = feature_fields[value]
                    embed.add_field(
                        name="Changes {}".format(
                            "{} / {}".format(
                                value + 1, len(feature_fields)
                            ) if len(feature_fields) > 1 else ""
                        ),
                        value=field,
                        inline=False
                    )

        # Send the embed to the user
        await ctx.send(embed=embed)

    @group(
        name="update",
        description="Shows you information about updates to Omega Psi.",
        cog_name="bot"
    )
    async def update(self, ctx):
        """Allows the user to view the current or past updates to the bot

        :param ctx: The context of where the message was sent
        """
        if not ctx.invoked_subcommand:

            # Get the recent update data
            recent_update = await database.bot.get_recent_update()

            # Create the embed
            embed = Embed(
                title="Updates",
                description="Here's the most recent update to Omega Psi.",
                colour=await get_embed_color(ctx.author)
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

            await ctx.send(embed=embed)

    @update.command(
        name="all",
        description="Shows you a list of past updates to Omega Psi.",
        cog_name="bot"
    )
    async def update_all(self, ctx):
        """Allows the user to view all the updates in the bot

        :param ctx: The context of where the message was sent
        """

        # Get all the updates
        updates = await database.bot.get_updates()

        # Create the embed
        embed = Embed(
            title="Updates",
            description="Here's a list of updates to Omega Psi in order of most recent to oldest.",
            colour=await get_embed_color(ctx.author)
        )

        # Setup fields
        current = 0

        def create_feature_fields():
            return {
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
        fields = create_feature_fields()

        # Add all fields to embed
        for field in fields:
            sub_fields = create_fields(fields[field])
            add_fields(embed, field, sub_fields)

        # Send the message and add the scroll reactions
        message = await ctx.send(embed=embed)
        await add_scroll_reactions(message, updates)
        while True:

            # Wait for reactions
            def check(r, u):
                return r.message.id == message.id and \
                       u.id == ctx.author.id and \
                       str(r) in SCROLL_REACTIONS

            done, pending = await wait([
                self.bot.wait_for("reaction_add", check=check),
                self.bot.wait_for("reaction_remove", check=check)
            ], return_when=FIRST_COMPLETED)
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
                title="Updates",
                description="Here's a list of updates to Omega Psi in order of most recent to oldest.",
                colour=await get_embed_color(ctx.author)
            )

            fields = create_feature_fields()
            for field in fields:
                sub_fields = create_fields(fields[field])
                add_fields(embed, field, sub_fields)
            await message.edit(embed=embed)

    @group(
        name="tasks",
        description="Shows you a list of tasks that developers have made to modify Omega Psi.",
        cog_name="bot"
    )
    async def tasks(self, ctx):
        """Allows the user to view a tasklist of what the developers
        intend to accomplish in the bot.

        :param ctx: The context of where the message was sent
        """
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
                embed=Embed(
                    title="Tasklist",
                    description=task_string,
                    colour=await get_embed_color(ctx.author)
                )
            )

    @command(
        name="botInfo", aliases=["bi"],
        description="Shows you information about Omega Psi.",
        cog_name="bot"
    )
    async def botinfo(self, ctx):
        """Allows the user to view information about Omega Psi

        :param ctx: The context of where the message was sent
        """

        # Get the bot application information
        bot_info = await self.bot.application_info()
        owner = bot_info.owner
        developers = [self.bot.get_user(int(dev)) if self.bot.get_user(int(dev)) is not None else dev for dev in
                      await database.bot.get_developers()]

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
            title="Omega Psi Info",
            description="Here's some information about me!",
            colour=await get_embed_color(ctx.author)
        ).set_image(
            url=(
                    "https://discordbots.org/api/widget/535587516816949248.png?" +
                    "topcolor={1}&avatarbg={1}&datacolor={1}&highlightcolor={0}&" +
                    "middlecolor={0}&usernamecolor={0}&labelcolor={2}"
                ).format(
                    "293134", "ec7600", "808080"
            )
        ).set_footer(
            text="Created on {}. Omega Psi is {} old.".format(
                datetime_to_string(OMEGA_PSI_CREATION, short=True),
                datetime_to_length(OMEGA_PSI_CREATION)
            )
        )

        for field in fields:
            sub_fields = create_fields(fields[field])
            add_fields(embed, field, sub_fields)

        await ctx.send(embed=embed)

    @command(
        name="support", aliases=["discord"],
        description="Gives you an invite link to my Discord server.",
        cog_name="bot"
    )
    async def support(self, ctx):
        """Gives a user an invite link to my Discord server

        :param ctx: The context of where the message was sent
        """
        await ctx.send("discord.gg/F3fn57f")

    @command(
        name="website",
        description="Gives you the link to my personal website.",
        cog_name="bot"
    )
    async def website(self, ctx):
        """Gives the user a link to my personal website

        :param ctx: The context of where the message was sent
        """
        await ctx.send("https://fellowhashbrown.com")

    @command(
        name="botSite",
        description="Gives you the link to Omega Psi's website.",
        cog_name="bot"
    )
    async def botsite(self, ctx):
        """Gives the user a link to Omega Psi's website

        :param ctx: The context of where the message was sent
        """
        await ctx.send("https://omegapsi.fellowhashbrown.com")

    @command(
        name="source", aliases=["src"],
        description="Gives you the link to Omega Psi's source code.",
        cog_name="bot"
    )
    async def source(self, ctx):
        """Gives the user link to the source code for Omega Psi

        :param ctx: The context of where the message was sent
        """
        await ctx.send(
            "https://github.com/FellowHashbrown/Omega-Psi"
        )

    @command(
        name="invite",
        description="Gives you the invite link to invite me to your own server.",
        cog_name="bot"
    )
    async def invite(self, ctx):
        """Gives the user an invite link for Omega Psi

        :param ctx: The context of where the message was sent
        """
        await ctx.send(
            "https://discord.com/oauth2/authorize?client_id=535587516816949248&scope=bot&permissions=519232"
        )

    @command(
        name="ping",
        description="pong!",
        cog_name="bot"
    )
    async def ping(self, ctx):
        """Ping pong!

        :param ctx: The context of where the message was sent
        """
        await ctx.send(
            "Pong! `{}ms`".format(int(self.bot.latency * 1000))
        )

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @tasks.command(
        name="add",
        description="Adds a new task to the tasklist.",
        cog_name="bot"
    )
    @is_developer()
    async def tasks_add(self, ctx, *, task=None):
        """Allows a developer to add a task to the tasklist

        :param ctx: The context of where the message was sent
        :param task: The task to add to the tasklist
        """
        await database.bot.add_task(task)
        await ctx.send(
            embed=Embed(
                title="Task Added",
                description="*{}* was added to the tasklist".format(task),
                colour=await get_embed_color(ctx.author)
            )
        )

    @tasks.command(
        name="remove",
        description="Removes an existing task from the tasklist.",
        cog_name="bot"
    )
    @is_developer()
    async def tasks_remove(self, ctx, *, task_number=None):
        """Allows a developer to remove a task from the tasklist

        :param ctx: The context of where the message was sent
        :param task_number: The number of the task to remove
        """

        # Check that the task number is a number
        try:
            task_number = int(task_number)
            tasks = await database.bot.get_tasks()
            if task_number < 1 or task_number > len(tasks):
                raise Exception()
            task_id = list(tasks.keys())[task_number - 1]
            removed = await database.bot.remove_task(task_id)
        except Exception as _:
            removed = None
        await ctx.send(
            embed=Embed(
                title="Task Removed" if removed else "No Task Removed",
                description="*{}* was removed from the tasklist".format(
                    removed["task"]
                ) if removed else "That task number is invalid.",
                colour=await get_embed_color(ctx.author)
            )
        )

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def setup(bot):
    """Add's this cog to the bot

    :param bot: The bot to add the cog to
    """
    bot.add_cog(Bot(bot))
