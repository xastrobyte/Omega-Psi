from util.file.omegaPsi import OmegaPsi

import json

class User:

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # File locations
    USER_FILE = "data/users/{}.json"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Helper Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def openUser(discordUser):
        """Opens the file for the Discord User given.\n

        discordUser - The Discord User to load.\n
        """

        # Default values
        defaultValues = {
            "id": discordUser.id,
            "name": discordUser.name,
            "discriminator": discordUser.discriminator,
            "stats": {
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
                }
            }
        }

        # Try to open file
        try:

            # Open file
            with open(User.USER_FILE.format(discordUser.id), "r") as userFile:
                userDict = json.load(userFile)
            
            # See if default values are missing
            for value in defaultValues:

                # Check if value is not in user dictionary; Set default value
                if value not in userDict:
                    userDict[value] = defaultValues[value]
            
            # See if User name or discriminator changed
            userDict["name"] = discordUser.name
            userDict["discriminator"] = discordUser.discriminator
            
            return userDict
            
        # File did not exist, create it
        except IOError:
            userDict = defaultValues 
            User.closeUser(userDict)

            return User.openUser(discordUser)
    
    def closeUser(userDict):
        """Closes the file for the Discord User.\n

        userDict - The Discord User to save.\n
        """

        # Open file
        with open(User.USER_FILE.format(userDict["id"]), "w") as userFile:
            userFile.write(json.dumps(userDict, sort_keys = True, indent = 4))
    
    def updateHangman(discordUser, *, didWin = False):
        """Updates the hangman score.\n

        - discordUser - The Discord User to update the hangman stats of.\n
        - didWin - Whether or not the player won a hangman game.\n
        """

        # Open user file
        user = User.openUser(discordUser)

        # Update member hangman stats
        user["stats"]["hangman"]["won"] += 1 if didWin else 0
        user["stats"]["hangman"]["lost"] += 1 if not didWin else 0

        # Close user file
        User.closeUser(user)
    
    def updateRPS(discordUser, *, didWin = False):
        """Updates the Rock, Paper, Scissors score.\n

        - discordUser - The Discord User to update the Rock, Paper, Scissors stats in.\n
        - didWin - Whether or not the player won a Rock, Paper, Scissors game.\n
        """

        # Open user file
        user = User.openUser(discordUser)

        # Update member RPS stats
        user["stats"]["rps"]["won"] += 1 if didWin else 0
        user["stats"]["rps"]["lost"] += 1 if not didWin else 0

        # Close user file
        User.closeUser(user)
    
    def updateScramble(discordUser, *, didWin = False):
        """Updates the scramble score.\n

        - discordUser - The Discord User to update the scramble stats in.\n
        - didWin - Whether or not the player won a scramble game.\n
        """

        # Open user file
        user = User.openUser(discordUser)

        # Update member scramble stats
        user["stats"]["scramble"]["won"] += 1 if didWin else 0
        user["stats"]["scramble"]["lost"] += 1 if not didWin else 0

        # Close user file
        User.closeUser(user)
