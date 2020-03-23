from datetime import datetime
from discord import Embed
from discord.ext.commands import Cog, group
from hashlib import md5
from os import environ
from random import randint
from requests import get
from urllib.parse import quote

from cogs.errors import get_error_message
from cogs.globals import loop

from cogs.comics.comics_util import get_marvel_character_embed, get_marvel_series_embed, get_marvel_comic_embed

from util.database.database import database
from util.discord import process_scrolling
from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

MARVEL_CHARACTER_API = "http://gateway.marvel.com/v1/public/characters?name={}&limit=10&apikey={}&ts={}&hash={}"
MARVEL_SERIES_API = "http://gateway.marvel.com/v1/public/series?title={}&limit=10&apikey={}&ts={}&hash={}"
MARVEL_COMIC_API = "http://gateway.marvel.com/v1/public/comics?title={}&limit=10&apikey={}&ts={}&hash={}"
STRANGE_PLANET_RANDOM_API = "https://fellowhashbrown.com/api/strangePlanet"
STRANGE_PLANET_RECENT_API = f"{STRANGE_PLANET_RANDOM_API}?recent=true"
STRANGE_PLANET_SEARCH_API = f"{STRANGE_PLANET_RANDOM_API}?keywords={{}}&target={{}}&limit=-1"
XKCD_API_CALL = "https://xkcd.com/{}/info.0.json"
XKCD_RECENT_API_CALL = "https://xkcd.com/info.0.json"

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class Comics(Cog, name = "comics"):
    """Comic stuff goes here!"""
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @group(
        name = "marvel",
        description = "Search up a character, a series, or a specific comic in Marvel comics",
        cog_name = "comics"
    )
    async def marvel(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send(
                embed = get_error_message(
                    "You must run a subcommand of this command. Try doing `{}help marvel`".format(
                        await database.guilds.get_prefix(ctx.guild) if ctx.guild else ""
                    )
                )
            )
    
    @marvel.command(
        name = "character",
        description = "Search for a specific character in Marvel comics",
        cog_name = "comics"
    )
    async def marvel_character(self, ctx, *, character = None):

        # Check if no character is given
        if character is None:
            embed = get_error_message("You must provide a name for the Marvel character")
        
        # A character is given
        else:
            
            # Call the Marvel API
            timestamp = int(datetime.now().timestamp())
            response = await loop.run_in_executor(None,
                get,
                MARVEL_CHARACTER_API.format(
                    character,
                    environ["MARVEL_PUBLIC_API_KEY"],
                    timestamp,
                    md5("{}{}{}".format(
                        timestamp, environ["MARVEL_PRIVATE_API_KEY"],
                        environ["MARVEL_PUBLIC_API_KEY"]
                    ).encode("utf-8")).hexdigest()
                )
            )
            response = response.json()

            # Check if there were no results
            if response["data"]["count"] == 0:
                embed = get_error_message("No Marvel characters could be found with the name \"{}\"".format(character))
            
            # There were results
            else:
                
                # Create embeds for each result using the get_marvel_character_embed method
                embeds = [
                    get_marvel_character_embed(response["attributionText"], result)
                    for result in response["data"]["results"]
                ]

                # Use the scrolling method to allow the user to scroll through
                #   the results and view comics or series
                await process_scrolling(ctx, self.bot, title = "Results", pages = embeds)
                embed = None
        
        # Send an embed if it exists
        if embed is not None:
            await ctx.send(embed = embed)
    
    @marvel.command(
        name = "series",
        description = "Search for a specific series in Marvel comics",
        cog_name = "comics"
    )
    async def marvel_series(self, ctx, *, series = None):

        # Check if no series is given
        if series is None:
            embed = get_error_message("You must provide a name for the Marvel series")
        
        # A series is given
        else:
            
            # Call the Marvel API
            timestamp = int(datetime.now().timestamp())
            response = await loop.run_in_executor(None,
                get,
                MARVEL_SERIES_API.format(
                    series,
                    environ["MARVEL_PUBLIC_API_KEY"],
                    timestamp,
                    md5("{}{}{}".format(
                        timestamp, environ["MARVEL_PRIVATE_API_KEY"],
                        environ["MARVEL_PUBLIC_API_KEY"]
                    ).encode("utf-8")).hexdigest()
                )
            )
            response = response.json()

            # Check if there were no results
            if response["data"]["count"] == 0:
                embed = get_error_message("No Marvel series' could be found with the name \"{}\"".format(series))
            
            # There were results
            else:
                
                # Create embeds for each result using the get_marvel_series_embed method
                embeds = [
                    get_marvel_series_embed(response["attributionText"], result)
                    for result in response["data"]["results"]
                ]

                # Use the scrolling method to allow the user to scroll through
                #   the results and view comics or series
                await process_scrolling(ctx, self.bot, title = "Results", pages = embeds)
                embed = None
        
        # Send an embed if it exists
        if embed is not None:
            await ctx.send(embed = embed)
    
    @marvel.command(
        name = "comic",
        description = "Search for a specific comic in Marvel comics",
        cog_name = "comics"
    )
    async def marvel_comic(self, ctx, *, comic = None):

        # Check if no comic is given
        if comic is None:
            embed = get_error_message("You must provide a name for the Marvel comic")
        
        # A comic is given
        else:
            
            # Call the Marvel API
            timestamp = int(datetime.now().timestamp())
            response = await loop.run_in_executor(None,
                get,
                MARVEL_COMIC_API.format(
                    comic,
                    environ["MARVEL_PUBLIC_API_KEY"],
                    timestamp,
                    md5("{}{}{}".format(
                        timestamp, environ["MARVEL_PRIVATE_API_KEY"],
                        environ["MARVEL_PUBLIC_API_KEY"]
                    ).encode("utf-8")).hexdigest()
                )
            )
            response = response.json()

            # Check if there were no results
            if response["data"]["count"] == 0:
                embed = get_error_message("No Marvel comics could be found with the name \"{}\"".format(comic))
            
            # There were results
            else:
                
                # Create embeds for each result using the get_marvel_comic_embed method
                embeds = [
                    get_marvel_comic_embed(response["attributionText"], result)
                    for result in response["data"]["results"]
                ]

                # Use the scrolling method to allow the user to scroll through
                #   the results and view comics or series
                await process_scrolling(ctx, self.bot, title = "Results", pages = embeds)
                embed = None
        
        # Send an embed if it exists
        if embed is not None:
            await ctx.send(embed = embed)
    
    @group(
        name = "xkcd",
        description = "Sends a random XKCD comic.",
        cog_name = "comics"
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
        cog_name = "comics"
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
        cog_name = "comics"
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
        cog_name = "comics"
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
        cog_name = "comics"
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
        cog_name = "comics"
    )
    async def strange_planet_search(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send(
                embed = get_error_message(
                    "You must specify whether you want to look for comics or reactions. Try `{}help strangeplanet search`".format(
                        await database.guilds.get_prefix(ctx.guild) if ctx.guild else ""
                    )
                )
            )
    
    @strange_planet_search.command(
        name = "comics",
        description = "Lets you search for a comic from the Strange Planet series.",
        cog_name = "comics"
    )
    async def strange_planet_search_comics(self, ctx, *, keywords = None):

        # Check if there are no keywords
        if not keywords:
            await ctx.send(
                embed = get_error_message(
                    "You need to specify keywords to search for comics."
                )
            )
        
        # There are keywords
        else:
            
            # Call the API and get an image
            response = await loop.run_in_executor(None,
                get, STRANGE_PLANET_SEARCH_API.format(quote(keywords), "comics")
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
        name = "reactions",
        description = "Lets you search for a reaction from the Strange Planet series.",
        cog_name = "comics"
    )
    async def strange_planet_search_reactions(self, ctx, *, keywords = None):
        
        # Check if there are no keywords
        if not keywords:
            await ctx.send(
                embed = get_error_message(
                    "You need to specify keywords to search for reactions."
                )
            )
        
        # There are keywords
        else:
            
            # Call the API and get an image
            response = await loop.run_in_executor(None,
                get, STRANGE_PLANET_SEARCH_API.format(quote(keywords), "reactions")
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
    bot.add_cog(Comics(bot))