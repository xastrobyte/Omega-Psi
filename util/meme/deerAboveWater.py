from util.image.image import MemeTemplate

IMAGE = "https://i.imgur.com/Npr993s.jpg"

deerAboveWater = MemeTemplate(
    "deer above water",
    IMAGE,
    {
        "deerText": {
            "location": [410, 225],
            "color": [255, 255, 255],
            "size": 75, "max": 15
        },
        "handText": {
            "location": [385, 575],
            "size": 75, "max": 15
        }
    }
)

def generateImage(deerText, handText):
    return deerAboveWater.generateImage(
        deerText = deerText,
        handText = handText
    )