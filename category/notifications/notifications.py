import discord

from discord.ext import commands

from category import errors
from category.globals import FIELD_THRESHOLD

from database import loop
from database import database

# # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # #

class Notifications(commands.Cog, name = "Notifications"):
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @commands.command(
        name = "notify",
        description = "Notifies you about the online status of a user or a bot.",
        cog_name = "Notifications"
    )
    async def notify(self, ctx, member: discord.Member = None):

        # Check if no member was mentioned
        if member == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need to mention the member you want to get notified about."
                )
            )
        
        # A member was mentioned
        else:

            # Add the listener to the database
            await database.online_status.add_listener(ctx.author, member)

            await ctx.send(
                embed = discord.Embed(
                    title = "Notifications Added",
                    description = "You are now being notified about the online status of {}.".format(
                        member.mention
                    ),
                    colour = 0x00FF00
                )
            )
    
    @commands.command(
        name = "delete",
        description = "Stops notifying you about the online status of a user or a bot.",
        cog_name = "Notifications"
    )
    async def delete(self, ctx, member: discord.Member = None):

        # Check if there is no member mentioned
        if member == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need to mention the member you want to delete notifications for."
                )
            )
        
        # A member was mentioned
        else:

            # Remove the listener from the database
            await database.online_status.delete_listener(ctx.author, member)

            await ctx.send(
                embed = discord.Embed(
                    title = "Notifications Deleted",
                    description = "You are no longer being notified about the online status of {}.".format(
                        member.mention
                    ),
                    colour = 0xFF0000
                )
            )
    
    @commands.command(
        name = "toggle",
        description = "Toggles whether or not you receive the notifications for a user or a bot.",
        cog_name = "Notifications"
    )
    async def toggle(self, ctx, member: discord.Member = None):

        # Check if no member was mentioned
        if member == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need to mention the member you want to toggle the notifications for."
                )
            )
        
        # A member was mentioned
        else:

            # Toggle the listener in the database
            await database.online_status.toggle_listener(ctx.author, member)

            # Get the status of the listener from the database
            notifying = await database.online_status.listener_status(ctx.author, member)

            await ctx.send(
                embed = discord.Embed(
                    title = "Notifications Turned {}".format(
                        "On" if notifying else "Off"
                    ),
                    description = "You are {} notified about the online status of {}.".format(
                        "being" if notifying else "temporarily not being",
                        member.mention
                    ),
                    colour = 0xFFFF00
                )
            )
    
    @commands.command(
        name = "list",
        description = "Lists all the notifications you receive and whether or not they are active.",
        cog_name = "Notifications"
    )
    async def notify_list(self, ctx):

        # Get a list of the listeners for the user
        try:
            listeners = await database.online_status.get_listeners(ctx.author)
        except IndexError:
            listeners = []

        # Check if there are any listeners
        if len(listeners) > 0:

            # Create a list with the bot/user name along with a green checkmark
            # or a red X to display whether or not the user is receiving notifications
            fields = []
            field_text = ""

            # Iterate through the listeners
            count = 0
            for listener in listeners:
                count += 1

                # Get the target user
                user = self.bot.get_user(int(listener))

                # Add it to the text list
                field_text += "{}#{} - {}\n".format(
                    user.name, user.discriminator,
                    "✔️" if listeners[listener] else "❌"
                )

                if len(field_text) > FIELD_THRESHOLD:
                    fields.append(field_text)
                    field_text = ""
            
            if len(field_text) > 0:
                fields.append(field_text)
            
            # Create an embed
            embed = discord.Embed(
                title = "Notifications {}".format(
                    "({} / {})".format(
                        1, len(fields)
                    ) if len(fields) > 1 else ""
                ),
                description = fields[0],
                colour = 0x00FF00
            )
            
            count = 1
            for field in fields[1:]:
                count += 1
                embed.add_field(
                    name = "Notifications {}".format(
                        "({} / {})".format(
                            count, len(fields)
                        ) if len(fields) > 1 else ""
                    ),
                    value = field,
                    inline = False
                )
        
        # There are no listeners
        else:
            embed = discord.Embed(
                title = "No Notifications",
                description = "You are not being notified of anybody's online status.",
                colour = 0x0080FF
            )
        
        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(Notifications(bot))