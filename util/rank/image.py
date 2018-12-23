from util.file.server import Server

from util.utils.miscUtils import loadImageFromUrl

import pygame
import pygame.freetype
import pygame.color

pygame.init()

class Rect:

    def __init__(self, x, y, w, h, color, font):
        """Creates a Rect object to help render certain text components
        or image components onto a rank image.\n

        x - The x-coordinate of the Rect object.\n
        y - The y-coordinate of the Rect object.\n
        w - The width of the Rect object.\n
        h - The height of the Rect object.\n
        color - The color of the Rect object.\n
        font - The font of the Rect object.\n
        """

        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._color = color
        self._font = font
    
    def getX(self):
        """Returns the x-coordinate of the Rect object.\n
        """
        return self._x

    def getY(self):
        """Returns the y-coordinate of the Rect object.\n
        """
        return self._y

    def getWidth(self):
        """Returns the width of the Rect object.\n
        """
        return self._w

    def getHeight(self):
        """Returns the height of the Rect object.\n
        """
        return self._h

    def getColor(self):
        """Returns the color of the Rect object.\n
        """
        return pygame.Color(self._color[0], self._color[1], self._color[2], 255)

    def getFont(self):
        """Returns the font of the Rect object.\n
        """
        return self._font

async def createRankImage(discordMember):
    """Creates an XP card image for the member.

    Parameters:
        discordMember (discord.Member): The Discord Member to get the ranking stats for.
    """

    # Keep a Rect object for each image and text objects
    iconRect = Rect(
        50, 30, 135, 135,
        [255, 255, 255], None
    )

    nameRect = Rect(
        200, 30, 325, 40,
        [255, 255, 255],
        pygame.font.Font("util/image/Light.ttf", 45)
    )

    levelRect = Rect(
        200, 80, 200, 40,
        [200, 200, 200],
        pygame.font.Font("util/image/Light.ttf", 40)
    )

    expRect = Rect(
        200, 125, 200, 40,
        [128, 255, 128],
        pygame.font.Font("util/image/Light.ttf", 40)
    )

    progressRect = Rect(
        50, 180, 750, 40,
        [128, 255, 128], None
    )

    # Get necessary values for rank image
    member = await Server.getMember(discordMember.guild, discordMember)

    ID = discordMember.id
    name = discordMember.name
    nickname = discordMember.nick
    discriminator = discordMember.discriminator
    avatar = discordMember.avatar
    level = member["level"]
    currentExp = member["experience"]
    nextExp = Server.getExpFromLevel(level + 1)

    # Open rank card image
    rankImage = pygame.image.load("util/rank/xpCard.png")

    # - Add Name
    nameText = nameRect.getFont().render(
        "{} #{}".format(
            name if nickname == None else nickname, 
            discriminator
        ),
        True,
        nameRect.getColor()
    )
    rankImage.blit(nameText,(
        nameRect.getX(), nameRect.getY()
    ))

    # - Add Level
    levelText = levelRect.getFont().render(
        "Level {}".format(level),
        True,
        levelRect.getColor()
    )
    rankImage.blit(levelText, (
        levelRect.getX(), levelRect.getY()
    ))

    # - Add Experience (Current / Next)
    expText = expRect.getFont().render(
        "{} xp / {} xp".format(
            convert(currentExp),
            convert(nextExp)
        ),
        True,
        expRect.getColor()
    )
    rankImage.blit(expText, (
        expRect.getX(), expRect.getY()
    ))

    # - Add Progress Bar (Map length of bar depending on current experience and level)
    expBar = [
        int(mapping(

            # Value
            currentExp,

            # Initial Start                # Initial End
            Server.getExpFromLevel(level), Server.getExpFromLevel(level + 1),

            # Final Start                  # Final End
            0,                             progressRect.getWidth()
        )), progressRect.getHeight()
    ]
    if expBar[0] > 0:
        expBar = pygame.Surface(expBar)
        expBar.fill(progressRect.getColor())
        rankImage.blit(expBar, (
            progressRect.getX(), progressRect.getY()
        ))
    
    # - Add Icon

    # Make an HTTP request to the members avatar as a png (if avatar is not None)
    # Load the request as a raw PNG into Pillow and turn into Pygame image
    if avatar != None:

        # Make Request; Get Image through Pillow
        pygameImage = loadImageFromUrl(Server.XP_ICON_SOURCE.format(ID, avatar))

        # Resize Pygame Image and add to Rank Image
        pygameImage = pygame.transform.scale(pygameImage, (
            iconRect.getWidth(), iconRect.getHeight()
        ))
        rankImage.blit(pygameImage, (
            iconRect.getX(), iconRect.getY()
        ))
    
    # Save image to folder
    image = Server.XP_CARD_IMAGE.format(name, discriminator)
    pygame.image.save(rankImage, image)

    return image

def convert(number):
    """Converts a number into a shorthand string.\n

    Examples:
        1,985         --> 1.98k
        91,827,465    --> 91.82M
        1,854,989,454 --> 1.85B
    
    number - The number to convert.\n
    """

    # Keep track of number conversions and order
    lookup = {
        "k": 10 ** 3,
        "M": 10 ** 6,
        "B": 10 ** 9,
        "T": 10 ** 12,
        "P": 10 ** 15,
        "E": 10 ** 18,
        "Z": 10 ** 21,
        "Y": 10 ** 24
    }
    order = "YZEPTBMk"

    # See if number can be divided by any of the values
    for conversion in order:

        # Only do conversion if the number / conversion is greater than 1
        if int(number / lookup[conversion]):

            # Get number and turn into string
            number = str(number / lookup[conversion])

            # Shorten number up to 2nd decimal place
            number = number[ : number.find(".") + 3]

            return number + conversion # Add conversion to end of the resulting shortened number
    
    # No conversion took place; Return regular number
    return number

def mapping(value, start1, stop1, start2, stop2):
    """Maps a value proportionally from a start range to a final range.\n

    value - The value to retrieve a proportional value of.\n
    start1 - The lower bound of the start range.\n
    stop1 - The upper bound of the start range.\n
    start2 - The lower bound of the final range.\n
    stop2 - The upper bound of the final range.\n
    """
    return start2 + (stop2 - start2) * ((value - start1) / (stop1 - start1))