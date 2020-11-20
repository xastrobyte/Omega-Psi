from discord import Embed
from discord.ext.commands import Cog, command, group
from functools import partial
from requests import get
from os import environ
from urllib.parse import quote

from cogs.globals import loop
from cogs.errors import get_error_message, UNIMPLEMENTED_ERROR

from util.database.database import database
from util.discord import process_scrolling
from util.functions import get_embed_color
from util.string import seconds_to_runtime

from .call_of_duty import build_mw_match, build_wz_match

# # # # # # # # # # # # # # # # # # # # # # # # #

DIVISION_2_URL = "https://public-api.tracker.gg/v2/division-2/standard/profile/{}/{}"
MW_MULTI_STATS_URL = "https://call-of-duty-modern-warfare.p.rapidapi.com/multiplayer/{}/{}"
MW_MULTI_MATCH_URL = "https://call-of-duty-modern-warfare.p.rapidapi.com/multiplayer-matches/{}/{}"
MW_WAR_STATS_URL = "https://call-of-duty-modern-warfare.p.rapidapi.com/warzone/{}/{}"
MW_WAR_MATCH_URL = "https://call-of-duty-modern-warfare.p.rapidapi.com/warzone-matches/{}/{}"

# # # # # # # # # # # # # # # # # # # # # # # # #

