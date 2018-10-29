import discord

def getNoGame(game, colour, icon):
    """Returns the embed used when there is no game being played.\n

    game - The game that the embed originates from.\n
    colour - The colour to set the embed to.\n
    icon - The icon to set to the embed.\n
    """

    return discord.Embed(
        title = "No Game",
        description = "You were not playing a `{}` game".format(game),
        colour = colour
    ).set_thumbnail(
        url = icon
    )

def getQuitGame(game, colour, icon):
    """Returns the embed used when someone is quitting a game.\n

    game - The game that the embed originates from.\n
    colour - The colour to set the embed to.\n
    icon - The icon to set to the embed.\n
    """
    
    return discord.Embed(
        title = "Quit Game",
        description = "Your {} game was successfully ended.".format(game),
        colour = colour
    ).set_thumbnail(
        url = icon
    )
