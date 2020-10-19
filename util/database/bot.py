from datetime import datetime
from discord import User
from typing import Union
from uuid import uuid4

from cogs.globals import loop

from util.misc import set_default
from util.string import datetime_to_string, datetime_to_dict


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class Bot:
    def __init__(self, bot):
        self._bot = bot

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Information Access Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_bot_sync(self) -> dict:
        """Synchronously retrieves the bot data stored in the database"""

        # Defaults
        data = {
            "_id": "bot_information",
            "developers": ["373317798430244864"],
            "testers": ["373317798430244864"],
            "owner": "373317798430244864",
            "updates": [],
            "pending_update": {},
            "changed_files": {},
            "tasks": [],
            "restart": {
                "send": False
            },
            "disabled_commands": [],
            "notifications": {
                "update": [],
                "new_feature": []
            }
        }

        # Get the bot data from the data base
        bot_data = self._bot.find_one({"_id": "bot_information"})
        if bot_data is None:
            self.set_bot_sync(data, insert=True)
            bot_data = self.get_bot_sync()
        bot_data = set_default(data, bot_data)
        return bot_data

    def set_bot_sync(self, bot_data, *, insert=False):
        """Synchronously updates the bot data stored in the database

        :param bot_data: A JSON object holding information about Omega Psi
        :param insert: Whether to insert or update data in the database
        """
        if insert:
            self._bot.insert_one(bot_data)
        else:
            self._bot.update_one(
                {"_id": "bot_information"},
                {"$set": bot_data},
                upsert=False)

    async def get_bot(self) -> dict:
        """Asynchronously retrieves the bot data stored in the database"""
        return await loop.run_in_executor(None, self.get_bot_sync)

    async def set_bot(self, bot_data, *, insert=False):
        """Synchronously updates the bot data stored in the database

        :param bot_data: A JSON object holding information about Omega Psi
        :param insert: Whether to insert or update data in the database
        """
        await loop.run_in_executor(None, self.set_bot_sync, bot_data)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_owner(self) -> str:
        """Retrieves the owner of Omega Psi's ID"""
        bot_data = await self.get_bot()
        return bot_data["owner"]

    async def get_restart(self) -> dict:
        """Retrieves the data when the restart command is used"""
        bot_data = await self.get_bot()
        return bot_data["restart"]

    async def set_restart(self, restart_data: dict):
        """Sets the data for when the restart command is used

        :param restart_data: A JSON object holding the data for restarting Omega Psi
        """
        bot_data = await self.get_bot()
        bot_data["restart"] = restart_data
        await self.set_bot(bot_data)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Developers Access Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_developers_sync(self) -> list:
        """Synchronously retrieves a list of developers of Omega Psi
        This will return a list of Discord IDs
        """
        bot_data = self.get_bot_sync()
        return bot_data["developers"]

    def set_developers_sync(self, developers: list):
        """Synchronously sets the list of developers of Omega Psi

        :param developers: A list of developer Discord IDs
        """
        bot_data = self.get_bot_sync()
        bot_data["developers"] = developers
        self.set_bot_sync(bot_data)

    def is_developer_sync(self, user: Union[User, str]) -> bool:
        """Synchronously tests whether or not the specified user is a developer of Omega Psi

        :param user: The Discord user or their ID
        """
        developers = self.get_developers_sync()
        if isinstance(user, str):
            return str(user) in developers
        return str(user.id) in developers

    def add_developer_sync(self, user: Union[User, str]):
        """Synchronously adds the specified user to the list of developers of Omega Psi

        :param user: The Discord user or their ID
        """
        developers = self.get_developers_sync()
        if not isinstance(user, str):
            user = str(user.id)
        developers.append(str(user))
        self.set_developers_sync(developers)

    def remove_developer_sync(self, user: Union[User, str]):
        """Synchronously removes the specified user from the list of developers of Omega Psi

        :param user: The Discord user or their ID
        """
        developers = self.get_developers_sync()
        if not isinstance(user, str):
            user = str(user.id)
        if str(user) in developers:
            developers.remove(str(user))
        self.set_developers_sync(developers)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_developers(self) -> list:
        """Asynchronously retrieves a list of developers of Omega Psi
        This will return a list of Discord IDs
        """
        return await loop.run_in_executor(None, self.get_developers_sync)

    async def set_developers(self, developers_data: list):
        """Asynchronously sets the list of developers of Omega Psi

        :param developers_data: A list of developer Discord IDs
        """
        await loop.run_in_executor(None, self.set_developers_sync, developers_data)

    async def is_developer(self, user: Union[User, str]) -> bool:
        """Asynchronously tests whether or not the specified user is a developer of Omega Psi

        :param user: The Discord user or their ID
        """
        return await loop.run_in_executor(None, self.is_developer_sync, user)

    async def add_developer(self, user: Union[User, str]):
        """Asynchronously adds the specified user to the list of developers of Omega Psi

        :param user: The Discord user or their ID
        """
        await loop.run_in_executor(None, self.add_developer_sync, user)

    async def remove_developer(self, user: Union[User, str]):
        """Asynchronously removes the specified user from the list of developers of Omega Psi

        :param user: The Discord user or their ID
        """
        await loop.run_in_executor(None, self.remove_developer_sync, user)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Testers Access Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_testers_sync(self) -> list:
        """Synchronously retrieves a list of testers of Omega Psi
        This will return a list of Discord IDs
        """
        bot_data = self.get_bot_sync()
        return bot_data["testers"]

    def set_testers_sync(self, testers: list):
        """Synchronously sets the list of testers of Omega Psi

        :param testers: A list of tester Discord IDs
        """
        bot_data = self.get_bot_sync()
        bot_data["testers"] = testers
        self.set_bot_sync(bot_data)

    def is_tester_sync(self, user: Union[User, str]) -> bool:
        """Synchronously tests whether or not the specified user is a tester of Omega Psi

        :param user: The Discord user or their ID
        """
        testers = self.get_testers_sync()
        if isinstance(user, str):
            return str(user) in testers
        return str(user.id) in testers

    def add_tester_sync(self, user: Union[User, str]):
        """Synchronously adds the specified user to the list of testers of Omega Psi

        :param user: The Discord user or their ID
        """
        testers = self.get_testers_sync()
        if not isinstance(user, str):
            user = str(user.id)
        testers.append(str(user))
        self.set_testers_sync(testers)

    def remove_tester_sync(self, user: Union[User, str]):
        """Synchronously removes the specified user from the list of testers of Omega Psi

        :param user: The Discord user or their ID
        """
        testers = self.get_testers_sync()
        if not isinstance(user, str):
            user = str(user.id)
        if str(user) in testers:
            testers.remove(str(user))
        self.set_testers_sync(testers)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_testers(self) -> list:
        """Asynchronously retrieves a list of testers of Omega Psi
        This will return a list of Discord IDs
        """
        return await loop.run_in_executor(None, self.get_testers_sync)

    async def set_testers(self, testers_data: list):
        """Asynchronously sets the list of testers of Omega Psi

        :param testers_data: A list of tester Discord IDs
        """
        await loop.run_in_executor(None, self.set_testers_sync, testers_data)

    async def is_tester(self, user: Union[User, str]) -> bool:
        """Asynchronously tests whether or not the specified user is a tester of Omega Psi

        :param user: The Discord user or their ID
        """
        return await loop.run_in_executor(None, self.is_tester_sync, user)

    async def add_tester(self, user: Union[User, str]):
        """Asynchronously adds the specified user to the list of testers of Omega Psi

        :param user: The Discord user or their ID
        """
        await loop.run_in_executor(None, self.add_tester_sync, user)

    async def remove_tester(self, user: Union[User, str]):
        """Asynchronously removes the specified user from the list of testers of Omega Psi

        :param user: The Discord user or their ID
        """
        await loop.run_in_executor(None, self.remove_tester_sync, user)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Updates / Pending Update Access Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_updates_sync(self) -> list:
        """Synchronously retrieves a list of updates made to Omega Psi

        :returns: A list of JSON object of updates of the following format:
            {
                "date": ____,
                "version": ____,
                "description": ____,
                "features": [
                    {
                        "feature": ____,
                        "type": ____
                    },
                    ... More Features ...
                ]
            }
        """
        bot_data = self.get_bot_sync()
        return bot_data["updates"]

    def set_updates_sync(self, updates: list):
        """Synchronously sets the list of updates made to Omega Psi

        :param updates: A list of JSON objects for updates made to Omega Psi
        """
        bot_data = self.get_bot_sync()
        bot_data["updates"] = updates
        self.set_bot_sync(bot_data)

    def get_recent_update_sync(self) -> dict:
        """Synchronously retrieves the most recent update made to Omega Psi"""
        updates = self.get_updates_sync()
        return updates[0]

    def get_pending_update_sync(self) -> dict:
        """Synchronously retrieves the pending update being made to Omega Psi"""
        bot_data = self.get_bot_sync()
        return bot_data["pending_update"]

    def set_pending_update_sync(self, pending_update: dict):
        """Synchronously sets the pending update being made to Omega Psi

        :param pending_update: A JSON object of the pending update to set
        """
        bot_data = self.get_bot_sync()
        bot_data["pending_update"] = pending_update
        self.set_bot_sync(bot_data)

    def create_pending_update_sync(self):
        """Synchronously creates a pending update to Omega Psi"""
        if self.get_pending_update_sync() == {}:
            self.set_pending_update_sync({
                "features": {}
            })

    def commit_pending_update_sync(self, version: str, description: str):
        """Synchronously commits and publishes the pending update as an update to Omega Psi

        :param version: The version of the update
        :param description: The description of the update
        """
        updates = self.get_updates_sync()
        features = self.get_pending_update_sync()["features"]
        current_date = datetime_to_string(datetime.now(), short=True)
        updates.insert(0, {
            "date": current_date,
            "version": version,
            "description": description,
            "features": [
                {
                    "feature": features[feature]["feature"],
                    "type": features[feature]["type"]
                }
                for feature in features
            ]
        })
        self.set_updates_sync(updates)
        self.set_pending_update_sync({})

    def add_pending_feature_sync(self, feature: str, feature_type: str) -> dict:
        """Synchronously adds a new pending feature to Omega Psi

        :param feature: The feature to add to the pending update
        :param feature_type: The type of feature that is being added to the pending update
        
        :returns: The JSON object of the created feature that contains the id,
            the feature, the feature type, and the datetime it was added
        """
        pending_update = self.get_pending_update_sync()
        uid = uuid4()
        feature_json = {
            "id": str(uid),
            "feature": feature,
            "type": feature_type,
            "datetime": datetime_to_dict(datetime.now())
        }
        pending_update["features"][str(uid)] = feature_json
        self.set_pending_update_sync(pending_update)
        return feature_json

    def edit_pending_feature_sync(self, feature_id: str, feature: str, feature_type: str) -> [dict, None]:
        """Synchronously edits the feature given in the pending update

        :param feature_id: The ID of the feature to edit
        :param feature: The new feature value
        :param feature_type: he new feature type value
            
        :returns: The JSON object of the resulting edit of the feature
            If None is returned, the feature_id was not found
        """
        pending_update = self.get_pending_update_sync()
        if feature_id in pending_update["features"]:
            pending_update["features"][feature_id].update(
                feature=feature,
                type=feature_type
            )
            self.set_pending_update_sync(pending_update)
            return pending_update["features"][feature_id]
        return None

    def remove_pending_feature_sync(self, feature_id: str) -> [dict, None]:
        """Synchronously removes the feature given from the pending update

        :param feature_id: The ID of the feature to remove
            
        :returns: The JSON object of the removed feature
            If None is returned, the feature_id was not found
        """
        pending_update = self.get_pending_update_sync()
        if feature_id in pending_update["features"]:
            feature_json = pending_update["features"].pop(feature_id)
            self.set_pending_update_sync(pending_update)
            return feature_json
        return None

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_updates(self) -> list:
        """Asynchronously retrieves a list of updates made to Omega Psi

        :returns: A list of JSON object of updates of the following format:
            {
                "date": ____,
                "version": ____,
                "description": ____,
                "features": [
                    {
                        "feature": ____,
                        "type": ____
                    },
                    ... More Features ...
                ]
            }
        """
        return await loop.run_in_executor(None, self.get_updates_sync)

    async def set_updates(self, updates_data: dict):
        """Asynchronously sets the list of updates made to Omega Psi

        :param updates: A list of JSON objects for updates made to Omega Psi
        """
        await loop.run_in_executor(None, self.set_updates_sync, updates_data)

    async def get_recent_update(self) -> dict:
        """Asynchronously retrieves the most recent update made to Omega Psi"""
        return await loop.run_in_executor(None, self.get_recent_update_sync)

    async def get_pending_update(self) -> dict:
        """Asynchronously retrieves the pending update being made to Omega Psi"""
        return await loop.run_in_executor(None, self.get_pending_update_sync)

    async def set_pending_update(self, pending_update_data: dict):
        """Asynchronously sets the pending update being made to Omega Psi

        :param pending_update: A JSON object of the pending update to set
        """
        await loop.run_in_executor(None, self.set_pending_update_sync, pending_update_data)

    async def create_pending_update(self):
        """Asynchronously creates a pending update to Omega Psi"""
        await loop.run_in_executor(None, self.create_pending_update_sync)

    async def commit_pending_update(self, version: str, description: str):
        """Asynchronously commits and publishes the pending update as an update to Omega Psi

        :param version: The version of the update
        :param description: The description of the update
        """
        await loop.run_in_executor(None, self.commit_pending_update_sync, version, description)

    async def add_pending_feature(self, feature: str, feature_type: str):
        """Asynchronously adds a new pending feature to Omega Psi

        :param feature: The feature to add to the pending update
        :param feature_type: The type of feature that is being added to the pending update
        
        :returns: The JSON object of the created feature that contains the id,
            the feature, the feature type, and the datetime it was added
        """
        await loop.run_in_executor(None, self.add_pending_feature_sync, feature, feature_type)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Tasks Access Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_tasks_sync(self) -> dict:
        """Synchronously retrieves the task list from the database"""
        bot_data = self.get_bot_sync()
        return bot_data["tasks"]

    def set_tasks_sync(self, tasks: dict):
        """Synchronously sets the task list in the database

        :param tasks: A JSON object for tasks to set in the database
        """
        bot_data = self.get_bot_sync()
        bot_data["tasks"] = tasks
        self.set_bot_sync(bot_data)

    def add_task_sync(self, task: str) -> dict:
        """Synchronously adds a new task to the task list

        :param task: The task to add to the database

        :returns: A JSON object of the task and an ID for the task
        """
        tasks = self.get_tasks_sync()
        uid = uuid4()
        tasks[str(uid)] = task
        self.set_tasks_sync(tasks)
        return {
            "task": task,
            "id": str(uid)
        }

    def edit_task_sync(self, task_id: str, task: str) -> [dict, None]:
        """Synchronously edits a task in the task list

        :param task_id: The ID of the task to edit
        :param task: The new task value
        
        :returns: The resulting task edit
            If None is returned, the task was not found
        """
        tasks = self.get_tasks_sync()
        if task_id in tasks:
            tasks[task_id] = task
            self.set_tasks_sync(tasks)
            return {
                "task": task,
                "id": task_id
            }
        return None

    def remove_task_sync(self, task_id: str) -> [dict, None]:
        """Synchronously removes a task from the task list

        :param task_id: The ID of the task to remove
        
        :returns: The removed task
            If None is returned, the task was not found
        """
        tasks = self.get_tasks_sync()
        if task_id in tasks:
            task = tasks.pop(task_id)
            self.set_tasks_sync(tasks)
            return {
                "task": task,
                "id": task_id
            }
        return None

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_tasks(self) -> dict:
        """Asynchronously retrieves the task list from the database"""
        return await loop.run_in_executor(None, self.get_tasks_sync)

    async def set_tasks(self, tasks_data: dict):
        """Asynchronously sets the task list in the database

        :param tasks: A JSON object for tasks to set in the database
        """
        await loop.run_in_executor(None, self.set_tasks_sync, tasks_data)

    async def add_task(self, task: str) -> dict:
        """Asynchronously adds a new task to the task list

        :param task: The task to add to the database

        :returns: A JSON object of the task and an ID for the task
        """
        return await loop.run_in_executor(None, self.add_task_sync, task)

    async def remove_task(self, task_id: str) -> [dict, None]:
        """Asynchronously removes a task from the task list

        :param task_id: The ID of the task to remove
        
        :returns: The removed task
            If None is returned, the task was not found
        """
        return await loop.run_in_executor(None, self.remove_task_sync, task_id)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Invocation Access Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_disabled_commands_sync(self):
        """Synchronously returns a list of disabled commands in the entire bot

        Returns
        -------
            list
                A list of disabled commands in the entire bot
        """
        bot_data = self.get_bot_sync()
        return bot_data["disabled_commands"]

    def is_command_enabled_sync(self, command_name):
        """Synchronously returns whether or not the specified command is enabled

        Parameters
        ----------
            command_name : str
                The name of the command to check if it's enabled
        
        Returns
        -------
            bool
                Whether or not the command is enabled
        """
        bot_data = self.get_bot_sync()
        return command_name not in bot_data["disabled_commands"]

    def enable_command_sync(self, command_name):
        """Synchronously enables the specified command

        Parameters
        ----------
            command_name : str
                The command to enable
        
        Returns
        -------
            bool
                Whether or not the command was enabled
        """
        bot_data = self.get_bot_sync()
        if command_name in bot_data["disabled_commands"]:
            bot_data["disabled_commands"].remove(command_name)
            self.set_bot_sync(bot_data)
            return True
        return False

    def disable_command_sync(self, command_name):
        """Synchronously disables the specified command

        Parameters
        ----------
            command_name : str
                The command to disable
        
        Returns
        -------
            bool
                Whether or not the command was disabled
        """
        bot_data = self.get_bot_sync()
        if command_name not in bot_data["disabled_commands"]:
            bot_data["disabled_commands"].append(command_name)
            self.set_bot_sync(bot_data)
            return True
        return False

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_disabled_commands(self):
        """Asynchronously returns a list of disabled commands in the entire bot

        Returns
        -------
            list
                A list of disabled commands in the entire bot
        """
        return await loop.run_in_executor(None, self.get_disabled_commands_sync)

    async def is_command_enabled(self, command_name):
        """Asynchronously returns whether or not the specified command is enabled

        Parameters
        ----------
            command_name : str
                The name of the command to check if it's enabled
        
        Returns
        -------
            bool
                Whether or not the command is enabled
        """
        return await loop.run_in_executor(None, self.is_command_enabled_sync, command_name)

    async def enable_command(self, command_name):
        """Asynchronously enables the specified command

        Parameters
        ----------
            command_name : str
                The command to enable
        
        Returns
        -------
            bool
                Whether or not the command was enabled
        """
        return await loop.run_in_executor(None, self.enable_command_sync, command_name)

    async def disable_command(self, command_name):
        """Asynchronously disables the specified command

        Parameters
        ----------
            command_name : str
                The command to disable
        
        Returns
        -------
            bool
                Whether or not the command was disabled
        """
        return await loop.run_in_executor(None, self.disable_command_sync, command_name)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Notifications Access Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_notifications_sync(self):
        """Synchronously retrieves the notification data for the bot

        Returns
        -------
            dict
                The notification data for the bot
        """
        bot_data = self.get_bot_sync()
        return bot_data["notifications"]

    def set_notification_sync(self, notification_data):
        """Synchronously sets the notification data for the bot

        Parameters
        ----------
            notification_data : dict
                The notification data for the bot
        """
        bot_data = self.get_bot_sync()
        bot_data["notifications"] = notification_data
        self.set_bot_sync(bot_data)

    def manage_notifications_sync(self, target, user: Union[User, str], add):
        """Synchronously manages notifications in the bot

        Parameters
        ----------
            target : str
                Which notification to manage
            user : str or User
                The user to add or remove from the specified notification
            add : boolean
                Whether or not to add the user to the specified notification
        """
        notification_data = self.get_notifications_sync()
        user = user if isinstance(user, str) else str(user.id)
        if add and user not in notification_data[target]:
            notification_data[target].append(user)
        elif not add and user in notification_data[target]:
            notification_data[target].remove(user)
        self.set_notification_sync(notification_data)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_notifications(self):
        """Asynchronously retrieves the notification data for the bot

        Returns
        -------
            dict
                The notification data for the bot
        """
        return await loop.run_in_executor(None, self.get_notifications_sync)

    async def set_notification(self, notification_data):
        """Asynchronously sets the notification data for the bot

        Parameters
        ----------
            notification_data : dict
                The notification data for the bot
        """
        await loop.run_in_executor(None, self.set_notification_sync, notification_data)

    async def manage_notifications(self, target, user: Union[User, str], add):
        """Asynchronously manages notifications in the bot

        Parameters
        ----------
            target : str
                Which notification to manage
            user : str or User
                The user to add or remove from the specified notification
            add : boolean
                Whether or not to add the user to the specified notification
        """
        await loop.run_in_executor(None, self.manage_notifications_sync, target, user, add)
