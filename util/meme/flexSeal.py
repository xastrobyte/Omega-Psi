from util.image.image import MemeTemplate

IMAGE = "https://i.imgur.com/cGLvumT.jpg"

flexSeal = MemeTemplate(
    "flex seal",
    IMAGE,
    {
        "holderText": {
            "location": [145, 135],
            "color": [255, 255, 255],
            "size": 65, "max": 15
        },
        "boxText": {
            "location": [205, 360],
            "size": 65, "max": 15
        },
        "receiverText": {
            "location": [320, 735],
            "size": 65, "max": 15
        }
    }
)

def generateImage(holderText, boxText, receiverText):
    return flexSeal.generateImage(
        holderText = holderText,
        boxText = boxText,
        receiverText = receiverText
    )