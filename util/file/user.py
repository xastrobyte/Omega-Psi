from util.file.database import omegaPsi
from util.file.server import Server

from util.utils.dictUtils import setDefault

class User:

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Helper Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def openUser(discordUser):
        """Opens the file for the Discord User given.\n

        discordUser - The Discord User to load.\n
        """

        # Default values
        defaultValues = {
            "_id": discordUser.id,
            "connect_four": {
                "won": 0,
                "lost": 0
            },
            "hangman": {
                "won": 0,
                "lost": 0
            },
            "rps": {
                "won": 0,
                "lost": 0
            },
            "scramble": {
                "won": 0,
                "lost": 0
            },
            "tic_tac_toe": {
                "won": 0,
                "lost": 0
            }
        }

        # Get user information
        userDict = omegaPsi.getUser(str(discordUser.id))
            
        return setDefault(defaultValues, userDict)
    
    def closeUser(userDict):
        """Closes the file for the Discord User.\n

        userDict - The Discord User to save.\n
        """

        # Update user information
        omegaPsi.setUser(userDict["_id"], userDict)
        
    def updateConnectFour(discordUser, *, didWin = False):
        """Updates the connect four score.

        Parameters:
            discordUser (discord.User): The Discord User to update the connect four stats in.
            didWin (bool): Whether or not the player won a connect four game.
        """

        # Open user file
        user = User.openUser(discordUser)

        # Update member connect four stats
        user["connect_four"]["won"] += 1 if didWin else 0
        user["connect_four"]["lost"] += 1 if not didWin else 0

        # Close user file
        User.closeUser(user)
    
    def updateHangman(discordUser, *, didWin = False):
        """Updates the hangman score.

        Parameters:
            discordUser (discord.User): The Discord User to update the hangman stats in.
            didWin (bool): Whether or not the player won a hangman game.
        """

        # Open user file
        user = User.openUser(discordUser)

        # Update member hangman stats
        user["hangman"]["won"] += 1 if didWin else 0
        user["hangman"]["lost"] += 1 if not didWin else 0

        # Close user file
        User.closeUser(user)
    
    def updateRPS(discordUser, *, didWin = False):
        """Updates the tic tac toe score.

        Parameters:
            discordUser (discord.User): The Discord User to update the rock paper scissors stats in.
            didWin (bool): Whether or not the player won a rock paper scissors game.
        """

        # Open user file
        user = User.openUser(discordUser)

        # Update member RPS stats
        user["rps"]["won"] += 1 if didWin else 0
        user["rps"]["lost"] += 1 if not didWin else 0

        # Close user file
        User.closeUser(user)
    
    def updateScramble(discordUser, *, didWin = False):
        """Updates the tic tac toe score.

        Parameters:
            discordUser (discord.User): The Discord User to update the scramble stats in.
            didWin (bool): Whether or not the player won a scramble game.
        """

        # Open user file
        user = User.openUser(discordUser)

        # Update member scramble stats
        user["scramble"]["won"] += 1 if didWin else 0
        user["scramble"]["lost"] += 1 if not didWin else 0

        # Close user file
        User.closeUser(user)
    
    def updateTicTacToe(discordUser, *, didWin = False):
        """Updates the tic tac toe score.

        Parameters:
            discordUser (discord.User): The Discord User to update the tic tac toe stats in.
            didWin (bool): Whether or not the player won a tic tac toe game.
        """

        # Open user file
        user = User.openUser(discordUser)

        # Update member tic tac toe stats
        user["tic_tac_toe"]["won"] += 1 if didWin else 0
        user["tic_tac_toe"]["lost"] += 1 if not didWin else 0

        # Close user file
        User.closeUser(user)