import json

SEASONS = {
    "0": "Preseason 3", "1": "Season 3",
    "2": "Preseason 2014", "3": "Season 2014",
    "4": "Preseason 2015", "5": "Season 2015",
    "6": "Preseason 2016", "7": "Season 2016",
    "8": "Preseason 2017", "9": "Season 2017",
    "10": "Preseason 2018", "11": "Season 2018",
    "12": "Preseason 2019", "13": "Season 2019"
}

MATCH_QUEUES = {
    "0": "Custom Game",
    "72": "1v1 Snowdown Showdown", "73": "2v2 Snowdown Showdown",
    "75": "6v6 Hexakill", "76": "Ultra Rapid Fire", "78": "One For All: Mirror Mode",
    "83": "Co-op vs AI Ultra Rapid Fire", "98": "6v6 Hexakill",
    "100": "5v5 ARAM", "310": "Nemesis", "313": "Black Market Brawlers", 
    "317": "Definitely Not Dominion", "325": "All Random",
    "400": "5v5 Draft Pick", "420": "5v5 Ranked Solo", 
    "430": "5v5 Blind Pick", "440": "5v5 Ranked Flex",
    "450": "5v5 ARAM", "460": "3v3 Blind Pick", "470": "3v3 Ranked Flex",
    "600": "Blood Hunt Assassin", "610": "Dark Star: Singularity",
    "700": "Clash", "800": "Co-op vs AI Intermediate Bot",
    "810": "Co-op vs AI Intro Bot", "820": "Co-op vs AI Beginner Bot",
    "830": "Co-op vs AI Intro Bot", "840": "Co-op vs AI Beginner Bot",
    "850": "Co-op vs AI Intermediate Bot", "900": "ARURF",
    "910": "Ascension", "920": "Legend of the Poro King",
    "940": "Nexus Siege", "950": "Doom Bots Voting",
    "960": "Doom Bots Standard", "980": "Star Guardian Invasion: Normal",
    "990": "Star Guardian Invasion: Onslaught", "1000": "PROJECT: Hunters",
    "1010": "Snow ARURF", "1020": "One for All", "1030": "Odyssey Extraction: Intro",
    "1040": "Odyssey Extraction: Crewmember", "1060": "Odyssey Extraction: Captain",
    "1070": "Odyssey Extraction: Onslaught", "1200": "Nexus Blitz"
}

BLUE = 100
RED = 200

def get_league_match_stats(discordEmbed, matchDict, accountId):
    """Gets the match stats and adds them to the specified Embed

    Parameters:
        discordEmbed (discord.Embed): The Embed to add the stats to.
        matchDict (dict): The dictionary of the match stats.
        accountId (int): The account ID to get results for.
    """

    # Get each team info
    team1 = matchDict["teams"][0]
    team2 = matchDict["teams"][1]

    # Get winning team ID
    winningTeamId = team1["teamId"] if team1["win"] == "Win" else team2["teamId"]

    # Get accountId's participantId
    participantId = -1
    for participant in matchDict["participantIdentities"]:
        if participant["player"]["accountId"] == accountId:
            participantId = participant["participantId"]
            break
    
    # Get participantIdentities
    participantIdentities = matchDict["participantIdentities"]

    # Search through participants until found participantId and see if there was a victory
    victory = False
    for participant in matchDict["participants"]:
        if participantId == participant["participantId"]:
            victory = participant["teamId"] == winningTeamId
            break

    # Get blue and red team information
    # First, find longest value for each stat (Name, Tier, KDA and Ratio, Total Damage)
    nameLength   = 0
    tierLength   = 0
    kdaLength    = 0
    damageLength = 0
    for participant in range(len(matchDict["participants"])):
        participantName = participantIdentities[participant]["player"]["summonerName"]
        participant = matchDict["participants"][participant]

        name = participantName
        if len(name) > nameLength:
            nameLength = len(name)

        try:
            tier = participant["highestAchievedSeasonTier"]
        except:
            tier = "Unknown"

        if len(tier) > tierLength:
            tierLength = len(tier)
        
        kda = "{}/{}/{} ({})".format(
            participant["stats"]["kills"],
            participant["stats"]["deaths"],
            participant["stats"]["assists"],
            round((participant["stats"]["kills"] + participant["stats"]["assists"]) / (participant["stats"]["deaths"] if participant["stats"]["deaths"] != 0 else 1), 2)
        )
        if len(kda) > kdaLength:
            kdaLength = len(kda)
        
        damage = str(participant["stats"]["totalDamageDealtToChampions"])
        if len(damage) > damageLength:
            damageLength = len(damage)

    blueTeamText = ""
    redTeamText = ""
    count = 0
    for participant in matchDict["participants"]:
        participantName = participantIdentities[count]["player"]["summonerName"]

        try:
            tier = participant["highestAchievedSeasonTier"]
        except:
            tier = "Unknown"

        # Get participant Name, Tier, KDA and Ratio, and Total Damage
        participantInfo = "{} - {} - {} - {}".format(
            participantName.ljust(nameLength),              # Name

            tier.capitalize().ljust(tierLength),       # Tier

            "{}/{}/{} ({})".format(
                participant["stats"]["kills"],      # KDA and Ratio
                participant["stats"]["deaths"],     #
                participant["stats"]["assists"],    #
                round((participant["stats"]["kills"] + participant["stats"]["assists"]) / (participant["stats"]["deaths"] if participant["stats"]["deaths"] != 0 else 1), 2)
            ).ljust(kdaLength),
            
            str(participant["stats"]["totalDamageDealtToChampions"]).ljust(damageLength)      # Total Damage
        )

        # Highlight (Bold and Emphasize) Participant if was one that was looked up
        #if participant["participantId"] == participantId:
         #   participantInfo = "**_" + participantInfo + "_**"
        if participant["teamId"] == winningTeamId:
            participantInfo = "+ " + participantInfo
        else:
            participantInfo = "- " + participantInfo

        # Add to Blue or Red team based off of Team ID (100 is Blue, 200 is Red)
        if participant["teamId"] == BLUE:
            blueTeamText += participantInfo + "\n"
        else:
            redTeamText += participantInfo + "\n"
        count += 1

    # Setup fields
    fields = {
        "Stats": "**{}** - _{}_\nDuration: {}".format(
            "Unknown" if str(matchDict["queueId"]) not in MATCH_QUEUES else MATCH_QUEUES[str(matchDict["queueId"])],
            "Victory" if victory else "Defeat",
            convertSeconds(matchDict["gameDuration"])
        ),
        "Blue Team": "```diff\n{}\n```".format(blueTeamText),
        "Red Team": "```diff\n{}\n```".format(redTeamText)
    }

    # Add fields to embed
    for field in fields:
        discordEmbed.add_field(
            name = field,
            value = fields[field],
            inline = False
        )

    return discordEmbed

def convertSeconds(seconds):
    """Converts seconds into a string.

    Example: 2435 becomes 40m 35s
             1361 becomes 22m 41s

    Parameters:
        seconds (int): The amount of seconds to convert.
    """

    # Get hours
    hours = seconds // 3600
    seconds -= (hours * 3600)

    # Get minutes
    minutes = seconds // 60
    seconds -= (minutes * 60)

    # Add hours if not 0
    result = ""
    if hours > 0:
        result += str(hours) + "h "
    
    # Add minutes if not 0
    if minutes > 0:
        result += str(minutes) + "m "
    
    # Add seconds if not 0
    if seconds > 0:
        result += str(seconds) + "s"
    
    return result