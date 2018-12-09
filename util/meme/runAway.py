from util.image.image import MemeTemplate

import pygame

pygame.init()

IMAGE = "https://tinyurl.com/y9zqyq92"

runAway = MemeTemplate(
    "run away",
    IMAGE,
    {
        "chaserText": {
            "location": [380, 250],
            "color": [0, 160, 160],
            "size": 60, "max": 20
        },
        "runnerText": {
            "location": [230, 455],
            "color": [255, 255, 255],
            "size": 80, "max": 10
        }
    }
)

def generateImage(chaserText, runnerText):
    return runAway.generateImage(
        runnerText = runnerText,
        chaserText = chaserText
    )
