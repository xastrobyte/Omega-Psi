import discord

def processColor(colorJson):
    """Gets the information about a color and puts it into an embed.
    """

    tags = {
        "Hex": "0x{}".format(
            colorJson["hex"]["clean"]
        ),
        "RGB": "{}, {}, {}".format(
            colorJson["rgb"]["r"], colorJson["rgb"]["g"], colorJson["rgb"]["b"]
        ),
        "HSL": "{}, {}%, {}%".format(
            colorJson["hsl"]["h"], colorJson["hsl"]["s"], colorJson["hsl"]["l"]
        ),
        "CMYK": "{}, {}, {}, {}".format(
            colorJson["cmyk"]["c"], colorJson["cmyk"]["m"], colorJson["cmyk"]["y"], colorJson["cmyk"]["k"]
        )
    }
    
    # Create embed and add color tags to it
    embed = discord.Embed(
        title = colorJson["name"]["value"],
        description = " ",
        colour = eval(tags["Hex"])
    )

    for tag in tags:
        embed.add_field(
            name = tag,
            value = tags[tag],
            inline = True
        )
    
    return embed