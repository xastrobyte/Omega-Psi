from util.image.image import renderLines

from util.utils import loadImageFromUrl, splitText

import pygame

pygame.init()

# IMAGE = "https://preview.redd.it/erpvm5m39gw11.jpg?width=640&crop=smart&auto=webp&s=5f06e60d8ce81befbc5d9005772f82e19d0514b1"
IMAGE = "https://tinyurl.com/surprisedDwight"

# Text Angles, Colors, and Default Sizes
DWIGHT_LOCATION = [220, 300]
DWIGHT_ANGLE = 0
DWIGHT_COLOR = [255, 255, 255]
DWIGHT_SIZE = 60
DWIGHT_MAX = 15
DWIGHT_FONT = pygame.font.SysFont("arial", DWIGHT_SIZE)

ANGELA_LOCATION = [485, 300]
ANGELA_ANGLE = 0
ANGELA_COLOR = [255, 255, 255]
ANGELA_SIZE = 60
ANGELA_MAX = 10
ANGELA_FONT = pygame.font.SysFont("arial", ANGELA_SIZE)

def generateImage(dwightText, angelaText):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Load Image
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    # Make Request; Get Image through Pillow
    pygameImage = loadImageFromUrl(IMAGE)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Add Text
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # # Dwight Text
    # First split up text, by word, not exceeding DWIGHT_MAX
    lines = splitText(dwightText, DWIGHT_MAX)
    pygameImage = renderLines(pygameImage, DWIGHT_LOCATION, lines, DWIGHT_FONT, DWIGHT_COLOR, angle = DWIGHT_ANGLE)

    # # Angela Text
    # First split up text, by word, not exceeding ANGELA_MAX
    lines = splitText(angelaText, ANGELA_MAX)
    pygameImage = renderLines(pygameImage, ANGELA_LOCATION, lines, ANGELA_FONT, ANGELA_COLOR, angle = ANGELA_ANGLE)

    # Temporarily save image under util/image
    image = "util/image/SURPRISED_DWIGHT_{}.png".format(dwightText)
    pygame.image.save(pygameImage, image)

    return image

