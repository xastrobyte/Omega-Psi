from util.image.image import MemeTemplate

import pygame

pygame.init()

IMAGE = "https://i.imgur.com/o1NzXyW.jpg"

spontaneousAnger = MemeTemplate(
    "spontaneous anger",
    IMAGE,
    {
        "angerText": {
            "location": [135, 20],
            "size": 35, "max": 10
        },
        "questionText": {
            "location": [385, 20],
            "size": 35, "max": 10
        }
    }
)

def generateImage(angerText, questionText):
    return spontaneousAnger.generateImage(
        angerText = angerText,
        questionText = questionText
    )