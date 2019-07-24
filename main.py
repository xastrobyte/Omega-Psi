import app, asyncio, discord, os, requests, traceback

from discord.ext.commands import AutoShardedBot, check
from functools import partial

from category import errors
from category.globals import MESSAGE_THRESHOLD, FIELD_THRESHOLD
from category.globals import DBL_BOT_STAT_API_CALL
from category.globals import SCROLL_REACTIONS, FIRST_PAGE, LAST_PAGE, PREVIOUS_PAGE, NEXT_PAGE, LEAVE
from category.globals import VALID_STATUSES
from category.globals import add_scroll_reactions
from category.globals import get_embed_color
from category.predicates import get_prefix, is_nsfw_or_private, is_developer

from database import loop
from database import database

from util.ifttt import ifttt_push

# Open Bot Client
bot = AutoShardedBot(command_prefix = get_prefix, case_insensitive = True)
bot.remove_command("help")

# Keep track of the separate cogs and their names and their emojis
#   also keep track of any channel checks or user checks that need to be done 
#   prior to showing the cog or the help menu
cogs = {
    "api": {
        "command": "help api",
        "description": "Test out my own APIs here :)",
        "check": None,
        "caps": True,
        "emoji": ":pager: ",
        "extension": "category.api.api"
    },
    "code": {
        "command": "help code",
        "description": "All things having to do with coding go here.",
        "check": None,
        "emoji": ":keyboard: ",
        "extension": "category.code.code"
    },
    "math": {
        "command": "help math",
        "description": "Mathematical stuff like calculus and basic algebra!",
        "check": None,
        "emoji": ":asterisk: ",
        "extension": "category.math.math"
    },
    "game": {
        "command": "help game",
        "description": "There are games in this category!",
        "check": None,
        "emoji": ":video_game: ",
        "extension": "category.game.game"
    },
    "food": {
        "command": "help food",
        "description": "Food and drink stuff can be found here.",
        "check": None,
        "emoji": ":apple: ",
        "extension": "category.food.food"
    },
    "animal": {
        "command": "help animal",
        "description": "Animal pictures! and facts (soon).",
        "check": None,
        "emoji": ":unicorn: ",
        "extension": "category.animal.animal"
    },
    "internet": {
        "command": "help internet",
        "description": "All internet-based commands go here.",
        "check": None,
        "emoji": ":desktop: ",
        "extension": "category.internet.internet"
    },
    "image": {
        "command": "help image",
        "description": "Image commands are here! Hint: dog's and cat's are here too.",
        "check": None,
        "emoji": ":frame_photo: ",
        "extension": "category.image.image"
    },
    "insults": {
        "command": "help insults",
        "description": "If you feel in the mood for insults, here you are!",
        "check": None,
        "emoji": ":exclamation: ",
        "extension": "category.insults.insults"
    },
    "misc": {
        "command": "help misc",
        "description": "This category has commands that really don't fit anywhere.",
        "check": None,
        "emoji": ":mag: ",
        "extension": "category.misc.misc"
    },
    "notifications": {
        "command": "help notifications",
        "description": "You can get notified about the online status of people here!",
        "check": None,
        "emoji": ":vibration_mode: ",
        "extension": "category.notifications.notifications"
    },
    "nsfw": {
        "command": "help nsfw",
        "description": "18+ ;)",
        "check": is_nsfw_or_private,
        "caps": True,
        "emoji": ":underage: ",
        "extension": "category.nsfw.nsfw"
    },
    "stats": {
        "command": "help stats",
        "description": "Video Game stats! For all sorts of games!",
        "check": None,
        "emoji": ":clipboard: ",
        "extension": "category.stats.stats"
    },
    "bot": {
        "command": "help bot",
        "description": "Primarily bot-related commands.",
        "check": None,
        "emoji": ":robot: ",
        "extension": "category.bot.bot"
    },
    "info": {
        "command": "help info",
        "description": "Basic info stuff really.",
        "check": None,
        "emoji": ":question: ",
        "extension": "category.info.info"
    }
}

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Basic Events
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@bot.event
async def on_ready():
    """Overrides discord.py's event for on_ready.
    This will print out in the console when it is ready.
    Then it will update the bot's presence.
    If the bot was restarted using the `restart` command, it will send a message.
    """

    # Send a push notification to IFTTT
    await ifttt_push(
        "on_push",
        "Ready To Go",
        "Omega Psi is online and ready to go.",
        ""
    )
    print("I'm ready to go")
    
    # Retrieve the activity types
    activity_type = await database.bot.get_activity_type()
    activity_name = await database.bot.get_activity_name()
    activity_name = "{} in {} Servers".format(
        activity_name,
        len(bot.guilds)
    )
    
    # Set presence
    await bot.change_presence(
        status = discord.Status.online,
        activity = discord.Activity(
            name = activity_name,
            type = activity_type,
            url = "https://twitch.tv/FellowHashbrown"
        )
    )

    # Tell about the restarting
    restart = await database.bot.get_restart()

    # Only send the message if the restart happened through the command
    if restart["send"]:

        # Get the channel and author
        author = bot.get_user(int(restart["author_id"]))
        channel = bot.get_channel(int(restart["channel_id"]))
        if channel == None:
            channel = author

        # Set the "send" value to false; The only time it becomes true is from the restart command
        restart["send"] = False

        # Update the restart data
        await database.bot.set_restart(restart)

        # Send the message
        await channel.send(
            "{}, I'm back!".format(author.mention)
        )

