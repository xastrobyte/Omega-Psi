from cogs.globals import FIRST_PAGE, LAST_PAGE, PREVIOUS_PAGE, NEXT_PAGE, LEAVE
from cogs.globals import PRIMARY_EMBED_COLOR, FIELD_THRESHOLD, loop

from util.database.database import database

async def add_scroll_reactions(message, fields):
    """Adds the scrolling reactions to a message based off how many fields there are.

    :param message: The discord message that the reactions are being added to
    :param fields: A list of items that are being scrolled through
    """

    # Only add scrolling reactions if there are more than 1 page
    if len(fields) > 1:

        # If there are more than 2 pages, add a first page and last page reaction
        if len(fields) > 2:
            await message.add_reaction(FIRST_PAGE)
        
        await message.add_reaction(PREVIOUS_PAGE)
        await message.add_reaction(NEXT_PAGE)
    
        # If there are more than 2 pages, add a first page and last page reaction
        if len(fields) > 2:
            await message.add_reaction(LAST_PAGE)
    
    # The leave reaction is always added to stop the scrolling
    await message.add_reaction(LEAVE)

def add_fields(embed, field_name, fields, *, empty_message = None):
    """Adds fields to an embed with field numbers that correspond to how many different fields
    there are

    :param embed: The discord embed to add the fields to
    :param field_name: The name that each field should have
    :param fields: The fields to process through
    :param empty_message: A string that is given in the embed whenever there are no fields
    """

    # Check if there are no fields, display the empty message
    if len(fields) == 0:
        embed.add_field(
            name = field_name,
            value = empty_message if empty_message else "",
            inline = False
        )

    # There are fields to go through, add them to the embed
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
    
def create_fields(data, *, by_word = False, threshold = FIELD_THRESHOLD, key = None, include_count = False, new_line = True):
    """Creates fields based on a given list of inputs

    :param data: An iterable to add to field text
    :param by_word: Whether or not to split up the data by word (if str is given)
    :param threshold: The maximum size of the data to add to a field
    :param key: A custom function to format the data after it's been loaded
    :param include_count: Whether or not to include the field count in the title of each field
    :param new_line: Whether or not to add a new line to each value in the data
    """

    # Check if the data is not a list; Make a list out of it
    if type(data) == str:

        # Split data up by word
        if by_word:
            data = data.split(" ")
        
        # Split data up by newline
        else:
            data = data.split("\n")
    
    # Keep track of each of the fields
    fields = []
    field_text = ""
    count = 0
    for line in data:

        if key:
            if include_count:
                line = key(line, count) + ("\n" if new_line else " ")
            else:
                line = key(line) + ("\n" if new_line else " ")
        else:
            line += "\n" if new_line else " "
            
        if len(line) + len(field_text) > threshold:
            fields.append(field_text)
            field_text = ""
        field_text += line
    if len(field_text) > 0:
        fields.append(field_text)
    
    return fields

def get_embed_color_sync(user):
    """Retrieves the embed color for the specified user. If they do not have one, the primary color
    is returned

    :param user: The discord user to get the embed color of
    
    :rtype: int
    """
    colour = database.users.get_embed_color_sync(user)
    if colour is None:
        return PRIMARY_EMBED_COLOR
    return colour

async def get_embed_color(user):
    """Retrieves the embed color for the specified user. If they do not have one, the primary color
    is returned

    :param user: The discord user to get the embed color of
    
    :rtype: int
    """
    return await loop.run_in_executor(None, get_embed_color_sync, user)