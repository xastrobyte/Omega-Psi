import asyncio, dbl, discord, os

class DiscordBotsOrgAPI:
    """Handles interactions with the discordbots.org API"""

    def __init__(self, client):
        self.client = client
        self._token = os.environ["DISCORD_BOT_ORG_TOKEN"]
        self._dblpy = dbl.Client(self.client, self._token)
        self.client.loop.create_task(self.update_stats())

    async def update_stats(self):
        """This function runs every 30 minutes to automatically update your server count"""

        while True:
            try:
                await self._dblpy.post_server_count()
                app = await self.client.application_info()
                await app.owner.send(
                    embed = discord.Embed(
                        title = "Posted Server Count To DBL",
                        description = " ",
                        colour = 0x00FF00,
                        url = "https://discordbots.org/bot/503804826187071501"
                    )
                )
            except Exception as e:
                app = await self.client.application_info()
                await app.owner.send(
                    embed = discord.Embed(
                        title = "Could Not Post Server Count To DBL",
                        description = str(e),
                        colour = 0xFF0000,
                        url = "https://discordbots.org/bot/503804826187071501"
                    )
                )
            await asyncio.sleep(1800)

def setup(client):
    client.add_cog(DiscordBotsOrgAPI(client))