from discord import Embed
from discord.ext.commands import Cog, command, group

# # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # #

class Memes(Cog, name="memes"):
    """Generate memes quickly in this category :)"""
    def __init__(self, bot):
        self.bot = bot
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    

    # # # # # # # # # # # # # # # # # # # # # # # # #

def setup(bot):
    bot.add_cog(Memes(bot))