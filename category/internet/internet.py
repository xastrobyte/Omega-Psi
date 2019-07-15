import asyncio, discord, os, requests
from datetime import datetime
from discord.ext import commands
from imdb import IMDb
from random import randint

import database
from category import errors
from category.globals import add_scroll_reactions, FIRST_PAGE, LAST_PAGE, PREVIOUS_PAGE, NEXT_PAGE, LEAVE, SCROLL_REACTIONS
from category.globals import get_embed_color
from category.internet.weather import weather, forecast
from util.string import minutes_to_runtime

from .ticketmaster import get_event_embed, get_attraction_embed

# # # # # # # # # # # # # # # # # # # # # # # # #

IMDB = IMDb()

IMDB_LINK = "https://www.imdb.com/title/tt{}/?ref_=nv_sr_1"

SUPERHERO_API_CALL = "https://superheroapi.com/api.php/{}/search/{}"
TINYURL_API_CALL = "http://tinyurl.com/api-create.php?url={}"
WEATHER_API_CALL = "https://api.apixu.com/v1/current.json?key={}&q={}"
FORECAST_API_CALL = "https://api.apixu.com/v1/forecast.json?key={}&q={}&days=7"
XKCD_API_CALL = "https://xkcd.com/{}/info.0.json"
XKCD_RECENT_API_CALL = "https://xkcd.com/info.0.json"

TICKETMASTER_EVENT_API_CALL = "https://app.ticketmaster.com/discovery/v2/events.json?keyword={}&apikey={}"
TICKETMASTER_ATTRACTION_API_CALL = "https://app.ticketmaster.com/discovery/v2/attractions.json?keyword={}&apikey={}"

DC_ICON = "https://www.dccomics.com/sites/default/files/imce/DC_Logo_Blue_Final_573b356bd056a9.41641801.jpg"
MARVEL_ICON = "http://thetechnews.com/wp-content/uploads/2018/03/2_The-latest-Marvel-logo.jpg"

# # # # # # # # # # # # # # # # # # # # # # # # #

