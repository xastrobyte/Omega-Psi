from util.image.image import MemeTemplate

IMAGE = "https://i.imgur.com/lIatply.jpg"

brainOf = MemeTemplate(
    "brain of",
    IMAGE,
    {
        "brainText": {
            "location": [60, 495],
            "size": 40, "max": 55,
            "centered": [False, True]
        }       
    }
)

def generateImage(brainText):
    return brainOf.generateImage(
        brainText = brainText
    )