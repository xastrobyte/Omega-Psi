from functools import partial

from category.globals import loop

from util.misc import set_default

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
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_prefix(self, guild):

        # Open guild information
        guild_data = await self.get_guild(guild)

        return guild_data["prefix"]
    
    async def set_prefix(self, guild, prefix):

        # Open guild information
        guild_data = await self.get_guild(guild)

        guild_data["prefix"] = prefix

        await self.set_guild(guild, guild_data)