class Internet(commands.Cog, name = "internet"):
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @commands.command(
        name = "movie",
        description = "Gives you information about a Movie on IMDb.",
        cog_name = "internet"
    )
    async def movie(self, ctx, *, movie = None):

        # Check if the movie is None; Throw error message
        if movie == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need a movie to look up."
                )
            )
        
        # Movie is not None; Look for it
        else:

            results = await database.loop.run_in_executor(None,
                IMDB.search_movie,
                movie
            )
            movies = []
            for movie in results:
                if movie.data["kind"] in ["movie"]:
                    movies.append(movie)
            
            # There were no movies found
            if len(movies) == 0:
                await ctx.send(
                    embed = errors.get_error_message(
                        "There were no movies found with that title."
                    )
                )
            
            # There was a movie found
            else:
                movie = await database.loop.run_in_executor(None,
                    IMDB.get_movie,
                    movies[0].movieID
                )

                try: title = movie.get("title")
                except: title = "No Title Found"

                try: plotOutline = movie.get("plot outline")
                except: plotOutline = "No Plot Outline Yet"
            
                # Get following data only:
                #   - title
                #   - plot outline
                #   - directors
                #   - producers
                #   - year released
                #   - running time
                #   - cast (first 20)
                #   - poster (if possible)
                try: title = movie.get("title")
                except: title = "No Title"

                try: plotOutline = movie.get("plot outline")
                except: plotOutline = "No Plot Outline Yet."

                try: directors = [director.get("name") for director in movie.get("director")]
                except: directors = ["N/A"]

                try: producers = [dist.get("name") for dist in movie.get("production companies")]
                except: producers = ["N/A"]

                try: year = movie.get("year")
                except: year = "No Year"

                try: length = minutes_to_runtime(int(movie.get("runtimes")[0]))
                except: length = "N/A"

                try: cast = [person.get("name") for person in movie.get("cast")[:20]]
                except: cast = ["N/A"]

                try: poster = movie.get("cover url")
                except: poster = None

                fields = {
                    "Director(s)": ", ".join(directors),
                    "Producers": ", ".join(producers),
                    "Year Released": year,
                    "Running Time": length,
                    "Cast (first 20)": ", ".join(cast)
                }
        
                # Add data to embed
                embed = discord.Embed(
                    title = title,
                    description = plotOutline,
                    colour = await get_embed_color(ctx.author),
                    timestamp = datetime.now(),
                    url = IMDB_LINK.format(movie.movieID)
                ).set_footer(
                    text = "IMDb"
                )

                for field in fields:
                    embed.add_field(
                        name = field,
                        value = fields[field],
                        inline = False
                    )
                
                if poster != None:
                    embed.set_image(
                        url = poster
                    )
                
                await ctx.send(
                    embed = embed
                )
    
    @commands.command(
        name = "tvShow",
        aliases = ["tv", "show"],
        description = "Gives you information about a TV Show on IMDb.",
        cog_name = "internet"
    )
    async def tv_show(self, ctx, show = None):

        # Check if the show is None; Throw error message
        if show == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need a TV Show to look up."
                )
            )
        
        # Show is not None; Look for it
        else:

            # Get TV Show data
            results = await database.loop.run_in_executor(None,
                IMDB.search_movie,
                show
            )
            shows = []
            for show in results:
                if show.data["kind"] in ["tv show", "tv series"]:
                    shows.append(show)

            # There were no shows found
            if len(shows) == 0:
                await ctx.send(
                    embed = errors.get_error_message(
                        "There were no shows found with that title."
                    )
                )

            # There were shows found
            else:

                show = await database.loop.run_in_executor(None,
                    IMDB.get_movie,
                    shows[0].movieID
                )

                # Get following data only:
                #   - title
                #   - plot outline
                #   - writer
                #   - distributors
                #   - year released
                #   - number of seasons
                #   - cast (first 20)
                #   - poster (if possible)
                try: title = show.get("title")
                except: title = "No Title"

                try: plotOutline = show.get("plot outline")
                except: plotOutline = "No Plot Outline Yet."

                try: writer = [person.get("name") for person in show.get("writer")]
                except: writer = ["N/A"]

                try: producers = [dist.get("name") for dist in show.get("production companies")]
                except: producers = ["N/A"]

                try: year = show.get("year")
                except: year = "No Year"

                try: seasons = show.get("seasons")
                except: seasons = "No Seasons"

                try: cast = [person.get("name") for person in show.get("cast")[:20]]
                except: cast = ["N/A"]

                try: poster = show.get("cover url")
                except: poster = None

                fields = {
                    "Writer(s)": ", ".join(writer),
                    "Producers": ", ".join(producers),
                    "Year Released": year,
                    "Seasons": seasons,
                    "Cast (first 20)": ", ".join(cast)
                }

                # Add all data to the embed
                embed = discord.Embed(
                    title = title,
                    description = plotOutline,
                    colour = await get_embed_color(ctx.author),
                    timestamp = datetime.now(),
                    url = IMDB_LINK.format(show.movieID)
                ).set_footer(
                    text = "IMDb"
                )

                for field in fields:
                    embed.add_field(
                        name = field,
                        value = fields[field],
                        inline = True
                    )

                if poster != None:
                    embed.set_image(
                        url = poster
                    )
                
                await ctx.send(
                    embed = embed
                )
    
    @commands.command(
        name = "searchConcert",
        aliases = ["concert"],
        description = "Let's you search up events pertaining to keywords to search by.",
        cog_name = "internet"
    )
    async def search_concert(self, ctx, *, keywords = None):

        # Check if keywords is None; Send error message
        if keywords == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need keywords to search up a concert/event by."
                )
            )
        
        # Keywords is not None
        else:

            # Request ticketmaster api
            response = await database.loop.run_in_executor(None,
                requests.get,
                TICKETMASTER_EVENT_API_CALL.format(
                    keywords.replace(" ", "+"),
                    os.environ["TICKETMASTER_API_KEY"]
                )
            )
            response = response.json()

            # Make sure there exists at least 1 element
            if response["page"]["totalElements"] > 0:

                # Keep track of current events to show information about
                # Multiple events will be put into a scrolling embed
                current = 0
                events = response["_embedded"]["events"]

                embed = await get_event_embed(ctx, events[current])

                # Send message
                msg = await ctx.send(
                    embed = embed
                )

                await add_scroll_reactions(msg, events)

                while True:

                    # Wait for next reaction from user
                    def check(reaction, user):
                        return str(reaction) in SCROLL_REACTIONS and reaction.message.id == msg.id and user == ctx.author

                    done, pending = await asyncio.wait([
                        self.bot.wait_for("reaction_add", check = check),
                        self.bot.wait_for("reaction_remove", check = check)
                    ], return_when = asyncio.FIRST_COMPLETED)

                    reaction, user = done.pop().result()

                    # Cancel any futures
                    for future in pending:
                        future.cancel()
                    
                    # Reaction is FIRST_PAGE
                    if str(reaction) == FIRST_PAGE:
                        current = 0
                    
                    # Reaction is LAST_PAGE
                    elif str(reaction) == LAST_PAGE:
                        current = len(events) - 1
                    
                    # Reaction is PREVIOUS_PAGE
                    elif str(reaction) == PREVIOUS_PAGE:
                        current -= 1
                        if current < 0:
                            current = 0
                    
                    # Reaction is NEXT_PAGE
                    elif str(reaction) == NEXT_PAGE:
                        current += 1
                        if current > len(events) - 1:
                            current = len(events) - 1
                    
                    # Reaction is LEAVE
                    elif str(reaction) == LEAVE:
                        await msg.delete()
                        break
                    
                    # Update event
                    await msg.edit(
                        embed = await get_event_embed(ctx, events[current])
                    )
            
            # There was nothing
            else:
                await ctx.send(
                    embed = errors.get_error_message(
                        "Nothing was found for `{}`".format(keywords)
                    )
                )
    
    @commands.command(
        name = "searchAttraction",
        aliases = ["attraction", "searchPerformer", "performer"],
        description = "Let's you search up attractions/performers pertaining to keywords to search by.",
        cog_name = "internet"
    )
    async def search_attraction(self, ctx, *, keywords = None):

        # Check if keywords is None; Send error message
        if keywords == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need keywords to search up an attraction/performer by."
                )
            )
        
        # Keywords is not None
        else:

            # Request ticketmaster api
            response = await database.loop.run_in_executor(None,
                requests.get,
                TICKETMASTER_ATTRACTION_API_CALL.format(
                    keywords.replace(" ", "+"),
                    os.environ["TICKETMASTER_API_KEY"]
                )
            )
            response = response.json()

            # Make sure there exists at least 1 element
            if response["page"]["totalElements"] > 0:

                # Get the first attraction
                attraction = response["_embedded"]["attractions"][0]

                # Send message
                await ctx.send(
                    embed = await get_attraction_embed(ctx, attraction)
                )
            
            # There was nothing
            else:
                await ctx.send(
                    embed = errors.get_error_message(
                        "Nothing was found for `{}`".format(keywords)
                    )
                )
    
    @commands.command(
        name = "xkcd",
        description = "Sends an XKCD comic with the specified number or sends a random one.",
        cog_name = "internet"
    )
    async def xkcd(self, ctx, comic = None):

        # Get most recent comic
        recent = await database.loop.run_in_executor(None,
            requests.get,
            XKCD_RECENT_API_CALL
        )
        recent = recent.json()
        
        # Check if comic is None; Get random
        if comic == None:
            comic = str(randint(1, recent["num"]))
        
        # Check if comic is not None; Get comic
        if comic != None:

            # Check if comic is recent; Send recent
            if comic in ["recent", "r"]:
                comic = recent["num"]
        
            # comic is not recent; Send random or requested
            try:
                comic = int(comic)
                value = comic

                # Check if comic is in range
                success = True
                if comic < 1 or comic > recent["num"]:
                    success = False
                    await ctx.send(
                        embed = errors.get_error_message(
                            "That comic is not a valid comic number."
                        )
                    )
                
                else:

                    comic = await database.loop.run_in_executor(None,
                        requests.get,
                        XKCD_API_CALL.format(comic)
                    )
                    comic = comic.json()

                if success:

                    # Delete invocation command
                    await ctx.message.delete()

                    embed = discord.Embed(
                        title = comic["safe_title"],
                        description = " ",
                        colour = await get_embed_color(ctx.author),
                        timestamp = datetime(int(comic["year"]), int(comic["month"]), int(comic["day"]))
                    ).set_image(
                        url = comic["img"]
                    )

                    msg = await ctx.send(
                        embed = embed
                    )

                    for reaction in SCROLL_REACTIONS:
                        await msg.add_reaction(reaction)

                    # Keep comic scroll up until user closes it
                    while True:

                        # Wait for next reaction from user
                        def check(reaction, user):
                            return str(reaction) in SCROLL_REACTIONS and reaction.message.id == msg.id and user == ctx.author

                        done, pending = await asyncio.wait([
                            self.bot.wait_for("reaction_add", check = check),
                            self.bot.wait_for("reaction_remove", check = check)
                        ], return_when = asyncio.FIRST_COMPLETED)

                        reaction, user = done.pop().result()

                        # Cancel any futures
                        for future in pending:
                            future.cancel()
                        
                        # Reaction is FIRST_PAGE
                        if str(reaction) == FIRST_PAGE:
                            value = 1
                        
                        # Reaction is LAST_PAGE
                        elif str(reaction) == LAST_PAGE:
                            value = recent["num"]
                        
                        # Reaction is PREVIOUS_PAGE
                        elif str(reaction) == PREVIOUS_PAGE:
                            value -= 1
                            if value < 1:
                                value = 1
                        
                        # Reaction is NEXT_PAGE
                        elif str(reaction) == NEXT_PAGE:
                            value += 1
                            if value > recent["num"]:
                                value = recent["num"]
                        
                        # Reaction is LEAVE
                        elif str(reaction) == LEAVE:
                            await msg.delete()
                            break
                        
                        # Update comic
                        comic = await database.loop.run_in_executor(None,
                            requests.get,
                            XKCD_API_CALL.format(value)
                        )
                        comic = comic.json()

                        embed = discord.Embed(
                            title = comic["safe_title"],
                            description = " ",
                            colour = await get_embed_color(ctx.author),
                            timestamp = datetime(int(comic["year"]), int(comic["month"]), int(comic["day"]))
                        ).set_image(
                            url = comic["img"]
                        )

                        await msg.edit(
                            embed = embed
                        )
            
            # requested comic is not a number
            except:
                await ctx.send(
                    embed = errors.get_error_message(
                        "The value you entered is not a number."
                    )
                )
    
    @commands.command(
        name = "dc",
        description = "Allows you to search up and get info about a DC character.",
        cog_name = "internet"
    )
    async def dc(self, ctx, *, character = None):
        
        # Check if character is none; Throw error message
        if character == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need a character to look up."
                )
            )

        # Character is not none; Look it up
        else:
            superhero = await database.loop.run_in_executor(None,
                requests.get,
                SUPERHERO_API_CALL.format(
                    os.environ["SUPERHERO_API_KEY"],
                    character
                )
            )
            superhero = superhero.json()

            # See if the character was found
            if superhero["response"] == "success":

                # Look for first DC character
                found = False
                for hero in superhero["results"]:
                    if hero["biography"]["publisher"] == "DC Comics":
                        superhero = hero
                        found = True
                        break

                if not found:
                    superhero = superhero["results"][0]

                # See if the character is from DC
                if superhero["biography"]["publisher"] == "DC Comics":

                    # Setup the fields and create the embed
                    fields = {
                        "First Appearance": superhero["biography"]["first-appearance"],
                        "Place of Birth": superhero["biography"]["place-of-birth"],
                        "Stats": (
                            "**Intelligence: {}**\n" +
                            "**Strength: {}**\n" +
                            "**Speed: {}**\n" +
                            "**Durability: {}**\n" +
                            "**Power: {}**\n" +
                            "**Combat: {}**\n"
                        ).format(
                            superhero["powerstats"]["intelligence"], superhero["powerstats"]["strength"],
                            superhero["powerstats"]["speed"], superhero["powerstats"]["durability"],
                            superhero["powerstats"]["power"], superhero["powerstats"]["combat"]
                        ),
                        "Aliases": ", ".join(superhero["biography"]["aliases"]),
                        "Appearance": (
                            "**Race: {}**\n" +
                            "**Height: {} ({})**\n" +
                            "**Weight: {} ({})**\n" +
                            "**Eye Color: {}**\n" +
                            "**Hair Color: {}**\n"
                        ).format(
                            superhero["appearance"]["race"],
                            superhero["appearance"]["height"][0], superhero["appearance"]["height"][1],
                            superhero["appearance"]["weight"][0], superhero["appearance"]["weight"][1],
                            superhero["appearance"]["eye-color"], superhero["appearance"]["hair-color"]
                        ),
                        "Affiliations": superhero["connections"]["group-affiliation"],
                        "Relatives": superhero["connections"]["relatives"]
                    }

                    embed = discord.Embed(
                        title = "{} - {} {}".format(
                            superhero["name"], 
                            superhero["biography"]["full-name"],
                            "({})".format(
                                superhero["biography"]["alter-egos"]
                            ) if superhero["biography"]["alter-egos"] != "No alter egos found." else ""
                        ),
                        description = " ",
                        colour = await get_embed_color(ctx.author)
                    ).set_image(
                        url = superhero["image"]["url"]
                    )

                    for field in fields:
                        embed.add_field(
                            name = field,
                            value = fields[field],
                            inline = True
                        )
                    
                    await ctx.send(
                        embed = embed
                    )
                    
                # Character is not from DC
                else:
                    await ctx.send(
                        embed = errors.get_error_message(
                            "That character is not from DC Comics."
                        )
                    )
            
            # Character is not found
            else:
                await ctx.send(
                    embed = errors.get_error_message(
                        "That character was not found."
                    )
                )
    
    @commands.command(
        name = "marvel",
        description = "Allows you to search up and get info about a Marvel character.",
        cog_name = "internet"
    )
    async def marvel(self, ctx, *, character = None):

        # Check if character is none; Throw error message
        if character == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need a character to look up."
                )
            )

        # There were the proper amount of parameters
        else:

            # Get the superhero data
            superhero = await database.loop.run_in_executor(None,
                requests.get,
                SUPERHERO_API_CALL.format(
                    os.environ["SUPERHERO_API_KEY"],
                    character
                )
            )
            superhero = superhero.json()

            # See if the character was found
            if superhero["response"] == "success":

                # Look for first DC character
                found = False
                for hero in superhero["results"]:
                    if hero["biography"]["publisher"] == "Marvel Comics":
                        superhero = hero
                        found = True
                        break

                if not found:
                    superhero = superhero["results"][0]

                # See if the character is from Marvel
                if superhero["biography"]["publisher"] == "Marvel Comics":

                    # Setup the fields and create the embed
                    fields = {
                        "First Appearance": superhero["biography"]["first-appearance"],
                        "Place of Birth": superhero["biography"]["place-of-birth"],
                        "Stats": (
                            "**Intelligence: {}**\n" +
                            "**Strength: {}**\n" +
                            "**Speed: {}**\n" +
                            "**Durability: {}**\n" +
                            "**Power: {}**\n" +
                            "**Combat: {}**\n"
                        ).format(
                            superhero["powerstats"]["intelligence"], superhero["powerstats"]["strength"],
                            superhero["powerstats"]["speed"], superhero["powerstats"]["durability"],
                            superhero["powerstats"]["power"], superhero["powerstats"]["combat"]
                        ),
                        "Aliases": ", ".join(superhero["biography"]["aliases"]),
                        "Appearance": (
                            "**Race: {}**\n" +
                            "**Height: {} ({})**\n" +
                            "**Weight: {} ({})**\n" +
                            "**Eye Color: {}**\n" +
                            "**Hair Color: {}**\n"
                        ).format(
                            superhero["appearance"]["race"],
                            superhero["appearance"]["height"][0], superhero["appearance"]["height"][1],
                            superhero["appearance"]["weight"][0], superhero["appearance"]["weight"][1],
                            superhero["appearance"]["eye-color"], superhero["appearance"]["hair-color"]
                        ),
                        "Affiliations": superhero["connections"]["group-affiliation"],
                        "Relatives": superhero["connections"]["relatives"]
                    }

                    embed = discord.Embed(
                        title = "{} - {} {}".format(
                            superhero["name"], 
                            superhero["biography"]["full-name"],
                            "({})".format(
                                superhero["biography"]["alter-egos"]
                            ) if superhero["biography"]["alter-egos"] != "No alter egos found." else ""
                        ),
                        description = " ",
                        colour = await get_embed_color(ctx.author)
                    ).set_image(
                        url = superhero["image"]["url"]
                    )

                    for field in fields:
                        embed.add_field(
                            name = field,
                            value = fields[field],
                            inline = True
                        )
                    
                    await ctx.send(
                        embed = embed
                    )
                
                # Character is not from DC
                else:
                    await ctx.send(
                        embed = errors.get_error_message(
                            "That character is not from Marvel Comics."
                        )
                    )
            
            # Character was not found
            else:
                await ctx.send(
                    embed = errors.get_error_message(
                        "That character was not found."
                    )
                )
    
    @commands.command(
        name = "shortenUrl",
        aliases = ["shorten", "shortUrl", "url"],
        description = "Shortens a URL given.",
        cog_name = "internet"
    )
    async def shorten_url(self, ctx, *, url= None):
        
        # Check if url is None; Throw error message
        if url == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need to specify a URL to shorten."
                )
            )
        
        # URL is not none; Shorten it
        else:

            # Check if URL does not start with https:// or http://
            if not url.startswith("https://") and not url.startswith("http://"):
                await ctx.send(
                    embed = errors.get_error_message(
                        "The URL you provided is invalid."
                    )
                )
            
            # URL is valid
            else:
                tinyurl = await database.loop.run_in_executor(None,
                    requests.get,
                    TINYURL_API_CALL.format(url)
                )
                tinyurl = tinyurl.content.decode()

                await ctx.send(
                    embed = discord.Embed(
                        title = "Your TinyURL link was generated!",
                        description = tinyurl,
                        colour = await get_embed_color(ctx.author)
                    )
                )

    @commands.command(
        name = "weather",
        description = "Shows you the current weather for a specific place.",
        cog_name = "internet"
    )
    async def weather(self, ctx, *, location = None):

        # Check if location is None
        if location == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need to specify a location to get the weather for."
                )
            )
        
        else:

            # Call API
            response = await database.loop.run_in_executor(None,
                requests.get,
                WEATHER_API_CALL.format(
                    os.environ["WEATHER_API_KEY"],
                    location.replace(" ", "+")
                )
            )
            response = response.json()

            # Check if there was an error
            if "error" in response:
                await ctx.send(
                    embed = errors.get_error_message(
                        "There was an error: `{}`".format(
                            response["error"]["message"]
                        )
                    )
                )
            
            # There was no error
            else:
                await ctx.send(
                    embed = weather(response)
                )
    
    @commands.command(
        name = "forecast",
        description = "Shows you the forecaset for the next 7 days for a specific place.",
        cog_name = "internet"
    )
    async def forecast(self, ctx, *, location = None):

        # Check if location is None
        if location == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need to specify a location to get the weather for."
                )
            )
        
        else:

            # Call API
            response = await database.loop.run_in_executor(None,
                requests.get,
                FORECAST_API_CALL.format(
                    os.environ["WEATHER_API_KEY"],
                    location.replace(" ", "+")
                )
            )
            response = response.json()

            # Check if there was an error
            if "error" in response:
                await ctx.send(
                    embed = errors.get_error_message(
                        "There was an error: `{}`".format(
                            response["error"]["message"]
                        )
                    )
                )
            
            # There was no error
            else:

                # Get forecast
                fore_cast = forecast(response)

                # Create embed
                current = 0
                embed = discord.Embed(
                    title = "Forecast for {}".format(
                        fore_cast["location"]
                    ),
                    description = fore_cast["forecasts"][current]["date"],
                    colour = await get_embed_color(ctx.author)
                ).set_author(
                    name = "Apixu",
                    icon_url = "https://cdn.apixu.com/v4/images/logo.png",
                    url = "https://www.apixu.com"
                ).set_thumbnail(
                    url = fore_cast["forecasts"][current]["condition_icon"]
                )

                for field in fore_cast["forecasts"][current]:
                    if field not in ["date", "condition_icon"]:
                        embed.add_field(
                            name = field,
                            value = fore_cast["forecasts"][current][field]
                        )

                # Send message and add reactions
                msg = await ctx.send(
                    embed = embed
                )

                await add_scroll_reactions(msg, fore_cast["forecasts"])

                # Let user scroll through forecast
                while True:

                    def check_reaction(reaction, user):
                        return reaction.message.id == msg.id and user.id == ctx.author.id and str(reaction) in SCROLL_REACTIONS
                    
                    done, pending = await asyncio.wait([
                        self.bot.wait_for("reaction_add", check = check_reaction),
                        self.bot.wait_for("reaction_remove", check = check_reaction)
                    ], return_when = asyncio.FIRST_COMPLETED)
                    reaction, user = done.pop().result()

                    # Cancel all futures
                    for future in pending:
                        future.cancel()
                    
                    # Reaction is FIRST_PAGE
                    if str(reaction) == FIRST_PAGE:
                        current = 0
                    
                    # Reaction is LAST_PAGE
                    elif str(reaction) == LAST_PAGE:
                        current = len(fore_cast["forecasts"]) - 1
                    
                    # Reaction is PREVIOUS_PAGE
                    elif str(reaction) == PREVIOUS_PAGE:
                        current -= 1
                        if current < 0:
                            current = 0

                    # Reaction is NEXT_PAGE
                    elif str(reaction) == NEXT_PAGE:
                        current += 1
                        if current >= len(fore_cast["forecasts"]):
                            current = len(fore_cast["forecasts"]) - 1

                    # Reaction is LEAVE
                    elif str(reaction) == LEAVE:
                        await msg.delete()
                        break
                    
                    # Update embed
                    embed = discord.Embed(
                        title = "Forecast for {}".format(
                            fore_cast["location"]
                        ),
                        description = fore_cast["forecasts"][current]["date"],
                        colour = await get_embed_color(ctx.author)
                    ).set_author(
                        name = "Apixu",
                        icon_url = "https://cdn.apixu.com/v4/images/logo.png",
                        url = "https://www.apixu.com"
                    ).set_thumbnail(
                        url = fore_cast["forecasts"][current]["condition_icon"]
                    )

                    for field in fore_cast["forecasts"][current]:
                        if field not in ["date", "condition_icon"]:
                            embed.add_field(
                                name = field,
                                value = fore_cast["forecasts"][current][field]
                            )
                    
                    await msg.edit(
                        embed = embed
                    )

def setup(bot):
    bot.add_cog(Internet(bot))