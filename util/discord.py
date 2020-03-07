from asyncio import wait, FIRST_COMPLETED
from discord import Embed
from requests import post

from cogs.globals import loop, SCROLL_REACTIONS
from cogs.globals import FIRST_PAGE, LAST_PAGE, PREVIOUS_PAGE, NEXT_PAGE, LEAVE, DELETE, CHECK_MARK

from util.functions import add_scroll_reactions, get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def send_webhook_sync(webhook_url, embed):
    """Synchronously sends a webhook to the specified webhook URL.
    This uses the embed given to send it to the proper channel in discord

    Parameters
    ----------
        webhook_url : str
            The URL to send a webhook through
        embed : Embed
            The embed object to send through the webhook
    """
    post(
        webhook_url, 
        json = { "embeds": [ embed.to_dict() ] },
        headers = { "Content-Type": "application/json"}
    )

async def send_webhook(webhook_url, embed):
    """Asynchronously sends a webhook to the specified webhook URL.
    This uses the embed given to send it to the proper channel in discord

    Parameters
    ----------
        webhook_url : str
            The URL to send a webhook through
        embed : Embed
            The embed object to send through the webhook
    """
    await loop.run_in_executor(None, send_webhook_sync, webhook_url, embed)

async def process_page_reactions(ctx, bot, base_embed, title, pages, *, key = None, image = False, approve_function = None, deny_function = None):
    """Processes the reactions given to an embed to scroll through pages of the embed
    If no base_embed is given, it is assumed that the pages parameter holds individual Embeds

    Parameters
    ----------
        ctx : context
            The context where the message is sent
        bot : bot
            The discord bot object that controls the waiting for reactions
        base_embed : Embed
            The base embed that the scrolling message will always show
        title: str
            The title of each page of the scrolling message
        pages : list
            The list of pages that will be processed for the embed
    """

    # If there is no embed, the pages are individual embeds, only deal with those
    #   however, if a key is specified, use that data to store the data into the embed
    #   if image is True, set the image of an embed
    current_page = 0
    if base_embed and not key:

        # Make a copy of the base embed and add the first page as a field
        embed = base_embed.copy()
        embed.add_field(
            name = "{} {}".format(
                title, "({} / {})".format(
                    current_page + 1, len(pages)
                ) if len(pages) > 1 else ""
            ),
            value = pages[current_page],
            inline = False
        )
    elif key:
        embed = Embed(
            title = key(pages[current_page])["title"],
            description = key(pages[current_page])["description"],
            colour = await get_embed_color(ctx.author)
        )

        if image:
            embed.set_image(
                url = key(pages[current_page])["url"]
            )
    else:
        embed = pages[current_page]

    # Send the message to keep track of the reactions
    message = await ctx.send(embed = embed)
    await add_scroll_reactions(message, pages)

    # Add the approve/deny reactions to the message
    if approve_function != None:
        await message.add_reaction(DELETE)
    
    if deny_function != None:
        await message.add_reaction(CHECK_MARK)
    
    # Continue waiting for reactions until the reaction is a LEAVE reaction
    while True:
        
        # Wait for the reaction but only wait until the author reacts to the specific message
        #   once the user reacts, cancel all futures because the reaction has already been detected
        def check_reaction(reaction, user):
            return (
                reaction.message.id == message.id and
                ctx.author.id == user.id and
                str(reaction) in SCROLL_REACTIONS
            )
        done, pending = await wait([
            bot.wait_for("reaction_add", check = check_reaction),
            bot.wait_for("reaction_remove", check = check_reaction)
        ], return_when = FIRST_COMPLETED)
        reaction, user = done.pop().result()
        reaction = str(reaction)
        for future in pending:
            future.cancel()

        # Check which reaction was clicked and go to the proper page
        if reaction == FIRST_PAGE:
            current_page = 0
        elif reaction == LAST_PAGE:
            current_page = len(pages) - 1
        elif reaction == PREVIOUS_PAGE:
            current_page -= 1 if current_page > 0 else 0
        elif reaction == NEXT_PAGE:
            current_page += 1 if (current_page < len(pages) - 1) else 0
        elif reaction == LEAVE:
            await message.delete()
            break
        elif reaction == DELETE and deny_function != None:
            await deny_function(current_page)
        elif reaction == CHECK_MARK and approve_function != None:
            await approve_function(current_page)
        
        # Update the embed; if there was no base_embed, the pages are the embeds
        if base_embed:
            embed = base_embed.copy()
            embed.add_field(
                name = "{} {}".format(
                    title, "({} / {})".format(
                        current_page + 1, len(pages)
                    ) if len(pages) > 1 else ""
                ),
                value = pages[current_page],
                inline = False
            )
        else:
            embed = pages[current_page]
        await message.edit(embed = embed)

