import app, asyncio, discord, os, requests, traceback

from discord.ext.commands import AutoShardedBot
from functools import partial

from category import errors
from category.globals import PRIMARY_EMBED_COLOR, MESSAGE_THRESHOLD, FIELD_THRESHOLD
from category.globals import SCROLL_REACTIONS, FIRST_PAGE, LAST_PAGE, PREVIOUS_PAGE, NEXT_PAGE, LEAVE
from category.globals import add_scroll_reactions
from category.predicates import get_prefix, is_nsfw_or_private
from database import database

# Open Bot Client
bot = AutoShardedBot(command_prefix = get_prefix, case_insensitive = True)
bot.remove_command("help")

# Keep track of extensions
exts = [
    "category.code.code",
    "category.game.game",
    "category.internet.internet",
    "category.image.image",
    "category.misc.misc",
    "category.nsfw.nsfw",
    "category.stats.stats",
    "category.bot.bot",
    "category.info.info",
    "category.insults.insults"
]

cogs = {
    "Code": {
        "command": "help code",
        "description": "All things having to do with coding go here.",
        "check": None
    },
    "Game": {
        "command": "help game",
        "description": "There are games in this category!",
        "check": None
    },
    "Internet": {
        "command": "help internet",
        "description": "All internet-based commands go here.",
        "check": None
    },
    "Image": {
        "command": "help image",
        "description": "Image commands are here! Hint: dog's and cat's are here too.",
        "check": None
    },
    "Insults": {
        "command": "help insults",
        "description": "If you feel in the mood for insults, here you are!",
        "check": None
    },
    "Misc": {
        "command": "help misc",
        "description": "This category has commands that really don't fit anywhere.",
        "check": None
    },
    "NSFW": {
        "command": "help nsfw",
        "description": "18+ ;)",
        "check": is_nsfw_or_private
    },
    "Stats": {
        "command": "help stats",
        "description": "Video Game stats! For all sorts of games!",
        "check": None
    },
    "Bot": {
        "command": "help bot",
        "description": "Primarily bot-related commands.",
        "check": None
    },
    "Info": {
        "command": "help info",
        "description": "Basic info stuff really.",
        "check": None
    }
}

cog_emojis = {
    "Code": ":keyboard: ",
    "Game": ":video_game: ",
    "Internet": ":desktop: ",
    "Image": ":frame_photo: ",
    "Insults": ":exclamation: ",
    "Misc": ":mag: ",
    "NSFW": ":underage: ",
    "Stats": ":clipboard: ",
    "Bot": ":robot: ",
    "Info": ":question: "
}

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Basic Events
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@bot.event
async def on_ready():

    print("I'm ready to go.")
    activity_type = await database.get_activity_type()
    activity_name = await database.get_activity_name()
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
    restart = await database.get_restart()

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
        await database.set_restart(restart)

        # Send the message
        await channel.send(
            "{}, I'm back!".format(author.mention)
        )

@bot.event
async def on_command(ctx):
    async with ctx.typing():
        pass

@bot.event
async def on_command_error(ctx, error):
    
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

@bot.event
async def on_command_completion(ctx):

    # Create embed
    embed = discord.Embed(
        title = "Command Success",
        description = ctx.message.content,
        color = 0x008000
    )

    # Add fields
    fields = {
        "Command Author": ctx.author,
        "Guild Name": ctx.guild.name if ctx.guild != None else "Private Message",
        "Channel Name": ctx.channel.name if ctx.guild != None else "Private Message with {}#{}".format(ctx.author.name, ctx.author.discriminator)
    }

    for field in fields:
        embed.add_field(
            name = field,
            value = fields[field],
            inline = False
        )
    
    # Get the error channel
    channel = bot.get_channel(int(os.environ["COMMAND_SUCCESS_CHANNEL"]))

    await channel.send(
        embed = embed
    )

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Guild Events
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@bot.event
async def on_guild_join(guild):
    
    # Send message to primary channel channel in guild
    channel = guild.system_channel

    embed = discord.Embed(
        title = "Hello!",
        description = (
            """
            Greetings! I am Omega Psi. I was created by _**Fellow Hashbrown#4323**_
            I used to be a moderation bot and an entertainment bot but I couldn't handle that.
            So now I'm just an entertainment bot! Thanks!
            """
        ),
        colour = PRIMARY_EMBED_COLOR
    )

    # Send notification through IFTTT that Omega Psi has joined a new server
    await database.loop.run_in_executor(None,
        partial(
            requests.post,
            "https://maker.ifttt.com/trigger/on_error/with/key/{}".format(os.environ["IFTTT_WEBHOOK_KEY"]),
            json = {
                "value1": "Omega Psi\n",
                "value2": "Added to new Discord server.\n",
                "value3": "Guild: {}\nOwner: {}".format(guild.name, guild.owner)
            }
        )
    )

    # Update presence
    activity_type = await database.get_activity_type()
    activity_name = await database.get_activity_name()
    activity_name = "{} | Currently in {} Servers".format(
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

    try:
        await channel.send(
            embed = embed
        )
    except:
        pass

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Global Commands
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

@bot.command(
    name = "help", 
    aliases = ["h", "?"]
)
async def help(ctx, specific = None):

    # Get prefix
    if ctx.guild != None:
        prefix = await database.get_prefix(ctx.guild)
    
    else:
        prefix = "o."
    
    # See if getting help for a specific category or command
    if specific != None:

        # Specific help is a Cog
        if specific.title() in cogs and (await cogs[specific.title()]["check"](ctx) if cogs[specific.title()]["check"] != None else True):

            # Create fields for all commands
            commands = bot.get_cog_commands(specific.title())
            commands = sorted(commands, key = lambda k: k.name)

            fields = []
            fieldText = ""
            for command in commands:

                # Filter based on author and channel
                if not await command.can_run(ctx):
                    continue

                name_descr = "`{}{}` - {}\n".format(
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
            
            # Create embed for menu
            embed = discord.Embed(
                title = "{} {}".format(
                    cog_emojis[specific.title()] + specific.title(),
                    "- Page ({} / {})".format(
                        1, len(fields)
                    ) if len(fields) > 1 else ""
                ),
                description = fields[0],
                colour = PRIMARY_EMBED_COLOR
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
                            cog_emojis[specific.title()] + specific.title(),
                            "- Page ({} / {})".format(
                                current + 1, len(fields)
                            ) if len(fields) > 1 else ""
                        ),
                        description = fields[current],
                        colour = PRIMARY_EMBED_COLOR
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
                        colour = PRIMARY_EMBED_COLOR
                    )

                    # Only add parameters if it exists
                    if len(command.clean_params) > 0:
                        params = dict(command.clean_params)

                        embed.add_field(
                            name = "Parameters",
                            value = " ".join(params.keys()),
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
        recent = await database.get_recent_update()
        recent = recent["version"]

        # Create embed with all categories as fields
        embed = discord.Embed(
            title = "Omega Psi Commands",
            description = "Here's a list of categories in Omega Psi.",
            colour = PRIMARY_EMBED_COLOR
        ).set_author(
            name = "Version " + recent
        )

        # Iterate through cogs
        for cog in cogs:
            
            # Make sure user can see it
            if (True if cogs[cog]["check"] == None else await cogs[cog]["check"](ctx)):
                embed.add_field(
                    name = cog_emojis[cog] + cog,
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

    for ext in exts:
        try:
            bot.load_extension(ext)
        except Exception as error:
            print("{} cannot be loaded.\n - {}".format(ext, error))
        
    app.keep_alive(bot, cogs)
    bot.run(os.environ["BOT_TOKEN"])
