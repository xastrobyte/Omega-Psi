from discord import Embed
from datetime import datetime

from .gamemodes import COD_MW_MODES, COD_MW_MAPS

from util.string import seconds_to_runtime

# # # # # # # # # # # # # # # # # # # #

LOST = 0x804040  # Bright red
WON  = 0x408040  # Bright green

# # # # # # # # # # # # # # # # # # # #

def build_mw_match(match):
    """Creates a Discord Embed for the specified match

    :param match: The Modern Warfare match to build an embed for
    """

    # Create the embed and fields for the match
    embed = Embed(
        title = COD_MW_MODES[match["mode"]],
        description = COD_MW_MAPS[match["map"]],
        colour = LOST if match["result"] == "loss" else WON,
        timestamp = datetime.fromtimestamp(match["utcStartSeconds"])
    ).set_author(
        name = match["player"]["username"]
    )
    fields = {
        "Match Length": seconds_to_runtime(match["duration"] // 1000),

        "Score": match["playerStats"]["score"],
        "Score XP": match["playerStats"]["scoreXp"],
        "Total XP": match["playerStats"]["totalXp"],

        "Most Killed": match["player"]["mostKilled"] if "mostKilled" in match["player"] else "None",
        "Nemesis": match["player"]["nemesis"] if "nemesis" in match["player"] else "None",
        "K/D/R": "{}/{}/{}".format(
            match["playerStats"]["kills"],
            match["playerStats"]["deaths"],
            str(round(match["playerStats"]["kdRatio"], 2))
        ),

        "Headshots": match["playerStats"]["headshots"],
        "Executions": match["playerStats"]["executions"],
        "Assists": match["playerStats"]["assists"]
    }

    # Add the fields for the match
    for field in fields:
        embed.add_field(
            name = field,
            value = fields[field],
            inline = field != "Match Length"
        )
    return embed

def build_wz_match(match):
    """Creates a Discord Embed for the specified match

    :param match: The Warzone match to build an embed for
    """

    # Create the embed and fields for the match
    embed = Embed(
        title = COD_MW_MODES[match["mode"]],
        description = COD_MW_MAPS[match["map"]],
        colour = LOST if match["playerStats"]["teamPlacement"] != 1 else WON,
        timestamp = datetime.fromtimestamp(match["utcStartSeconds"])
    ).set_author(
        name = ""
    )
    fields = {
        "Match Length": seconds_to_runtime(match["duration"] // 1000),

        "Score": f"{match['playerStats']['score']:,}",
        "Score XP": f"{match['playerStats']['scoreXp']:,}",
        "Total XP": f"{match['playerStats']['matchXp']:,}",

        "Damage Done": f"{match['playerStats']['damageDone']:,}",
        "Damage Taken": f"{match['playerStats']['damageTaken']:,}",
        "K/D/R": "{}/{}/{}".format(
            match["playerStats"]["kills"],
            match["playerStats"]["deaths"],
            str(round(match["playerStats"]["kdRatio"], 2))
        ),

        "Headshots": match["playerStats"]["headshots"],
        "Executions": match["playerStats"]["executions"],
        "Assists": match["playerStats"]["assists"]
    }

    # Add the fields for the match
    for field in fields:
        embed.add_field(
            name = field,
            value = fields[field],
            inline = field != "Match Length"
        )
    return embed