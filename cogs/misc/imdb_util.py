from datetime import datetime
from discord import Embed

from cogs.globals import loop

from util.functions import get_embed_color
from util.string import minutes_to_runtime

# # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # #

async def get_movie_embed(ctx, imdb, movie, movie_link):
    """Retrieves a movie object and gets the data associated with the movie
    to put into an Embed

    Parameters
    ----------
        ctx : Context
            The context that the movie command was run in
        imdb : IMDb
            The IMDb object to use to access movie data
        movie : Movie
            The movie object to process
        movie_link : str
            A formatted string to get the link to the specified movie on IMDb
    """

    movie = await loop.run_in_executor(None,
        imdb.get_movie,
        movie.movieID
    )

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
    except: plotOutline = "No Plot Outline Yet"

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
    embed = Embed(
        title = title,
        description = plotOutline,
        colour = await get_embed_color(ctx.author),
        timestamp = datetime.now(),
        url = movie_link.format(movie.movieID)
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
    
    return embed

async def get_tv_show_embed(ctx, imdb, tv_show, tv_show_link):
    """Retrieves a tv show object and gets the data associated with the tv show
    to put into an Embed

    Parameters
    ----------
        ctx : Context
            The context that the tvShow command was run in
        imdb : IMDb
            The IMDb object to use to access tv show data
        tv_show : TVShow
            The tv show object to process
        tv_show_link : str
            A formatted string to get the link to the specified tv show on IMDb
    """

    show = await loop.run_in_executor(None,
        imdb.get_movie,
        tv_show.movieID
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
    embed = Embed(
        title = title,
        description = plotOutline,
        colour = await get_embed_color(ctx.author),
        timestamp = datetime.now(),
        url = tv_show_link.format(show.movieID)
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
    
    return embed