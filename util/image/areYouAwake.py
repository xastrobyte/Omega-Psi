from util.image.image import MemeTemplate

import pygame

pygame.init()

IMAGE = "https://i.imgflip.com/2gqv88.jpg"

areYouAwake = MemeTemplate(
    "are you awake",
    IMAGE,
    {
        "text": {
            "location": [25, 270],
            "size": 25, "max": 30,
            "centered": [False, False]
        }
    }
)

def generateImage(text):
    return areYouAwake.generateImage(
        text = text
    )