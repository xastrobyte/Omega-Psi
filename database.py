import asyncio, os, pytz

from datetime import datetime
from functools import partial
from pymongo import MongoClient
from random import choice

from util.string import datetime_to_dict

# Create new event loop
loop = asyncio.get_event_loop()

# Each collection has its own class

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
            "theme": {},
            "files": []
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
            "theme": {},
            "files": []
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

    async def get_theme(self):

        # Get bot data
        bot_data = await self.get_bot()

        # Check if theme of the day is empty
        current = datetime.now().astimezone(pytz.timezone("US/Mountain"))
        date = "{}-{}".format(
            current.month,
            current.day
        )

        # Return default if theme of day is empty
        if date not in bot_data["theme"]:
            return {
                "date": date,
                "dark": "293134",
                "light": "ec7600",
                "medium": "678cb1",
                "description": "Nothing special happens on {}".format(date.replace("-", "/"))
            }

        return bot_data["theme"][date]
    
    async def set_theme(self, date, dark, medium, light, description):

        # Get bot data
        bot_data = await self.get_bot()

        bot_data["theme"][date] = {
            "dark": dark,
            "medium": medium,
            "light": light,
            "date": date,
            "description": description
        }

        # Set bot data
        await self.set_bot(bot_data)

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

        files.append({
            "file": filename,
            "reason": reason
        })

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

class Guild:
    def __init__(self, guilds):
        self._guilds = guilds
    
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
            await loop.run_in_executor(None,
                partial(
                    self._guilds.insert_one,
                    {"_id": str(guild.id)}
                )
            )
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

