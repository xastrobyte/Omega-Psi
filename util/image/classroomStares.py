from util.image.image import renderLines

from util.utils import loadImageFromUrl, splitText

import pygame

pygame.init()

IMAGE = "https://i.imgur.com/3QVQ2V5.jpg"

# Text Angles, Colors, and Default Sizes
BUBBLE_LOCATION = [350, 250]
BUBBLE_ANGLE = 10
BUBBLE_COLOR = [255, 255, 255]
BUBBLE_SIZE = 80
BUBBLE_MAX = 10
BUBBLE_FONT = pygame.font.SysFont("arial", BUBBLE_SIZE)

def generateImage(bubbleText):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Load Image
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    # Make Request; Get Image through Pillow
    pygameImage = loadImageFromUrl(IMAGE)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Add Text
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # # Bubble Text
    # First split up text, by word, not exceeding BUBBLE_MAX
    lines = splitText(bubbleText, BUBBLE_MAX)
    pygameImage = renderLines(pygameImage, BUBBLE_LOCATION, lines, BUBBLE_FONT, BUBBLE_COLOR, angle = BUBBLE_ANGLE)

    # Temporarily save image under util/image
    image = "util/image/CLASSROOM_STARES_{}.png".format(bubbleText)
    pygame.image.save(pygameImage, image)

    return image

