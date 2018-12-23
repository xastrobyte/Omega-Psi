from util.image.image import MemeTemplate

IMAGE = "https://i.imgur.com/EyBqASK.png"

thanosStone = MemeTemplate(
    "thanos stone",
    IMAGE,
    {
        "stoneText": {
            "location": [550, 170],
            "size": 50, "max": 30,
        },
        "thanosText": {
            "location": [500, 820],
            "size": 50, "max": 30,
        }
    }
)

def generateImage(stoneText, thanosText):
    return thanosStone.generateImage(
        stoneText = stoneText,
        thanosText = thanosText
    )