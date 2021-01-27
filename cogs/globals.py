from asyncio import get_event_loop
from datetime import datetime

loop = get_event_loop()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

PRIMARY_EMBED_COLOR = 0xEC7600

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

YES = "✅"
NO = "❌"

JOIN = "🖐️"
PLAY_NOW = "▶"

OMEGA_PSI_CHANNEL = 521186436519821352
OMEGA_PSI_CREATION = datetime(2019, 1, 17, 10, 33, 0)

DBL_BOT_STAT_API_CALL = "https://discordbots.org/api/bots/535587516816949248/stats"
DBL_VOTE_API_CALL = "https://discordbots.org/api/bots/535587516816949248/votes"

MESSAGE_THRESHOLD = 2000
FIELD_THRESHOLD = 1000

SCROLL_REACTIONS = ["⏪", "⬅", "➡", "⏩", "🚫", "✅", "📤", "❌"]
FIRST_PAGE = SCROLL_REACTIONS[0]
LAST_PAGE = SCROLL_REACTIONS[3]
PREVIOUS_PAGE = SCROLL_REACTIONS[1]
NEXT_PAGE = SCROLL_REACTIONS[2]
DELETE = SCROLL_REACTIONS[4]
CHECK_MARK = SCROLL_REACTIONS[5]
OUTBOX = SCROLL_REACTIONS[6]
LEAVE = SCROLL_REACTIONS[7]

VALID_STATUSES = ["offline", "online", "idle", "dnd"]

NUMBER_EMOJIS = [
    "1\u20e3",      # 1
    "2\u20e3",      # 2
    "3\u20e3",      # 3
    "4\u20e3",      # 4
    "5\u20e3",      # 5
    "6\u20e3",      # 6
    "7\u20e3",      # 7
    "8\u20e3",      # 8
    "9\u20e3",      # 9
    '\U0001f51f'    # 10
]

LETTER_EMOJIS = [
    "🇦", "🇧", "🇨", "🇩", "🇪",
    "🇫", "🇬", "🇭", "🇮", "🇯",
    "🇰", "🇱", "🇲", "🇳", "🇴",
    "🇵", "🇶", "🇷", "🇸", "🇹",
    "🇺", "🇻", "🇼", "🇽", "🇾",
    "🇿" 
]

GRADUATION = "🎓"
BRIEFCASE = "💼"
SPIN = "🔄"

BUY_HOUSE = "🏠"
SELL_HOUSE = "💰"
DO_NOTHING = "🤷"
LOANS = "💲"

FAMILY = "👶"
RISKY_ROAD = "⚠"

PAYDAY = "💵"
PAYDAY_BONUS = SELL_HOUSE
GET_MONEY = "📥"
PAY_MONEY = "📤"
PET = "🐶"
ACTION = "❗"
HOUSE = BUY_HOUSE
SPIN_TO_WIN = SPIN
BABY = FAMILY
LOAN = "💳"
SUED = "⚖"
MARRIED = "💍"
RETIRED = "☮"

X_PIECE = "❌"
RED_PIECE = "🔴"
ROBOT = "🤖"
QUIT = "❌"

SMART = ROBOT
RANDOM = "🎲"

MINIGAMES = [
    "battleship", "connect_four", "cards_against_humanity", 
    "game_of_life", "omok", "tic_tac_toe", 
    "uno", "chess", "mastermind", 
    "checkers", "hangman", "black_box"]

CONSIDER = "▶️"
NOT_CONSIDER = "⏹️"