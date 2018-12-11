from util.image.image import MemeTemplate

IMAGE = "https://i.imgur.com/EzWiHEX.png"

holdUpEarth = MemeTemplate(
    "hold up earth",
    IMAGE,
    {
        "earthText": {
            "location": [285, 90],
            "color": [255, 255, 255],
            "size": 65, "max": 20
        },
        "personText": {
            "location": [280, 365],
            "color": [255, 255, 255],
            "size": 65, "max": 20
        }
    }
)

def generateImage(earthText, personText):
    return holdUpEarth.generateImage(
        earthText = earthText,
        personText = personText
    )