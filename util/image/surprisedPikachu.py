from util.image.image import renderLines

from util.utils import loadImageFromUrl, splitText

import pygame

pygame.init()

IMAGE = "https://imgflip.com/s/meme/Surprised-Pikachu.jpg"

# Text Angles, Colors, and Default Sizes
FONT = pygame.font.SysFont("arial", 120)
SIZE = 40
COLOR = [0, 0, 0]

def generateImage(lines):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Load Image
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    # Make Request; Get Image through Pillow
    pygameImage = loadImageFromUrl(IMAGE)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Add Text (based off of how many lines there are)
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # Get line spacing
    spacing = len(lines) * -93 + 600
    origin = [20, 20 * (len(lines) % 2)]

    for line in range(len(lines)):

        # Split text
        textLines = splitText(lines[line], SIZE)

        # Add each line of text
        for text in range(len(textLines)):

            pygameImage = renderLines(
                pygameImage, [origin[0], origin[1] + line * spacing + text * FONT.size(textLines[text])[1]],
                [textLines[text]], FONT,
                COLOR,
                centered = [False, False]
            )

    # Temporarily save image under util/image
    image = "util/image/SURPRISED_PIKACHU_{}.png".format(lines[0])
    pygame.image.save(pygameImage, image)
    return image
