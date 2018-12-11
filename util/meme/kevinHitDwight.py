from util.image.image import MemeTemplate

IMAGE = "https://i.imgur.com/Tuh9AqB.png"

kevinHitDwight = MemeTemplate(
    "kevin hit dwight",
    IMAGE,
    {
        "kevinText": {
            "location": [435, 190],
            "color": [255, 255, 255],
            "size": 65, "max": 20
        },
        "dwightText": {
            "location": [645, 320],
            "color": [255, 255, 255],
            "size": 65, "max": 20
        }
    }
)

def generateImage(kevinText, dwightText):
    return kevinHitDwight.generateImage(
        kevinText = kevinText,
        dwightText = dwightText
    )