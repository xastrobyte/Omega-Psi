from util.image.image import MemeTemplate

IMAGE = "https://i.imgur.com/rmUyMnP.jpg"

grusPlan = MemeTemplate(
    "grus plan",
    IMAGE,
    {
        "firstPanelText": {
            "location": [295, 80],
            "size": 35, "max": 18,
            "centered": [False, False],
        },
        "secondPanelText": {
            "location": [815, 90],
            "size": 35, "max": 20,
            "centered": [False, False],
        },
        "lastPanelTextLeft": {
            "location": [300, 415],
            "size": 35, "max": 20,
            "centered": [False, False],
        },
        "lastPanelTextRight": {
            "location": [815, 415],
            "size": 35, "max": 20,
            "centered": [False, False],
        }
    }
)

def generateImage(firstPanelText, secondPanelText, lastPanelText):
    return grusPlan.generateImage(
        firstPanelText = firstPanelText,
        secondPanelText = secondPanelText,
        lastPanelTextLeft = lastPanelText,
        lastPanelTextRight = lastPanelText
    )