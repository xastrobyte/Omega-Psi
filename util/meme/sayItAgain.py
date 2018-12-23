from util.image.image import MemeTemplate

IMAGE ="https://i.imgflip.com/16iyn1.jpg?a428353"

sayItAgain = MemeTemplate(
    "say it again",
    IMAGE,
    {
        "topText": {
            "location": [335, 30],
            "size": 70, "max": 25,
            "centered": [True, False]
        },
        "bottomText": {
            "location": [335, 850],
            "size": 65, "max": 25
        }
    }
)

def generateImage(topText, bottomText):
    return sayItAgain.generateImage(
        topText = topText,
        bottomText = bottomText
    )