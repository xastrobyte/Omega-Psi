from datetime import datetime
from functools import partial

from category.globals import loop

from util.misc import set_default

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class User:
    def __init__(self, users):
        self._users = users
    
    def get_user_sync(self, user):

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
            "ifttt": {
                "active": False,
                "webhook_key": None
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
        user_data = self._users.find_one({"_id": str(user.id)})

        # User data is None; Create user data
        if user_data == None:
            self._users.insert_one({"_id": str(user.id)})
            self.set_user(user, data)
            user_data = data
        
        # set defaults
        user_data = set_default(data, user_data)
        return user_data

    def set_user_sync(self, user, data):

        # Set the user data
        self._users.update_one({"_id": str(user.id)}, {"$set": data}, upsert = False)
    
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
            "ifttt": {
                "active": False,
                "webhook_key": None
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

    async def get_ifttt(self, user):

        # Get user data
        user_data = await self.get_user(user)

        return user_data["ifttt"]
    
    async def set_ifttt(self, user, ifttt):

        # Get user data
        user_data = await self.get_user(user)

        user_data["ifttt"] = ifttt

        # Set user data
        await self.set_user(user, user_data)
    
    async def ifttt_active(self, user):

        # Get IFTTT data
        ifttt_data = await self.get_ifttt(user)

        return ifttt_data["active"]
    
    async def toggle_ifttt(self, user):

        # Get IFTTT data
        ifttt_data = await self.get_ifttt(user)

        ifttt_data["active"] = not ifttt_data["active"]

        # Set IFTTT data
        await self.set_ifttt(user, ifttt_data)

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