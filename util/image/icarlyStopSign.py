from util.image.image import renderLines

from util.utils import loadImageFromUrl, splitText

import pygame

pygame.init()

IMAGE = "https://i.imgur.com/MSaTVD2.jpg"

# Text Angles, Colors, and Default Sizes
SPENCER_LOCATION = [135, 250]
SPENCER_ANGLE = 0
SPENCER_COLOR = [255, 255, 255]
SPENCER_SIZE = 30
SPENCER_MAX = 15
SPENCER_FONT = pygame.font.SysFont("arial", SPENCER_SIZE)

STOP_LOCATION = [115, 80]
STOP_ANGLE = 37
STOP_COLOR = [0, 0, 0]
STOP_SIZE = 25
STOP_MAX = 15
STOP_FONT = pygame.font.SysFont("arial", STOP_SIZE)

GIBBY_LOCATION = [260, 155]
GIBBY_ANGLE = 0
GIBBY_COLOR = [255, 255, 255]
GIBBY_SIZE = 30
GIBBY_MAX = 10
GIBBY_FONT = pygame.font.SysFont("arial", GIBBY_SIZE)

def generateImage(spencerText, stopText, gibbyText):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Load Image
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    # Make Request; Get Image through Pillow
    pygameImage = loadImageFromUrl(IMAGE)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Add Text
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # # Card Text
    # First split up text, by word, not exceeding SPENCER_MAX
    lines = splitText(spencerText, SPENCER_MAX)
    pygameImage = renderLines(pygameImage, SPENCER_LOCATION, lines, SPENCER_FONT, SPENCER_COLOR, angle = SPENCER_ANGLE)
    
    # # Body Text
    # First split up text, by word, not exceeding STOP_MAX
    lines = splitText(stopText, STOP_MAX)
    pygameImage = renderLines(pygameImage, STOP_LOCATION, lines, STOP_FONT, STOP_COLOR, angle = STOP_ANGLE)

    # # Table Text
    # First split up text, by word, not exceeding GIBBY_MAX
    lines = splitText(gibbyText, GIBBY_MAX)
    pygameImage = renderLines(pygameImage, GIBBY_LOCATION, lines, GIBBY_FONT, GIBBY_COLOR, angle = GIBBY_ANGLE)

    # Temporarily save image under util/image
    image = "util/image/ICARLY_STOP_SIGN_{}.png".format(spencerText)
    pygame.image.save(pygameImage, image)

    return image

