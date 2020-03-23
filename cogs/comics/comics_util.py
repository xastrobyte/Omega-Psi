from discord import Embed

from cogs.globals import PRIMARY_EMBED_COLOR

def get_marvel_character_embed(attribution_text, result):
    """Parses a given JSON object that contains a result of a Marvel 
    character and turns it into an Embed

    Parameters
    ----------
        attribution_text : str
            The attributions to give to Marvel for using the API
        result : dict
            A JSON object of a Marvel API call result
    
    Returns
    -------
        Embed
    """
    return Embed(
        title = result["name"],
        description = result["description"],
        colour = PRIMARY_EMBED_COLOR
    ).add_field(
        name = "Series",
        value = "\n".join([
            "\* `{}`".format(series["name"])
            for series in result["series"]["items"]
        ])
    ).add_field(
        name = "Comics",
        value = "\n".join([
            "\* `{}`".format(comic["name"])
            for comic in result["comics"]["items"]
        ])
    ).set_image(
        url = "{}.{}".format(
            result["thumbnail"]["path"],
            result["thumbnail"]["extension"]
        )
    ).set_footer(
        text = attribution_text
    )

def get_marvel_series_embed(attribution_text, result):
    """Parses a given JSON object that contains a result of a Marvel 
    series and turns it into an Embed

    Parameters
    ----------
        attribution_text : str
            The attributions to give to Marvel for using the API
        result : dict
            A JSON object of a Marvel API call result
    
    Returns
    -------
        Embed
    """

    # Create the embed
    embed = Embed(
        title = result["title"],
        description = result["description"],
        colour = PRIMARY_EMBED_COLOR
    ).add_field(
        name = "Years Active",
        value = "{} - {}".format(result["startYear"], result["endYear"])
    ).set_image(
        url = "{}.{}".format(
            result["thumbnail"]["path"],
            result["thumbnail"]["extension"]
        )
    ).set_footer(
        text = attribution_text
    )

    # Add the previous series if it exists
    if result["previous"] is not None:
        embed.add_field(
            name = "Previous Series",
            value = result["previous"]["name"]
        )
    
    # Add the next series if it exists
    if result["next"] is not None:
        embed.add_field(
            name = "Next Series",
            value = result["next"]["name"]
        )
    return embed

def get_marvel_comic_embed(attribution_text, result):
    """Parses a given JSON object that contains a result of a Marvel 
    comic and turns it into an Embed

    Parameters
    ----------
        attribution_text : str
            The attributions to give to Marvel for using the API
        result : dict
            A JSON object of a Marvel API call result
    
    Returns
    -------
        Embed
    """
    return Embed(
        title = result["title"],
        description = result["description"] if result["description"] is not None else "No description exists for this issue",
        colour = PRIMARY_EMBED_COLOR
    ).add_field(
        name = "Issue Information",
        value = (
            """
            **Issue #**: {}
            **Print Price**: {}
            **# of Pages**: {}
            """
        ).format(
            result["issueNumber"],
            "${}".format(result["prices"][0]["price"]) if len(result["prices"]) > 0 else "Unknown",
            result["pageCount"]
        )
    ).add_field(
        name = "Links",
        value = "\n".join([
            "[{}]({})".format(
                url["type"].title(), url["url"]
            )
            for url in result["urls"]
        ])
    ).set_image(
        url = "{}.{}".format(
            result["thumbnail"]["path"],
            result["thumbnail"]["extension"]
        )
    ).set_footer(
        text = attribution_text
    )