from util.image.image import MemeTemplate

IMAGE = "https://i.imgur.com/3aIi1fH.jpg"

fearNot = MemeTemplate(
    "fear not",
    IMAGE,
    {
        "speechText": {
            "location": [360, 25],
            "size": 45, "max": 23,
            "centered": [False, False]
        }
    }
)

def generateImage(speechText):
    return fearNot.generateImage(
        speechText = speechText
    )