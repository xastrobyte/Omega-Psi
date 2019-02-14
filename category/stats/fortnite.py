V_BUCKS_ICON = "https://image.fnbr.co/price/icon_vbucks_50x.png"

def add_fortnite_game_type(discordEmbed, gameTypeDict, gameType):
    """Adds the data for a game type to the specified embed

    Parameters:
        discordEmbed (discord.Embed): The Embed to add to.
        gameTypeDict (dict): The dict to use.
    """

    # Only do it if gameTypeDict is not None
    if gameTypeDict != None:

        # Keep track of game types
        gameTypes = {
            "p2": "Solo", "p10": "Duo", "p9": "Squad",
            "curr_p2": "Season Solo", "curr_p10": "Season Duo", "curr_p9": "Season Squad"
        }

        if gameType.find("p2") != -1:
            topN1 = {
                "text": "Top 10",
                "value": gameTypeDict["top10"]["value"]
            }
            topN2 = {
                "text": "Top 25",
                "value": gameTypeDict["top25"]["value"]
            }
        
        elif gameType.find("p10") != -1:
            topN1 = {
                "text": "Top 5",
                "value": gameTypeDict["top5"]["value"]
            }
            topN2 = {
                "text": "Top 12",
                "value": gameTypeDict["top12"]["value"]
            }
        
        else:
            topN1 = {
                "text": "Top 3",
                "value": gameTypeDict["top3"]["value"]
            }
            topN2 = {
                "text": "Top 6",
                "value": gameTypeDict["top6"]["value"]
            }

        discordEmbed.add_field(
            name = gameTypes[gameType],
            value = "{}\n{}\n{}\n{}\n{}\n{}\n".format(
                "**Matches**: " + gameTypeDict["matches"]["value"],
                "**Wins**: " + gameTypeDict["top1"]["value"],
                "**{}**: {}".format(topN1["text"], topN1["value"]),
                "**{}**: {}".format(topN2["text"], topN2["value"]),
                "**Kills**: {}".format(gameTypeDict["kills"]["value"]),
                "**K/d**: " + gameTypeDict["kd"]["value"]
            ),
            inline = True
        )

    return discordEmbed