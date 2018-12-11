from util.image.image import MemeTemplate

IMAGE = "https://i.imgur.com/rv80SIU.jpg"

threeDoors = MemeTemplate(
    "three doors",
    IMAGE,
    {
        "firstDoorText": {
            "location": [75, 65],
            "size": 65, "max": 10
        },
        "secondDoorText": {
            "location": [280, 65],
            "size": 65, "max": 10
        },
        "thirdDoorText": {
            "location": [565, 65],
            "size": 65, "max": 10
        },
        "personText": {
            "location": [285, 755],
            "size": 45, "max": 10
        }
    }
)

def generateImage(firstDoorText, secondDoorText, thirdDoorText, personText):
    return threeDoors.generateImage(
        firstDoorText = firstDoorText,
        secondDoorText = secondDoorText,
        thirdDoorText = thirdDoorText,
        personText = personText
    )