import asyncio, discord, os, requests, json
from datetime import datetime
from discord.ext import commands
from functools import partial

import database
from category import errors
from category.globals import SCROLL_REACTIONS, FIRST_PAGE, LAST_PAGE, PREVIOUS_PAGE, NEXT_PAGE, LEAVE
from category.globals import get_embed_color

from .call_of_duty import call_of_duty
from .fortnite import add_fortnite_game_type
from .league import get_league_match_stats

# # # # # # # # # # # # # # # # # # # # # # # # #

BLACK_OPS_3_ICON = "https://mbtskoudsalg.com/images/black-ops-3-symbol-png-8.png"
BLACK_OPS_3_URL = "https://cod-api.tracker.gg/v1/standard/bo3/profile/{}/{}"

BLACK_OPS_4_ICON = "https://purepng.com/public/uploads/large/call-of-duty-black-ops-4-logo-idp.png"
BLACK_OPS_4_URL = "https://cod-api.tracker.gg/v1/standard/bo4/profile/{}/{}"
BLACK_OPS_4_LEVEL = 0

FORTNITE_URL = "https://api.fortnitetracker.com/v1/profile/{}/{}"
FORTNITE_ICON = "https://melbournechapter.net/images/meteor-transparent-fortnite-3.png"
FORTNITE_ITEM_SHOP_URL = "https://api.fortnitetracker.com/v1/store"
FORTNITE_MATCHES_PLAYED = 7
FORTNITE_WINS = 8
FORTNITE_KILLS = 10
FORTNITE_TOP_10 = 3
FORTNITE_TOP_25 = 5

LEAGUE_SUMMONER_URL = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}"
LEAGUE_MATCHES_URL = "https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/{}"
LEAGUE_MATCH_URL = "https://na1.api.riotgames.com/lol/match/v4/matches/{}"
LEAGUE_VERSIONS = "https://ddragon.leagueoflegends.com/api/versions.json"
LEAGUE_ICON_URL = "http://ddragon.leagueoflegends.com/cdn/{}/img/profileicon/{}.png"

# # # # # # # # # # # # # # # # # # # # # # # # #

