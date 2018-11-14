from util.image.image import MemeTemplate

import pygame

pygame.init()

IMAGE = "https://i.imgur.com/3QVQ2V5.jpg"

classroomStares = MemeTemplate(
    "classroom stares",
    IMAGE,
    {
        "bubbleText": {
            "location": [350, 250],
            "color": [255, 255, 255],
            "size": 80, "max": 10
        }
    }
)

def generateImage(bubbleText):
    return classroomStares.generateImage(
        bubbleText = bubbleText
    )
