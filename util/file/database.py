from pymongo import MongoClient
import asyncio, os

# Create event loop
loop = asyncio.get_event_loop()

class Database:

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Initialization
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self):
        """Initializes the Database to be used.
        """

        # Create the Connection and Get the Database for OmegaPsi
        self._connection = MongoClient("ds115244.mlab.com", 15244, connect = False)
        self._omegaPsi = self._connection["omegapsi"]

        # Get the Username and Password to authenticate database access
        username = os.environ["DATABASE_USERNAME"]
        password = os.environ["DATABASE_PASSWORD"]
        self._omegaPsi.authenticate(username, password)

        # Keep track of different collections
        self._bot = self._omegaPsi.bot
        self._servers = self._omegaPsi.servers
        self._users = self._omegaPsi.users

        self._data = self._omegaPsi.data
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Helper Methods - For Bot, Servers, and Users
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __add_bot(self):
        """A helper method that adds the bot information file.
        """
        result = self._bot.insert_one({"_id": "bot_information"})
        return result

    def __add_server(self, serverId):
        """A helper method that adds a server to the server file.

        Parameters:
            serverId (str): The ID of the Server to add.
        """
        result = self._servers.insert_one({"_id": str(serverId)})
        return result

    def __add_user(self, userId):
        """A helper method that adds a user to the User file.

        Parameters:
            userId (str): The ID of the User to add.
        """
        result = self._users.insert_one({"_id": str(userId)})
        return result
    

    def __get_bot(self, create = True):
        """A helper method that gets the bot's information file.

        Parameters:
            create (bool): Whether or not to create the file if it doesn't exist.
        """
        bot = self._bot.find_one({"_id": "bot_information"})

        if bot == None:

            if not create:
                raise Exception("There is no bot information saved.")
            
            self.__add_bot()
            return self.__get_bot(create)
        
        return bot

    def __get_server(self, serverId, create = True):
        """A helper method that gets the server information from the Server file.

        Parameters:
            serverId (str): The ID of the Server to get.
            create (bool): Whether or not to create the entry if it doesn't exist.
        """
        server = self._servers.find_one({"_id": serverId})

        if server == None:

            if not create:
                raise Exception("There is no server by that ID ({})".format(serverId))
            
            self.__add_server(serverId)
            return self.__get_server(serverId, create)
        
        return server

    def __get_user(self, userId, create = True):
        """A helper method that gets the user information from the User file.

        Parameters:
            userId (str): The ID of the User to get.
            create (bool): Whether or not to create the entry if it doesn't exist
        """
        user = self._users.find_one({"_id": userId})

        if user == None:

            if not create:
                raise Exception("There is no user by that ID ({}).".format(userId))
            
            self.__add_user(userId)
            return self.__get_user(userId, create)
        
        return user
    

    def __edit_bot(self, key, value):
        """A helper method that edits the bot information entry.

        Parameters:
            key (str): The key to change the value of.
            value (object): The value to set.
        """
        bot = self.__get_bot()

        bot[key] = value

        return self.__set_bot_info(bot)

    def __edit_server(self, serverId, key, value):
        """A helper method that edits the server information for the specified serverId

        Parameters:
            serverId (str): The ID of the Server to edit.
            key (str): The key to change the value of.
            value (object): The value to set.
        """
        server = self.__get_server(serverId)

        server[key] = value

        return self.__set_server_info(serverId, server)

    def __edit_user(self, userId, key, value):
        """A helper method that edits the user information for the specified userId

        Parameters:
            userId (str): The ID of the User to edit.
            key (str): The key to change the value of.
            value (object): The value to set.
        """
        user = self.__get_user(userId)

        user[key] = value

        return self.__set_user_info(userId, user)


    def __set_bot_info(self, botInfo):
        """A helper method that sets the bot information.

        Parameters:
            botInfo (object): The info to set.
        """
        botData = self._bot.update_one({"_id": "bot_information"}, {"$set": botInfo}, upsert = False)

        return botData.raw_result

    def __set_server_info(self, serverId, serverInfo):
        """A helper method that sets the server information.

        Parameters:
            serverId (str): The ID of the server to set.
            serverInfo (object): The info to set.
        """
        serverData = self._servers.update_one({"_id": serverId}, {"$set": serverInfo}, upsert = False)

        return serverData.raw_result

    def __set_user_info(self, userId, userInfo):
        """A helper method that sets the user information.

        Parameters:
            userId (str): The ID of the user to set.
            userInfo (object): The info to set.
        """
        userData = self._users.update_one({"_id": userId}, {"$set": userInfo}, upsert = False)

        return userData.raw_result

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Helper Methods - For Data
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __add_insult(self, level, insult, tags):
        """A helper method that adds an insult to the data information.

        Parameters:
            level (str): The level of the insult.
            insult (str): The insult to add.
            tags (list): The tags for the insult.
        """
        insultData = self.__get_insults()
        
        insultData[level].append({
            "value": insult,
            "level": level,
            "tags": tags
        })

        return self.__set_insults(insultData)
    
    def __add_pending_insult(self, user, level, insult, tags):
        """A helper method that adds a pending insult to the data information.

        Parameters:
            user (discord.User): The Discord User to notify if it gets added.
            level (str): The level of the insult to add.
            insult (str): The insult to add.
            tags (list): The tags for the insult.
        """
        pendingData = self.__get_pending_insults()

        pendingData["pending_insults"].append({
            "user": str(user.id),
            "value": insult,
            "level": level,
            "tags": tags,
            "addedTags": []
        })
        
        return self.__set_pending_insults(pendingData["pending_insults"])
    
    def __remove_pending_insult(self, value):
        """A helper method that removes a pending insult from the data information.

        Parameters:
            value (int): The index of the pending insult to remove.
        """
        pendingData = self.__get_pending_insults()

        pendingData["pending_insults"].pop(value)

        return self.__set_pending_insults(pendingData["pending_insults"])

    def __get_insults(self):
        """A helper method that gets the insults from the data information.
        """
        insultData = self._data.find_one({"_id": "insults"})
        return insultData
    
    def __get_pending_insults(self):
        """A helper method that gets the pending insults from the data information.
        """
        pendingData = self._data.find_one({"_id": "pending_insults"})
        return pendingData

    def __set_insults(self, insults):
        """A helper method that sets the insults in the data information.

        Parameters:
            insults (dict): The insults info to set.
        """
        insultData = self._data.update_one({"_id": "insults"}, {"$set": insults}, upsert = False)
        return insultData.raw_result
    
    def __set_pending_insults(self, pendingInsults):
        """A helper method that sets the pending insults in the data information.

        Parameters:
            pendingInsults (dict): The pending insults info to set.
        """
        pendingData = self._data.update_one({"_id": "pending_insults"}, {"$set": {"pending_insults": pendingInsults}}, upsert = False)
        return pendingData.raw_result
    

    def __get_hangman_words(self):
        """A helper method that gets the hangman words from the data information.
        """
        hangmanData = self._data.find_one({"_id": "hangman"})
        return hangmanData


    def __get_scramble_words(self):
        """A helper method that gets the scramble words from the data information.
        """
        scrambleData = self._data.find_one({"_id": "scramble"})
        return scrambleData
    
    
    def __get_lang(self):
        """A helper method that gets the language codes from the data information.
        """
        langData = self._data.find_one({"_id": "lang"})
        return langData
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Methods - For Bot, Servers, and Users
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def addBot(self):
        """Adds the bot information to the database.
        """
        return self.__add_bot()
    
    def getBot(self, create = True):
        """Gets the bot information from the database.

        Parameters:
            create (bool): Whether or not to create the entry if it doesn't exist.
        """
        return self.__get_bot(create)
    
    def editBot(self, key, value):
        """Edits the bot information in the database.

        Parameters:
            key (str): The key to set the value of.
            value (object): The value to set.
        """
        return self.__edit_bot(key, value)

    def setBot(self, botInfo):
        """Sets the bot information in the database.

        Parameters:
            botInfo (dict): The dictionary to set for the bot information.
        """
        return self.__set_bot_info(botInfo)
    
    
    def addServer(self, serverId):
        """Adds the server information to the database.

        Parameters:
            serverId (str): The ID of the Server to add.
        """
        return self.__add_server(serverId)
    
    def getServer(self, serverId, create = True):
        """Gets the server information from the database.

        Parameters:
            serverId (str): The ID of the Server to get.
            create (bool): Whether or not to create the entry if it doesn't exist.
        """
        return self.__get_server(serverId, create)
    
    def editServer(self, serverId, key, value):
        """Edits the server information in the database.

        Parameters:
            serverId (str): The ID of the Server to edit.
            key (str): The key to set the value of.
            value (object): The value to set.
        """
        return self.__edit_server(serverId, key, value)
    
    def setServer(self, serverId, serverInfo):
        """Sets the server information in the database.

        Parameters:
            serverId (str): The ID of the Server to set.
            serverInfo (dict): The dictionary to set for the server information.
        """
        return self.__set_server_info(serverId, serverInfo)
    
    
    def addUser(self, userId):
        """Adds the user information to the database.

        Parameters:
            userId (str): The ID of the User to add.
        """
        return self.__add_user(userId)
    
    def getUser(self, userId, create = True):
        """Gets the user information from the database.

        Parameters:
            userId (str): The ID of the User to get.
            create (bool): Whether or not to create the entry if it doesn't exist.
        """
        return self.__get_user(userId, create)
    
    def editUser(self, userId, key, value):
        """Edits the user information from the database.

        Parameters:
            userId (str): The ID of the User to edit.
            key (str): The key to set the value of.
            value (object): The value to set.
        """
        return self.__edit_user(userId, key, value)
    
    def setUser(self, userId, userInfo):
        """Sets the user information in the database.

        Parameters:
            userId (str): The ID of the User to set.
            userInfo (dict): The dictionary to set for the user information.
        """
        return self.__set_user_info(userId, userInfo)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Methods - For Data
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def addInsult(self, level, insult, tags):
        """Adds an insult to the database.

        Parameters:
            level (str): The level of the insult.
            insult (str): The insult to add.
            tags (list): The tags for the insult.
        """
        return self.__add_insult(level, insult, tags)
    
    def addPendingInsult(self, user, level, insult, tags):
        """Adds a pending insult to the database.

        Parameters:
            user (discord.User): The Discord User to message once it's approved.
            level (str): The insult level to add the insult to.
            insult (str): The insult to add to the pending list.
            tags (list): The tags for the insult.
        """
        return self.__add_pending_insult(user, level, insult, tags)
    
    def removePendingInsult(self, value):
        """Removes a pending insult from the database.

        Parameters:
            value (int): The index of the pending insult to remove.
        """
        return self.__remove_pending_insult(value)

    def getInsults(self):
        """Gets the insults from the database.
        """
        return self.__get_insults()
    
    def getPendingInsults(self):
        """Gets the pending insults from the database.
        """
        return self.__get_pending_insults()
    
    def setPendingInsults(self, pendingInsults):
        """Sets the pending insults.
        """
        return self.__set_pending_insults(pendingInsults)
    

    def getHangmanWords(self):
        """Gets the hangman words from the database.
        """
        return self.__get_hangman_words()


    def getScrambleWords(self):
        """Gets the scramble words from the database.
        """
        return self.__get_scramble_words()


    def getLang(self):
        """Gets the country codes from the database.
        """
        return self.__get_lang()
    
    
omegaPsi = Database()