class Stats(commands.Cog, name = "stats"):
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    """
    @commands.command(
        name = "blackOps3", 
        aliases = ["bo3"],
        description = "Gives you stats on a specific player in Black Ops 3.",
        cog_name = "stats"
    )
    async def black_ops_3(self, ctx, platform = None, username = None):
        
        # Check if platform is None; Throw error message
        if platform == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need the `platform` to search on and the `username` to look for."
                )
            )
        
        # Check if username is None; Throw error message
        elif username == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need the `username` to look for."
                )
            )
        
        # The platform and username are not None; Find the user
        else:

            # Check if platform is valid
            valid = True
            if platform in ["xbox", "xbx", "x"]:
                platform = 1
            elif platform in ["psn", "playstation", "p"]:
                platform = 2
            
            # Platform was invalid
            else:
                valid = False
                await ctx.send(
                    embed = errors.get_error_message(
                        "The platform you gave was invalid."
                    )
                )
            
            if valid:
                bo3 = await database.loop.run_in_executor(None,
                    partial(
                        requests.get,
                        BLACK_OPS_3_URL.format(platform, username),
                        headers = {
                            "TRN-Api-Key": os.environ["BLACK_OPS_API_KEY"]
                        }
                    )
                )
                bo3 = bo3.json()

                # See if an error is given
                if "errors" in bo3:
                    await ctx.send(
                        embed = errors.get_error_message(
                            "There was no user found with that username."
                        )
                    )
                
                # No error was given
                else:

                    # Get stats and put inside Embed
                    embed = discord.Embed(
                        title = "Black Ops 3 Stats",
                        description = "{} - {}".format(
                            bo3["data"]["metadata"]["platformUserHandle"],
                            "Xbox" if bo3["data"]["metadata"]["platformId"] == 1 else "PSN"
                        ),
                        colour = await get_embed_color(ctx.author),
                        timestamp = datetime.now()
                    ).set_author(
                        name = bo3["data"]["metadata"]["platformUserHandle"],
                        icon_url = BLACK_OPS_3_ICON
                    ).set_footer(
                        text = "Black Ops 3 Tracker"
                    )

                    # Add stats using Black Ops 3 parser
                    embed = call_of_duty(embed, bo3)

                    await ctx.send(
                        embed = embed
                    )
    
    @commands.command(
        name = "blackOps4", 
        aliases = ["bo4"],
        description = "Gives you stats on a specific player in Black Ops 4.",
        cog_name = "stats"
    )
    async def black_ops_4(self, ctx, platform = None, username = None):
        
        # Check if platform is None; Throw error message
        if platform == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need the `platform` to search on and the `username` to look for."
                )
            )
        
        # Check if username is None; Throw error message
        elif username == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need the `username` to look for."
                )
            )
        
        # The platform and username are not None; Find the user
        else:

            # Check if platform is valid
            valid = True
            if platform in ["xbox", "xbx", "x"]:
                platform = 1
            elif platform in ["psn", "playstation", "p"]:
                platform = 2
            elif platform in ["battlenet", "battle", "b", "pc"]:
                platform = 6
            
            # Platform was invalid
            else:
                valid = False
                await ctx.send(
                    embed = errors.get_error_message(
                        "The platform you gave was invalid."
                    )
                )
            
            if valid:
                bo4 = await database.loop.run_in_executor(None,
                    partial(
                        requests.get,
                        BLACK_OPS_4_URL.format(platform, username),
                        headers = {
                            "TRN-Api-Key": os.environ["BLACK_OPS_API_KEY"]
                        }
                    )
                )
                bo4 = bo4.json()

                # See if an error is given
                if "errors" in bo4:
                    await ctx.send(
                        embed = errors.get_error_message(
                            "There was no user found with that username."
                        )
                    )
                
                # No error was given
                else:

                    # Get stats and put inside Embed
                    embed = discord.Embed(
                        title = "Black Ops 4 Stats",
                        description = "{} - {}".format(
                            bo4["data"]["metadata"]["platformUserHandle"],
                            "Xbox" if bo4["data"]["metadata"]["platformId"] == 1 else "PSN"
                        ),
                        colour = await get_embed_color(ctx.author),
                        timestamp = datetime.now()
                    ).set_author(
                        name = bo4["data"]["metadata"]["platformUserHandle"],
                        icon_url = BLACK_OPS_4_ICON
                    ).set_footer(
                        text = "Black Ops 4 Tracker"
                    )

                    # Add stats using Black Ops 4 parser
                    embed = call_of_duty(embed, bo4)

                    await ctx.send(
                        embed = embed
                    )
    """
    
    @commands.command(
        name = "fortnite",
        description = "Gives you stats on a specific player in Fortnite.",
        cog_name = "stats"
    )
    async def fortnite(self, ctx, platform = None, username = None):
        
        # Check if platform is None; Throw error message
        if platform == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need the `platform` to search on and the `username` to look for."
                )
            )
        
        # Check if username is None; Throw error message
        elif username == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need the `username` to look for."
                )
            )
        
        # Platform and username are valid; Send the stats
        else:

            # Make sure platform is valid
            valid = True
            if platform in ["pc", "PC"]:
                platform = "pc"
            elif platform in ["xbox", "xbx", "x"]:
                platform = "xbox"
            elif platform in ["psn", "playstation", "p"]:
                platform = "psn"
            
            # Platform is not valid
            else:
                valid = False
                await ctx.send(
                    embed = errors.get_error_message(
                        "The platform you gave was invalid."
                    )
                )
            
            if valid:

                # Request data
                fortnite = await database.loop.run_in_executor(None,
                    partial(
                        requests.get,
                        FORTNITE_URL.format(platform, username),
                        headers = {
                            "TRN-Api-Key": os.environ["FORTNITE_API_KEY"]
                        }
                    )
                )
                fortnite = fortnite.json()
                print(json.dumps(fortnite, indent = 4))

                # See if an error was given.
                if "error" in fortnite:
                    await ctx.send(
                        embed = errors.get_error_message(
                            "There was no user found with that username."
                        )
                    )
                
                else:
                
                    # There was no error given; Get Solo, Duo, and Squad information
                    # Attempt to get each section of information; If no data for section
                    # Don't use it, set it to None
                    try:
                        solo = fortnite["stats"]["p2"]
                    except:
                        solo = None
                    try:
                        duo = fortnite["stats"]["p10"]
                    except:
                        duo = None
                    try:
                        squads = fortnite["stats"]["p9"]
                    except:
                        squads = None

                    try:
                        seasonSolo = fortnite["stats"]["curr_p2"]
                    except:
                        seasonSolo = None
                    try:
                        seasonDuo = fortnite["stats"]["curr_p10"]
                    except:
                        seasonDuo = None
                    try:
                        seasonSquads = fortnite["stats"]["curr_p9"]
                    except:
                        seasonSquads = None

                    gameTypeStats = [
                        solo, duo, squads,
                        seasonSolo, seasonDuo, seasonSquads
                    ]
                    gameTypes = [
                        "p2", "p10", "p9",
                        "curr_p2", "curr_p10", "curr_p9"
                    ]

                    lifetime = fortnite["lifeTimeStats"]

                    # Create embed
                    embed = discord.Embed(
                        title = "Fortnite Stats",
                        description = fortnite["epicUserHandle"] + " - " + fortnite["platformNameLong"],
                        colour = await get_embed_color(ctx.author),
                        timestamp = datetime.now()
                    ).set_author(
                        name = fortnite["epicUserHandle"],
                        icon_url = FORTNITE_ICON
                    ).set_footer(
                        text = "Fortnite Tracker"
                    )

                    for gameType in range(len(gameTypeStats)):
                        embed = add_fortnite_game_type(embed, gameTypeStats[gameType], gameTypes[gameType])
                    
                    # Add lifetime stats
                    embed.add_field(
                        name = "Lifetime Stats",
                        value = "{}\n{}\n{}\n{}\n{}\n".format(
                            "**Matches Played**: " + lifetime[FORTNITE_MATCHES_PLAYED]["value"],
                            "**Wins**: " + lifetime[FORTNITE_WINS]["value"],
                            "**Kills**: " + lifetime[FORTNITE_KILLS]["value"],
                            "**Top 10**: " + lifetime[FORTNITE_TOP_10]["value"],
                            "**Top 25**: " + lifetime[FORTNITE_TOP_25]["value"]
                        ),
                        inline = False
                    )

                    await ctx.send(
                        embed = embed
                    )
    
    @commands.command(
        name = "league", 
        aliases = ["lol"],
        description = "Gives you stats on a specific Summoner in League of Legends.",
        cog_name = "stats"
    )
    async def league(self, ctx, username = None):
        
        # Check if username is None; Throw error message
        if username == None:
            await ctx.send(
                embed = errors.get_error_message(
                    "You need the `username` of the Summoner to get information about."
                )
            )
        
        # Username was not None; Send stats
        else:

            # Get most recent version (used for profile icon)
            versionsJson = await database.loop.run_in_executor(None,
                requests.get,
                LEAGUE_VERSIONS
            )
            version = versionsJson.json()[0]
            
            # Request the user data
            leagueJson = await database.loop.run_in_executor(None,
                partial(
                    requests.get,
                    LEAGUE_SUMMONER_URL.format(username),
                    headers = {
                        "X-Riot-Token": os.environ["LEAGUE_API_KEY"]
                    }
                )
            )
            leagueJson = leagueJson.json()

            # Request the matches data
            leagueMatchesJson = await database.loop.run_in_executor(None,
                partial(
                    requests.get,
                    LEAGUE_MATCHES_URL.format(leagueJson["accountId"]),
                    headers = {
                        "X-Riot-Token": os.environ["LEAGUE_API_KEY"]
                    }
                )
            )
            leagueMatchesJson = leagueMatchesJson.json()
                
            # Show match data while user wants to
            count = 0
            msg = None
            while True:
                matches = leagueMatchesJson["matches"]
                match = matches[count]

                # Request the match data
                leagueMatchJson = await database.loop.run_in_executor(None,
                    partial(
                        requests.get,
                        LEAGUE_MATCH_URL.format(match["gameId"]),
                        headers = {
                            "X-Riot-Token": os.environ["LEAGUE_API_KEY"]
                        }
                    )
                )
                leagueMatchJson = leagueMatchJson.json()

                # Setup embed
                embed = discord.Embed(
                    title = "League of Legends Stats",
                    description = " ",
                    colour = await get_embed_color(ctx.author),
                    timestamp = datetime.fromtimestamp(int(leagueMatchJson["gameCreation"]) / 1000)
                ).set_author(
                    name = leagueJson["name"],
                    icon_url = LEAGUE_ICON_URL.format(version, leagueJson["profileIconId"])
                ).set_footer(
                    text = "Riot Games API"
                )

                embed = get_league_match_stats(embed, leagueMatchJson, leagueJson["accountId"])

                # Send message and add reactions
                if msg == None:
                    msg = await ctx.send(
                        embed = embed
                    )

                    if len(matches) > 1:

                        await msg.add_reaction(FIRST_PAGE)

                        if len(matches) > 2:
                            await msg.add_reaction(PREVIOUS_PAGE)
                            await msg.add_reaction(NEXT_PAGE)
                        
                        await msg.add_reaction(LAST_PAGE)
                    
                    await msg.add_reaction(LEAVE)
                
                else:
                    await msg.edit(
                        embed = embed
                    )

                # Wait for reactions
                def check(reaction, user):
                    return str(reaction) in SCROLL_REACTIONS and reaction.message.id == msg.id and user == ctx.author
                
                done, pending = await asyncio.wait([
                    self.bot.wait_for("reaction_add", check = check),
                    self.bot.wait_for("reaction_remove", check = check)
                ], return_when = asyncio.FIRST_COMPLETED)

                reaction, user = done.pop().result()

                # Cancel all futures
                for future in pending:
                    future.cancel()
                
                # Reaction is first page
                if str(reaction) == FIRST_PAGE:
                    count = 0
                
                # Reaction is last page
                elif str(reaction) == LAST_PAGE:
                    count = len(matches) - 1
                
                # Reaction is previous page
                elif str(reaction) == PREVIOUS_PAGE:
                    count -= 1
                    if count < 0:
                        count = 0
                
                # Reaction is next page
                elif str(reaction) == NEXT_PAGE:
                    count += 1
                    if count >= len(matches):
                        count = len(matches) - 1
                
                # Reaction is leave
                elif str(reaction) == LEAVE:
                    await msg.delete()
                    break

def setup(bot):
    bot.add_cog(Stats(bot))