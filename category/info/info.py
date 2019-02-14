import discord, json, os, requests, time
from datetime import datetime
from discord.ext import commands
from discord.ext.commands import has_permissions, guild_only
from functools import partial

from category import errors
from category.globals import PRIMARY_EMBED_COLOR, FIELD_THRESHOLD
from database import database as db
from database import loop
from util.string import datetime_to_string

UPTIME_API_URL = "https://api.uptimerobot.com/v2/getMonitors"

class Info:
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @commands.command(
        name = "botInfo",
        aliases = ["bi"],
        description = "Allows you to get info about the bot.",
        cog_name = "Info"
    )
    async def bot_info(self, ctx):
        
        # Send information about Omega Psi
        bot_info = await self.bot.application_info()
        owner = bot_info.owner

        recent_update = await db.get_recent_update()
        pending_update = await db.get_pending_update()
        developers = [self.bot.get_user(int(dev)) if self.bot.get_user(int(dev)) != None else dev for dev in await db.get_developers()]

        fields = {
            "Owner": "{}#{}".format(owner.name, owner.discriminator),
            "Developers": ", ".join([
                dev if type(dev) == str else "{}#{}".format(
                    dev.name,
                    dev.discriminator
                )
                for dev in developers
            ]),
            "Recent Update": "**Version**: {}\n**Description**: {}\n**Features**: {}\n**Fixes**: {}".format(
                recent_update["version"],
                recent_update["description"],
                "\n".join(recent_update["features"]) if len(recent_update["features"]) > 0 else "No Features Added.",
                "\n".join(recent_update["fixes"]) if len(recent_update["fixes"]) > 0 else "No Fixes Made."
            ),
            "Pending Update": "**Features**: {}\n**Fixes**: {}\n".format(
                "\n".join(pending_update["features"]) if len(pending_update["features"]) > 0 else "No Features Added Yet.",
                "\n".join(pending_update["fixes"]) if len(pending_update["fixes"]) > 0 else "No Fixes Made Yet."
            ) if pending_update != {} else "No Pending Update Yet"
        }

        # Add to embed
        embed = discord.Embed(
            title = "Omega Psi Info",
            description = "Here's some information about me!",
            colour = PRIMARY_EMBED_COLOR
        )

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
        name = "support",
        description = "Gives you the invite link to my discord server!",
        cog_name = "Info"
    )
    async def support(self, ctx):
        
        # Send the link
        await ctx.send(
            "discord.gg/W8yVrHt"
        )
    
    @commands.command(
        name = "website",
        aliases = ["web"],
        description = "Sends you a link to my website.",
        cog_name = "Info"
    )
    async def website(self, ctx):
        
        # Send the link
        await ctx.send(
            "https://www.fellowhashbrown.com"
        )
    
    @commands.command(
        name = "replit",
        aliases = ["repl"],
        description = "Gives you a link so you can read my source code.",
        cog_name = "Info"
    )
    async def replit(self, ctx):
        
        # Send the link
        await ctx.send(
            "https://repl.it/@FellowHashbrown/Omega-Psi-5"
        )
    
    @commands.command(
        name = "uptime",
        description = "Shows you my uptime!",
        cog_name = "Info"
    )
    async def uptime(self, ctx):
        
        # Request downtime from Uptime Robot
        downtime = await loop.run_in_executor(None,
            partial(
                requests.post,
                UPTIME_API_URL,
                data = "api_key={}&format=json&logs=1".format(os.environ["UPTIME_API_KEY"]),
                headers = {
                    "content-type": "application/x-www-form-urlencoded",
                    "cache-control": "no-cache"
                }
            )
        )
        downtime = downtime.json()

        # Only get the data if there is no error
        if downtime["stat"] == "ok":
            downtimeDay = 0
            downtimeWeek = 0
            downtimeMonth = 0
            recentDowntime = None

            # Go through all the logs and detect the downtime (any log that is not of type 2)
            for log in downtime["monitors"][0]["logs"]:

                # Get the most recent downtime
                if log["type"] != 2:
                    if recentDowntime == None:
                        seconds = log["duration"]

                        hours = seconds // 3600
                        seconds -= 3600 * hours

                        minutes = seconds // 60

                        recentDowntime = {
                            "hours": hours,
                            "minutes": minutes,
                            "last": datetime_to_string(datetime.fromtimestamp(log["datetime"]))
                        }

                    # Keep track of the last 24 hours
                    if time.time() - log["datetime"] <= 60*60*24:
                        downtimeDay += log["duration"]
                    
                    # Keep track of the last 7 days
                    if time.time() - log["datetime"] <= 60*60*24*7:
                        downtimeWeek += log["duration"]
                    
                    # Keep track of the last 30 days
                    if time.time() - log["datetime"] <= 60*60*24*30:
                        downtimeMonth += log["duration"]
            
            # Keep uptime in separate fields
            fields = {
                "Last 24 Hours": round(100 - (downtimeDay / (60 * 60 * 24) * 100), 2),
                "Last 7 Days": round(100 - (downtimeWeek / (60 * 60 * 24 * 7) * 100), 2),
                "Last 30 Days": round(100 - (downtimeMonth / (60 * 60 * 25 * 30) * 100), 2)
            }

            # Put the text for the most recent downtime in its own text
            recentDowntime = "The latest downtime happened on {} for {} hr{} {} min{}".format(
                recentDowntime["last"],
                recentDowntime["hours"], "s" if recentDowntime["hours"] != 1 else "",
                recentDowntime["minutes"], "s" if recentDowntime["minutes"] != 1 else ""
            )
            
            # Create the embed and add the fields
            embed = discord.Embed(
                title = "Omega Psi Uptime",
                description = recentDowntime,
                colour = PRIMARY_EMBED_COLOR,
                url = "https://status.omegapsi.fellowhashbrown.com"
            )

            for field in fields:
                embed.add_field(
                    name = field,
                    value = str(fields[field]) + "%"
                )
        
        # There was an error
        else:
            embed = discord.Embed(
                title = "Error",
                description = "```json\n{}\n```".format(json.dumps(downtime["error"], indent = 4)),
                colour = PRIMARY_EMBED_COLOR
            )
        
        await ctx.send(
            embed = embed
        )
    
    @commands.command(
        name = "invite",
        description = "Allows you to invite me to your own server!",
        cog_name = "Info"
    )
    async def invite(self, ctx):
        
        # Send the link
        await ctx.send(
            "https://discordapp.com/oauth2/authorize?client_id=535587516816949248&scope=bot&permissions=519232"
        )
    
    @commands.command(
        name = "ping",
        description = "Ping-Pong!",
        cog_name = "Info"
    )
    async def ping(self, ctx):
        
        # Get current time
        start = datetime.now()

        # Send message
        ping_msg = await ctx.send(
            "Pong..."
        )

        # Get end time
        end = datetime.now()

        # Edit message
        await ping_msg.edit(
            content = "Pong! `{}ms`".format(
                int((end - start).total_seconds() * 1000)
            )
        )
    
    @commands.command(
        name = "suggest",
        description = "If you feel like something could be improved on in this bot, please suggest it!",
        cog_name = "Info"
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

            # Send message to all developers
            for dev in await db.get_developers():

                # Get the dev user object
                user = self.bot.get_user(int(dev))

                # Send the message
                await user.send(
                    embed = discord.Embed(
                        title = "Suggestion",
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
                    title = "Suggestion Sent",
                    description = suggestion,
                    colour = PRIMARY_EMBED_COLOR
                )
            )
    
    @commands.command(
        name = "bug",
        description = "Is there a bug or something in the bot? Use this! Give a decent description so I know what to look for!",
        cog_name = "Info"
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

            # Send message to all developers
            for dev in await db.get_developers():

                # Get the dev user object
                user = self.bot.get_user(int(dev))

                # Send the message
                await user.send(
                    embed = discord.Embed(
                        title = "Bug Reported",
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
                    title = "Bug Sent!",
                    description = bug,
                    colour = PRIMARY_EMBED_COLOR
                )
            )

    @commands.command(
        name = "prefix", 
        aliases = ["pre"],
        description = "Allows you to change the prefix for this server.",
        cog_name = "Info"
    )
    @has_permissions(manage_guild = True)
    @guild_only()
    async def prefix(self, ctx, prefix):

        # Change prefix for guild
        await db.set_prefix(ctx.guild, prefix)
        
        # Send message
        await ctx.send(
            embed = discord.Embed(
                title = "Prefix Changed",
                description = f"This server's prefix is now `{prefix}`",
                colour = PRIMARY_EMBED_COLOR
            )
        )
    
    # # # # # # # # # # # # # # # # # # # # # # # # #
    
    @prefix.error
    async def guild_only_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):

            # Check if in guild; Then person doesn't have proper permissions
            if ctx.guild:
                await ctx.send(
                    embed = errors.get_error_message(
                        "You need to have `Manage Server` permissions to run this."
                    )
                )
            
            # Not in guild
            else:
                await ctx.send(
                    embed = errors.get_error_message(
                        "This command can only be run in guilds."
                    )
                )

def setup(bot):
    bot.add_cog(Info(bot))