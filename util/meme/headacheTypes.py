from util.image.image import MemeTemplate

IMAGE = "https://i.imgur.com/AWl1ktB.jpg"

headacheTypes = MemeTemplate(
    "headache types",
    IMAGE,
    {
        "headacheText": {
            "location": [465, 515],
            "size": 65, "max": 20,
        }
    }
)

def generateImage(headacheText):
    return headacheTypes.generateImage(
        headacheText = headacheText
    )