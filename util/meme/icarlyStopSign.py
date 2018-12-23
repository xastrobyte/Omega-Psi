from util.image.image import MemeTemplate

IMAGE = "https://i.imgur.com/MSaTVD2.jpg"

icarlyStopSign = MemeTemplate(
    "icarly stop sign",
    IMAGE,
    {
        "spencerText": {
            "location": [135, 250],
            "color": [255, 255, 255],
            "size": 30, "max": 15
        },
        "stopText": {
            "location": [140, 80], "angle": 37,
            "size": 25, "max": 15
        },
        "gibbyText": {
            "location": [260, 155],
            "color": [255, 255, 255],
            "size": 30, "max": 10
        }
    }
)

def generateImage(spencerText, stopText, gibbyText):
    return icarlyStopSign.generateImage(
        spencerText = spencerText,
        stopText = stopText,
        gibbyText = gibbyText
    )