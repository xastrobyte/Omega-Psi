from util.image.image import MemeTemplate

IMAGE = "https://i.imgur.com/Tmasvyy.jpg"

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