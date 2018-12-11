from util.image.image import MemeTemplate

IMAGE = "https://i.imgur.com/91Orpkg.jpg"

soccerTongue = MemeTemplate(
    "soccer tongue",
    IMAGE,
    {
        "tongueText": {
            "location": [330, 95],
            "color": [255, 255, 255],
            "size": 65, "max": 20
        },
        "personText": {
            "location": [555, 185],
            "color": [255, 255, 255],
            "size": 65, "max": 15
        }
    }
)

def generateImage(tongueText, personText):
    return soccerTongue.generateImage(
        tongueText = tongueText,
        personText = personText
    )