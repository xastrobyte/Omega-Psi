from util.image.image import MemeTemplate

IMAGE = "https://i.imgur.com/U2cudpx.png"

trump = MemeTemplate(
    "trump",
    IMAGE,
    {
        "tweetText": {
            "location": [40, 165],
            "size": 65, "max": 50,
            "centered": [False, False]
        }
    }
)

def generateImage(tweetText):
    return trump.generateImage(
        tweetText = tweetText
    )