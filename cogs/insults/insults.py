from discord import Embed, Member, DMChannel
from discord.ext.commands import Cog, command

from cogs.errors import NotADeveloper, NOT_A_DEVELOPER_ERROR, NO_INSULT_ERROR, NO_COMPLIMENT_ERROR
from cogs.globals import PRIMARY_EMBED_COLOR
from cogs.predicates import is_developer

from util.database.database import database

from util.discord import process_page_reactions
from util.functions import create_fields, get_embed_color


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class Insults(Cog, name="insults"):
    """If you feel in the mood for insults or compliments, try these commands"""

    def __init__(self, bot):
        self.bot = bot

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @command(
        name="insult",
        description="Allows you to insult someone or be insulted.",
        cog_name="insults"
    )
    async def insult(self, ctx, *, member: Member = None):
        """Allows a user to insult someone or be insulted

        :param ctx: The context of where the message was sent
        :param member: The member to insult
        """

        # Get a random insult
        insult = await database.data.get_insult(
            ctx.channel.is_nsfw()
            if not isinstance(ctx.channel, DMChannel) else
            True
        )

        # Check if insulting self
        if not member:
            member = ctx.author
        await ctx.send(
            "{}, {}".format(
                member.mention, insult["insult"]
            )
        )

    @command(
        name="viewInsults",
        aliases=["viewI", "vi"],
        description="Let's you view a list of insults that can be sent.",
        cog_name="insults"
    )
    async def view_insults(self, ctx):
        """Allows a user to view insults in the bot

        :param ctx: The context of where the message was sent
        """

        # Get a list of insults
        insults = await database.data.get_insults()

        # Add each insult to fields and create a base embed for viewing insults
        fields = create_fields(insults, key=lambda insult: insult["insult"])
        embed = Embed(
            title="Insults",
            description="Here's a list of insults in the bot.",
            colour=await get_embed_color(ctx.author)
        )

        # Let the user scroll through an embed if needed
        await process_page_reactions(ctx, self.bot, embed, "Insults", fields)

    @command(
        name="addInsult",
        alises=["addI", "ai"],
        description="Let's you add a custom insult to the bot.",
        cog_name="insults"
    )
    async def add_insult(self, ctx, *, insult=None):
        """Allows a user to add a custom insult to the bot

        :param ctx: The context of where the message was sent
        :param insult: The insult to add
        """

        # Check if there is no insult
        if not insult:
            await ctx.send(
                embed=NO_INSULT_ERROR
            )

        # An insult was provided
        else:

            # Add the insult to pending insults
            await database.data.add_pending_insult(insult, str(ctx.author.id))

            # Notify all developers
            for dev in await database.bot.get_developers():
                user = self.bot.get_user(int(dev))
                if user is not None:
                    await user.send(
                        embed=Embed(
                            title="New Pending Insult",
                            description=" ",
                            colour=await get_embed_color(user)
                        ).add_field(
                            name="Author",
                            value=str(ctx.author),
                            inline=False
                        ).add_field(
                            name="Insult",
                            value=insult,
                            inline=False
                        )
                    )

            # Confirm to the user the insult was sent
            await ctx.send(
                embed=Embed(
                    title="Insult Pending!",
                    description="Your insult was added to be reviewed by an Omega Psi developer.",
                    colour=await get_embed_color(ctx.author)
                )
            )

    @command(
        name="compliment",
        description="Allows you to compliment someone or be complimented.",
        cog_name="insults"
    )
    async def compliment(self, ctx, *, member: Member = None):
        """Allows a user to compliment someone or be complimented

        :param ctx: The context of where the message was sent
        :param member: The member to compliment
        """

        # Get a random compliment
        compliment = await database.data.get_compliment(
            ctx.channel.is_nsfw()
            if not isinstance(ctx.channel, DMChannel) else
            True
        )

        # Check if complimenting self
        if not member:
            member = ctx.author
        await ctx.send(
            "{}, {}".format(
                member.mention, compliment["compliment"]
            )
        )

    @command(
        name="viewCompliments",
        aliases=["viewC", "vc"],
        description="Let's you view a list of compliments that can be sent.",
        cog_name="insults"
    )
    async def view_compliments(self, ctx):
        """Allows a user to view the compliments in the bot

        :param ctx: The context of where the message was sent
        """

        # Get a list of compliments
        compliments = await database.data.get_compliments()

        # Add each compliment to fields and create a base embed for viewing compliments
        fields = create_fields(compliments, key=lambda compliment: compliment["compliment"])
        embed = Embed(
            title="Compliments",
            description="Here's a list of compliments in the bot.",
            colour=await get_embed_color(ctx.author)
        )

        # Let the user scroll through an embed if needed
        await process_page_reactions(ctx, self.bot, embed, "Compliments", fields)

    @command(
        name="addCompliment",
        aliases=["addC", "ac"],
        description="Let's you add a custom compliment to the bot.",
        cog_name="insults"
    )
    async def add_compliment(self, ctx, *, compliment=None):
        """Allows a user to add a compliment to the bot

        :param ctx: The context of where the message was sent
        :param compliment: The compliment to add
        """

        # Check if there is no compliment
        if not compliment:
            await ctx.send(
                embed=NO_COMPLIMENT_ERROR
            )

        # A compliment was provided
        else:

            # Add the compliment to pending compliments
            await database.data.add_pending_compliment(compliment, str(ctx.author.id))

            # Notify all developers
            for dev in await database.bot.get_developers():
                user = self.bot.get_user(int(dev))
                if user is not None:
                    await user.send(
                        embed=Embed(
                            title="New Pending Compliment",
                            description=" ",
                            colour=await get_embed_color(user)
                        ).add_field(
                            name="Author",
                            value=str(ctx.author),
                            inline=False
                        ).add_field(
                            name="Compliment",
                            value=compliment,
                            inline=False
                        )
                    )

            # Confirm to the user the compliment was sent
            await ctx.send(
                embed=Embed(
                    title="Compliment Pending!",
                    description="Your compliment was added to be reviewed by an Omega Psi developer.",
                    colour=await get_embed_color(ctx.author)
                )
            )

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @command(
        name="pendingInsults",
        aliases=["pendingI"],
        description="Shows a list of pending insults.",
        cog_name="insults"
    )
    @is_developer()
    async def pending_insults(self, ctx):
        """Allows a developer to view pending insults

        :param ctx: The context of where the message was sent
        """

        # Get a list of pending insults in the bot
        pending_insults = await database.data.get_pending_insults()

        # Only create the fields if there are pending compliments
        if len(pending_insults) > 0:

            # Create the fields for pending insults
            fields = []
            for i in range(len(pending_insults)):
                pending_insult = pending_insults[i]
                fields.append(
                    Embed(
                        title="Pending Insults {}".format(
                            "({} / {})".format(
                                i + 1, len(pending_insults)
                            ) if len(pending_insults) > 1 else ""
                        ),
                        description=" ",
                        colour=PRIMARY_EMBED_COLOR
                    ).add_field(
                        name="Insult",
                        value=pending_insult["insult"]
                    ).add_field(
                        name="Author",
                        value=(
                            "Unknown"
                            if not self.bot.get_user(int(pending_insult["author"])) else
                            str(self.bot.get_user(int(pending_insult["author"])))
                        )
                    )
                )

            # Let the user scroll through pending insults
            await process_page_reactions(ctx, self.bot, None, "Pending Insults", fields,
                                         approve_function=lambda index: self.approve(ctx, index),
                                         deny_function=lambda index: self.deny(ctx, index)
                                         )

        # If there are no pending insults, let the user know
        else:
            await ctx.send(
                embed=Embed(
                    title="No Pending Insults",
                    description="There are currently no pending insults to review.",
                    colour=await get_embed_color(ctx.author)
                )
            )

    @command(
        name="pendingCompliments",
        aliases=["pendingC"],
        description="Shows a list of pending compliments.",
        cog_name="insults"
    )
    @is_developer()
    async def pending_compliments(self, ctx):
        """Allows a developer to view pending compliments

        :param ctx: The context of where the message was sent
        """

        # Get a list of pending compliments in the bot
        pending_compliments = await database.data.get_pending_compliments()

        # Only create the fields if there are pending compliments
        if len(pending_compliments) > 0:

            # Create the fields for pending compliments
            fields = []
            for i in range(len(pending_compliments)):
                pending_compliment = pending_compliments[i]
                fields.append(
                    Embed(
                        title="Pending Compliments {}".format(
                            "({} / {})".format(
                                i + 1, len(pending_compliments)
                            ) if len(pending_compliments) > 1 else ""
                        ),
                        description=" ",
                        colour=PRIMARY_EMBED_COLOR
                    ).add_field(
                        name="Compliment",
                        value=pending_compliment["compliment"]
                    ).add_field(
                        name="Author",
                        value=(
                            "Unknown"
                            if not self.bot.get_user(int(pending_compliment["author"])) else
                            str(self.bot.get_user(int(pending_compliment["author"])))
                        )
                    )
                )

            # Let the user scroll through pending compliments
            await process_page_reactions(ctx, self.bot, None, "Pending Compliments", fields,
                                         approve_function=lambda index: self.approve(ctx, index, is_insult=False),
                                         deny_function=lambda index: self.deny(ctx, index, is_insult=False)
                                         )

        # If there are no pending compliments, let the user know
        else:
            await ctx.send(
                embed=Embed(
                    title="No Pending Compliments",
                    description="There are currently no pending compliments to review.",
                    colour=await get_embed_color(ctx.author)
                )
            )

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @pending_insults.error
    @pending_compliments.error
    async def developer_error(self, ctx, error):
        """Handles errors having to do with not being a developer

        :param ctx: The context of where the error occurred
        :param error: The error that occurred
        """

        # Check if the error has to deal with not being a developer
        if isinstance(error, NotADeveloper):
            await ctx.send(embed=NOT_A_DEVELOPER_ERROR)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def approve(self, ctx, index, *, is_insult=True):
        """Approves a pending insult or compliment at the specified index and lets
        the original author know that their insult has been approved

        :param ctx: The context of where to send the confirmation message to whoever
            reacted with the approve reaction
        :param index: The index of the pending insult or compliment to approve
        :param is_insult: Whether or not to approve an insult or compliment at the specified index.
            Defaults to True
        """

        # Get the pending insult/compliment and the original author, and approve the insult/compliment
        if is_insult:
            pending_insults = await database.data.get_pending_insults()
            pending_data = pending_insults[index]["insult"]
            author = pending_insults[index]["author"]
            await database.data.approve_pending_insult(index)
        else:
            pending_compliments = await database.data.get_pending_compliments()
            pending_data = pending_compliments[index]["compliment"]
            author = pending_compliments[index]["author"]
            await database.data.approve_pending_compliment(index)

        # Let the original author know their insult/compliment was approved
        #   if the user cannot be found anymore, don't send anything
        user = self.bot.get_user(int(author))
        if user:
            await user.send(
                embed=Embed(
                    title="{} Approved!".format(
                        "Insult" if is_insult else "Compliment"
                    ),
                    description="The {} you wanted to add: `{}`\nhas been approved and added to the bot!".format(
                        "insult" if is_insult else "compliment",
                        pending_data
                    ),
                    colour=await get_embed_color(user)
                )
            )

        # Confirm to the approver that the insult/compliment has been approved
        await ctx.send(
            embed=Embed(
                title="{} Approved".format(
                    "Insult" if is_insult else "Compliment"
                ),
                description=" ",
                colour=await get_embed_color(ctx.author)
            ).add_field(
                name="Insult" if is_insult else "Compliment",
                value=pending_data
            ).add_field(
                name="Author",
                value="Unknown" if not user else str(user)
            ),
            delete_after=10
        )

    async def deny(self, ctx, index, *, is_insult=True):
        """Denies a pending insult or compliment at the specified index and lets
        the original author know that their insult has been denied with a reason
        given by the denier

        :param ctx: The context of where to send the confirmation message to whoever
            reacted with the deny reaction
        :param index: The index of the pending insult or compliment to deny
        :param is_insult: Whether or not to deny an insult at the specified index.
            Defaults to True
        """

        # Get the pending insult/compliment and the original author, and approve the insult/compliment
        if is_insult:
            pending_insults = await database.data.get_pending_insults()
            pending_data = pending_insults[index]["insult"]
            author = pending_insults[index]["author"]
            await database.data.deny_pending_insult(index)
        else:
            pending_compliments = await database.data.get_pending_compliments()
            pending_data = pending_compliments[index]["compliment"]
            author = pending_compliments[index]["author"]
            await database.data.deny_pending_compliment(index)

        # Ask the denier for a reason that the specified insult/compliment was denied
        await ctx.send(
            embed=Embed(
                title="Provide a Reason",
                description="Send a message with the reason that the {} was denied.".format(
                    "insult" if is_insult else "compliment"
                ),
                colour=await get_embed_color(ctx.author)
            )
        )

        def check_message(m):
            return (
                    m.author.id == ctx.author.id and
                    m.channel.id == ctx.channel.id
            )

        message = await self.bot.wait_for("message", check=check_message)
        reason = message.content

        # Let the original author know their insult/compliment was denied
        #   and for what reason it was denied
        #   if the user cannot be found anymore, don't send anything
        user = self.bot.get_user(int(author))
        if user:
            await user.send(
                embed=Embed(
                    title="{} Denied".format(
                        "Insult" if is_insult else "Compliment"
                    ),
                    description="The {} you wanted to add: `{}`\nhas been denied.".format(
                        "insult" if is_insult else "compliment",
                        pending_data
                    ),
                    colour=await get_embed_color(user)
                ).add_field(
                    name="Reason",
                    value=reason,
                    inline=False
                )
            )

        # Confirm to the approver that the insult/compliment has been approved
        await ctx.send(
            embed=Embed(
                title="{} Denied".format(
                    "Insult" if is_insult else "Compliment"
                ),
                description=" ",
                colour=await get_embed_color(ctx.author)
            ).add_field(
                name="Insult" if is_insult else "Compliment",
                value=pending_data
            ).add_field(
                name="Author",
                value="Unknown" if not user else str(user)
            ).add_field(
                name="Reason",
                value=reason
            ),
            delete_after=10
        )

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def setup(bot):
    """Add's this cog to the bot

    :param bot: The bot to add the cog to
    """
    bot.add_cog(Insults(bot))