@bot.event
async def on_command(ctx):
    """Overrides discord.py's event for on_command.
    This will just label the bot as typing.
    """
    async with ctx.typing():
        pass

@bot.event
async def on_command_error(ctx, error):
    """Overrides discord.py's event for on_command_error.
    This will send a message to the COMMAND_ERROR_CHANNEL (environment variable.) 
        with a traceback to easily locate the error.
    """
    
    # Create embed
    embed = discord.Embed(
        title = "Command Failed",
        description = str(error),
        color = 0x800000
    )

    # Add fields
    exc = traceback.format_exception(type(error), error, error.__traceback__)
    fields = {
        "Command Author": ctx.author,
        "Guild Name": ctx.guild.name if ctx.guild != None else "Private Message",
        "Channel Name": ctx.channel.name if ctx.guild != None else "Private Message with {}#{}".format(
            ctx.author.name, ctx.author.discriminator
        )
    }

    # Create traceback fields
    tb_fields = []
    tb_field = ""
    for line in exc:

        line += "\n"

        if len(tb_field) + len(line) > FIELD_THRESHOLD:
            tb_fields.append(tb_field)
            tb_field = ""
        
        tb_field += line
    
    if len(tb_field) > 0:
        tb_fields.append(tb_field)

    for field in fields:
        embed.add_field(
            name = field,
            value = fields[field],
            inline = False
        )
    
    count = 0
    for field in tb_fields:
        count += 1
        embed.add_field(
            name = "Traceback {}".format(
                "({} / {})".format(
                    count, len(tb_fields)
                ) if len(tb_fields) > 1 else ""
            ),
            value = "```py\n{}\n```".format(field),
            inline = False
        )
    
    # Get the error channel
    channel = bot.get_channel(int(os.environ["COMMAND_ERROR_CHANNEL"]))

    await channel.send(
        embed = embed
    )

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Guild Events
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@bot.event
async def on_guild_join(guild):
    """Overrides discord.py's event for on_guild_join.
    This will make use of IFTTT and send a push notification to my android device.
    It will also make a POST request to DBL to update the amount of servers Omega Psi is in.
    """

    # Update presence
    activity_type = await database.bot.get_activity_type()
    activity_name = await database.bot.get_activity_name()
    activity_name = "{} in {} servers.".format(
        activity_name,
        len(bot.guilds)
    )
    
    await bot.change_presence(
        status = discord.Status.online,
        activity = discord.Activity(
            name = activity_name,
            type = activity_type,
            url = "https://twitch.tv/FellowHashbrown"
        )
    )

    # Update server count on DBL
    await update_dbl(True, guild)

