import discord

from discord.ext import commands

from category import errors
from category.globals import FIELD_THRESHOLD, get_embed_color
from category.predicates import guild_only

from database import database

# # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # #

class Notifications(commands.Cog, name = "notifications"):
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @commands.command(
        name = "setIFTTTKey",
        description = "Allows you to set the webhook key linked to your IFTTT account. This key remains private and will never be accessible by anyone.",
        cog_name = "notifications"
    )
    async def set_ifttt_key(self, ctx, key = None):
        
        # Check if the key does not exist (is None)
        if key == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need to specify the webhook key connected to your IFTTT account."
                )
            )
        
        # The key exists, set the key for the user
        else:

            # Get the IFTTT data for the user
            ifttt_data = await database.users.get_ifttt(ctx.author)
            ifttt_data["webhook_key"] = key

            # Activate IFTTT if webhook_key and event_name both exist (are not None)
            if ifttt_data["webhook_key"] != None:
                ifttt_data["active"] = True
            
            # Set the IFTTT data for the user
            await database.users.set_ifttt(ctx.author, ifttt_data)

            # Send a message to the user
            await ctx.send(
                embed = discord.Embed(
                    title = "Webhook Key Set!",
                    description = "You set your IFTTT webhook key. You will now receive notifications through IFTTT.",
                    colour = await get_embed_color(ctx.author)
                )
            )

    @commands.command(
        name = "toggleIFTTT",
        description = "Allows you to toggle whether or not you receive notifications through IFTTT.",
        cog_name = "notifications"
    )
    async def toggle_ifttt(self, ctx):

        # Get the IFTTT status from the database
        ifttt_data = await database.users.get_ifttt(ctx.author)

        # Check if the webhook key does not exist
        if ifttt_data["webhook_key"] == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need to set your IFTTT webhook key before you can get notifications through IFTTT."
                )
            )
        
        else:

            # Toggle IFTTT in the database
            await database.users.toggle_ifttt(ctx.author)
            
            # Send a message to the user
            await ctx.send(
                embed = discord.Embed(
                    title = "IFTTT {}".format(
                        "Turned On" if ifttt_data["active"] else "Turned Off"
                    ),
                    description = "You will now receive notifications through {}.".format(
                        "your IFTTT connected device" if ifttt_data["active"] else "discord"
                    ),
                    colour = await get_embed_color(ctx.author)
                )
            )
    
    @commands.command(
        name = "helpIFTTT",
        description = "Guides you on how to set up your IFTTT account to receive push notifications with a webhook key and an event name.",
        cog_name = "notifications"
    )
    async def help_ifttt(self, ctx):
        
        # Step 1: Create an account (if you don't have one)
        steps = [
            "Go to https://ifttt.com. If you've already signed up, skip to step 5. If not, keep going.",
            "Click **Sign Up** at the top right.",
            "Either use a Google/Facebook account or sign up manually.",
            "If you want to pick and select services at the screen after you sign up, go ahead. If not, click the `X` at the top right.",
            "If you have already connected your webhooks service, skip to step 10.",
            "Search `webhooks` in the search bar at the top of the page.",
            "Click on **Services**. Then click on **Webhooks**. If you have already connected the webhooks service, skip the next step.",
            "Click on **Connect** to connect the webhooks service.",
            "Click on **Settings** at the top right of the webhooks service.",
            "Copy the webhook key that is right after `maker.ifttt.com/use/`",
            "On discord, run Omega Psi's command `o.setIFTTTKey` and add the your webhook key from the previous step to set it.",
            "If you have already connected your notifications service, skip to step 16.",
            "Go back to IFTTT.com and search `notifications` in the search bar at the top of the page.",
            "Click on **Services**. Then click on the first notifications service that appears.",
            "Click on **Connect** to connect the notifications service.",
            "Now click on **My Applets** at the top left of the page.",
            "Click on **New Applet** at the top right.",
            "Click on where it says **this** and search `webhooks`.",
            "Click on the webhooks service and then click on **Receive a web request**.",
            "Where it says **Event Name**, type in `omega_psi_push` and click **Create Trigger**.",
            "Click on where it says **that** and search `notifications`.",
            "Click on the notifications service and the click on **Send a rich notification**.",
            "Where it says **Title**, clear it and type in `{{Value1}}`",
            "Where it says **Message**, clear it and type in `{{Value2}}`.",
            "Press enter and type in `{{Value3}}`. Then click **Create Action**. Then click **Finish**.",
            "Then you're done! You can toggle IFTTT through Omega Psi, or if your webhook key changes, set it through there."
        ]

        # Add the steps to fields
        fields = []
        field_text = ""
        count = 1
        for step in steps:

            step = "{}.) {}\n".format(
                count, step
            )
            count += 1

            if len(field_text) + len(step) > FIELD_THRESHOLD:
                fields.append(field_text)
                field_text = ""
            
            field_text += step
    
        if len(field_text) > 0:
            fields.append(field_text)
        
        # Create embed
        embed = discord.Embed(
            title = "IFTTT Steps",
            description = "_ _",
            colour = await get_embed_color(ctx.author)
        )

        # Add fields
        for field in fields:
            embed.add_field(
                name = "Steps",
                value = field,
                inline = False
            )
        
        # Send message
        await ctx.send(
            embed = embed
        )

    # # # # # # # # # # # # # # # # # # # # # # # # #

    @commands.command(
        name = "notify",
        description = "Notifies you about the online status of a user or a bot.",
        cog_name = "notifications"
    )
    @commands.check(guild_only)
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
                    colour = await get_embed_color(ctx.author)
                )
            )
    
    @commands.command(
        name = "delete",
        description = "Stops notifying you about the online status of a user or a bot.",
        cog_name = "notifications"
    )
    @commands.check(guild_only)
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
                    colour = await get_embed_color(ctx.author)
                )
            )
    
    @commands.command(
        name = "toggle",
        description = "Toggles whether or not you receive the notifications for a user or a bot.",
        cog_name = "notifications"
    )
    @commands.check(guild_only)
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
                    colour = await get_embed_color(ctx.author)
                )
            )
    
    @commands.command(
        name = "list",
        description = "Lists all the notifications you receive and whether or not they are active.",
        cog_name = "notifications"
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

                # Get the target user
                user = self.bot.get_user(int(listener))

                # Check if the user is invalid (user == None)
                if user == None:

                    # Invalidate the listener and remove it from the user's listener
                    await database.online_status.invalidate_listener(ctx.author, listener)
                
                # The user is not invalid
                else:
                    count += 1

                    # Add it to the text list
                    field_text += "{}#{} - {}\n".format(
                        user.name if user != None else "Invalid User", user.discriminator if user != None else "0000",
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
                colour = await get_embed_color(ctx.author)
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
                colour = await get_embed_color(ctx.author)
            )
        
        await ctx.send(embed = embed)
    
    @commands.command(
        name = "clearNotifications",
        aliases = ["clear"],
        description = "Deletes all notifications you may have. Do NOT run this if you want to remove any invalid users. The o.list command does that automatically.",
        cog_name = "notifications"
    )
    async def clear(self, ctx):

        # Clear all listeners
        await database.online_status.clear_listeners(ctx.author)

        # Send a confirm message
        await ctx.send(
            embed = discord.Embed(
                title = "All Notifications Deleted",
                description = "You have deleted all of your notifications.",
                colour = await get_embed_color(ctx.author)
            )
        )
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @notify.error
    @delete.error
    @toggle.error
    async def notify_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(
                embed = errors.get_error_message(
                    "That member does not seem to be in this server :("
                )
            )
        if isinstance(error, commands.CheckFailure):
            await ctx.send(
                embed = errors.get_error_message(
                    "You can only run this command in a guild."
                )
            )

def setup(bot):
    bot.add_cog(Notifications(bot))