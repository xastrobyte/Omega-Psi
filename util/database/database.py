from os import environ
from pymongo import MongoClient

from util.database.bot import Bot
from util.database.case_numbers import CaseNumber
from util.database.data import Data
from util.database.guilds import Guild
from util.database.users import User

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class Database:
    def __init__(self):

        # Create the connection to the Omega Psi database and authenticate
        self.connection = MongoClient("ds115244.mlab.com", 15244, connect = False, retryWrites = False)
        self._omega_psi = self.connection["omegapsi"]

        self._omega_psi.authenticate(
            environ["DATABASE_USERNAME"], 
            environ["DATABASE_PASSWORD"]
        )

        # Keep track of the collections
        self._bot = self._omega_psi.bot
        self._guilds = self._omega_psi.guilds
        self._users = self._omega_psi.users
        self._data = self._omega_psi.data
        self._case_numbers = self._omega_psi.case_numbers

        # Give each collection their own database class to help split it up by data types
        self.bot = Bot(self._bot)
        self.guilds = Guild(self._guilds)
        self.users = User(self._users)
        self.data = Data(self._data)
        self.case_numbers = CaseNumber(self._case_numbers)

database = Database()