import asyncio, discord, os
from discord.ext import commands

from category.errors import get_error_message
from category.globals import FIRST_PAGE, LAST_PAGE, PREVIOUS_PAGE, NEXT_PAGE, LEAVE, SCROLL_REACTIONS
from category.globals import add_scroll_reactions
from category.globals import get_embed_color, FIELD_THRESHOLD
from category.predicates import is_developer
from database import database

from util.discord import send_webhook

class Insults(commands.Cog, name = "Insults"):
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @commands.command(
        name = "viewInsults",
        aliases = ["viewi"],
        description = "Let's you see a list of insults.",
        cog_name = "Insults"
    )
    async def view_insults(self, ctx):

        # Get list of insults
        insults = await database.data.get_insults()

        # Add each to field, paginate if needed
        fields = []
        field_text = ""
        for insult in insults:

            insult = insult["insult"] + "\n"

            if len(field_text) + len(insult) > FIELD_THRESHOLD:
                fields.append(field_text)
                field_text = ""
            
            field_text += insult
        
        if len(field_text) > 0:
            fields.append(field_text)
        
        # Create scrolling embed
        current = 0
        embed = discord.Embed(
            title = "Insults",
            description = "Here's a list of insults in the bot.",
            colour = await get_embed_color(ctx.author)
        ).add_field(
            name = "Insults {}".format(
                "({} / {})".format(
                    current + 1, len(fields)
                ) if len(fields) > 1 else ""
            ),
            value = fields[0]
        )

        # Send message
        msg = await ctx.send(
            embed = embed
        )

        await add_scroll_reactions(msg, fields)

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
            embed = discord.Embed(
                title = "Insults",
                description = "Here's a list of insults in the bot.",
                colour = await get_embed_color(ctx.author)
            ).add_field(
                name = "Insults {}".format(
                    "({} / {})".format(
                        current + 1, len(fields)
                    ) if len(fields) > 1 else ""
                ),
                value = fields[current]
            )

            await msg.edit(
                embed = embed
            )

    @commands.command(
        name = "insult",
        aliases = ["i"],
        description = "Allows you to insult someone or be insulted.",
        cog_name = "Insults"
    )
    async def insult(self, ctx, member : discord.Member = None):
        
        # Generate random insult
        insult = await database.data.get_insult(ctx.channel.is_nsfw() if not isinstance(ctx.channel, discord.DMChannel) else True)

        # Check if insulting self
        if member == None:
            member = ctx.author
        
        await ctx.send(
            "{}, {}".format(
                member.mention, insult["insult"]
            )
        )
    
    @commands.command(
        name = "addInsult",
        aliases = ["addI"],
        description = "Allows you to add an insult to the bot.",
        cog_name = "Insults"
    )
    async def add_insult(self, ctx, *, insult = None):
        
        # Check if insult is None; Send error
        if insult == None:
            await ctx.send(
                embed = get_error_message(
                    "You can't add an empty insult."
                )
            )
        
        # Insult is not None; Add it, notify all developers, notify author
        else:

            # Add to pending insults
            await database.data.add_pending_insult(insult, str(ctx.author.id))

            # Notify all developers
            for dev in await database.bot.get_developers():

                # Get dev user object
                user = self.bot.get_user(int(dev))

                # Only send if user is found
                if user != None:
                    await user.send(
                        embed = discord.Embed(
                            title = "New Pending Insult",
                            description = " ",
                            colour = await get_embed_color(ctx.author)
                        ).add_field(
                            name = "Author",
                            value = "{} ({})".format(
                                ctx.author.mention, ctx.author
                            ),
                            inline = False
                        ).add_field(
                            name = "Insult",
                            value = insult,
                            inline = False
                        )
                    )
            
            # Notify author
            await ctx.send(
                embed = discord.Embed(
                    title = "Insult Pending!",
                    description = "Your insult was added to be reviewed by an Omega Psi developer.\nYou will be notified if it is denied or approved.",
                    colour = await get_embed_color(ctx.author)
                )
            )

            # Send the insult to the discord channel dedicated to insults
            await send_webhook(
                os.environ["INSULT_WEBHOOK"],
                discord.Embed(
                    title = "Insult Suggested",
                    description = " ",
                    colour = await get_embed_color(ctx.author)
                ).add_field(
                    name = "User",
                    value = ctx.author
                ).add_field(
                    name = "Origin",
                    value = ("Server: " + ctx.guild.name) if ctx.guild != None else "Private Message"
                ).add_field(
                    name = "Insult",
                    value = insult
                ).set_thumbnail(
                    url = ctx.author.avatar_url
                )
            )
        
    @commands.command(
        name = "pendingInsults",
        aliases = ["pendingI", "pendInsults", "pendI"],
        description = "Shows a list of pending insults.",
        cog_name = "Insults"
    )
    @commands.check(is_developer)
    async def pending_insults(self, ctx):
        
        # Get list of pending insults
        pending_insults = await database.data.get_pending_insults()
        
        # Check if there are any pending insults
        if len(pending_insults) > 0:

            # Create Embed
            current = 0
            author = self.bot.get_user(int(pending_insults[current]["author"]))
            embed = discord.Embed(
                title = "Pending Insults {}".format(
                    "({} / {})".format(
                        current + 1, len(pending_insults)
                    ) if len(pending_insults) > 1 else ""
                ),
                description = "**Insult**: {}\n**Author**: {}\n**Tags**: `{}`".format(
                    pending_insults[current]["insult"],
                    "Unknown" if author == None else "{} ({})".format(
                        author.mention, author
                    ),
                    ", ".join(pending_insults[current]["tags"]) if len(pending_insults[current]["tags"]) > 0 else "None"
                ),
                colour = await get_embed_color(ctx.author)
            )

            msg = await ctx.send(
                embed = embed
            )

            await add_scroll_reactions(msg, pending_insults)

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
                    current = 0

                # Reaction is last page
                elif str(reaction) == LAST_PAGE:
                    current = len(pending_insults) - 1

                # Reaction is previous page
                elif str(reaction) == PREVIOUS_PAGE:
                    current -= 1
                    if current < 0:
                        current = 0

                # Reaction is next page
                elif str(reaction) == NEXT_PAGE:
                    current += 1
                    if current > len(pending_insults) - 1:
                        current = len(pending_insults) - 1

                # Reaction is leave
                elif str(reaction) == LEAVE:
                    await msg.delete()
                    break

                # Update embed
                author = self.bot.get_user(int(pending_insults[current]["author"]))
                embed = discord.Embed(
                    title = "Pending Insults {}".format(
                        "({} / {})".format(
                            current + 1, len(pending_insults)
                        ) if len(pending_insults) > 1 else ""
                    ),
                    description = "**Insult**: {}\n**Author**: {}\n**Tags**: `{}`".format(
                        pending_insults[current]["insult"],
                        "Unknown" if author == None else "{} ({})".format(
                            author.mention, author
                        ),
                        ", ".join(pending_insults[current]["tags"]) if len(pending_insults[current]["tags"]) > 0 else "None"
                    ),
                    colour = await get_embed_color(ctx.author)
                )

                await msg.edit(
                    embed = embed
                )

        # There are no pending insutls
        else:

            await ctx.send(
                embed = discord.Embed(
                    title = "No Pending Insults",
                    description = "There aren't currently any pending insults to review.",
                    colour = await get_embed_color(ctx.author)
                )
            )
    
    @commands.command(
        name = "addInsultTag",
        aliases = ["addITag"],
        description = "Adds a tag, or tags, to an insult specified.",
        cog_name = "Insults"
    )
    @commands.check(is_developer)
    async def add_insult_tag(self, ctx, index : int, *tags):
        
        # Get list of pending insults
        pending_insults = await database.data.get_pending_insults()

        # Check if index is in range of list
        index -= 1
        tags = list(tags)
        if index >= 0 and index < len(pending_insults):

            # Add the tags to the insult
            await database.data.add_pending_insult_tags(index, tags)

            await ctx.send(
                embed = discord.Embed(
                    title = "Tags Added" if len(tags) > 1 else "Tag Added",
                    description = "The following tag{} been added: `{}`".format(
                        "s have" if len(tags) > 1 else " has",
                        ", ".join(tags)
                    ),
                    colour = await get_embed_color(ctx.author)
                )
            )
        
        # Index is out of range
        else:
            await ctx.send(
                embed = get_error_message(
                    "The index you gave is out of range."
                )
            )
    
    @commands.command(
        name = "approveInsult",
        aliases = ["approveI"],
        description = "Approves the specified insult.",
        cog_name = "Insults"
    )
    @commands.check(is_developer)
    async def approve_insult(self, ctx, index : int):
        
        # Get list of pending insults
        pending_insults = await database.data.get_pending_insults()

        # Check if index is in range of pending insults
        index -= 1
        if index >= 0 and index < len(pending_insults):

            # Approve the insult and let the author know
            author = self.bot.get_user(int(pending_insults[index]["author"]))

            embed = discord.Embed(
                title = "Insult Approved!",
                description = "Insult: *{}*\n{}".format(
                    pending_insults[index]["insult"],
                    "These tags were given to the insult: `{}`".format(
                        ", ".join(pending_insults[index]["tags"])
                    ) if len(pending_insults[index]["tags"]) > 0 else ""
                ),
                colour = await get_embed_color(ctx.author)
            )

            # Only send message if author was found
            await database.data.approve_pending_insult(index)
            if author != None:
                await author.send(
                    embed = embed
                )
            
            # Let dev know
            await ctx.send(
                embed = embed
            )
        
        # Index is out of range`
        else:
            await ctx.send(
                embed = get_error_message(
                    "The index you gave is out of range."
                )
            )
    
    @commands.command(
        name = "denyInsult",
        aliases = ["denyI"],
        description = "Denies the specified insult.",
        cog_name = "Insults"
    )
    @commands.check(is_developer)
    async def deny_insult(self, ctx, index : int, *, reason = None):
        
        # Get list of pending insults
        pending_insults = await database.data.get_pending_insults()

         # Check if index is in range of pending insults
        index -= 1
        if index >= 0 and index < len(pending_insults):
            
            # Deny the insult and tell the author why
            author = self.bot.get_user(int(pending_insults[index]["author"]))

            embed = discord.Embed(
                title = "Insult Denied.",
                description = "Insult: *{}*\n\nReason: *{}*".format(
                    pending_insults[index]["insult"],
                    reason if reason != None else "No Reason Provided. DM a developer for the reason."
                ),
                colour = await get_embed_color(ctx.author)
            )

            # Only send message if author was found
            await database.data.deny_pending_insult(index)
            if author != None:
                await author.send(
                    embed = embed
                )
            
            await ctx.send(
                embed = embed
            )
        
        # Index is out of range`
        else:
            await ctx.send(
                embed = get_error_message(
                    "The index you gave is out of range."
                )
            )
    
    @commands.command(
        name = "viewCompliments",
        aliases = ["viewc"],
        description = "Let's you see a list of compliments.",
        cog_name = "Compliments"
    )
    async def view_compliments(self, ctx):

        # Get list of compliments
        compliments = await database.data.get_compliments()

        # Add each to field, paginate if needed
        fields = []
        field_text = ""
        for compliment in compliments:

            compliment = compliment["compliment"] + "\n"

            if len(field_text) + len(compliment) > FIELD_THRESHOLD:
                fields.append(field_text)
                field_text = ""
            
            field_text += compliment
        
        if len(field_text) > 0:
            fields.append(field_text)
        
        # Create scrolling embed
        current = 0
        embed = discord.Embed(
            title = "Compliments",
            description = "Here's a list of compliments in the bot.",
            colour = await get_embed_color(ctx.author)
        ).add_field(
            name = "Compliments {}".format(
                "({} / {})".format(
                    current + 1, len(fields)
                ) if len(fields) > 1 else ""
            ),
            value = fields[0]
        )

        # Send message
        msg = await ctx.send(
            embed = embed
        )

        await add_scroll_reactions(msg, fields)

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
            embed = discord.Embed(
                title = "Compliments",
                description = "Here's a list of compliments in the bot.",
                colour = await get_embed_color(ctx.author)
            ).add_field(
                name = "Compliments {}".format(
                    "({} / {})".format(
                        current + 1, len(fields)
                    ) if len(fields) > 1 else ""
                ),
                value = fields[current]
            )

            await msg.edit(
                embed = embed
            )
    
    @commands.command(
        name = "compliment",
        aliases = ["c"],
        description = "Allows you to compliment someone or be complimented.",
        cog_name = "Insults"
    )
    async def compliment(self, ctx, member : discord.Member = None):
        
        # Generate random compliment
        compliment = await database.data.get_compliment(ctx.channel.is_nsfw() if not isinstance(ctx.channel, discord.DMChannel) else True)

        # Check if complimenting self
        if member == None:
            member = ctx.author
        
        await ctx.send(
            "{}, {}".format(
                member.mention, compliment["compliment"]
            )
        )
    
    @commands.command(
        name = "addCompliment",
        aliases = ["addC"],
        description = "Allows you to add a compliment to the bot.",
        cog_name = "Insults"
    )
    async def add_compliment(self, ctx, *, compliment = None):
        
        # Check if compliment is None; Send error
        if compliment == None:
            await ctx.send(
                embed = get_error_message(
                    "You can't add an empty compliment."
                )
            )
        
        # Compliment is not None; Add it, notify all developers, notify author
        else:

            # Add to pending compliments
            await database.data.add_pending_compliment(compliment, str(ctx.author.id))

            # Notify all developers
            for dev in await database.bot.get_developers():

                # Get dev user object
                user = self.bot.get_user(int(dev))

                # Only send if user is found
                if user != None:
                    await user.send(
                        embed = discord.Embed(
                            title = "New Pending Compliment",
                            description = " ",
                            colour = await get_embed_color(ctx.author)
                        ).add_field(
                            name = "Author",
                            value = "{} ({})".format(
                                ctx.author.mention, ctx.author
                            ),
                            inline = False
                        ).add_field(
                            name = "Compliment",
                            value = compliment,
                            inline = False
                        )
                    )
            
            # Notify author
            await ctx.send(
                embed = discord.Embed(
                    title = "Compliment Pending!",
                    description = "Your compliment was added to be reviewed by an Omega Psi developer.\nYou will be notified if it is denied or approved.",
                    colour = await get_embed_color(ctx.author)
                )
            )

            # Send the bug to the discord channel dedicated to compliments
            await send_webhook(
                os.environ["COMPLIMENT_WEBHOOK"],
                discord.Embed(
                    title = "Compliment Suggested",
                    description = " ",
                    colour = await get_embed_color(ctx.author)
                ).add_field(
                    name = "User",
                    value = ctx.author
                ).add_field(
                    name = "Origin",
                    value = ("Server: " + ctx.guild.name) if ctx.guild != None else "Private Message"
                ).add_field(
                    name = "Compliment",
                    value = compliment
                ).set_thumbnail(
                    url = ctx.author.avatar_url
                )
            )
        
    @commands.command(
        name = "pendingCompliments",
        aliases = ["pendingC", "pendCompliments", "pendC"],
        description = "Shows a list of pending compliments.",
        cog_name = "Insults"
    )
    @commands.check(is_developer)
    async def pending_compliments(self, ctx):
        
        # Get list of pending compliments
        pending_compliments = await database.data.get_pending_compliments()
        
        # Check if there are any pending compliments
        if len(pending_compliments) > 0:

            # Create Embed
            current = 0
            author = self.bot.get_user(int(pending_compliments[current]["author"]))
            embed = discord.Embed(
                title = "Pending Compliments {}".format(
                    "({} / {})".format(
                        current + 1, len(pending_compliments)
                    ) if len(pending_compliments) > 1 else ""
                ),
                description = "**Compliment**: {}\n**Author**: {}\n**Tags**: `{}`".format(
                    pending_compliments[current]["compliment"],
                    "Unknown" if author == None else "{} ({})".format(
                        author.mention, author
                    ),
                    ", ".join(pending_compliments[current]["tags"]) if len(pending_compliments[current]["tags"]) > 0 else "None"
                ),
                colour = await get_embed_color(ctx.author)
            )

            msg = await ctx.send(
                embed = embed
            )

            await add_scroll_reactions(msg, pending_compliments)

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
                    current = 0

                # Reaction is last page
                elif str(reaction) == LAST_PAGE:
                    current = len(pending_compliments) - 1

                # Reaction is previous page
                elif str(reaction) == PREVIOUS_PAGE:
                    current -= 1
                    if current < 0:
                        current = 0

                # Reaction is next page
                elif str(reaction) == NEXT_PAGE:
                    current += 1
                    if current > len(pending_compliments) - 1:
                        current = len(pending_compliments) - 1

                # Reaction is leave
                elif str(reaction) == LEAVE:
                    await msg.delete()
                    break

                # Update embed
                author = self.bot.get_user(int(pending_compliments[current]["author"]))
                embed = discord.Embed(
                    title = "Pending Compliments {}".format(
                        "({} / {})".format(
                            current + 1, len(pending_compliments)
                        ) if len(pending_compliments) > 1 else ""
                    ),
                    description = "**Compliment**: {}\n**Author**: {}\n**Tags**: `{}`".format(
                        pending_compliments[current]["compliment"],
                        "Unknown" if author == None else "{} ({})".format(
                            author.mention, author
                        ),
                        ", ".join(pending_compliments[current]["tags"]) if len(pending_compliments[current]["tags"]) > 0 else "None"
                    ),
                    colour = await get_embed_color(ctx.author)
                )

                await msg.edit(
                    embed = embed
                )

        # There are no pending insutls
        else:

            await ctx.send(
                embed = discord.Embed(
                    title = "No Pending Compliments",
                    description = "There aren't currently any pending compliments to review.",
                    colour = await get_embed_color(ctx.author)
                )
            )
    
    @commands.command(
        name = "addComplimentTag",
        aliases = ["addCTag"],
        description = "Adds a tag, or tags, to a compliment specified.",
        cog_name = "Insults"
    )
    @commands.check(is_developer)
    async def add_compliment_tag(self, ctx, index : int, *tags):
        
        # Get list of pending compliments
        pending_compliments = await database.data.get_pending_compliments()

        # Check if index is in range of list
        index -= 1
        tags = list(tags)
        if index >= 0 and index < len(pending_compliments):

            # Add the tags to the compliment
            await database.data.add_pending_compliment_tags(index, tags)

            await ctx.send(
                embed = discord.Embed(
                    title = "Tags Added" if len(tags) > 1 else "Tag Added",
                    description = "The following tag{} been added: `{}`".format(
                        "s have" if len(tags) > 1 else " has",
                        ", ".join(tags)
                    ),
                    colour = await get_embed_color(ctx.author)
                )
            )
        
        # Index is out of range
        else:
            await ctx.send(
                embed = get_error_message(
                    "The index you gave is out of range."
                )
            )
    
    @commands.command(
        name = "approveCompliment",
        aliases = ["approveC"],
        description = "Approves the specified compliment.",
        cog_name = "Insults"
    )
    @commands.check(is_developer)
    async def approve_compliment(self, ctx, index : int):
        
        # Get list of pending compliments
        pending_compliments = await database.data.get_pending_compliments()

        # Check if index is in range of pending compliments
        index -= 1
        if index >= 0 and index < len(pending_compliments):

            # Approve the compliment and let the author know
            author = self.bot.get_user(int(pending_compliments[index]["author"]))

            embed = discord.Embed(
                title = "Compliment Approved!",
                description = "Compliment: *{}*\n{}".format(
                    pending_compliments[index]["compliment"],
                    "These tags were given to the compliment: `{}`".format(
                        ", ".join(pending_compliments[index]["tags"])
                    ) if len(pending_compliments[index]["tags"]) > 0 else ""
                ),
                colour = await get_embed_color(ctx.author)
            )

            # Only send message if author was found
            await database.data.approve_pending_compliment(index)
            if author != None:
                await author.send(
                    embed = embed
                )
            
            # Let dev know
            await ctx.send(
                embed = embed
            )
        
        # Index is out of range`
        else:
            await ctx.send(
                embed = get_error_message(
                    "The index you gave is out of range."
                )
            )
    
    @commands.command(
        name = "denyCompliment",
        aliases = ["denyC"],
        description = "Denies the specified compliment.",
        cog_name = "Insults"
    )
    @commands.check(is_developer)
    async def deny_compliment(self, ctx, index : int, *, reason = None):
        
        # Get list of pending compliments
        pending_compliments = await database.data.get_pending_compliments()

         # Check if index is in range of pending compliments
        index -= 1
        if index >= 0 and index < len(pending_compliments):
            
            # Deny the compliment and tell the author why
            author = self.bot.get_user(int(pending_compliments[index]["author"]))

            embed = discord.Embed(
                title = "Compliment Denied.",
                description = "Compliment: *{}*\n\nReason: *{}*".format(
                    pending_compliments[index]["compliment"],
                    reason if reason != None else "No Reason Provided. DM a developer for the reason."
                ),
                colour = await get_embed_color(ctx.author)
            )

            # Only send message if author was found
            await database.data.deny_pending_compliment(index)
            if author != None:
                await author.send(
                    embed = embed
                )
            
            await ctx.send(
                embed = embed
            )
        
        # Index is out of range`
        else:
            await ctx.send(
                embed = get_error_message(
                    "The index you gave is out of range."
                )
            )

def setup(bot):
    bot.add_cog(Insults(bot))