import discord, json, os, requests, time
from datetime import datetime
from discord.ext import commands
from functools import partial

from category import errors
from category.globals import FIELD_THRESHOLD, OMEGA_PSI_CREATION
from category.globals import get_embed_color
from category.predicates import can_manage_guild, guild_only

from database import database as db
from database import loop

from util.misc import get_theme
from util.string import datetime_to_string, datetime_to_length

UPTIME_API_URL = "https://api.uptimerobot.com/v2/getMonitors"
DBL_VOTE_LINK = "https://discordbots.org/bot/535587516816949248/vote"

class Info(commands.Cog, name = "info"):
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @commands.command(
        name = "botInfo",
        aliases = ["bi"],
        description = "Allows you to get info about the bot.",
        cog_name = "info"
    )
    async def info(self, ctx):
        
        # Send information about Omega Psi
        bot_info = await self.bot.application_info()
        owner = bot_info.owner

        developers = [self.bot.get_user(int(dev)) if self.bot.get_user(int(dev)) != None else dev for dev in await db.bot.get_developers()]

        fields = {
            "Owner": "{}#{}".format(owner.name, owner.discriminator),
            "Developers": "\n".join([
                dev if type(dev) == str else "{} ({})".format(
                    dev.mention,
                    dev
                )
                for dev in developers
            ])
        }

        # Add to embed
        #   Get a random theme
        theme = get_theme()
        embed = discord.Embed(
            title = "Omega Psi Info",
            description = "Here's some information about me!",
            colour = await get_embed_color(ctx.author)
        ).set_image(
            url = "https://discordbots.org/api/widget/535587516816949248.png?topcolor={1}&avatarbg={1}&datacolor={1}&highlightcolor={0}&middlecolor={0}&usernamecolor={0}&labelcolor={2}".format(
                theme[0],   # Dark
                theme[2],   # Light
                theme[1]    # Medium
            )
        ).set_footer(
            text = "Created on {}. Omega Psi is {} old.".format(
                datetime_to_string(OMEGA_PSI_CREATION, short = True),
                datetime_to_length(OMEGA_PSI_CREATION)
            )
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

        # Send the embed
        await ctx.send(
            embed = embed
        )
    
    @commands.command(
        name = "support",
        description = "Gives you the invite link to my discord server!",
        cog_name = "info"
    )
    async def support(self, ctx):
        
        # Send the link
        await ctx.send(
            "discord.gg/W8yVrHt"
        )
    
    @commands.command(
        name = "vote",
        description = "Gives you a link to vote for Omega Psi on DBL.",
        cog_name = "info"
    )
    async def vote(self, ctx):

        await ctx.send(
            DBL_VOTE_LINK
        )
    
    @commands.command(
        name = "website",
        aliases = ["web"],
        description = "Sends you a link to my personal website.",
        cog_name = "info"
    )
    async def website(self, ctx):
        
        # Send the link
        await ctx.send(
            "https://www.fellowhashbrown.com"
        )
    
    @commands.command(
        name = "botSite",
        description = "Sends you a link to Omega Psi's website.",
        cog_name = "info"
    )
    async def botsite(self, ctx):

        # Send the link
        await ctx.send(
            "https://omegapsi.fellowhashbrown.com"
        )
    
    @commands.command(
        name = "replit",
        aliases = ["repl", "source", "src"],
        description = "Gives you a link so you can read my source code.",
        cog_name = "info"
    )
    async def replit(self, ctx):
        
        # Send the link
        await ctx.send(
            "https://repl.it/@FellowHashbrown/Omega-Psi\nhttps://github.com/FellowHashbrown/Omega-Psi"
        )
    
    @commands.command(
        name = "uptime",
        description = "Shows you my uptime!",
        cog_name = "info"
    )
    async def uptime(self, ctx):
        
        # Request downtime from Uptime Robot
        downtime = await loop.run_in_executor(None,
            partial(
                requests.post,
                UPTIME_API_URL,
                data = "api_key={}&format=json&logs=1".format(
                    os.environ["UPTIME_API_KEY"]
                ),
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
                            "last": datetime.fromtimestamp(log["datetime"])
                        }

                    # Keep track of the last 24 hours
                    if time.time() - log["datetime"] <= 60*60*24:
                        downtimeDay += log["duration"]
                    
                    # Keep track of the last 7 days
                    if time.time() - log["datetime"] <= 60*60*24*7:
                        downtimeWeek += log["duration"]
                    
                    # Keep track of the month
                    if time.time() - log["datetime"] <= 60*60*24*datetime.now().day:
                        downtimeMonth += log["duration"]
            
            # Keep uptime in separate fields
            fields = {
                "Last 24 Hours": round(100 - (downtimeDay / (60 * 60 * 24) * 100), 2),
                "Last 7 Days": round(100 - (downtimeWeek / (60 * 60 * 24 * 7) * 100), 2),
                "This Month": round(100 - (downtimeMonth / (60 * 60 * 24 * datetime.now().day) * 100), 2)
            }
            
            # Create the embed and add the fields
            embed = discord.Embed(
                title = "Omega Psi Uptime",
                description = " ",
                colour = await get_embed_color(ctx.author),
                url = "https://status.omegapsi.fellowhashbrown.com",
                timestamp = recentDowntime["last"]
            ).set_footer(
                text ="Latest downtime ({} hrs {} min) ➡".format(
                    recentDowntime["hours"],
                    recentDowntime["minutes"]
                )
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
                colour = await get_embed_color(ctx.author)
            )
        
        await ctx.send(
            embed = embed
        )
    
    @commands.command(
        name = "invite",
        description = "Allows you to invite me to your own server!",
        cog_name = "info"
    )
    async def invite(self, ctx):
        
        # Send the link
        await ctx.send(
            "https://discordapp.com/oauth2/authorize?client_id=535587516816949248&scope=bot&permissions=519232"
        )
    
    @commands.command(
        name = "ping",
        description = "Ping-Pong!",
        cog_name = "info"
    )
    async def ping(self, ctx):

        # Edit message
        await ctx.send(
            "Pong! `{}ms`".format(
                int(self.bot.latency * 1000)
            )
        )

    @commands.command(
        name = "prefix", 
        aliases = ["pre"],
        description = "Allows you to change the prefix for this server.",
        cog_name = "info"
    )
    @commands.check(can_manage_guild)
    @commands.check(guild_only)
    async def prefix(self, ctx, prefix: str = None):

        # Check if prefix is None (didn't enter it in)
        if prefix == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You must clarify the new prefix!"
                )
            )
        
        # There is a prefix specified
        else:

            # Check if prefix ends with letter or digit
            if prefix[-1].isdigit() or prefix[-1].isalpha():
                prefix += " "

            # Change prefix for guild
            await db.guilds.set_prefix(ctx.guild, prefix)
            
            # Send message
            await ctx.send(
                embed = discord.Embed(
                    title = "Prefix Changed",
                    description = f"This server's prefix is now `{prefix}`",
                    colour = await get_embed_color(ctx.author)
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