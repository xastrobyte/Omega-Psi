import math
import youtube_dl

from discord import VoiceChannel, Embed
from discord.ext.commands import Cog, command, group, Context, Bot
from discord.ext.commands import NoPrivateMessage

from cogs.music.errors import YTDLError
from cogs.music.util import VoiceState, YTDLSource, Song
from cogs.predicates import guild_manager
from cogs.errors import (
    NOT_IN_VOICE_CHANNEL_ERROR, ALREADY_IN_VOICE_CHANNEL_ERROR, EMPTY_QUEUE_ERROR,
    ALREADY_VOTED_ERROR, NOTHING_PLAYING_ERROR, INVALID_VOLUME_ERROR,
    MUSIC_NOT_FOUND_ERROR, get_error_message)

from util.discord import get_embed_color
from util.database.database import database

# Silence useless bug reports messages
youtube_dl.utils.bug_reports_message = lambda: ''

class Music(Cog, name="music"):
    """A way to listen to music!"""
    def __init__(self, bot: Bot):
        self.bot = bot
        self.voice_states = {}

    # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_voice_state(self, ctx: Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: Context):
        if not ctx.guild:
            raise NoPrivateMessage('This command can\'t be used in DM channels.')

        return True

    async def cog_before_invoke(self, ctx: Context):
        ctx.voice_state = self.get_voice_state(ctx)

    @command(
        name='join',
        description="Forces Omega Psi to join whichever voice channel you're in!",
        cog_name="music"
    )
    async def join(self, ctx: Context):
        """Joins a voice channel.

        :param ctx: The context of where the message was sent
        """

        # Check if the user is in a voice channel
        if ctx.author.voice:
            destination = ctx.author.voice.channel
            ctx.voice_state.voice = await destination.connect()

    @command(
        name='summon',
        description="Summons the bot to a voice channel. If there was none specified, it'll join yours!",
        cog_name="music"
    )
    @guild_manager()
    async def summon(self, ctx: Context, *, channel: VoiceChannel = None):
        """Summons the bot to a voice channel.
        If no channel was specified, it joins your channel.

        :param ctx: The context of where the message was sent
        :param channel: The voice channel for Omega Psi to join
        """

        # Check if the user is not in a voice channel
        if not channel and not ctx.author.voice:
            await ctx.send(embed=NOT_IN_VOICE_CHANNEL_ERROR)
        
        # The user is in a voice channel
        else:
            destination = channel or ctx.author.voice.channel
            if ctx.voice_state.voice:
                await ctx.voice_state.voice.move_to(destination)
                return

            ctx.voice_state.voice = await destination.connect()

    @command(
        name='leave', aliases=['disconnect'],
        description = "Leaves the voice channel and clears your queue of songs",
        cog_name="music"
    )
    @guild_manager()
    async def leave(self, ctx: Context):
        """Clears the queue and leaves the voice channel.

        :param ctx: The context of where the message was sent
        """

        if not ctx.voice_state.voice:
            await ctx.send(embed = NOT_IN_VOICE_CHANNEL_ERROR)

        else:
            await ctx.voice_state.stop()
            del self.voice_states[ctx.guild.id]

    @command(
        name='volume',
        description = "Sets the volume of the music!",
        cog_name="music"
    )
    async def volume(self, ctx: Context, *, volume=None):
        """Sets the volume of the player.

        :param ctx: The context of where the message was sent
        :param volume: The volume to set the music of
        """
        
        try:
            volume = int(volume)
            if not ctx.voice_state.is_playing:
                await ctx.send(embed=NOTHING_PLAYING_ERROR)

            elif volume < 0 or volume > 100:
                await ctx.send(embed=INVALID_VOLUME_ERROR(volume))

            else:
                ctx.voice_state.volume = volume / 100
                await ctx.send('Volume of the player set to {}%'.format(volume))
        except ValueError:
            await ctx.send(embed=get_error_message(
                "That's an invalid volume :eyes:"
            ))

    @command(
        name='now', aliases=['current', 'playing'],
        description="Shows you the current song that is playing",
        cog_name="music"
    )
    async def now(self, ctx: Context):
        """Displays the currently playing song.

        :param ctx: The context of where the message was sent
        """

        if ctx.voice_state.voice.is_playing():
            await ctx.send(embed=ctx.voice_state.current.create_embed(
                await get_embed_color(ctx.author)
            ))
        else:
            await ctx.send(embed=NOTHING_PLAYING_ERROR)

    @command(
        name='pause',
        description="Pauses the current song",
        cog_name="music"
    )
    @guild_manager()
    async def pause(self, ctx: Context):
        """Pauses the currently playing song.

        :param ctx: The context of where the message was sent
        """
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            await ctx.message.add_reaction('⏯')

    @command(
        name='resume',
        description="Resumes playing the current song",
        cog_name="music"
    )
    @guild_manager()
    async def resume(self, ctx: Context):
        """Resumes a currently paused song."""

        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.message.add_reaction('⏯')

    @command(
        name='stop',
        description="Stops playing music and clears the queue",
        cog_name="music"
    )
    @guild_manager()
    async def stop(self, ctx: Context):
        """Stops playing song and clears the queue.

        :param ctx: The context of where the message was sent
        """

        ctx.voice_state.songs.clear()

        if ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()
            await ctx.message.add_reaction('⏹')

    @command(
        name='skip',
        description=(
            "Skips the currently playing song. If you were not the requester of the song, " +
            "there will be a vote where you need 3 people to skip it"
        ),
        cog_name="music"
    )
    async def skip(self, ctx: Context):
        """Vote to skip a song. The requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send(embed=NOTHING_PLAYING_ERROR)

        voter = ctx.message.author
        if voter.id == ctx.voice_state.current.requester.id:
            await ctx.message.add_reaction('⏭')
            ctx.voice_state.skip()

        elif voter.id not in ctx.voice_state.skip_votes:
            ctx.voice_state.skip_votes.add(voter.id)
            total_votes = len(ctx.voice_state.skip_votes)

            if total_votes >= 3:
                await ctx.message.add_reaction('⏭')
                ctx.voice_state.skip()
            else:
                await ctx.send('Skip vote added, currently at **{}/3**'.format(total_votes))

        else:
            await ctx.send(embed=ALREADY_VOTED_ERROR)

    @command(
        name='queue',
        description="Show the queue of which songs are next!",
        cog_name="music"
    )
    async def queue(self, ctx: Context, *, page=None):
        """Shows the player's queue.

        You can optionally specify the page to show. Each page contains 10 elements.
        """
        
        if page is None:
            page = 1

        try:
            page = int(page)
            if len(ctx.voice_state.songs) == 0:
                return await ctx.send(embed=EMPTY_QUEUE_ERROR)

            items_per_page = 10
            pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

            start = (page - 1) * items_per_page
            end = start + items_per_page

            queue = ''
            for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
                queue += '`{0}.` [**{1.source.title}**]({1.source.url})\n'.format(i + 1, song)

            embed = Embed(
                description='**{} tracks:**\n\n{}'.format(
                    len(ctx.voice_state.songs), 
                    queue
                )).set_footer(
                    text='Viewing page {}/{}'.format(page, pages)
                )
            await ctx.send(embed=embed)
        except TypeError:
            await ctx.send(embed=get_error_message("That is not a valid page number!"))

    @command(
        name='shuffle',
        description="Shuffles the current queue!",
        cog_name="music"
    )
    async def shuffle(self, ctx: Context):
        """Shuffles the queue."""

        if len(ctx.voice_state.songs) == 0:
            await ctx.send(embed=EMPTY_QUEUE_ERROR)

        else:
            ctx.voice_state.songs.shuffle()
            await ctx.message.add_reaction('✅')

    @command(
        name='remove',
        description="Allows you to remove a song from the queue",
        cog_name="music"
    )
    async def remove(self, ctx: Context, index: int):
        """Removes a song from the queue at a given index."""

        if len(ctx.voice_state.songs) == 0:
            await ctx.send(empty=EMPTY_QUEUE_ERROR)

        else:
            ctx.voice_state.songs.remove(index - 1)
            await ctx.message.add_reaction('✅')

    @command(
        name='loop',
        description="Allows you to loop the current song. Call it again to stop looping it!",
        cog_name="music"
    )
    async def loop(self, ctx: Context):
        """Loops the currently playing song.

        Invoke this command again to unloop the song.
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send(embed=NOTHING_PLAYING_ERROR)

        # Inverse boolean value to loop and unloop.
        else:
            ctx.voice_state.loop = not ctx.voice_state.loop
            await ctx.message.add_reaction('✅')

    @command(
        name='play',
        description="Plays a song you request!",
        cog_name="music"
    )
    async def play(self, ctx: Context, *, search: str = None):
        """Plays a song.

        If there are songs in the queue, this will be queued until the
        other songs finished playing.

        This command automatically searches from various sites if no URL is provided.
        A list of these sites can be found here: https://rg3.github.io/youtube-dl/supportedsites.html
        """

        # Check if the search parameter is not given
        if search is None:
            await ctx.send(embed=get_error_message(
                "You must specify a song of some sort to play!"
            ))

        # There was something given
        else:
            if not ctx.voice_state.voice:
                await ctx.invoke(self.join)
            
            await self.play_song(ctx, [search])
    
    @group(
        name="playlist",
        description="Lets you create, view, or play a playlist saved in the server!",
        cog_name="music"
    )
    async def playlist(self, ctx: Context):
        if not ctx.invoked_subcommand:
            await ctx.send(embed=get_error_message(
                "You must specify a subcommand! Try `{}help playlist` for more info!".format(
                    await database.guilds.get_prefix(ctx.guild)
                )
            ))
        
    @playlist.command(
        name="view",
        description = "Lets you view the saved playlists in this server!",
        cog_name="music"
    )
    async def playlist_view(self, ctx: Context, *, name: str = None):
        
        # Check if no playlist name is specified, show all playlist names
        if name is None:
            playlists_data = await database.guilds.get_playlists(ctx.guild)
            no_playlists = len(playlists_data) == 0
            await ctx.send(embed = Embed(
                title = "{}Saved Playlists".format("No " if no_playlists else ""),
                description = "\n".join(list(playlists_data.keys())) if not no_playlists else "_ _",
                colour = await get_embed_color(ctx.author)
            ))
        
        elif await database.guilds.does_playlist_exist(ctx.guild, name):
            playlist_data = await database.guilds.get_playlist(ctx.guild, name)
            await ctx.send(embed = Embed(
                title = name,
                description = "\n".join([
                    f"`{i + 1}`.) *`{playlist_data[i]}`*" 
                    for i in range(len(playlist_data))
                ]) if len(playlist_data) > 0 else "No Songs",
                colour = await get_embed_color(ctx.author)
            ))
        
        else:
            await ctx.send(embed=get_error_message("There is no playlist with that name!"))
    
    @playlist.command(
        name="create",
        description="Lets you create a playlist to save to play in the future!",
        cog_name="music"
    )
    @guild_manager()
    async def playlist_create(self, ctx: Context, *, name: str = None):
        
        # If the name is not given, tell the user to specify one
        if name is None:
            await ctx.send(embed=get_error_message(
                "You must specify a playlist name!"
            ))
        
        # Check that the name is alphanumeric
        elif name.isalnum():
            await database.guilds.create_playlist(ctx.guild, name)
            await ctx.send(embed=Embed(
                title = "Playlist Created!",
                description = f"The playlist `{name}` was created!",
                colour = await get_embed_color(ctx.author)
            ))
        
        # Otherwise, create the playlist in the server database
        else:
            await ctx.send(embed=get_error_message(
                "You can't set a playlist name that isn't alphanumeric :eyes:"
            ))
            
    
    @playlist.command(
        name="delete",
        description="Deletes a specified playlist from your server.",
        cog_name="music"
    )
    @guild_manager()
    async def playlist_delete(self, ctx: Context, *, name: str = None):
        
        # If the name is not given, tell the user to specify one
        if name is None:
            await ctx.send(embed=get_error_message(
                "You must specify a playlist name to delete it."
            ))
        
        # Verify the playlist exists
        elif await database.guilds.does_playlist_exist(ctx.guild, name):
            confirm_message = await ctx.send(embed=Embed(
                title = "Confirm Delete",
                description = f"Are you __**_sure_**__ you want to delete `{name}`?",
                colour = await get_embed_color(ctx.author)
            ))
            await confirm_message.add_reaction("✅")
            await confirm_message.add_reaction("❌")
            reaction, user = await self.bot.wait_for("reaction_add", check = lambda r, u: (
                str(r) in ["✅", "❌"] and
                u.id == ctx.author.id and
                r.message.id == confirm_message.id
            ))
            await confirm_message.delete()
            if str(reaction) == "✅":
                await database.guilds.delete_playlist(ctx.guild, name)
                await ctx.send(
                    embed=Embed(
                        title = f"Playlist {name} Deleted",
                        description = "_ _",
                        colour = await get_embed_color(ctx.author)
                    )
                )
            else:
                await ctx.send(
                    embed = Embed(
                        title = f"Playlist {name} Not Deleted",
                        description = "smart move :ok_hand:",
                        colour = await get_embed_color(ctx.author)
                    )
                )
        
        # The playlist does not exist
        else:
            await ctx.send(embed=get_error_message("That playlist does not exist!"))
    
    @playlist.command(
        name="add",
        description="Add a song to a playlist you specify!",
        cog_name="music"
    )
    @guild_manager()
    async def playlist_add(self, ctx: Context, playlist: str = None, *, song: str = None):
        
        # Check if no playlist is given
        if playlist is None:
            await ctx.send(embed=get_error_message(
                "You must specify a playlist name to add a song to!"
            ))
        
        # Check if no song name is given
        elif song is None:
            await ctx.send(embed=get_error_message(
                "There is no song name given! I can't add a nonexistent song!"
            ))
        
        # Check if the playlist given is valid
        elif await database.guilds.does_playlist_exist(ctx.guild, playlist):
            await database.guilds.add_song_to_playlist(ctx.guild, playlist, song)
            await ctx.send(embed=Embed(
                title = "Song Added!",
                description = f"The song `{song}` was added to the playlist `{playlist}`!",
                colour = await get_embed_color(ctx.author)
            ))
        
        # If it's not valid, let the user know
        else:
            await ctx.send(embed=get_error_message(
                "That is not a valid playlist name!"
            ))
    
    @playlist.command(
        name="remove",
        description="Remove a song from a playlist you specify!",
        cog_name="music"
    )
    @guild_manager()
    async def playlist_remove(self, ctx: Context, playlist = None, *, index = None):
        
        # Check if the playlist is not given
        if playlist is None:
            await ctx.send(embed=get_error_message(
                "You must specify a playlist to remove a song from."
            ))
        
        # Check if a song is not given
        elif index is None:
            await ctx.send(embed=get_error_message(
                "You must specify the song number to remove."
            ))
        
        # Check if the playlist exists
        elif await database.guilds.does_playlist_exist(ctx.guild, playlist):
            try:
                index = int(index)
                song = await database.guilds.remove_song_from_playlist(ctx.guild, playlist, index)
                await ctx.send(embed=Embed(
                    title = "Song {}Removed!".format("" if song is not None else "Not "),
                    description = f"`{song}` was removed from the playlist `{playlist}`"
                        if song is not None else "That song number does not exist!",
                    colour = await get_embed_color(ctx.author)
                ))
            except TypeError:
                await ctx.send(embed=get_error_message("That's not an integer ..."))
        
        # The playlist does not exist
        else:
            await ctx.send(embed=get_error_message("That playlist does not exist!"))
    
    @playlist.command(
        name="play",
        description="Plays a playlist you specify!",
        cog_name="music"
    )
    async def playlist_play(self, ctx: Context, *, playlist: str = None):
        
        # Check if the playlist name was given
        if playlist is None:
            await ctx.send(embed=get_error_message(
                "You must specify the name of the playlist to play!"
            ))
        
        # Verify that the playlist exists
        elif await database.guilds.does_playlist_exist(ctx.guild, playlist):
            if not ctx.voice_state.voice:
                await ctx.invoke(self.join)

            # Iterate through all the songs and "play" them
            #   any songs that are not ready to be played yet will be queued
            songs = await database.guilds.get_playlist(ctx.guild, playlist)
            await self.play_song(ctx, songs, no_queue_message = True)
        
        # The playlist does not exist
        else:
            await ctx.send(embed=get_error_message("That playlist does not exist!"))
        
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

    async def play_song(self, ctx: Context, songs: list, *, no_queue_message: bool = False):
        """This will handle the logic behind adding a song, or songs, to the queue
        both through the use of a command or programmatically.

        :param ctx: The context of where the play the song
        :param songs: A list of songs to add
        :param no_queue_message: Whether or not to display a message showing which songs have been queued
        """

        for song in songs:
            async with ctx.typing():
                try:
                    source = await YTDLSource.create_source(ctx, song, loop=self.bot.loop)
                except YTDLError:
                    await ctx.send(embed=MUSIC_NOT_FOUND_ERROR(song))
                else:
                    song = Song(source)
                    song_embed = song.create_embed(await get_embed_color(ctx.author))
                    song_embed.title = "Added to Queue!"

                    await ctx.voice_state.songs.put(song)
                    if ctx.voice_state.current is not None and not no_queue_message:
                        await ctx.send(embed=song_embed)

    @join.before_invoke
    @play.before_invoke
    async def ensure_voice_state(self, ctx: Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send(embed=NOT_IN_VOICE_CHANNEL_ERROR)

        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                await ctx.send(embed=ALREADY_IN_VOICE_CHANNEL_ERROR)

def setup(bot):
    bot.add_cog(Music(bot))