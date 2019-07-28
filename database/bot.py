from datetime import datetime
from functools import partial

from category.globals import loop

from util.misc import set_default
from util.string import datetime_to_string

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class Bot:
    def __init__(self, bot):
        self._bot = bot
    
    async def get_bot(self):
        
        # Set defaults
        data = {
            "activity_name": "o.help",
            "activity_type": 2,
            "developers": ["373317798430244864"],
            "owner": "373317798430244864",
            "todo": [],
            "pending_update": {},
            "updates": [],
            "restart": {
                "send": False
            },
            "files": {},
            "commands_run": 0
        }

        # Get bot data
        bot_data = await loop.run_in_executor(None,
            partial(
                self._bot.find_one,
                {"_id": "bot_information"}
            )
        )

        # Bot data is None; Create bot data
        if bot_data == None:
            self._bot.insert_one({"_id": "bot_information"})
            await self.set_bot(data)
        
        # Set defaults
        bot_data = set_default(data, bot_data)
        return bot_data
    
    async def set_bot(self, data):
        
        # Set bot data
        await loop.run_in_executor(None,
            partial(
                self._bot.update_one,
                {"_id": "bot_information"},
                {"$set": data},
                upsert = False
            )
        )
    
    def get_bot_sync(self):

        # Set defaults
        data = {
            "activity_name": "o.help",
            "activity_type": 2,
            "developers": ["373317798430244864"],
            "owner": "373317798430244864",
            "todo": [],
            "pending_update": {},
            "updates": [],
            "restart": {
                "send": False
            },
            "files": {},
            "commands_run": 0
        }

        # Get bot data
        bot_data = self._bot.find_one({"_id": "bot_information"})

        # Bot data is None; Create bot data
        if bot_data == None:
            self._bot.insert_one({"_id": "bot_information"})
            self.set_bot_sync(data)
        
        # Set defaults
        bot_data = set_default(data, bot_data)
        return bot_data
    
    def set_bot_sync(self, bot_data):
        self._bot.update_one({"_id": "bot_information"}, {"$set": bot_data}, upsert = False)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_restart(self):

        # Get bot data
        bot_data = await self.get_bot()

        return bot_data["restart"]
    
    async def set_restart(self, restart_data):

        # Get bot_data
        bot_data = await self.get_bot()

        bot_data["restart"] = restart_data

        # Set bot data
        await self.set_bot(bot_data)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_activity_name(self):
        
        # Get bot data
        bot_data = await self.get_bot()

        return bot_data["activity_name"]
    
    async def set_activity_name(self, activity_name):

        # Get bot data
        bot_data = await self.get_bot()

        bot_data["activity_name"] = activity_name

        # Set bot data
        await self.set_bot(bot_data)
    
    async def get_activity_type(self):

        # Get bot data
        bot_data = await self.get_bot()

        return bot_data["activity_type"]
    
    async def set_activity_type(self, activity_type):

        # Get bot data
        bot_data = await self.get_bot()

        bot_data["activity_type"] = activity_type

        # Set bot data
        await self.set_bot(bot_data)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_developers_sync(self):

        # Get bot data
        bot_data = self.get_bot_sync()

        return bot_data["developers"]
    
    async def get_developers(self):

        # Get bot data
        bot_data = await self.get_bot()

        return bot_data["developers"]
    
    async def is_developer(self, user):

        # Get bot data
        bot_data = await self.get_bot()

        return str(user.id) in bot_data["developers"]
    
    async def set_developers(self, developers):

        # Get bot data
        bot_data = await self.get_bot()

        bot_data["developers"] = developers

        # Set bot data
        await self.set_bot(bot_data)

    async def add_developer(self, developer):

        # Get developers
        dev_data = await self.get_developers()

        dev_data.append(developer)

        # Set developers
        await self.set_developers(dev_data)
    
    async def remove_developer(self, developer):

        # Get developers
        dev_data = await self.get_developers()

        dev_data.remove(developer)

        # Set developers
        await self.set_developers(dev_data)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_owner(self):

        # Get bot data
        bot_data = await self.get_bot()

        return bot_data["owner"]

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_todo(self):

        # Get bot data
        bot_data = await self.get_bot()

        return bot_data["todo"]
    
    async def set_todo(self, todo):

        # Get bot data
        bot_data = await self.get_bot()

        bot_data["todo"] = todo

        # Set bot data
        await self.set_bot(bot_data)
    
    async def add_todo_item(self, item):

        # Get todo list
        todo_list = await self.get_todo()

        todo_list.append(item)

        # Set todo list
        await self.set_todo(todo_list)
    
    async def remove_todo_item(self, index):

        # Get todo list
        todo_list = await self.get_todo()

        item = todo_list.pop(index)

        # Set todo list
        await self.set_todo(todo_list)

        return item
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_changed_files(self):

        # Get bot data
        bot_data = await self.get_bot()

        return bot_data["files"]
    
    async def set_changed_files(self, files):

        # Get bot data
        bot_data = await self.get_bot()

        bot_data["files"] = files

        # Set bot data
        await self.set_bot(bot_data)
    
    async def add_changed_file(self, filename, reason):

        # Get changed files
        files = await self.get_changed_files()

        # Check if the file already exists, add to the reasons
        if filename in files:
            files[filename].append(reason)

        # The file does not exist, create it
        else:
            files[filename] = [reason]

        # Set changed files
        await self.set_changed_files(files)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_pending_update(self):

        # Get bot data
        bot_data = await self.get_bot()

        return bot_data["pending_update"]
    
    async def get_updates(self):

        # Get bot data
        bot_data = await self.get_bot()

        return bot_data["updates"]
    
    async def get_recent_update(self):

        # Get updates
        updates = await self.get_updates()

        return updates[0]
    
    async def set_pending_update(self, pending_update):

        # Get bot data
        bot_data = await self.get_bot()

        bot_data["pending_update"] = pending_update

        # Set bot data
        await self.set_bot(bot_data)
    
    async def create_pending_update(self):

        # Set pending update dict
        data = {
            "fixes": [],
            "features": []
        }

        # Set pending update
        await self.set_pending_update(data)
    
    async def add_pending_fix(self, fix):

        # Get pending update
        pending_update = await self.get_pending_update()

        pending_update["fixes"].append(fix)

        # Set pending update
        await self.set_pending_update(pending_update)
    
    async def add_pending_feature(self, feature):

        # Get pending update
        pending_update = await self.get_pending_update()

        pending_update["features"].append(feature)

        # Set pending update
        await self.set_pending_update(pending_update)
    
    async def commit_pending_update(self, version, description):

        # Get pending update
        pending_update = await self.get_pending_update()

        # Reset pending update in bot
        await self.set_pending_update({})

        # Get updates
        updates = await self.get_updates()

        # Add update to bot; Include the current date as well
        current_date = datetime_to_string(datetime.now(), short = True)
        updates.insert(0, {
            "date": current_date,
            "version": version,
            "description": description,
            "features": pending_update["features"],
            "fixes": pending_update["fixes"]
        })

        # Set updates
        await self.set_updates(updates)
    
    async def set_updates(self, updates):

        # Get bot data
        bot_data = await self.get_bot()

        bot_data["updates"] = updates

        # Set bot data
        await self.set_bot(bot_data)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def run_command(self):

        # Get bot data
        bot_data = await self.get_bot()

        bot_data["commands_run"] += 1

        # Set bot data
        await self.set_bot(bot_data)
    
    async def get_commands_run(self):

        # Get bot data
        bot_data = await self.get_bot()

        return bot_data["commands_run"]