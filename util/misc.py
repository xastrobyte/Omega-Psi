from datetime import datetime
from random import randint

def get_theme():
    """Returns a random list of dark, medium, light theme colors depending on the day
    """

    # Get the current date
    current = datetime.now()

    # Keep track of the offsets for the dark, medium, and light colors
    shades = [0, 96, 192]

    # Iterate through the shades
    for index in range(len(shades)):

        # Remember the offset
        offset = shades[index]

        # Get the red, green, and blue values
        red = randint(0, current.month * 256) % 64
        green = randint(0, current.day * 16) % 64
        blue = randint(0, current.year) % 64

        # Replace the index in the shades
        shades[index] = "{}{}{}".format(
            hex(red + offset)[2:].rjust(2, "0"), 
            hex(green + offset)[2:].rjust(2, "0"), 
            hex(blue + offset)[2:].rjust(2, "0")
        )

    return shades