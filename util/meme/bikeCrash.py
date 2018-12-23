from util.image.image import MemeTemplate

IMAGE = "https://i.imgur.com/Y6p8GZw.jpg"

bikeCrash = MemeTemplate(
    "bike crash",
    IMAGE,
    {
        "firstText": {
            "location": [280, 500],
            "size": 50, "max": 30,
            "centered": [False, False]
        },
        "crashText": {
            "location": [640, 1185],
            "size": 50, "max": 30,
        }
    }
)

def generateImage(firstText, crashText):
    return bikeCrash.generateImage(
        firstText = firstText,
        crashText = crashText
    )