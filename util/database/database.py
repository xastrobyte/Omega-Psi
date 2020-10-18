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
    """The Database class collects all the functions from each of the
    specific database classes into one to make it easier to use
    """
    def __init__(self):

        # Create the connection to the Omega Psi database and authenticate
        self.client = MongoClient(f"mongodb+srv://{environ['DATABASE_USERNAME']}:{environ['DATABASE_PASSWORD']}@fellowhashbrown.orymo.gcp.mongodb.net/omegapsi?retryWrites=true&w=majority")
        self.omegapsi = self.client.omegapsi

        self.bot = Bot(self.omegapsi["bot"])
        self.data = Data(self.omegapsi["data"])
        self.case_numbers = CaseNumber(self.omegapsi["case_numbers"])
        self.guilds = Guild(self.omegapsi["guilds"])
        self.users = User(self.omegapsi["users"])


database = Database()
