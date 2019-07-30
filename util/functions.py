import os, requests

from datetime import datetime
from functools import partial

from category.globals import FIRST_PAGE, LAST_PAGE, PREVIOUS_PAGE, NEXT_PAGE, LEAVE
from category.globals import loop
from category.globals import DBL_VOTE_API_CALL, PRIMARY_EMBED_COLOR, FIELD_THRESHOLD

from database.database import database

async def add_scroll_reactions(message, fields):
    """Adds the scrolling reactions to a message based off how many fields there are."""

    if len(fields) > 1:

        if len(fields) > 2:
            await message.add_reaction(FIRST_PAGE)
        
        await message.add_reaction(PREVIOUS_PAGE)
        await message.add_reaction(NEXT_PAGE)
    
        if len(fields) > 2:
            await message.add_reaction(LAST_PAGE)
    
    await message.add_reaction(LEAVE)

def add_fields(embed, field_name, fields, *, empty_message = None):

    if len(fields) == 0:
        embed.add_field(
            name = field_name,
            value = empty_message if empty_message else "",
            inline = False
        )

    else:
        count = 0
        for field in fields:
            count += 1
            embed.add_field(
                name = "{} {}".format(
                    field_name,
                    "({} / {})".format(
                        count, len(fields)
                    ) if len(fields) > 1 else ""
                ),
                value = field,
                inline = False
            )
    
def create_fields(data, *, by_word = False, threshold = FIELD_THRESHOLD):

    # Check if the data is not a list; Make a list out of it
    if type(data) != list:

        # Split data up by word
        if by_word:
            data = data.split(" ")
        
        # Split data up by newline
        else:
            data = data.split("\n")
    
    fields = []
    field_text = ""
    for line in data:
        line += "\n"
        if len(line) + len(field_text) > threshold:
            fields.append(field_text)
            field_text = ""
        field_text += line
    if len(field_text) > 0:
        fields.append(field_text)
    
    return fields

async def did_author_vote(author):

    # Call DBL API
    response = await loop.run_in_executor(None,
        partial(
            requests.get,
            DBL_VOTE_API_CALL,
            headers = {
                "Authorization": os.environ["DBL_API_KEY"]
            }
        )
    )
    response = response.json()

    # Check if author id is in the votes
    for user in response:
        if str(user["id"]) == str(author.id):

            # Update the previous vote for author in database
            await database.users.set_previous_vote(author, int(datetime.now().timestamp()))
            return True
    
    # Check if author needs to vote
    if await database.users.needs_to_vote(author):
        return False
        
    return True

async def get_color_scheme():
    return await database.bot.get_theme()

async def get_embed_color(user):
    colour = await database.users.get_embed_color(user)

    if colour == None:
        return PRIMARY_EMBED_COLOR
    
    return colour

async def is_on_mobile(ctx):

    # Get prefix
    if ctx.guild != None:
        prefix = await database.guilds.get_prefix(ctx.guild)
    
    else:
        prefix = "o."
    
    # Check if user is on mobile
    return ctx.message.content.startswith(prefix + ".") or ctx.message.content.startswith(".")