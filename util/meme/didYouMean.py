from util.image.image import MemeTemplate

IMAGE = "https://i.imgur.com/8GpQQun.png"
IMAGE_BOTTOM = "https://i.imgur.com/TmAPdcG.png"

didYouMean = MemeTemplate(
    "did you mean",
    IMAGE,
    {
        "searchText": {
            "location": [165, 40],
            "color": [0, 0, 0],
            "size": 25, "max": 30,
            "centered": [False, True]
        },
        "didYouMeanText": {
            "location": [285, 182],
            "color": [0, 0, 0],
            "size": 25, "max": 30,
            "centered": [False, True]
        }
    }
)

didYouMeanBottom = MemeTemplate(
    "did you mean bottom",
    IMAGE_BOTTOM,
    {
        "didYouMeanText": {
            "location": [125, 62],
            "color": [0, 0, 0],
            "size": 25, "max": 30,
            "centered": [False, True]
        }
    }
)

def generateImage(searchText, didYouMeanText):

    if len(searchText) == 0:
        return didYouMeanBottom.generateImage(
            didYouMeanText = didYouMeanText
        )

    return didYouMean.generateImage(
        searchText = searchText,
        didYouMeanText = didYouMeanText
    )