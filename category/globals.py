import os, requests
from functools import partial

from database import loop

PRIMARY_EMBED_COLOR = 0xEC7600

DBL_BOT_STAT_API_CALL = "https://discordbots.org/api/bots/535587516816949248/stats"
DBL_VOTE_API_CALL = "https://discordbots.org/api/bots/535587516816949248/votes"

MESSAGE_THRESHOLD = 2000
FIELD_THRESHOLD = 1000

SCROLL_REACTIONS = ["⏪", "⬅", "➡", "⏩", "🚫", "✅", "❌"]
FIRST_PAGE = SCROLL_REACTIONS[0]
LAST_PAGE = SCROLL_REACTIONS[3]
PREVIOUS_PAGE = SCROLL_REACTIONS[1]
NEXT_PAGE = SCROLL_REACTIONS[2]
DELETE = SCROLL_REACTIONS[4]
CHECK_MARK = SCROLL_REACTIONS[5]
LEAVE = SCROLL_REACTIONS[6]

NUMBER_EMOJIS = [
    "1\u20e3",
    "2\u20e3",
    "3\u20e3",
    "4\u20e3",
    "5\u20e3",
    "6\u20e3",
    "7\u20e3",
    "8\u20e3",
    "9\u20e3",
    '\U0001f51f'
]

LETTER_EMOJIS = [
    "🇦", "🇧", "🇨", "🇩", "🇪",
    "🇫", "🇬", "🇭", "🇮", "🇯",
    "🇰", "🇱", "🇲", "🇳", "🇴",
    "🇵", "🇶", "🇷", "🇸", "🇹",
    "🇺", "🇻", "🇼", "🇽", "🇾",
    "🇿" 
]

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

async def did_author_vote(author_id):

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
        if str(user["id"]) == str(author_id):
            return True
    
    return False