class User:
    def __init__(self, users):
        self._users = users
    
    async def get_user(self, user):

        # Set defaults
        data = {
            "_id": str(user.id),
            "embed_color": None,
            "vote": {
                "previous": 0,
                "refresh": 2 * 24 * 60 * 60 # By default, user must vote once every 
                                            # 2 days to use "premium" commands
                                            # Can be set per user by bot moderators
            },
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
            },
            "trivia": {
                "won": 0,
                "lost": 0
            },
            "uno": {
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
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_previous_vote(self, user):

        # Get user data
        user_data = await self.get_user(user)

        return user_data["vote"]["previous"]
    
    async def set_previous_vote(self, user, previous_vote):

        # Get user data
        user_data = await self.get_user(user)

        user_data["vote"]["previous"] = previous_vote

        await self.set_user(user, user_data)
    
    async def get_refresh_vote(self, user):

        # Get user data
        user_data = await self.get_user(user)

        return user_data["vote"]["refresh"]
    
    async def set_refresh_vote(self, user, refresh):

        # Get user data
        user_data = await self.get_user(user)

        user_data["vote"]["refresh"] = refresh * 24 * 60 * 60 # Refresh parameter should be in days

        await self.set_user(user, user_data)
    
    async def needs_to_vote(self, user):

        # Check if previous vote + refresh is less than current time
        current = int(datetime.now().timestamp())
        previous = await self.get_previous_vote(user)
        refresh = await self.get_refresh_vote(user)
        
        return (previous + refresh) < current

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_imgur(self, user):

        # Get user data
        user_data = await self.get_user(user)

        return user_data["imgur"]
    
    async def set_imgur(self, user, imgur):

        # Get user data
        user_data = await self.get_user(user)

        user_data["imgur"] = imgur

        # Set user data
        await self.set_user(user, user_data)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_embed_color(self, user):

        # Get user data
        user_data = await self.get_user(user)

        return user_data["embed_color"]
    
    async def set_embed_color(self, user, color):

        # Get user data
        user_data = await self.get_user(user)

        user_data["embed_color"] = color

        # Set user data
        await self.set_user(user, user_data)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_connect_four(self, user):

        # Get user data
        user_data = await self.get_user(user)

        return user_data["connect_four"]
    
    async def update_connect_four(self, user, won):

        # Get user data
        user_data = await self.get_user(user)

        if won:
            user_data["connect_four"]["won"] += 1
        else:
            user_data["connect_four"]["lost"] += 1
        
        # Set user data
        await self.set_user(user, user_data)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_hangman(self, user):

        # Get user data
        user_data = await self.get_user(user)

        return user_data["hangman"]
    
    async def update_hangman(self, user, won):

        # Get user data
        user_data = await self.get_user(user)

        if won:
            user_data["hangman"]["won"] += 1
        else:
            user_data["hangman"]["lost"] += 1
        
        # Set user data
        await self.set_user(user, user_data)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_rps(self, user):

        # Get user data
        user_data = await self.get_user(user)

        return user_data["rps"]
    
    async def update_rps(self, user, won):

        # Get user data
        user_data = await self.get_user(user)

        if won:
            user_data["rps"]["won"] += 1
        else:
            user_data["rps"]["lost"] += 1
        
        # Set user data
        await self.set_user(user, user_data)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_scramble(self, user):

        # Get user data
        user_data = await self.get_user(user)

        return user_data["scramble"]
    
    async def update_scramble(self, user, won):

        # Get user data
        user_data = await self.get_user(user)

        if won:
            user_data["scramble"]["won"] += 1
        else:
            user_data["scramble"]["lost"] += 1
        
        # Set user data
        await self.set_user(user, user_data)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_tic_tac_toe(self, user):

        # Get user data
        user_data = await self.get_user(user)

        return user_data["tic_tac_toe"]
    
    async def update_tic_tac_toe(self, user, won):

        # Get user data
        user_data = await self.get_user(user)

        if won:
            user_data["tic_tac_toe"]["won"] += 1
        else:
            user_data["tic_tac_toe"]["lost"] += 1
        
        # Set user data
        await self.set_user(user, user_data)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_cards_against_humanity(self, user):

        # Get user data
        user_data = await self.get_user(user)

        return user_data["cards_against_humanity"]
    
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

    async def get_trivia(self, user):

        # Get user data
        user_data = await self.get_user(user)

        return user_data["trivia"]
    
    async def update_trivia(self, user, won):

        # Get user data
        user_data = await self.get_user(user)

        if won:
            user_data["trivia"]["won"] += 1
        else:
            user_data["trivia"]["lost"] += 1
        
        # Set user data
        await self.set_user(user, user_data)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_uno(self, user):

        # Get user data
        user_data = await self.get_user(user)

        return user_data["uno"]
    
    async def update_uno(self, user, won):

        # Get user data
        user_data = await self.get_user(user)

        if won:
            user_data["uno"]["won"] += 1
        else:
            user_data["uno"]["lost"] += 1
        
        # Set user data
        await self.set_user(user, user_data)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class Data:
    def __init__(self, data):
        self._data = data
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_hangman_data_sync(self):
        
        # Get hangman data
        return self._data.find_one({"_id": "hangman"})
    
    def set_hangman_data_sync(self, hangman_data):
        
        # Set hangman data
        self._data.update_one(
            {"_id": "hangman"},
            {"$set": hangman_data},
            upsert = False
        )
    
    def add_pending_hangman_word_sync(self, phrase, author, email):
        
        # Get hangman data
        hangman_data = self.get_hangman_data_sync()

        # Add the phrase to the pending hangmans
        hangman_data["pending_hangman"].append({
            "phrase": phrase,
            "author": author,
            "email": email
        })

        # Set hangman data
        self.set_hangman_data_sync(hangman_data)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_scramble_data_sync(self):
        
        # Get scramble data
        return self._data.find_one({"_id": "scramble"})
    
    def set_scramble_data_sync(self, scramble_data):
        
        # Set scramble data
        self._data.update_one(
            {"_id": "scramble"},
            {"$set": scramble_data},
            upsert = False
        )
    
    def add_pending_scramble_word_sync(self, phrase, author, email):
        
        # Get scramble data
        scramble_data = self.get_scramble_data_sync()

        # Add the phrase to the pending scrambles
        scramble_data["pending_scramble"].append({
            "phrase": phrase,
            "author": author,
            "email": email,
            "hints": []
        })

        # Set scramble data
        self.set_scramble_data_sync(scramble_data)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_insult_data_sync(self):
        
        # Get insult data
        return self._data.find_one({"_id": "insults"})
    
    def set_insult_data_sync(self, insult_data):
        
        # Set insult data
        self._data.update_one(
            {"_id": "insults"},
            {"$set": insult_data},
            upsert = False
        )
    
    def add_pending_insult_sync(self, insult, author, email):
        
        # Get insult data
        insult_data = self.get_insult_data_sync()

        # Add insult to pending insult
        insult_data["pending_insults"].append({
            "insult": insult,
            "author": author,
            "email": email,
            "tags": []
        })
    
        # Set insult data
        self.set_insult_data_sync(insult_data)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_hangman_data(self):

        # Get hangman data
        hangman_data = await loop.run_in_executor(None,
            partial(
                self._data.find_one,
                {"_id": "hangman"}
            )
        )

        return hangman_data
    
    async def set_hangman_data(self, hangman_data):

        # Set hangman data
        await loop.run_in_executor(None,
            partial(
                self._data.update_one,
                {"_id": "hangman"},
                {"$set": hangman_data},
                upsert = False
            )
        )
    
    async def add_hangman_word(self, phrase):

        # Get hangman data
        hangman_data = await self.get_hangman_words()

        hangman_data["words"].append({
            "value": phrase,
            "level": "None"
        })

        # Set hangman data
        await self.set_hangman_words(hangman_data)
    
    async def get_hangman_words(self):
        return await self.get_hangman_data()
    
    async def set_hangman_words(self, hangman_words):
        await self.set_hangman_data(hangman_words)
    
    async def add_pending_hangman(self, phrase, author):
        
        # Get pending hangman data
        pending_hangman_data = await self.get_pending_hangman()

        # Add the phrase to the pending hangmans
        pending_hangman_data.append({
            "phrase": phrase,
            "author": author
        })

        # Set pending hangman data
        await self.set_pending_hangman(pending_hangman_data)
    
    async def get_pending_hangman(self):
        
        # Get hangman data
        hangman_data = await self.get_hangman_data()

        return hangman_data["pending_hangman"]
    
    async def set_pending_hangman(self, pending_hangman_data):
        
        # Get hangman data
        hangman_data = await self.get_hangman_data()

        hangman_data["pending_hangman"] = pending_hangman_data

        # Set hangman data
        await self.set_hangman_data(hangman_data)
    
    async def approve_pending_hangman(self, index):
        
        # Get pending hangman data
        pending_hangman_data = await self.get_pending_hangman()

        pending_hangman = pending_hangman_data.pop(index)

        # Set pending hangman data
        await self.set_pending_hangman(pending_hangman_data)

        # Add hangman phrase
        await self.add_hangman_word(pending_hangman["phrase"])
    
    async def deny_pending_hangman(self, index):
        
        # Get pending hangman data
        pending_hangman_data = await self.get_pending_hangman()

        pending_hangman_data.pop(index)

        # Set pending hangman data
        await self.set_pending_hangman(pending_hangman_data)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_scramble_data(self):

        # Get scramble data
        scramble_data = await loop.run_in_executor(None,
            partial(
                self._data.find_one,
                {"_id": "scramble"}
            )
        )

        return scramble_data
    
    async def set_scramble_data(self, scramble_data):

        # Set scramble data
        await loop.run_in_executor(None,
            partial(
                self._data.update_one,
                {"_id": "scramble"},
                {"$set": scramble_data},
                upsert = False
            )
        )
    
    async def add_scramble_word(self, phrase, hints):

        # Get scramble data
        scramble_data = await self.get_scramble_words()

        scramble_data["words"].append({
            "value": phrase,
            "hints": hints
        })

        # Set scramble data
        await self.set_scramble_words(scramble_data)
    
    async def get_scramble_words(self):
        return await self.get_scramble_data()
    
    async def set_scramble_words(self, scramble_words):
        await self.set_scramble_data(scramble_words)
    
    async def add_pending_scramble(self, phrase, author):
        
        # Get pending scramble data
        pending_scramble_data = await self.get_pending_scramble()

        # Add the phrase to the pending scrambles
        pending_scramble_data.append({
            "phrase": phrase,
            "author": author,
            "hints": []
        })

        # Set pending scramble data
        await self.set_pending_scramble(pending_scramble_data)
    
    async def add_pending_scramble_hints(self, index, hints = []):

        # Get pending scramble data
        pending_scramble_data = await self.get_pending_scramble()

        # Add the hints to the proper index
        pending_scramble_data[index]["hints"] += hints

        # Set pending scramble data
        await self.set_pending_scramble(pending_scramble_data)
    
    async def get_pending_scramble(self):
        
        # Get scramble data
        scramble_data = await self.get_scramble_data()

        return scramble_data["pending_scramble"]
    
    async def set_pending_scramble(self, pending_scramble_data):
        
        # Get scramble data
        scramble_data = await self.get_scramble_data()

        scramble_data["pending_scramble"] = pending_scramble_data

        # Set scramble data
        await self.set_scramble_data(scramble_data)
    
    async def approve_pending_scramble(self, index):
        
        # Get pending scramble data
        pending_scramble_data = await self.get_pending_scramble()

        pending_scramble = pending_scramble_data.pop(index)

        # Set pending scramble data
        await self.set_pending_scramble(pending_scramble_data)

        # Add scramble phrase
        await self.add_scramble_word(
            pending_scramble["phrase"],
            pending_scramble["hints"]
        )
    
    async def deny_pending_scramble(self, index):
        
        # Get pending scramble data
        pending_scramble_data = await self.get_pending_scramble()

        pending_scramble_data.pop(index)

        # Set pending scramble data
        await self.set_pending_scramble(pending_scramble_data)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
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
    
    async def get_insult_data(self):

        default = {
            "pending_insults": [],
            "insults": []
        }

        # Get insult data
        insult_data = await loop.run_in_executor(None,
            partial(
                self._data.find_one,
                {"_id": "insults"}
            )
        )

        if insult_data == None:
            await loop.run_in_executor(None,
                partial(
                    self._data.insert_one,
                    {"_id": "insults"}
                )
            )
            await self.set_insult_data(default)
            insult_data = default
        
        return insult_data
    
    async def set_insult_data(self, insult_data):

        # Set insult data
        await loop.run_in_executor(None,
            partial(
                self._data.update_one,
                {"_id": "insults"}, 
                {"$set": insult_data}, 
                upsert = False
            )
        )
    
    async def get_pending_insults(self):

        # Get insult data
        insult_data = await self.get_insult_data()

        return insult_data["pending_insults"]
    
    async def set_pending_insults(self, pending_insults):

        # Get insult data
        insult_data = await self.get_insult_data()

        insult_data["pending_insults"] = pending_insults

        # Set insult data
        await self.set_insult_data(insult_data)
    
    async def add_pending_insult(self, insult, author):

        # Get pending insults
        pending_insults = await self.get_pending_insults()

        pending_insults.append({
            "insult": insult,
            "author": author,
            "tags": []
        })

        # Set pending insults
        await self.set_pending_insults(pending_insults)
    
    async def add_pending_insult_tags(self, index, tags = []):

        # Get pending insults
        pending_insults = await self.get_pending_insults()

        for tag in tags:
            if tag.lower() not in pending_insults[index]["tags"]:
                pending_insults[index]["tags"].append(tag.lower())

        # Set pending insults
        await self.set_pending_insults(pending_insults)
    
    async def approve_pending_insult(self, index):

        # Get pending insults
        pending_insults = await self.get_pending_insults()

        # Remove insult
        insult = pending_insults.pop(index)

        # Set pending insults
        await self.set_pending_insults(pending_insults)

        # Get insults
        insults = await self.get_insults()

        # Add insult
        insults.append(insult)

        # Set insults
        await self.set_insults(insults)
    
    async def deny_pending_insult(self, index):

        # Get pending insults
        pending_insults = await self.get_pending_insults()

        # Remove insult
        pending_insults.pop(index)

        # Set pending insults
        await self.set_pending_insults(pending_insults)
    
    async def get_insults(self):

        # Get insult data
        insult_data = await self.get_insult_data()

        return insult_data["insults"]
    
    async def set_insults(self, insults):

        # Get insult data
        insult_data = await self.get_insult_data()

        insult_data["insults"] = insults

        # Set insult data
        await self.set_insult_data(insult_data)
    
    async def get_insult(self, nsfw = False):

        # Get insults
        insults = await self.get_insults()

        while True:
            insult = choice(insults)

            if nsfw or "nsfw" not in insult["tags"]:
                return insult
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_compliment_data(self):

        default = {
            "pending_compliments": [],
            "compliments": []
        }

        # Get compliment data
        compliment_data = await loop.run_in_executor(None,
            partial(
                self._data.find_one,
                {"_id": "compliments"}
            )
        )

        if compliment_data == None:
            await loop.run_in_executor(None,
                partial(
                    self._data.insert_one,
                    {"_id": "compliments"}
                )
            )
            await self.set_compliment_data(default)
            compliment_data = default
        
        return compliment_data
    
    async def set_compliment_data(self, compliment_data):

        # Set compliment data
        await loop.run_in_executor(None,
            partial(
                self._data.update_one,
                {"_id": "compliments"}, 
                {"$set": compliment_data}, 
                upsert = False
            )
        )
    
    async def get_pending_compliments(self):

        # Get compliment data
        compliment_data = await self.get_compliment_data()

        return compliment_data["pending_compliments"]
    
    async def set_pending_compliments(self, pending_compliments):

        # Get compliment data
        compliment_data = await self.get_compliment_data()

        compliment_data["pending_compliments"] = pending_compliments

        # Set compliment data
        await self.set_compliment_data(compliment_data)
    
    async def add_pending_compliment(self, compliment, author):

        # Get pending compliments
        pending_compliments = await self.get_pending_compliments()

        pending_compliments.append({
            "compliment": compliment,
            "author": author,
            "tags": []
        })

        # Set pending compliments
        await self.set_pending_compliments(pending_compliments)
    
    async def add_pending_compliment_tags(self, index, tags = []):

        # Get pending compliments
        pending_compliments = await self.get_pending_compliments()

        for tag in tags:
            if tag.lower() not in pending_compliments[index]["tags"]:
                pending_compliments[index]["tags"].append(tag.lower())

        # Set pending compliments
        await self.set_pending_compliments(pending_compliments)
    
    async def approve_pending_compliment(self, index):

        # Get pending compliments
        pending_compliments = await self.get_pending_compliments()

        # Remove compliment
        compliment = pending_compliments.pop(index)

        # Set pending compliments
        await self.set_pending_compliments(pending_compliments)

        # Get compliments
        compliments = await self.get_compliments()

        # Add compliment
        compliments.append(compliment)

        # Set compliments
        await self.set_compliments(compliments)
    
    async def deny_pending_compliment(self, index):

        # Get pending compliments
        pending_compliments = await self.get_pending_compliments()

        # Remove compliment
        pending_compliments.pop(index)

        # Set pending compliments
        await self.set_pending_compliments(pending_compliments)
    
    async def get_compliments(self):

        # Get compliment data
        compliment_data = await self.get_compliment_data()

        return compliment_data["compliments"]
    
    async def set_compliments(self, compliments):

        # Get compliment data
        compliment_data = await self.get_compliment_data()

        compliment_data["compliments"] = compliments

        # Set compliment data
        await self.set_compliment_data(compliment_data)
    
    async def get_compliment(self, nsfw = False):

        # Get compliments
        compliments = await self.get_compliments()

        while True:
            compliment = choice(compliments)

            if nsfw or "nsfw" not in compliment["tags"]:
                return compliment

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class CaseNumber:
    def __init__(self, case_numbers):
        self._case_numbers = case_numbers
    
    def get_suggestion_cases_sync(self):

        default = {
            "number": 1,
            "cases": {}
        }

        # Get suggestion data
        case_data = self._case_numbers.find_one({"_id": "suggestions"})

        if case_data == None:
            self.set_suggestion_cases_sync(default)
            case_data = default
        
        return case_data
    
    def set_suggestion_cases_sync(self, cases):

        # Check if there is None; create it
        suggestion_data = self._case_numbers.find_one({"_id": "suggestions"})

        if suggestion_data == None:
            self._case_numbers.insert_one({"_id": "suggestions"})
        
        # Set data
        self._case_numbers.update_one(
            {"_id": "suggestions"},
            {"$set": cases},
            upsert = False
        )
    
    def get_suggestion_number_sync(self):
        suggestion_cases = self.get_suggestion_cases_sync()

        return suggestion_cases["number"]
    
    def add_suggestion_sync(self, suggestion, author, email):
        
        # Get suggestion cases
        suggestion_cases = self.get_suggestion_cases_sync()

        # Get current number then update it
        number = suggestion_cases["number"]
        suggestion_cases["number"] += 1

        # Add the suggestion
        current_time = datetime_to_dict(datetime.now())
        suggestion_cases["cases"][str(number)] = {
            "suggestion": suggestion,
            "author": author,
            "email": email,     # This is only set in the sync version of the function
                                # because it is used for the website version of the command
                                # that uses it
            "time": current_time,
            "seen": False
        }

        # Set suggestion cases
        self.set_suggestion_cases_sync(suggestion_cases)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_bug_cases_sync(self):

        default = {
            "number": 1,
            "cases": {}
        }

        # Get bug data
        case_data = self._case_numbers.find_one({"_id": "bugs"})

        if case_data == None:
            self.set_bug_cases_sync(default)
            case_data = default
        
        return case_data
    
    def set_bug_cases_sync(self, cases):

        # Check if there is None; create it
        bug_data = self._case_numbers.find_one({"_id": "bugs"})

        if bug_data == None:
            self._case_numbers.insert_one({"_id": "bugs"})
        
        # Set data
        self._case_numbers.update_one(
            {"_id": "bugs"},
            {"$set": cases},
            upsert = False
        )
    
    def get_bug_number_sync(self):
        bug_cases = self.get_bug_cases_sync()

        return bug_cases["number"]
    
    def add_bug_sync(self, bug, author, email):
        
        # Get bug cases
        bug_cases = self.get_bug_cases_sync()

        # Get current number then update it
        number = bug_cases["number"]
        bug_cases["number"] += 1

        # Add the bug
        current_time = datetime_to_dict(datetime.now())
        bug_cases["cases"][str(number)] = {
            "bug": bug,
            "author": author,
            "email": email,     # This is only set in the sync version of the function
                                # because it is used for the website version of the command
                                # that uses it
            "time": current_time,
            "seen": False
        }

        # Set bug cases
        self.set_bug_cases_sync(bug_cases)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_suggestion_cases(self):

        default = {
            "number": 1,
            "cases": {}
        }
        
        # Get suggestion data
        case_data = await loop.run_in_executor(None,
            self._case_numbers.find_one,
            {"_id": "suggestions"}
        )

        if case_data == None:
            await self.set_suggestion_cases(default)
            case_data = default
        
        return case_data
    
    async def set_suggestion_cases(self, cases):

        # Check if there is None; Create it
        suggestion_data = await loop.run_in_executor(None,
            self._case_numbers.find_one,
            {"_id": "suggestions"}
        )
        if suggestion_data == None:
            await loop.run_in_executor(None,
                self._case_numbers.insert_one,
                {"_id": "suggestions"}
            )
        
        # Set data
        await loop.run_in_executor(None,
            partial(
                self._case_numbers.update_one,
                {"_id": "suggestions"},
                {"$set": cases},
                upsert = False
            )
        )
    
    async def get_suggestion(self, number):
        
        # Get suggestion cases
        suggestion_cases = await self.get_suggestion_cases()

        if str(number) in suggestion_cases:
            return suggestion_cases[str(number)]
        return None
    
    async def get_suggestion_number(self):

        suggestion_cases = await self.get_suggestion_cases()

        return suggestion_cases["number"]
    
    async def mark_suggestion_seen(self, number):

        # Get suggestions cases
        suggestion_cases = await self.get_suggestion_cases()

        suggestion_cases["cases"][str(number)]["seen"] = True

        # Set suggestion cases
        await self.set_suggestion_cases(suggestion_cases)
    
    async def add_suggestion(self, suggestion, author):
        
        # Get suggestion cases
        suggestion_cases = await self.get_suggestion_cases()

        # Get current number then update it
        number = suggestion_cases["number"]
        suggestion_cases["number"] += 1

        # Add the suggestion
        current_time = datetime_to_dict(datetime.now())
        suggestion_cases["cases"][str(number)] = {
            "suggestion": suggestion,
            "author": author,
            "time": current_time,
            "seen": False
        }

        # Set suggestion cases
        await self.set_suggestion_cases(suggestion_cases)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_bug_cases(self):
        
        default = {
            "number": 1,
            "cases": {}
        }
        
        # Get bug data
        case_data = await loop.run_in_executor(None,
            self._case_numbers.find_one,
            {"_id": "bugs"}
        )

        if case_data == None:
            await self.set_bug_cases(default)
            case_data = default
        
        return case_data
    
    async def set_bug_cases(self, cases):

        # Check if there is None; Create it
        bug_data = await loop.run_in_executor(None,
            self._case_numbers.find_one,
            {"_id": "bugs"}
        )
        if bug_data == None:
            await loop.run_in_executor(None,
                self._case_numbers.insert_one,
                {"_id": "bugs"}
            )
        
        # Set data
        await loop.run_in_executor(None,
            partial(
                self._case_numbers.update_one,
                {"_id": "bugs"},
                {"$set": cases},
                upsert = False
            )
        )
    
    async def get_bug(self, number):

        # Get bug cases
        bug_cases = await self.get_bug_cases()

        if str(number) in bug_cases:
            return bug_cases[str(number)]
        return None
    
    async def get_bug_number(self):

        bug_cases = await self.get_bug_cases()

        return bug_cases["number"]
    
    async def mark_bug_seen(self, number):

        # Get bug cases
        bug_cases = await self.get_bug_cases()

        bug_cases["cases"][str(number)]["seen"] = True

        # Set bug cases
        await self.set_bug_cases(bug_cases)
    
    async def add_bug(self, bug, author):

        # Get bug cases
        bug_cases = await self.get_bug_cases()

        # Get current number then update it
        number = bug_cases["number"]
        bug_cases["number"] += 1

        # Add the bug
        current_time = datetime_to_dict(datetime.now())
        bug_cases["cases"][str(number)] = {
            "bug": bug,
            "author": author,
            "time": current_time,
            "seen": False
        }

        # Set bug cases
        await self.set_bug_cases(bug_cases)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class OnlineStatus:
    def __init__(self, online_status):
        self._online_status = online_status

    # # # # # # # # # # # # # # # # # # # #

    async def get_user(self, user):
        
        # Default user data
        default = {
            "_id": str(user.id),
            "listeners": {}
        }

        # Try loading the user
        user_data = await loop.run_in_executor(None,
            partial(
                self._online_status.users.find_one,
                {"_id": str(user.id)}
            )
        )

        # If user_data is None, there is no user saved
        #   Create a new user
        #   Then setup the user using set_user
        if user_data == None:
            await loop.run_in_executor(None,
                partial(
                    self._online_status.users.insert_one,
                    {"_id": str(user.id)}
                )
            )
            await self.set_user(user, default)
            return default
        
        # user_Data is not None, return the data
        return user_data
    
    async def set_user(self, user, data):
        
        # Set the user data
        await loop.run_in_executor(None,
            partial(
                self._online_status.users.update_one,
                {"_id": str(user.id)},
                {"$set": data},
                upsert = False
            )
        )
    
    # # # # # # # # # # # # # # # # # # # #

    async def get_listener(self, target, create = True):
        
        # Default listener data
        default = {
            "_id": str(target.id),
            "users": {}
        }

        # Try loading the listener data
        listener_data = await loop.run_in_executor(None,
            partial(
                self._online_status.targets.find_one,
                {"_id": str(target.id)}
            )
        )

        # If listener_data is None, there is no listener saved
        #   Create a new listener
        #   Then setup the listener using set_listener
        if listener_data == None and create:
            await loop.run_in_executor(None,
                partial(
                    self._online_status.targets.insert_one,
                    {"_id": str(target.id)}
                )
            )
            await self.set_listener(target, default)
            return default
        
        # listener_data is None, return the data
        return listener_data
    
    async def set_listener(self, target, data):
        
        # Set the listener data
        await loop.run_in_executor(None,
            partial(
                self._online_status.targets.update_one,
                {"_id": str(target.id)},
                {"$set": data},
                upsert = False
            )
        )
    
    async def get_listeners(self, user):
        
        # Load the user's data
        user_data = await self.get_user(user)

        # Return the listeners underneath the user
        return user_data["listeners"]
    
    async def set_listeners(self, user, data):
        
        # Load the user's data
        user_data = await self.get_user(user)

        # Update the listeners
        user_data["listeners"] = data

        # Set the user's data
        await self.set_user(user, user_data)
    
    async def get_targets(self):

        # Load the targets collection
        targets = await loop.run_in_executor(None,
            self._online_status.targets.find
        )

        return list(targets)
    
    # # # # # # # # # # # # # # # # # # # #

    async def add_listener(self, user, target):
        
        # Load the user's data
        user_data = await self.get_user(user)

        # Load the target's data
        target_data = await self.get_listener(target)

        # Add the listener to the user's data
        user_data["listeners"][str(target.id)] = True

        # Add the listener to the target data
        target_data["users"][str(user.id)] = {
            "active": True,
            "guild_id": str(user.guild.id)
        }

        # Set the user's data
        await self.set_user(user, user_data)

        # Set the target's data
        await self.set_listener(target, target_data)
    
    async def delete_listener(self, user, target):
        
        # Check if the user has the listener
        user_data = await self.get_user(user)
        if str(target.id) in user_data["listeners"]:
            user_data["listeners"].pop(str(target.id))
        await self.set_user(user, user_data)
        
        # Check if the user is under the target listener
        target_data = await self.get_listener(target)
        if str(user.id) in target_data["users"]:
            target_data["users"].pop(str(user.id))
        await self.set_listener(target, target_data)

    async def toggle_listener(self, user, target):
        
        # Toggle the user listening to the target
        user_data = await self.get_user(user)
        if str(target.id) in user_data["listeners"]:
            user_data["listeners"][str(target.id)] = not user_data["listeners"][str(target.id)]
        await self.set_user(user, user_data)
        
        # Toggle the target data listening to the user
        target_data = await self.get_listener(target)
        if str(user.id) in target_data["users"]:
            target_data["users"][str(user.id)]["active"] = not target_data["users"][str(user.id)]["active"]
        await self.set_listener(target, target_data)
    
    async def listener_status(self, user, target):

        # Get the user data
        user_data = await self.get_user(user)

        # Check if the target exists as a listener
        if str(target.id) in user_data["listeners"]:
            return user_data["listeners"][str(target.id)]
        
        return False

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class Database:

    def __init__(self):

        # Create the connection and get the database for Omega Psi
        self._omega_psi_connection = MongoClient("ds115244.mlab.com", 15244, connect = False)
        self._omegaPsi = self._omega_psi_connection["omegapsi"]

        # Get the username and password to authenticate database access
        username = os.environ["DATABASE_USERNAME"]
        password = os.environ["DATABASE_PASSWORD"]
        self._omegaPsi.authenticate(username, password)

        # Create the connection and get the database for Online Status
        self._online_status_connection = MongoClient("ds133762.mlab.com", 33762, connect = False)
        self._onlineStatus = self._online_status_connection["onlinestatus"]

        # Get the username and password to authenticate database access
        username = os.environ["ONLINE_STATUS_DATABASE_USERNAME"]
        password = os.environ["ONLINE_STATUS_DATABASE_PASSWORD"]
        self._onlineStatus.authenticate(username, password)

        # Keep track of different collections
        self._bot = self._omegaPsi.bot
        self._guilds = self._omegaPsi.guilds
        self._users = self._omegaPsi.users
        self._data = self._omegaPsi.data
        self._case_numbers = self._omegaPsi.case_numbers
        self._online_status = self._onlineStatus.onlinestatus

        self.bot = Bot(self._bot)
        self.guilds = Guild(self._guilds)
        self.users = User(self._users)
        self.data = Data(self._data)
        self.case_numbers = CaseNumber(self._case_numbers)
        self.online_status = OnlineStatus(self._online_status)

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