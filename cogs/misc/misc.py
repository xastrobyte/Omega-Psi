from datetime import datetime
from discord import Embed
from discord.ext.commands import Cog, group, command, Paginator
from functools import partial
from imdb import IMDb
from os import environ
from random import choice, randint
from requests import get
from urllib.parse import quote

from cogs.errors import get_error_message, UNIMPLEMENTED_ERROR
from cogs.globals import loop

from util.database.database import database
from util.discord import process_scrolling, process_page_reactions
from util.functions import get_embed_color
from util.imgur import Imgur
from util.string import generate_random_string

from .imdb_util import get_movie_embed, get_tv_show_embed

# # # # # # # # # # # # # # # # # # # # # # # # #

IMDB = IMDb()

IMDB_LINK = "https://www.imdb.com/title/tt{}/?ref_=nv_sr_1"

ADVICE_URL = "https://api.adviceslip.com/advice"
AVATAR_LIST = "https://api.adorable.io/avatars/list"
AVATAR_API = "https://api.adorable.io/avatars/face/{}/{}/{}/{}"
CHUCK_NORRIS_URL = "https://api.chucknorris.io/jokes/random"
COIT_URL = "https://coit.pw/{}"
ROBOHASH_API = "https://robohash.org/{}"
STRANGE_PLANET_RANDOM_API = "https://fellowhashbrown.com/api/strangePlanet"
STRANGE_PLANET_RECENT_API = f"{STRANGE_PLANET_RANDOM_API}?recent=true"
STRANGE_PLANET_SEARCH_API = f"{STRANGE_PLANET_RANDOM_API}?keywords={{}}&target={{}}&limit=-1"
XKCD_API_CALL = "https://xkcd.com/{}/info.0.json"
XKCD_RECENT_API_CALL = "https://xkcd.com/info.0.json"

EMOJI_DIGITS = [
    ":zero:",
    "1\u20e3",
    "2\u20e3",
    "3\u20e3",
    "4\u20e3",
    "5\u20e3",
    "6\u20e3",
    "7\u20e3",
    "8\u20e3",
    "9\u20e3",
    '\U0001f51f'
]

SYMBOLS = {
    "?": "❓",
    "!": "❗",
    "+": "➕",
    "*": "✖",
    "-": "➖",
    "/": "➗",
    "$": "💲",
    " ": "  "
}

# # # # # # # # # # # # # # # # # # # # # # # # #