@bot.event
async def on_guild_remove(guild):
    """Overrides discord.py's event for on_guild_remove.
    This will make use of IFTTT and send a push notification to my android device.
    It will also make a POST request to DBL to update the amount of servers Omega Psi is in.
    """

    # Update presence
    activity_type = await database.bot.get_activity_type()
    activity_name = await database.bot.get_activity_name()
    activity_name = "{} in {} servers.".format(
        activity_name,
        len(bot.guilds)
    )
    
    await bot.change_presence(
        status = discord.Status.online,
        activity = discord.Activity(
            name = activity_name,
            type = activity_type,
            url = "https://twitch.tv/FellowHashbrown"
        )
    )

    # Update server count on DBL
    await update_dbl(False, guild)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Member Events
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@bot.event
async def on_member_update(before, after):
    """Overrides discord.py's on_member_update event
    to provide users with notifications for any member updates that may be
    made when users use the `o.notify` command.
    """

    # Check if the member's online status changed
    if str(before.status) != str(after.status) and str(before.status) in VALID_STATUSES and str(after.status) in VALID_STATUSES:

        # Load the target of the member if they exist
        target = await database.online_status.get_listener(after, create = False)

        # Only run if the target does exist (is not None)
        if target != None:

            # Iterate through all the users in the target
            for user in target["users"]:
                user_object = bot.get_user(int(user))

                # Only send the message if the guild ID matches
                if str(after.guild.id) == target["users"][user]["guild_id"] and target["users"][user]["active"]:
                    
                    # Check if the member came online
                    if str(after.status) == "online":
                        title = "Online"
                        message = "{}#{} is online!".format(
                            after.name, after.discriminator
                        )
                    
                    # Check if the member went offline
                    elif str(after.status) == "offline":
                        title = "Offline"
                        message = "{}#{} went offline.".format(
                            after.name, after.discriminator
                        )
                    
                    # Check if the member went idle
                    elif str(after.status) == "idle":
                        title = "Idle"
                        message = "{}#{} went idle.".format(
                            after.name, after.discriminator
                        )
                    
                    # Check if the member turned on Do Not Disturb
                    elif str(after.status) == "dnd":
                        title = "Do Not Disturb"
                        message = "{}#{} turned on Do Not Disturb.".format(
                            after.name, after.discriminator
                        )
                        
                    # Check if the user has their IFTTT account connected
                    ifttt_data = await database.users.get_ifttt(user_object)
                    if ifttt_data["active"]:
                        
                        # Get the users webhook key and event name
                        webhook_key = ifttt_data["webhook_key"]

                        # Send a push notification to the user
                        await ifttt_push(
                            "omega_psi_push",
                            title,
                            message,
                            "",
                            key = webhook_key
                        )
                    
                    # The user's IFTTT is not active
                    else:
                        try:
                            await user_object.send(message)
                        except:
                            pass

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Global Commands
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

async def update_dbl(joined_guild = None, guild = None, *, ctx = None):
    """Updates the Discord Bots List server count for Omega Psi
    and sends a message to all developers about how many servers
    Omega Psi is in.
    """

    # Update the dbl
    response = await loop.run_in_executor(None,
        partial(
            requests.post,
            DBL_BOT_STAT_API_CALL,
            json = {
                "server_count": len(bot.guilds)
            },
            headers = {
                "Authorization": os.environ["DBL_API_KEY"]
            }
        )
    )
    response = response.json()

    # Send message to all developers saying DBL update failed or succeeded
    embed = discord.Embed(
        title = "DBL Server Count Update {}".format(
            "Successful" if "error" not in response else "Failed"
        ),
        description = "Omega Psi is now in {} servers".format(len(bot.guilds)) if "error" not in response else response["error"],
        colour = 0x008000 if "error" not in response else 0x800000
    )

    # Iterate through all the devs and send a message
    for dev in await database.bot.get_developers():

        # Get dev user object
        user = bot.get_user(int(dev))

        if user != None and (user.id != ctx.author.id if ctx != None else True):
            await user.send(
                embed = embed
            )

    # Send a current message if the update was made manually
    if ctx != None:   
        await ctx.send(
            embed = embed
        )

    # Send a notification if Omega Psi was added to/removed from a server
    if joined_guild != None:

        # Send notification through IFTTT that Omega Psi has left a server
        await ifttt_push(
            "on_push",
            "Omega Psi\n",
            "Added to Discord Server.\n" if joined_guild else "Removed from Discord Server.\n",
            "Guild: {}\nOwner: {}".format(guild.name, guild.owner)
        )

