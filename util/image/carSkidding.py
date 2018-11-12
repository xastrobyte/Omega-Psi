from util.image.image import renderLines

from util.utils import loadImageFromUrl, splitText

import pygame

pygame.init()

# IMAGE = "https://lh3.googleusercontent.com/70CdRIbwtm_58qoxp5MgpplMnDC8BDwoS89HNxohXKpY8kks-L6Tj0e2eKNFssUvmloaFCUppnpyGEeh3CjLVEKVxmwZsxZmCMrFExcxIpPHlnOWaC2XrES8qeQw8FhZzOeCN7_KqutzjOkh6Q2jtAVR2VJON5aqb8btX2gUWW6IjkGBw9oVqdzcIqAj-RP8GYNZGoG3FIEZIgq1XWnCFnXO9YGHF_CSsR_mTPxHZs3KORNBN2UGaxYWJOSXczWUHTW_jwd3qgxwhFnUj5dn1O8rqgKHCG3FoKzFPO77f7dSLd9RiTbFD7oRYJ2QmkuEgr7G3r-8ujQEimoLesJLLhVDiiC-JOWdP0ZfXR96KI4dpme35v01jCbA3rLlMFqQKUjpLKG6yaCe855BQ0dyMR5kjM10cuiGGFDaABhMQ0PksdumZF4GO1UVav9CfUHA99CTPlq9MxrO094YpuYQ_ElSXDMATjFjORbA3Hv194DZ5BGZQZh8qxRguzCpJhO52yXZEElaHPiiyXPvyVomhDWcF6CaDLXztnZF6teMxVrkiIlDRZEU133TOV2u9wbqUdI-a7nEsib5GfU6-PeleDVQAI5TOpv1SsACBd3_N76ZmypoQk4j-J_rcexa--U-M1HQuQg9DTIoj53fl9EtQDiXlY4OGmAA4Urgrj9CIz6ZGclWL6RsBzVC84OIkGhyAm0n2h2vd95RI5RFwZLQPh_sgcgv9d_Re2P11w=w940-h889-no"
IMAGE = "https://tinyurl.com/carSkidding"

# Text Angles, Colors, and Default Sizes
CAR_LOCATION = [450, 660]
CAR_ANGLE = 0
CAR_COLOR = [255, 255, 255]
CAR_SIZE = 60
CAR_MAX = 10
CAR_FONT = pygame.font.SysFont("arial", CAR_SIZE)

STRAIGHT_LOCATION = [285, 210]
STRAIGHT_ANGLE = 0
STRAIGHT_COLOR = [255, 255, 255]
STRAIGHT_SIZE = 60
STRAIGHT_MAX = 10
STRAIGHT_FONT = pygame.font.SysFont("arial", STRAIGHT_SIZE)

EXIT_LOCATION = [570, 210]
EXIT_ANGLE = 0
EXIT_COLOR = [255, 255, 255]
EXIT_SIZE = 60
EXIT_MAX = 10
EXIT_FONT = pygame.font.SysFont("arial", EXIT_SIZE)

def generateImage(carText, straightText, exitText):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Load Image
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    # Make Request; Get Image through Pillow
    pygameImage = loadImageFromUrl(IMAGE)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Add Text
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # # Car Text
    # First split up text, by word, not exceeding CAR_MAX
    lines = splitText(carText, CAR_MAX)
    pygameImage = renderLines(pygameImage, CAR_LOCATION, lines, CAR_FONT, CAR_COLOR, angle = CAR_ANGLE)
    
    # # Straight Text
    # First split up text, by word, not exceeding STRAIGHT_MAX
    lines = splitText(straightText, STRAIGHT_MAX)
    pygameImage = renderLines(pygameImage, STRAIGHT_LOCATION, lines, STRAIGHT_FONT, STRAIGHT_COLOR, angle = STRAIGHT_ANGLE)

    # # Exit Text
    # First split up text, by word, not exceeding EXIT_MAX
    lines = splitText(exitText, EXIT_MAX)
    pygameImage = renderLines(pygameImage, EXIT_LOCATION, lines, EXIT_FONT, EXIT_COLOR, angle = EXIT_ANGLE)

    # Temporarily save image under util/image
    image = "util/image/CAR_SKIDDING_{}.png".format(carText)
    pygame.image.save(pygameImage, image)

    return image

