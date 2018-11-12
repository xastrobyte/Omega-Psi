from util.image.image import renderLines

from util.utils import loadImageFromUrl, splitText

import pygame

pygame.init()

# IMAGE = "https://lh3.googleusercontent.com/A8DL1PjutxJYJHiqXtWSB6mZ9OEpvF_1l-U7sGUwRSt7vBopZT_N3uRMPUYxYilpYfzOCYLGOXStWkXqEYqVId_AeugUdZGrHFHPYprQBtLs9N_Vx5e4wlolkIpdLcZFQeQB4GCwrIPYbidAx3vSeqcSCb7amO-KoKogZMwlOnrzTclmEoZUCfHmO5m6z4fABTfCjOGdciImzxgRIVUmU0wpwO5jYPqhsIZ5TPqJE-KUAKNss2CQrJP9vcEKQj6uWyO8hss1j0DRp7kSiZsk1mIBVrlnNN3AiP_cYSuKsPtUp68YEvl8BWHlelIO6BgErS5uzQYRKErJYMOfxdFZxSbyA0t8AFBPry2LCL8FSE1yxmaKx42TgawRpYm9hHp-ToQifyhj2yCiokUy_1hu8fNcrsvM042mSCEZK44aSy4W3asYyObNnm06d6HRlu4d40en7Sx5ZWH1g3BTodV1d9-AwfzphZyZa_fdPRWZz7ajpBIvtUrO7xRRfuID_F6t1_7zK7RtnfrQSrbVenWsBEm3GknE8ErnXgxQdv9S0ZAbfzkxFsU1pOiPzga8kq1ORnRhtx20UGedqDtBtJzhBDmLMHKo-u-IylZ4AfoTit7ZVb7eIHy08YoQH_EZlKKc05qvYBz4Hw8eW-rXU24t0rsBdzzyQtgk4oDb8ocU6zlpbpnzHp9uP3zy0i9csN3pRhtK2XXF5WdDn4_XZK--N634r6KIgj-FV1kKiLk=w1013-h889-no"
IMAGE = "https://tinyurl.com/saveOneMeme"

# Text Angles, Colors, and Default Sizes
PERSON_LOCATION = [240, 250]
PERSON_ANGLE = 0
PERSON_COLOR = [0, 0, 0]
PERSON_SIZE = 80
PERSON_MAX = 15
PERSON_FONT = pygame.font.SysFont("arial", PERSON_SIZE)

LEFT_BEHIND_LOCATION = [600, 235]
LEFT_BEHIND_ANGLE = 0
LEFT_BEHIND_COLOR = [0, 0, 0]
LEFT_BEHIND_SIZE = 60
LEFT_BEHIND_MAX = 10
LEFT_BEHIND_FONT = pygame.font.SysFont("arial", LEFT_BEHIND_SIZE)

SAVE_LOCATION = [900, 210]
SAVE_ANGLE = 0
SAVE_COLOR = [0, 0, 0]
SAVE_SIZE = 60
SAVE_MAX = 10
SAVE_FONT = pygame.font.SysFont("arial", SAVE_SIZE)

def generateImage(personText, leftBehindText, saveText):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Load Image
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    # Make Request; Get Image through Pillow
    pygameImage = loadImageFromUrl(IMAGE)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Add Text
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # # Person Text
    # First split up text, by word, not exceeding PERSON_MAX
    lines = splitText(personText, PERSON_MAX)
    pygameImage = renderLines(pygameImage, PERSON_LOCATION, lines, PERSON_FONT, PERSON_COLOR, angle = PERSON_ANGLE)
    
    # # Left Behind Text
    # First split up text, by word, not exceeding LEFT_BEHIND_MAX
    lines = splitText(leftBehindText, LEFT_BEHIND_MAX)
    pygameImage = renderLines(pygameImage, LEFT_BEHIND_LOCATION, lines, LEFT_BEHIND_FONT, LEFT_BEHIND_COLOR, angle = LEFT_BEHIND_ANGLE)

    # # Save Text
    # First split up text, by word, not exceeding SAVE_MAX
    lines = splitText(saveText, SAVE_MAX)
    pygameImage = renderLines(pygameImage, SAVE_LOCATION, lines, SAVE_FONT, SAVE_COLOR, angle = SAVE_ANGLE)

    # Temporarily save image under util/image
    image = "util/image/SAVE_ONE_{}.png".format(personText)
    pygame.image.save(pygameImage, image)

    return image

