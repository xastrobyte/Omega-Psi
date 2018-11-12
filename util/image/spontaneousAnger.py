from util.image.image import renderLines

from util.utils import loadImageFromUrl, splitText

import pygame

pygame.init()

IMAGE = "https://i.imgur.com/o1NzXyW.jpg"

# Text Angles, Colors, and Default Sizes
ANGER_LOCATION = [135, 20]
ANGER_ANGLE = 0
ANGER_COLOR = [0, 0, 0]
ANGER_SIZE = 35
ANGER_MAX = 10
ANGER_FONT = pygame.font.SysFont("arial", ANGER_SIZE)

QUESTION_LOCATION = [385, 20]
QUESTION_ANGLE = 0
QUESTION_COLOR = [0, 0, 0]
QUESTION_SIZE = 35
QUESTION_MAX = 10
QUESTION_FONT = pygame.font.SysFont("arial", QUESTION_SIZE)

def generateImage(angerText, questionText):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Load Image
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    # Make Request; Get Image through Pillow
    pygameImage = loadImageFromUrl(IMAGE)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Add Text
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # # Anger Text
    # First split up text, by word, not exceeding ANGER_MAX
    lines = splitText(angerText, ANGER_MAX)
    pygameImage = renderLines(pygameImage, ANGER_LOCATION, lines, ANGER_FONT, ANGER_COLOR, angle = ANGER_ANGLE, centeredY = False)

    # # Question Text
    # First split up text, by word, not exceeding QUESTION_MAX
    lines = splitText(questionText, QUESTION_MAX)
    pygameImage = renderLines(pygameImage, QUESTION_LOCATION, lines, QUESTION_FONT, QUESTION_COLOR, angle = QUESTION_ANGLE, centeredY = False)

    # Temporarily save image under util/image
    image = "util/image/SPONTANEOUS_ANGER_{}.png".format(angerText)
    pygame.image.save(pygameImage, image)

    return image

