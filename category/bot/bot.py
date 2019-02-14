import asyncio, discord, os, sys
from datetime import datetime
from discord.ext import commands

from category import errors
from category.globals import PRIMARY_EMBED_COLOR, FIELD_THRESHOLD, SCROLL_REACTIONS, FIRST_PAGE, LAST_PAGE, PREVIOUS_PAGE, NEXT_PAGE, LEAVE, add_scroll_reactions
from category.predicates import is_developer, is_in_guild
from database import database

class Bot:
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @commands.command(
        name = "servers",
        aliases = ["serverList", "sl"],
        description = "Shows you a list of servers that Omega Psi is in. (DEV ONLY)",
        cog_name = "Bot"
    )
    @is_developer()
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
        description = "Allows you to restart the bot. (DEV ONLY)",
        cog_name = "Bot"
    )
    @is_developer()
    async def restart(self, ctx, html_style = None):

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
        await database.set_restart({
            "send": True,
            "channel_id": str(ctx.channel.id) if ctx.channel != None else None,
            "author_id": str(ctx.author.id)
        })

        # Set the html style if applicable
        if html_style != None:

            # Validate html style
            if html_style in ["normal", "n", "regular", "r"]:
                html_style = "normal"
            elif html_style in ["fancy", "f", "dropdown", "d"]:
                html_style = "fancy"
            elif html_style in ["column", "c", "section", "s"]:
                html_style = "column"
            
            # No html styles fit; Default to normal
            else:
                html_style = "normal"

            await database.set_html_style(html_style)

        # Actually restart
        await ctx.send(
            "{}, I will be right back!".format(ctx.author.mention)
        )

        os.execv(sys.executable, ["python"] + sys.argv)

        await self.bot.logout()

    @commands.command(
        name = "kill",
        description = "Stops the bot and logs out. (DEV ONLY)",
        cog_name = "Bot"
    )
    @is_developer()
    async def kill(self, ctx):

        await ctx.send(
            "Bye! {}".format(ctx.author.mention)
        )

        await self.bot.logout()
    
    @commands.command(
        name = "createUpdate",
        aliases = ["createUpd"],
        description = "Creates a new pending update to the bot. (DEV ONLY)",
        cog_name = "Bot"
    )
    @is_developer()
    async def create_update(self, ctx):
        
        # Create the update; Send message to all other developers
        await database.create_pending_update()

        for dev in await database.get_developers():

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
        description = "Adds a fix to the pending update. (DEV ONLY)",
        cog_name = "Bot"
    )
    @is_developer()
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

            await database.add_pending_fix(fix)

            # Send to all other developers
            for dev in await database.get_developers():

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
        description = "Adds a feature to the pending update. (DEV ONLY)",
        cog_name = "Bot"
    )
    @is_developer()
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

            await database.add_pending_feature(feature)

            # Send to all other developers
            for dev in await database.get_developers():

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
        description = "Commits the pending update as a new update. (DEV ONLY)",
        cog_name = "Bot"
    )
    @is_developer()
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
            await database.commit_pending_update(version, description)
            update = await database.get_recent_update()

            for dev in await database.get_developers():

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
        name = "rules",
        description = "Sends the rules for Fellow Hashbrown's private server. (DEV ONLY)",
        cog_name = "Bot"
    )
    @is_developer()
    @is_in_guild(int(os.environ["DEVELOPER_SERVER"]))
    async def rules(ctx):

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
                `Supercog` --> **`!supercog`**
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
                `Logic API` --> **`!logicapi`**
                `Morse API` --> **`!morseapi`**
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
        description = "Sends the template for submitting a bot in Fellow Hashbrown's private server. (DEV ONLY)",
        cog_name = "Bot"
    )
    @is_developer()
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
                "Bot commands must be activated by a prefix. If a bot responses to phrases, it will not be added.\n"
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