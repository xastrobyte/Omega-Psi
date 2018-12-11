from util.image.image import MemeTemplate

IMAGE = "https://i.imgur.com/lmZASmG.jpg"

executiveOrder = MemeTemplate(
    "executive order",
    IMAGE,
    {
        "text": {
            "location": [755, 575],
            "size": 60, "max": 20,
            "centered": [False, False]
        }
    }
)

def generateImage(text):
    return executiveOrder.generateImage(
        text = text
    )