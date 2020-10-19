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

    def get_users(self):
        """Synchronously retrieves all the users from the database

        Returns
        -------
            list
                A list of users
        """
        users = list(self._users.find({}))
        return users

    def get_user_sync(self, user: Union[User, str]):
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
            "notifications": {
                "update": {
                    "active": False
                },
                "new_feature": {
                    "active": False
                }
            },
            "minigames": {
                "battleship": {
                    "won": 0,
                    "lost": 0
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
                },
                "mastermind": {
                    "won": 0,
                    "lost": 0
                }
            }
        }

        # Get user data
        user_data = self._users.find_one({"_id": user_id})
        if user_data is None:
            self.set_user_sync(user_id, data, insert=True)
            user_data = self.get_user_sync(user_id)
        user_data = set_default(data, user_data)
        return user_data

    def set_user_sync(self, user: Union[User, str], user_data, *, insert=False):
        """Synchronously sets user data from the database

        Parameters
        ----------
            user : str or User
        """
        user_id = user if isinstance(user, str) else str(user.id)
        if insert:
            self._users.insert_one(user_data)
        else:
            self._users.update_one(
                {"_id": user_id},
                {"$set": user_data},
                upsert=False)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_user(self, user: Union[User, str]):
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

    async def set_user(self, user: Union[User, str], user_data):
        """Asynchronously sets user data from the database

        Parameters
        ----------
            user : str or User
        """
        await loop.run_in_executor(None, self.set_user_sync, user, user_data)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # IFTTT Access Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_ifttt_sync(self, user: Union[User, str]):
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

    def set_ifttt_sync(self, user: Union[User, str], ifttt_data):
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

    def is_ifttt_active_sync(self, user: Union[User, str]):
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

    def toggle_ifttt_sync(self, user: Union[User, str]):
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

    async def get_ifttt(self, user: Union[User, str]):
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

    async def set_ifttt(self, user: Union[User, str], ifttt_data):
        """Asynchronously sets the user's IFTTT data in the database

        Parameters
        ----------
            user : str or User
                The User to set the IFTTT data for
            ifttt_data : dict
                The JSON object of the user's IFTTT data
        """
        await loop.run_in_executor(None, self.set_ifttt_sync, user, ifttt_data)

    async def is_ifttt_active(self, user: Union[User, str]):
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

    async def toggle_ifttt(self, user: Union[User, str]):
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
    # Notification Access Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_notifications_sync(self, user: Union[User, str]):
        """Synchronously retrieves the user's notification data

        Parameters
        ----------
            user : str or User
                The User to get the notification data of
        
        Returns
        -------
            dict
                The User's notification data
        """
        user_data = self.get_user_sync(user)
        return user_data["notifications"]

    def set_notifications_sync(self, user: Union[User, str], notification_data):
        """Synchronously sets the user's notification data

        Parameters
        ----------
            user : str or User
                The User to set the notification data of
            notification_data : dict
                The JSON object of the User's notification data
        """
        user_data = self.get_user_sync(user)
        user_data["notifications"] = notification_data
        self.set_user_sync(user, user_data)

    # # # # # # # # # # # # # # #

    def get_update_notification_sync(self, user: Union[User, str]):
        """Synchronously retrieves the user's update notification data

        Parameters
        ----------
            user : str or User
                The User to get the update notification data of
        
        Returns
        -------
            dict
                The User's update notification data
        """
        notification_data = self.get_notifications_sync(user)
        return notification_data["update"]

    def set_update_notification_sync(self, user: Union[User, str], update_notification_data):
        """Synchronously sets the user's update notification data

        Parameters
        ----------
            user : str or User
                The User to set the update notification data of
            update_notification_data : dict
                The JSON object of the User's update notification data
        """
        notification_data = self.get_notifications_sync(user)
        notification_data["update"] = update_notification_data
        self.set_notifications_sync(user, notification_data)

    def is_update_notification_active_sync(self, user: Union[User, str]):
        """Synchronously retrieves whether or not the user's update notifications are active

        Parameters
        ----------
            user : str or User
                The User to get the status of the user's update notification
        
        Returns
        -------
            boolean
                Whether or not the User's update notification is active
        """
        update_notification_data = self.get_update_notification_sync(user)
        return update_notification_data["active"]

    def toggle_update_notification_sync(self, user: Union[User, str], is_active=None):
        """Synchronously toggles the status of the user's update notifications

        Parameters
        ----------
            user : str or User
                The User to toggle the status of the user's update notification
            is_active : boolean
                The active status to manually set the user's update notification
                Note that if this is ignored (set to None), the user's update notification will be toggled
                    like normal
        
        Returns
        -------
            boolean
                Whether the User's update notification has been activated or not
        """
        update_notification_data = self.get_update_notification_sync(user)
        update_notification_data["active"] = not update_notification_data["active"] if is_active is None else is_active
        self.set_update_notification_sync(user, update_notification_data)
        return update_notification_data["active"]

    # # # # # # # # # # # # # # #

    def get_new_feature_notification_sync(self, user: Union[User, str]):
        """Synchronously retrieves the user's new feature notification data

        Parameters
        ----------
            user : str or User
                The User to get the new feature notification data of
        
        Returns
        -------
            dict
                The User's new feature notification data
        """
        notification_data = self.get_notifications_sync(user)
        return notification_data["new_feature"]

    def set_new_feature_notification_sync(self, user: Union[User, str], new_feature_notification_data):
        """Synchronously sets the user's new feature notification data

        Parameters
        ----------
            user : str or User
                The User to set the new feature notification data of
            new_feature_notification_data : dict
                The JSON object of the User's new feature notification data
        """
        notification_data = self.get_notifications_sync(user)
        notification_data["new_feature"] = new_feature_notification_data
        self.set_notifications_sync(user, notification_data)

    def is_new_feature_notification_active_sync(self, user: Union[User, str]):
        """Synchronously retrieves whether or not the user's new feature notifications are active

        Parameters
        ----------
            user : str or User
                The User to get the status of the user's new feature notification
        
        Returns
        -------
            boolean
                Whether or not the User's new feature notification is active
        """
        new_feature_notification_data = self.get_new_feature_notification_sync(user)
        return new_feature_notification_data["active"]

    def toggle_new_feature_notification_sync(self, user: Union[User, str], is_active=None):
        """Synchronously toggles the status of the user's new feature notifications

        Parameters
        ----------
            user : str or User
                The User to toggle the status of the user's new feature notification
            is_active : boolean
                The active status to manually set the user's new feature notification
                Note that if this is ignored (set to None), the user's new feature notification will be toggled
                    like normal
        
        Returns
        -------
            boolean
                Whether the User's new feature notification has been activated or not
        """
        new_feature_notification_data = self.get_new_feature_notification_sync(user)
        new_feature_notification_data["active"] = not new_feature_notification_data[
            "active"] if is_active is None else is_active
        self.set_new_feature_notification_sync(user, new_feature_notification_data)
        return new_feature_notification_data["active"]

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_notifications(self, user: Union[User, str]):
        """Asynchronously retrieves the user's notification data

        Parameters
        ----------
            user : str or User
                The User to get the notification data of
        
        Returns
        -------
            dict
                The User's notification data
        """
        return await loop.run_in_executor(None, self.get_notifications_sync, user)

    async def set_notifications(self, user: Union[User, str], notification_data):
        """Asynchronously sets the user's notification data

        Parameters
        ----------
            user : str or User
                The User to set the notification data of
            notification_data : dict
                The JSON object of the User's notification data
        """
        await loop.run_in_executor(None, self.set_notifications_sync, user, notification_data)

    # # # # # # # # # # # # # # #

    async def get_update_notification(self, user: Union[User, str]):
        """Asynchronously retrieves the user's update notification data

        Parameters
        ----------
            user : str or User
                The User to get the update notification data of
        
        Returns
        -------
            dict
                The User's update notification data
        """
        return await loop.run_in_executor(None, self.get_update_notification_sync, user)

    async def set_update_notification(self, user: Union[User, str], update_notification_data):
        """Asynchronously sets the user's update notification data

        Parameters
        ----------
            user : str or User
                The User to set the update notification data of
            update_notification_data : dict
                The JSON object of the User's update notification data
        """
        await loop.run_in_executor(None, self.set_update_notification_sync, user, update_notification_data)

    async def is_update_notification_active(self, user: Union[User, str]):
        """Asynchronously retrieves whether or not the user's update notifications are active

        Parameters
        ----------
            user : str or User
                The User to get the status of the user's update notification
        
        Returns
        -------
            boolean
                Whether or not the User's update notification is active
        """
        return await loop.run_in_executor(None, self.is_update_notification_active_sync, user)

    async def toggle_update_notification(self, user: Union[User, str]):
        """Asynchronously toggles the status of the user's update notifications

        Parameters
        ----------
            user : str or User
                The User to toggle the status of the user's update notification
        
        Returns
        -------
            boolean
                Whether the User's update notification has been activated or not
        """
        return await loop.run_in_executor(None, self.toggle_update_notification_sync, user)

    # # # # # # # # # # # # # # #

    async def get_new_feature_notification(self, user: Union[User, str]):
        """Asynchronously retrieves the user's new feature notification data

        Parameters
        ----------
            user : str or User
                The User to get the new feature notification data of
        
        Returns
        -------
            dict
                The User's new feature notification data
        """
        return await loop.run_in_executor(None, self.get_new_feature_notification_sync, user)

    async def set_new_feature_notification(self, user: Union[User, str], new_feature_notification_data):
        """Asynchronously sets the user's new feature notification data

        Parameters
        ----------
            user : str or User
                The User to set the new feature notification data of
            new_feature_notification_data : dict
                The JSON object of the User's new feature notification data
        """
        await loop.run_in_executor(None, self.set_new_feature_notification_sync, user, new_feature_notification_data)

    async def is_new_feature_notification_active(self, user: Union[User, str]):
        """Asynchronously retrieves whether or not the user's new feature notifications are active

        Parameters
        ----------
            user : str or User
                The User to get the status of the user's new feature notification
        
        Returns
        -------
            boolean
                Whether or not the User's new feature notification is active
        """
        return await loop.run_in_executor(None, self.is_new_feature_notification_active_sync, user)

    async def toggle_new_feature_notification(self, user: Union[User, str]):
        """Asynchronously toggles the status of the user's new feature notifications

        Parameters
        ----------
            user : str or User
                The User to toggle the status of the user's new feature notification
        
        Returns
        -------
            boolean
                Whether the User's new feature notification has been activated or not
        """
        return await loop.run_in_executor(None, self.toggle_new_feature_notification_sync, user)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Minigame Access Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_minigame_data_sync(self, user: Union[User, str]):
        """Synchronously retrieves the user's minigame data from the database

        Parameters
        ----------
            user : str or User
                The User to get the minigame data of
        
        Returns
        -------
            dict
                The User's minigame data
        """
        user_data = self.get_user_sync(user)
        return user_data["minigames"]

    def get_battleship_sync(self, user: Union[User, str]):
        """Synchronously retrieves the user's battleship data from the database

        Parameters
        ----------
            user : str or User
                The User to get the Battleship data of
        
        Returns
        -------
            dict
                The User's Battleship data
        """
        user_data = self.get_user_sync(user)
        return user_data["minigames"]["battleship"]

    def get_connect_four_sync(self, user: Union[User, str]):
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
        return user_data["minigames"]["connect_four"]

    def get_tic_tac_toe_sync(self, user: Union[User, str]):
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
        return user_data["minigames"]["tic_tac_toe"]

    def get_game_of_life_sync(self, user: Union[User, str]):
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
        return user_data["minigames"]["game_of_life"]

    def get_omok_sync(self, user: Union[User, str]):
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
        return user_data["minigames"]["omok"]

    def get_mastermind_sync(self, user: Union[User, str]):
        """Synchronously retrieves the user's mastermind data from the database

        Parameters
        ----------
            user : str or User
                The User to get the Mastermind data of
            
        Returns
        -------
            dict
                The User's Mastermind data
        """
        user_data = self.get_user_sync(user)
        return user_data["minigames"]["mastermind"]

    # # # # # # # # # # # # # # #

    def update_battleship_sync(self, user: Union[User, str], won):
        """Synchronously updates the user's battleship data in the database

        Parameters
        ----------
            user : str or User
                The User to update the Battleship data of
            won : boolean
                Whether or not the User won
        """
        user_data = self.get_user_sync(user)
        user_data["minigames"]["battleship"]["won" if won else "lost"] += 1
        self.set_user_sync(user, user_data)

    def update_connect_four_sync(self, user: Union[User, str], won):
        """Synchronously updates the user's connect four data in the database

        Parameters
        ----------
            user : str or User
                The User to update the Connect Four data of
            won : boolean
                Whether or not the User won
        """
        user_data = self.get_user_sync(user)
        user_data["minigames"]["connect_four"]["won" if won else "lost"] += 1
        self.set_user_sync(user, user_data)

    def update_tic_tac_toe_sync(self, user: Union[User, str], won):
        """Synchronously updates the user's tic tac toe data in the database

        Parameters
        ----------
            user : str or User
                The User to update the Tic Tac Toe data of
            won : boolean
                Whether or not the User won
        """
        user_data = self.get_user_sync(user)
        user_data["minigames"]["tic_tac_toe"]["won" if won else "lost"] += 1
        self.set_user_sync(user, user_data)

    def update_game_of_life_sync(self, user: Union[User, str], won):
        """Synchronously updates the user's game of life data in the database

        Parameters
        ----------
            user : str or User
                The User to update the Game of Life data of
            won : boolean
                Whether or not the User won
        """
        user_data = self.get_user_sync(user)
        user_data["minigames"]["game_of_life"]["won" if won else "lost"] += 1
        self.set_user_sync(user, user_data)

    def update_omok_sync(self, user: Union[User, str], won):
        """Synchronously updates the user's omok data in the database

        Parameters
        ----------
            user : str or User
                The User to update the Omok data of
            won : boolean
                Whether or not the User won
        """
        user_data = self.get_user_sync(user)
        user_data["minigames"]["omok"]["won" if won else "lost"] += 1
        self.set_user_sync(user, user_data)

    def update_mastermind_sync(self, user: Union[User, str], won):
        """Synchronously updates the user's mastermind data in the database

        Parameters
        ----------
            user : str or User
                The User to update the Mastermind data of
            won : boolean
                Whether or not the User won
        """
        user_data = self.get_user_sync(user)
        user_data["minigames"]["mastermind"]["won" if won else "lost"] += 1
        self.set_user_sync(user, user_data)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_minigame_data(self, user: Union[User, str]):
        """Asynchronously retrieves the user's minigame data from the database

        Parameters
        ----------
            user : str or User
                The User to get the minigame data of
        
        Returns
        -------
            dict
                The User's minigame data
        """
        return await loop.run_in_executor(None, self.get_minigame_data_sync, user)

    async def get_battleship(self, user: Union[User, str]):
        """Asynchronously retrieves the user's battleship data from the database

        Parameters
        ----------
            user : str or User
                The User to get the Battleship data of
        
        Returns
        -------
            dict
                The User's Battleship data
        """
        return await loop.run_in_executor(None, self.get_battleship_sync, user)

    async def get_connect_four(self, user: Union[User, str]):
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

    async def get_tic_tac_toe(self, user: Union[User, str]):
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

    async def get_game_of_life(self, user: Union[User, str]):
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

    async def get_omok(self, user: Union[User, str]):
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

    async def get_mastermind(self, user: Union[User, str]):
        """Asynchronously retrieves the user's mastermind data from the database

        Parameters
        ----------
            user : str or User
                The User to get the Mastermind data of
            
        Returns
        -------
            dict
                The User's Mastermind data
        """
        return await loop.run_in_executor(None, self.get_mastermind_sync, user)

    # # # # # # # # # # # # # # #

    async def update_battleship(self, user: Union[User, str], won):
        """Asynchronously updates the user's battleship data in the database

        Parameters
        ----------
            user : str or User
                The User to update the Battleship data of
            won : boolean
                Whether or not the User won
        """
        await loop.run_in_executor(None, self.update_battleship_sync, user, won)

    async def update_connect_four(self, user: Union[User, str], won):
        """Asynchronously updates the user's connect four data in the database

        Parameters
        ----------
            user : str or User
                The User to update the Connect Four data of
            won : boolean
                Whether or not the User won
        """
        await loop.run_in_executor(None, self.update_connect_four_sync, user, won)

    async def update_tic_tac_toe(self, user: Union[User, str], won):
        """Asynchronously updates the user's tic tac toe data in the database

        Parameters
        ----------
            user : str or User
                The User to update the Tic Tac Toe data of
            won : boolean
                Whether or not the User won
        """
        await loop.run_in_executor(None, self.update_tic_tac_toe_sync, user, won)

    async def update_game_of_life(self, user: Union[User, str], won):
        """Asynchronously updates the user's game of life data in the database

        Parameters
        ----------
            user : str or User
                The User to update the Game of Life data of
            won : boolean
                Whether or not the User won
        """
        await loop.run_in_executor(None, self.update_game_of_life_sync, user, won)

    async def update_omok(self, user: Union[User, str], won):
        """Asynchronously updates the user's omok data in the database

        Parameters
        ----------
            user : str or User
                The User to update the Omok data of
            won : boolean
                Whether or not the User won
        """
        await loop.run_in_executor(None, self.update_omok_sync, user, won)

    async def update_mastermind(self, user: Union[User, str], won):
        """Asynchronously updates the user's mastermind data in the database

        Parameters
        ----------
            user : str or User
                The User to update the Mastermind data of
            won : boolean
                Whether or not the User won
        """
        await loop.run_in_executor(None, self.update_mastermind_sync, user, won)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Card Game Access Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_cards_against_humanity_sync(self: Union[User, str], user):
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
        return user_data["minigames"]["cards_against_humanity"]

    def get_uno_sync(self: Union[User, str], user):
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
        return user_data["minigames"]["uno"]

    # # # # # # # # # # # # # # #

    def update_cards_against_humanity_sync(self, user: Union[User, str], won):
        """Synchronously updates the cards against humanity data in the database

        Parameters
        ----------
            user : str or User
                The User to get update the Cards Against Humanity data for
            won : boolean
                Whether or not the User won
        """
        user_data = self.get_user_sync(user)
        user_data["minigames"]["cards_against_humanity"]["won" if won else "lost"] += 1
        self.set_user_sync(user, user_data)

    def update_uno_sync(self, user: Union[User, str], won):
        """Synchronously updates the user's uno data in the database

        Parameters
        ----------
            user : str or User
                The User to get update the Uno data for
            won : boolean
                Whether or not the User won
        """
        user_data = self.get_user_sync(user)
        user_data["minigames"]["uno"]["won" if won else "lost"] += 1
        self.set_user_sync(user, user_data)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_cards_against_humanity(self, user: Union[User, str]):
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

    async def get_uno(self, user: Union[User, str]):
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

    async def update_cards_against_humanity(self, user: Union[User, str], won):
        """Asynchronously updates the cards against humanity data in the database

        Parameters
        ----------
            user : str or User
                The User to get update the Cards Against Humanity data for
            won : boolean
                Whether or not the User won
        """
        await loop.run_in_executor(None, self.update_cards_against_humanity_sync, user, won)

    async def update_uno(self, user: Union[User, str], won):
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

    def get_imgur_sync(self, user: Union[User, str]):
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

    def set_imgur_sync(self, user: Union[User, str], imgur_data):
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

    def get_embed_color_sync(self, user: Union[User, str]):
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

    def set_embed_color_sync(self, user: Union[User, str], embed_color):
        """Synchronously sets the user's embed color in the database

        Parameters
        ----------
            user : str or User
                The User to set the embed color for
            embed_color:
        """
        user_data = self.get_user_sync(user)
        user_data["embed_color"] = embed_color
        self.set_user_sync(user, user_data)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_imgur(self, user: Union[User, str]):
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

    async def set_imgur(self, user: Union[User, str], imgur_data):
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

    async def get_embed_color(self, user: Union[User, str]):
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

    async def set_embed_color(self, user: Union[User, str], embed_color):
        """Asynchronously sets the user's embed color in the database

        Parameters
        ----------
            user : str or User
                The User to set the embed color for
            embed_color:
        """
        await loop.run_in_executor(None, self.set_embed_color_sync, user, embed_color)
