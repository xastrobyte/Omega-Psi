from util.image.image import MemeTemplate

import pygame

pygame.init()

IMAGE_TWO = "https://tinyurl.com/twoArmHandshake"
IMAGE_THREE = "https://tinyurl.com/threeArmHandshake"
IMAGE_FOUR = "https://tinyurl.com/fourArmHandshake"

twoArmHandshake = MemeTemplate(
    "two arm handshake",
    IMAGE_TWO,
    {
        "handsText": {
            "location": [370, 140],
            "color": [255, 255, 255],
            "size": 65, "max": 15
        },
        "firstArm": {
            "location": [275, 475],
            "color": [255, 255, 255],
            "size": 65, "max": 10
        },
        "secondArm": {
            "location": [650, 375],
            "color": [255, 255, 255],
            "size": 65, "max": 10
        }
    }
)

threeArmHandshake = MemeTemplate(
    "three arm handshake",
    IMAGE_THREE,
    {
        "handsText": {
            "location": [320, 90],
            "color": [255, 255, 255],
            "size": 65, "max": 15
        },
        "firstArm": {
            "location": [200, 410],
            "color": [255, 255, 255],
            "size": 65, "max": 10
        },
        "secondArm": {
            "location": [600, 170],
            "color": [255, 255, 255],
            "size": 65, "max": 10
        },
        "thirdArm": {
            "location": [600, 350],
            "color": [255, 255, 255],
            "size": 65, "max": 10
        }
    }
)

fourArmHandshake = MemeTemplate(
    "four arm handshake",
    IMAGE_FOUR,
    {
        "handsText": {
            "location": [240, 65],
            "color": [255, 255, 255],
            "size": 65, "max": 15
        },
        "firstArm": {
            "location": [210, 180],
            "color": [255, 255, 255],
            "size": 65, "max": 10
        },
        "secondArm": {
            "location": [165, 290],
            "color": [255, 255, 255],
            "size": 65, "max": 10
        },
        "thirdArm": {
            "location": [425, 125],
            "color": [255, 255, 255],
            "size": 65, "max": 10
        },
        "fourthArm": {
            "location": [440, 260],
            "color": [255, 255, 255],
            "size": 65, "max": 10
        }
    }
)

def generateImage(handsText, firstArm, secondArm, thirdArm = None, fourthArm = None):
    if thirdArm == None:
        return twoArmHandshake.generateImage(
            handsText = handsText,
            firstArm = firstArm,
            secondArm = secondArm
        )
    
    if fourthArm == None:
        return threeArmHandshake.generateImage(
            handsText = handsText,
            firstArm = firstArm,
            secondArm = secondArm,
            thirdArm = thirdArm
        )
    
    return fourArmHandshake.generateImage(
        handsText = handsText,
        firstArm = firstArm,
        secondArm = secondArm,
        thirdArm = thirdArm,
        fourthArm = fourthArm
    )