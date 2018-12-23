from util.image.image import MemeTemplate

IMAGE = "https://tinyurl.com/puppetMeme"

puppetMeme = MemeTemplate(
    "puppet meme",
    IMAGE,
    {
        "handText": {
            "location": [80, 50],
            "size": 35, "max": 10
        },
        "puppetText": {
            "location": [105, 230],
            "color": [160, 160, 0],
            "size": 35, "max": 10
        }
    }
)

def generateImage(handText, puppetText):
    return puppetMeme.generateImage(
        handText = handText,
        puppetText = puppetText
    )