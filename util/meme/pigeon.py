from util.image.image import MemeTemplate

IMAGE = "https://i.kym-cdn.com/photos/images/original/001/374/087/be2.png"

pigeon = MemeTemplate(
    "is this a pigeon",
    IMAGE,
    {
        "pigeonText": {
            "location": [425, 90],
            "color": [0, 0, 0],
            "size": 25, "max": 15
        },
        "personText": {
            "location": [165, 230],
            "color": [255, 255, 255],
            "size": 25, "max": 10
        },
        "questionText": {
            "location": [285, 390],
            "color": [255, 255, 255],
            "size": 35, "max": 30,
            "centered": [False, True]
        }
    }
)

def generateImage(pigeonText, personText, questionText):
    return pigeon.generateImage(
        pigeonText = pigeonText,
        personText = personText,
        questionText = questionText
    )