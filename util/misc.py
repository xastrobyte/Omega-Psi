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

def set_default(default_dict, result_dict):
    """Sets default values for a dictionary recursively.
    """

    # Iterate through default values
    for tag in default_dict:

        # If the tag does not exist in the result dictionary, add it
        if tag not in result_dict:
            result_dict[tag] = default_dict[tag]
        
        # Tag exists in guild dict, see if tag is a dictionary
        else:
            if type(result_dict[tag]) == dict:
                result_dict[tag] = set_default(default_dict[tag], result_dict[tag])
    
    return result_dict