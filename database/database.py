import os

from pymongo import MongoClient

from database.bot import Bot
from database.guilds import Guild
from database.users import User
from database.data import Data
from database.case_numbers import CaseNumber
from database.online_status import OnlineStatus

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

database = Database()