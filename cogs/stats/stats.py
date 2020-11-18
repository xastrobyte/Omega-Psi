from discord import Embed
from discord.ext.commands import Cog, group
from functools import partial
from requests import get
from os import environ

from cogs.globals import loop
from cogs.errors import get_error_message, UNIMPLEMENTED_ERROR

from util.functions import get_embed_color
from util.database.database import database

# # # # # # # # # # # # # # # # # # # # # # # # #

DIVISION_2_URL = "https://public-api.tracker.gg/v2/division-2/standard/profile/{}/{}"

# # # # # # # # # # # # # # # # # # # # # # # # #

class Stats(Cog, name="stats"):
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @group(
        name="apex",
        description="Retrieves game stats for a user that plays Apex Legends",
        cog_name="stats"
    )
    async def apex(self, ctx):
        await ctx.send(embed = UNIMPLEMENTED_ERROR)

    @group(
        name="division2",
        description="Retrieves game stats for a user that plays Tom Clancy's The Division 2",
        cog_name="stats"
    )
    async def division_2(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send(embed = get_error_message(
                "Try running `{}help division2` :)".format(
                    await database.guilds.get_prefix(ctx.guild)
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
        description="Retrieves game stats for a user that plays The Division 2 on Uplay",
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
        description="Retrieves game stats for a user that plays The Division 2 on Uplay",
        cog_name="stats"
    )
    async def division_2_psn(self, ctx, *, username=None):
        """Gives the user game stats on a specified player that plays The Division 2
        on Playstation (psn)

        :param ctx: The context of where the message was sent
        :param username: The username to search for
        """
        await self.division_2_lookup(ctx, "psn", username)
    
    @group(
        name="csGo",
        description="Retrieves game stats for a user that plays Counter Strike: Global Offensive (CSGO)",
        cog_name="stats"
    )
    async def csgo(self, ctx):
        await ctx.send(embed = UNIMPLEMENTED_ERROR)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    async def division_2_lookup(self, ctx, platform, username):

        # Call the API
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

def setup(bot):
    bot.add_cog(Stats(bot))