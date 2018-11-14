from util.utils import loadImageFromUrl, splitText

import pygame
pygame.init()

def renderLines(source, origin, lines, font, color, *, angle = 0, centered = [True, True]):
    """Renders lines on a pygame surface.

    Parameters:
        source (pygame.image): The source to add to.
        origin (list): The x,y coordinates of the origin of the lines.
        lines (list): The lines to add.
        font (pygame.font): The font to use to render.
        color (list): The color of the text.
        angle (int): The angle to set for the text.
    """

    # Get largestWidth and height of surface
    width = 0
    height = 0
    for line in range(len(lines)):
        if font.size(lines[line])[0] + 5 > width:
            width = font.size(lines[line])[0] + 5
        height += font.size(lines[line])[1] + 5

    # Create temporary surface for text that can be rotated
    tempSurf = pygame.Surface((width, height), pygame.SRCALPHA, 32)
    tempSurf.set_alpha(255)

    for line in range(len(lines)):
        cardText = font.render(lines[line], True, color)
        tempSurf.blit(
            cardText,
            [
                0,
                line * (font.get_height() + 2)
            ]
        )
    
    # Add temporary surface at an angle
    tempSurf = pygame.transform.rotate(tempSurf, angle)
    source.blit(tempSurf, (
        origin[0] - ((tempSurf.get_width() / 2) if centered[0] else 0),
        origin[1] - ((tempSurf.get_height() / 2) if centered[1] else 0)
    ))
    return source

class MemeTemplate:
    """Creates a MemeTemplate object.

        Any text that is given a name must have a coinciding text attribute.
        
        Example:
            line1 = \"Hello World\"
            line1 = {
                # Attribute tags
            }
        
        The textAttributes must have the following tags:
            \"location\" (list - containing x and y coordinates)
            \"angle\" (int - angle to rotate the text at)
            \"color\" (list - containing red, green, and blue values)
            \"size\" (int - font size of the text)
            \"max\" (int - maximum size of a line of text in the field)
            \"centered\" (list - containing an x-centered and y-centered variable)

        Parameters:
            templateName (str): The name of the template
            imageUrl (str): The URL of the image to load.
            textAttributes (dict): The attributes that specific text follows.
            generateImageFunction (func): A custom function that generates an image. (Defaults to None)
        """

    def __init__(self, templateName, imageUrl, textAttributes, generateImageFunction = None):
        """Creates a MemeTemplate object.

        Any text that is given a name must have a coinciding text attribute.
        
        Example:
            line1 = \"Hello World\"
            line1 = {
                # Attribute tags
            }
        
        The textAttributes must have the following tags:
            \"location\" (list - containing x and y coordinates)
            \"angle\" (int - angle to rotate the text at) (Defaults to 0)
            \"color\" (list - containing red, green, and blue values) (Defaults to Black)
            \"size\" (int - font size of the text)
            \"font\" (pygame.font.SysFont - the font to use for the text) (Defaults to regular type)
            \"max\" (int - maximum size of a line of text in the field) (Defaults to 10)
            \"centered\" (list - containing an x-centered and y-centered variable) (Defaults to True for both).

        Parameters:
            templateName (str): The name of the template
            imageUrl (str): The URL of the image to load.
            textAttributes (dict): The attributes that specific text follows.
            generateImageFunction (func): A custom function that generates an image. (Defaults to None)
        """

        self._template_name = templateName
        self._image_url = imageUrl
        self._generate_image_function = generateImageFunction

        self._text_attributes = textAttributes
        for textType in self._text_attributes:
            if "angle" not in self._text_attributes[textType]:
                self._text_attributes[textType]["angle"] = 0
            if "color" not in self._text_attributes[textType]:
                self._text_attributes[textType]["color"] = [0, 0, 0]
            if "font" not in self._text_attributes[textType]:
                self._text_attributes[textType]["font"] = pygame.font.SysFont("arial", self._text_attributes[textType]["size"])
            if "max" not in self._text_attributes[textType]:
                self._text_attributes[textType]["max"] = 10
            if "centered" not in self._text_attributes[textType]:
                self._text_attributes[textType]["centered"] = [True, True]
    
    def generateImage(self, **kwargs):
        """Generates and returns the file location of a meme based off of the url and attributes given.

        Parameters:
            kwargs (dict): The text to set that must match the text attributes.
        """

        # Run custom function
        if self._generate_image_function != None:
            return self._generate_image_function(kwargs)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Load Image
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        
        # Make Request; Get Image through Pillow
        pygameImage = loadImageFromUrl(self._image_url)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Add Text
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        fileName = ""
        count = 0
        for textType in self._text_attributes:
            if count == 0:
                fileName = kwargs[textType]

            # Split up text, by word, not exceeding max
            lines = splitText(kwargs[textType], self._text_attributes[textType]["max"])

            # Add lines to pygameImage
            pygameImage = renderLines(pygameImage, 
                self._text_attributes[textType]["location"], lines, 
                self._text_attributes[textType]["font"], self._text_attributes[textType]["color"], 
                angle = self._text_attributes[textType]["angle"], centered = self._text_attributes[textType]["centered"]
            )

            count += 1

        # Temporarily save image under util/image
        image = "util/image/{}_{}.png".format(
            self._template_name.upper().replace(" ", "_"),
            fileName.upper().replace(" ", "_")
        )
        pygame.image.save(pygameImage, image)
        return image