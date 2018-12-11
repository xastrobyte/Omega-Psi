from util.image.image import MemeTemplate

IMAGE = "https://i.imgur.com/fAsM4Vb.jpg"

iCantRead = MemeTemplate(
    "i cant read",
    IMAGE,
    {
        "signText": {
            "location": [45, 110],
            "size": 45, "max": 20,
            "centered": [False, False],
        },
        "personText": {
            "location": [330, 625],
            "size": 65, "max": 20
        }
    }
)

def generateImage(signText, personText):
    return iCantRead.generateImage(
        signText = signText,
        personText = personText
    )