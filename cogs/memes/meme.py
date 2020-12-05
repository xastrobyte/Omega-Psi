from discord import File
from PIL import Image, ImageDraw, ImageFont
from requests import get
from io import BytesIO
from math import sqrt

# # # # # # # # # # # # # # #

roboto = "cogs/memes/roboto.ttf"

# # # # # # # # # # # # # # #


class TextLocation:
    """The TextLocation class is what will hold the x,y coordinate of the 
    text on a meme along with whether or not it will be centered.

    :param x: The x-coord of the text on a meme
    :param y: The y-coord of the text on a meme
    :param fill: The fill color of the text
    :param stroke: The color of the stroke around the text
    :param stroke_width: The width of the stroke around the text
    :param center_x: Whether or not the text is centered on the meme horizontally
    :param center_y: Whether or not the text is centered on the meme vertically
    """
    def __init__(self, x, y, fill, *, stroke=None, stroke_width=1, center_x=False, center_y=False):
        self.__x = x
        self.__y = y
        self.__fill = fill
        
        self.__stroke = stroke
        self.__stroke_width = stroke_width
        self.__center_x = center_x
        self.__center_y = center_y
    
    # # # # # # # # # # # # # # #

    @property
    def x(self):
        return self.__x
    
    @property
    def y(self):
        return self.__y
    
    @property
    def fill(self):
        return self.__fill
    
    @property
    def stroke(self):
        return self.__stroke
    
    @property
    def stroke_width(self):
        return self.__stroke_width
    
    @property
    def center_x(self):
        return self.__center_x
    
    @property
    def center_y(self):
        return self.__center_y
    
    # # # # # # # # # # # # # # #

    def is_centered(self) -> bool:
        """Returns whether or not the text will be centered"""
        return self.__center_x and self.__center_y
    
# # # # # # # # # # # # # # #

class Meme:
    """A Meme class is what is used to hold the base image of a meme
    and then the locations of text in pixels.

    :param base_image: The base image of the Meme to generate
    :param font_size: The size of the font to use to keep the meme lightweight of text
    :param text_locations: A dictionary of text location objects to use to place
        text on a meme
    """
    def __init__(self, id, base_image, font_size, **text_locations):
        self.__id = id
        self.__base_image = base_image
        self.__text_locations = text_locations

        self.__font = ImageFont.truetype(roboto, font_size)
    
    # # # # # # # # # # # # # # #

    @property
    def id(self):
        return self.__id

    @property
    def base_image(self):
        return self.__base_image
    
    @property
    def font(self):
        return self.__font
    
    @property
    def text_locations(self):
        return self.__text_locations
    
    # # # # # # # # # # # # # # #

    def generate(self, user_id, **text):
        """Generates this meme with each string of text
        associated with the text_id used in text_locations

        :param text: A dict of text_ids mapped to strings of text to
            put onto the meme
        """

        # Get the image from imgur
        response = get(self.base_image)
        image = Image.open(BytesIO(response.content))

        for key in text:

            # Skip the piece of text if there is no length to it
            if len(text[key]) > 0:
                # Check if the text will be centered or not
                words = text[key].split()
                phrases = []
                if self.text_locations[key].is_centered():

                    # Center each text as much as possible if the text is bigger than
                    #   a certain amount
                    # get this amount by getting the square root of how many words there are
                    #   and creating phrases from that
                    #   the x_offset becomes - (15 * max_width)
                    #   the y_offset becomes - (15 * len(phrases))
                    max_width = sqrt(len(words)) // 1
                    for i in range(len(words)):
                        if i % max_width == 0:
                            if i != 0:
                                phrases[-1] = " ".join(phrases[-1])
                            phrases.append([words[i]])
                        else:
                            phrases[-1].append(words[i])
                    if len(phrases) > 0:
                        if isinstance(phrases[-1], list):
                            phrases[-1] = " ".join(phrases[-1])
                
                # If the text is not being centered, split the text whenever the rendered text
                #   exceeds the width of the image
                else:
                    max_width = image.width - 10
                    last = 0
                    for i in range(len(words)):
                        if self.font.getsize(" ".join(words[last:i + 1]))[0] >= max_width:
                            phrases.append(" ".join(words[last:i]))
                            last = i
                    if i < len(words):
                        phrases.append(" ".join(words[last:]))
                
                phrases = "\n".join(phrases)
                
                # Add each phrase into the image with a thin stroke to make it easier to read
                #   on colorfully complex images
                x_offset = y_offset = 0
                target_function = ImageDraw.Draw(image).text
                if self.text_locations[key].is_centered():
                    x_offset, y_offset = self.font.getsize_multiline(phrases)
                    x_offset //= 2
                    y_offset //= 2
                    target_function = ImageDraw.Draw(image).multiline_text
                elif self.text_locations[key].center_x:
                    x_offset = self.font.getsize(phrases)[0] // 2
                elif self.text_locations[key].center_y:
                    y_offset = self.font.getsize(phrases)[1] // 2
                
                target_function(
                    (
                        self.text_locations[key].x - x_offset,
                        self.text_locations[key].y - y_offset
                    ), phrases, 
                    self.text_locations[key].fill,
                    font = self.font,
                    stroke_width = self.text_locations[key].stroke_width,
                    stroke_fill = self.text_locations[key].stroke
                )
        
        # Save the resulting image into a BytesIO object so we don't have to save
        #   the file onto the system itself
        arr = BytesIO()
        image.save(arr, format="PNG")
        arr.seek(0)  # Do this because Pillow sets the pointer
                        # to the very end of the file instead of the beginning
        return File(arr, filename=f"{user_id}-{self.id}.png")
        