class Misc(Cog, name = "misc"):
    """This category has commands that really don't fit anywhere."""
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @command(
        name = "advice",
        description = "Gives you a random piece of advice.",
        cog_name = "misc"
    )
    async def advice(self, ctx):
        
        # Get the advice
        advice = await loop.run_in_executor(None,
            get, ADVICE_URL
        )
        advice = advice.json()

        await ctx.send(
            embed = Embed(
                title = "Advice Number {}".format(advice["slip"]["slip_id"]),
                description = advice["slip"]["advice"],
                colour = await get_embed_color(ctx.author),
                timestamp = datetime.now()
            ).set_footer(
                text = "Advice Slip API"
            )
        )
    
    @command(
        name = "chuckNorris",
        description = "Gives you a random Chuck Norris joke.",
        cog_name = "misc"
    )
    async def chuck_norris(self, ctx):
        
        # Get the joke; and URL
        chuckNorrisJson = await loop.run_in_executor(None,
            get, CHUCK_NORRIS_URL
        )
        chuckNorrisJson = chuckNorrisJson.json()

        await ctx.send(
            embed = Embed(
                name = "Chuck Norris",
                description = chuckNorrisJson["value"],
                colour = await get_embed_color(ctx.author),
                timestamp = datetime.now()
            ).set_author(
                name = "Chuck Norris Joke",
                icon_url = chuckNorrisJson["icon_url"]
            ).set_footer(
                text = "Chuck Norris API"
            )
        )
    
    @command(
        name = "color",
        description = "Gives you the information about a color given the HEX code.",
        cog_name = "misc"
    )
    async def color(self, ctx, hex_code = None):

        # Check if hex_code is None; Throw error message
        if hex_code == None:
            await ctx.send(
                embed = get_error_message(
                    "You need to specify the hex code for the color."
                ),
                delete_after = 5
            )
        
        # Check if hex_code is not valid hex
        elif len(hex_code) > 8 or len([char for char in hex_code if char not in "0123456789abcdef"]) > 0:
            await ctx.send(
                embed = get_error_message(
                    "The hex code you gave is an invalid hex code."
                )
            )

        # Color is valid
        else:
            embed = Embed(
                title = "#{}".format(hex_code.upper()),
                description = "_ _",
                colour = eval("0x{}".format(hex_code[:6])) # only get first 6 hex digits for embed color
            ).set_image(
                url = COIT_URL.format(hex_code)
            )
        
            await ctx.send(
                embed = embed
            )
    
    @command(
        name = "emojify",
        description = "Gives you text but in Emoji style.",
        cog_name = "misc"
    )
    async def emojify(self, ctx, *, text = None):
        
        # Check if text is None; Throw error message
        if text == None:
            await ctx.send(
                embed = get_error_message(
                    "You need text to emojify."
                )
            )
        
        # Text is not None; Emojify it
        else:
            result = ""
            for char in text.lower():
                if char.isalpha():
                    result += ":regional_indicator_{}: ".format(char)
                elif char.isdigit():
                    result += EMOJI_DIGITS[int(char)]
                elif char in SYMBOLS:
                    result += SYMBOLS[char]
                else:
                    result += char
                
            await ctx.send(
                result
            )
    
    @command(
        name = "setEmbedColor",
        aliases = ["setColor", "setEmbed", "embedColor", "embed"],
        description = "Sets the color of the embed for all embeds that are sent.",
        cog_name = "misc"
    )
    async def set_embed_color(self, ctx, hex_code = None):
        
        # Check if resetting
        if hex_code == None:
            await database.users.set_embed_color(ctx.author, None)

            await ctx.send(
                embed = Embed(
                    title = "Embed Color Reset!",
                    description = "Your embed color was reset to the default.",
                    colour = await get_embed_color(ctx.author)
                )
            )

        # Not resetting, setting color
        else:

            # Check if color is a valid HEX color
            if len(hex_code) == 6 and len([char for char in hex_code.lower() if char not in "0123456789abcdef"]) == 0:
                await database.users.set_embed_color(ctx.author, eval("0x{}".format(hex_code)))

                await ctx.send(
                    embed = Embed(
                        title = "Embed Color Set!",
                        description = "Your embed color was set to #{}".format(hex_code),
                        colour = await get_embed_color(ctx.author)
                    )
                )
            
            # Color is not valid
            else:
                await ctx.send(
                    embed = get_error_message(
                        "That is not a valid HEX color code."
                    )
                )
    
    @command(
        name = "avatar",
        description = "Sends a random cute avatar.",
        cog_name = "image"
    )
    async def avatar(self, ctx):
        
        # Get list of face features
        face_values = await loop.run_in_executor(None,
            get, AVATAR_LIST
        )
        face_values = face_values.json()["face"]

        # Choose random eyes, nose, mouth, and color
        eyes = choice(face_values["eyes"])
        nose = choice(face_values["nose"])
        mouth = choice(face_values["mouth"])
        color = hex(randint(0, 16777215))[2:].rjust(6, "0")

        # Send image in embed
        await ctx.send(
            embed = Embed(
                title = "Avatar!",
                description = " ",
                colour = await get_embed_color(ctx.author)
            ).set_image(
                url = AVATAR_API.format(eyes, nose, mouth, color)
            )
        )
    
    @command(
        name = "robohash",
        aliases = ["robo"],
        description = "Sends a robohash avatar based off the text you enter.",
        cog_name = "image"
    )
    async def robohash(self, ctx, *, text = None):
        
        # Generate personal robohash if content is empty
        if text == None:
            text = str(ctx.author.id)
        
        elif text == "random":
            text = generate_random_string()
        
        # Send image in embed
        await ctx.send(
            embed = Embed(
                title = "Robohash!",
                description = " ",
                colour = await get_embed_color(ctx.author)
            ).set_image(
                url = ROBOHASH_API.format(text.replace(" ", "+"))
            )
        )
    
    @command(
        name = "imgur",
        description = "Allows you to upload an image to an anonymous Imgur album.",
        cog_name = "misc"
    )
    async def imgur(self, ctx, *params):

        # Get the album for the user and the attachments or parameters given
        album = await database.users.get_imgur(ctx.author)
        album_hash = album["hash"]
        album_id = album["id"]
        attachments = [
            attachment if isinstance(attachment, str) else attachment.url
            for attachment in (list(params) + list(ctx.message.attachments))
        ]

        # Check if there are parameters attachments
        if len(attachments) != 0:

            # Check if the user does not have an imgur album attached to their user data
            #   create the album and update their imgur data
            album_created = False
            if not album_hash or not album_id:
                album_created = True
                imgur_data = Imgur.create_imgur_album({
                    "title": ctx.author,
                    "description": "An anonymous imgur album made for the above {}".format(str(ctx.author))
                })
                album_hash = imgur_data["hash"]
                album_id = imgur_data["id"]
                await database.users.set_imgur(ctx.author, imgur_data)
            
            # Add each image/attachment to Imgur, if possible
            #   then add the results to a paginator to display the results of the
            #   command
            results = []
            successful_count = 0
            for attachment in attachments:
                response = await Imgur.add_to_imgur_album(attachment, album_hash)
                results.append("Image uploaded to {}".format(
                        Imgur.IMGUR_IMAGE_URL.format(response["id"])
                    ) if response["success"] else "Failed to upload: {}".format(
                        response["reason"]
                    )
                )
                successful_count += 1 if response["success"] else 0
            paginator = Paginator(prefix = "", suffix = "", max_size = 1000)
            for result in results:
                paginator.add_line(paginator)
            
            # Add each page of the paginator to an embed
            title = ""
            if album_created:
                title += "Imgur Album Created"
            if successful_count == 0:
                title += " but Images Failed to Upload"
            else:
                title += " and Image{} Uploaded".format("s" if successful_count > 1 else "")
            embed = Embed(
                title = title,
                description = "_ _" if not album_created else "An anonymous Imgur album was created for you here: {}".format(
                    Imgur.IMGUR_ALBUM_URL.format(album_id)
                ),
                colour = await get_embed_color(ctx.author)
            )
            for i in range(len(paginator.pages)):
                embed.add_field(
                    name = "Results {}".format(
                        "({} / {})".format(
                            i + 1, len(paginator.pages)
                        ) if len(paginator.pages) else ""
                    ),
                    value = paginator.pages[i]
                )
            
            await ctx.send(embed = embed)
        
        # User is only accessing their Imgur album
        else:

            # Get the list of images
            album_images = await Imgur.get_imgur_album(album_id)

            # Create the scrolling embed
            await process_scrolling(ctx, self.bot, title = "Images",
                pages = [
                    Embed(
                        title = "Your Imgur Album",
                        description = "_ _" if len(album_images) > 0 else "You don't have any images",
                        colour = await get_embed_color(ctx.author)
                    ).set_image(
                        url = image["link"]
                    )
                    for image in album_images
                ],
                send_page = True
            )

    @command(
        name = "movie",
        description = "Gives you information about a movie on IMDb.",
        cog_name = "misc"
    )
    async def movie(self, ctx, *, movie = None):

        # There was no movie specified
        if not movie:
            await ctx.send(embed = get_error_message("You must specify a movie to look up."))
        
        # A movie was specified
        else:
            results = await loop.run_in_executor(None,
                IMDB.search_movie, movie
            )
            movies = []
            for movie in results:
                movies.append(movie)
            
            # There were no movies found
            if len(movies) == 0:
                await ctx.send(embed = get_error_message("There were no movies found with that title."))
            
            # There was at least one movie found,
            #   let the user scroll through the results
            #   limit the amount of movies to 10
            else:
                await ctx.send(embed = await get_movie_embed(ctx, IMDB, movies[0], IMDB_LINK))
    
    @command(
        name = "tvShow",
        aliases = ["tv", "show"],
        description = "Gives you information about a TV show on IMDb.",
        cog_name = "misc"
    )
    async def tv_show(self, ctx, *, tv_show = None):

        # There was no tv show specified
        if not tv_show:
            await ctx.send(embed = get_error_message("You must specify a tv show to look up."))
        
        # A tv show was specified
        else:
            results = await loop.run_in_executor(None,
                IMDB.search_movie, tv_show
            )
            tv_shows = []
            for tv_show in results:
                tv_shows.append(tv_show)
            
            # There were no tv shows found
            if len(tv_shows) == 0:
                await ctx.send(embed = get_error_message("There were no tv shows found with that title."))
            
            # There was at least one tv show found
            else:
                await ctx.send(embed = await get_tv_show_embed(ctx, IMDB, tv_shows[0], IMDB_LINK))
    
    @group(
        name = "xkcd",
        description = "Sends a random XKCD comic.",
        cog_name = "misc"
    )
    async def xkcd(self, ctx):
        if not ctx.invoked_subcommand:

            # Get the most recent comic in order to get a random comic
            recent = await loop.run_in_executor(None,
                get, XKCD_RECENT_API_CALL
            )
            recent = recent.json()
            comic = str(randint(1, recent["num"]))

            # Get the comic and send it in an embed, allowing the user to scroll through
            comic = await loop.run_in_executor(None,
                get, XKCD_API_CALL.format(comic)
            )
            comic = comic.json()

            # Process the scrolling
            await process_scrolling(ctx, self.bot, refresh_function = self.xkcd_comic_refresh, min_page = 1, max_page = recent["num"], current_page = comic["num"])

    @xkcd.command(
        name = "recent",
        aliases = ["r"],
        description = "Sends the most recent XKCD comic.",
        cog_name = "misc"
    )
    async def xkcd_recent(self, ctx):

        # Get the most recent comic in order to get a random comic
        recent = await loop.run_in_executor(None,
            get, XKCD_RECENT_API_CALL
        )
        recent = recent.json()

        # Process the scrolling
        await process_scrolling(ctx, self.bot, refresh_function = self.xkcd_comic_refresh, min_page = 1, max_page = recent["num"], current_page = recent["num"])
    
    @xkcd.command(
        name = "search",
        aliases = ["find"],
        description = "Sends an XKCD comic with the specified comic number.",
        cog_name = "misc"
    )
    async def xkcd_find(self, ctx, comic_number= None):

        # Check if the comic_number was not specified
        if not comic_number:
            await ctx.send(embed = get_error_message("You must specify the XKCD comic number to look for."))
        
        # The comic number was specified
        else:

            # Validate that comic_number is a number
            try:
                comic_number = int(comic_number)
        
                # Get the most recent comic in order validate the comic number
                recent = await loop.run_in_executor(None,
                    get, XKCD_RECENT_API_CALL
                )
                recent = recent.json()

                # Check if the comic number is invalid
                if comic_number < 1 or comic_number > recent["num"]:
                    await ctx.send(embed = get_error_message("That XKCD comic does not exist!"))
                
                # The comic number is valid
                else:

                    # Get the comic and send it in an embed, allowing the user to scroll through
                    comic = await loop.run_in_executor(None,
                        get, XKCD_API_CALL.format(comic_number)
                    )
                    comic = comic.json()

                    # Process the scrolling
                    await process_scrolling(ctx, self.bot, refresh_function = self.xkcd_comic_refresh, min_page = 1, max_page = recent["num"], current_page = comic["num"])
            
            # comic_number is not a number
            except:
                await ctx.send(embed = get_error_message("The comic number you gave isn't a number at all."))
    
    @group(
        name = "strangePlanet",
        description = "Sends a random comic from Nathan W. Pyle's Strange Planet series.",
        cog_name = "misc"
    )
    async def strange_planet(self, ctx):
        if not ctx.invoked_subcommand:

            # Call the API and get an image
            #   then send the image in an embed
            response = await loop.run_in_executor(None,
                get, STRANGE_PLANET_RANDOM_API
            )
            response = response.json()
            await ctx.send(
                embed = Embed(
                    title = "Random Strange Planet Comic",
                    description = "_ _",
                    colour = await get_embed_color(ctx.author)
                ).set_image(
                    url = response["data"]
                )
            )
    
    @strange_planet.command(
        name = "recent",
        aliases = ["r"],
        description = "Sends the most recent comic from the Strange Planet series.",
        cog_name = "misc"
    )
    async def strange_planet_recent(self, ctx):

        # Call the API and get an image
        #   then send the image in an embed
        response = await loop.run_in_executor(None,
            get, STRANGE_PLANET_RECENT_API
        )
        response = response.json()
        await ctx.send(
            embed = Embed(
                title = "Recent Strange Planet Comic",
                description = "_ _",
                colour = await get_embed_color(ctx.author)
            ).set_image(
                url = response["data"]
            )
        )
    
    @strange_planet.group(
        name = "search",
        aliases = ["find"],
        description = "Lets you search for a comic or reaction from the Strange Planet series.",
        cog_name = "misc",
        invoke_without_command = True
    )
    async def strange_planet_search(self, ctx, *, keywords = None, target = "all"):
        if not ctx.invoked_subcommand:

            # Check if there are no keywords
            if not keywords:
                await ctx.send(
                    embed = get_error_message(
                        "You need to specify keywords to search for comics or reactions."
                    )
                )
            
            # There are keywords
            else:
                
                # Call the API and get an image
                response = await loop.run_in_executor(None,
                    get, STRANGE_PLANET_SEARCH_API.format(quote(keywords), target)
                )
                response = response.json()

                # No images were found, tell the user
                if len(response["data"]) == 0:
                    await ctx.send(
                        embed = get_error_message(
                            "There were no comics found :(\nMaybe try a more broad search?"
                        )
                    )
                
                # Images were found, show the user all search results
                else:
                    pages = response["data"]
                    await process_scrolling(
                        ctx, self.bot, 
                        pages = [
                            Embed(
                                title = "Search results for \"{}\" {}".format(
                                    keywords,
                                    "({} / {})".format(
                                        i + 1, len(pages)
                                    ) if len(pages) > 1 else ""
                                ),
                                description = "_ _",
                                colour = await get_embed_color(ctx.author)
                            ).set_image(
                                url = pages[i]
                            )
                            for i in range(len(pages))
                        ]
                    )
    
    @strange_planet_search.command(
        name = "comics",
        description = "Lets you search for a comic from the Strange Planet series.",
        cog_name = "misc"
    )
    async def strange_planet_search_comics(self, ctx, *, keywords = None):
        await self.strange_planet_search(ctx, keywords = keywords, target = "comics")
    
    @strange_planet_search.command(
        name = "reactions",
        description = "Lets you search for a reaction from the Strange Planet series.",
        cog_name = "misc"
    )
    async def strange_planet_search_reactions(self, ctx, *, keywords = None):
        await self.strange_planet_search(ctx, keywords = keywords, target = "reactions")
    
    # # # # # # # # # # # # # # # # # # # # # # # # # 

    async def xkcd_comic_refresh(self, ctx, comic_number):
        """Grabs the comic at the specified number and returns the title, description, and url for
        an embed
        """

        # Get the comic
        comic = await loop.run_in_executor(None,
            get, XKCD_API_CALL.format(comic_number)
        )
        comic = comic.json()

        # Return the comic data
        return Embed(
            title = "{} (#{})".format(comic["safe_title"], comic["num"]),
            description = "_ _",
            colour = await get_embed_color(ctx.author),
            timestamp = datetime(int(comic["year"]), int(comic["month"]), int(comic["day"]))
        ).set_image(
            url = comic["img"]
        )

def setup(bot):
    bot.add_cog(Misc(bot))