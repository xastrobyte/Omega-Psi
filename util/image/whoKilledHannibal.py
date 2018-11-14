from util.image.image import MemeTemplate

IMAGE = "https://i.imgflip.com/28s2gu.jpg"

whoKilledHannibal = MemeTemplate(
    "who killed hannibal",
    IMAGE,
    {
        "ericAndreText": {
            "location": [865, 475],
            "color": [255, 255, 255],
            "size": 80, "max": 10
        },
        "gunText": {
            "location": [610, 290],
            "color": [255, 255, 255],
            "size": 80, "max": 10
        },
        "actionText": {
            "location": [600, 670],
            "color": [200, 200, 0],
            "size": 80, "max": 30
        },
        "hannibalText": {
            "location": [300, 435],
            "color": [255, 255, 255],
            "size": 80, "max": 10
        },
        "questionText": {
            "location": [600, 1385],
            "color": [200, 200, 0],
            "size": 80, "max": 30
        }
    }
)

def generateImage(ericAndreText, gunText, hannibalText, questionText):
    return whoKilledHannibal.generateImage(
        ericAndreText = ericAndreText,
        gunText = gunText,
        actionText = "[gunshots]",
        hannibalText = hannibalText,
        questionText = questionText
    )