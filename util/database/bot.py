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

    def get_bot_sync(self):
        """Synchronously retrieves the bot data stored in the database

        Returns
        -------
            dict
                The bot data
        """

        # Defaults
        data = {
            "developers": ["373317798430244864"],
            "owner": "373317798430244864",
            "updates": [],
            "pending_update": {},
            "changed_files": {},
            "tasks": [],
            "restart": {
                "send": False
            },
            "commands_run": {},
            "disabled_commands": []
        }

        # Get the bot data from the data base
        bot_data = self._bot.find_one({"_id": "bot_information"})
        if not bot_data:
            self._bot.insert_one({"_id": "bot_information"})
            self.set_bot_sync(data)
            data = bot_data
        
        # Set defaults
        bot_data = set_default(data, bot_data)
        return bot_data
    
    def set_bot_sync(self, bot_data):
        """Synchronously updates the bot data stored in the database

        Parameters
        ----------
            bot_data : dict
                A JSON object holding information about Omega Psi
        """
        self._bot.update_one(
            {"_id": "bot_information"},
            {"$set": bot_data},
            upsert = False
        )
    
    async def get_bot(self):
        """Asynchronously retrieves the bot data stored in the database

        Returns
        -------
            dict
                The bot data
        """
        return await loop.run_in_executor(None, self.get_bot_sync)
    
    async def set_bot(self, bot_data):
        """Synchronously updates the bot data stored in the database

        Parameters
        ----------
            bot_data : dict
                A JSON object holding information about Omega Psi
        """
        await loop.run_in_executor(None, self.set_bot_sync, bot_data)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_owner(self):
        """Retrieves the owner of Omega Psi
        
        Returns
        -------
            str
                The owner's Discord ID
        """
        bot_data = await self.get_bot()
        return bot_data["owner"]
    
    async def get_restart(self):
        """Retrieves the data when the restart command is used

        Returns
        -------
            dict
                The restart data
        """
        bot_data = await self.get_bot()
        return bot_data["restart"]
    
    async def set_restart(self, restart_data):
        """Sets the data for when the restart command is used

        Parameters
        ----------
            restart_data : dict
                A JSON object holding the data for restarting Omega Psi
        """
        bot_data = await self.get_bot()
        bot_data["restart"] = restart_data
        await self.set_bot(bot_data)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Developers Access Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_developers_sync(self):
        """Synchronously retrieves a list of developers of Omega Psi

        Returns
        -------
            list
                A list of developer Discord IDs
        """
        bot_data = self.get_bot_sync()
        return bot_data["developers"]
    
    def set_developers_sync(self, developers):
        """Synchronously sets the list of developers of Omega Psi

        Parameters
        ----------
            developers_data : str[]
                A list of developer Discord IDs
        """
        bot_data = self.get_bot_sync()
        bot_data["developers"] = developers
        self.set_bot_sync(bot_data)
    
    def is_developer_sync(self, user : Union[User, str]):
        """Synchronously tests whether or not the specified user is a developer of Omega Psi

        Parameters
        ----------
            user : discord.User, str
                The Discord user or their Discord ID
        """
        developers = self.get_developers_sync()
        if isinstance(user, str):
            return str(user) in developers
        return str(user.id) in developers
    
    def add_developer_sync(self, user : Union[User, str]):
        """Synchronously adds the specified user to the list of developers of Omega Psi

        Parameters
        ----------
            user : discord.User, str
                The Discord user or their Discord ID
        """
        developers = self.get_developers_sync()
        if not isinstance(user, str):
            user = str(user.id)
        developers.append(str(user))
        self.set_developers_sync(developers)
    
    def remove_developer_sync(self, user : Union[User, str]):
        """Synchronously removes the specified user from the list of developers of Omega Psi

        Parameters
        ----------
            user : discord.User, str
                The Discord user or their Discord ID
        """
        developers = self.get_developers_sync()
        if not isinstance(user, str):
            user = str(user.id)
        if str(user) in developers:
            developers.remove(str(user))
        self.set_developers_sync(developers)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_developers(self):
        """Asynchronously retrieves a list of developers of Omega Psi
        
        Returns
        -------
            list
                A list of developer Discord IDs
        """
        return await loop.run_in_executor(None, self.get_developers_sync)
    
    async def set_developers(self, developers_data):
        """Asynchronously sets the list of developers of Omega Psi

        Parameters
        ----------
            developers_data : list
                A list of developer Discord IDs
        """
        await loop.run_in_executor(None, self.set_developers_sync, developers_data)
    
    async def is_developer(self, user : Union[User, str]):
        """Asynchronously tests whether or not the specified user is a developer of Omega Psi

        Parameters
        ----------
            user : discord.User, str
                The Discord user or their Discord ID
        """
        return await loop.run_in_executor(None, self.is_developer_sync, user)
    
    async def add_developer(self, user : Union[User, str]):
        """Asynchronously adds the specified user to the list of developers of Omega Psi

        Parameters
        ----------
            user : discord.User, str
                The Discord user or their Discord ID
        """
        await loop.run_in_executor(None, self.add_developer_sync, user)
    
    async def remove_developer(self, user : Union[User, str]):
        """Asynchronously removes the specified user from the list of developers of Omega Psi

        Parameters
        ----------
            user : discord.User, str
                The Discord user or their Discord ID
        """
        await loop.run_in_executor(None, self.remove_developer_sync, user)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Updates / Pending Update Access Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    def get_updates_sync(self):
        """Synchronously retrieves a list of updates made to Omega Psi

        Returns
        -------
            list
                A list of JSON objects of updates made to Omega Psi
        """
        bot_data = self.get_bot_sync()
        return bot_data["updates"]
    
    def set_updates_sync(self, updates):
        """Synchronously sets the list of updates made to Omega Psi

        Parameters
        ----------
            updates : list
                A list of JSON object of updates made to Omega Psi
        """
        bot_data = self.get_bot_sync()
        bot_data["updates"] = updates
        self.set_bot_sync(bot_data)
    
    def get_recent_update_sync(self):
        """Synchronously retrieves the most recent update made to Omega Psi

        Returns
        -------
            dict
                A JSON object of the most recent update made to Omega Psi
        """
        updates = self.get_updates_sync()
        return updates[0]
    
    def get_pending_update_sync(self):
        """Synchronously retrieves the pending update being made to Omega Psi

        Returns
        -------
            dict
                A JSON object of the current pending update being made to Omega Psi
        """
        bot_data = self.get_bot_sync()
        return bot_data["pending_update"]
    
    def set_pending_update_sync(self, pending_update):
        """Synchronously sets the pending update being made to Omega Psi

        Parameters
        ----------
            pending_update : dict
                A JSON object of the pending update to set
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
        
    def commit_pending_update_sync(self, version, description):
        """Synchronously commits and publishes the pending update as an update to Omega Psi

        Parameters
        ----------
            version : str
                The version of the update
            description : str
                The description of the update
        """
        updates = self.get_updates_sync()
        features = self.get_pending_update_sync()["features"]
        current_date = datetime_to_string(datetime.now(), short = True)
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
    
    def add_pending_feature_sync(self, feature, type):
        """Synchronously adds a new pending feature to Omega Psi

        Parameters
        ----------
            feature : str
                The feature to add to the pending update
            type : str
                The type of feature that is being added to the pending update
        
        Returns
        -------
            dict
                The JSON object of the created feature
        """
        pending_update = self.get_pending_update_sync()
        uid = uuid4()
        feature_json = {
            "id": str(uid),
            "feature": feature,
            "type": type,
            "datetime": datetime_to_dict(datetime.now())
        }
        pending_update["features"][str(uid)] = feature_json
        self.set_pending_update_sync(pending_update)
        return feature_json
    
    def edit_pending_feature_sync(self, featureID, feature, type):
        """Synchronously edits the feature given in the pending update

        Parameters
        ----------
            featureID : str
                The ID of the feature to edit
            feature : str
                The new feature value
            type : str
                The new feature type value
            
        Returns
        -------
            feature_json : dict or None
                The JSON object of the resulting edit of the feature
                    If None is returned, the featureID was not found
        """
        pending_update = self.get_pending_update_sync()
        if featureID in pending_update["features"]:
            pending_update["features"][featureID].update(
                feature = feature,
                type = type
            )
            self.set_pending_update_sync(pending_update)
            return pending_update["features"][featureID]
        return None
    
    def remove_pending_feature_sync(self, featureID):
        """Synchronously removes the feature given from the pending update

        Parameters
        ----------
            featureID : str
                The ID of the feature to remove
            
        Returns
        -------
            feature_json : dict or None
                The JSON object of the removed feature
                    If None is returned, the featureID was not found
        """
        pending_update = self.get_pending_update_sync()
        if featureID in pending_update["features"]:
            feature_json = pending_update["features"].pop(featureID)
            self.set_pending_update_sync(pending_update)
            return feature_json
        return None
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_updates(self):
        """Asynchronously retrieves a list of updates made to Omega Psi

        Returns
        -------
            list
                A list of JSON objects of updates made to Omega Psi
        """
        return await loop.run_in_executor(None, self.get_updates_sync)

    async def set_updates(self, updates_data):
        """Asynchronously sets the list of updates made to Omega Psi

        Parameters
        ----------
            updates : list
                A list of JSON object of updates made to Omega Psi
        """
        await loop.run_in_executor(None, self.set_updates_sync, updates_data)

    async def get_recent_update(self):
        """Asynchronously retrieves the most recent update made to Omega Psi

        Returns
        -------
            dict
                A JSON object of the most recent update made to Omega Psi
        """
        return await loop.run_in_executor(None, self.get_recent_update_sync)
    
    async def get_pending_update(self):
        """Asynchronously retrieves the pending update being made to Omega Psi

        Returns
        -------
            dict
                A JSON object of the current pending update being made to Omega Psi
        """
        return await loop.run_in_executor(None, self.get_pending_update_sync)
    
    async def set_pending_update(self, pending_update_data):
        """Asynchronously sets the pending update being made to Omega Psi

        Parameters
        ----------
            pending_update : dict
                A JSON object of the pending update to set
        """
        await loop.run_in_executor(None, self.set_pending_update_sync, pending_update_data)
    
    async def create_pending_update(self):
        """Asynchronously creates a pending update to Omega Psi"""
        await loop.run_in_executor(None, self.create_pending_update_sync)
    
    async def commit_pending_update(self, version, description):
        """Asynchronously commits and publishes the pending update as an update to Omega Psi

        Parameters
        ----------
            version : str
                The version of the update
            description : str
                The description of the update
        """
        await loop.run_in_executor(None, self.commit_pending_update_sync, version, description)
    
    async def add_pending_feature(self, feature, type):
        """Asynchronously adds a new pending feature to Omega Psi

        Parameters
        ----------
            feature : str
                The feature to add to the pending update
            type : str
                The type of feature that is being added to the pending update
        
        Returns
        -------
            dict
                The JSON object of the created feature
        """
        await loop.run_in_executor(None, self.add_pending_feature_sync, feature, type)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Tasks Access Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_tasks_sync(self):
        """Synchronously retrieves the task list from the database

        Returns
        -------
            dict
                A JSON object of IDs to their tasks
        """
        bot_data = self.get_bot_sync()
        return bot_data["tasks"]
    
    def set_tasks_sync(self, tasks):
        """Synchronously sets the task list in the database

        Parameters
        ----------
            tasks : dict
                A JSON object for tasks to set in the database
        """
        bot_data = self.get_bot_sync()
        bot_data["tasks"] = tasks
        self.set_bot_sync(bot_data)
    
    def add_task_sync(self, task):
        """Synchronously adds a new task to the task list

        Parameters
        ----------
            task : str
                The task to add to the database
        
        Returns
        -------
            str
                The ID of the created task
        """
        tasks = self.get_tasks_sync()
        uid = uuid4()
        tasks[str(uid)] = task
        self.set_tasks_sync(tasks)
        return {
            "task": task,
            "id": str(uid)
        }
    
    def edit_task_sync(self, taskID, task):
        """Synchronously edits a task in the task list

        Parameters
        ----------
            taskID : str
                The ID of the task to edit
            task : str
                The new task value
        
        Returns
        -------
            task_json : str or None
                The resulting task edit
                    If None is returned, the task was not found
        """
        tasks = self.get_tasks_sync()
        if taskID in tasks:
            tasks[taskID] = task
            self.set_tasks_sync(tasks)
            return {
                "task": task,
                "id": taskID
            }
        return None
    
    def remove_task_sync(self, taskID):
        """Synchronously removes a task from the task list

        Parameters
        ----------
            taskID : str
                The ID of the task to remove
        
        Returns
        -------
            task : str or None
                The removed task
                    If None is returned, the task was not found
        """
        tasks = self.get_tasks_sync()
        if taskID in tasks:
            task = tasks.pop(taskID)
            self.set_tasks_sync(tasks)
            return {
                "task": task,
                "id": taskID
            }
        return None
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_tasks(self):
        """Asynchronously retrieves the task list from the database

        Returns
        -------
            dict
                A JSON object of IDs to their tasks
        """
        return await loop.run_in_executor(None, self.get_tasks_sync)
    
    async def set_tasks(self, tasks_data):
        """Asynchronously sets the task list in the database

        Parameters
        ----------
            tasks : dict
                A JSON object for tasks to set in the database
        """
        await loop.run_in_executor(None, self.set_tasks_sync, tasks_data)
    
    async def add_task(self, task):
        """Asynchronously adds a new task to the task list

        Parameters
        ----------
            task : str
                The task to add to the database
        """
        await loop.run_in_executor(None, self.add_task_sync, task)
    
    async def remove_task(self, taskID):
        """Asynchronously removes a task from the task list

        Parameters
        ----------
            taskID : str
                The ID of the task to remove
        
        Returns
        -------
            task : str or None
                The removed task
        """
        return await loop.run_in_executor(None, self.remove_task_sync, taskID)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Changed File Access Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_changed_files_sync(self):
        """Synchronously retrieves the file changes saved in the database

        Returns
        -------
            dict
                The JSON object of files that are being saved to be changed in Omega Psi
        """
        bot_data = self.get_bot_sync()
        return bot_data["changed_files"]

    def set_changed_files_sync(self, changed_files):
        """Synchronously sets the file changes in the database

        Parameters
        ----------
            changed_files : dict
                The JSON object of files to remember
        """
        bot_data = self.get_bot_sync()
        bot_data["changed_files"] = changed_files
        self.set_bot_sync(bot_data)
    
    def add_file_sync(self, filename):
        """Synchronously adds a new file to the changed files

        Parameters
        ----------
            filename : str
                The filename to add the database to remember
        
        Returns
        -------
            fileID : str or None
                The ID of the created file
                    If None is returned, a file with the specified filename already exists
        """
        changed_files = self.get_changed_files_sync()
        for fileID in changed_files:
            if changed_files[fileID]["filename"] == filename:
                return None
        uid = uuid4()
        changed_files[str(uid)] = {
            "filename": filename,
            "changes": {}
        }
        self.set_changed_files_sync(changed_files)
        return str(uid)
    
    def edit_file_sync(self, fileID, filename):
        """Synchronously edits an existing file in the changed files

        Parameters
        ----------
            fileID : str
                The ID of the file to change
            filename : str
                The new filename to set
        
        Returns
        -------
            file_json : dict or None
                The resulting JSON object of the file with the new change
                    If None is returned, the fileID does not exist
        """
        changed_files = self.get_changed_files_sync()
        if fileID not in changed_files:
            return None
        changed_files[fileID]["filename"] = filename
        file_json = changed_files[fileID]
        self.set_changed_files_sync(changed_files)
        return file_json
    
    def remove_file_sync(self, fileID):
        """Synchronously removes a file from the changed files

        Parameters
        ----------
            fileID : str
                The ID of the file to remove
        
        Returns
        -------
            file_json : dict or None
                The JSON object of the removed file
                    If None is returned, the fileID does not exist
        """
        changed_files = self.get_changed_files_sync()
        if fileID in changed_files:
            file_json = changed_files.pop(fileID)
            self.set_changed_files_sync(changed_files)
            return file_json
        return None
    
    def add_file_change_sync(self, fileID, change):
        """Synchronously adds a file change to a file

        Parameters
        ----------
            fileID : str
                The ID of the file to add the change to
            change : str
                The change to add to the file
        
        Returns
        -------
            changeID : str or None
                The ID of the file change that was added
                    If None is returned, the fileID does not exist
        """
        changed_files = self.get_changed_files_sync()
        if fileID in changed_files:
            uid = uuid4()
            changed_files[fileID]["changes"][str(uid)] = change
            self.set_changed_files_sync(changed_files)
            return str(uid)
        return None
        
    def edit_file_change_sync(self, fileID, changeID, change):
        """Synchronously edits an existing change in a file

        Parameters
        ----------
            fileID : str
                The ID of the file to change the file in
            changeID : str
                The ID of the change to update
            change : str
                The new change to set
        
        Returns
        -------
            change : str, False, or None
                The resulting change
                    If False is returned, the changeID is not in the file
                    If None is returned, the fileID does not exist
        """
        changed_files = self.get_changed_files_sync()
        if fileID not in changed_files:
            return None
        if changeID not in changed_files[fileID]["changes"]:
            return False
        changed_files[fileID]["changes"][changeID] = change
        self.set_changed_files_sync(changed_files)
        return change
    
    def remove_file_change_sync(self, fileID, changeID):
        """Synchronously removes a file change from a file

        Parameters
        ----------
            fileID : str
                The ID of the file to remove a change from
            changeID : str
                The ID of the change to remove
        
        Returns
        -------
            change : str, False, or None
                The change that was removed
                    If False is returned, the changeID is not in the file
                    If None is returned, the fileID does not exist
        """
        changed_files = self.get_changed_files_sync()
        if fileID in changed_files:
            if changeID in changed_files[fileID]["changes"]:
                change = changed_files[fileID]["changes"].pop(changeID)
                self.set_changed_files_sync(changed_files)
                return change
            return False
        return None

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_changed_files(self):
        """Asynchronously retrieves the file changes saved in the database

        Returns
        -------
            dict
                The JSON object of files that are being saved to be changed in Omega Psi
        """
        return await loop.run_in_executor(None, self.get_changed_files_sync)
    
    async def set_changed_files(self, changed_files):
        """Asynchronously sets the file changes in the database

        Parameters
        ----------
            changed_files : dict
                The JSON object of files to remember
        """
        await loop.run_in_executor(None, self.set_changed_files_sync, changed_files)

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
        """Aynchronously returns a list of disabled commands in the entire bot

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