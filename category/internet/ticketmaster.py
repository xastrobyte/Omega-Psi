import discord

from category.globals import get_embed_color

from util.string import timestamp_to_datetime

IGNORE_EXTERNAL = ["musicbrainz"]

async def get_event_embed(ctx, event_json):

    # Get title and url of event
    title = event_json["name"]
    url = event_json["url"]

    # Get largest image for event
    largest_index = 0
    largest_dimensions = 0
    for image in range(len(event_json["images"])):
        img = event_json["images"][image]

        if img["width"] * img["height"] > largest_dimensions:
            largest_dimensions = img["width"] * img["height"]
            largest_index = image
    
    # Get time of event
    if not event_json["dates"]["start"]["timeTBA"]:
        time = event_json["dates"]["start"]["localTime"]
    else:
        time = "*TBA*"
    
    if not event_json["dates"]["start"]["dateTBA"]:
        date = event_json["dates"]["start"]["localDate"]
    else:
        date = "*TBA*"

    # Get Venue name and url
    venue = event_json["_embedded"]["venues"][0]
    if "name" in venue:
        venue_name = venue["name"]
    else:
        venue_name = "**_Unknown Venue_**"
    
    if "url" in venue:
        venue_url = venue["url"]
    else:
        venue_url = None

    # Get Location (Address, City, State, Country, Postal Code)
    if "address" in venue:
        if "line1" in venue["address"]:
            address = venue["address"]["line1"]
        elif "line2" in venue["address"]:
            address = venue["address"]["line2"]
        else:
            address = "**_Unknown Address_**"
    else:
        address = "**_Unknown Address_**"
    
    if "city" in venue:
        city = venue["city"]["name"]
    else:
        city = "**_Unknown City_**"
    
    if "state" in venue:
        state = venue["state"]["name"]
    else:
        state = "**_Unknown State_**"
    
    if "country" in venue:
        country = venue["country"]["name"]
    else:
        country = "**_Unknown Country_**"
    
    if "postalCode" in venue:
        postal_code = venue["postalCode"]
    else:
        postal_code = ""

    location = "{}\n{}, {}, {}, {}".format(
        address,
        city,
        state,
        country,
        postal_code
    )

    # Get Performers (Attractions)
    performers = []
    for attraction in event_json["_embedded"]["attractions"]:
        if "name" not in attraction:
            performers.append("**_Unknown Performer_**")
        else:
            performers.append(
                "[**{}**]({})".format(
                    attraction["name"],
                    attraction["url"]
                )
            )
    
    # Setup fields
    fields = {
        "Date/Time": "**Date**: {}\n**Time**: {}".format(
            date, time
        ),
        "Venue": "[**{}**]({})".format(
            venue_name,
            venue_url
        ) if venue_url != None else "**{}**".format(venue_name),
        "Location": location,
        "Performers": "\n".join(performers)
    }

    # Create embed
    embed = discord.Embed(
        title = title,
        description = "_ _",
        colour = await get_embed_color(ctx.author),
        url = url
    ).set_image(
        url = event_json["images"][largest_index]["url"]
    )

    for field in fields:
        embed.add_field(
            name = field,
            value = fields[field]
        )
    
    return embed

async def get_attraction_embed(ctx, attraction_json):
    
    # Get name and url
    name = attraction_json["name"]
    url = attraction_json["url"]

    # Get external links (ignoring musicbrainz)
    external_links = []
    for link in attraction_json["externalLinks"]:
        if link not in IGNORE_EXTERNAL:
            external_links.append("[**{}**]({})".format(
                link.title(),
                attraction_json["externalLinks"][link][0]["url"]
            ))
    
    # Get largest image for attraction
    largest_index = 0
    largest_dimensions = 0
    for image in range(len(attraction_json["images"])):
        img = attraction_json["images"][image]

        if img["width"] * img["height"] > largest_dimensions:
            largest_dimensions = img["width"] * img["height"]
            largest_index = image
    image = attraction_json["images"][largest_index]["url"]

    # Get genre and subgenre
    if "genre" in attraction_json["classifications"][0]:
        genre = attraction_json["classifications"][0]["genre"]["name"]
    else:
        genre = None

    if "subGenre" in attraction_json["classifications"][0]:
        sub_genre = attraction_json["classifications"][0]["subGenre"]["name"]
    else:
        sub_genre = None
    
    if genre == sub_genre == None:
        genre = "**_Unknown Genre_**"
    elif sub_genre and not genre:
        genre = sub_genre
    elif genre and sub_genre:
        genre = "{}, {}".format(
            genre, sub_genre
        )
    
    # Create fields
    fields = {
        "Genre": genre,
        "Social Links": "\n".join(external_links)
    }
    
    # Create embed
    embed = discord.Embed(
        title = name,
        description = "_ _",
        colour = await get_embed_color(ctx.author),
        url = url
    ).set_image(
        url = image
    )

    # Add fields
    for field in fields:
        embed.add_field(
            name = field,
            value = fields[field]
        )
    
    return embed