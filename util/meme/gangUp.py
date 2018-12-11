from util.image.image import MemeTemplate

IMAGE = "https://i.imgur.com/wSQIQdC.png"

gangUp = MemeTemplate(
    "gang up",
    IMAGE,
    {
        "attackerOneTop": {
            "location": [195, 65],
            "color": [255, 255, 255],
            "size": 50, "max": 10
        },
        "attackerOneBottom": {
            "location": [195, 465],
            "color": [255, 255, 255],
            "size": 50, "max": 10
        },
        "attackerTwoTop": {
            "location": [380, 65],
            "color": [255, 255, 255],
            "size": 50, "max": 10
        },
        "attackerTwoBottom": {
            "location": [380, 465],
            "color": [255, 255, 255],
            "size": 50, "max": 10
        },
        "attackerThreeTop": {
            "location": [545, 135],
            "color": [255, 255, 255],
            "size": 50, "max": 10
        },
        "attackerThreeBottom": {
            "location": [545, 515],
            "color": [255, 255, 255],
            "size": 50, "max": 10
        },
        "attackerFour": {
            "location": [40, 600],
            "size": 50, "max": 10
        },
        "personTextTop": {
            "location": [310, 325],
            "size": 50, "max": 10
        },
        "personTextBottom": {
            "location": [310, 700],
            "size": 50, "max": 10
        }
    }
)

def generateImage(attackerOne, attackerTwo, attackerThree, attackerFour, personText):
    return gangUp.generateImage(
        attackerOneTop = attackerOne,
        attackerOneBottom = attackerOne,
        attackerTwoTop = attackerTwo,
        attackerTwoBottom = attackerTwo,
        attackerThreeTop = attackerThree,
        attackerThreeBottom = attackerThree,
        attackerFour = attackerFour,
        personTextTop = personText,
        personTextBottom = personText
    )