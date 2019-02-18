import asyncio, discord, os, requests, sys
from datetime import datetime
from discord.ext import commands
from functools import partial

from category import errors
from category.globals import PRIMARY_EMBED_COLOR, FIELD_THRESHOLD, SCROLL_REACTIONS, FIRST_PAGE, LAST_PAGE, PREVIOUS_PAGE, NEXT_PAGE, CHECK_MARK, LEAVE
from category.globals import add_scroll_reactions
from category.predicates import is_developer, is_in_guild
from database import loop
from database import database
from util.string import dict_to_datetime

class Bot:
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @commands.command(
        name = "suggestions",
        description = "Shows all suggestions made or a specific suggestion.",
        cog_name = "Bot"
    )
    @commands.check(is_developer)
    async def suggestion_reports(self, ctx, data = None):

        # Get all suggestions
        suggestion_cases = await database.case_numbers.get_suggestion_cases()
        suggestion_cases = suggestion_cases["cases"]

        # Make sure suggestion exists or data is None
        if data == None or str(data) in suggestion_cases:

            # Only send scrolling message if there are cases
            if len(suggestion_cases) != 0:
                
                # Create embed
                current = 1 if data == None else int(data)
                author = self.bot.get_user(int(suggestion_cases[str(current)]["author"]))
                embed = discord.Embed(
                    title = "Suggestions",
                    description = "**Suggestion #{}**: {}\n**Author**: {}".format(
                        str(current),
                        suggestion_cases[str(current)]["suggestion"],
                        "{} ({})".format(
                            author.mention, author
                        )
                    ),
                    colour = PRIMARY_EMBED_COLOR,
                    timestamp = dict_to_datetime(suggestion_cases[str(current)]["time"])
                ).set_footer(
                    text = "Suggestion Seen? {}".format(
                        "✅" if suggestion_cases[str(current)]["seen"] else "❎"
                    )
                )

                # Send the message and add the reactions
                msg = await ctx.send(
                    embed = embed
                )

                await add_scroll_reactions(msg, suggestion_cases)
                await msg.add_reaction(CHECK_MARK)

                while True:

                    def check_reaction(reaction, user):
                        return reaction.message.id == msg.id and ctx.author.id == user.id and str(reaction) in SCROLL_REACTIONS
                    
                    done, pending = await asyncio.wait([
                        self.bot.wait_for("reaction_add", check = check_reaction),
                        self.bot.wait_for("reaction_remove", check = check_reaction)
                    ], return_when = asyncio.FIRST_COMPLETED)
                    reaction, user = done.pop().result()

                    # Cancel all futures
                    for future in pending:
                        future.cancel()
                    
                    # Reaction is first page
                    if str(reaction) == FIRST_PAGE:
                        current = 1

                    # Reaction is last page
                    elif str(reaction) == LAST_PAGE:
                        current = len(suggestion_cases)

                    # Reaction is previous page
                    elif str(reaction) == PREVIOUS_PAGE:
                        current -= 1
                        if current < 1:
                            current = 1

                    # Reaction is next page
                    elif str(reaction) == NEXT_PAGE:
                        current += 1
                        if current > len(suggestion_cases):
                            current = len(suggestion_cases)
                        
                    # Reaction is check mark (suggestion marked as seen)
                    elif str(reaction) == CHECK_MARK:
                        if not suggestion_cases[str(current)]["seen"]:

                            # Notify author that their suggestion was seen
                            user = self.bot.get_user(int(suggestion_cases[str(current)]["author"]))
                            if user != None:
                                await user.send(
                                    embed = discord.Embed(
                                        title = "Suggestion Seen By Developer",
                                        description = " ",
                                        colour = PRIMARY_EMBED_COLOR,
                                        timestamp = datetime.now()
                                    ).add_field(
                                        name = "Suggestion (#{})".format(str(current)),
                                        value = suggestion_cases[str(current)]["suggestion"],
                                        inline = False
                                    )
                                )

                            # Make suggestion as seen
                            await database.case_numbers.mark_suggestion_seen(str(current))
                            suggestion_cases = await database.case_numbers.get_suggestion_cases()
                            suggestion_cases = suggestion_cases["cases"]

                    # Reaction is leave
                    elif str(reaction) == LEAVE:
                        await msg.delete()
                        break

                    # Update embed
                    author = self.bot.get_user(int(suggestion_cases[str(current)]["author"]))
                    embed = discord.Embed(
                        title = "Suggestions",
                        description = "**Suggestion #{}**: {}\n**Author**: {}".format(
                            str(current),
                            suggestion_cases[str(current)]["suggestion"],
                            "{} ({})".format(
                                author.mention, author
                            )
                        ),
                        colour = PRIMARY_EMBED_COLOR,
                        timestamp = dict_to_datetime(suggestion_cases[str(current)]["time"])
                    ).set_footer(
                        text = "Suggestion Seen? {}".format(
                            "✅" if suggestion_cases[str(current)]["seen"] else "❎"
                        )
                    )

                    await msg.edit(
                        embed = embed
                    )
                    
            # There are no cases
            else:
                await ctx.send(
                    embed = discord.Embed(
                        title = "No suggestions",
                        description = "There are currently no suggestions.",
                        colour = PRIMARY_EMBED_COLOR
                    )
                )
        
        # Suggestion number is invalid
        else:
            await ctx.send(
                embed = errors.get_error_message(
                    "That suggestion was not found."
                )
            )

    @commands.command(
        name = "suggest",
        description = "If you feel like something could be improved on in this bot, please suggest it!",
        cog_name = "Bot"
    )
    async def suggest(self, ctx, *, suggestion = None):

        # Check if there is no suggestion
        if suggestion == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "In order to suggest something, you need to, ya know, **_suggest it_**."
                )
            )
        
        # There is a suggestion
        else:

            # Get the current suggestion number and add the suggestion to the reports
            suggestion_number = await database.case_numbers.get_suggestion_number()
            await database.case_numbers.add_suggestion(
                suggestion,
                str(ctx.author.id)
            )

            # Send message to all developers
            for dev in await database.bot.get_developers():

                # Get the dev user object
                user = self.bot.get_user(int(dev))

                # Send the message
                await user.send(
                    embed = discord.Embed(
                        title = "Suggestion Made (#{})".format(suggestion_number),
                        description = " ",
                        colour = PRIMARY_EMBED_COLOR
                    ).add_field(
                        name = "User",
                        value = ctx.author
                    ).add_field(
                        name = "Origin",
                        value = ("Server: " + ctx.guild.name) if ctx.guild != None else "Private Message"
                    ).add_field(
                        name = "Suggestion",
                        value = suggestion
                    ).set_thumbnail(
                        url = ctx.author.avatar_url
                    )
                )
            
            # Send message to user saying suggestion was sent
            await ctx.send(
                embed = discord.Embed(
                    title = "Suggestion Sent (Suggestion #{})".format(suggestion_number),
                    description = suggestion,
                    colour = PRIMARY_EMBED_COLOR
                )
            )
        
    @commands.command(
        name = "bugs",
        description = "Shows all bug reports made or a specific bug report.",
        cog_name = "Bot"
    )
    @commands.check(is_developer)
    async def bug_reports(self, ctx, data = None):
        
        # Get all bugs
        bug_cases = await database.case_numbers.get_bug_cases()
        bug_cases = bug_cases["cases"]

        # Make sure bug exists or data is None
        if data == None or str(data) in bug_cases:

            # Only send scrolling message if there are cases
            if len(bug_cases) != 0:
                
                # Create embed
                current = 1 if data == None else int(data)
                author = self.bot.get_user(int(bug_cases[str(current)]["author"]))
                embed = discord.Embed(
                    title = "Bugs",
                    description = "**Bug #{}**: {}\n**Author**: {}".format(
                        str(current),
                        bug_cases[str(current)]["bug"],
                        "{} ({})".format(
                            author.mention, author
                        )
                    ),
                    colour = PRIMARY_EMBED_COLOR,
                    timestamp = dict_to_datetime(bug_cases[str(current)]["time"])
                ).set_footer(
                    text = "Bug Seen? {}".format(
                        "✅" if bug_cases[str(current)]["seen"] else "❎"
                    )
                )

                # Send the message and add the reactions
                msg = await ctx.send(
                    embed = embed
                )

                await add_scroll_reactions(msg, bug_cases)
                await msg.add_reaction(CHECK_MARK)

                while True:

                    def check_reaction(reaction, user):
                        return reaction.message.id == msg.id and ctx.author.id == user.id and str(reaction) in SCROLL_REACTIONS
                    
                    done, pending = await asyncio.wait([
                        self.bot.wait_for("reaction_add", check = check_reaction),
                        self.bot.wait_for("reaction_remove", check = check_reaction)
                    ], return_when = asyncio.FIRST_COMPLETED)
                    reaction, user = done.pop().result()

                    # Cancel all futures
                    for future in pending:
                        future.cancel()
                    
                    # Reaction is first page
                    if str(reaction) == FIRST_PAGE:
                        current = 1

                    # Reaction is last page
                    elif str(reaction) == LAST_PAGE:
                        current = len(bug_cases)

                    # Reaction is previous page
                    elif str(reaction) == PREVIOUS_PAGE:
                        current -= 1
                        if current < 1:
                            current = 1

                    # Reaction is next page
                    elif str(reaction) == NEXT_PAGE:
                        current += 1
                        if current > len(bug_cases):
                            current = len(bug_cases)
                        
                    # Reaction is check mark (bug marked as seen)
                    elif str(reaction) == CHECK_MARK:
                        if not bug_cases[str(current)]["seen"]:

                            # Notify author that their bug was seen
                            user = self.bot.get_user(int(bug_cases[str(current)]["author"]))
                            if user != None:
                                await user.send(
                                    embed = discord.Embed(
                                        title = "Bug Report Seen By Developer",
                                        description = " ",
                                        colour = PRIMARY_EMBED_COLOR,
                                        timestamp = datetime.now()
                                    ).add_field(
                                        name = "Bug Report (#{})".format(str(current)),
                                        value = bug_cases[str(current)]["bug"],
                                        inline = False
                                    )
                                )

                            await database.case_numbers.mark_bug_seen(str(current))
                            bug_cases = await database.case_numbers.get_bug_cases()
                            bug_cases = bug_cases["cases"]

                    # Reaction is leave
                    elif str(reaction) == LEAVE:
                        await msg.delete()
                        break

                    # Update embed
                    author = self.bot.get_user(int(bug_cases[str(current)]["author"]))
                    embed = discord.Embed(
                        title = "Bugs",
                        description = "**Bug #{}**: {}\n**Author**: {}".format(
                            str(current),
                            bug_cases[str(current)]["bug"],
                            "{} ({})".format(
                                author.mention, author
                            )
                        ),
                        colour = PRIMARY_EMBED_COLOR,
                        timestamp = dict_to_datetime(bug_cases[str(current)]["time"])
                    ).set_footer(
                        text = "Bug Seen? {}".format(
                            "✅" if bug_cases[str(current)]["seen"] else "❎"
                        )
                    )

                    await msg.edit(
                        embed = embed
                    )
                    
            # There are no cases
            else:
                await ctx.send(
                    embed = discord.Embed(
                        title = "No Bug Reports",
                        description = "There are currently no bug reports.",
                        colour = PRIMARY_EMBED_COLOR
                    )
                )
        
        # Bug number is invalid
        else:
            await ctx.send(
                embed = errors.get_error_message(
                    "That bug report was not found."
                )
            )
    
    @commands.command(
        name = "bug",
        description = "Is there a bug or something in the bot? Use this! Give a decent description so I know what to look for!",
        cog_name = "Bot"
    )
    async def bug(self, ctx, *, bug = None):

        # Check if there is no bug
        if bug == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "In order to report a bug, you need to give a description of it."
                )
            )
        
        # There is a bug
        else:

            # Get the current bug number and add the bug to the reports
            bug_number = await database.case_numbers.get_bug_number()
            await database.case_numbers.add_bug(
                bug,
                str(ctx.author.id)
            )

            # Send message to all developers
            for dev in await database.bot.get_developers():

                # Get the dev user object
                user = self.bot.get_user(int(dev))

                # Send the message
                await user.send(
                    embed = discord.Embed(
                        title = "Bug Reported (#{})".format(bug_number),
                        description = " ",
                        colour = PRIMARY_EMBED_COLOR
                    ).add_field(
                        name = "User",
                        value = ctx.author
                    ).add_field(
                        name = "Origin",
                        value = ("Server: " + ctx.guild.name) if ctx.guild != None else "Private Message"
                    ).add_field(
                        name = "Bug",
                        value = bug
                    ).set_thumbnail(
                        url = ctx.author.avatar_url
                    )
                )
            
            # Send message to user saying bug was sent
            await ctx.send(
                embed = discord.Embed(
                    title = "Bug Sent! (Bug #{})".format(bug_number),
                    description = bug,
                    colour = PRIMARY_EMBED_COLOR
                )
            )

    @commands.command(
        name = "servers",
        aliases = ["serverList", "sl"],
        description = "Shows you a list of servers that Omega Psi is in.",
        cog_name = "Bot"
    )
    @commands.check(is_developer)
    async def server_list(self, ctx):

        # Get list of all guilds that the bot is in.
        fields = []
        fieldText = ""
        count = 0
        for guild in self.bot.guilds:
            count += 1

            name = "{}.) {}\n".format(
                count,
                guild.name
            )

            if len(fieldText) + len(name) > FIELD_THRESHOLD:
                fields.append(fieldText)
                fieldText = ""
            
            fieldText += name
        
        if len(fieldText) > 0:
            fields.append(fieldText)

        # Send message as a scrolling embed
        msg = await ctx.send(
            embed = discord.Embed(
                title = "Server List",
                description = "Here is a list of servers that Omega Psi is in.",
                colour = PRIMARY_EMBED_COLOR
            ).add_field(
                name = "Servers {}".format(
                    "({} / {})".format(
                        1, len(fields)
                    ) if len(fields) > 1 else ""
                ),
                value = fields[0]
            )
        )

        # Add necessary scroll reactions
        await add_scroll_reactions(msg, fields)

        while True:

            # Wait for reactions
            def check(reaction, user):
                return reaction.message.id == msg.id and user.id == ctx.author.id and str(reaction) in SCROLL_REACTIONS
            
            done, pending = await asyncio.wait([
                self.bot.wait_for("reaction_add", check = check),
                self.bot.wait_for("reaction_remove", check = check)
            ], return_when = asyncio.FIRST_COMPLETED)
            reaction, user = done.pop().result()

            # Cancel all futures
            for future in pending:
                future.cancel()
            
            # Reaction is first page
            if str(reaction) == FIRST_PAGE:
                current = 0
            
            # Reaction is last page
            elif str(reaction) == LAST_PAGE:
                current = len(fields) - 1
            
            # Reaction is previous page
            elif str(reaction) == PREVIOUS_PAGE:
                current -= 1
                if current < 0:
                    current = 0
            
            # Reaction is next page
            elif str(reaction) == NEXT_PAGE:
                current += 1
                if current > len(fields) - 1:
                    current = len(fields) - 1
            
            # Reaction is leave
            elif str(reaction) == LEAVE:
                await msg.delete()
                break
            
            # Update embed
            await msg.edit(
                embed = discord.Embed(
                    title = "Server List",
                    description = "Here is a list of servers that Omega Psi is in.",
                    colour = PRIMARY_EMBED_COLOR
                ).add_field(
                    name = "Servers {}".format(
                        "({} / {})".format(
                            current + 1, len(fields)
                        ) if len(fields) > 1 else ""
                    ),
                    value = fields[current]
                )
            )


    @commands.command(
        name = "restart",
        description = "Allows you to restart the bot.",
        cog_name = "Bot"
    )
    @commands.check(is_developer)
    async def restart(self, ctx):

        # Change the bot presence to say "Reloading..."
        await self.bot.change_presence(
            status = discord.Status.online,
            activity = discord.Activity(
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

        os.execv(sys.executable, ["python"] + sys.argv)

        await self.bot.logout()

    @commands.command(
        name = "kill",
        description = "Stops the bot and logs out.",
        cog_name = "Bot"
    )
    @commands.check(is_developer)
    async def kill(self, ctx):

        await ctx.send(
            "Bye! {}".format(ctx.author.mention)
        )

        await self.bot.logout()
    
    @commands.command(
        name = "createUpdate",
        aliases = ["createUpd"],
        description = "Creates a new pending update to the bot.",
        cog_name = "Bot"
    )
    @commands.check(is_developer)
    async def create_update(self, ctx):
        
        # Create the update; Send message to all other developers
        await database.bot.create_pending_update()

        for dev in await database.bot.get_developers():

            # Get the dev user object
            user = self.bot.get_user(int(dev))

            # Send to everyone except sender
            if user.id != ctx.author.id:
                await user.send(
                    embed = discord.Embed(
                        title = "Pending Update Created",
                        description = "There was a pending update created by {}.".format(ctx.author),
                        colour = PRIMARY_EMBED_COLOR
                    )
                )
            
        # Send to user
        await ctx.send(
            embed = discord.Embed(
                title = "Pending Update Created!",
                description = "Use `createFix` and `createFeature` to add fixes or features to this pending update.",
                colour = PRIMARY_EMBED_COLOR
            )
        )
    
    @commands.command(
        name = "createFix",
        aliases = ["addFix"],
        description = "Adds a fix to the pending update.",
        cog_name = "Bot"
    )
    @commands.check(is_developer)
    async def create_fix(self, ctx, *, fix = None):
        
        # Check if fix is None; Throw error message
        if fix == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need to give a brief description of what the fix is."
                )
            )
        
        # Fix is not None; Add it
        else:

            await database.bot.add_pending_fix(fix)

            # Send to all other developers
            for dev in await database.bot.get_developers():

                # Get the dev user object
                user = self.bot.get_user(int(dev))

                # Send to everyone except author
                if user.id != ctx.author.id:
                    await user.send(
                        embed = discord.Embed(
                            title = "Fix Created",
                            description = "{} created a fix in the current pending update.\n\n{}".format(
                                ctx.author,
                                fix
                            ),
                            colour = PRIMARY_EMBED_COLOR
                        )
                    )
            
            # Send to author
            await ctx.send(
                embed = discord.Embed(
                    title = "Fix Created",
                    description = fix,
                    colour = PRIMARY_EMBED_COLOR
                )
            )
    
    @commands.command(
        name = "createFeature",
        aliases = ["addFeature"],
        description = "Adds a feature to the pending update.",
        cog_name = "Bot"
    )
    @commands.check(is_developer)
    async def create_feature(self, ctx, *, feature = None):
        
        # Check if feature is None; Throw error message
        if feature == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need to give a brief description of what the feature is."
                )
            )
        
        # Feature is not None; Add it
        else:

            await database.bot.add_pending_feature(feature)

            # Send to all other developers
            for dev in await database.bot.get_developers():

                # Get the dev user object
                user = self.bot.get_user(int(dev))

                # Send to everyone except author
                if user.id != ctx.author.id:
                    await user.send(
                        embed = discord.Embed(
                            title = "Feature Created",
                            description = "{} created a feature in the current pending update.\n\n{}".format(
                                ctx.author,
                                feature
                            ),
                            colour = PRIMARY_EMBED_COLOR
                        )
                    )
            
            # Send to author
            await ctx.send(
                embed = discord.Embed(
                    title = "Feature Created",
                    description = feature,
                    colour = PRIMARY_EMBED_COLOR
                )
            )
    
    @commands.command(
        name = "commitUpdate",
        aliases = ["commit"],
        description = "Commits the pending update as a new update.",
        cog_name = "Bot"
    )
    @commands.check(is_developer)
    async def commit_update(self, ctx, version = None, *, description = None):
        
        # Check if version or description are None; Throw error message
        if version == None or description == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "In order to commit the update, you need to establish the `version` and the `description` of this update."
                )
            )
        
        # Version and description are not None; Commit the update
        else:

            # Commit the update. Then get the update so we can inform all other developers
            await database.bot.commit_pending_update(version, description)
            update = await database.bot.get_recent_update()

            for dev in await database.bot.get_developers():

                # Get the dev user object
                user = self.bot.get_user(int(dev))

                # Send to everyon except author
                if user.id != ctx.author.id:
                    await user.send(
                        embed = discord.Embed(
                            title = "Update Committed by {} - (Version {})".format(
                                ctx.author,
                                update["version"]
                            ),
                            description = update["description"],
                            colour = PRIMARY_EMBED_COLOR
                        ).add_field(
                            name = "Features",
                            value = "No New Features Were Made." if len(update["features"]) == 0 else "\n".join(update["features"]),
                            inline = False
                        ).add_field(
                            name = "Fixes",
                            value = "No New Fixes Were Made." if len(update["fixes"]) == 0 else "\n".join(update["fixes"]),
                            inline = False
                        )
                    )
                
            # Send webhook to Integromat
            # Split up features and fixes into platform-specific
            #  Tumblr should be Markdown supported
            #  Twitter, Facebook, and Push Notification should be regular
            markdown = {
                "description": description,
                "features": "\n".join([
                    " - {}".format(feature) for feature in update["features"]
                ]) if len(update["features"]) > 0 else "No New Features.",
                "fixes": "\n".join([
                    " - {}".format(fix) for fix in update["fixes"]
                ]) if len(update["fixes"]) > 0 else "No New Fixes."
            }

            regular = {
                "description": description.replace("`", ""),
                "features": "\n".join([
                    " - {}".format(feature.replace("`", "")) for feature in update["features"]
                ]) if len(update["features"]) > 0 else "No New Features.",
                "fixes": "\n".join([
                    " - {}".format(fix.replace("`", "")) for fix in update["fixes"]
                ]) if len(update["fixes"]) > 0 else "No New Fixes."
            }

            await loop.run_in_executor(None,
                partial(
                    requests.post,
                    os.environ["INTEGROMAT_WEBHOOK_CALL"],
                    json = {
                        "version": version,
                        "markdown": markdown,
                        "regular": regular
                    }
                )
            )

            # Send to author
            await ctx.send(
                embed = discord.Embed(
                    title = "Update Committed - (Version {})".format(update["version"]),
                    description = update["description"],
                    colour = PRIMARY_EMBED_COLOR
                ).add_field(
                    name = "Features",
                    value = "No New Features Were Made." if len(update["features"]) == 0 else "\n".join(update["features"]),
                    inline = False
                ).add_field(
                    name = "Fixes",
                    value = "No New Fixes Were Made." if len(update["fixes"]) == 0 else "\n".join(update["fixes"]),
                    inline = False
                )
            )
    
    @commands.command(
        name = "todo",
        description = "Allows you to add, remove, or view the todo list.",
        cog_name = "Bot"
    )
    async def todo(self, ctx, action = None, *, item = None):

        todo_list = await database.bot.get_todo()

        # Check if action is going to add or remove
        if action in ["add", "a", "remove", "r"]:

            # Check if item wasn't given (or index)
            if item != None:

                # Check if author is a developer
                if str(ctx.author.id) in await database.bot.get_developers():
                    
                    # Check if action is adding
                    if action in ["add", "a"]:
                        await database.bot.add_todo_item(item)
                        await ctx.send(
                            embed = discord.Embed(
                                title = "Added item to todo list.",
                                description = "*{}*".format(item),
                                colour = PRIMARY_EMBED_COLOR
                            )
                        )
                    
                    # Action is remove
                    elif action in ["remove", "r"]:

                        # Check if index is in range
                        try:
                            item = int(item) - 1
                            if item < 0 or item >= len(todo_list):
                                raise ValueError()

                            item = await database.bot.remove_todo_item(item)
                            await ctx.send(
                                embed = discord.Embed(
                                    title = "Removed item from todo list.",
                                    description = "*{}*".format(item),
                                    colour = PRIMARY_EMBED_COLOR
                                )
                            )
                        
                        # Index is out of range
                        except:
                            await ctx.send(
                                embed = errors.get_error_message(
                                    "That index is out of range."
                                )
                            )
                    
                    # Action is invalid
                    else:
                        await ctx.send(
                            embed = errors.get_error_message(
                                "That action is invalid."
                            )
                        )
                
                # Author is not a developer
                else:
                    await ctx.send(
                        embed = errors.get_error_message(
                            "You do not have access to this function."
                        )
                    )
            
            # Item was None
            else:
                await ctx.send(
                    embed = errors.get_error_message(
                        "You need the {} of the item to {}.".format(
                            "description" if action in ["add", "a"] else "index",
                            "add" if action in ["add", "a"] else "remove"
                        )
                    )
                )
        
        # Action is merely to view
        else:

            # Add items to list
            fields = []
            field_text = ""
            count = 0
            for i in todo_list:
                count += 1

                i = "*{}.)* {}\n".format(
                    count, i
                )

                if len(field_text) + len(i) > FIELD_THRESHOLD:
                    fields.append(field_text)
                    field_text = ""
                
                field_text += i
            
            if len(field_text) > 0:
                fields.append(field_text)
            
            # Create embed
            embed = discord.Embed(
                title = "Todo List",
                description = "There's nothing in your todo list." if len(fields) == 0 else fields[0],
                colour = PRIMARY_EMBED_COLOR
            )

            for field in fields[1:]:
                embed.add_field(
                    name = "_ _",
                    value = field,
                    inline = False
                )
            
            # Send message
            await ctx.send(
                embed = embed
            )
    
    @commands.command(
        name = "addDeveloper",
        aliases = ["addDev"],
        description = "Allows you to add a developer to the bot.",
        cog_name = "Bot"
    )
    @commands.check(is_developer)
    async def add_developer(self, ctx, members: commands.Greedy[discord.Member] = []):

        # Check if there are no members in the list
        if len(members) == 0:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need to mention members to add as a developer."
                )
            )
        
        # There are members
        else:

            # Keep track of whether or not the member was added
            results = []
            for member in members:
                if not await database.bot.is_developer(member):
                    await database.bot.add_developer(str(member.id))
                    success = True
                    reason = "{} ({}) was added as a developer.".format(member.mention, member)
                else:
                    success = False
                    reason = "{} ({}) is already a developer.".format(member.mention, member)
                
                results.append({"success": success, "reason": reason})
            
            await ctx.send(
                embed = discord.Embed(
                    title = "Members Added" if len(results) > len([result for result in results if not result["success"]]) else "Members Not Added",
                    description = "\n".join([result["reason"] for result in results]),
                    colour = PRIMARY_EMBED_COLOR
                )
            )
        
    @commands.command(
        name = "removeDeveloper",
        aliases = ["removeDev", "remDeveloper", "remDev"],
        description = "Allows you to remove a developer from the bot.",
        cog_name = "Bot"
    )
    @commands.check(is_developer)
    async def remove_developer(self, ctx, members: commands.Greedy[discord.Member] = []):
        
        # Check if there are no members in the list
        if len(members) == 0:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need to mention members to remove as a developer."
                )
            )
        
        # There are members
        else:

            # Keep track of whether or not the member was removed
            results = []
            for member in members:
                if await database.bot.is_developer(member):

                    # Make sure it's not self
                    if ctx.author == member:
                        success = True
                        reason = "You can't remove yourself as a developer."
                    
                    # Make sure it's not owner
                    elif str(member.id) == await database.bot.get_owner():
                        success = True
                        reason = "You can't remove the bot's owner as a developer."
                    
                    # Everything is good
                    else:
                        await database.bot.remove_developer(str(member.id))
                        success = True
                        reason = "{} ({}) was removed as a developer.".format(member.mention, member)
                else:
                    success = False
                    reason = "{} ({}) was not a developer.".format(member.mention, member)
                
                results.append({"success": success, "reason": reason})
            
            await ctx.send(
                embed = discord.Embed(
                    title = "Members Removed" if len(results) > len([result for result in results if not result["success"]]) else "Members Not Removed",
                    description = "\n".join([result["reason"] for result in results]),
                    colour = PRIMARY_EMBED_COLOR
                )
            )
    
    @commands.command(
        name = "rules",
        description = "Sends the rules for Fellow Hashbrown's private server.",
        cog_name = "Bot"
    )
    @commands.check(is_developer)
    @is_in_guild(int(os.environ["DEVELOPER_SERVER"]))
    async def rules(self, ctx):

        embed = discord.Embed(
            title = "Welcome To My Server!",
            description = (
                """
                First off, thanks for joining! It means a lot to know that people support me and my growth as a developer.
                Any pointers and such can go in the <#521216139213144066> channel. I appreciate all feedback!
                """
            ),
            colour = 0xEC7600,
            timestamp = datetime.now()
        ).set_author(
            name = "Fellow Hashbrown",
            url = "https://www.fellowhashbrown.com",
            icon_url = ctx.author.avatar_url
        ).add_field(
            name = ":book: Rules",
            value = (
                """
                1.) Be respectful to others.
                2.) Hate speech will not be tolerated.
                3.) Keep personal beef in the DMs.
                4.) Self-promotion is okay. Just try not to spam it.
                5.) All arguments/discussions between people is okay (Politics, moral stuff, etc.), but keep it civil.
                6.) Any violators will be subject to a temporary mute.
                7.) Try keeping memes and any off topic talk in <#521186307922329603> or <#521196475032535050>.
                8.) Anything that is NSFW must stay in NSFW channels. Violators will be subject to a temporary mute as well.
                9.) Enjoy the server :grinning:
                """
            )
        ).add_field(
            name = ":vibration_mode: Project Notifications",
            value = (
                """
                I set up my server so that you can choose which projects, APIs, or other stuff to follow.
                
                Projects (`!projects` to get access to all projects):
                `2054` --> **`!2054`**
                `Element Generator` --> **`!elementgenerator`**
                `Invasion` --> **`!invasion`**
                `Omega Psi` --> **`!omegapsi`**
                `Website` --> **`!website`**

                To do the invert of each command, just add `stop` in front of it.
                (i.e. `!stop2054`, `!stopprojects`)
                """
            )
        ).add_field(
            name = ":vibration_mode: API Notifications",
            value = (
                """
                APIs (`!apis` to get access to all APIs):
                `Hangman API` --> **`!hangmanapi`**
                `Scramble API` --> **`!scrambleapi`**
                `Morse API` --> **`!morseapi`**
                `Logic API` --> **`!logicapi`**
                `Profanity API` --> **`!profanityapi`**
                `Llamas API` --> **`!llamasapi`**
                `Office API` --> **`!officeapi`**

                To do the invert of each command, just add `stop` in front of it.
                (i.e. `!stopmorseapi`)
                """
            )
        ).add_field(
            name = ":vibration_mode: Other Notifications",
            value = (
                """
                `Twitch Notifications` --> **`!twitch`**

                To do the invert of each command, just add `stop` in front of it.
                (i.e. `!stoptwitch`)
                """
            )
        ).add_field(
            name = ":bulb: Server Access",
            value = (
                """
                This server doesn't just function as my developer server. I also have sections based around other things.
                Here is a list of sections and their commands:
                
                `The Office` --> **`!office`**
                `Parks and Rec` --> **`!pnr`**
                `Brooklyn 99` --> **`!b99`**

                To do the invert of each command, just add `stop` in front of it.
                (i.e. `!stoppnr`)
                """
            )
        ).add_field(
            name = ":desktop: Social Media",
            value = (
                """
                Below are social media and coding links of mine and my website too! (Which you can also get to by clicking my name at the top of this embed)
                Just click on the icons!
                
                [<:instagram:538799450693566494>](https://instagram.com/FellowHashbrown) [<:facebook:538799482880655383>](https://facebook.com/FellowHashbrown) [<:twitter:538799503457779713>](https://twitter.com/FellowHashbrown) [<:tumblr:538799532159270932>](https://fellowhashbrown.tumblr.com) [<:twitch:538799516850323497>](https://twitch.tv/FellowHashbrown) [<:github:538799471912419350>](https://github.com/FellowHashbrown) [<:repl_it:538799640263393281>](https://repl.it/@FellowHashbrown) [<:fellow_hashbrown:538800208008577074>](https://www.fellowhashbrown.com)
                """
            )
        )

        await ctx.send(
            embed = embed
        )
    
    @commands.command(
        name = "botTemplate",
        description = "Sends the template for submitting a bot in Fellow Hashbrown's private server.",
        cog_name = "Bot"
    )
    @commands.check(is_developer)
    @is_in_guild(int(os.environ["DEVELOPER_SERVER"]))
    async def bot_template(self, ctx):

        # Create bot submission template
        embed = discord.Embed(
            title = "Submit a Bot!",
            description = "Do you have a bot of your own you'd like on this server?\nDo you know of a bot (that may not be yours) and would like it here?\n**Submit It Then!**",
            colour = PRIMARY_EMBED_COLOR
        ).add_field(
            name = "Template",
            value = (
                "`Bot Name:`\n" +
                "`Bot Prefix:`\n" +
                "`Bot Source:` *(if available. if not, don't add this)*\n" +
                "`Bot Invite Link:`\n"
            ),
            inline = False
        ).add_field(
            name = "Rules to Follow",
            value = (
                "If a bot needs minimal permissions, (i.e. permissions that don't manage the server), it might be added depending on how the bot functions.\n" +
                "Any bot that allows NSFW content in SFW channels will not be added until it is fixed.\n" +
                "Bot commands must be activated by a prefix. If a bot responds to phrases, it will not be added.\n" +
                "If there is a leveling system in your bot, please deactivate it for this server. If you don't deactivate it after 3 notices, your bot will be muted until it is deactivated.\n"
            ),
            inline = False
        )

        await ctx.send(
            embed = embed
        )

    # # # # # # # # # # # # # # # # # # # # # # # # #
    
    @restart.error
    async def developer_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(
                embed = errors.get_error_message(
                    "You need to be a bot developer to run that."
                )
            )

def setup(bot):
    bot.add_cog(Bot(bot))