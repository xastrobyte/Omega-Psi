from util.utils import loadImageFromUrl, getSmallestRect

from datetime import datetime
import pygame

pygame.init()

V_BUCKS_ICON = "https://image.fnbr.co/price/icon_vbucks_50x.png"

def addGameType(discordEmbed, gameTypeDict, gameType):
    """Adds the data for a game type to the specified embed

    Parameters:
        discordEmbed (discord.Embed): The Embed to add to.
        gameTypeDict (dict): The dict to use.
    """

    # Only do it if gameTypeDict is not None
    if gameTypeDict != None:

        # Keep track of game types
        gameTypes = {
            "p2": "Solo", "p10": "Duo", "p9": "Squad",
            "curr_p2": "Season Solo", "curr_p10": "Season Duo", "curr_p9": "Season Squad"
        }

        if gameType.find("p2") != -1:
            topN1 = {
                "text": "Top 10",
                "value": gameTypeDict["top10"]["value"]
            }
            topN2 = {
                "text": "Top 25",
                "value": gameTypeDict["top25"]["value"]
            }
        
        elif gameType.find("p10") != -1:
            topN1 = {
                "text": "Top 5",
                "value": gameTypeDict["top5"]["value"]
            }
            topN2 = {
                "text": "Top 12",
                "value": gameTypeDict["top12"]["value"]
            }
        
        else:
            topN1 = {
                "text": "Top 3",
                "value": gameTypeDict["top3"]["value"]
            }
            topN2 = {
                "text": "Top 6",
                "value": gameTypeDict["top6"]["value"]
            }

        discordEmbed.add_field(
            name = gameTypes[gameType],
            value = "{}\n{}\n{}\n{}\n{}\n{}\n".format(
                "**Matches**: " + gameTypeDict["matches"]["value"],
                "**Wins**: " + gameTypeDict["top1"]["value"],
                "**{}**: {}".format(topN1["text"], topN1["value"]),
                "**{}**: {}".format(topN2["text"], topN2["value"]),
                "**Kills**: {}".format(gameTypeDict["kills"]["value"]),
                "**K/d**: " + gameTypeDict["kd"]["value"]
            ),
            inline = True
        )

    return discordEmbed

def getItemShopImage(itemShopDict):
    """Returns a single image for the current item shop.

    Parameters:
        itemShopDict (dict): The dictionary that stores all the information for an item.
    """

    # Get smallest rect of rectangle
    numItems = len(itemShopDict)
    smallestRect = getSmallestRect(numItems)
    while (abs(smallestRect[0] - smallestRect[1]) > 2):
        numItems += 1
        smallestRect = getSmallestRect(numItems)
    
    # Create surface given size
    shopSurface = pygame.Surface((smallestRect[0] * (512 + (smallestRect[0] - 1)), smallestRect[1] * (512 + (smallestRect[1] - 1))))
    shopSurface.fill([20, 20, 20])

    count = 0
    for item in itemShopDict:
        shopSurface.blit(
            getItemImage(item),
            (
                (count %  smallestRect[0]) * 512 + (count %  smallestRect[0]),
                (count // smallestRect[1]) * 512 + (count // smallestRect[1])
            )
        )
        count += 1
    
    # Save Shop surface
    currentTime = datetime.now()
    image = "shop_{}_{}_{}.png".format(
        currentTime.month, currentTime.day, currentTime.year
    )

    pygame.image.save(shopSurface, image)

    return image

def getItemImage(itemDict):
    """Returns the filename for the image url given masked over top of a Fortnite rarity background.

    Parameters:
        itemDict (dict): The dictionary of the item to draw
    """

    # Get valid rarity
    rarity = itemDict["rarity"].lower()
    if rarity in ["uncommon", "handmade"]:
        rarity = "Uncommon"
    elif rarity in ["rare", "sturdy"]:
        rarity = "Rare"
    elif rarity in ["epic", "quality"]:
        rarity = "Epic"
    elif rarity in ["legendary", "fine"]:
        rarity = "Legendary"
    else:
        rarity = "Common"
    
    # Load the rarity image; Resize to 512x512
    rarity = pygame.image.load("util/game/fortniteRarities/fortnite{}.png".format(rarity))
    rarity = pygame.transform.scale(rarity, (512, 512))

    # Load the item image
    item = loadImageFromUrl(itemDict["imageUrl"])

    # Load the V-bucks image
    vBucks = loadImageFromUrl(V_BUCKS_ICON)

    # Blit the item on top of the rarity
    rarity.blit(item, (0, 0))

    # Blit the item's name and V-Bucks on top of it as well (Create separate surface for it)
    font = pygame.font.SysFont("arial", 50)

    nameText = font.render(itemDict["name"], True, (0, 0, 0))
    vBucksText = font.render(str(itemDict["vBucks"]), True, (0, 0, 0))
    
    # Put Name on left side
    rarity.blit(
        nameText,
        (5, 5)
    )

    # Put V-Bucks on right side
    rarity.blit(
        vBucks,
        (rarity.get_width() - 5 - vBucks.get_width() - 2 - vBucksText.get_width(), 5)
    )
    rarity.blit(
        vBucksText,
        (rarity.get_width() - 5 - vBucksText.get_width(), (vBucks.get_height() - vBucksText.get_height()) // 2 + 5)
    )

    return rarity