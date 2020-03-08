from discord import Guild
from typing import Union

from cogs.globals import loop
from util.misc import set_default

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class Guild:
    def __init__(self, guilds):
        self._guilds = guilds
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    def get_guild_sync(self, guild : Union[Guild, str]):
        """Synchronously retrieves the data for the specified guild

        Parameters
        ----------
            guild : str or Guild
                The ID of the guild or the Guild object
        
        Returns
        -------
            dict
                The data for the specified Guild
        """
        guild_id = guild if isinstance(guild, str) else str(guild.id)

        # Default
        data = {
            "_id": guild_id,
            "disabled_commands": [],
            "prefix": "o."
        }

        # Get guild data
        guild_data = self._guilds.find_one({"_id": guild_id})
        if not guild_data:
            self._guilds.insert_one({"_id": guild_id})
            self.set_guild_sync(guild_id, data)
            guild_data = data
        
        guild_data = set_default(data, guild_data)
        return guild_data

    def set_guild_sync(self, guild : Union[Guild, str], guild_data):
        """Synchronously sets the data for the specified guild

        Parameters
        -----------
            guild : str or Guild
                The ID of the guild or the Guild object
            guild_data : dict
                The JSON object of the guild data to set
        """
        guild_id = guild if isinstance(guild, str) else str(guild.id)
        self._guilds.update_one({"_id": guild_id}, {"$set": guild_data}, upsert = False)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_guild(self, guild : Union[Guild, str]):
        """Asynchronously retrieves the data for the specified guild

        Parameters
        ----------
            guild : str or Guild
                The ID of the guild or the Guild object
        
        Returns
        -------
            dict
                The data for the specified Guild
        """
        return await loop.run_in_executor(None, self.get_guild_sync, guild)
    
    async def set_guild(self, guild : Union[Guild, str], guild_data):
        """Asynchronously sets the data for the specified guild

        Parameters
        -----------
            guild : str or Guild
                The ID of the guild or the Guild object
            guild_data : dict
                The JSON object of the guild data to set
        """
        await loop.run_in_executor(None, self.set_guild_sync, guild, guild_data)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Prefix Access Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_prefix_sync(self, guild : Union[Guild, str]):
        """Synchronously retrieves the prefix for the specified guild

        Parameters
        ----------
            guild : str or Guild
                The ID of the guild or the Guild object
        
        Returns
        -------
            str
                The prefix for the Guild
        """
        guild_data = self.get_guild_sync(guild)
        return guild_data["prefix"]
    
    def set_prefix_sync(self, guild : Union[Guild, str], prefix):
        """Synchronously sets the prefix for the specified guild

        Parameters
        ----------
            guild : str or Guild
                The ID of the guild or the Guild object
            prefix : str
                The prefix to set
        """
        guild_data = self.get_guild_sync(guild)
        guild_data["prefix"] = prefix
        self.set_guild_sync(guild, guild_data)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_prefix(self, guild : Union[Guild, str]):
        """Asynchronously retrieves the prefix for the specified guild

        Parameters
        ----------
            guild : str or Guild
                The ID of the guild or the Guild object
        
        Returns
        -------
            str
                The prefix for the Guild
        """
        return await loop.run_in_executor(None, self.get_prefix_sync, guild)
    
    async def set_prefix(self, guild : Union[Guild, str], prefix):
        """Asynchronously sets the prefix for the specified guild

        Parameters
        ----------
            guild : str or Guild
                The ID of the guild or the Guild object
            prefix : str
                The prefix to set
        """
        await loop.run_in_executor(None, self.set_prefix_sync, guild, prefix)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Enabled/Disabled Commands Access Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_disabled_commands_sync(self, guild : Union[Guild, str]):
        """Synchronously returns a list of disabled commands in the specified Guild

        Parameters
        ----------
            guild : str or Guild
                The ID of the guild or the Guild object

        Returns
        -------
            list
                A list of disabled commands in the entire bot
        """
        guild_data = self.get_guild_sync(guild)
        return guild_data["disabled_commands"]

    def is_command_enabled_sync(self, guild : Union[Guild, str], command):
        """Synchronously returns whether or not the specified command is enabled in this Guild

        Parameters
        ----------
            guild : str or Guild
                The ID of the guild or the Guild object
            command_name : str
                The command to check
        
        Returns
        -------
            bool
                Whether or not the command is enabled
        """
        guild_data = self.get_guild_sync(guild)
        return command not in guild_data["disabled_commands"]
    
    def enable_command_sync(self, guild : Union[Guild, str], command):
        """Synchronously disables the specified command

        Parameters
        ----------
            command_name : str
                The command to enable
        
        Returns
        -------
            bool
                Whether or not the command was enabled
        """
        guild_data = self.get_guild_sync(guild)
        if command in guild_data["disabled_commands"]:
            guild_data["disabled_commands"].remove(command)
            self.set_guild_sync(guild, guild_data)
            return True
        return False
    
    def disable_command_sync(self, guild : Union[Guild, str], command):
        """Synchronously disables the specified command

        Parameters
        ----------
            command_name : str
                The command to disable
        
        Returns
        -------
            bool
                Whether or not the command was disabled
        """
        guild_data = self.get_guild_sync(guild)
        if command not in guild_data["disabled_commands"]:
            guild_data["disabled_commands"].append(command)
            self.set_guild_sync(guild, guild_data)
            return True
        return False
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_disabled_commands(self, guild : Union[Guild, str]):
        """Aynchronously returns a list of disabled commands in the specified Guild

        Parameters
        ----------
            guild : str or Guild
                The ID of the guild or the Guild object

        Returns
        -------
            list
                A list of disabled commands in the entire bot
        """
        return await loop.run_in_executor(None, self.get_disabled_commands_sync, guild)

    async def is_command_enabled(self, guild : Union[Guild, str], command):
        """Asynchronously returns whether or not the specified command is enabled in this Guild

        Parameters
        ----------
            guild : str or Guild
                The ID of the guild or the Guild object
            command_name : str
                The command to check
        
        Returns
        -------
            bool
                Whether or not the command is enabled
        """
        return await loop.run_in_executor(None, self.is_command_enabled_sync, guild, command)
    
    async def enable_command(self, guild : Union[Guild, str], command):
        """Asynchronously disables the specified command

        Parameters
        ----------
            command_name : str
                The command to enable
        
        Returns
        -------
            bool
                Whether or not the command was enabled
        """
        return await loop.run_in_executor(None, self.enable_command_sync, guild, command)
    
    async def disable_command(self, guild : Union[Guild, str], command):
        """Asynchronously disables the specified command

        Parameters
        ----------
            command_name : str
                The command to disable
        
        Returns
        -------
            bool
                Whether or not the command was disabled
        """
        return await loop.run_in_executor(None, self.disable_command_sync, guild, command)