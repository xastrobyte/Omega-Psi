from util.utils.miscUtils import loadImageFromUrl
from util.utils.stringUtils import splitText

import pygame, random
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
            Note: if you include \"image_size\", it will only affect images.
                    By default, \"image_size\" will be set to the \"size\"
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
            \"angle\" (int - angle to rotate the text at)
            \"color\" (list - containing red, green, and blue values)
            \"size\" (int - font size of the text)
                Note: if you include \"image_size\", it will only affect images.
                      By default, \"image_size\" will be set to the 150% of the \"size\"
            \"max\" (int - maximum size of a line of text in the field)
            \"centered\" (list - containing an x-centered and y-centered variable)

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
                self._text_attributes[textType]["font"] = pygame.font.SysFont("/util/image/Light.ttf", self._text_attributes[textType]["size"])
            if "max" not in self._text_attributes[textType]:
                self._text_attributes[textType]["max"] = 10
            if "centered" not in self._text_attributes[textType]:
                self._text_attributes[textType]["centered"] = [True, True]
            if "size" not in self._text_attributes[textType]:
                self._text_attributes[textType]["size"] = 50
            if "image_size" not in self._text_attributes[textType]:
                self._text_attributes[textType]["image_size"] = int(self._text_attributes[textType]["size"] * 3)
    
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
        # Add Text / Images
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        fileName = random.randint(1, 100000)
        for textType in self._text_attributes:

            # Check if text is a valid URL
            try:

                # Load image and resize
                image = loadImageFromUrl(kwargs[textType])

                # Get ratio of size
                width =  int((image.get_width()  * self._text_attributes[textType]["image_size"]) / image.get_width())
                height = int((image.get_height() * self._text_attributes[textType]["image_size"]) / image.get_width())

                image = pygame.transform.scale(image, (width, height))

                # Add image to centerpoint
                x, y = self._text_attributes[textType]["location"]
                pygameImage.blit(image,
                    (
                        (x - (width / 2)) if self._text_attributes[textType]["centered"][0] else x,
                        (y - (height / 2)) if self._text_attributes[textType]["centered"][1] else y
                    )
                )
            
            # Text is not a URL; Add regularly. If it fails, it's up to the user anyways
            except:

                # Split up text, by word, not exceeding max
                lines = splitText(kwargs[textType], self._text_attributes[textType]["max"])

                # Add lines to pygameImage
                pygameImage = renderLines(pygameImage, 
                    self._text_attributes[textType]["location"], lines, 
                    self._text_attributes[textType]["font"], self._text_attributes[textType]["color"], 
                    angle = self._text_attributes[textType]["angle"], centered = self._text_attributes[textType]["centered"]
                )

        # Temporarily save image under util/image
        image = "util/image/{}_{}.png".format(
            self._template_name.upper().replace(" ", "_"),
            fileName
        )
        pygame.image.save(pygameImage, image)
        return image