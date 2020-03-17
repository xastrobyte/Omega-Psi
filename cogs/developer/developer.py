from asyncio import wait, FIRST_COMPLETED
from discord import Embed, Member
from discord.ext.commands import Cog, group, command, Greedy
from functools import partial
from os import environ
from requests import post

from cogs.errors import get_error_message
from cogs.globals import PRIMARY_EMBED_COLOR, SCROLL_REACTIONS, CHECK_MARK, FIRST_PAGE, LAST_PAGE, PREVIOUS_PAGE, NEXT_PAGE, LEAVE, loop
from cogs.predicates import is_developer

from util.database.database import database
from util.discord import update_top_gg
from util.functions import get_embed_color, add_scroll_reactions, create_fields, add_fields
from util.string import dict_to_datetime

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

FEATURE_TYPES = {
    "🟩": "added", 
    "🟥": "removed", 
    "🟪": "changed", 
    "🟦": "fixed", 
    "🟫": "deprecated", 
    "🟨": "security"
}

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class Developer(Cog, name = "developer"):
    """Developers only ;)"""
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @command(
        name = "updateTopGG",
        aliases = ["updateDBL"],
        description = "Updates the server count on top.gg",
        cog_name = "developer"
    )
    @is_developer()
    async def update_top_gg(self, ctx):
        await update_top_gg(self.bot)
        await ctx.send(
            embed = Embed(
                title = "Omega Psi Updated on top.gg",
                description = "Omega Psi's server count on top.gg has been updated! Omega Psi is in {} servers".format(len(self.bot.guilds)),
                colour = await get_embed_color(ctx.author)
            )
        )

    @command(
        name = "addDeveloper",
        aliases = ["addDev"],
        description = "Adds a new developer to the bot.",
        cog_name = "developer"
    )
    @is_developer()
    async def add_developer(self, ctx, members : Greedy[Member] = []):

        # Check if there are no members in the list
        if len(members) == 0:
            await ctx.send(embed = get_error_message("You need to mention members to add as a developer."))
        
        # There are members
        else:
            results = []
            for member in members:
                if not await database.bot.is_developer(member):
                    await database.bot.add_developer(str(member.id))
                    success = True
                    reason = "{} was added as a developer.".format(str(member))
                else:
                    success = False
                    reason = "{} is already a developer.".format(str(member))
                results.append({"success": success, "reason": reason})
            
            await ctx.send(
                embed = Embed(
                    title = "Members Added" if len(results) > len([result for result in results if not result["success"]]) else "Members Not Added",
                    description = "\n".join([result["reason"] for result in results]),
                    colour = await get_embed_color(ctx.author)
                )
            )

    @command(
        name = "removeDeveloper",
        aliases = ["removeDev", "remDeveloper", "remDev"],
        description = "Allows you to remove a developer from the bot.",
        cog_name = "bot"
    )
    @is_developer()
    async def remove_developer(self, ctx, members: Greedy[Member] = []):
        
        # Check if there are no members in the list
        if len(members) == 0:
            await ctx.send(embed = get_error_message("You need to mention members to remove as a developer."))
        
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
                        reason = "{} was removed as a developer.".format(str(member))
                else:
                    success = False
                    reason = "{} was not a developer.".format(str(member))
                
                results.append({"success": success, "reason": reason})
            
            await ctx.send(
                embed = Embed(
                    title = "Members Removed" if len(results) > len([result for result in results if not result["success"]]) else "Members Not Removed",
                    description = "\n".join([result["reason"] for result in results]),
                    colour = await get_embed_color(ctx.author)
                )
            )
    
    @command(
        name = "createUpdate",
        description = "Creates a new pending update.",
        cog_name = "developer"
    )
    @is_developer()
    async def create_update(self, ctx):

        # Check if there is an existing pending update, dont overwrite it
        pending_update = await database.bot.get_pending_update()
        if len(pending_update) != 0:
            embed = Embed(
                title = "Existing Pending Update",
                description = "There is already a pending update!",
                colour = await get_embed_color(ctx.author)
            )
        
        # There is no pending update, create it
        else:
            await database.bot.create_pending_update()
            embed = Embed(
                title = "Pending Update Created",
                description = "A new pending update has been created. Use the `createFeature` command to add a new feature to the update.",
                colour = await get_embed_color(ctx.author)
            )
        await ctx.send(embed = embed)
    
    @command(
        name = "createFeature",
        aliases = ["addFeature", "newFeature"],
        description = "Adds a new feature to the current pending update.",
        cog_name = "developer"
    )
    @is_developer()
    async def create_feature(self, ctx, *, feature = None):
        pending_update = await database.bot.get_pending_update()

        # Check if no feature is given
        if not feature:
            embed = get_error_message("You must specify the feature you want to add")
        
        # Check if there is no pending update
        elif len(pending_update) == 0:
            embed = Embed(
                title = "No Pending Update",
                description = "There is currently no pending update to add this to. Use the `createUpdate` command to create a pending update.",
                colour = await get_embed_color(ctx.author)
            )
        
        # There is a pending update
        else:

            # Ask the user what kind of feature it is:
            #   added, removed, changed, fixed, deprecated, security
            message = await ctx.send(
                embed = Embed(
                    title = "Feature Type?",
                    description = "React with the type of feature this is\n{}".format(
                        "\n".join([
                            "`{}` -> {}".format(FEATURE_TYPES[feature_type], feature_type)
                            for feature_type in FEATURE_TYPES
                        ])
                    ),
                    colour = await get_embed_color(ctx.author)
                )
            )
            for emoji in FEATURE_TYPES:
                await message.add_reaction(emoji)
            
            reaction, user = await self.bot.wait_for("reaction_add", check = lambda reaction, user: (
                reaction.message.id == message.id and
                user.id == ctx.author.id and
                str(reaction) in FEATURE_TYPES
            ))
            feature_type = FEATURE_TYPES[str(reaction)]
            await message.delete()

            # Add the feature to the database
            await database.bot.add_pending_feature(feature, feature_type)
            embed = Embed(
                title = "Feature Added",
                description = "\"{}\" has been added as a feature to the pending update.".format(feature),
                colour = await get_embed_color(ctx.author)
            )
        await ctx.send(embed = embed)
    
    @command(
        name = "commitUpdate",
        aliases = ["commit"],
        description = "Commits the pending update as a new update.",
        cog_name = "developer"
    )
    @is_developer()
    async def commit_update(self, ctx, version = None, *, description = None):

        # Check if the version parameter is not given
        if not version:
            embed = get_error_message("You need to specify the version")
        
        # Check if the description parameter is not given
        elif not description:
            embed = get_error_message("You need to specify the description")
        
        # The version and description of the update
        else:

            # Clear the file changes
            await database.bot.set_changed_files({})

            # Commit the update in the database and get the most recent
            await database.bot.commit_pending_update(version, description)
            update = await database.bot.get_recent_update()

            # Create an Embed to notify all developers
            devs = await database.bot.get_developers()
            for dev in devs:
                dev = self.bot.get_user(int(dev))

                # Send to other developers except author
                if dev.id != ctx.author.id:
                    embed = Embed(
                        title = "Update Committed by {} - (Version {})".format(
                            ctx.author, update["verson"]
                        ),
                        description = update["description"],
                        colour = await get_embed_color(ctx.author)
                    )
                    change_fields = create_fields(update["features"], key = lambda feature: (
                        "`{}` | {}".format(feature["type"], feature["feature"])
                    ))
                    add_fields(embed, "Changes", change_fields, empty_message = "No Changes Made")
                    await dev.send(embed = embed)

            # (future update) Notify users who want to be notified about the update
            # Send an embed to the announcements channel
            announcements_embed = embed = Embed(
                title = "New Update! Version {}".format(version),
                description = description,
                colour = PRIMARY_EMBED_COLOR
            )
            fields = create_fields(update["features"], key = lambda feature: (
                "`{}` | {}".format(feature["type"], feature["feature"])
            ))
            add_fields(announcements_embed, "Changes", fields, empty_message = "No Changes Made")
            await self.bot.get_channel(int(environ["ANNOUNCEMENTS_OMEGA_PSI"])).send(
                "@everyone", embed = announcements_embed
            )

            # Send a webhook to integromat to update Facebook, Twitter, GitHub, etc.
            markdown = {
                "description": description,
                "changes": "\n".join([
                    " * `{}` | {}".format(
                        feature["type"],
                        feature["feature"]
                    )
                    for feature in update["features"]
                ])
            }
            regular = {
                "description": description.replace("`", ""),
                "changes": "\n".join([
                    " * |{}| - {}".format(
                        feature["type"],
                        feature["feature"].replace("`", "\'")
                    )
                    for feature in update["features"]
                ])
            }
            await loop.run_in_executor(None,
                partial(
                    post, environ["INTEGROMAT_WEBHOOK_CALL"],
                    json = {
                        "version": version,
                        "markdown": markdown,
                        "regular": regular
                    }
                )
            )

        await ctx.send(embed = embed)
    
    @group(
        name = "bugs",
        description = "Shows you a list of unseen bugs reported in the bot.",
        cog_name = "developer"
    )
    @is_developer()
    async def bugs(self, ctx):
        if not ctx.invoked_subcommand:
            await self.view_cases(ctx)
        
    @bugs.command(
        name = "all",
        description = "Shows you a list of all bugs reported in the bot.",
        cog_name = "developer"
    )
    @is_developer()
    async def bugs_all(self, ctx):
        await self.view_cases(ctx, unseen_only = False)
    
    @bugs.command(
        name = "find",
        description = "Searches for a specific bug report.",
        cog_name = "developer"
    )
    @is_developer()
    async def bugs_find(self, ctx, bug_case = None):

        # Check if there is no specific bug case referenced
        if not bug_case:
            await ctx.send(
                embed = get_error_message("You must specify a specific bug case number to look at.")
            )
        
        # There was a specific bug case referenced
        else:
            await self.view_cases(ctx, specific = bug_case, unseen_only = False)
    
    @group(
        name = "suggestions",
        description = "Shows you a list of unseen suggestions in the bot.",
        cog_name = "developer"
    )
    @is_developer()
    async def suggestions(self, ctx):
        if not ctx.invoked_subcommand:
            await self.view_cases(ctx, bugs = False)
        
    @suggestions.command(
        name = "all",
        description = "Shows you a list of all suggestions in the bot.",
        cog_name = "developer"
    )
    @is_developer()
    async def suggestions_all(self, ctx):
        await self.view_cases(ctx, bugs = False, unseen_only = False)
    
    @suggestions.command(
        name = "find",
        description = "Searches for a specific suggestion.",
        cog_name = "developer"
    )
    @is_developer()
    async def suggestions_find(self, ctx, suggestion_case = None):

        # Check if there is no specific suggestion case referenced
        if not suggestion_case:
            await ctx.send(
                embed = get_error_message("You must specify a specific suggestion case number to look at.")
            )
        
        # There was a specific suggestion case referenced
        else:
            await self.view_cases(ctx, specific = suggestion_case, bugs = False, unseen_only = False)

    @command(
        name = "globallyEnableCommand",
        description = "Enables a specified command in the entire bot",
        cog_name = "developer"
    )
    @is_developer()
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
                enabled = await database.bot.enable_command(cmd.qualified_name)
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
        name = "globallyDisableCommand",
        description = "Disables a specified command in the entire bot",
        cog_name = "developer"
    )
    @is_developer()
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
                disabled = await database.bot.disable_command(cmd.qualified_name)
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

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def view_cases(self, ctx, specific = None, *, bugs = True, unseen_only = True):
        """Let's a user view and scroll through given case numbers pertaining to either
        bug reports or suggestions

        Parameters
        ----------
            ctx : Context
                The current context of where the command was run
            specific : str
                The specific case to look at first
        
        Keyword Parameters
        ------------------
            bugs : boolean  
                Whether or not the cases passed through are bug cases
            unseen_only : boolean
                Whether or not to view only unseen cases
        """

        # Check if the cases are from bug reports or suggestions
        case_id = "bug" if bugs else "suggestion"
        if bugs:
            cases = await database.case_numbers.get_bug_cases()
        else:
            cases = await database.case_numbers.get_suggestion_cases()
        cases = cases["cases"]
        
        # Get a list of all unseen cases in the bot
        cases = {
            case: cases[case]
            for case in cases
            if not unseen_only or not cases[case]["seen"]
        }

        # Check if there are any unseen bugs
        if len(cases) > 0:

            # Keep track of the case numbers, the current case, and 
            #   create a lambda function to get the current case with ease
            case_numbers = list(cases.keys())
            current_case = 0
            get_case = lambda current_case: cases[case_numbers[current_case]]

            # Check if the user wants to start at a specific case number
            #   if the case number is not found, the current case number still starts
            #   at the lowest one
            if specific != None:
                if specific in case_numbers:
                    current_case = case_numbers.index(specific)
                else:
                    current_case = -1
                    await ctx.send(embed = get_error_message("There are no cases with the specified case number."))

            # Setup an embed to view the current unseen bug case
            if current_case != -1:
                author = self.bot.get_user(int(get_case(current_case)["author"]))
                developer = self.bot.get_user(int(get_case(current_case)["seen"]))
                embed = Embed(
                    title = "Bugs" if bugs else "Suggestions",
                    description = "**{} #{}**: {}{}\n**Author**: {}".format(
                        "Bug" if bugs else "Suggestion", case_numbers[current_case], get_case(current_case)[case_id],
                        "\n**Source**: `{}` - {}".format(
                            get_case(current_case)["source_type"],
                            get_case(current_case)["source"],
                        ) if bugs else "",
                        str(author)
                    ),
                    colour = await get_embed_color(ctx.author),
                    timestamp = dict_to_datetime(get_case(current_case)["time"])
                ).set_footer(
                    text = "{} Seen? {} {}".format(
                        "Bug" if bugs else "Suggestion",
                        CHECK_MARK if get_case(current_case)["seen"] else LEAVE,
                        "By {}".format(
                            str(developer)
                        ) if get_case(current_case)["seen"] else ""
                    )
                )

                # Let the user view all the bug reports in a scrolling embed
                message = await ctx.send(embed = embed)
                await add_scroll_reactions(message, cases)
                await message.add_reaction(CHECK_MARK)
                while True:
                    
                    # Wait for the user to react with what reaction they want to do
                    #   i.e. left arrow moves to the case to the left (if any)
                    check_reaction = lambda reaction, user: (
                        reaction.message.id == message.id and
                        user.id == ctx.author.id and
                        str(reaction) in (SCROLL_REACTIONS + [CHECK_MARK])
                    )
                    done, pending = await wait([
                        self.bot.wait_for("reaction_add", check = check_reaction),
                        self.bot.wait_for("reaction_remove", check = check_reaction)
                    ], return_when = FIRST_COMPLETED)
                    reaction, user = done.pop().result()
                    for future in pending:
                        future.cancel()
                    
                    # Check if the reaction is the first page
                    if str(reaction) == FIRST_PAGE:
                        current_case = 0
                    
                    # The reaction is the last page
                    elif str(reaction) == LAST_PAGE:
                        current_case = len(case_numbers) - 1
                    
                    # The reaction is the previous page
                    elif str(reaction) == PREVIOUS_PAGE:
                        current_case -= 1 if current_case > 0 else 0
                    
                    # The reaction is the next page
                    elif str(reaction) == NEXT_PAGE:
                        current_case += 1 if current_case < len(case_numbers) - 1 else 0
                    
                    # The reaction is the check mark (mark case number as seen)
                    elif str(reaction) == CHECK_MARK and not get_case(current_case)["seen"]:

                        # Mark the case as seen
                        if bugs:
                            await database.case_numbers.mark_bug_seen(case_numbers[current_case], ctx.author)
                        else:
                            await database.case_numbers.mark_suggestion_seen(case_numbers[current_case], ctx.author)

                        # Notify the author that their case was seen
                        user = self.bot.get_user(int(get_case(current_case)["author"]))
                        if user:
                            try:
                                await user.send(
                                    embed = Embed(
                                        title = "{} Seen By Developer".format(
                                            "Bug Report" if bugs else "Suggestion"
                                        ),
                                        description = "{} has seen your {}".format(
                                            str(ctx.author),
                                            "bug report" if bugs else "suggestion"
                                        ),
                                        colour = await get_embed_color(user)
                                    ).add_field(
                                        name = "{} (#{})".format(
                                            "Bug" if bugs else "Suggestion",
                                            str(case_numbers[current_case])
                                        ),
                                        value = get_case(current_case)[case_id]
                                    )
                                )
                            except:
                                await ctx.send(
                                    embed = Embed(
                                        title = "Could Not Send Message",
                                        description = "Attempt to notify author of viewing {} failed.".format(
                                            "bug report" if bugs else "suggestion"
                                        ),
                                        colour = 0x800000
                                    ),
                                    delete_after = 15
                                )
                    
                    # The reaction is leave, delete the message and break from the loop
                    elif str(reaction) == LEAVE:
                        await message.delete()
                        break
                    
                    # Update the embed and the message
                    author = self.bot.get_user(int(get_case(current_case)["author"]))
                    developer = self.bot.get_user(int(get_case(current_case)["seen"]))
                    embed = Embed(
                        title = "Bugs" if bugs else "Suggestions",
                        description = "**{} #{}**: {}{}\n**Author**: {}".format(
                            "Bug" if bugs else "Suggestion", case_numbers[current_case], get_case(current_case)[case_id],
                            "\n**Source**: `{}` - {}".format(
                                get_case(current_case)["source_type"],
                                get_case(current_case)["source"],
                            ) if bugs else "",
                            str(author)
                        ),
                        colour = await get_embed_color(ctx.author),
                        timestamp = dict_to_datetime(get_case(current_case)["time"])
                    ).set_footer(
                        text = "{} Seen? {} {}".format(
                            "Bug" if bugs else "Suggestion",
                            CHECK_MARK if get_case(current_case)["seen"] else LEAVE,
                            "By {}".format(
                                str(developer)
                            ) if get_case(current_case)["seen"] else ""
                        )
                    )
                    await message.edit(embed = embed)
        
        # There are no unseen bugs
        else:
            await ctx.send(
                embed = Embed(
                    title = "No Unseen {}".format("Bug Reports" if bugs else "Suggestions"),
                    description = "There were no unseen {} found".format("bug reports" if bugs else "suggestions"),
                    colour = await get_embed_color(ctx.author)
                )
            )  

def setup(bot):
    bot.add_cog(Developer(bot))