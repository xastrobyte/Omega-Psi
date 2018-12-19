def getGameStats(discordEmbed, gameStatsDict):
    """Adds the Game Stats for a Call of Duty player to the specified embed

    Parameters:
        discordEmbed (discord.Embed): The Embed to add the stats to.
        gameStatsDict (dict): The dictionary of the stats to add.
    """

    # Get just the stats
    stats = gameStatsDict["data"]["stats"]

    # Iterate through stats
    statCategories = {}
    for stat in stats:

        # Make an empty category name to Other
        if stat["metadata"]["categoryName"] == "":
            stat["metadata"]["categoryName"] = "Other"

        # Add to stat category
        if stat["metadata"]["categoryName"] not in statCategories:
            statCategories[stat["metadata"]["categoryName"]] = ""

        statCategories[stat["metadata"]["categoryName"]] += "**{}**: {} {}\n".format(
            stat["metadata"]["name"], stat["displayValue"], 
            "" if "percentile" not in stat else "({}%)".format(
                stat["percentile"]
            )
        )
    
    for category in statCategories:
        discordEmbed.add_field(
            name = category,
            value = statCategories[category],
            inline = True
        )
    
    return discordEmbed