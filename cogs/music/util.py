import asyncio

from async_timeout import timeout
from functools import partial
from itertools import islice
from random import shuffle

from discord import PCMVolumeTransformer, FFmpegPCMAudio
from discord import Embed
from discord.ext.commands import Context, Bot
from youtube_dl import YoutubeDL

from cogs.music.errors import YTDLError, VoiceError
from util.discord import get_embed_color

class YTDLSource(PCMVolumeTransformer):
    """A Youtube-DL source class to control music functionality
    in Discord
    """
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = YoutubeDL(YTDL_OPTIONS)

    def __init__(self, ctx: Context, source: FFmpegPCMAudio, *, data: dict, volume: float = 0.5):
        super().__init__(source, volume)

        self.requester = ctx.author
        self.channel = ctx.channel
        self.data = data

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        date = data.get('upload_date')
        self.upload_date = date[6:8] + '.' + date[4:6] + '.' + date[0:4]
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return '**{0.title}** by **{0.uploader}**'.format(self)

    @classmethod
    async def create_source(cls, ctx: Context, search: str, *, loop: asyncio.BaseEventLoop = None):
        """Creates a songs source from the specified search parameters

        :param cls: 
        :param ctx: The context of where the song comes from
        :param loop: The async loop to use
        """

        # Retrieve the loop or create a new one, then call the YTDL
        #   to retrieve the song from the given search parameter
        loop = loop or asyncio.get_event_loop()
        partial_data = partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial_data)

        # Check if anything was found.
        #   if not, raise an error
        #   if so, save the first result
        if data is None:
            raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))
        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError('Couldn\'t find anything that matches `{}`'.format(search))

        # Get the URL of the source of the song and process the information
        webpage_url = process_info['webpage_url']
        partial_data= partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial_data)

        if processed_info is None:
            raise YTDLError('Couldn\'t fetch `{}`'.format(webpage_url))

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError('Couldn\'t retrieve any matches for `{}`'.format(webpage_url))

        return cls(ctx, FFmpegPCMAudio(info['url'], **cls.FFMPEG_OPTIONS), data=info)

    @staticmethod
    def parse_duration(duration: int):
        """Retrieve the duration given in days, hours, minutes, and seconds

        :param duration: The duration to process
        """
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        duration = []
        if days > 0:
            duration.append('{} days'.format(days))
        if hours > 0:
            duration.append('{} hours'.format(hours))
        if minutes > 0:
            duration.append('{} minutes'.format(minutes))
        if seconds > 0:
            duration.append('{} seconds'.format(seconds))

        return ', '.join(duration)


class Song:
    """A Song holds information about the actual source of the song
    and who requested the song to be played
    """
    __slots__ = ('source', 'requester')

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self, color = 0xEC7600):
        """Creates an embed for the song's information

        :param color: The embed color of the requester (Default: #EC7600)
        """
        embed = Embed(
            title='Now playing',
            description='```css\n{0.source.title}\n```'.format(self),
            color=color
        ).add_field(
            name='Duration', 
            value=self.source.duration
        ).add_field(
            name='Requested by', 
            value=self.requester.mention
        ).add_field(
            name='Uploader', 
            value='[{0.source.uploader}]({0.source.uploader_url})'.format(self)
        ).add_field(
            name='URL', 
            value='[Click]({0.source.url})'.format(self)
        ).set_thumbnail(url=self.source.thumbnail)

        return embed


class SongQueue(asyncio.Queue):
    """A SongQueue keeps track of the songs in the queue and which one will play next
    """
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]


class VoiceState:
    """A VoiceState class keeps track of information including the bot, the context
    of where the songs will be played, and the list of songs to be played
    """
    def __init__(self, bot: Bot, ctx: Context):
        self.bot = bot
        self._ctx = ctx

        self.current = None
        self.voice = None
        self.next = asyncio.Event()
        self.songs = SongQueue()

        self._loop = False
        self._volume = 0.5
        self.skip_votes = set()

        self.audio_player = bot.loop.create_task(self.audio_player_task())

    def __del__(self):
        self.audio_player.cancel()

    @property
    def loop(self):
        return self._loop

    @loop.setter
    def loop(self, value: bool):
        self._loop = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value: float):
        self._volume = value

    @property
    def is_playing(self):
        return self.voice and self.current

    async def audio_player_task(self):
        """Handles all tasks related to playing songs in a queue"""
        
        while True:
            self.next.clear()

            if not self.loop:
                # Try to get the next song within 5 minutes.
                # If no song will be added to the queue in time,
                # the player will disconnect due to performance
                # reasons.
                try:
                    async with timeout(300):  # 5 minutes
                        self.current = await self.songs.get()
                except asyncio.TimeoutError:
                    self.bot.loop.create_task(self.stop())
                    return

            self.current.source.volume = self._volume
            self.voice.play(self.current.source, after=self.play_next_song)
            await self.current.source.channel.send(embed=self.current.create_embed(
                await get_embed_color(self.current.requester)
            ))

            await self.next.wait()

    def play_next_song(self, error=None):
        if error:
            raise VoiceError(str(error))

        self.next.set()

    def skip(self):
        self.skip_votes.clear()

        if self.is_playing:
            self.voice.stop()

    async def stop(self):
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None