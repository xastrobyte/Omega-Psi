import discord

def get_error_message(message):

    return discord.Embed(
        title = "Error",
        description = message,
        colour = 0xFF8000
    )