@bot.command(
    name = "updateDBL",
    aliases = ["dbl"],
    description = "Updates the server count on DBL for Omega Psi manually."
)
@check(is_developer)
async def update_DBL(ctx):
    await update_dbl(ctx = ctx)

@bot.command(
    name = "help", 
    aliases = ["h", "?"],
    description = "Shows help on a specific command, a category, or all the categories in Omega Psi."
)
async def help(ctx, specific = None):

    # Get prefix
    if ctx.guild != None:
        prefix = await database.guilds.get_prefix(ctx.guild)
    
    else:
        prefix = "o."
    
    # Check if user is on mobile
    on_mobile = ctx.message.content.startswith(prefix + ".") or ctx.message.content.startswith(".")
    
    # See if getting help for a specific category or command
    if specific != None:

        # Specific help is a Cog
        if specific.lower() in cogs and (await cogs[specific.lower()]["check"](ctx) if cogs[specific.lower()]["check"] != None else True):

            # Create fields for all commands
            commands = bot.get_cog(specific.lower()).get_commands()
            commands = sorted(commands, key = lambda k: k.name)

            fields = []
            fieldText = ""
            for command in commands:

                # Filter based on author and channel
                if not await command.can_run(ctx):
                    continue

                name_descr = "**`{}{}`** - {}\n".format(
                    prefix,
                    command.name,
                    command.description
                )

                if len(fieldText) + len(name_descr) > MESSAGE_THRESHOLD:
                    fields.append(fieldText)
                    fieldText = ""
                
                fieldText += name_descr
            
            if len(fieldText) > 0:
                fields.append(fieldText)
        
            # Get the cog text
            cog_text = specific.title()
            if "caps" in cogs[specific.lower()]:
                if cogs[specific.lower()]["caps"]:
                    cog_text = specific.upper()

            # Create embed for menu
            embed = discord.Embed(
                title = "{} {}".format(
                    cogs[specific.lower()]["emoji"] + cog_text,
                    "- Page ({} / {})".format(
                        1, len(fields)
                    ) if len(fields) > 1 else ""
                ),
                description = fields[0],
                colour = await get_embed_color(ctx.author)
            ).set_footer(
                text = "❕❕❕ Add an extra . to any command for a mobile view!"
            )
            
            # Send message and add navigation reactions
            msg = await ctx.send(
                embed = embed
            )

            await add_scroll_reactions(msg, fields)
            
            # Run a wait for reaction until the user presses leave
            current = 0
            while True:

                # Wait for next reaction from user
                def check(reaction, user):
                    return str(reaction) in SCROLL_REACTIONS and user == ctx.author

                done, pending = await asyncio.wait([
                    bot.wait_for("reaction_add", check = check),
                    bot.wait_for("reaction_remove", check = check)
                ], return_when = asyncio.FIRST_COMPLETED)

                reaction, user = done.pop().result()

                # Cancel any futures
                for future in pending:
                    future.cancel()

                # Reaction is FIRST_PAGE
                if str(reaction) == FIRST_PAGE:
                    current = 0
                
                # Reaction is LAST_PAGE
                elif str(reaction) == LAST_PAGE:
                    current = len(fields) - 1
                
                # Reaction is PREVIOUS_PAGE
                elif str(reaction) == PREVIOUS_PAGE:
                    current -= 1
                    if current < 0:
                        current = 0

                # Reaction is NEXT_PAGE
                elif str(reaction) == NEXT_PAGE:
                    current += 1
                    if current >= len(fields):
                        current = len(fields) - 1

                # Reaction is LEAVE
                elif str(reaction) == LEAVE:
                    await msg.delete()
                    break
                
                # Update help message
                await msg.edit(
                    embed = discord.Embed(
                        title = "{} {}".format(
                            cogs[specific.lower()]["emoji"] + specific.lower(),
                            "- Page ({} / {})".format(
                                current + 1, len(fields)
                            ) if len(fields) > 1 else ""
                        ),
                        description = fields[current],
                        colour = await get_embed_color(ctx.author)
                    )
                )
            
        # Specific help is a Command or is invalid
        else:

            command = bot.get_command(specific)

            # Command is invalid
            if command == None:
                await ctx.send(
                    embed = errors.get_error_message(
                        "That is an invalid command."
                    ),
                    delete_after = 5
                )
            
            # Command is valid
            else:

                # Check if the command can be accessed by the author
                check_perms = cogs[command.cog_name]["check"]
                if check_perms == None or await check_perms(ctx):

                    # Create command embed
                    embed = discord.Embed(
                        title = command.name,
                        description = command.description,
                        colour = await get_embed_color(ctx.author)
                    ).set_footer(
                        text = "❕❕❕ Add an extra . to any command for a mobile view!"
                    )

                    # Only add parameters if it exists
                    if len(command.clean_params) > 0:
                        params = dict(command.clean_params)

                        embed.add_field(
                            name = "Parameters",
                            value = " ".join(["`{}`".format(param) for param in params.keys()]),
                            inline = False
                        )

                    # Only add aliases if it exists
                    if len(command.aliases) > 0:
                        embed.add_field(
                            name = "Aliases",
                            value = ", ".join(command.aliases),
                            inline = False
                        )

                    await ctx.send(
                        embed = embed
                    )
                
                # Command cannot be accessed
                else:
                    await ctx.send(
                        embed = errors.get_error_message(
                            "You can't run that command here."
                        ),
                        delete_after = 5
                    )
    
    # Specific does equal None; Just send a list of cogs and their descriptions (custom)
    else:

        # Get recent version
        recent = await database.bot.get_recent_update()
        recent = recent["version"]

        # Check if on mobile
        if on_mobile:
            
            # Iterate through cogs
            fields = []
            field_text = ""
            for cog in cogs:

                # Make sure user can see it
                if (True if cogs[cog]["check"] == None else await cogs[cog]["check"](ctx)):

                    # Get the cog text
                    cog_text = cog.title()
                    if "caps" in cogs[cog]:
                        if cogs[cog]["caps"]:
                            cog_text = cog.upper()

                    # Get the description
                    description = "{}{} - `{}`\n".format(
                        cogs[cog]["emoji"], cog_text,
                        prefix + cogs[cog]["command"]
                    )

                    if len(field_text) + len(description) > FIELD_THRESHOLD:
                        fields.append(field_text)
                        field_text = ""
                    
                    field_text += description
            
            if len(field_text) > 0:
                fields.append(field_text)
            
            # Create embed and add all categories
            embed = discord.Embed(
                title = "Omega Psi Commands",
                description = "Here's a list of categories in Omega Psi.",
                colour = await get_embed_color(ctx.author)
            ).set_author(
                name = "Version " + recent
            ).set_footer(
                text = "❕❕❕ Add an extra . to any command for a mobile view!"
            )

            for field in fields:
                embed.add_field(
                    name = "_ _",
                    value = field,
                    inline = False
                )
        
        # Not on mobile
        else:

            # Create embed with all categories as fields
            embed = discord.Embed(
                title = "Omega Psi Commands",
                description = "Here's a list of categories in Omega Psi.",
                colour = await get_embed_color(ctx.author)
            ).set_author(
                name = "Version " + recent
            ).set_footer(
                text = "❕❕❕ Add an extra . to any command for a mobile view!"
            )

            # Iterate through cogs
            for cog in cogs:

                # Get the cog text
                cog_text = cog.title()
                if "caps" in cogs[cog]:
                    if cogs[cog]["caps"]:
                        cog_text = cog.upper()
                
                # Make sure user can see it
                if (True if cogs[cog]["check"] == None else await cogs[cog]["check"](ctx)):
                    embed.add_field(
                        name = cogs[cog]["emoji"] + cog_text,
                        value = "`{}`\n[Hover Me!](https://www.fellowhashbrown.com/projects#omegaPsi \"{}\")".format(
                            prefix + cogs[cog]["command"],
                            cogs[cog]["description"]
                        ),
                        inline = True
                    )
        
        await ctx.send(
            embed = embed
        )

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Run The Bot
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

if __name__ == "__main__":

    for cog in cogs:
        try:
            bot.load_extension(cogs[cog]["extension"])
        except Exception as error:
            print("{} cannot be loaded.\n - {}".format(cog, error))
    
    app.OMEGA_PSI_BOT = bot
    app.keep_alive(bot, cogs)
    bot.run(os.environ["BOT_TOKEN"])
