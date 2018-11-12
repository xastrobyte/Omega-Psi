from util.image.image import renderLines

from util.utils import loadImageFromUrl, splitText

import pygame

pygame.init()

# IMAGE = "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/intermediary/f/918578eb-1cd2-494b-a4cf-549d6c9a7ceb/dagvpp7-9548a83d-07aa-4bf1-87e5-9c8d4fed81ec.jpg/v1/fill/w_963,h_830,q_70,strp/master_s_blessing_by_morkardfc_dagvpp7-pre.jpg"
IMAGE = "https://tinyurl.com/mastersBlessing"

# Text Angles, Colors, and Default Sizes
MASTER_LOCATION = [350, 250]
MASTER_ANGLE = 10
MASTER_COLOR = [255, 255, 255]
MASTER_SIZE = 80
MASTER_MAX = 10
MASTER_FONT = pygame.font.SysFont("arial", MASTER_SIZE)

SWORD_LOCATION = [480, 385]
SWORD_ANGLE = 8
SWORD_COLOR = [255, 255, 255]
SWORD_SIZE = 80
SWORD_MAX = 25
SWORD_FONT = pygame.font.SysFont("arial", SWORD_SIZE)

APPRENTICE_LOCATION = [655, 540]
APPRENTICE_ANGLE = 10
APPRENTICE_COLOR = [255, 255, 255]
APPRENTICE_SIZE = 80
APPRENTICE_MAX = 10
APPRENTICE_FONT = pygame.font.SysFont("arial", APPRENTICE_SIZE)

def generateImage(masterText, swordText, apprenticeText):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Load Image
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    # Make Request; Get Image through Pillow
    pygameImage = loadImageFromUrl(IMAGE)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Add Text
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # # Card Text
    # First split up text, by word, not exceeding MASTER_MAX
    lines = splitText(masterText, MASTER_MAX)
    pygameImage = renderLines(pygameImage, MASTER_LOCATION, lines, MASTER_FONT, MASTER_COLOR, angle = MASTER_ANGLE)
    
    # # Body Text
    # First split up text, by word, not exceeding SWORD_MAX
    lines = splitText(swordText, SWORD_MAX)
    pygameImage = renderLines(pygameImage, SWORD_LOCATION, lines, SWORD_FONT, SWORD_COLOR, angle = SWORD_ANGLE)

    # # Table Text
    # First split up text, by word, not exceeding APPRENTICE_MAX
    lines = splitText(apprenticeText, APPRENTICE_MAX)
    pygameImage = renderLines(pygameImage, APPRENTICE_LOCATION, lines, APPRENTICE_FONT, APPRENTICE_COLOR, angle = APPRENTICE_ANGLE)

    # Temporarily save image under util/image
    image = "util/image/MASTERS_BLESSING_{}.png".format(masterText)
    pygame.image.save(pygameImage, image)

    return image

