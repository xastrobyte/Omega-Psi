class TextLocation:
    """The TextLocation class is what will hold the x,y coordinate of the 
    text on a meme along with whether or not it will be centered.

    :param x: The x-coord of the text on a meme
    :param y: The y-coord of the text on a meme
    :param centered: Whether or not the text is centered on the meme
    """
    def __init__(self, x, y, centered=False):
        self.__x = x
        self.__y = y
        self.__centered = centered
    
    # # # # # # # # # # # # # # #

    @property
    def x(self):
        return self.__x
    
    @property
    def y(self):
        return self.__y
    
    # # # # # # # # # # # # # # #

    def is_centered(self) -> bool:
        """Returns whether or not the text will be centered"""
        return self.__centered
    
# # # # # # # # # # # # # # #

class Meme:
    """A Meme class is what is used to hold the base image of a meme
    and then the locations of text in pixels.

    :param base_image: The base image of the Meme to generate
    :param text_locations: A dictionary of text location objects to use to place
        text on a meme
    """
    def __init__(self, base_image, **text_locations):
        self.__base_image = base_image
        self.__text_locations = text_locations
    
    # # # # # # # # # # # # # # #

    @property
    def base_image(self):
        return self.__base_image
    
    @property
    def text_locations(self):
        return self.__text_locations
    
    # # # # # # # # # # # # # # #

    def generate(self, **text):
        """Generates this meme with each string of text
        associated with the text_id used in text_locations

        :param text: A dict of text_ids mapped to strings of text to
            put onto the meme
        """
        pass