from util.file.server import Server
from util.file.omegaPsi import OmegaPsi
from util.file.user import User

from util.game.game import getNoGame, getQuitGame
from util.game import connectFour
from util.game import hangman
from util.game import scramble
from util.game import ticTacToe

from util.game import blackOps3
from util.game import blackOps4
from util.game import fortnite

from util.utils import sendMessage, getErrorMessage, run

from datetime import datetime
from random import choice as choose
from supercog import Category, Command
import discord, os, requests

class Game(Category):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    EMBED_COLOR = 0xFF8000

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
    # Other Fields
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
    FORTNITE_ICON = "https://d1u5p3l4wpay3k.cloudfront.net/fortnite_gamepedia/6/64/Favicon.ico"
    FORTNITE_ITEM_SHOP_URL = "https://api.fortnitetracker.com/v1/store"
    FORTNITE_MATCHES_PLAYED = 7
    FORTNITE_WINS = 8
    FORTNITE_KILLS = 10
    FORTNITE_TOP_10 = 3
    FORTNITE_TOP_25 = 5

    LEAGUE_URL = ""
    LEAGUE_ICON = ""

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Constructors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, client):
        super().__init__(
            client, 
            "Game",
            description = "You can play games with these.",
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
            }
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
            }
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
            }
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
            }
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
            }
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
            }
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
            }
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
            }
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
            }
        })

        self._fortniteItemShop = Command(commandDict = {
            "alternatives": ["fortniteItemShop"],
            "info": "Gives you the current items in the Fortnite Item Shop."
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
            }
        })

        self.setCommands([
            self._connectFour,
            self._hangman,
            self._rps,
            self._scramble,
            self._ticTacToe,
            self._stats,

            self._blackOps3,
            self._blackOps4,
            self._fortnite,
            self._fortniteItemShop
        ])

        self._connectFourGames = {}
        self._hangmanGames = {}
        self._scrambleGames = {}
        self._ticTacToeGames = {}

        self._rpsActions = ["rock", "paper", "scissors"]

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def connectFour(self, discordUser, *, difficulty, move = None):
        """Creates a Connect Four game or continues a Connect Four game.

        Parameters:
            discordUser (discord.Member): The Discord User to create a game or continue one.
            difficulty (str): The difficulty of the game to create.
            move (str): What column to drop the game piece in.
        """
        
        # Check if game was started in server
        try:
            serverId = str(discordUser.guild.id)
        
        # Game was started in private message
        except:
            serverId = "private"

        authorId = str(discordUser.id)

        # Create server connect four instances
        if serverId not in self._connectFourGames:
            self._connectFourGames[serverId] = {}
        
        # Check if new game is being created
        if difficulty != None:

            # Check if user wants to quit
            if difficulty in self._connectFour.getAcceptedParameter("difficulty", "quit").getAlternatives():

                # Check if user is playing a game
                if authorId in self._connectFourGames[serverId]:
                    self._connectFourGames[serverId].pop(authorId)
                    return getQuitGame("Connect Four", Game.EMBED_COLOR, Game.SUCCESS_ICON)
                
                # User was not playing a game
                else:
                    return getNoGame("Connect Four", Game.EMBED_COLOR, Game.FAILED_ICON)
            
            # Create game instance
            self._connectFourGames[serverId][authorId] = {
                "board": connectFour.generateBoard(7, 6),
                "difficulty": "hard",
                "width": 7,
                "height": 6,
                "challenger_turn": True,
                "challenger": discordUser,
                "opponent": None
            }
            game = self._connectFourGames[serverId][authorId]

            return discord.Embed(
                title = "Connect Four",
                description = "{}\n{}\n{}".format(
                    connectFour.getBoard(game["board"]),
                    ":large_blue_circle: " + discordUser.mention,
                    ":red_circle: AI"
                ),
                colour = Game.EMBED_COLOR
            ).set_thumbnail(
                url = Game.CONNECT_FOUR_ICON
            )
        
        # Check if move is being made
        elif move != None:
            game = self._connectFourGames[serverId][authorId]

            # Check if move is not number
            try:
                move = int(move)
            except:
                return getErrorMessage(self._connectFour, Game.INVALID_INPUT)
            
            # Check if move is not between 1 and width
            if move < 1 or move > game["width"]:
                return getErrorMessage(self._connectFour, Game.INVALID_SPOT)
            
            # Check if column is full
            if connectFour.isColumnFull(game["board"], move - 1):
                return getErrorMessage(self._connectFour, Game.COLUMN_FULL)
            
            # Move was valid; Set user's move
            winnerCheck = None
            if game["opponent"] == None:
                connectFour.addPiece(game["board"], move - 1, game["challenger_turn"])

                # Check for winner
                winnerCheck = connectFour.checkForWinner(game["board"])

                # Check for draw
                drawCheck = connectFour.isBoardFull(game["board"])
                if drawCheck:

                    # Delete game instance
                    board = game["board"]
                    challenger = game["challenger"]
                    opponent = game["opponent"]
                    self._connectFourGames[serverId].pop(authorId)

                    return discord.Embed(
                        title = "Draw",
                        description = "The game was a draw.\n{}\n{}\n{}".format(
                            connectFour.getBoard(board),
                            ":large_blue_circle: " + challenger.mention,
                            ":red_circle: " + "AI" if opponent == None else opponent.mention
                        ),
                        colour = Game.EMBED_COLOR
                    ).set_thumbnail(
                        url = Game.CONNECT_FOUR_ICON
                    )

                # Get AI's move if winner is None
                if winnerCheck == None:
                    aiMove = connectFour.getAIMove(game["board"], game["difficulty"])

                    # Check if AI's move made a draw
                    if not aiMove:

                        # Delete game instance
                        board = game["board"]
                        challenger = game["challenger"]
                        opponent = game["opponent"]
                        self._connectFourGames[serverId].pop(authorId)

                        return discord.Embed(
                            title = "Draw",
                            description = "The game was a draw.\n{}\n{}\n{}".format(
                                connectFour.getBoard(board),
                                ":large_blue_circle: " + challenger.mention,
                                ":red_circle: " + "AI" if opponent == None else opponent.mention
                            ),
                            colour = Game.EMBED_COLOR
                        ).set_thumbnail(
                            url = Game.CONNECT_FOUR_ICON
                        )

                    winnerCheck = connectFour.checkForWinner(game["board"])
            else:
                connectFour.addPiece(game["board"], move - 1, game["challenger_turn"])

                # Check for winner
                winnerCheck = connectFour.checkForWinner(game["board"])

                # Invert challenger turn for next player's turn
                game["challenger_turn"] = not game["challenger_turn"]
            
            # Check if there was a winner
            if winnerCheck == None:

                return discord.Embed(
                    title = "Connect Four",
                    description = "{}\n{}\n{}".format(
                        connectFour.getBoard(game["board"]),
                        ":large_blue_circle: " + discordUser.mention,
                        ":red_circle: AI"
                    ),
                    colour = Game.EMBED_COLOR
                ).set_thumbnail(
                    url = Game.CONNECT_FOUR_ICON
                )
            
            # Winner was challenger
            else:

                # Delete game instance
                board = game["board"]
                challenger = game["challenger"]
                opponent = game["opponent"]
                self._connectFourGames[serverId].pop(authorId)

                # Only update opponent if opponent is not None
                User.updateConnectFour(challenger, didWin = winnerCheck)
                if opponent != None:
                    User.updateConnectFour(opponent, didWin = not winnerCheck)

                return discord.Embed(
                    title = "{} Won!".format("Challenger" if winnerCheck else "Opponent"),
                    description = "{}\n{}\n{}".format(
                        connectFour.getBoard(board),
                        ":large_blue_circle: " + challenger.mention,
                        ":red_circle: " + "AI" if opponent == None else opponent.mention
                    ),
                    colour = Game.EMBED_COLOR
                ).set_thumbnail(
                    url = Game.SUCCESS_ICON if winnerCheck else Game.FAILED_ICON
                )

    def hangman(self, discordUser, *, difficulty = None, guess = None):
        """Creates a hangman game or continues a hangman game.\n

        Parameters:
            discordUser (discord.Member): The Discord User to create a game or continue one.\n
            difficulty (str): The difficulty of the game to create.\n
            guess (chr): The guess that the user made.\n
        """

        # Check if game was started in server
        try:
            serverId = str(discordUser.guild.id)
        
        # Game was started in private message
        except:
            serverId = "private"

        authorId = str(discordUser.id)

        # Create server hangman instances
        if serverId not in self._hangmanGames:
            self._hangmanGames[serverId] = {}

        # Check if new game is being created
        if difficulty != None:

            # Check if user wants to quit
            if difficulty in self._hangman.getAcceptedParameter("difficulty", "quit").getAlternatives():

                # Check if user is playing a game
                if authorId in self._hangmanGames[serverId]:
                    self._hangmanGames[serverId].pop(authorId)
                    return getQuitGame("Hangman", Game.EMBED_COLOR, Game.SUCCESS_ICON)
                
                # User was not playing a game
                else:
                    return getNoGame("Hangman", Game.EMBED_COLOR, Game.FAILED_ICON)
            
            # Make sure difficulty is valid
            difficulty = difficulty if difficulty not in [None, ""] else "easy"
            if difficulty in self._hangman.getAcceptedParameter("difficulty", "easy").getAlternatives():
                difficulty = "easy"
            elif difficulty in self._hangman.getAcceptedParameter("difficulty", "medium").getAlternatives():
                difficulty = "medium"
            elif difficulty in self._hangman.getAcceptedParameter("difficulty", "hard").getAlternatives():
                difficulty = "hard"
            
            # Difficulty is invalid
            else:
                return getErrorMessage(self._hangman, Game.INVALID_DIFFICULTY)
            
            # Create game instance
            self._hangmanGames[serverId][authorId] = {
                "word": hangman.generateWord(difficulty).lower(),
                "guesses": 0,
                "fails": 0,
                "guessed": [],
                "found": []
            }
            game = self._hangmanGames[serverId][authorId]

            return discord.Embed(
                title = "Hangman",
                description = hangman.getWord(game["word"], game["found"]),
                colour = Game.EMBED_COLOR
            ).set_thumbnail(
                url = Game.HANGMAN_ICON
            ).add_field(
                name = "Guesses: {}".format(
                    ", ".join(game["guessed"]) if len(game["guessed"]) > 0 else "None"
                ),
                value = hangman.getHangman(game["fails"])
            )
        
        # Check if guess is being made
        elif guess != None:
            game = self._hangmanGames[serverId][authorId]
            guess = guess.lower()

            # Check if guess is the word
            if guess == game["word"]:

                # Save word and amount of guesses
                word = game["word"]
                guesses = game["guesses"] + 1

                # Delete game instance; Update stats
                self._hangmanGames[serverId].pop(authorId)
                User.updateHangman(discordUser, didWin = True)

                return discord.Embed(
                    title = "Guessed",
                    description = "You guessed correctly! The word was {}\nIt took you {} guesses!".format(
                        word,
                        guesses
                    ),
                    colour = Game.EMBED_COLOR
                ).set_thumbnail(
                    url = Game.SUCCESS_ICON
                )
            
            # Make sure guess is one letter long
            # This also allows people to continue messaging someone
            # Without getting error messages from the bot
            if len(guess) > 1:
                return None

            # Make sure guess is a letter; Not number
            if guess.isnumeric():
                return getErrorMessage(self._hangman, Game.INVALID_INPUT)
            
            # Make sure guess was not already guessed
            if guess in game["guessed"]:
                return getErrorMessage(self._hangman, Game.ALREADY_GUESSED)
            
            # Guess was not already guessed; See if it was in word and add to found
            if guess in game["word"]:
                game["found"].append(guess)
            
            # Guess was not in word
            else:
                game["fails"] += 1

            # Add guess to guessed
            game["guessed"].append(guess)
            game["guesses"] += 1

            # See if guess limit was reached
            if game["fails"] >= Game.MAX_HANGMAN_GUESSES:

                # Delete game instance
                word = game["word"]
                fails = game["fails"]
                self._hangmanGames[serverId].pop(authorId)
                User.updateHangman(discordUser, didWin = False)

                return discord.Embed(
                    title = "Game Ended - Word: `{}`".format(word),
                    description = "You did not guess the word quick enough.\n{}".format(
                        hangman.getHangman(fails)
                    ),
                    colour = Game.EMBED_COLOR
                ).set_thumbnail(
                    url = Game.FAILED_ICON
                )
            
            # See if word was guessed finished by letter guessing
            # The following line gets all the letters in the word
            # Then it joins them together to create a string in order
            # To compare it to the actual word
            if "".join([letter for letter in game["word"] if letter in game["found"]]) == game["word"]:

                # Delete game instance
                word = game["word"]
                guesses = game["guesses"]
                self._hangmanGames[serverId].pop(authorId)
                User.updateHangman(discordUser, didWin = True)

                return discord.Embed(
                    title = "Success!",
                    description = "The word was `{}`\nYou guessed in {} guess{}.".format(
                        game["word"], 
                        guesses,
                        "es" if guesses > 1 else ""
                    ),
                    colour = Game.EMBED_COLOR
                ).set_thumbnail(
                    url = Game.SUCCESS_ICON
                )

            return discord.Embed(
                title = "Hangman",
                description = hangman.getWord(game["word"], game["found"]),
                colour = Game.EMBED_COLOR
            ).set_thumbnail(
                url = Game.HANGMAN_ICON
            ).add_field(
                name = "Guesses: {}".format(
                    ", ".join(game["guessed"]) if len(game["guessed"]) > 0 else "None"
                ),
                value = hangman.getHangman(game["fails"])
            )
    
    def rps(self, discordUser, action):
        """Starts or continues a Rock Paper Scissors game.\n

        Parameters:
            discordUser: The Discord User that played the game.\n
            action: The action the Discord User did.\n
        """

        # Get a random rps action
        botRps = choose(self._rpsActions)

        # Get user's rps action
        if action in self._rps.getAcceptedParameter("action", "rock").getAlternatives():
            userRps = "rock"
        elif action in self._rps.getAcceptedParameter("action", "paper").getAlternatives():
            userRps = "paper"
        elif action in self._rps.getAcceptedParameter("action", "scissors").getAlternatives():
            userRps = "scissors"
        
        # Action was invalid
        else:
            return getErrorMessage(self._rps, Game.INVALID_INPUT)

        # Check if values are the same
        message = "You had {} and I had {}".format(
            userRps, botRps
        )
        icon = Game.RPS_ICON
        if botRps == userRps:
            title = "Tied!"
            message = "You and I both tied."
        
        elif (
            (botRps == "rock" and userRps == "paper") or
            (botRps == "paper" and userRps == "scissors") or
            (botRps == "scissors" and userRps == "rock")
        ):
            title = "You Won!"
            icon = Game.SUCCESS_ICON
            User.updateRPS(discordUser, didWin = True)

        elif (
            (botRps == "rock" and userRps == "scissors") or
            (botRps == "paper" and userRps == "rock") or
            (botRps == "scissors" and userRps == "paper")
        ):
            title = "You Lost!"
            icon = Game.FAILED_ICON
            User.updateRPS(discordUser, didWin = False)
        
        return discord.Embed(
            title = title,
            description = message,
            colour = Game.EMBED_COLOR
        ).set_thumbnail(
            url = icon
        )

    def scramble(self, discordUser, *, difficulty = None, guess = None):
        """Starts or continues a scrambled word game.\n

        Parameters:
            discordUser: The Discord User that started the game.\n
        """

        # Check if game was started in server
        try:
            serverId = str(discordUser.guild.id)
        
        # Game was started in private message
        except:
            serverId = "private"

        authorId = str(discordUser.id)

        # Add serverId to scramble games if it does not exist
        if serverId not in self._scrambleGames:
            self._scrambleGames[serverId] = {}
        
        # There was no guess, start or reset game
        if difficulty != None:

            # Check if user wants to quit
            if difficulty in self._scramble.getAcceptedParameter("difficulty", "quit").getAlternatives():

                # Check if user is playing a game
                if authorId in self._scrambleGames[serverId]:
                    self._scrambleGames[serverId].pop(authorId)
                    return getQuitGame("Scramble", Game.EMBED_COLOR, Game.SUCCESS_ICON)

                # User was not playing a game
                else:
                    return getNoGame("Scramble", Game.EMBED_COLOR, Game.FAILED_ICON)
            
            # Make sure difficulty is valid
            difficulty = difficulty if difficulty not in [None, ""] else "normal"
            if difficulty in self._scramble.getAcceptedParameter("difficulty", "normal").getAlternatives():
                difficulty = "normal"
            elif difficulty in self._scramble.getAcceptedParameter("difficulty", "expert").getAlternatives():
                difficulty = "expert"
            
            # Difficult is invalid
            else:
                return getErrorMessage(self._hangman, Game.INVALID_DIFFICULTY)

            # Create game
            word = scramble.generateWord().lower()
            self._scrambleGames[serverId][authorId] = {
                "word": word,
                "scrambled": scramble.scrambleWord(word, difficulty),
                "guesses": 0,
                "guessed": []
            }
            game = self._scrambleGames[serverId][authorId]

            # Return embed
            return discord.Embed(
                title = "Scrambled",
                description = "Unscramble this word/phrase. Good luck.\n`{}`".format(
                    game["scrambled"]
                ),
                colour = Game.EMBED_COLOR
            ).set_thumbnail(
                url = Game.SCRAMBLE_ICON
            )
        
        # There was a guess; Check if it was longer than a character
        elif guess != None:
            game = self._scrambleGames[serverId][authorId]
            guess = guess.lower()

            if len(guess) > 1:

                # See if guess was equal to the word
                if guess == game["word"]:

                    # Delete game instance
                    word = game["word"]
                    guesses = game["guesses"] + 1
                    self._scrambleGames[serverId].pop(authorId)
                    User.updateScramble(discordUser, didWin = True)

                    return discord.Embed(
                        title = "Correct!",
                        description = "You guessed the word in {} guesses!".format(guesses),
                        colour = Game.EMBED_COLOR
                    ).set_thumbnail(
                        url = Game.SUCCESS_ICON
                    )
                
                # Guess was not equal to word
                else:

                    # See if guess was already guessed
                    if guess in game["guessed"]:
                        return getErrorMessage(self._scramble, Game.ALREADY_GUESSED)

                    # See if guess limit was reached
                    if game["guesses"] + 1 >= Game.MAX_SCRAMBLE_GUESSES:

                        # Delete game instance
                        word = game["word"]
                        self._scrambleGames[serverId].pop(authorId)
                        User.updateScramble(discordUser, didWin = False)

                        return discord.Embed(
                            title = "Failed",
                            description = "Unfortunately, you did not guess the word.\nThe word was {}".format(
                                word
                            ),
                            colour = Game.EMBED_COLOR
                        ).set_thumbnail(
                            url = Game.FAILED_ICON
                        )
                    
                    # Increase guesses
                    game["guessed"].append(guess)
                    game["guesses"] += 1

                    return discord.Embed(
                        title = "Nope",
                        description = "That is not the word.\nAttempts Left: {}\n`{}`".format(
                            Game.MAX_SCRAMBLE_GUESSES - game["guesses"],
                            game["scrambled"]
                        ),
                        colour = Game.EMBED_COLOR
                    ).set_thumbnail(
                        url = Game.SCRAMBLE_ICON
                    )
                
    def ticTacToe(self, discordUser, *, difficulty = None, move = None):
        """Creates a Tic Tac Toe game or continues a Tic Tac Toe game.

        Parameters:
            discordUser (discord.Member): The Discord User to create a game or continue one.
            difficulty (str): The difficulty of the game to create.
            move (str): What spot to make the move at.
        """
        
        # Check if game was started in server
        try:
            serverId = str(discordUser.guild.id)
        
        # Game was started in private message
        except:
            serverId = "private"

        authorId = str(discordUser.id)

        # Add serverId to Tic Tac Toe games if it does not exist
        if serverId not in self._ticTacToeGames:
            self._ticTacToeGames[serverId] = {}
        
        # There was no move made, start a game
        if difficulty != None:

            # Check if user wants to quit
            if difficulty in self._ticTacToe.getAcceptedParameter("difficulty", "quit").getAlternatives():

                # Check if user is playing game
                if authorId in self._ticTacToeGames[serverId]:
                    self._ticTacToeGames[serverId].pop(authorId)
                    return getQuitGame("Tic Tac Toe", Game.EMBED_COLOR, Game.SUCCESS_ICON)
                
                # User was not playing a game
                else:
                    return getNoGame("Tic Tac Toe", Game.EMBED_COLOR, Game.FAILED_ICON)
            
            # Create game
            self._ticTacToeGames[serverId][authorId] = {
                "board": [None] * 9,
                "difficulty": difficulty if difficulty not in [None, ""] else "easy",
                "challenger_turn": True,
                "challenger": discordUser,
                "opponent": None
            }
            game = self._ticTacToeGames[serverId][authorId]

            return discord.Embed(
                title = "Tic Tac Toe",
                description = "{}\n{}\n{}".format(
                        ticTacToe.getBoard(game["board"]),
                        ":x: " + game["challenger"].mention,
                        ":o: " + "AI" if game["opponent"] == None else game["opponent"].mention
                    ),
                colour = Game.EMBED_COLOR
            ).set_thumbnail(
                url = Game.TIC_TAC_TOE_ICON
            )
        
        # There was a move; See what move it was
        elif move != None:
            game = self._ticTacToeGames[serverId][authorId]

            # Check if move is not number
            try:
                move = int(move)
            except:
                return getErrorMessage(self._ticTacToe, Game.INVALID_INPUT)
            
            # Check if move is not between 1 and 9
            if move < 1 or move > 9:
                return getErrorMessage(self._ticTacToe, Game.INVALID_SPOT)
            
            # Check if move is already been done
            if game["board"][move - 1] != None:
                return getErrorMessage(self._ticTacToe, Game.ALREADY_GUESSED)
            
            # Move is valid; Set user's move
            winnerCheck = None
            if game["opponent"] == None:
                game["board"][move - 1] = True

                # Check for winner
                winnerCheck = ticTacToe.checkForWinner(game["board"])

                # Check if the board is full; There is no winner
                if game["board"].count(None) == 0 and winnerCheck == None:

                    # Delete game instance
                    board = game["board"]
                    challenger = game["challenger"]
                    opponent = game["opponent"]
                    self._ticTacToeGames[serverId].pop(authorId)

                    return discord.Embed(
                        title = "Draw",
                        description = "The game was a draw.\n{}\n{}\n{}".format(
                            ticTacToe.getBoard(board),
                            ":x: " + challenger.mention,
                            ":o: " + "AI" if opponent == None else opponent.mention
                        ),
                        colour = Game.EMBED_COLOR
                    ).set_thumbnail(
                        url = Game.TIC_TAC_TOE_ICON
                    )

                # Get AI's move if winner is None
                if winnerCheck == None:
                    ticTacToe.getAIMove(game["board"], game["difficulty"])

                    # Check if the board is full; There is no winner
                    if game["board"].count(None) == 0:

                        # Delete game instance
                        board = game["board"]
                        challenger = game["challenger"]
                        opponent = game["opponent"]
                        self._ticTacToeGames[serverId].pop(authorId)

                        return discord.Embed(
                            title = "Draw",
                            description = "The game was a draw.\n{}\n{}\n{}".format(
                                ticTacToe.getBoard(board),
                                ":x: " + challenger.mention,
                                ":o: " + "AI" if opponent == None else opponent.mention
                            ),
                            colour = Game.EMBED_COLOR
                        ).set_thumbnail(
                            url = Game.TIC_TAC_TOE_ICON
                        )

                    # Check for winner
                    winnerCheck = ticTacToe.checkForWinner(game["board"])
            else:
                game["board"][move - 1] = game["challenger_turn"]

                # Check for winner
                winnerCheck = ticTacToe.checkForWinner(game["board"])

                # Check if the board is full; There is no winner
                if game["board"].count(None) == 0 and winnerCheck == None:

                    # Delete game instance
                    board = game["board"]
                    challenger = game["challenger"]
                    opponent = game["opponent"]
                    self._ticTacToeGames[serverId].pop(authorId)

                    return discord.Embed(
                        title = "Draw",
                        description = "The game was a draw.\n{}\n{}\n{}".format(
                            ticTacToe.getBoard(board),
                            ":x: " + challenger.mention,
                            ":o: " + "AI" if opponent == None else opponent.mention
                        ),
                        colour = Game.EMBED_COLOR
                    ).set_thumbnail(
                        url = Game.TIC_TAC_TOE_ICON
                    )

                # Invert challenger turn for next player's turn
                game["challenger_turn"] = not game["challenger_turn"]

            # Check if there was a winner
            if winnerCheck == None:

                # Show result
                return discord.Embed(
                    title = "Tic Tac Toe",
                    description = "{}\n{}\n{}".format(
                        ticTacToe.getBoard(game["board"]),
                        ":x: " + game["challenger"].mention,
                        ":o: " + "AI" if game["opponent"] == None else game["opponent"].mention
                    ),
                    colour = Game.EMBED_COLOR
                ).set_thumbnail(
                    url = Game.TIC_TAC_TOE_ICON
                )
            
            # Winner was challenger
            else:
                
                # Delete game instance
                board = game["board"]
                challenger = game["challenger"]
                opponent = game["opponent"]
                self._ticTacToeGames[serverId].pop(authorId)

                # Only update opponent if opponent is not None
                User.updateTicTacToe(challenger, didWin = winnerCheck)
                if opponent != None:
                    User.updateTicTacToe(opponent, didWin = not winnerCheck)
                
                # Show results
                return discord.Embed(
                    title = "{} Won!".format("Challenger" if winnerCheck else "Opponent"),
                    description = "{}\n{}\n{}".format(
                        ticTacToe.getBoard(board),
                        ":x: " + challenger.mention,
                        ":o: " + "AI" if opponent == None else opponent.mention
                    ),
                    colour = Game.EMBED_COLOR
                ).set_thumbnail(
                    url = Game.SUCCESS_ICON if winnerCheck else Game.FAILED_ICON
                )
    
    def stats(self, discordUser):
        """Shows the stats for the specified Discord User.\n

        Parameters:
            discordUser: The Discord User to get the stats of.\n
        """

        # Open user file
        user = User.openUser(discordUser)

        # Get game stats
        games = {
            ":red_circle: Connect Four": user["connect_four"].copy(),
            ":skull_crossbones: Hangman": user["hangman"].copy(),
            ":scissors: Rock Paper Scissors": user["rps"].copy(),
            ":cyclone: Scramble": user["scramble"].copy(),
            ":x: Tic Tac Toe": user["tic_tac_toe"].copy()
        }

        # Close user file
        User.closeUser(user)

        embed = discord.Embed(
            title = "Stats",
            description = "Game Stats for {}".format(discordUser.mention),
            colour = Game.EMBED_COLOR
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
        
        return embed
    
    def blackOps3(self, parameters):
        """Gets the Black Ops 3 stats for a user on a platform.

        Parameters:
            platform (str): The platform to get the stats on.
            username (str): The user to get the stats for.
        """

        # Check for not enough parameters
        if len(parameters) < self._blackOps3.getMinParameters():
            return getErrorMessage(self._blackOps3, Game.NOT_ENOUGH_PARAMETERS)
        
        # There were enough parameters
        platform = parameters[0]
        username = " ".join(parameters[1:])

        # Make sure platform is valid
        if platform in self._blackOps3.getAcceptedParameter("platform", "xbox").getAlternatives():
            platform = 1
        elif platform in self._blackOps3.getAcceptedParameter("platform", "psn").getAlternatives():
            platform = 2
        
        # Platform is not valid
        else:
            return getErrorMessage(self._blackOps3, Game.INVALID_PLATFORM)
        
        # Request data
        blackOps3Json = requests.get(
            Game.BLACK_OPS_3_URL.format(platform, username),
            headers = {
                "TRN-Api-Key": os.environ["BLACK_OPS_API_KEY"]
            }
        ).json()

        # See if an error was given
        if "errors" in blackOps3Json:
            return getErrorMessage(self._blackOps3, Game.NO_USER)
        
        # There was no error given; Get stats and put inside Embed
        embed = discord.Embed(
            title = "Black Ops 3 Stats",
            description = "{} - {}".format(
                blackOps3Json["data"]["metadata"]["platformUserHandle"],
                "Xbox" if blackOps3Json["data"]["metadata"]["platformId"] == 1 else "PSN"
            ),
            colour = Game.EMBED_COLOR,
            timestamp = datetime.now()
        ).set_author(
            name = blackOps3Json["data"]["metadata"]["platformUserHandle"],
            icon_url = Game.BLACK_OPS_3_ICON
        ).set_footer(
            text = "Black Ops 3 Tracker"
        )

        # Add stats using Black Ops 3 parser
        embed = blackOps3.getGameStats(embed, blackOps3Json)

        return embed
    
    def blackOps4(self, parameters):
        """Gets the Black Ops 4 stats for a user on a platform.

        Parameters:
            platform (str): The platform to get the stats on.
            username (str): The user to get the stats for.
        """

        # Check for not enough parameters
        if len(parameters) < self._blackOps4.getMinParameters():
            return getErrorMessage(self._blackOps4, Game.NOT_ENOUGH_PARAMETERS)
        
        # There were enough parameters
        platform = parameters[0]
        username = " ".join(parameters[1:])

        # Make sure platform is valid
        if platform in self._blackOps4.getAcceptedParameter("platform", "xbox").getAlternatives():
            platform = 1
        elif platform in self._blackOps4.getAcceptedParameter("platform", "psn").getAlternatives():
            platform = 2
        
        # Platform is not valid
        else:
            return getErrorMessage(self._blackOps4, Game.INVALID_PLATFORM)
        
        # Request data
        blackOps4Json = requests.get(
            Game.BLACK_OPS_4_URL.format(platform, username),
            headers = {
                "TRN-Api-Key": os.environ["BLACK_OPS_API_KEY"]
            }
        ).json()

        # See if an error was given
        if "errors" in blackOps4Json:
            return getErrorMessage(self._blackOps4, Game.NO_USER)
        
        # There was no error given; Get stats and put inside Embed; Use Level icon for author icon
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
            colour = Game.EMBED_COLOR,
            timestamp = datetime.now()
        ).set_author(
            name = blackOps4Json["data"]["metadata"]["platformUserHandle"],
            icon_url = levelIcon
        ).set_footer(
            text = "Black Ops 4 Tracker"
        )

        # Add stats using Black Ops 4 parser
        embed = blackOps4.getGameStats(embed, blackOps4Json)

        return embed
    
    def fortnite(self, parameters):
        """Gets the Fortnite stats for a user on a platform.

        Parameters:
            platform (str): The platform to get the stats on.
            username (str): The user to get the stats for.
        """

        # Check for not enough parameters
        if len(parameters) < self._fortnite.getMinParameters():
            return getErrorMessage(self._fortnite, Game.NOT_ENOUGH_PARAMETERS)
        
        # There were enough parameters
        platform = parameters[0]
        username = " ".join(parameters[1:])

        # Make sure platform is valid
        if platform in self._fortnite.getAcceptedParameter("platform", "pc").getAlternatives():
            platform = "pc"
        elif platform in self._fortnite.getAcceptedParameter("platform", "xbox").getAlternatives():
            platform = "xbox"
        elif platform in self._fortnite.getAcceptedParameter("platform", "psn").getAlternatives():
            platform = "psn"
        
        # Platform is not valid
        else:
            return getErrorMessage(self._fortnite, Game.INVALID_PLATFORM)

        # Request data
        fortniteJson = requests.get(
            Game.FORTNITE_URL.format(platform, username),
            headers = {
                "TRN-Api-Key": os.environ["FORTNITE_API_KEY"]
            }
        ).json()

        # See if an error was given.
        if "error" in fortniteJson:
            return getErrorMessage(self._fortnite, Game.NO_USER)
        
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
            colour = Game.EMBED_COLOR,
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

        return embed
    
    def fortniteItemShop(self):
        """Gets the current Fortnite Item shop.
        """

        # Request data
        fortniteItems = requests.get(
            Game.FORTNITE_ITEM_SHOP_URL,
            headers = {
                "TRN-Api-Key": os.environ["FORTNITE_API_KEY"]
            }
        ).json()

        # Create file
        return fortnite.getItemShopImage(fortniteItems)
    
    def league(self, parameters):
        """Gets the League of Legends stats for a Summoner.

        Parameters:
            username (str): The username of the Summoner to get stats for.
        """

        return None
    
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
        if Server.startsWithPrefix(message.guild, message.content) and not message.author.bot:

            # Split up into command and parameters if possible
            command, parameters = Category.parseText(Server.getPrefixes(message.guild), message.content)
            
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            # Connect Four Command
            if command in self._connectFour.getAlternatives():

                # 0 or 1 Parameter Exists
                if len(parameters) in [0, 1]:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._connectFour, self.connectFour, message.author, difficulty = "".join(parameters))
                    )
                
                # 2 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._connectFour, Category.TOO_MANY_PARAMETERS)
                    )

            # Hangman Command
            elif command in self._hangman.getAlternatives():

                # 0 or 1 Parameter Exists
                if len(parameters) in [0, 1]:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._hangman, self.hangman, message.author, difficulty = "".join(parameters))
                    )
                
                # 2 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._hangman, Game.TOO_MANY_PARAMETERS)
                    )
            
            # Rock Paper Scissors Command
            elif command in self._rps.getAlternatives():

                # 0 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._rps, Game.NOT_ENOUGH_PARAMETERS)
                    )
                
                # 1 Parameter Exists
                elif len(parameters) == 1:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._rps, self.rps, message.author, parameters[0])
                    )
                
                # 2 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._hangman, Game.TOO_MANY_PARAMETERS)
                    )
            
            # Scramble Command
            elif command in self._scramble.getAlternatives():

                # 0 or 1 Parameter Exists
                if len(parameters) in [0, 1]:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._scramble, self.scramble, message.author, difficulty = "".join(parameters))
                    )
                
                # 2 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._scramble, Game.TOO_MANY_PARAMETERS)
                    )
            
            # Tic Tac Toe Command
            elif command in self._ticTacToe.getAlternatives():

                # 0 or 1 Parameter Exists
                if len(parameters) in [0, 1]:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._ticTacToe, self.ticTacToe, message.author, difficulty = "".join(parameters))
                    )
                
                # 2 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._ticTacToe, Game.TOO_MANY_PARAMETERS)
                    )
            
            # Stats Command
            elif command in self._stats.getAlternatives():

                # 0 Parameters Exist
                if len(parameters) == 0:
                    await sendMessage(
                        self.client,
                        message,
                        embed = await run(message, self._stats, self.stats, message.author)
                    )
                
                # 1 or More Parameters Exist
                else:
                    await sendMessage(
                        self.client,
                        message,
                        embed = getErrorMessage(self._stats, Game.TOO_MANY_PARAMETERS)
                    )
                
            # Black Ops 3 Command
            elif command in self._blackOps3.getAlternatives():

                await sendMessage(
                    self.client,
                    message,
                    embed = await self.run(message, self._blackOps3, self.blackOps3, parameters)
                )
            
            # Black Ops 4 Command
            elif command in self._blackOps4.getAlternatives():

                await sendMessage(
                    self.client,
                    message,
                    embed = await self.run(message, self._blackOps4, self.blackOps4, parameters)
                )
            
            # Fortnite Command
            elif command in self._fortnite.getAlternatives():

                await sendMessage(
                    self.client,
                    message,
                    embed = await self.run(message, self._fortnite, self.fortnite, parameters)
                )
            
            # Fortnite Item Shop Command
            elif command in self._fortniteItemShop.getAlternatives():
                result = await self.run(message, self._fortniteItemShop, self.fortniteItemShop)

                await sendMessage(
                    self.client,
                    message,
                    filename = result
                )
                os.remove(result)
        
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Check Running Games
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Only run games if prefix is not found
        if not Server.startsWithPrefix(message.guild, message.content):

            # Connect Four
            if self.isPlayerInGame(self._connectFourGames, message.author, message.guild):
                await sendMessage(
                    self.client,
                    message,
                    embed = self.connectFour(message.author, move = message.content)
                )

            # Hangman
            if self.isPlayerInGame(self._hangmanGames, message.author, message.guild):
                await sendMessage(
                    self.client,
                    message,
                    embed = self.hangman(message.author, guess = message.content)
                )
            
            # Scramble
            if self.isPlayerInGame(self._scrambleGames, message.author, message.guild):
                await sendMessage(
                    self.client,
                    message,
                    embed = self.scramble(message.author, guess = message.content)
                )
            
            # Tic Tac Toe
            if self.isPlayerInGame(self._ticTacToeGames, message.author, message.guild):
                await sendMessage(
                    self.client,
                    message,
                    embed = self.ticTacToe(message.author, move = message.content)
                )

def setup(client):
    client.add_cog(Game(client))
