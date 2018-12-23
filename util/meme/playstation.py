from util.image.image import MemeTemplate

IMAGE = "https://i.imgur.com/ic6R1lS.png"
IMAGE_THREE = "https://i.imgur.com/vO06vSr.png"
IMAGE_TWO = "https://i.imgur.com/vZhv4Hh.png"

playstationFour = MemeTemplate(
    "playstation four",
    IMAGE,
    {
        "triangleText": {
            "location": [145, 55],
            "size": 35, "max": 35,
            "centered": [False, True]
        },
        "squareText": {
            "location": [145, 160],
            "size": 35, "max": 35,
            "centered": [False, True]
        },
        "xText": {
            "location": [145, 260],
            "size": 35, "max": 35,
            "centered": [False, True]
        },
        "circleText": {
            "location": [145, 370],
            "size": 35, "max": 35,
            "centered": [False, True]
        }
    }
)

playstationThree = MemeTemplate(
    "playstation three",
    IMAGE_THREE,
    {
        "squareText": {
            "location": [145, 45],
            "size": 35, "max": 35,
            "centered": [False, True]
        },
        "xText": {
            "location": [145, 150],
            "size": 35, "max": 35,
            "centered": [False, True]
        },
        "circleText": {
            "location": [145, 260],
            "size": 35, "max": 35,
            "centered": [False, True]
        }
    }
)

playstationTwo = MemeTemplate(
    "playstation two",
    IMAGE_TWO,
    {
        "xText": {
            "location": [145, 45],
            "size": 35, "max": 35,
            "centered": [False, True]
        },
        "circleText": {
            "location": [145, 160],
            "size": 35, "max": 35,
            "centered": [False, True]
        }
    }
)

def generateImage(triangleText, squareText, xText, circleText):

    if len(triangleText) == 0:

        if len(squareText) == 0:
            
            return playstationTwo.generateImage(
                xText = xText,
                circleText = circleText
            )
        
        return playstationThree.generateImage(
            squareText = squareText,
            xText = xText,
            circleText = circleText
        )

    return playstationFour.generateImage(
        triangleText = triangleText,
        squareText = squareText,
        xText = xText,
        circleText = circleText
    )