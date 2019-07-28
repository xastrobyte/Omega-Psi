from functools import partial

from category.globals import loop

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class OnlineStatus:
    def __init__(self, online_status):
        self._online_status = online_status

    # # # # # # # # # # # # # # # # # # # #

    async def get_user(self, user = None, *, user_id = None):
        
        # Default user data
        user_id = str(user.id) if user != None else str(user_id)
        default = {
            "_id": user_id,
            "listeners": {}
        }

        # Try loading the user
        user_data = await loop.run_in_executor(None,
            partial(
                self._online_status.users.find_one,
                {"_id": user_id}
            )
        )

        # If user_data is None, there is no user saved
        #   Create a new user
        #   Then setup the user using set_user
        if user_data == None:
            await loop.run_in_executor(None,
                partial(
                    self._online_status.users.insert_one,
                    {"_id": user_id}
                )
            )
            await self.set_user(user, default)
            return default
        
        # user_Data is not None, return the data
        return user_data
    
    async def set_user(self, user, data, *, user_id = None):
        
        # Set the user data
        user_id = str(user.id) if user != None else str(user_id)
        await loop.run_in_executor(None,
            partial(
                self._online_status.users.update_one,
                {"_id": user_id},
                {"$set": data},
                upsert = False
            )
        )
    
    # # # # # # # # # # # # # # # # # # # #

    async def get_listener(self, target= None, *, create = True, target_id = None):
        
        # Default listener data
        target_id = str(target.id) if target != None else str(target_id)
        default = {
            "_id": target_id,
            "users": {}
        }

        # Try loading the listener data
        listener_data = await loop.run_in_executor(None,
            partial(
                self._online_status.targets.find_one,
                {"_id": target_id}
            )
        )

        # If listener_data is None, there is no listener saved
        #   Create a new listener
        #   Then setup the listener using set_listener
        if listener_data == None and create:
            await loop.run_in_executor(None,
                partial(
                    self._online_status.targets.insert_one,
                    {"_id": target_id}
                )
            )
            await self.set_listener(target, default)
            return default
        
        # listener_data is None, return the data
        return listener_data
    
    async def set_listener(self, target, data, *, target_id = None):
        
        # Set the listener data
        target_id = str(target.id) if target != None else str(target_id)
        await loop.run_in_executor(None,
            partial(
                self._online_status.targets.update_one,
                {"_id": target_id},
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
    
    async def clear_listeners(self, user):

        # Get the user data
        user_data = await self.get_user(user)

        # Iterate through the listeners
        for listener in user_data["listeners"]:

            # Get the target data
            target_data = await self.get_listener(create = False, target_id = listener)

            # Remove the user if they are a listener of the target
            if target_data != None:
                if str(user.id) in target_data["users"]:
                    target_data["users"].pop(str(user.id))
            
                # Set the target data
                await self.set_listener(None, target_data, target_id = listener)
        
        # Clear the listeners dictionary
        user_data["listeners"] = {}
        
        # Set the user data
        await self.set_user(user, user_data)
    
    async def invalidate_listener(self, user, target_id):

        # Get the user data
        user_data = await self.get_user(user)

        # Check if the target is in the listeners for the user
        if str(target_id) in user_data["listeners"]:
            user_data["listeners"].pop(str(target_id))

            # Remove the user from the listeners users
            target_data = await self.get_listener(create = False, target_id = target_id)
            if target_data != None:
                if str(user.id) in target_data["users"]:
                    target_data["users"].pop(str(user.id))
            
                # Set the target data
                await self.set_listener(None, target_data, target_id = target_id)
        
        # Set the user data
        await self.set_user(user, user_data)
    
    async def listener_status(self, user, target):

        # Get the user data
        user_data = await self.get_user(user)

        # Check if the target exists as a listener
        if str(target.id) in user_data["listeners"]:
            return user_data["listeners"][str(target.id)]
        
        return False

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #