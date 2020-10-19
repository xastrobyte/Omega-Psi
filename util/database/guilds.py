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

    def get_guilds(self):
        """Synchronously retrieves the data for all guilds saved in the database

        Returns
        -------
            dict
                All the guilds saved in the database
        """
        guilds = list(self._guilds.find({}))
        return guilds

    def get_guild_sync(self, guild: Union[Guild, str]):
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
            "prefix": "o.",
            "music": {
                "playlists": {}
            }
        }

        # Get guild data
        guild_data = self._guilds.find_one({"_id": guild_id})
        if guild_data is None:
            self.set_guild_sync(guild_id, data, insert=True)
            guild_data = self.get_guild_sync(guild_id)
        guild_data = set_default(data, guild_data)
        return guild_data

    def set_guild_sync(self, guild: Union[Guild, str], guild_data, *, insert=False):
        """Synchronously sets the data for the specified guild

        Parameters
        -----------
            guild : str or Guild
                The ID of the guild or the Guild object
            guild_data : dict
                The JSON object of the guild data to set
        """
        guild_id = guild if isinstance(guild, str) else str(guild.id)
        
        if insert:
            self._guilds.insert_one(guild_data)
        else:
            self._guilds.update_one(
                {"_id": guild_id},
                {"$set": guild_data},
                upsert=False)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_guild(self, guild: Union[Guild, str]):
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

    async def set_guild(self, guild: Union[Guild, str], guild_data):
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

    def get_prefix_sync(self, guild: Union[Guild, str]):
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

    def set_prefix_sync(self, guild: Union[Guild, str], prefix):
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

    async def get_prefix(self, guild: Union[Guild, str]):
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

    async def set_prefix(self, guild: Union[Guild, str], prefix):
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

    def get_disabled_commands_sync(self, guild: Union[Guild, str]):
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

    def is_command_enabled_sync(self, guild: Union[Guild, str], command):
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

    def enable_command_sync(self, guild: Union[Guild, str], command):
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

    def disable_command_sync(self, guild: Union[Guild, str], command):
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

    async def get_disabled_commands(self, guild: Union[Guild, str]):
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

    async def is_command_enabled(self, guild: Union[Guild, str], command):
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

    async def enable_command(self, guild: Union[Guild, str], command):
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

    async def disable_command(self, guild: Union[Guild, str], command):
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

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Music Access Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_playlists_sync(self, guild: Union[Guild, str]) -> list:
        """Returns the playlists saved to the specified server

        :param guild: The server to get the playlists of
        """
        guild_data = self.get_guild_sync(guild)
        return guild_data["music"]["playlists"]
    
    def set_playlists_sync(self, guild: Union[Guild, str], playlists_data: dict):
        """Sets the playlists saved in the specified server

        :param playlists_data: The data for the playlists in this server
        """
        guild_data = self.get_guild_sync(guild)
        guild_data["music"]["playlists"] = playlists_data
        self.set_guild_sync(guild, guild_data)
    
    def create_playlist_sync(self, guild: Union[Guild, str], name: str):
        """Creates a new playlist in the specified server

        :param guild: The server to add the playlist to
        :param name: The name of the playlist
        """
        playlists_data = self.get_playlists_sync(guild)
        playlists_data[name] = []
        self.set_playlists_sync(guild, playlists_data)
    
    def delete_playlist_sync(self, guild: Union[Guild, str], name: str) -> str:
        """Deletes a playlist from the specified server

        :param guild: The server to delete the playlist from
        :param name: The playlist to delete
        """
        playlists_data = self.get_playlists_sync(guild)
        removed_playlist = None
        if name in playlists_data:
            removed_playlist = playlists_data.pop(name)
        self.set_playlists_sync(guild, playlists_data)
        return removed_playlist
    
    def get_playlist_sync(self, guild: Union[Guild, str], name: str) -> [dict, None]:
        """Retrieves a specific playlist from the specified server

        :param guild: The server to get the playlist from
        :param name: The name of the playlist to get
        """
        playlists_data = self.get_playlists_sync(guild)
        if name in playlists_data:
            return playlists_data[name]
        return None
    
    def set_playlist_sync(self, guild: Union[Guild, str], name: str, playlist_data: dict):
        """Sets the data for a specific playlist in a specified server

        :param guild: The server to set the playlist in
        :param name: The name of the playlist to set
        :param playlist_data: The data of the specified playlist
        """
        playlists_data = self.get_playlists_sync(guild)
        if name in playlists_data:
            playlists_data[name] = playlist_data
        self.set_playlists_sync(guild, playlists_data)
    
    def does_playlist_exist_sync(self, guild: Union[Guild, str], name: str):
        """Determines if a playlist exists in the specified guild

        :param guild: The server to check for the playlist
        :param name: The name of the playlist to check for
        """
        return self.get_playlist_sync(guild, name) is not None
    
    def add_song_to_playlist_sync(self, guild: Union[Guild, str], playlist: str, song: str):
        """Adds a song to a specified playlist in the specified server

        :param guild: The server to add the song to
        :param playlist: The playlist to add the song to
        :param song: The song to add
        """
        playlist_data = self.get_playlist_sync(guild, playlist)
        playlist_data.append(song)
        self.set_playlist_sync(guild, playlist, playlist_data)
    
    def remove_song_from_playlist_sync(self, guild: Union[Guild, str], playlist: str, index: int) -> str:
        """Removes a song from a specified playlist in the specified server

        :param guild: The server to remove the song from
        :param playlist: The playlist to remove the song from
        :param index: The index of the song to remove
        """
        playlist_data = self.get_playlist_sync(guild, playlist)
        removed_song = None
        if index < len(playlist_data):
            removed_song = playlist_data.pop(index)
        self.set_playlist_sync(guild, playlist, playlist_data)
        return removed_song
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_playlists(self, guild: Union[Guild, str]) -> list:
        """Returns the playlists saved to the specified server

        :param guild: The server to get the playlists of
        """
        return await loop.run_in_executor(None, self.get_playlists_sync, guild)
    
    async def set_playlists(self, guild: Union[Guild, str], playlists_data: dict):
        """Sets the playlists saved in the specified server

        :param playlists_data: The data for the playlists in this server
        """
        await loop.run_in_executor(None, self.set_playlists_sync, guild, playlists_data)
    
    async def create_playlist(self, guild: Union[Guild, str], name: str):
        """Creates a new playlist in the specified server

        :param guild: The server to add the playlist to
        :param name: The name of the playlist
        """
        await loop.run_in_executor(None, self.create_playlist_sync, guild, name)
    
    async def delete_playlist(self, guild: Union[Guild, str], name: str) -> str:
        """Deletes a playlist from the specified server

        :param guild: The server to delete the playlist from
        :param name: The playlist to delete
        """
        return await loop.run_in_executor(None, self.delete_playlist_sync, guild, name)
    
    async def get_playlist(self, guild: Union[Guild, str], name: str) -> [dict, None]:
        """Retrieves a specific playlist from the specified server

        :param guild: The server to get the playlist from
        :param name: The name of the playlist to get
        """
        return await loop.run_in_executor(None, self.get_playlist_sync, guild, name)
    
    async def set_playlist(self, guild: Union[Guild, str], name: str, playlist_data: dict):
        """Sets the data for a specific playlist in a specified server

        :param guild: The server to set the playlist in
        :param name: The name of the playlist to set
        :param playlist_data: The data of the specified playlist
        """
        return await loop.run_in_executor(None, self.set_playlist_sync, guild, name, playlist_data)
    
    async def does_playlist_exist(self, guild: Union[Guild, str], name: str) -> bool:
        """Determines if a playlist exists in the specified guild

        :param guild: The server to check for the playlist
        :param name: The name of the playlist to check for
        """
        return await loop.run_in_executor(None, self.does_playlist_exist_sync, guild, name)
    
    async def add_song_to_playlist(self, guild: Union[Guild, str], playlist: str, song: str):
        """Adds a song to a specified playlist in the specified server

        :param guild: The server to add the song to
        :param playlist: The playlist to add the song to
        :param song: The song to add
        """
        await loop.run_in_executor(None, self.add_song_to_playlist_sync, guild, playlist, song)
    
    async def remove_song_from_playlist(self, guild: Union[Guild, str], playlist: str, index: int) -> str:
        """Removes a song from a specified playlist in the specified server

        :param guild: The server to remove the song from
        :param playlist: The playlist to remove the song from
        :param index: The index of the song to remove
        """
        return await loop.run_in_executor(None, self.remove_song_from_playlist_sync, guild, playlist, index)