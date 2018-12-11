from util.image.image import MemeTemplate

IMAGE = "https://i.imgur.com/uQ9GZUS.png"

rewindTime = MemeTemplate(
    "rewind time",
    IMAGE,
    {
        "text": {
            "location": [35, 40],
            "size": 45, "max": 40,
            "centered": [False, False]
        }
    }
)

def generateImage(text):
    return rewindTime.generateImage(
        text = text
    )