from util.image.image import MemeTemplate

# IMAGE = "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/intermediary/f/918578eb-1cd2-494b-a4cf-549d6c9a7ceb/dagvpp7-9548a83d-07aa-4bf1-87e5-9c8d4fed81ec.jpg/v1/fill/w_963,h_830,q_70,strp/master_s_blessing_by_morkardfc_dagvpp7-pre.jpg"
IMAGE = "https://tinyurl.com/mastersBlessing"

mastersBlessing = MemeTemplate(
    "masters blessing",
    IMAGE,
    {
        "masterText": {
            "location": [350, 250], "angle": 10,
            "color": [255, 255, 255], "size": 80,
            "max": 10
        },
        "swordText": {
            "location": [480, 385], "angle": 8,
            "color": [255, 255, 255], "size": 80,
            "max": 25
        },
        "apprenticeText": {
            "location": [655, 540], "angle": 10,
            "color": [255, 255, 255], "size": 80,
            "max": 10
        }
    }
)

def generateImage(masterText, swordText, apprenticeText):
    return mastersBlessing.generateImage(
        masterText = masterText, 
        swordText = swordText, 
        apprenticeText = apprenticeText
    )