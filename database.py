from functools import partial
from pymongo import MongoClient

import asyncio, os

# Create new event loop
loop = asyncio.get_event_loop()

class Database:

    def __init__(self):

        # Create the connection and get the database for Omega Psi
        self._connection = MongoClient("ds115244.mlab.com", 15244, connect = False)
        self._omegaPsi = self._connection["omegapsi"]

        # Get the username and password to authenticate database access
        username = os.environ["DATABASE_USERNAME"]
        password = os.environ["DATABASE_PASSWORD"]
        self._omegaPsi.authenticate(username, password)

        # Keep track of different collections
        self._bot = self._omegaPsi.bot
        self._guilds = self._omegaPsi.guilds
        self._users = self._omegaPsi.users
        self._data = self._omegaPsi.data

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Methods for Guilds
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_guild(self, guild):

        # Set defaults
        data = {
            "_id": str(guild.id),
            "prefix": "o."
        }

        # Get guild data
        guild_data = await loop.run_in_executor(None,
            partial(
                self._guilds.find_one,
                {"_id": str(guild.id)}
            )
        )

        # Guild data is None; Create guild data
        if guild_data == None:
            self._guilds.insert_one({"_id": str(guild.id)})
            await self.set_guild(guild, data)
            guild_data = data
        
        # set defaults
        guild_data = set_default(data, guild_data)
        return guild_data
    
    async def set_guild(self, guild, data):

        # Set guild data
        await loop.run_in_executor(None,
            partial(
                self._guilds.update_one,
                {"_id": str(guild.id)}, 
                {"$set": data}, 
                upsert = False
            )
        )
    
    async def get_prefix(self, guild):

        # Open guild information
        guild_data = await self.get_guild(guild)

        return guild_data["prefix"]
    
    async def set_prefix(self, guild, prefix):

        # Open guild information
        guild_data = await self.get_guild(guild)

        guild_data["prefix"] = prefix

        await self.set_guild(guild, guild_data)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Methods for Users
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_user(self, user):

        # Set defaults
        data = {
            "_id": str(user.id),
            "imgur": {
                "hash": None,
                "id": None
            },
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
            },
            "cards_against_humanity": {
                "won": 0,
                "lost": 0
            }
        }

        # Get user data
        user_data = await loop.run_in_executor(None,
            partial(
                self._users.find_one,
                {"_id": str(user.id)}
            )
        )

        # User data is None; Create user data
        if user_data == None:
            self._users.insert_one({"_id": str(user.id)})
            await self.set_user(user, data)
            user_data = data
        
        # set defaults
        user_data = set_default(data, user_data)
        return user_data
    
    async def set_user(self, user, data):

        # Set user data
        await loop.run_in_executor(None,
            partial(
                self._users.update_one,
                {"_id": str(user.id)},
                {"$set": data},
                upsert = False
            )
        )

    # # # # # User Getters # # # # # 

    async def get_imgur(self, user):

        # Get user data
        user_data = await self.get_user(user)

        return user_data["imgur"]
    
    async def get_connect_four(self, user):

        # Get user data
        user_data = await self.get_user(user)

        return user_data["connect_four"]
    
    async def get_hangman(self, user):

        # Get user data
        user_data = await self.get_user(user)

        return user_data["hangman"]
    
    async def get_rps(self, user):

        # Get user data
        user_data = await self.get_user(user)

        return user_data["rps"]
    
    async def get_scramble(self, user):

        # Get user data
        user_data = await self.get_user(user)

        return user_data["scramble"]
    
    async def get_tic_tac_toe(self, user):

        # Get user data
        user_data = await self.get_user(user)

        return user_data["tic_tac_toe"]
    
    async def get_cards_against_humanity(self, user):

        # Get user data
        user_data = await self.get_user(user)

        return user_data["cards_against_humanity"]

    # # # # # User Setters # # # # # 

    async def set_imgur(self, user, imgur):

        # Get user data
        user_data = await self.get_user(user)

        user_data["imgur"] = imgur

        # Set user data
        await self.set_user(user, user_data)

    async def update_hangman(self, user, won):

        # Get user data
        user_data = await self.get_user(user)

        if won:
            user_data["hangman"]["won"] += 1
        else:
            user_data["hangman"]["lost"] += 1
        
        # Set user data
        await self.set_user(user, user_data)
    
    async def update_connect_four(self, user, won):

        # Get user data
        user_data = await self.get_user(user)

        if won:
            user_data["connect_four"]["won"] += 1
        else:
            user_data["connect_four"]["lost"] += 1
        
        # Set user data
        await self.set_user(user, user_data)
    
    async def update_rps(self, user, won):

        # Get user data
        user_data = await self.get_user(user)

        if won:
            user_data["rps"]["won"] += 1
        else:
            user_data["rps"]["lost"] += 1
        
        # Set user data
        await self.set_user(user, user_data)
    
    async def update_scramble(self, user, won):

        # Get user data
        user_data = await self.get_user(user)

        if won:
            user_data["scramble"]["won"] += 1
        else:
            user_data["scramble"]["lost"] += 1
        
        # Set user data
        await self.set_user(user, user_data)
    
    async def update_tic_tac_toe(self, user, won):

        # Get user data
        user_data = await self.get_user(user)

        if won:
            user_data["tic_tac_toe"]["won"] += 1
        else:
            user_data["tic_tac_toe"]["lost"] += 1
        
        # Set user data
        await self.set_user(user, user_data)
    
    async def update_cards_against_humanity(self, user, won):

        # Get user data
        user_data = await self.get_user(user)

        if won:
            user_data["cards_against_humanity"]["won"] += 1
        else:
            user_data["cards_against_humanity"]["lost"] += 1
        
        # Set user data
        await self.set_user(user, user_data)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Methods for Bot
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_bot(self):
        
        # Set defaults
        data = {
            "activity_name": "o.help",
            "activity_type": 2,
            "developers": ["373317798430244864"],
            "owner": "373317798430244864",
            "todo": [],
            "pending_update": [],
            "updates": [],
            "html_style": "normal",
            "restart": {
                "send": False
            }
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
            }
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
    
    # # # # # Bot Getters # # # # # 

    def get_html_style_sync(self):

        # Get bot data
        bot_data = self.get_bot_sync()

        return bot_data["html_style"]

    async def get_restart(self):

        # Get bot data
        bot_data = await self.get_bot()

        return bot_data["restart"]

    async def get_activity_name(self):
        
        # Get bot data
        bot_data = await self.get_bot()

        return bot_data["activity_name"]
    
    async def get_activity_type(self):

        # Get bot data
        bot_data = await self.get_bot()

        return bot_data["activity_type"]
    
    async def get_developers(self):

        # Get bot data
        bot_data = await self.get_bot()

        return bot_data["developers"]
    
    async def is_developer(self, user):

        # Get bot data
        bot_data = await self.get_bot()

        return str(user.id) in bot_data["developers"]
    
    async def get_owner(self):

        # Get bot data
        bot_data = await self.get_bot()

        return bot_data["owner"]
    
    async def get_todo(self):

        # Get bot data
        bot_data = await self.get_bot()

        return bot_data["todo"]
    
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
    
    # # # # # Bot Setters # # # # # 

    async def set_html_style(self, html_style):

        # Get bot data
        bot_data = await self.get_bot()

        bot_data["html_style"] = html_style

        # Set bot data
        await self.set_bot(bot_data)

    async def set_restart(self, restart_data):

        # Get bot_data
        bot_data = await self.get_bot()

        bot_data["restart"] = restart_data

        # Set bot data
        await self.set_bot(bot_data)

    async def set_activity_name(self, activity_name):

        # Get bot data
        bot_data = await self.get_bot()

        bot_data["activity_name"] = activity_name

        # Set bot data
        await self.set_bot(bot_data)
    
    async def set_activity_type(self, activity_type):

        # Get bot data
        bot_data = await self.get_bot()

        bot_data["activity_type"] = activity_type

        # Set bot data
        await self.set_bot(bot_data)
    
    async def set_developers(self, developers):

        # Get bot data
        bot_data = await self.get_bot()

        bot_data["developers"] = developers

        # Set bot data
        await self.set_bot(bot_data)
    
    async def set_owner(self, owner):

        # Get bot data
        bot_data = await self.get_bot()

        bot_data["owner"] = owner

        # Set bot data
        await self.set_bot(bot_data)
    
    async def set_todo(self, todo):

        # Get bot data
        bot_data = await self.get_bot()

        bot_data["todo"] = todo

        # Set bot data
        await self.set_bot(bot_data)
    
    async def add_todo(self, todo, index = -1):

        # Get bot data
        bot_data = await self.get_bot()

        # Check if index is -1; Add to end
        if index == -1:
            bot_data["todo"].append(todo)
            result = {
                "success": True,
                "reason": "`{}` was added to the todo list.".format(todo)
            }
        
        # Index is greater than zero, less than length
        elif index > 0 and index <= len(bot_data["todo"]):
            bot_data["todo"].insert(index - 1, todo)
            result = {
                "success": True,
                "reason": "`{}` was inserted into spot `{}` of the todo list.".format(todo, index)
            }
        
        # Index is invalid
        else:
            result = {
                "success": False,
                "reason": "The index provided (`{}`) is out of range of the todo list."
            }

        # Set bot data
        await self.set_todo(bot_data["todo"])

        return result
    
    async def remove_todo(self, index):

        # Get bot data
        bot_data = await self.get_bot()

        # Index is -1; Clear list
        if index == -1:
            bot_data["todo"] = []
            result = {
                "success": True,
                "reason": "The todo list was cleared."
            }

        # Check if index is greater than zero, less than length
        elif index > 0 and index <= len(bot_data["todo"]):
            removed = bot_data["todo"].pop(index - 1)
            result = {
                "success": True,
                "reason": "`{}` was removed from the todo list.".format(removed)
            }
        
        # Index is invalid
        else:
            result = {
                "success": False,
                "reason": "The index provided (`{}`) is out of range of the todo list.".format(index)
            }

        # Set bot data
        await self.set_todo(bot_data["todo"])

        return result
    
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

        # Add update to bot
        updates.insert(0, {
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
    # Methods for Games
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_hangman_words(self):

        # Get hangman data
        hangman_data = await loop.run_in_executor(None,
            partial(
                self._data.find_one,
                {"_id": "hangman"}
            )
        )

        return hangman_data
    
    async def set_hangman_words(self, hangman_data):

        # Set hangman data
        await loop.run_in_executor(None,
            partial(
                self._data.update_one,
                {"_id": "hangman"},
                {"$set": hangman_data},
                upsert = False
            )
        )
    
    async def add_hangman(self, difficulty, phrase):

        # Get hangman data
        hangman_data = await self.get_hangman_words()

        hangman_data[difficulty].append({
            "value": phrase,
            "level": difficulty
        })

        # Set hangman data
        await self.set_hangman_words(self, hangman_data)
    
    async def get_scramble_words(self):

        # Get scramble data
        scramble_data = await loop.run_in_executor(None,
            partial(
                self._data.find_one,
                {"_id": "scramble"}
            )
        )

        return scramble_data
    
    async def set_scramble_words(self, scramble_data):

        # Set scramble data
        await loop.run_in_executor(None,
            partial(
                self._data.update_one,
                {"_id": "scramble"},
                {"$set": scramble_data},
                upsert = False
            )
        )
    
    async def add_scramble(self, phrase, hints):

        # Get scramble data
        scramble_data = await self.get_scramble_words()

        scramble_data["words"].append({
            "value": phrase,
            "hints": hints
        })

        # Set scramble data
        await self.set_scramble_words(scramble_data)
    
    async def get_cards_against_humanity_cards(self):

        # Get cards against humanity data
        cah_data = await loop.run_in_executor(None,
            partial(
                self._data.find_one,
                {"_id": "cards_against_humanity"}
            )
        )

        return cah_data

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # 
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def set_default(default_dict, result_dict):

    # Iterate through default values
    for tag in default_dict:

        # If the tag does not exist in the result dictionary, add it
        if tag not in result_dict:
            result_dict[tag] = default_dict[tag]
        
        # Tag exists in guild dict, see if tag is a dictionary
        else:
            if type(result_dict[tag]) == dict:
                result_dict[tag] = set_default(default_dict[tag], result_dict[tag])
    
    return result_dict

database = Database()