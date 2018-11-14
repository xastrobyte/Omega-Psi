from util.image.image import MemeTemplate

import pygame

pygame.init()

# IMAGE = "https://preview.redd.it/erpvm5m39gw11.jpg?width=640&crop=smart&auto=webp&s=5f06e60d8ce81befbc5d9005772f82e19d0514b1"
IMAGE = "https://tinyurl.com/surprisedDwight"

surprisedDwight = MemeTemplate(
    "surprised dwight",
    IMAGE,
    {
        "dwightText": {
            "location": [220, 300],
            "color": [255, 255, 255],
            "size": 60, "max": 15
        },
        "angelaText": {
            "location": [485, 300],
            "color": [255, 255, 255],
            "size": 60, "max": 10
        }
    }
)

def generateImage(dwightText, angelaText):
    return surprisedDwight.generateImage(
        dwightText = dwightText,
        angelaText = angelaText
    )