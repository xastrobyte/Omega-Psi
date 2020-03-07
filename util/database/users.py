from discord import User
from typing import Union

from cogs.globals import loop

from util.misc import set_default

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class User:
    def __init__(self, users):
        self._users = users
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # User Access Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_user_sync(self, user : Union[User, str]):
        """Synchronously retrieves user data from the database

        Parameters
        ----------
            user : str or User
                The User to get the data for from the database
        
        Returns
        -------
            dict
                The JSON object of the user's data
        """
        user_id = user if isinstance(user, str) else str(user.id)
        
        # Default
        data = {
            "_id": user_id,
            "embed_color": None,
            "imgur": {
                "hash": None,
                "id": None
            },
            "ifttt": {
                "active": False,
                "webhook_key": None
            },
            "connect_four": {
                "won": 0,
                "lost": 0
            },
            "tic_tac_toe": {
                "won": 0,
                "lost": 0
            },
            "cards_against_humanity": {
                "won": 0,
                "lost": 0
            },
            "uno": {
                "won": 0,
                "lost": 0
            },
            "game_of_life": {
                "won": 0,
                "lost": 0
            },
            "omok": {
                "won": 0,
                "lost": 0
            }
        }

        # Get user data
        user_data = self._users.find_one({"_id": user_id})
        if not user_data:
            self._users.insert_one({"_id": user_id})
            self.set_user_sync(user, data)
            user_data = data
        
        user_data = set_default(data, user_data)
        return user_data
    
    def set_user_sync(self, user : Union[User, str], user_data):
        """Synchronously sets user data from the database

        Parameters
        ----------
            user : str or User
        """
        user_id = user if isinstance(user, str) else str(user.id)
        self._users.update_one({"_id": user_id}, {"$set": user_data}, upsert = False)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_user(self, user : Union[User, str]):
        """Asynchronously retrieves user data from the database

        Parameters
        ----------
            user : str or User
                The User to get the data for from the database
        
        Returns
        -------
            dict
                The JSON object of the user's data
        """
        return await loop.run_in_executor(None, self.get_user_sync, user)
    
    async def set_user(self, user : Union[User, str], user_data):
        """Asynchronously sets user data from the database

        Parameters
        ----------
            user : str or User
        """
        await loop.run_in_executor(None, self.set_user_sync, user, user_data)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # IFTTT Access Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_ifttt_sync(self, user : Union[User, str]):
        """Synchronously retrieves the user's IFTTT data from the database

        Parameters
        ----------
            user : str or User
                The User to get the IFTTT data of
        
        Returns
        -------
            dict
                The User's IFTTT data
        """
        user_data = self.get_user_sync(user)
        return user_data["ifttt"]
    
    def set_ifttt_sync(self, user : Union[User, str], ifttt_data):
        """Synchronously sets the user's IFTTT data in the database

        Parameters
        ----------
            user : str or User
                The User to set the IFTTT data for
            ifttt_data : dict
                The JSON object of the user's IFTTT data
        """
        user_data = self.get_user_sync(user)
        user_data["ifttt"] = ifttt_data
        self.set_user_sync(user, user_data)
    
    def is_ifttt_active_sync(self, user : Union[User, str]):
        """Synchronously retrieves whether or not IFTTT is active for the user

        Parameters
        ----------
            user : str or User
                The User to get the IFTTT status of
        
        Returns
        -------
            boolean
                Whether or not the User's IFTTT is active
        """
        ifttt_data = self.get_ifttt_sync(user)
        return ifttt_data["active"]
    
    def toggle_ifttt_sync(self, user : Union[User, str]):
        """Synchronously toggles the user's IFTTT on/off

        Parameters
        ----------
            user : str or User
                The User to toggle the IFTTT status of
        
        Returns
        -------
            boolean
                Whether or not the User's IFTTT is active
        """
        ifttt_data = self.get_ifttt_sync(user)
        ifttt_data["active"] = not ifttt_data["active"]
        self.set_ifttt_sync(user, ifttt_data)
        return ifttt_data["active"]
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_ifttt(self, user : Union[User, str]):
        """Asynchronously retrieves the user's IFTTT data from the database

        Parameters
        ----------
            user : str or User
                The User to get the IFTTT data of
        
        Returns
        -------
            dict
                The User's IFTTT data
        """
        return await loop.run_in_executor(None, self.get_ifttt_sync, user)
    
    async def set_ifttt(self, user : Union[User, str], ifttt_data):
        """Asynchronously sets the user's IFTTT data in the database

        Parameters
        ----------
            user : str or User
                The User to set the IFTTT data for
            ifttt_data : dict
                The JSON object of the user's IFTTT data
        """
        await loop.run_in_executor(None, self.set_ifttt_sync, user, ifttt_data)
    
    async def is_ifttt_active(self, user : Union[User, str]):
        """Asynchronously retrieves whether or not IFTTT is active for the user

        Parameters
        ----------
            user : str or User
                The User to get the IFTTT status of
        
        Returns
        -------
            boolean
                Whether or not the User's IFTTT is active
        """
        return await loop.run_in_executor(None, self.is_ifttt_active_sync, user)
    
    async def toggle_ifttt(self, user : Union[User, str]):
        """Asynchronously toggles the user's IFTTT on/off

        Parameters
        ----------
            user : str or User
                The User to toggle the IFTTT status of
        
        Returns
        -------
            boolean
                Whether or not the User's IFTTT is active
        """
        return await loop.run_in_executor(None, self.toggle_ifttt_sync, user)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Minigame Access Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_connect_four_sync(self, user : Union[User, str]):
        """Synchronously retrieves the user's connect four data from the database

        Parameters
        ----------
            user : str or User
                The User to get the Connect Four data of
        
        Returns
        -------
            dict
                The User's Connect Four data
        """
        user_data = self.get_user_sync(user)
        return user_data["connect_four"]
    
    def get_tic_tac_toe_sync(self, user : Union[User, str]):
        """Synchronously retrieves the user's tic tac toe data from the database

        Parameters
        ----------
            user : str or User
                The User to get the Tic Tac Toe data of
        
        Returns
        -------
            dict
                The User's Tic Tac Toe data
        """
        user_data = self.get_user_sync(user)
        return user_data["tic_tac_toe"]
    
    def get_game_of_life_sync(self, user : Union[User, str]):
        """Synchronously retrieves the user's game of life data from the database

        Parameters
        ----------
            user : str or User
                The User to get the Game of Life data of
        
        Returns
        -------
            dict
                The User's Game of Life data
        """
        user_data = self.get_user_sync(user)
        return user_data["game_of_life"]
    
    def get_omok_sync(self, user : Union[User, str]):
        """Synchronously retrieves the user's omok data from the database

        Parameters
        ----------
            user : str or User
                The User to get the Omok data of
        
        Returns
        -------
            dict
                The User's Omok data
        """
        user_data = self.get_user_sync(user)
        return user_data["omok"];
    
    # # # # # # # # # # # # # # #
    
    def update_connect_four_sync(self, user : Union[User, str], won):
        """Synchronously updates the user's connect four data in the database

        Parameters
        ----------
            user : str or User
                The User to update the Connect Four data of
            won : boolean
                Whether or not the User won
        """
        user_data = self.get_user_sync(user)
        user_data["connect_four"]["won" if won else "lost"] += 1
        self.set_user_sync(user, user_data)
    
    def update_tic_tac_toe_sync(self, user : Union[User, str], won):
        """Synchronously updates the user's tic tac toe data in the database

        Parameters
        ----------
            user : str or User
                The User to update the Tic Tac Toe data of
            won : boolean
                Whether or not the User won
        """
        user_data = self.get_user_sync(user)
        user_data["tic_tac_toe"]["won" if won else "lost"] += 1
        self.set_user_sync(user, user_data)
    
    def update_game_of_life_sync(self, user : Union[User, str], won):
        """Synchronously updates the user's game of life data in the database

        Parameters
        ----------
            user : str or User
                The User to update the Game of Life data of
            won : boolean
                Whether or not the User won
        """
        user_data = self.get_user_sync(user)
        user_data["game_of_life"]["won" if won else "lost"] += 1
        self.set_user_sync(user, user_data)
    
    def update_omok_sync(self, user : Union[User, str], won):
        """Synchronously updates the user's omok data in the database

        Parameters
        ----------
            user : str or User
                The User to update the Omok data of
            won : boolean
                Whether or not the User won
        """
        user_data = self.get_user_sync(user)
        user_data["omok"]["won" if won else "lost"] += 1
        self.set_user_sync(user, user_data)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_connect_four(self, user : Union[User, str]):
        """Asynchronously retrieves the user's connect four data from the database

        Parameters
        ----------
            user : str or User
                The User to get the Connect Four data of
        
        Returns
        -------
            dict
                The User's Connect Four data
        """
        return await loop.run_in_executor(None, self.get_connect_four_sync, user)
    
    async def get_tic_tac_toe(self, user : Union[User, str]):
        """Asynchronously retrieves the user's tic tac toe data from the database

        Parameters
        ----------
            user : str or User
                The User to get the Tic Tac Toe data of
        
        Returns
        -------
            dict
                The User's Tic Tac Toe data
        """
        return await loop.run_in_executor(None, self.get_tic_tac_toe_sync, user)
    
    async def get_game_of_life(self, user : Union[User, str]):
        """Asynchronously retrieves the user's game of life data from the database

        Parameters
        ----------
            user : str or User
                The User to get the Game of Life data of
        
        Returns
        -------
            dict
                The User's Game of Life data
        """
        return await loop.run_in_executor(None, self.get_game_of_life_sync, user)

    async def get_omok(self, user : Union[User, str]):
        """Asynchronously retrieves the user's omok data from the database

        Parameters
        ----------
            user : str or User
                The User to get the Omok data of
        
        Returns
        -------
            dict
                The User's Omok data
        """
        return await loop.run_in_executor(None, self.get_omok_sync, user)

    # # # # # # # # # # # # # # #

    async def update_connect_four(self, user : Union[User, str], won):
        """Asynchronously updates the user's connect four data in the database

        Parameters
        ----------
            user : str or User
                The User to update the Connect Four data of
            won : boolean
                Whether or not the User won
        """
        await loop.run_in_executor(None, self.update_connect_four_sync, user, won)
    
    async def update_tic_tac_toe(self, user : Union[User, str], won):
        """Asynchronously updates the user's tic tac toe data in the database

        Parameters
        ----------
            user : str or User
                The User to update the Tic Tac Toe data of
            won : boolean
                Whether or not the User won
        """
        await loop.run_in_executor(None, self.update_tic_tac_toe_sync, user, won)
    
    async def update_game_of_life(self, user : Union[User, str], won):
        """Asynchronously updates the user's game of life data in the database

        Parameters
        ----------
            user : str or User
                The User to update the Game of Life data of
            won : boolean
                Whether or not the User won
        """
        await loop.run_in_executor(None, self.update_game_of_life_sync, user, won)
    
    async def update_omok(self, user : Union[User, str], won):
        """Asynchronously updates the user's omok data in the database

        Parameters
        ----------
            user : str or User
                The User to update the Omok data of
            won : boolean
                Whether or not the User won
        """
        await loop.run_in_executor(None, self.update_omok_sync, user, won)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Card Game Access Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    def get_cards_against_humanity_sync(self : Union[User, str], user):
        """Synchronously retrieves the user's cards against humanity data from the database

        Parameters
        ----------
            user : str or User
                The User to get the Cards Against Humanity data of
        
        Returns
        -------
            dict
                The JSON object of the User's Cards Against Humanity data
        """
        user_data = self.get_user_sync(user)
        return user_data["cards_against_humanity"]
    
    def get_uno_sync(self : Union[User, str], user):
        """Synchronously retrieves the user's uno data from the database

        Parameters
        ----------
            user : str or User
                The User to get the Uno data of
        
        Returns
        -------
            dict
                The JSON object of the User's Uno data
        """
        user_data = self.get_user_sync(user)
        return user_data["uno"]
    
    # # # # # # # # # # # # # # #
    
    def update_cards_against_humanity_sync(self, user : Union[User, str], won):
        """Synchronously updates the cards against humanity data in the database

        Parameters
        ----------
            user : str or User
                The User to get update the Cards Against Humanity data for
            won : boolean
                Whether or not the User won
        """
        user_data = self.get_user_sync(user)
        user_data["cards_against_humanity"]["won" if won else "lost"] += 1
        self.set_user_sync(user, user_data)
    
    def update_uno_sync(self, user : Union[User, str], won):
        """Synchronously updates the user's uno data in the database

        Parameters
        ----------
            user : str or User
                The User to get update the Uno data for
            won : boolean
                Whether or not the User won
        """
        user_data = self.get_user_sync(user)
        user_data["uno"]["won" if won else "lost"] += 1
        self.set_user_sync(user, user_data)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_cards_against_humanity(self, user : Union[User, str]):
        """Asynchronously retrieves the user's cards against humanity data from the database

        Parameters
        ----------
            user : str or User
                The User to get the Cards Against Humanity data of
        
        Returns
        -------
            dict
                The JSON object of the User's Cards Against Humanity data
        """
        return await loop.run_in_executor(None, self.get_cards_against_humanity_sync, user)
    
    async def get_uno(self, user : Union[User, str]):
        """Asynchronously retrieves the user's uno data from the database

        Parameters
        ----------
            user : str or User
                The User to get the Uno data of
        
        Returns
        -------
            dict
                The JSON object of the User's Uno data
        """
        return await loop.run_in_executor(None, self.get_uno_sync, user)

    # # # # # # # # # # # # # # #

    async def update_cards_against_humanity(self, user : Union[User, str], won):
        """Asynchronously updates the cards against humanity data in the database

        Parameters
        ----------
            user : str or User
                The User to get update the Cards Against Humanity data for
            won : boolean
                Whether or not the User won
        """
        await loop.run_in_executor(None, self.update_cards_against_humanity_sync, user, won)
    
    async def update_uno(self, user : Union[User, str], won):
        """Asynchronously updates the user's uno data in the database

        Parameters
        ----------
            user : str or User
                The User to get update the Uno data for
            won : boolean
                Whether or not the User won
        """
        await loop.run_in_executor(None, self.update_uno_sync, user, won)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Miscellaneous Access Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_imgur_sync(self, user : Union[User, str]):
        """Synchronously retrieves the user's imgur data from the database

        Parameters
        ----------
            user : str or User
                The User to get the Imgur data of
        
        Returns
        -------
            dict
                The User's Imgur data
        """
        user_data = self.get_user_sync(user)
        return user_data["imgur"]
    
    def set_imgur_sync(self, user : Union[User, str], imgur_data):
        """Synchronously sets the user's imgur data in the database

        Parameters
        ----------
            user : str or User
                The User to set the Imgur data for
            imgur_data : dict
                The User's Imgur data
        """
        user_data = self.get_user_sync(user)
        user_data["imgur"] = imgur_data
        self.set_user_sync(user, user_data)
    
    # # # # # # # # # # # # # # #
    
    def get_embed_color_sync(self, user : Union[User, str]):
        """Synchronously retrieves the user's embed color from the database

        Parameters
        ----------
            user : str or User
                The User to get the embed color of
        
        Returns
        -------
            dict
                The User's embed color
        """
        user_data = self.get_user_sync(user)
        return user_data["embed_color"]
    
    def set_embed_color_sync(self, user : Union[User, str], embed_color):
        """Synchronously sets the user's embed color in the database

        Parameters
        ----------
            user : str or User
                The User to set the embed color for
            imgur_data : dict
                The User's embed color
        """
        user_data = self.get_user_sync(user)
        user_data["embed_color"] = embed_color
        self.set_user_sync(user, user_data)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_imgur(self, user : Union[User, str]):
        """Asynchronously retrieves the user's imgur data from the database

        Parameters
        ----------
            user : str or User
                The User to get the Imgur data of
        
        Returns
        -------
            dict
                The User's Imgur data
        """
        return await loop.run_in_executor(None, self.get_imgur_sync, user)
    
    async def set_imgur(self, user : Union[User, str], imgur_data):
        """Asynchronously sets the user's imgur data in the database

        Parameters
        ----------
            user : str or User
                The User to set the Imgur data for
            imgur_data : dict
                The User's Imgur data
        """
        await loop.run_in_executor(None, self.set_imgur_sync, user, imgur_data)
    
    # # # # # # # # # # # # # # #
    
    async def get_embed_color(self, user : Union[User, str]):
        """Asynchronously retrieves the user's embed color from the database

        Parameters
        ----------
            user : str or User
                The User to get the embed color of
        
        Returns
        -------
            dict
                The User's embed color
        """
        return await loop.run_in_executor(None, self.get_embed_color_sync, user)
    
    async def set_embed_color(self, user : Union[User, str], embed_color):
        """Asynchronously sets the user's embed color in the database

        Parameters
        ----------
            user : str or User
                The User to set the embed color for
            imgur_data : dict
                The User's embed color
        """
        await loop.run_in_executor(None, self.set_embed_color_sync, user, embed_color)