async def process_scrolling(ctx, bot, *, base_embed = None, title = None, pages = None, approve_function = None, deny_function = None, refresh_function = None, current_page = 0, min_page = 0, max_page = 1, send_page = False):
    """Processes scrolling through an embed dynamically

    Parameters
    ----------
        ctx : Context
            The context that the embed message is sent
        bot : AutoShardedBot
            The bot object that is used to wait for reactions
    
    Keyword Parameters
    ------------------
        base_embed : Embed
            The base embed for the scrolling embed
        title : str
            A custom title to use for pagination when using fields in an embed
        pages : list
            A list of pages to process from
            If no base embed is specified, the pages are assumed to be a list of Embed objects
            However, if the base embed is specified, the pages are strings to be inserted into the value
                of an embed field
        approve_function : coroutine
            The coroutine to call whenever the approve emoji is reacted with
        deny_function : coroutine
            The coroutine to call whenever the deny emojiy is reacted with
        refresh_function : coroutine
            The coroutine to call whenever a new page is being processed
            This function should have two parameters: one for the ctx and
                one for the current value. It should return an embed to be used in a message
        current_page : int
            The page to start the embed at
    """
    
    # If there is no embed, the pages are individual embeds, only deal with those
    #   however, if a key is specified, use that data to store the data into the embed
    #   if image is True, set the image of an embed
    current_page = current_page if current_page else 0
    if base_embed:

        # Make a copy of the base embed and add the first page as a field
        embed = base_embed.copy()
        embed.add_field(
            name = "{} {}".format(
                title, "({} / {})".format(
                    current_page + 1, len(pages)
                ) if len(pages) > 1 else ""
            ),
            value = pages[current_page],
            inline = False
        )
    elif not refresh_function:
        embed = pages[current_page]
        min_page = 0
        max_page = len(pages) - 1
    elif send_page:
        embed = await refresh_function(ctx, pages[current_page])
    else:
        embed = await refresh_function(ctx, current_page)

    # Send the message to keep track of the reactions
    message = await ctx.send(embed = embed)
    if pages:
        await add_scroll_reactions(message, pages)
    else:
        await add_scroll_reactions(message, range(min_page, max_page))

    # Add the approve/deny reactions to the message
    if approve_function != None:
        await message.add_reaction(DELETE)
    
    if deny_function != None:
        await message.add_reaction(CHECK_MARK)
    
    # Continue waiting for reactions until the reaction is a LEAVE reaction
    while True:
        
        # Wait for the reaction but only wait until the author reacts to the specific message
        #   once the user reacts, cancel all futures because the reaction has already been detected
        def check_reaction(reaction, user):
            return (
                reaction.message.id == message.id and
                ctx.author.id == user.id and
                str(reaction) in SCROLL_REACTIONS
            )
        done, pending = await wait([
            bot.wait_for("reaction_add", check = check_reaction),
            bot.wait_for("reaction_remove", check = check_reaction)
        ], return_when = FIRST_COMPLETED)
        reaction, user = done.pop().result()
        reaction = str(reaction)
        for future in pending:
            future.cancel()

        # Check which reaction was clicked and go to the proper page
        if reaction == FIRST_PAGE:
            current_page = min_page
        elif reaction == LAST_PAGE:
            current_page = max_page
        elif reaction == PREVIOUS_PAGE:
            current_page -= 1 if current_page > min_page else 0
        elif reaction == NEXT_PAGE:
            current_page += 1 if current_page < max_page else 0
        elif reaction == LEAVE:
            await message.delete()
            break
        elif reaction == DELETE and deny_function != None:
            await deny_function(current_page)
        elif reaction == CHECK_MARK and approve_function != None:
            await approve_function(current_page)
        
        # Update the embed; if there was no base_embed, the pages are the embeds
        if base_embed:
            embed = base_embed.copy()
            embed.add_field(
                name = "{} {}".format(
                    title, "({} / {})".format(
                        current_page + 1, len(pages)
                    ) if len(pages) > 1 else ""
                ),
                value = pages[current_page],
                inline = False
            )
        elif not refresh_function:
            embed = pages[current_page]
        elif send_page:
            embed = await refresh_function(ctx, pages[current_page])
        else:
            embed = await refresh_function(ctx, current_page)
        await message.edit(embed = embed)