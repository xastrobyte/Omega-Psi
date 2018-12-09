from util.image.image import MemeTemplate

import pygame

pygame.init()

IMAGE = "https://i.imgur.com/GBMCNYM.jpg"

cardSlam = MemeTemplate(
    "card slam",
    IMAGE,
    {
        "cardText": {
            "location": [560, 90],
            "size": 80, "max": 10
        },
        "bodyText": {
            "location": [660, 765],
            "color": [255, 255, 255],
            "size": 80, "max": 15
        },
        "tableText": {
            "location": [200, 1100], "angle": 30,
            "size": 60, "max": 20
        }
    }
)

def generateImage(cardText, bodyText, tableText):
    return cardSlam.generateImage(
        cardText = cardText,
        bodyText = bodyText,
        tableText = tableText
    )