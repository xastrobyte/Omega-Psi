from util.file.database import loop, omegaPsi
from util.file.server import Server
from util.file.omegaPsi import OmegaPsi
from util.file.user import User

from util.game.game import getNoGame, getQuitGame
from util.game import connectFour
from util.game import hangman
from util.game import scramble
from util.game import ticTacToe

from util.game import callOfDuty
from util.game import fortnite
from util.game import league

from util.utils.discordUtils import sendMessage, getErrorMessage

from datetime import datetime
from functools import partial
from random import choice as choose
from supercog import Category, Command
import asyncio, discord, os, requests

scrollEmbeds = {}
reactions = ["⏪", "⬅", "➡", "⏩"]
columns = [
    "1\u20e3",
    "2\u20e3",
    "3\u20e3",
    "4\u20e3",
    "5\u20e3",
    "6\u20e3",
    "7\u20e3",
    "❌"
]
spots = [
    "1\u20e3",
    "2\u20e3",
    "3\u20e3",
    "4\u20e3",
    "5\u20e3",
    "6\u20e3",
    "7\u20e3",
    "8\u20e3",
    "9\u20e3",
    "❌"
]

quitReaction = "❌"

class Game(Category):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # Connect Four URL
    CONNECT_FOUR_ICON = "https://is2-ssl.mzstatic.com/image/thumb/Purple118/v4/aa/e9/96/aae9966e-a95e-65b2-a504-afbb0c9ac51d/source/512x512bb.jpg"

    # Hangman Icon URL
    HANGMAN_ICON = "https://i.ytimg.com/vi/r91yPViqRX0/maxresdefault.jpg"

    # Rock, Paper, Scissors
    RPS_ICON = "https://png.pngtree.com/element_pic/00/16/08/0257a02447ae3eb.jpg"

    # Scramble Icon URL
    SCRAMBLE_ICON = "https://i.ytimg.com/vi/iW1Z0AZvWX8/hqdefault.jpg"

    # Tic Tac Toe URL
    TIC_TAC_TOE_ICON = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Tic_tac_toe.svg/2000px-Tic_tac_toe.svg.png"

    # Game Icon URL's
    SUCCESS_ICON = "https://cdn3.iconfinder.com/data/icons/social-messaging-ui-color-line/254000/172-512.png"
    FAILED_ICON = "https://png.pngtree.com/svg/20161229/fail_17487.png"

    MAX_HANGMAN_GUESSES = 7
    MAX_SCRAMBLE_GUESSES = 10
    MAX_RPS_GAMES = 9

    BLACK_OPS_3_ICON = "https://mbtskoudsalg.com/images/black-ops-3-symbol-png-8.png"
    BLACK_OPS_3_URL = "https://cod-api.tracker.gg/v1/standard/bo3/profile/{}/{}"

    BLACK_OPS_4_ICON = "https://purepng.com/public/uploads/large/call-of-duty-black-ops-4-logo-idp.png"
    BLACK_OPS_4_URL = "https://cod-api.tracker.gg/v1/standard/bo4/profile/{}/{}"
    BLACK_OPS_4_LEVEL = 0

    FORTNITE_URL = "https://api.fortnitetracker.com/v1/profile/{}/{}"
    FORTNITE_ICON = "https://melbournechapter.net/images/meteor-transparent-fortnite-3.png"
    FORTNITE_ITEM_SHOP_URL = "https://api.fortnitetracker.com/v1/store"
    FORTNITE_MATCHES_PLAYED = 7
    FORTNITE_WINS = 8
    FORTNITE_KILLS = 10
    FORTNITE_TOP_10 = 3
    FORTNITE_TOP_25 = 5

    LEAGUE_SUMMONER_URL = "https://na1.api.riotgames.com/lol/summoner/v3/summoners/by-name/{}"
    LEAGUE_MATCHES_URL = "https://na1.api.riotgames.com/lol/match/v3/matchlists/by-account/{}"
    LEAGUE_MATCH_URL = "https://na1.api.riotgames.com/lol/match/v3/matches/{}"
    LEAGUE_VERSIONS = "https://ddragon.leagueoflegends.com/api/versions.json"
    LEAGUE_ICON_URL = "http://ddragon.leagueoflegends.com/cdn/{}/img/profileicon/{}.png"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Errors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    ALREADY_GUESSED = "ALREADY_GUESSED"
    NOT_A_LETTER = "NOT_A_LETTER"
    LETTER_TOO_LONG = "LETTER_TOO_LONG"
    TOO_MANY_GAMES = "TOO_MANY_GAMES"
    COLUMN_FULL = "COLUMN_FULL"
    NO_USER = "NO_USER"
    
    INVALID_PLATFORM = "INVALID_PLATFORM"
    INVALID_DIFFICULTY = "INVALID_DIFFICULTY"
    INVALID_INPUT = "INVALID_INPUT"
    INVALID_SPOT = "INVALID_SPOT"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Constructors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, client):
        super().__init__(
            client, 
            "Game",
            description = "You can play games with these.",
            embed_color = 0xFF8000,
            locally_inactive_error = Server.getInactiveError,
            globally_inactive_error = OmegaPsi.getInactiveError,
            locally_active_check = Server.isCommandActive,
            globally_active_check = OmegaPsi.isCommandActive
        )

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Commands
        self._connectFour = Command(commandDict = {
            "alternatives": ["connectFour", "connect4", "cf"],
            "info": "Play connect four with Omega Psi.",
            "min_parameters": 1,
            "max_parameters": 3,
            "parameters": {
                "difficulty": {
                    "info": "The difficulty of Connect 4 to play.",
                    "optional": True,
                    "accepted_parameters": {
                        "quit": {
                            "alternatives": ["quit", "q", "exit"],
                            "info": "Allows you to quit the Connect 4 game."
                        }
                    }
                }
            },
            "errors": {
                Game.INVALID_SPOT: {
                    "messages": [
                        "That is not within the grid width."
                    ]
                },
                Game.INVALID_DIFFICULTY: {
                    "messages": [
                        "That is not a valid difficulty."
                    ]
                },
                Game.INVALID_INPUT: {
                    "messages": [
                        "The input was invalid."
                    ]
                },
                Game.COLUMN_FULL: {
                    "messages": [
                        "That column is full. You need to go somewhere else."
                    ]
                },
                Game.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "There are too many parameters. If you want to quit a game, use the `quit` parameter."
                    ]
                }
            },
            "command": self.connectFour
        })

        self._hangman = Command(commandDict = {
            "alternatives": ["hangman", "playHangman"],
            "info": "Let's you play hangman!",
            "max_parameters": 1,
            "parameters": {
                "difficulty": {
                    "info": "The difficulty of hangman to play.",
                    "optional": True,
                    "accepted_parameters": {
                        "easy": {
                            "alternatives": ["easy", "simple", "e"],
                            "info": "Play an easy game of Hangman."
                        },
                        "medium": {
                            "alternatives": ["medium", "m"],
                            "info": "Play a medium game of Hangman."
                        },
                        "hard": {
                            "alternatives": ["hard", "difficult", "h"],
                            "info": "Play a hard game of Hangman."
                        },
                        "quit": {
                            "alternatives": ["quit", "q", "exit"],
                            "info": "Allows you to quit the hangman game."
                        }
                    }
                }
            },
            "errors": {
                Game.ALREADY_GUESSED: {
                    "messages": [
                        "You already guessed that letter."
                    ]
                },
                Game.INVALID_DIFFICULTY: {
                    "messages": [
                        "That is not a valid difficulty."
                    ]
                },
                Game.INVALID_INPUT: {
                    "messages": [
                        "The input was invalid."
                    ]
                },
                Game.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to play a game of hangman, you only need the difficulty."
                    ]
                }
            },
            "command": self.hangman
        })

        self._rps = Command(commandDict = {
            "alternatives": ["rockPaperScissors", "rps"],
            "info": "Allows you to play Rock Paper Scissors with me.",
            "min_parameters": 1,
            "parameters": {
                "action": {
                    "info": "What action to start out with. (rock, paper, or scissors).",
                    "optional": False,
                    "accepted_parameters": {
                        "rock": {
                            "alternatives": ["rock", "r"],
                            "info": "Do a rock action."
                        },
                        "paper": {
                            "alternatives": ["paper", "p"],
                            "info": "Do a paper action."
                        },
                        "scissors": {
                            "alternatives": ["scissors", "s"],
                            "info": "Do a scissor action."
                        }
                    }
                }
            },
            "errors": {
                Game.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "You need to type in the action you want to do."
                    ]
                },
                Game.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to play rock, paper, scissors, you only need an amount of games."
                    ]
                },
                Game.INVALID_INPUT: {
                    "messages": [
                        "The input was invalid."
                    ]
                }
            },
            "command": self.rps
        })

        self._scramble = Command(commandDict = {
            "alternatives": ["scramble"],
            "info": "Allows you to guess an unscrambled word.",
            "max_parameters": 1,
            "parameters": {
                "difficulty": {
                    "info": "The difficulty of the game.",
                    "optional": True,
                    "accepted_parameters": {
                        "normal": {
                            "alternatives": ["normal", "n", "easy", "e"],
                            "info": "Only each word is scrambled."
                        },
                        "expert": {
                            "alternatives": ["expert", "hard", "difficult"],
                            "info": "The entire phrase is scrambled."
                        },
                        "quit": {
                            "alternatives": ["quit", "q", "exit"],
                            "info": "Allows you to quit the scramble game."
                        }
                    }
                }
            },
            "errors": {
                Game.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "To guess a scrambled word, you only need the difficulty."
                    ]
                },
                Game.INVALID_DIFFICULTY: {
                    "messages": [
                        "That is not a valid difficulty."
                    ]
                },
                Game.ALREADY_GUESSED: {
                    "messages": [
                        "You already guessed that word."
                    ]
                },
                Game.INVALID_INPUT: {
                    "messages": [
                        "The input was invalid."
                    ]
                }
            },
            "command": self.scramble
        })

        self._ticTacToe = Command(commandDict = {
            "alternatives": ["ticTacToe", "ttt"],
            "info": "Lets you play a Tic-Tac-Toe game against Omega Psi.",
            "max_parameters": 1,
            "parameters": {
                "difficulty": {
                    "info": "The difficulty of the Tic-Tac-Toe game.",
                    "optional": True,
                    "accepted_parameters": {
                        "easy": {
                            "alternatives": ["easy", "simple", "e"],
                            "info": "Play an easy game of Tic-Tac-Toe."
                        },
                        "medium": {
                            "alternatives": ["medium", "m"],
                            "info": "Play a medium game of Tic-Tac-Toe."
                        },
                        "hard": {
                            "alternatives": ["hard", "difficult", "h"],
                            "info": "Play a hard game of Tic-Tac-Toe."
                        },
                        "quit": {
                            "alternatives": ["quit", "q", "exit"],
                            "info": "Quit your game of Tic-Tac-Toe."
                        }
                    }
                }
            },
            "errors": {
                Game.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to play a game of Tic-Tac-Toe, you only need the difficulty."
                    ]
                },
                Game.INVALID_DIFFICULTY: {
                    "messages": [
                        "That is not a valid difficulty."
                    ]
                },
                Game.INVALID_INPUT: {
                    "messages": [
                        "That is not a valid move. A move must be a number between 1 and 9."
                    ]
                },
                Game.ALREADY_GUESSED: {
                    "messages": [
                        "That move was already taken."
                    ]
                }
            },
            "command": self.ticTacToe
        })

        self._stats = Command(commandDict = {
            "alternatives": ["stats", "gameStats"],
            "info": "Gives you stats on the games you've won/lost.",
            "errors": {
                Game.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to check your game stats, you don't need any parameters."
                    ]
                }
            },
            "command": self.stats
        })

        self._addHangman = Command(commandDict = {
            "alternatives": ["addHangman", "hangmanAdd"],
            "info": "Adds a hangman word/phrase to the database.",
            "bot_moderator_only": True,
            "parameters": {
                "difficulty": {
                    "info": "The difficulty of the phrase to add it to.",
                    "optional": False,
                    "accepted": {
                        "easy": {
                            "alternatives": ["easy", "e"],
                            "info": "Add the phrase to the easy difficulty level."
                        },
                        "medium": {
                            "alternatives": ["medium", "m"],
                            "info": "Add the phrase to the medium difficulty level."
                        },
                        "hard": {
                            "alternatives": ["hard", "h"],
                            "info": "Add the phrase to the hard difficulty level."
                        }
                    }
                },
                "phrase": {
                    "info": "The phrase to add to the hangman words.",
                    "optional": False
                }
            },
            "errors": {
                Game.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "To add a word/phrase to hangman, you need the difficulty and the word/phrase."
                    ]
                },
                Game.INVALID_DIFFICULTY: {
                    "messages": [
                        "That is an invalid difficulty."
                    ]
                }
            },
            "command": self.addHangman
        })

        self._addScramble = Command(commandDict = {
            "alternatives": ["addScramble", "scrambleAdd"],
            "info": "Adds a scramble word/phrase to the database.",
            "bot_moderator_only": True,
            "parameters": {
                "hints": {
                    "info": "A list of hints, separated by commas, to add to the word/phrase.",
                    "optional": False
                },
                "phrase": {
                    "info": "The phrase to add",
                    "optional": False
                }
            },
            "errors": {
                Game.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "To add a word/phrase to scramble, you need the difficulty, any hints (separated by commas), and the word/phrase."
                    ]
                },
                Game.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You have too many parameters for this. You just need the difficulty, any hints (separated by commas), and the word/phrase."
                    ]
                }
            },
            "command": self.addScramble
        })

        self._blackOps3 = Command(commandDict = {
            "alternatives": ["blackOps3", "blackops3", "bo3"],
            "info": "Gives you stats on a specific player in Black Ops 3",
            "parameters": {
                "platform": {
                    "info": "The platform to get the stats on.",
                    "optional": False,
                    "accepted_parameters": {
                        "xbox": {
                            "alternatives": ["xbox", "Xbox"],
                            "info": "Get Black Ops 3 stats for Xbox."
                        },
                        "psn": {
                            "alternatives": ["playstation", "psn", "PSN"],
                            "info": "Get Black Ops 3 stats for Playstation Network (PSN)."
                        }
                    }
                },
                "username": {
                    "info": "The username to get the stats for.",
                    "optional": False
                }
            },
            "errors": {
                Game.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to get Black Ops 3 stats, you need the platform and username."
                    ]
                },
                Game.INVALID_PLATFORM: {
                    "messages": [
                        "That is not a valid platform."
                    ]
                },
                Game.NO_USER: {
                    "messages": [
                        "There was no user found with that username."
                    ]
                }
            },
            "command": self.blackOps3
        })

        self._blackOps4 = Command(commandDict = {
            "alternatives": ["blackOps4", "blackops4", "bo4"],
            "info": "Gives you stats on a specific player in Black Ops 4",
            "parameters": {
                "platform": {
                    "info": "The platform to get the stats on.",
                    "optional": False,
                    "accepted_parameters": {
                        "xbox": {
                            "alternatives": ["xbox", "Xbox"],
                            "info": "Get Black Ops 4 stats for Xbox."
                        },
                        "psn": {
                            "alternatives": ["playstation", "psn", "PSN"],
                            "info": "Get Black Ops 4 stats for Playstation Network (PSN)."
                        },
                        "battleNet": {
                            "alternatives": ["battleNet"],
                            "info": "Get Black Ops 4 stats for Battle.net."
                        }
                    }
                },
                "username": {
                    "info": "The username to get the stats for.",
                    "optional": False
                }
            },
            "errors": {
                Game.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to get Black Ops 4 stats, you need the platform and username."
                    ]
                },
                Game.INVALID_PLATFORM: {
                    "messages": [
                        "That is not a valid platform."
                    ]
                },
                Game.NO_USER: {
                    "messages": [
                        "There was no user found with that username."
                    ]
                }
            },
            "command": self.blackOps4
        })

        self._fortnite = Command(commandDict = {
            "alternatives": ["fortnite"],
            "info": "Gives you stats on a specific player in Fortnite.",
            "parameters": {
                "platform": {
                    "info": "The platform to get the stats on.",
                    "optional": False,
                    "accepted_parameters": {
                        "psn": {
                            "alternatives": ["playstation", "psn", "ps"],
                            "info": "Get Fortnite stats for Playstation 4."
                        },
                        "xbox": {
                            "alternatives": ["xbox", "Xbox"],
                            "info": "Get Fortnite stats for Xbox."
                        },
                        "pc": {
                            "alternatives": ["pc", "PC"],
                            "info": "Get Fortnite stats for PC."
                        }
                    }
                },
                "username": {
                    "info": "The username to get the stats for.",
                    "optional": False
                }
            },
            "errors": {
                Game.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to get fortnite stats, you need at least the platform."
                    ]
                },
                Game.INVALID_PLATFORM: {
                    "messages": [
                        "That is not a valid gaming platform that can be tracked."
                    ]
                },
                Game.NO_USER: {
                    "messages": [
                        "There was no user found with that username."
                    ]
                }
            },
            "command": self.fortnite
        })

        self._fortniteItemShop = Command(commandDict = {
            "alternatives": ["fortniteItemShop"],
            "info": "Gives you the current items in the Fortnite Item Shop.",
            "command": self.fortniteItemShop
        })

        self._league = Command(commandDict = {
            "alternatives": ["league", "leagueOfLegends", "LoL"],
            "info": "Gives you stats on a specific Summoner in League of Legends.",
            "parameters": {
                "username": {
                    "info": "The username of the Summoner to look up.",
                    "optional": False
                }
            },
            "errors": {
                Game.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to get the stats for a summoner, you need their username."
                    ]
                },
                Game.NO_USER: {
                    "messages": [
                        "There was no Summoner found with that username."
                    ]
                }
            },
            "command": self.league
        })

        self.setCommands([
            self._connectFour,
            self._hangman,
            self._rps,
            self._scramble,
            self._ticTacToe,
            self._stats,
            self._addHangman,
            self._addScramble,

            self._blackOps3,
            self._blackOps4,
            self._fortnite,
            self._fortniteItemShop,
            self._league
        ])

        self._connectFourGames = {}
        self._hangmanGames = {}
        self._scrambleGames = {}
        self._ticTacToeGames = {}

        self._rpsActions = ["rock", "paper", "scissors"]

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def connectFour(self, message, parameters, *, move = None):
        """Creates a Connect Four game or continues a Connect Four game.

        Parameters:
            discordUser (discord.Member): The Discord User to create a game or continue one.
            difficulty (str): The difficulty of the game to create.
            move (str): What column to drop the game piece in.
        """
        
        # Check if game was started in server
        try:
            serverId = str(message.author.guild.id)
        
        # Game was started in private message
        except:
            serverId = "private"

        authorId = str(message.author.id)

        # Create server connect four instances
        if serverId not in self._connectFourGames:
            self._connectFourGames[serverId] = {}
        
        # Check if move is None; Game is being created or quit
        embed = None
        noError = False
        finishedGame = None
        initialState = move
        if move == None:

            # Check for too many parameters
            if len(parameters) > self._connectFour.getMaxParameters():
                embed = getErrorMessage(self._connectFour, Game.TOO_MANY_PARAMETERS)
            
            # There were the proper amount of parameters
            else:
                difficulty = "easy" if len(parameters) == 0 else parameters[0]

                # Check if user wants to quit
                if difficulty in self._connectFour.getAcceptedParameter("difficulty", "quit").getAlternatives():

                    # Check if user is playing a game
                    if authorId in self._connectFourGames[serverId]:
                        finishedGame = self._connectFourGames[serverId][authorId]
                        noError = True
                        self._connectFourGames[serverId].pop(authorId)
                        embed = getQuitGame("Connect Four", self.getEmbedColor() if message.guild == None else message.author.top_role.color, Game.SUCCESS_ICON)
                    
                    # User was not playing a game
                    else:
                        embed = getNoGame("Connect Four", self.getEmbedColor() if message.guild == None else message.author.top_role.color, Game.FAILED_ICON)
                
                # User does not want to quit
                else:

                    # Create game instance
                    self._connectFourGames[serverId][authorId] = {
                        "game": connectFour.ConnectFour(
                            message.author
                        ),
                        "original_message": message,
                        "message": None
                    }
                    game = self._connectFourGames[serverId][authorId]["game"]

                    embed = discord.Embed(
                        title = "Connect Four",
                        description = "{}\n{}\n{}".format(
                            game.showBoard(),
                            ":large_blue_circle: " + game.getChallenger().mention,
                            ":red_circle: " + "AI" if game.getOpponent() == None else game.getOpponent().mention
                        ),
                        colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                    ).set_thumbnail(
                        url = Game.CONNECT_FOUR_ICON
                    )
                    noError = True
        
        # Check if move is being made
        elif move != None:
            game = self._connectFourGames[serverId][authorId]["game"]

            # Check if move is not number
            try:
                move = int(move)

                # Check if move is not between 1 and width
                if move < 1 or move > game.getWidth():
                    embed = getErrorMessage(self._connectFour, Game.INVALID_SPOT)
                
                # Check if column is full
                elif connectFour.isColumnFull(game.getBoard(), move - 1):
                    embed = getErrorMessage(self._connectFour, Game.COLUMN_FULL)
                
                # Move is valid; Make and process it
                else:
                    # Move is valid; Make it and process it
                    move = game.makeMove(move - 1)
                
                    # Check for no winner
                    if move == None:
                    
                        embed = discord.Embed(
                            title = "Connect Four",
                            description = "{}\n{}\n{}".format(
                                game.showBoard(),
                                ":large_blue_circle: " + game.getChallenger().mention,
                                ":red_circle: " + "AI" if game.getOpponent() == None else game.getOpponent().mention
                            ),
                            colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                        ).set_thumbnail(
                            url = Game.CONNECT_FOUR_ICON
                        )
                        noError = True
                    
                    # Check for a DRAW
                    elif move == connectFour.ConnectFour.DRAW:

                        embed = discord.Embed(
                            title = "Draw",
                            description = "{}\n{}\n{}".format(
                                game.showBoard(),
                                ":large_blue_circle: " + game.getChallenger().mention,
                                ":red_circle: " + "AI" if game.getOpponent() == None else game.getOpponent().mention
                            ),
                            colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                        ).set_thumbnail(
                            url = Game.CONNECT_FOUR_ICON
                        )

                        finishedGame = game

                        self._connectFourGames[serverId].pop(authorId)
                    
                    # Check for challenger / opponent winner
                    else:

                        embed = discord.Embed(
                            title = "{} Won!".format(
                                "Challenger" if move else "Opponent"
                            ),
                            description = "{}\n{}\n{}".format(
                                game.showBoard(),
                                ":large_blue_circle: " + game.getChallenger().mention,
                                ":red_circle: " + "AI" if game.getOpponent() == None else game.opponent().mention
                            ),
                            colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                        ).set_thumbnail(
                            url = Game.SUCCESS_ICON if move else Game.FAILED_ICON
                        )

                        finishedGame = game

                        await User.updateConnectFour(game.getChallenger(), didWin = move)
                        if game.getOpponent() != None:
                            await User.updateConnectFour(game.getOpponent(), didWin = not move)

                        self._connectFourGames[serverId].pop(authorId)

            except:
                embed = getErrorMessage(self._connectFour, Game.INVALID_INPUT)
        
        if initialState == None or finishedGame:
            msg = await sendMessage(
                self.client,
                message,
                embed = embed
            )

        if not finishedGame:
            if noError:
                if initialState != None:
                    await self._connectFourGames[serverId][authorId]["message"].edit(
                        embed = embed
                    )
                else:
                    for reaction in columns:
                        await msg.add_reaction(reaction)
                    self._connectFourGames[serverId][authorId]["message"] = msg

    async def hangman(self, message, parameters, *, guess = None):
        """Creates a hangman game or continues a hangman game.\n

        Parameters:
            discordUser (discord.Member): The Discord User to create a game or continue one.\n
            difficulty (str): The difficulty of the game to create.\n
            guess (chr): The guess that the user made.\n
        """

        # Check if game was started in server
        try:
            serverId = str(message.author.guild.id)
        
        # Game was started in private message
        except:
            serverId = "private"

        authorId = str(message.author.id)

        # Create server hangman instances
        if serverId not in self._hangmanGames:
            self._hangmanGames[serverId] = {}

        # Check if guess is None; Game is being created or quit
        embed = None
        noError = False
        finishedGame = None
        if guess == None:

            # Check for too many parameters
            if len(parameters) > self._hangman.getMaxParameters():
                embed = getErrorMessage(self._hangman, Game.TOO_MANY_PARAMETERS)
            
            # There were the proper amount of parameters
            else:
                difficulty = "easy" if len(parameters) == 0 else parameters[0]

                # Check if user wants to quit
                if difficulty in self._hangman.getAcceptedParameter("difficulty", "quit").getAlternatives():

                    # Check if user is playing a game
                    if authorId in self._hangmanGames[serverId]:
                        finishedGame = self._hangmanGames[serverId][authorId]
                        noError = True
                        self._hangmanGames[serverId].pop(authorId)
                        embed = getQuitGame("Hangman", self.getEmbedColor() if message.guild == None else message.author.top_role.color, Game.SUCCESS_ICON)
                    
                    # User was not playing a game
                    else:
                        embed = getNoGame("Hangman", self.getEmbedColor() if message.guild == None else message.author.top_role.color, Game.FAILED_ICON)
                
                # User does not want to quit
                else:

                    # Make sure difficulty is valid
                    validDifficulty = True
                    difficulty = difficulty if difficulty not in [None, ""] else "easy"
                    if difficulty in self._hangman.getAcceptedParameter("difficulty", "easy").getAlternatives():
                        difficulty = "easy"
                    elif difficulty in self._hangman.getAcceptedParameter("difficulty", "medium").getAlternatives():
                        difficulty = "medium"
                    elif difficulty in self._hangman.getAcceptedParameter("difficulty", "hard").getAlternatives():
                        difficulty = "hard"
                    
                    # Difficulty is invalid
                    else:
                        embed = getErrorMessage(self._hangman, Game.INVALID_DIFFICULTY)
                        validDifficulty = False

                    if validDifficulty:
                    
                        # Create game instance
                        game = hangman.Hangman(message.author, difficulty)
                        await game.generateWord()

                        self._hangmanGames[serverId][authorId] = game
                        game = self._hangmanGames[serverId][authorId]

                        embed = discord.Embed(
                            title = "Hangman",
                            description = "{}\nGuesses: {}".format(
                                game.getHangmanWord(),
                                ", ".join(game.getGuessed()) if len(game.getGuessed()) > 0 else "No Guesses"
                            ),
                            colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                        ).set_thumbnail(
                            url = Game.HANGMAN_ICON
                        ).set_image(
                            url = game.getHangman()
                        )
                        noError = True
        
        # Check if guess is being made
        elif guess != None:
            game = self._hangmanGames[serverId][authorId]
            guess = guess.lower()

            guess = game.makeGuess(guess)

            # Guess was the word
            if guess == hangman.Hangman.WORD:

                embed = discord.Embed(
                    title = "Guessed",
                    description = "You guessed correctly! The word was {}\nIt took you {} guesse{}!".format(
                        game.getWord(),
                        game.getGuesses(),
                        "s" if game.getGuesses() != 1 else ""
                    ),
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                ).set_thumbnail(
                    url = Game.SUCCESS_ICON
                )
                noError = True
                finishedGame = self._hangmanGames[serverId][authorId]

                await User.updateHangman(game.getPlayer(), didWin = True)

                self._hangmanGames[serverId].pop(authorId)
            
            # Guess was a number
            elif guess == hangman.Hangman.NOT_ALPHA:
                embed = getErrorMessage(self._hangman, Game.INVALID_INPUT)
            
            # Guess was already guessed
            elif guess == hangman.Hangman.GUESSED:
                embed = getErrorMessage(self._hangman, Game.ALREADY_GUESSED)
            
            # Guess was a fail
            elif guess == hangman.Hangman.FAILED:
                
                embed = discord.Embed(
                    title = "Game Ended - Word: `{}`".format(game.getWord()),
                    description = "You did not guess the word quick enough.",
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                ).set_thumbnail(
                    url = Game.FAILED_ICON
                ).set_image(
                    url = game.getHangman()
                )

                noError = True
                finishedGame = self._hangmanGames[serverId][authorId]

                await User.updateHangman(game.getPlayer(), didWin = False)

                self._hangmanGames[serverId].pop(authorId)
            
            # Guess was a win
            elif guess == hangman.Hangman.WON:

                embed = discord.Embed(
                    title = "Success!",
                    description = "The word was `{}`\nYou guessed in {} guess{}.".format(
                        game.getWord(), 
                        game.getGuesses(),
                        "es" if game.getGuesses() > 1 else ""
                    ),
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                ).set_thumbnail(
                    url = Game.SUCCESS_ICON
                )

                noError = True
                finishedGame = self._hangmanGames[serverId][authorId]

                await User.updateHangman(game.getPlayer(), didWin = True)

                self._hangmanGames[serverId].pop(authorId)
            
            # Guess was a correct/incorrect letter
            elif guess in [True, False]:

                embed = discord.Embed(
                    title = "Hangman",
                    description = "{}\nGuesses: {}".format(
                        game.getHangmanWord(),
                        ", ".join(game.getGuessed()) if len(game.getGuessed()) > 0 else "No Guesses"
                    ),
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                ).set_thumbnail(
                    url = Game.HANGMAN_ICON
                ).set_image(
                    url = game.getHangman()
                )

                noError = True
        
        msg = await sendMessage(
            self.client,
            message,
            embed = embed
        )

        if not finishedGame:
            if noError:
                if self._hangmanGames[serverId][authorId].getPrevious() != None:
                    await self._hangmanGames[serverId][authorId].getPrevious().delete()
                self._hangmanGames[serverId][authorId].setPrevious(msg)
        else:
            await finishedGame.getPrevious().delete()
    
    async def rps(self, message, parameters):
        """Starts or continues a Rock Paper Scissors game.\n

        Parameters:
            discordUser: The Discord User that played the game.\n
            action: The action the Discord User did.\n
        """

        # Check for not enough parameters
        if len(parameters) < self._rps.getMinParameters():
            embed = getErrorMessage(self._rps, Game.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._rps.getMaxParameters():
            embed = getErrorMessage(self._rps, Game.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            action = parameters[0]

            # Get a random rps action
            botRps = choose(self._rpsActions)

            # Get user's rps action
            validInput = True
            if action in self._rps.getAcceptedParameter("action", "rock").getAlternatives():
                userRps = "rock"
            elif action in self._rps.getAcceptedParameter("action", "paper").getAlternatives():
                userRps = "paper"
            elif action in self._rps.getAcceptedParameter("action", "scissors").getAlternatives():
                userRps = "scissors"
            
            # Action was invalid
            else:
                embed = getErrorMessage(self._rps, Game.INVALID_INPUT)
                validInput = False
            
            if validInput:

                # Check if values are the same
                result = "You had {} and I had {}".format(
                    userRps, botRps
                )
                icon = Game.RPS_ICON
                if botRps == userRps:
                    title = "Tied!"
                    result = "You and I both tied."
                
                elif (
                    (botRps == "rock" and userRps == "paper") or
                    (botRps == "paper" and userRps == "scissors") or
                    (botRps == "scissors" and userRps == "rock")
                ):
                    title = "You Won!"
                    icon = Game.SUCCESS_ICON
                    await User.updateRPS(message.author, didWin = True)

                elif (
                    (botRps == "rock" and userRps == "scissors") or
                    (botRps == "paper" and userRps == "rock") or
                    (botRps == "scissors" and userRps == "paper")
                ):
                    title = "You Lost!"
                    icon = Game.FAILED_ICON
                    await User.updateRPS(message.author, didWin = False)
                
                embed = discord.Embed(
                    title = title,
                    description = result,
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                ).set_thumbnail(
                    url = icon
                )
        
        await sendMessage(
            self.client,
            message,
            embed = embed
        )

    async def scramble(self, message, parameters):
        """Starts or continues a scrambled word game.\n

        Parameters:
            discordUser: The Discord User that started the game.\n
        """

        # Check if game was started in server
        try:
            serverId = str(message.author.guild.id)
        
        # Game was started in private message
        except:
            serverId = "private"

        authorId = str(message.author.id)

        # Add serverId to scramble games if it does not exist
        if serverId not in self._scrambleGames:
            self._scrambleGames[serverId] = {}

        # Check for too many parameters
        if len(parameters) > self._scramble.getMaxParameters():
            embed = getErrorMessage(self._scramble, Game.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            difficulty = "normal" if len(parameters) == 0 else parameters[0]

            # Check if user wants to quit
            if difficulty in self._scramble.getAcceptedParameter("difficulty", "quit").getAlternatives():

                # Check if user is playing a game
                if authorId in self._scrambleGames[serverId]:
                    self._scrambleGames[serverId].pop(authorId)
                    embed = getQuitGame("Scramble", self.getEmbedColor() if message.guild == None else message.author.top_role.color, Game.SUCCESS_ICON)

                # User was not playing a game
                else:
                    embed = getNoGame("Scramble", self.getEmbedColor() if message.guild == None else message.author.top_role.color, Game.FAILED_ICON)
            
            # User does not want to quit
            else:
            
                # Make sure difficulty is valid
                validDifficulty = True
                difficulty = difficulty if difficulty not in [None, ""] else "normal"
                if difficulty in self._scramble.getAcceptedParameter("difficulty", "normal").getAlternatives():
                    difficulty = "normal"
                elif difficulty in self._scramble.getAcceptedParameter("difficulty", "expert").getAlternatives():
                    difficulty = "expert"
                
                # Difficult is invalid
                else:
                    embed = getErrorMessage(self._hangman, Game.INVALID_DIFFICULTY)
                    validDifficulty = False
                
                if validDifficulty:

                    # Create game
                    game = scramble.Scramble(message.author, difficulty)
                    await game.generateWord()

                    self._scrambleGames[serverId][authorId] = game
                    game = self._scrambleGames[serverId][authorId]

                    # Return embed
                    embed = discord.Embed(
                        title = "Scrambled",
                        description = "Unscramble this word/phrase. You have 15 seconds. Good luck.\n`{}`".format(
                            game.getScrambledWord()
                        ),
                        colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                    ).set_thumbnail(
                        url = Game.SCRAMBLE_ICON
                    ).add_field(
                        name = "Hint",
                        value = game.getHint()
                    )

                    await sendMessage(
                        self.client,
                        message,
                        embed = embed
                    )

                    # Wait for guess
                    try:
                        guess = await self.client.wait_for("message", timeout = 15, check = self.isAuthorPlayer)
                        guess = guess.content.lower()

                        # Check if it's right
                        if len(guess) > 1:

                            guess = game.makeGuess(guess)

                            embed = discord.Embed(
                                title = "Success" if guess else "Failed",
                                description = "{} `{}`.".format(
                                    "You guessed the word correctly! It was" if guess else "Unfortunately, you did not guess the word.\nThe word was",
                                    game.getWord()
                                ),
                                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                            ).set_thumbnail(
                                url = Game.SUCCESS_ICON if guess else Game.FAILED_ICON
                            )

                            await User.updateScramble(game.getPlayer(), didWin = guess)

                            self._scrambleGames[serverId].pop(authorId)
                        
                    except asyncio.TimeoutError:

                        embed = discord.Embed(
                            title = "Timed Out",
                            description = "Unfortunately, you did not guess the word in time.\nThe word was `{}`".format(
                                game.getWord()
                            ),
                            colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                        ).set_thumbnail(
                            url = Game.FAILED_ICON
                        )

                        await User.updateScramble(game.getPlayer(), didWin = False)

                        self._scrambleGames[serverId].pop(authorId)
                        
                    await sendMessage(
                        self.client,
                        message,
                        embed = embed
                    )
                
    async def ticTacToe(self, message, parameters, *, move = None):
        """Creates a Tic Tac Toe game or continues a Tic Tac Toe game.

        Parameters:
            discordUser (discord.Member): The Discord User to create a game or continue one.
            difficulty (str): The difficulty of the game to create.
            move (str): What spot to make the move at.
        """
        
        # Check if game was started in server
        try:
            serverId = str(message.author.guild.id)
        
        # Game was started in private message
        except:
            serverId = "private"

        authorId = str(message.author.id)

        # Add serverId to Tic Tac Toe games if it does not exist
        if serverId not in self._ticTacToeGames:
            self._ticTacToeGames[serverId] = {}
        
        # Check if move is None; Game is being created or quit
        embed = None
        noError = False
        finishedGame = None
        initialState = move
        if move == None:

            # Check for too many parameters
            if len(parameters) > self._ticTacToe.getMaxParameters():
                embed = getErrorMessage(self._ticTacToe, Game.TOO_MANY_PARAMETERS)
            
            # There were the proper amount of parameters
            else:
                difficulty = "easy" if len(parameters) == 0 else parameters[0]

                # Check if user wants to quit
                if difficulty in self._ticTacToe.getAcceptedParameter("difficulty", "quit").getAlternatives():

                    # Check if user is playing game
                    if authorId in self._ticTacToeGames[serverId]:
                        finishedGame = self._ticTacToeGames[serverId][authorId]
                        noError = True
                        self._ticTacToeGames[serverId].pop(authorId)
                        embed = getQuitGame("Tic Tac Toe", self.getEmbedColor() if message.guild == None else message.author.top_role.color, Game.SUCCESS_ICON)
                    
                    # User was not playing a game
                    else:
                        embed = getNoGame("Tic Tac Toe", self.getEmbedColor() if message.guild == None else message.author.top_role.color, Game.FAILED_ICON)
                
                # User does not want to quit
                else:

                    # Create game
                    self._ticTacToeGames[serverId][authorId] = {
                        "game": ticTacToe.TicTacToe(
                            difficulty if difficulty not in [None, ""] else "easy",
                            message.author
                        ),
                        "original_message": message,
                        "message": None
                    }

                    game = self._ticTacToeGames[serverId][authorId]["game"]

                    embed = discord.Embed(
                        title = "Tic Tac Toe",
                        description = "{}\n{}\n{}".format(
                                game.showBoard(),
                                ":x: " + game.getChallenger().mention,
                                ":o: " + "AI" if game.getOpponent() == None else game.getOpponent().mention
                            ),
                        colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                    ).set_thumbnail(
                        url = Game.TIC_TAC_TOE_ICON
                    )
                    noError = True
        
        # There was a move; See what move it was
        elif move != None:
            game = self._ticTacToeGames[serverId][authorId]["game"]

            # Check if move is not number
            try:
                move = int(move)

                 # Check if move is not between 1 and 9
                if move < 1 or move > 9:
                    embed = getErrorMessage(self._ticTacToe, Game.INVALID_INPUT)
                
                # Check if move is already been done
                elif game.getBoard()[move - 1] != None:
                    embed = getErrorMessage(self._ticTacToe, Game.ALREADY_GUESSED)
                
                # Move is valid
                else:
                    moveCheck = game.makeMove(move -1)

                    # The game was a draw
                    if moveCheck == ticTacToe.TicTacToe.DRAW:

                        embed = discord.Embed(
                            title = "Draw",
                            description = "The game was a draw.\n{}\n{}\n{}".format(
                                game.showBoard(),
                                ":x: " + game.getChallenger().mention,
                                ":o: " + "AI" if game.getOpponent() == None else game.getOpponent().mention
                            ),
                            colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                        ).set_thumbnail(
                            url = Game.TIC_TAC_TOE_ICON
                        )
                        noError = True
                        finishedGame = self._ticTacToeGames[serverId][authorId]

                        self._ticTacToeGames[serverId].pop(authorId)
                    
                    # There is no winner yet
                    elif moveCheck == None:

                        embed = discord.Embed(
                            title = "Tic Tac Toe",
                            description = "{}\n{}\n{}".format(
                                game.showBoard(),
                                ":x: " + game.getChallenger().mention,
                                ":o: " + "AI" if game.getOpponent() == None else game.getOpponent().mention
                            ),
                            colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                        ).set_thumbnail(
                            url = Game.TIC_TAC_TOE_ICON
                        )
                        noError = True

                    # The challenger or opponent won
                    else:

                        # Setup embed
                        embed = discord.Embed(
                            title = "{} Won".format(
                                "Challenger" if moveCheck else "Opponent"
                            ),
                            description = "{} wins the game.\n{}\n{}\n{}".format(
                                (
                                    game.getChallenger().mention
                                ) if moveCheck else (
                                    "AI" if game.getOpponent() == None else game.getOpponent().mention
                                ),
                                game.showBoard(),
                                ":x: " + game.getChallenger().mention,
                                ":o: " + "AI" if game.getOpponent() == None else game.getOpponent().mention
                            ),
                            colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
                        ).set_thumbnail(
                            url = Game.TIC_TAC_TOE_ICON
                        )
                        noError = True
                        finishedGame = self._ticTacToeGames[serverId][authorId]

                        # Update scores
                        await User.updateTicTacToe(game.getChallenger(), didWin = moveCheck)
                        if game.getOpponent() != None:
                            await User.updateTicTacToe(game.getOpponent(), didWin = not moveCheck)

                        # Remove game instance
                        self._ticTacToeGames[serverId].pop(authorId)

            except:
                embed = getErrorMessage(self._ticTacToe, Game.INVALID_INPUT)
        
        if initialState == None or finishedGame or not noError:
            msg = await sendMessage(
                self.client,
                message,
                embed = embed
            )

        if not finishedGame:
            if noError:
                if initialState != None:
                    await self._ticTacToeGames[serverId][authorId]["message"].edit(
                        embed = embed
                    )
                else:
                    for reaction in spots:
                        await msg.add_reaction(reaction)
                    self._ticTacToeGames[serverId][authorId]["message"] = msg
    
    async def stats(self, message, parameters):
        """Shows the stats for the specified Discord User.\n

        Parameters:
            discordUser: The Discord User to get the stats of.\n
        """

        # Check for too many parameters
        if len(parameters) > self._stats.getMaxParameters():
            embed = getErrorMessage(self._stats, Game.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Open user file
            user = await User.openUser(message.author)

            # Get game stats
            games = {
                ":red_circle: Connect Four": user["connect_four"].copy(),
                ":skull_crossbones: Hangman": user["hangman"].copy(),
                ":scissors: Rock Paper Scissors": user["rps"].copy(),
                ":cyclone: Scramble": user["scramble"].copy(),
                ":x: Tic Tac Toe": user["tic_tac_toe"].copy()
            }

            # Close user file
            await User.closeUser(user)

            embed = discord.Embed(
                title = "Stats",
                description = "Game Stats for {}".format(message.author.mention),
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            )

            # Add each game
            for game in games:

                # Get won / lost ratio
                if games[game]["won"] == 0 and games[game]["lost"] == 0:
                    winLostRatio = 0
                elif games[game]["lost"] == 0:
                    winLostRatio = round(games[game]["won"], 2)
                else:
                    winLostRatio = round(games[game]["won"] / games[game]["lost"], 2)

                embed.add_field(
                    name = game + " ({})".format(
                        winLostRatio
                    ),
                    value = "Won: {}\nLost: {}\n".format(
                        games[game]["won"],
                        games[game]["lost"]
                    )
                )
            
        await sendMessage(
            self.client,
            message,
            embed = embed
        )
    
    async def addHangman(self, message, parameters):
        """Adds a word/phrase to Hangman
        """

        # Check for not enough parameters
        if len(parameters) < self._addHangman.getMinParameters():
            embed = getErrorMessage(self._addHangman, Game.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            difficulty = parameters[0]
            phrase = " ".join(parameters[1:])

            # Make sure difficulty is valid
            validDifficulty = False
            for accepted in self._addHangman.getAcceptedParameters("difficulty"):
                if difficulty in self._addHangman.getAcceptedParameter("difficulty", accepted).getAlternatives():
                    difficulty = accepted
                    validDifficulty = True
                    break
            
            # Difficulty was valid
            if validDifficulty:
                omegaPsi.addHangman(difficulty, phrase)

                embed = discord.Embed(
                    title = "Hangman Phrase Added",
                    description = "**Phrase: {}**\n**Difficulty: {}**\n".format(
                        phrase, difficulty
                    ),
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color if message.guild == None else message.author.top_role.color
                )
            
            # Difficulty was not valid
            else:
                embed = getErrorMessage(self._addHangman, Game.INVALID_DIFFICULTY)
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def addScramble(self, message, parameters):
        """Adds a word/phrase to Scramble
        """

        # Check for not enough parameters
        if len(parameters) < self._addScramble.getMinParameters():
            embed = getErrorMessage(self._addScramble, Game.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._addScramble.getMaxParameters():
            embed = getErrorMessage(self._addScramble, Game.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            hints = parameters[0].split(",")
            phrase = parameters[1]
            
            omegaPsi.addScramble(hints, phrase)

            embed = discord.Embed(
                title = "Scramble Phrase Added",
                description = "**Phrase: {}**\n**Hints: {}**\n".format(
                    phrase, ", ".join(hints)
                ),
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color if message.guild == None else message.author.top_role.color
            )
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def blackOps3(self, message, parameters):
        """Gets the Black Ops 3 stats for a user on a platform.

        Parameters:
            platform (str): The platform to get the stats on.
            username (str): The user to get the stats for.
        """

        # Check for not enough parameters
        if len(parameters) < self._blackOps3.getMinParameters():
            embed = getErrorMessage(self._blackOps3, Game.NOT_ENOUGH_PARAMETERS)
        
        # There were enough parameters
        else:
            platform = parameters[0]
            username = " ".join(parameters[1:])

            # Make sure platform is valid
            validPlatform = True
            if platform in self._blackOps3.getAcceptedParameter("platform", "xbox").getAlternatives():
                platform = 1
            elif platform in self._blackOps3.getAcceptedParameter("platform", "psn").getAlternatives():
                platform = 2
            
            # Platform is not valid
            else:
                embed = getErrorMessage(self._blackOps3, Game.INVALID_PLATFORM)
                validPlatform = False
            
            if validPlatform:

                # Request data
                blackOps3Json = await loop.run_in_executor(None,
                    partial(
                        requests.get,
                        Game.BLACK_OPS_3_URL.format(platform, username),
                        headers = {
                            "TRN-Api-Key": os.environ["BLACK_OPS_API_KEY"]
                        }
                    )
                )
                blackOps3Json = blackOps3Json.json()

                # See if an error was given
                if "errors" in blackOps3Json:
                    embed = getErrorMessage(self._blackOps3, Game.NO_USER)
                
                # There was no error given
                else:
                
                    # Get stats and put inside Embed
                    embed = discord.Embed(
                        title = "Black Ops 3 Stats",
                        description = "{} - {}".format(
                            blackOps3Json["data"]["metadata"]["platformUserHandle"],
                            "Xbox" if blackOps3Json["data"]["metadata"]["platformId"] == 1 else "PSN"
                        ),
                        colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color,
                        timestamp = datetime.now()
                    ).set_author(
                        name = blackOps3Json["data"]["metadata"]["platformUserHandle"],
                        icon_url = Game.BLACK_OPS_3_ICON
                    ).set_footer(
                        text = "Black Ops 3 Tracker"
                    )

                    # Add stats using Black Ops 3 parser
                    embed = callOfDuty.getGameStats(embed, blackOps3Json)
        
        await sendMessage(
            self.client,
            message,
            embed = embed
        )
        
    async def blackOps4(self, message, parameters):
        """Gets the Black Ops 4 stats for a user on a platform.

        Parameters:
            platform (str): The platform to get the stats on.
            username (str): The user to get the stats for.
        """

        # Check for not enough parameters
        if len(parameters) < self._blackOps4.getMinParameters():
            embed = getErrorMessage(self._blackOps4, Game.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            platform = parameters[0]
            username = " ".join(parameters[1:])

            # Make sure platform is valid
            validPlatform = True
            if platform in self._blackOps4.getAcceptedParameter("platform", "xbox").getAlternatives():
                platform = 1
            elif platform in self._blackOps4.getAcceptedParameter("platform", "psn").getAlternatives():
                platform = 2
            elif platform in self._blackOps4.getAcceptedParameter("platform", "battleNet").getAlternatives():
                platform = 6
            
            # Platform is not valid
            else:
                embed = getErrorMessage(self._blackOps4, Game.INVALID_PLATFORM)
                validPlatform = False
            
            if validPlatform:
            
                # Request data
                blackOps4Json = await loop.run_in_executor(None,
                    partial(
                        requests.get,
                        Game.BLACK_OPS_4_URL.format(platform, username),
                        headers = {
                            "TRN-Api-Key": os.environ["BLACK_OPS_API_KEY"]
                        }
                    )
                )
                blackOps4Json = blackOps4Json.json()

                # See if an error was given
                if "errors" in blackOps4Json:
                    embed = getErrorMessage(self._blackOps4, Game.NO_USER)
                
                # There was no error given
                else:
                
                    # Get stats and put inside Embed; Use Level icon for author icon
                    try:
                        levelIcon = blackOps4Json["data"]["stats"][Game.BLACK_OPS_4_LEVEL]["metadata"]["iconUrl"]
                    except:
                        levelIcon = Game.BLACK_OPS_4_ICON

                    embed = discord.Embed(
                        title = "Black Ops 4 Stats",
                        description = "{} - {}".format(
                            blackOps4Json["data"]["metadata"]["platformUserHandle"],
                            "Xbox" if blackOps4Json["data"]["metadata"]["platformId"] == 1 else "PSN"
                        ),
                        colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color,
                        timestamp = datetime.now()
                    ).set_author(
                        name = blackOps4Json["data"]["metadata"]["platformUserHandle"],
                        icon_url = levelIcon
                    ).set_footer(
                        text = "Black Ops 4 Tracker"
                    )

                    # Add stats using Black Ops 4 parser
                    embed = callOfDuty.getGameStats(embed, blackOps4Json)

        await sendMessage(
            self.client,
            message,
            embed = embed
        )
        
    async def fortnite(self, message, parameters):
        """Gets the Fortnite stats for a user on a platform.

        Parameters:
            platform (str): The platform to get the stats on.
            username (str): The user to get the stats for.
        """

        # Check for not enough parameters
        if len(parameters) < self._fortnite.getMinParameters():
            embed = getErrorMessage(self._fortnite, Game.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            platform = parameters[0]
            username = " ".join(parameters[1:])

            # Make sure platform is valid
            validPlatform = True
            if platform in self._fortnite.getAcceptedParameter("platform", "pc").getAlternatives():
                platform = "pc"
            elif platform in self._fortnite.getAcceptedParameter("platform", "xbox").getAlternatives():
                platform = "xbox"
            elif platform in self._fortnite.getAcceptedParameter("platform", "psn").getAlternatives():
                platform = "psn"
            
            # Platform is not valid
            else:
                embed = getErrorMessage(self._fortnite, Game.INVALID_PLATFORM)
                validPlatform = False
            
            if validPlatform:

                # Request data
                fortniteJson = await loop.run_in_executor(None,
                    partial(
                        requests.get,
                        Game.FORTNITE_URL.format(platform, username),
                        headers = {
                            "TRN-Api-Key": os.environ["FORTNITE_API_KEY"]
                        }
                    )
                )
                fortniteJson = fortniteJson.json()

                # See if an error was given.
                if "error" in fortniteJson:
                    embed = getErrorMessage(self._fortnite, Game.NO_USER)
                
                else:
                
                    # There was no error given; Get Solo, Duo, and Squad information
                    # Attempt to get each section of information; If no data for section
                    # Don't use it, set it to None
                    try:
                        solo = fortniteJson["stats"]["p2"]
                    except:
                        solo = None
                    try:
                        duo = fortniteJson["stats"]["p10"]
                    except:
                        duo = None
                    try:
                        squads = fortniteJson["stats"]["p9"]
                    except:
                        squads = None

                    try:
                        seasonSolo = fortniteJson["stats"]["curr_p2"]
                    except:
                        seasonSolo = None
                    try:
                        seasonDuo = fortniteJson["stats"]["curr_p10"]
                    except:
                        seasonDuo = None
                    try:
                        seasonSquads = fortniteJson["stats"]["curr_p9"]
                    except:
                        seasonSquads = None

                    gameTypeStats = [
                        solo, duo, squads,
                        seasonSolo, seasonDuo, seasonSquads
                    ]
                    gameTypes = [
                        "p2", "p10", "p9",
                        "curr_p2", "curr_p10", "curr_p9"
                    ]

                    lifetime = fortniteJson["lifeTimeStats"]

                    # Create embed
                    embed = discord.Embed(
                        title = "Fortnite Stats",
                        description = fortniteJson["epicUserHandle"] + " - " + fortniteJson["platformNameLong"],
                        colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color,
                        timestamp = datetime.now()
                    ).set_author(
                        name = fortniteJson["epicUserHandle"],
                        icon_url = Game.FORTNITE_ICON
                    ).set_footer(
                        text = "Fortnite Tracker"
                    )

                    for gameType in range(len(gameTypeStats)):
                        embed = fortnite.addGameType(embed, gameTypeStats[gameType], gameTypes[gameType])
                    
                    # Add lifetime stats
                    embed.add_field(
                        name = "Lifetime Stats",
                        value = "{}\n{}\n{}\n{}\n{}\n".format(
                            "**Matches Played**: " + lifetime[Game.FORTNITE_MATCHES_PLAYED]["value"],
                            "**Wins**: " + lifetime[Game.FORTNITE_WINS]["value"],
                            "**Kills**: " + lifetime[Game.FORTNITE_KILLS]["value"],
                            "**Top 10**: " + lifetime[Game.FORTNITE_TOP_10]["value"],
                            "**Top 25**: " + lifetime[Game.FORTNITE_TOP_25]["value"]
                        ),
                        inline = False
                    )
        
        await sendMessage(
            self.client,
            message,
            embed = embed
        )
    
    async def fortniteItemShop(self, message, parameters):
        """Gets the current Fortnite Item shop.
        """

        # Check for too many parameters
        if len(parameters) > self._fortniteItemShop.getMaxParameters():
            embed = getErrorMessage(self._fortniteItemShop, Game.TOO_MANY_PARAMETERS)
        
            await sendMessage(
                self.client,
                message,
                embed = embed.set_footer(
                    text = "Requested by {}#{}".format(
                        message.author.name,
                        message.author.discriminator
                    ),
                    icon_url = message.author.avatar_url
                )
            )

        else:

            # Request data
            fortniteItems = await loop.run_in_executor(None,
                partial(
                    requests.get,
                    Game.FORTNITE_ITEM_SHOP_URL,
                    headers = {
                        "TRN-Api-Key": os.environ["FORTNITE_API_KEY"]
                    }
                )
            )
            fortniteItems = fortniteItems.json()

            # Create file
            result = await loop.run_in_executor(None,
                fortnite.getItemShopImage,
                fortniteItems
            )

            # Send file then delete
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def league(self, message, parameters):
        """Gets the League of Legends stats for a Summoner.

        Parameters:
            username (str): The username of the Summoner to get stats for.
        """

        # Check for not enough parameters
        if len(parameters) < self._league.getMinParameters():
            embed = getErrorMessage(self._league, Game.NOT_ENOUGH_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Get username
            username = " ".join(parameters)

            # Get most recent version (used for profile icon)
            versionsJson = await loop.run_in_executor(None,
                requests.get,
                Game.LEAGUE_VERSIONS
            )
            version = versionsJson.json()[0]
            
            # Request the user data
            leagueJson = await loop.run_in_executor(None,
                partial(
                    requests.get,
                    Game.LEAGUE_SUMMONER_URL.format(username),
                    headers = {
                        "X-Riot-Token": os.environ["LEAGUE_API_KEY"]
                    }
                )
            )
            leagueJson = leagueJson.json()

            # Request the matches data
            leagueMatchesJson = await loop.run_in_executor(None,
                partial(
                    requests.get,
                    Game.LEAGUE_MATCHES_URL.format(leagueJson["accountId"]),
                    headers = {
                        "X-Riot-Token": os.environ["LEAGUE_API_KEY"]
                    }
                )
            )
            leagueMatchesJson = leagueMatchesJson.json()

            # Request the first 20 matches data
            matches = []
            count = 0
            for match in leagueMatchesJson["matches"]:
                count += 1
                
                # Request the match data
                leagueMatchJson = await loop.run_in_executor(None,
                    partial(
                        requests.get,
                        Game.LEAGUE_MATCH_URL.format(match["gameId"]),
                        headers = {
                            "X-Riot-Token": os.environ["LEAGUE_API_KEY"]
                        }
                    )
                )
                leagueMatchJson = leagueMatchJson.json()

                matches.append(leagueMatchJson)

                if count >= 10:
                    break
            
            # Create scrollable embeds
            scroll = {
                "embeds": [],
                "value": 0
            }
            count = 0
            for match in matches:
                count += 1

                # Setup embed
                embed = discord.Embed(
                    title = "League of Legends Stats",
                    description = "({} / 10) Most Recent Game for **{}**".format(count, leagueJson["name"]),
                    colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color,
                    timestamp = datetime.now()
                ).set_author(
                    name = leagueJson["name"],
                    icon_url = Game.LEAGUE_ICON_URL.format(version, leagueJson["profileIconId"])
                ).set_footer(
                    text = "Riot Games API"
                )

                embed = league.getMatchStats(embed, match, leagueJson["accountId"])

                scroll["embeds"].append(embed)
            
            scrollEmbeds[str(message.author.id)] = scroll
            embed = scroll["embeds"][0]
            
        msg = await sendMessage(
            self.client,
            message,
            embed = embed
        )

        for reaction in reactions:
            await msg.add_reaction(reaction)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Helper Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def isPlayerInGame(self, gameDict, author, server = None):
        """Returns whether or not a player is in a game dictionary.\n

        Parameters:
            gameDict (dict): The game dictionary to look in.\n
            author (discord.User): The player.\n
            server (discord.Server): The server. Defaults to \"private\".\n
        """

        # Get server and author ID's
        if server == None:
            serverId = "private"
        else:
            serverId = str(server.id)
        
        authorId = str(author.id)

        # Test if serverId is in gameDict
        if serverId in gameDict:

            # Test if authorId is in server's gameDict
            if authorId in gameDict[serverId]:
                return True
        
        # Author or Server is not in gameDict
        return False
    
    def isAuthorPlayer(self, message):
        return self.isPlayerInGame(self._scrambleGames, message.author, message.guild)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Parsing
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def on_message(self, message):
        """Parses a message and runs a Game Category command if it can.\n

        Parameters:
            message (discord.Message): The Discord Message to parse.\n
        """

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Check Commands First
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Make sure message starts with the prefix
        if await Server.startsWithPrefix(message.guild, message.content) and not message.author.bot:

            # Split up into command and parameters if possible
            command, parameters = Category.parseText(await Server.getPrefixes(message.guild), message.content)
            
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            # Iterate through commands
            for cmd in self.getCommands():
                if command in cmd.getAlternatives():
                    async with message.channel.typing():

                        # Run the command but don't try running others
                        await self.run(message, cmd, cmd.getCommand(), message, parameters)
                    break
        
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Check Running Games
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Only run games if prefix is not found
        elif not (await Server.startsWithPrefix(message.guild, message.content)):

            # Hangman
            if self.isPlayerInGame(self._hangmanGames, message.author, message.guild):
                await self.hangman(message, [], guess = message.content)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Reactions
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def on_reaction_add(self, reaction, member):
        """Determines which reaction was added to a message. Only reactions right now are

        :arrow_left: which tells the embed to scroll back a field.
        :arrow_right: which tells the embed to scroll forward a field.
        :rewind: which tells the embed to go back to the beginning.
        :fast_forward: which tells the embed to go to the end.
        """
        await self.manage_scrolling(reaction, member)
        await self.manage_games(reaction, member)
        
    
    async def on_reaction_remove(self, reaction, member):
        """Determines which reaction was removed from a message. Only reactions right now are

        :arrow_left: which tells the embed to scroll back a field.
        :arrow_right: which tells the embed to scroll forward a field.
        :rewind: which tells the embed to go back to the beginning.
        :fast_forward: which tells the embed to go to the end.
        """
        await self.manage_scrolling(reaction, member)
        await self.manage_games(reaction, member)

    async def manage_scrolling(self, reaction, member):
        """Manages any scrolling embeds that exist
        """

        # See if the member has a scrolling embed in the list
        if str(member.id) in scrollEmbeds:
            initial = scrollEmbeds[str(member.id)]["value"]

            # User wants to go to the beginning
            if str(reaction) == "⏪":
                scrollEmbeds[str(member.id)]["value"] = 0

            # User wants to go to the end
            elif str(reaction) == "⏩":
                scrollEmbeds[str(member.id)]["value"] = len(scrollEmbeds[str(member.id)]["embeds"]) - 1

            # User wants to go left
            elif str(reaction) == "⬅":
                scrollEmbeds[str(member.id)]["value"] -= 1
                if scrollEmbeds[str(member.id)]["value"] < 0:
                    scrollEmbeds[str(member.id)]["value"] = 0

            # User wants to go right
            elif str(reaction) == "➡":
                scrollEmbeds[str(member.id)]["value"] += 1
                if scrollEmbeds[str(member.id)]["value"] > len(scrollEmbeds[str(member.id)]["embeds"]) - 1:
                    scrollEmbeds[str(member.id)]["value"] = len(scrollEmbeds[str(member.id)]["embeds"]) - 1

            # Update the embed if necessary
            if scrollEmbeds[str(member.id)]["value"] != initial:
                value = scrollEmbeds[str(member.id)]["value"]

                await reaction.message.edit(
                    embed = scrollEmbeds[str(member.id)]["embeds"][value]
                )
    
    async def manage_games(self, reaction, member):
        """Manages any games that are being played
        """

        try:
            guild = member.guild
            serverId = str(guild.id)
        except:
            guild = None
            serverId = "private"
        
        authorId = str(member.id)

        # See if the member is playing a Connect four game
        if self.isPlayerInGame(self._connectFourGames, member, guild):
            origMessage = self._connectFourGames[serverId][authorId]["original_message"]
            message = self._connectFourGames[serverId][authorId]["message"]

            # Make sure the reactor is the author of the original message
            # We don't want other people overriding the message

            # Also make sure that the message is the same as the sent message
            if origMessage.author.id == member.id and reaction.message.id == message.id:
                if str(reaction) in columns and str(reaction) != quitReaction:
                    move = columns.index(str(reaction)) + 1
                    await self.connectFour(
                        self._connectFourGames[serverId][authorId]["original_message"],
                        [],
                        move = str(move)
                    )
                
                if str(reaction) == quitReaction:
                    await self.connectFour(
                        self._connectFourGames[serverId][authorId]["original_message"],
                        ["quit"]
                    )
        
        # See if member is playing a Tic Tac Toe game
        if self.isPlayerInGame(self._ticTacToeGames, member, guild):
            origMessage = self._ticTacToeGames[serverId][authorId]["original_message"]
            message = self._ticTacToeGames[serverId][authorId]["message"]

            # Make sure the reactor is the author of the original message
            # We don't want other people overriding the message

            # Also make sure that the message is the same as the sent message
            if origMessage.author.id == member.id and reaction.message.id == message.id:
                if str(reaction) in spots and str(reaction) != quitReaction:
                    move = spots.index(str(reaction)) + 1
                    await self.ticTacToe(
                        self._ticTacToeGames[serverId][authorId]["original_message"],
                        [],
                        move = str(move)
                    )
                
                if str(reaction) == quitReaction:
                    await self.ticTacToe(
                        self._ticTacToeGames[serverId][authorId]["original_message"],
                        ["quit"]
                    )

def setup(client):
    client.add_cog(Game(client))