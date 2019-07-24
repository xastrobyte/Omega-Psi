import asyncio, discord, os, requests, sys
from datetime import datetime
from discord.ext import commands
from functools import partial

from category import errors
from category.globals import FIELD_THRESHOLD, SCROLL_REACTIONS, FIRST_PAGE, LAST_PAGE, PREVIOUS_PAGE, NEXT_PAGE, CHECK_MARK, OUTBOX, LEAVE
from category.globals import add_scroll_reactions
from category.globals import get_embed_color
from category.globals import PRIMARY_EMBED_COLOR, OMEGA_PSI_CHANNEL
from category.predicates import is_developer, is_in_guild

from database import loop
from database import database

from util.discord import send_webhook
from util.email import send_email
from util.string import dict_to_datetime

# # # # # # # # # # # # # # # # # # # # # # # # #

class Bot(commands.Cog, name = "bot"):
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @commands.command(
        name = "newTheme",
        aliases = ["theme"],
        description = "Adds a new theme of the day for the bot. Date is in MMDD format.",
        cog_name = "bot"
    )
    @commands.check(is_developer)
    async def new_theme(self, ctx, date = None, dark = None, medium = None, light = None, *, description = None):

        # Check if date is None
        if date == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need to specify the date this theme shows up in format MMDD"
                )
            )
        
        # Check if any of the colors are None
        elif dark == medium == light == description == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need to specify the dark, medium, and light colors of the theme along with the description of the theme of the day."
                )
            )
        
        # Every parameter exists; Validate parameters
        else:

            try:

                # Make sure date is valid
                month = int(date[:2])
                day = int(date[2:])

                # Get datetime int for date
                date = "{}-{}".format(
                    month, day
                )

                # Make sure colors are valid
                for color in [dark, medium, light]:
                    if len(color) > 6:
                        raise SyntaxError()
                    
                    # Iterate through color string
                    for digit in color.lower():
                        if digit not in "0123456789abcdef":
                            raise SyntaxError()
                
                # Everything is valid; Add theme
                await database.bot.set_theme(date, dark, medium, light, description)

                await ctx.send(
                    embed = discord.Embed(
                        title = "Theme Added",
                        description = "That theme has been added and set for {}!\n**Dark**: {}\n**Medium**: {}\n**Light**: {}".format(
                            date.replace("-", "/"),
                            dark, medium, light
                        ),
                        colour = await get_embed_color(ctx.author),
                    )
                )
            
            except SyntaxError:
                await ctx.send(
                    embed = errors.get_error_message(
                        "One of the colors you gave is invalid."
                    )
                )

            except ValueError:
                await ctx.send(
                    embed = errors.get_error_message(
                        "The date you gave is invalid."
                    )
                )

    @commands.command(
        name = "suggestions",
        description = "Shows all suggestions made or a specific suggestion.",
        cog_name = "bot"
    )
    @commands.check(is_developer)
    async def suggestion_reports(self, ctx, data = None):

        # Get all suggestions
        # Check if getting all suggestion cases or just ones that have been seen
        suggestion_cases = await database.case_numbers.get_suggestion_cases()
        unseen = None

        # Check if unseen suggestions
        if data == "unseen":
            data = None
            unseen = True
            temp = suggestion_cases["cases"]
            suggestion_cases = {}
            for case in temp:
                if not temp[case]["seen"]:
                    suggestion_cases[case] = temp[case]
                    if data == None:
                        data = case

        # Check if seen suggestions
        elif data == "seen":
            data = None
            unseen = False
            temp = suggestion_cases["cases"]
            suggestion_cases = {}
            for case in temp:
                if temp[case]["seen"]:
                    suggestion_cases[case] = temp[case]
                    if data == None:
                        data = case
        
        # Check if getting all suggestions
        else:
            suggestion_cases = suggestion_cases["cases"]

        # Make sure suggestion exists or data is None
        if data == None or str(data) in suggestion_cases:

            # Only send scrolling message if there are cases
            if len(suggestion_cases) != 0:
                
                # Create embed
                current = 1 if data == None else int(data)
                author = self.bot.get_user(int(suggestion_cases[str(current)]["author"]))
                embed = discord.Embed(
                    title = "{}Suggestions".format(
                        "Unseen " if unseen == True else (
                            "Seen " if unseen == False else ""
                        )
                    ),
                    description = "**Suggestion #{}**: {}\n**Author**: {}".format(
                        str(current),
                        suggestion_cases[str(current)]["suggestion"],
                        "{} ({})".format(
                            author.mention, author
                        )
                    ),
                    colour = await get_embed_color(ctx.author),
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

                # Only add outbox reaction if suggestion hasn't been marked as seen
                if not suggestion_cases[str(current)]["seen"]:
                    await msg.add_reaction(OUTBOX)

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

                        while str(current) not in suggestion_cases and current < len(suggestion_cases):
                            current += 1

                    # Reaction is last page
                    elif str(reaction) == LAST_PAGE:
                        current = len(suggestion_cases)

                        while str(current) not in suggestion_cases and current > 1:
                            current -= 1

                    # Reaction is previous page
                    elif str(reaction) == PREVIOUS_PAGE:
                        current -= 1

                        while str(current) not in suggestion_cases and current > 1:
                            current -= 1

                        if current < 1:
                            current = 1

                    # Reaction is next page
                    elif str(reaction) == NEXT_PAGE:
                        current += 1

                        while str(current) not in suggestion_cases and current < len(suggestion_cases):
                            current += 1

                        if current > len(suggestion_cases):
                            current = len(suggestion_cases)
                    
                    # Reaction is outbox (send suggestion to suggestion channel)
                    # Only test for reaction if suggestion hasn't been marked as seen
                    elif str(reaction) == OUTBOX and not suggestion_cases[str(current)]["seen"]:

                        # Get suggestion channel
                        channel = self.bot.get_channel(int(os.environ["SUGGESTION_CHANNEL"]))
                        user = self.bot.get_user(int(suggestion_cases[str(current)]["author"]))
                        await channel.send(
                            embed = discord.Embed(
                                title = "Suggestion #{}".format(str(current)),
                                description = suggestion_cases[str(current)]["suggestion"],
                                colour = await get_embed_color(ctx.author),
                                timestamp = datetime.now()
                            ).add_field(
                                name = "Submitted By",
                                value = "Unknown" if user == None else "{} ({})".format(
                                    user.mention, str(user)
                                ),
                                inline = False
                            )
                        )
                        
                    # Reaction is check mark (suggestion marked as seen)
                    elif str(reaction) == CHECK_MARK:
                        if not suggestion_cases[str(current)]["seen"]:

                            # Notify author that their suggestion was seen
                            user = self.bot.get_user(int(suggestion_cases[str(current)]["author"]))
                            if user != None:
                                try:
                                    await user.send(
                                        embed = discord.Embed(
                                            title = "Suggestion Seen By Developer",
                                            description = " ",
                                            colour = await get_embed_color(ctx.author),
                                            timestamp = datetime.now()
                                        ).add_field(
                                            name = "Suggestion (#{})".format(str(current)),
                                            value = suggestion_cases[str(current)]["suggestion"],
                                            inline = False
                                        )
                                    )
                                except:

                                    # Send the person an email if it can
                                    sent_email = False
                                    if "email" in suggestion_cases[str(current)]:

                                        try:
                                            await loop.run_in_executor(None,
                                                send_email,
                                                suggestion_cases[str(current)]["email"],
                                                "Suggestion Case (#{})".format(str(current)),
                                                "Your suggestion was seen by a developer.\n{}".format(
                                                    suggestion_cases[str(current)]["suggestion"]
                                                ),
                                                "<p>Your suggestion was seen by a developer.</p><br><em>{}</em>".format(
                                                    suggestion_cases[str(current)]["suggestion"]
                                                )
                                            )
                                            sent_email = True
                                        except:
                                            pass

                                    await ctx.send(
                                        embed = discord.Embed(
                                            title = "Could Not Send Message",
                                            description = "I tried sending the message to the suggestor but they didn't allow me to send the message.\n{}".format(
                                                "I could not send them an email either." if not sent_email else "I did send them an email."
                                            ),
                                            colour = 0x800000
                                        ),
                                        delete_after = 10
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
                        title = "{}Suggestions".format(
                            "Unseen " if unseen == True else (
                                "Seen " if unseen == False else ""
                            )
                        ),
                        description = "**Suggestion #{}**: {}\n**Author**: {}".format(
                            str(current),
                            suggestion_cases[str(current)]["suggestion"],
                            "{} ({})".format(
                                author.mention, author
                            )
                        ),
                        colour = await get_embed_color(ctx.author),
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
                        description = "There are currently no {}suggestions.".format(
                            "unseen " if unseen == True else (
                                "seen " if unseen == False else ""
                            )
                        ),
                        colour = await get_embed_color(ctx.author)
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
        cog_name = "bot"
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
                        colour = await get_embed_color(ctx.author)
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
                    colour = await get_embed_color(ctx.author)
                )
            )

            # Send the bug to the discord channel dedicated to suggestions
            await send_webhook(
                os.environ["SUGGESTION_WEBHOOK"],
                discord.Embed(
                    title = "Suggestion (#{})".format(suggestion_number),
                    description = " ",
                    colour = await get_embed_color(ctx.author)
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
    
    @commands.command(
        name = "bugs",
        description = "Shows all bug reports made or a specific bug report.",
        cog_name = "bot"
    )
    @commands.check(is_developer)
    async def bug_reports(self, ctx, data = None):
        
        # Get all bugs
        bug_cases = await database.case_numbers.get_bug_cases()
        unseen = None

        # Check if getting unseen reports
        if data == "unseen":
            data = None
            unseen = True
            temp = bug_cases["cases"]
            bug_cases = {}
            for case in temp:
                if not temp[case]["seen"]:
                    bug_cases[case] = temp[case]
                    if data == None:
                        data = case
        
        # Check if getting seen reports
        elif data == "seen":
            data = None
            unseen = False
            temp = bug_cases["cases"]
            bug_cases = {}
            for case in temp:
                if temp[case]["seen"]:
                    bug_cases[case] = temp[case]
                    if data == None:
                        data = case
        
        # Check if getting all reports
        else:
            bug_cases = bug_cases["cases"]

        # Make sure bug exists or data is None
        if data == None or str(data) in bug_cases:

            # Only send scrolling message if there are cases
            if len(bug_cases) != 0:
                
                # Create embed
                current = 1 if data == None else int(data)
                author = self.bot.get_user(int(bug_cases[str(current)]["author"]))
                embed = discord.Embed(
                    title = "{}Bugs".format(
                        "Unseen " if unseen == True else (
                            "Seen " if unseen == False else ""
                        )
                    ),
                    description = "**Bug #{}**: {}\n**Author**: {}".format(
                        str(current),
                        bug_cases[str(current)]["bug"],
                        "{} ({})".format(
                            author.mention, author
                        )
                    ),
                    colour = await get_embed_color(ctx.author),
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

                # Only add outbox reaction is bug hasn't been marked as seen
                if not bug_cases[str(current)]["seen"]:
                    await msg.add_reaction(OUTBOX)

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

                        while str(current) not in bug_cases and current < len(bug_cases):
                            current += 1

                    # Reaction is last page
                    elif str(reaction) == LAST_PAGE:
                        current = len(bug_cases)

                        while str(current) not in bug_cases and current > 1:
                            current -= 1

                    # Reaction is previous page
                    elif str(reaction) == PREVIOUS_PAGE:
                        current -= 1

                        while str(current) not in bug_cases and current > 1:
                            current -= 1

                        if current < 1:
                            current = 1

                    # Reaction is next page
                    elif str(reaction) == NEXT_PAGE:
                        current += 1

                        while str(current) not in bug_cases and current < len(bug_cases):
                            current += 1

                        if current > len(bug_cases):
                            current = len(bug_cases)
                    
                    # Reaction is outbox (send bug to bug channel)
                    # Only test for reaction if bug has not been marked as seen
                    elif str(reaction) == OUTBOX and not bug_cases[str(current)]["seen"]:

                        # Get bug channel
                        channel = self.bot.get_channel(int(os.environ["BUG_CHANNEL"]))
                        user = self.bot.get_user(int(bug_cases[str(current)]["author"]))
                        await channel.send(
                            embed = discord.Embed(
                                title = "Bug #{}".format(str(current)),
                                description = bug_cases[str(current)]["bug"],
                                colour = await get_embed_color(ctx.author),
                                timestamp = datetime.now()
                            ).add_field(
                                name = "Submitted By",
                                value = "Unknown" if user == None else "{} ({})".format(
                                    user.mention, str(user)
                                ),
                                inline = False
                            )
                        )
                        
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
                                        colour = await get_embed_color(ctx.author),
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
                        title = "{}Bugs".format(
                            "Unseen " if unseen == True else (
                                "Seen " if unseen == False else ""
                            )
                        ),
                        description = "**Bug #{}**: {}\n**Author**: {}".format(
                            str(current),
                            bug_cases[str(current)]["bug"],
                            "{} ({})".format(
                                author.mention, author
                            )
                        ),
                        colour = await get_embed_color(ctx.author),
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
                        description = "There are currently no {}bug reports.".format(
                            "unseen " if unseen == True else (
                                "seen " if unseen == False else ""
                            )
                        ),
                        colour = await get_embed_color(ctx.author)
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
        cog_name = "bot"
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
                        colour = await get_embed_color(ctx.author)
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
                    colour = await get_embed_color(ctx.author)
                )
            )

            # Send the bug to the discord channel dedicated to bugs
            await send_webhook(
                os.environ["BUG_WEBHOOK"],
                discord.Embed(
                    title = "Bug (#{})".format(bug_number),
                    description = " ",
                    colour = await get_embed_color(ctx.author)
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
    
    @commands.command(
        name = "setRefresh",
        aliases = ["setR"],
        description = "Allows you to set a refresh time for members who vote for Omega Psi on DBL. The refresh time should be in days.",
        cog_name = "bot"
    )
    @commands.check(is_developer)
    async def set_refresh(self, ctx, member : discord.Member = None, refresh_time : int = None):

        # Check if member is None
        if member == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need to mention the person you want to set the vote refresh time for."
                )
            )
        
        # A member was mentioned
        else:

            # Check if refresh_time is None; Default back to 2 days
            if refresh_time == None:
                refresh_time = 2
            
            # Set the refresh time for the member
            await database.users.set_refresh_vote(member, refresh_time)

            await ctx.send(
                embed = discord.Embed(
                    title = "Refresh Time Updated",
                    description = "The refresh time for {} has been updated to {} days".format(
                        member.mention, refresh_time
                    ),
                    colour = await self.get_embed_color(ctx.author)
                )
            )

    @commands.command(
        name = "servers",
        aliases = ["serverList", "sl"],
        description = "Shows you a list of servers that Omega Psi is in.",
        cog_name = "bot"
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
                colour = await get_embed_color(ctx.author)
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
                    colour = await get_embed_color(ctx.author)
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
        cog_name = "bot"
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
        cog_name = "bot"
    )
    @commands.check(is_developer)
    async def kill(self, ctx):

        await ctx.send(
            "Bye! {}".format(ctx.author.mention)
        )

        await self.bot.logout()
    
    @commands.command(
        name = "update",
        description = "Shows you information about the most recent update to the bot and the pending update if any.",
        cog_name = "bot"
    )
    async def update(self, ctx, *, get_all = None):

        # Check if get_all is in the list to get all updates
        get_all = get_all in ["all", "all updates"]

        # Check if getting all updates in a scrolling embed
        if get_all:
            
            # Get all the updates
            updates = await database.bot.get_updates()

            # Create the embed
            embed = discord.Embed(
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
                "Features": "\n".join(updates[current]["features"]) if len(updates[current]["features"]) > 0 else "No Features Added.",
                "Fixes": "\n".join(updates[current]["fixes"]) if len(updates[current]["fixes"]) > 0 else "No Fixes Made."
            }

            # Add all fields to embed
            for field in fields:

                # See if field extends past threshold
                sub_fields = []
                sub_field_text = ""

                field_lines = fields[field].split("\n")

                for line in field_lines:

                    line += "\n"

                    if len(sub_field_text) + len(line) > FIELD_THRESHOLD:
                        sub_fields.append(sub_field_text)
                        sub_field_text = ""
                    
                    sub_field_text += line
                
                if len(sub_field_text) > 0:
                    sub_fields.append(sub_field_text)
                
                # Add each sub_field
                count = 0
                for sub_field in sub_fields:
                    count += 1
                    embed.add_field(
                        name = field + "{}".format(
                            "({} / {})".format(
                                count, len(sub_fields)
                            ) if len(sub_fields) > 1 else ""
                        ),
                        value = sub_field,
                        inline = False
                    )
            
            # Send message
            msg = await ctx.send(
                embed = embed
            )
            
            # Add necessary scroll reactions
            await add_scroll_reactions(msg, updates)

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
                    await msg.delete()
                    break
                
                # Update the fields and embeds
                embed = discord.Embed(
                    title = "Updates",
                    description = "Here's a list of updates to Omega Psi in order of most recent to oldest.",
                    colour = await get_embed_color(ctx.author)
                )

                # Setup fields
                fields = {
                    "Release Date": updates[current]["date"],
                    "Version": updates[current]["version"],
                    "Description": updates[current]["description"],
                    "Features": "\n".join(updates[current]["features"]) if len(updates[current]["features"]) > 0 else "No Features Added.",
                    "Fixes": "\n".join(updates[current]["fixes"]) if len(updates[current]["fixes"]) > 0 else "No Fixes Made."
                }

                # Add all fields to embed
                for field in fields:

                    # See if field extends past threshold
                    sub_fields = []
                    sub_field_text = ""

                    field_lines = fields[field].split("\n")

                    for line in field_lines:

                        line += "\n"

                        if len(sub_field_text) + len(line) > FIELD_THRESHOLD:
                            sub_fields.append(sub_field_text)
                            sub_field_text = ""
                        
                        sub_field_text += line
                    
                    if len(sub_field_text) > 0:
                        sub_fields.append(sub_field_text)
                    
                    # Add each sub_field
                    count = 0
                    for sub_field in sub_fields:
                        count += 1
                        embed.add_field(
                            name = field + "{}".format(
                                "({} / {})".format(
                                    count, len(sub_fields)
                                ) if len(sub_fields) > 1 else ""
                            ),
                            value = sub_field,
                            inline = False
                        )
                    
                await msg.edit(
                    embed = embed
                )
        
        # Just getting the most recent
        else:

            # Get the recent update data
            recent_update = await database.bot.get_recent_update()

            # Create the embed
            embed = discord.Embed(
                title = "Updates",
                description = "Here's the most recent update to Omega Psi.",
                colour = await get_embed_color(ctx.author)
            )

            fields = {
                "Release Date": recent_update["date"],
                "Version": recent_update["version"],
                "Description": recent_update["description"],
                "Features": "\n".join(recent_update["features"]) if len(recent_update["features"]) > 0 else "No Features Added.",
                "Fixes": "\n".join(recent_update["fixes"]) if len(recent_update["fixes"]) > 0 else "No Fixes Made."
            }

            # Add all fields to embed
            for field in fields:

                # See if field extends past threshold
                sub_fields = []
                sub_field_text = ""

                field_lines = fields[field].split("\n")

                for line in field_lines:

                    line += "\n"

                    if len(sub_field_text) + len(line) > FIELD_THRESHOLD:
                        sub_fields.append(sub_field_text)
                        sub_field_text = ""
                    
                    sub_field_text += line
                
                if len(sub_field_text) > 0:
                    sub_fields.append(sub_field_text)
                
                # Add each sub_field
                count = 0
                for sub_field in sub_fields:
                    count += 1
                    embed.add_field(
                        name = field + " {}".format(
                            "({} / {})".format(
                                count, len(sub_fields)
                            ) if len(sub_fields) > 1 else ""
                        ),
                        value = sub_field,
                        inline = False
                    )

            await ctx.send(
                embed = embed
            )
    
    @commands.command(
        name = "pendingUpdate",
        aliases = ["pending"],
        description = "Shows you information about the current pending.",
        cog_name = "bot"
    )
    async def pending_update(self, ctx):

        # Get the pending update data
        pending_update = await database.bot.get_pending_update()

        # Create the embed
        embed = discord.Embed(
            title = "Updates",
            description = "Here's the current pending update to Omega Psi.",
            colour = await get_embed_color(ctx.author)
        )

        fields = {
            "Pending Update": "**Features**: {}\n**Fixes**: {}\n".format(
                "\n".join(pending_update["features"]) if len(pending_update["features"]) > 0 else "No Features Added Yet.",
                "\n".join(pending_update["fixes"]) if len(pending_update["fixes"]) > 0 else "No Fixes Made Yet."
            ) if pending_update != {} else "No Pending Update Yet"
        }

        # Add all fields to embed
        for field in fields:

            # See if field extends past threshold
            sub_fields = []
            sub_field_text = ""

            field_lines = fields[field].split("\n")

            for line in field_lines:

                line += "\n"

                if len(sub_field_text) + len(line) > FIELD_THRESHOLD:
                    sub_fields.append(sub_field_text)
                    sub_field_text = ""
                
                sub_field_text += line
            
            if len(sub_field_text) > 0:
                sub_fields.append(sub_field_text)
            
            # Add each sub_field
            count = 0
            for sub_field in sub_fields:
                count += 1
                embed.add_field(
                    name = field + "{}".format(
                        "({} / {})".format(
                            count, len(sub_fields)
                        ) if len(sub_fields) > 1 else ""
                    ),
                    value = sub_field,
                    inline = False
                )

        await ctx.send(
            embed = embed
        )
    
    @commands.command(
        name = "createUpdate",
        aliases = ["createUpd"],
        description = "Creates a new pending update to the bot.",
        cog_name = "bot"
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
                        colour = await get_embed_color(ctx.author)
                    )
                )
            
        # Send to user
        await ctx.send(
            embed = discord.Embed(
                title = "Pending Update Created!",
                description = "Use `createFix` and `createFeature` to add fixes or features to this pending update.",
                colour = await get_embed_color(ctx.author)
            )
        )
    
    @commands.command(
        name = "createFix",
        aliases = ["addFix"],
        description = "Adds a fix to the pending update.",
        cog_name = "bot"
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
                            colour = await get_embed_color(ctx.author)
                        )
                    )
            
            # Send to author
            await ctx.send(
                embed = discord.Embed(
                    title = "Fix Created",
                    description = fix,
                    colour = await get_embed_color(ctx.author)
                )
            )
    
    @commands.command(
        name = "createFeature",
        aliases = ["addFeature"],
        description = "Adds a feature to the pending update.",
        cog_name = "bot"
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
                            colour = await get_embed_color(ctx.author)
                        )
                    )
            
            # Send to author
            await ctx.send(
                embed = discord.Embed(
                    title = "Feature Created",
                    description = feature,
                    colour = await get_embed_color(ctx.author)
                )
            )
    
    @commands.command(
        name = "commitUpdate",
        aliases = ["commit"],
        description = "Commits the pending update as a new update.",
        cog_name = "bot"
    )
    @commands.check(is_developer)
    async def commit_update(self, ctx, version = None, *, description = None):
        
        # Check if version or description are None; Throw error message
        if version == None or (description == None and version not in ["recent", "r"]):
            await ctx.send(
                embed = errors.get_error_message(
                    "In order to commit the update, you need to establish the `version` and the `description` of this update."
                )
            )
        
        # Version and description are not None; Commit the update
        else:

            # Check if the commit version is "recent" or "r"
            # This means to just rerun the last commit command (last update)
            # as if it's a new commit
            if version in ["recent", "r"]:
                
                # Get the most recent update
                update = await database.bot.get_recent_update()

            else:

                # Commit the update. Then get the update so we can inform all other developers
                await database.bot.commit_pending_update(version, description)

                # Also clear the changed files
                await database.bot.set_changed_files({})
                update = await database.bot.get_recent_update()

                for dev in await database.bot.get_developers():

                    # Get the dev user object
                    user = self.bot.get_user(int(dev))

                    # Send to everyone except author
                    if user.id != ctx.author.id:
                        await user.send(
                            embed = discord.Embed(
                                title = "Update Committed by {} - (Version {})".format(
                                    ctx.author,
                                    update["version"]
                                ),
                                description = update["description"],
                                colour = await get_embed_color(ctx.author)
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
                        colour = await get_embed_color(ctx.author)
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

            # Send to Omega Psi channel
            channel = self.bot.get_channel(OMEGA_PSI_CHANNEL)
            await channel.send(
                "@everyone",
                embed = discord.Embed(
                    title = "New Update! Version {}".format(update["version"]),
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
        cog_name = "bot"
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
                                colour = await get_embed_color(ctx.author)
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
                                    colour = await get_embed_color(ctx.author)
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
                colour = await get_embed_color(ctx.author)
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
        name = "rememberFile",
        aliases = ["fileChange"],
        description = "Adds a file change to the bot to remember which files to update when it comes time to update the bot.",
        cog_name = "bot"
    )
    @commands.check(is_developer)
    async def remember_file(self, ctx, filename = None, *, reason = None):

        # Check if filename is None; Show list of files to remember
        if filename == None:

            # Get files
            files = await database.bot.get_changed_files()

            # Add to fields
            fields = []
            field_text = ""
            for f in files:
                
                file_text = "`{}`\n{}\n".format(
                    f,
                    "\n".join([
                        "--{}".format(reason)
                        for reason in files[f]
                    ])
                )

                if len(field_text) + len(file_text) > FIELD_THRESHOLD:
                    fields.append(field_text)
                    field_text = ""
                
                field_text += file_text
            
            if len(field_text) > 0:
                fields.append(field_text)

            # Create embed
            embed = discord.Embed(
                title = "Remembered Files",
                description = "Here's a list of files you need to update." if len(files) > 0 else "There aren't any files to remember.",
                colour = await get_embed_color(ctx.author)
            )

            count = 0
            for field in fields:
                embed.add_field(
                    name = "Files {}".format(
                        "({} / {})".format(
                            count + 1, len(fields)
                        ) if len(fields) > 1 else ""
                    ),
                    value = field,
                    inline = False
                )
                count += 1
            
            await ctx.send(
                embed = embed
            )
        
        # Filename is not None
        else:

            # Add changed file to database
            await database.bot.add_changed_file(filename, reason if reason else "No Reason Given")

            await ctx.send(
                embed = discord.Embed(
                    title = "Remembered!",
                    description = "The file `{}` has been remembered.".format(
                        filename
                    ),
                    colour = await get_embed_color(ctx.author)
                )
            )
    
    @commands.command(
        name = "addDeveloper",
        aliases = ["addDev"],
        description = "Allows you to add a developer to the bot.",
        cog_name = "bot"
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
                    colour = await get_embed_color(ctx.author)
                )
            )
        
    @commands.command(
        name = "removeDeveloper",
        aliases = ["removeDev", "remDeveloper", "remDev"],
        description = "Allows you to remove a developer from the bot.",
        cog_name = "bot"
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
                    colour = await get_embed_color(ctx.author)
                )
            )
    
    @commands.command(
        name = "rules",
        description = "Sends the rules for Fellow Hashbrown's private server.",
        cog_name = "bot"
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
                `PyLogic` --> **`!pylogic`**
                `JLogic` --> **`!jlogic`**
                `PyQM` --> **`!pyqm`**
                `JQM` --> **`!jqm`**
                `QM.js` --> **`!qmjs`**
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
                
                [<:instagram:538799450693566494>](https://instagram.com/FellowHashbrown) [<:facebook:538799482880655383>](https://facebook.com/FellowHashbrown) [<:twitter:538799503457779713>](https://twitter.com/FellowHashbrown) [<:tumblr:538799532159270932>](https://fellowhashbrown.tumblr.com) [<:steam:577748794855260171>](https://steamcommunity.com/id/FellowHashbrown) [<:twitch:538799516850323497>](https://twitch.tv/FellowHashbrown) [<:github:538799471912419350>](https://github.com/FellowHashbrown) [<:repl_it:538799640263393281>](https://repl.it/@FellowHashbrown) [<:fellow_hashbrown:538800208008577074>](https://www.fellowhashbrown.com) [<:npm:577742678813310986>](https://npmjs.com/~fellowhashbrown)
                """
            )
        )

        await ctx.send(
            embed = embed
        )
    
    @commands.command(
        name = "botTemplate",
        description = "Sends the template for submitting a bot in Fellow Hashbrown's private server.",
        cog_name = "bot"
    )
    @commands.check(is_developer)
    @is_in_guild(int(os.environ["DEVELOPER_SERVER"]))
    async def template(self, ctx):

        # Create bot submission template
        embed = discord.Embed(
            title = "Submit a Bot!",
            description = "Do you have a bot of your own you'd like on this server?\nDo you know of a bot (that may not be yours) and would like it here?\n**Submit It Then!**",
            colour = await get_embed_color(ctx.author)
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