class Stats(Cog, name="stats"):
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @group(
        name="modernWarfare", aliases=["mw"],
        description="Retrieves either the game stats or the 10 most recent matches for a user that plays Call of Duty: Modern Warfare (2019)",
        cog_name="stats"
    )
    async def modern_warfare(self, ctx):
        """The parent command for Modern Warfare mode commands"""
        if not ctx.invoked_subcommand:
            await ctx.send(embed = get_error_message(
                "Try running `{}help modernWarfare` :)".format(
                    await database.guilds.get_prefix(ctx.guild) 
                    if ctx.guild is not None else ""
                )
            ))
    
    @modern_warfare.group(
        name="stats",
        description="Retrieves the game stats for a user that plays Modern Warfare",
        cog_name="stats"
    )
    async def modern_warfare_stats(self, ctx):
        """The parent command for Modern Warfare stats commands"""
        if not ctx.invoked_subcommand:
            await ctx.send(embed = get_error_message(
                "Try running `{}help modernWarfare stats` :)".format(
                    await database.guilds.get_prefix(ctx.guild) 
                    if ctx.guild is not None else ""
                )
            ))
    
    @modern_warfare.group(
        name="matches", aliases=["match"],
        description="Retrieves the 10 most recent matches that a user played in Modern Warfare",
        cog_name="stats"
    )
    async def modern_warfare_matches(self, ctx):
        """The parent command for Modern Warfare matches commands"""
        if not ctx.invoked_subcommand:
            await ctx.send(embed = get_error_message(
                "Try running `{}help modernWarfare matches` :)".format(
                    await database.guilds.get_prefix(ctx.guild) 
                    if ctx.guild is not None else ""
                )
            ))
    
    @modern_warfare_stats.command(
        name="steam",
        description="Retrieves game stats for a user that plays Modern Warfare on Steam",
        cog_name="stats"
    )
    async def modern_warfare_stats_steam(self, ctx, *, username=None):
        """Gives the user game stats on a specified player that plays Modern Warfare
        on PC (steam)

        :param ctx: The context of where the message was sent
        :param username: The username to search for
        """
        await self.modern_warfare_lookup(ctx, "steam", "stats", username)
    
    @modern_warfare_stats.command(
        name="battle",
        description="Retrieves game stats for a user that plays Modern Warfare on Battle.net",
        cog_name="stats"
    )
    async def modern_warfare_stats_battle(self, ctx, *, username=None):
        """Gives the user game stats on a specified player that plays Modern Warfare
        on PC (battle)

        :param ctx: The context of where the message was sent
        :param username: The username to search for
        """
        await self.modern_warfare_lookup(ctx, "battle", "stats", username)
    
    @modern_warfare_stats.command(
        name="xbox", aliases=["xbl"],
        description="Retrieves game stats for a user that plays Modern Warfare on Xbox",
        cog_name="stats"
    )
    async def modern_warfare_xbox(self, ctx, *, username=None):
        """Gives the user game stats on a specified player that plays Modern Warfare
        on Xbox (xbl)

        :param ctx: The context of where the message was sent
        :param username: The username to search for
        """
        await self.modern_warfare_lookup(ctx, "xbl", "stats", username)
    
    @modern_warfare_stats.command(
        name="playstation", aliases=["psn", "ps"],
        description="Retrieves game stats for a user that plays Modern Warfare on Playstation",
        cog_name="stats"
    )
    async def modern_warfare_playstation(self, ctx, *, username=None):
        """Gives the user game stats on a specified player that plays Modern Warfare
        on Playstation (psn)

        :param ctx: The context of where the message was sent
        :param username: The username to search for
        """
        await self.modern_warfare_lookup(ctx, "psn", "stats", username)
    
    @modern_warfare_matches.command(
        name="steam",
        description="Retrieves the 10 most recent matches for a user that plays Modern Warfare on Steam",
        cog_name="stats"
    )
    async def modern_warfare_matches_steam(self, ctx, *, username=None):
        """Gives the 10 most recent matches for a specified player that plays Modern Warfare
        on Steam (steam)

        :param ctx: The context of where the message was sent
        :param username: The username to search for
        """
        await self.modern_warfare_lookup(ctx, "steam", "matches", username)
    
    @modern_warfare_matches.command(
        name="battle",
        description="Retrieves the 10 most recent matches for a user that plays Modern Warfare on Battle.net",
        cog_name="stats"
    )
    async def modern_warfare_matches_battle(self, ctx, *, username=None):
        """Gives the 10 most recent matches for a specified player that plays Modern Warfare
        on Battle.net (battle)

        :param ctx: The context of where the message was sent
        :param username: The username to search for
        """
        await self.modern_warfare_lookup(ctx, "battle", "matches", username)
    
    @modern_warfare_matches.command(
        name="xbox", aliases=["xbl"],
        description="Retrieves the 10 most recent matches for a user that plays Modern Warfare on Xbox",
        cog_name="stats"
    )
    async def modern_warfare_matches_xbox(self, ctx, *, username=None):
        """Gives the 10 most recent matches for a specified player that plays Modern Warfare
        on Xbox (xbl)

        :param ctx: The context of where the message was sent
        :param username: The username to search for
        """
        await self.modern_warfare_lookup(ctx, "xbl", "matches", username)
    
    @modern_warfare_matches.command(
        name="playstation", aliases=["psn", "ps"],
        description="Retrieves the 10 most recent matches for a user that plays Modern Warfare on Playstation",
        cog_name="stats"
    )
    async def modern_warfare_matches_playstation(self, ctx, *, username=None):
        """Gives the 10 most recent matches for a specified player that plays Modern Warfare
        on Playstation (psn)

        :param ctx: The context of where the message was sent
        :param username: The username to search for
        """
        await self.modern_warfare_lookup(ctx, "psn", "matches", username)
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @group(
        name="warzone", aliases=["wz"],
        description="Retrieves either the game stats or the 10 most recent matches for a user that plays Call of Duty: Warzone (2019)",
        cog_name="stats"
    )
    async def warzone(self, ctx):
        """The parent command for Warzone mode commands"""
        if not ctx.invoked_subcommand:
            await ctx.send(embed = get_error_message(
                "Try running `{}help warzone` :)".format(
                    await database.guilds.get_prefix(ctx.guild) 
                    if ctx.guild is not None else ""
                )
            ))
    
    @warzone.group(
        name="stats",
        description="Retrieves the game stats for a user that plays Warzone",
        cog_name="stats"
    )
    async def warzone_stats(self, ctx):
        """The parent command for Warzone stats commands"""
        if not ctx.invoked_subcommand:
            await ctx.send(embed = get_error_message(
                "Try running `{}help warzone stats` :)".format(
                    await database.guilds.get_prefix(ctx.guild) 
                    if ctx.guild is not None else ""
                )
            ))
    
    @warzone.group(
        name="matches", aliases=["match"],
        description="Retrieves the 10 most recent matches that a user played in Warzone",
        cog_name="stats"
    )
    async def warzone_matches(self, ctx):
        """The parent command for Warzone matches commands"""
        if not ctx.invoked_subcommand:
            await ctx.send(embed = get_error_message(
                "Try running `{}help warzone matches` :)".format(
                    await database.guilds.get_prefix(ctx.guild) 
                    if ctx.guild is not None else ""
                )
            ))
    
    @warzone_stats.command(
        name="steam",
        description="Retrieves game stats for a user that plays Warzone on Steam",
        cog_name="stats"
    )
    async def warzone_stats_steam(self, ctx, *, username=None):
        """Gives the user game stats on a specified player that plays Warzone
        on PC (steam)

        :param ctx: The context of where the message was sent
        :param username: The username to search for
        """
        await self.warzone_lookup(ctx, "steam", "stats", username)
    
    @warzone_stats.command(
        name="battle",
        description="Retrieves game stats for a user that plays Warzone on Battle.net",
        cog_name="stats"
    )
    async def warzone_stats_battle(self, ctx, *, username=None):
        """Gives the user game stats on a specified player that plays Warzone
        on PC (battle)

        :param ctx: The context of where the message was sent
        :param username: The username to search for
        """
        await self.warzone_lookup(ctx, "battle", "stats", username)
    
    @warzone_stats.command(
        name="xbox", aliases=["xbl"],
        description="Retrieves game stats for a user that plays Warzone on Xbox",
        cog_name="stats"
    )
    async def warzone_xbox(self, ctx, *, username=None):
        """Gives the user game stats on a specified player that plays Warzone
        on Xbox (xbl)

        :param ctx: The context of where the message was sent
        :param username: The username to search for
        """
        await self.warzone_lookup(ctx, "xbl", "stats", username)
    
    @warzone_stats.command(
        name="playstation", aliases=["psn", "ps"],
        description="Retrieves game stats for a user that plays Warzone on Playstation",
        cog_name="stats"
    )
    async def warzone_playstation(self, ctx, *, username=None):
        """Gives the user game stats on a specified player that plays Warzone
        on Playstation (psn)

        :param ctx: The context of where the message was sent
        :param username: The username to search for
        """
        await self.warzone_lookup(ctx, "psn", "stats", username)
    
    @warzone_matches.command(
        name="steam",
        description="Retrieves the 10 most recent matches for a user that plays Warzone on Steam",
        cog_name="stats"
    )
    async def warzone_matches_steam(self, ctx, *, username=None):
        """Gives the 10 most recent matches for a specified player that plays Warzone
        on Steam (steam)

        :param ctx: The context of where the message was sent
        :param username: The username to search for
        """
        await self.warzone_lookup(ctx, "steam", "matches", username)
    
    @warzone_matches.command(
        name="battle",
        description="Retrieves the 10 most recent matches for a user that plays Warzone on Battle.net",
        cog_name="stats"
    )
    async def warzone_matches_battle(self, ctx, *, username=None):
        """Gives the 10 most recent matches for a specified player that plays Warzone
        on Battle.net (battle)

        :param ctx: The context of where the message was sent
        :param username: The username to search for
        """
        await self.warzone_lookup(ctx, "battle", "matches", username)
    
    @warzone_matches.command(
        name="xbox", aliases=["xbl"],
        description="Retrieves the 10 most recent matches for a user that plays Warzone on Xbox",
        cog_name="stats"
    )
    async def warzone_matches_xbox(self, ctx, *, username=None):
        """Gives the 10 most recent matches for a specified player that plays Warzone
        on Xbox (xbl)

        :param ctx: The context of where the message was sent
        :param username: The username to search for
        """
        await self.warzone_lookup(ctx, "xbl", "matches", username)
    
    @warzone_matches.command(
        name="playstation", aliases=["psn", "ps"],
        description="Retrieves the 10 most recent matches for a user that plays Warzone on Playstation",
        cog_name="stats"
    )
    async def warzone_matches_playstation(self, ctx, *, username=None):
        """Gives the 10 most recent matches for a specified player that plays Warzone
        on Playstation (psn)

        :param ctx: The context of where the message was sent
        :param username: The username to search for
        """
        await self.warzone_lookup(ctx, "psn", "matches", username)
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @group(
        name="division2",
        description="Retrieves game stats for a user that plays Tom Clancy's The Division 2",
        cog_name="stats"
    )
    async def division_2(self, ctx):
        """The parent command for The Division 2 platform commands"""
        if not ctx.invoked_subcommand:
            await ctx.send(embed = get_error_message(
                "Try running `{}help division2` :)".format(
                    await database.guilds.get_prefix(ctx.guild) 
                    if ctx.guild is not None else ""
                )
            ))

    @division_2.command(
        name="uplay",
        description="Retrieves game stats for a user that plays The Division 2 on Uplay",
        cog_name="stats"
    )
    async def division_2_uplay(self, ctx, *, username=None):
        """Gives the user game stats on a specified player that plays The Division 2
        on PC (uplay)

        :param ctx: The context of where the message was sent
        :param username: The username to search for
        """
        await self.division_2_lookup(ctx, "uplay", username)
    
    @division_2.command(
        name="xbox", aliases=["xbl"],
        description="Retrieves game stats for a user that plays The Division 2 on Xbox",
        cog_name="stats"
    )
    async def division_2_xbl(self, ctx, *, username=None):
        """Gives the user game stats on a specified player that plays The Division 2
        on Xbox (xbl)

        :param ctx: The context of where the message was sent
        :param username: The username to search for
        """
        await self.division_2_lookup(ctx, "xbl", username)
    
    @division_2.command(
        name="playstation", aliases=["psn", "ps"],
        description="Retrieves game stats for a user that plays The Division 2 on Playstation",
        cog_name="stats"
    )
    async def division_2_psn(self, ctx, *, username=None):
        """Gives the user game stats on a specified player that plays The Division 2
        on Playstation (psn)

        :param ctx: The context of where the message was sent
        :param username: The username to search for
        """
        await self.division_2_lookup(ctx, "psn", username)
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    # # # # # # # # # # # # # # # # # # # # # # # # #

    async def division_2_lookup(self, ctx, platform, username):
        """Gives the user game stats on a specified player that plays Division 2
        on a specified platform

        :param ctx: The context of where the message was sent
        :param platform: The platform to search for the user on
        :param username: The user to search for
        """

        # Call the API if the username is given
        if username is not None:
            result = await loop.run_in_executor(
                None,
                partial(
                    get, DIVISION_2_URL.format(
                        platform, username
                    ),
                    headers = {
                        "TRN-Api-Key": environ["TRACKER_GG_TOKEN"]
                    }
                )
            )
            result = result.json()

            # Check if no data was found
            if "errors" in result:
                await ctx.send(embed = get_error_message(
                    "There was no one found with that username :("
                ))
            
            # There was data found, put it into an embed and 
            #   give it to the user
            else:
                result = result["data"]
                platform = result["platformInfo"]
                stats = result["segments"][0]["stats"]

                # Create an embed
                embed = Embed(
                    title = platform["platformUserHandle"],
                    description = (
                        """
                        **Gear Score**: `{}`
                        **Level**: `{}`
                        """
                    ).format(
                        stats["latestGearScore"]["displayValue"],
                        stats["highestPlayerLevel"]["displayValue"]
                    ),
                    colour = await get_embed_color(ctx.author)
                ).set_footer(
                    text = "Retrieved through Tracker.gg"
                ).set_thumbnail(
                    url = platform["avatarUrl"]
                )

                # Create fields for the data
                fields = {
                    f"Lifetime Basic Stats ({stats['timePlayed']['displayValue']})": (
                        """
                        *Items Looted: `{}`*
                        *E-Credit Balance: `{}`*
                        *Commendations: `{}`*
                        *Curr Comm. Score: `{}`*
                        """
                    ).format(
                        stats["itemsLooted"]["displayValue"],
                        stats["eCreditBalance"]["displayValue"],
                        stats["commendationCount"]["displayValue"],
                        stats["commendationScore"]["displayValue"]
                    ),
                    "Lifetime Kill Stats": (
                        """
                        *PvP Kills: `{}`*
                        *NPC Kills: `{}`*
                        *Skill Kills: `{}`*
                        *Headshots: `{}`*
                        *Sharpshooter: `{}`*
                        *Survivalist: `{}`*
                        *Demolitionist: `{}`*
                        """
                    ).format(
                        stats["killsPvP"]["displayValue"],
                        stats["killsNpc"]["displayValue"],
                        stats["killsSkill"]["displayValue"],
                        stats["headshots"]["displayValue"],
                        stats["killsSpecializationSharpshooter"]["displayValue"],
                        stats["killsSpecializationSurvivalist"]["displayValue"],
                        stats["killsSpecializationDemolitionist"]["displayValue"]
                    ),
                    f"PvE ({stats['timePlayedPve']['displayValue']})": (
                        """
                        *PvE XP: `{}`*
                        *Elite Kills: `{}`*
                        *Named Kills: `{}`*
                        *Hyena Kills: `{}`*
                        *OutCasts Kills: `{}`*
                        *TrueSons Kills: `{}`*
                        *BlackTusk Kills: `{}`*
                        """
                    ).format(
                        stats["xPPve"]["displayValue"],
                        stats["killsRoleElite"]["displayValue"],
                        stats["killsRoleNamed"]["displayValue"],
                        stats["killsFactionBlackbloc"]["displayValue"],
                        stats["killsFactionCultists"]["displayValue"],
                        stats["killsFactionMilitia"]["displayValue"],
                        stats["killsFactionEndgame"]["displayValue"]
                    ),
                    f"Dark Zone Basic Stats ({stats['timePlayedDarkZone']['displayValue']})": (
                        """
                        *DZ Level: `{}`*
                        *DZ XP: `{}`*
                        *Rogues Killed: `{}`*
                        *Rogue Time Played: `{}`*
                        *Rogue Longest Time Played: `{}`*
                        """
                    ).format(
                        stats["rankDZ"]["displayValue"],
                        stats["xPDZ"]["displayValue"],
                        stats["roguesKilled"]["displayValue"],
                        stats["timePlayedRogue"]["displayValue"],
                        stats["timePlayedRogueLongest"]["displayValue"]
                    ),
                    "Dark Zone Kill Stats": (
                        """
                        *Hyena Kills: `{}`*
                        *OutCasts Kills: `{}`*
                        *TrueSons Kills: `{}`*
                        *BlackTusk Kills: `{}`*
                        *Elite Kills: `{}`*
                        *Named Kills: `{}`*
                        """
                    ).format(
                        stats["killsFactionDzBlackbloc"]["displayValue"],
                        stats["killsFactionDzCultists"]["displayValue"],
                        stats["killsFactionDzMilitia"]["displayValue"],
                        stats["killsFactionDzEndgame"]["displayValue"],
                        stats["killsRoleDzElite"]["displayValue"],
                        stats["killsRoleDzNamed"]["displayValue"]
                    )
                }

                for field in fields:
                    embed.add_field(
                        name = field,
                        value = fields[field]
                    )
                
                await ctx.send(embed = embed)
        
        else:
            await ctx.send(embed = get_error_message(
                "You must specify the username to search for!"
            ))
    
    async def modern_warfare_lookup(self, ctx, platform, mode, username):
        """Gives the user game stats on a specified player that plays Modern Warfare
        on a specified platform

        :param ctx: The context of where the message was sent
        :param platform: The platform to search for the user on
        :param mode: The mode of Modern Warfare to look up (Either stats or matches)
        :param username: The user to search for
        """

        # Check if the username was given
        if username is not None:
            
            # Get the multiplayer stats or the most recent 5 matches
            if mode == "stats":
                multi_stats = await loop.run_in_executor(
                    None,
                    partial(
                        get, MW_MULTI_STATS_URL.format(quote(username), platform),
                        headers = {
                            "x-rapidapi-key": environ["RAPID_API_KEY"]
                        }
                    )
                )
                multi_stats = multi_stats.json()

                # Check if the player is not found
                if "error" in multi_stats:
                    await ctx.send(embed = get_error_message(
                        "No one was found with that username :("
                    ))
                    return None
                else:
                    stat = multi_stats["lifetime"]["all"]["properties"]

                    # Create the base embed
                    embed = Embed(
                        title = multi_stats["username"],
                        description = (
                            """
                            *Time Played*: {}
                            *Matches Played*: {}
                            *Level*: {}
                            """
                        ).format(
                            seconds_to_runtime(stat["timePlayedTotal"]),
                            f"{stat['totalGamesPlayed']:,}",
                            multi_stats["level"]
                        ),
                        colour = await get_embed_color(ctx.author)
                    )

                    # Create the fields and add them to the embed
                    fields = {
                        "K/D Ratio": f"{stat['kdRatio']:.2f}",
                        "Kills": f"{stat['kills']:,}",
                        "Win %": f"{stat['winLossRatio']:.2f}",
                        "Wins": f"{stat['wins']:,}",

                        "Best Killstreak": stat["recordKillStreak"],
                        "Current Win Streak": stat["recordLongestWinStreak"],
                        "Losses": f"{stat['losses']:,}",
                        "Ties": stat["ties"],
                        "Assists": f"{stat['assists']:,}",
                        "Deaths": f"{stat['deaths']:,}",
                        "Score/min": f"{stat['scorePerMinute']:,.2f}",
                        "Score/game": f"{stat['scorePerGame']:,.2f}",
                        "Score": f"{stat['score']:,}",

                        "Accuracy": (
                            """
                            *Misses*: {}
                            *Hits*: {}
                            *Headshots*: {}
                            """
                        ).format(
                            f"{stat['totalShots'] - stat['hits'] - stat['headshots']:,}",
                            f"{stat['hits']:,}",
                            f"{stat['headshots']:,}"
                        )

                    }
                    for field in fields:
                        embed.add_field(
                            name = field,
                            value = fields[field]
                        )
                    
                    await ctx.send(embed = embed)
            else:
                multi_match = await loop.run_in_executor(
                    None,
                    partial(
                        get, MW_MULTI_MATCH_URL.format(quote(username), platform),
                        headers = {
                            "x-rapidapi-key": environ["RAPID_API_KEY"]
                        }
                    )
                )
                multi_match = multi_match.json()

                # Check if the player is not found
                if "error" in multi_match:
                    await ctx.send(embed = get_error_message(
                        "No one was found with that username :("
                    ))
                    return None
                else:

                    # Check if there are no results
                    if len(multi_match) == 0:
                        await ctx.send(embed = get_error_message(
                            "This player has no recent matches!"
                        ))
                    else:
                        await process_scrolling(
                            ctx, self.bot,
                            pages = [
                                build_mw_match(match)
                                for match in multi_match["matches"][:10]
                            ]
                        )
        
        # The username was not given
        else:
            await ctx.send(embed = get_error_message(
                "You must specify the username to search for!"
            ))
    
    async def warzone_lookup(self, ctx, platform, mode, username):
        """Gives the user game stats on a specified player that plays Warzone
        on a specified platform

        :param ctx: The context of where the message was sent
        :param platform: The platform to search for the user on
        :param mode: The mode of Warzone to look up (Either stats or matches)
        :param username: The user to search for
        """

        # Check if the username is given
        if username is not None:

            # Get the warzone stats or the most recent 5 matches
            if mode == "stats":
                warzone_stats = await loop.run_in_executor(
                    None,
                    partial(
                        get, MW_WAR_STATS_URL.format(quote(username), platform),
                        headers = {
                            "x-rapidapi-key": environ["RAPID_API_KEY"]
                        }
                    )
                )
                warzone_stats = warzone_stats.json()

                # Check if the player is not found
                if "error" in warzone_stats:
                    await ctx.send(embed = get_error_message(
                        "No one was found with that username :("
                    ))
                    return None
                else:
                    stat = warzone_stats["br_all"]

                    # Create the base embed
                    embed = Embed(
                        title = username,
                        description = (
                            """
                            *Time Played*: {}
                            *Matches Played*: {}
                            """
                        ).format(
                            seconds_to_runtime(stat["timePlayed"]),
                            f"{stat['gamesPlayed']:,}"
                        ),
                        colour = await get_embed_color(ctx.author)
                    )

                    # Create the fields and add them to the embed
                    fields = {
                        "Wins": f"{stat['wins']:,}",
                        "Top 5": f"{stat['topFive']:,}",
                        "K/D Ratio": f"{stat['kdRatio']:,.2f}",

                        "Top 10": f"{stat['topTen']:,}",
                        "Top 25": f"{stat['topTwentyFive']:,}",
                        "Win %": f"{100 * stat['wins'] / stat['gamesPlayed']:.2f}",

                        "Kills": f"{stat['kills']:,}",
                        "Deaths": f"{stat['deaths']:,}",
                        "Downs": f"{stat['downs']:,}",

                        "Score": f"{stat['score']:,}",
                        "Score/min": f"{stat['scorePerMinute']:,.2f}",
                        "Score/game": f"{stat['score'] / stat['gamesPlayed']:,.2f}"
                    }
                    for field in fields:
                        embed.add_field(
                            name = field,
                            value = fields[field]
                        )
                    await ctx.send(embed = embed)
            else:
                warzone_match = await loop.run_in_executor(
                    None,
                    partial(
                        get, MW_WAR_MATCH_URL.format(quote(username), platform),
                        headers = {
                            "x-rapidapi-key": environ["RAPID_API_KEY"]
                        }
                    )
                )
                warzone_match = warzone_match.json()
            
                # Check if the player is not found
                if "error" in warzone_match:
                    await ctx.send(embed = get_error_message(
                        "No one was found with that username :("
                    ))
                    return None
                else:
                    await process_scrolling(
                        ctx, self.bot,
                        pages = [
                            build_wz_match(match)
                            for match in warzone_match["matches"]
                        ]
                    )
        
        # The username was not given
        else:
            await ctx.send(embed = get_error_message(
                "You must specify the username to search for!"
            ))

def setup(bot):
    bot.add_cog(Stats(bot))