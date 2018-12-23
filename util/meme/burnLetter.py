from util.image.image import MemeTemplate

IMAGE = "https://tinyurl.com/burnLetter"

burnLetter = MemeTemplate(
    "burn letter",
    IMAGE,
    {
        "letterText": {
            "location": [25, 35],
            "size": 15, "max": 15,
            "centered": [False, False]
        },
        "spongebobText": {
            "location": [180, 55],
            "size": 15, "max": 10
        }
    }
)

def generateImage(letterText, spongebobText):
    return burnLetter.generateImage(
        letterText = letterText,
        spongebobText = spongebobText
    )