from util.image.image import renderLines

from util.utils import loadImageFromUrl, splitText

import pygame

pygame.init()

IMAGE = "https://i.imgur.com/GBMCNYM.jpg"

# Text Angles, Colors, and Default Sizes
CARD_LOCATION = [560, 90]
CARD_ANGLE = 0
CARD_COLOR = [0, 0, 0]
CARD_SIZE = 80
CARD_MAX = 10
CARD_FONT = pygame.font.SysFont("arial", CARD_SIZE)

BODY_LOCATION = [660, 765]
BODY_ANGLE = 0
BODY_COLOR = [255, 255, 255]
BODY_SIZE = 80
BODY_MAX = 15
BODY_FONT = pygame.font.SysFont("arial", BODY_SIZE)

TABLE_LOCATION = [200, 1100]
TABLE_ANGLE = 30
TABLE_COLOR = [0, 0, 0]
TABLE_SIZE = 60
TABLE_MAX = 20
TABLE_FONT = pygame.font.SysFont("arial", TABLE_SIZE)

def generateImage(cardText, bodyText, tableText):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Load Image
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    # Make Request; Get Image through Pillow
    pygameImage = loadImageFromUrl(IMAGE)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Add Text
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # # Card Text
    # First split up text, by word, not exceeding CARD_MAX
    lines = splitText(cardText, CARD_MAX)
    pygameImage = renderLines(pygameImage, CARD_LOCATION, lines, CARD_FONT, CARD_COLOR, angle = CARD_ANGLE, centeredY = False)
    
    # # Body Text
    # First split up text, by word, not exceeding BODY_MAX
    lines = splitText(bodyText, BODY_MAX)
    pygameImage = renderLines(pygameImage, BODY_LOCATION, lines, BODY_FONT, BODY_COLOR, angle = BODY_ANGLE)

    # # Table Text
    # First split up text, by word, not exceeding TABLE_MAX
    lines = splitText(tableText, TABLE_MAX)
    pygameImage = renderLines(pygameImage, TABLE_LOCATION, lines, TABLE_FONT, TABLE_COLOR, angle = TABLE_ANGLE)

    # Temporarily save image under util/image
    image = "util/image/CARD_SLAM_{}.png".format(cardText)
    pygame.image.save(pygameImage, image)

    return image
