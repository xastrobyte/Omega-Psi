from util.image.image import MemeTemplate

import pygame

pygame.init()

IMAGE = "https://i.imgur.com/GzRvZUx.png"

butILikeThis = MemeTemplate(
    "but i like this",
    IMAGE,
    {
        "redCarText": {
            "location": [450, 185],
            "color": [255, 255, 255],
            "size": 50, "max": 15
        },
        "whiteCarText": {
            "location": [160, 515],
            "angle": 15,
            "size": 50, "max": 15
        }
    }
)

def generateImage(redCarText, whiteCarText):
    return butILikeThis.generateImage(
        redCarText = redCarText,
        whiteCarText = whiteCarText
    )