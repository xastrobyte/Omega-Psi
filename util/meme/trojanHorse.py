from util.image.image import MemeTemplate

IMAGE = "https://i.imgur.com/pNR2At1.jpg"

trojanHorse = MemeTemplate(
    "trojan horse",
    IMAGE,
    {
        "hidersText": {
            "location": [240, 415],
            "color": [255, 255, 255],
            "size": 80, "max": 10
        },
        "horseText": {
            "location": [360, 225],
            "size": 80, "max": 10
        },
        "castleText": {
            "location": [520, 35],
            "size": 80, "max": 10,
            "centered": [True, False]
        },
        "welcomersText": {
            "location": [560, 550],
            "color": [255, 255, 255],
            "size": 80, "max": 10
        }
    }
)

def generateImage(hidersText, horseText, castleText, welcomersText):
    return trojanHorse.generateImage(
        hidersText = hidersText,
        horseText = horseText,
        castleText = castleText,
        welcomersText = welcomersText
    )