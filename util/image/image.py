import pygame
pygame.init()

def renderLines(source, origin, lines, font, color, *, angle = 0, centeredX = True, centeredY = True):
    """Renders lines on a pygame surface.

    Parameters:
        source (pygame.image): The source to add to.
        origin (list): The x,y coordinates of the origin of the lines.
        lines (list): The lines to add.
        font (pygame.font): The font to use to render.
        color (list): The color of the text.
        angle (int): The angle to set for the text.
    """

    # Get largestWidth and height of surface
    width = 0
    height = 0
    for line in range(len(lines)):
        if font.size(lines[line])[0] + 5 > width:
            width = font.size(lines[line])[0] + 5
        height += font.size(lines[line])[1] + 5

    # Create temporary surface for text that can be rotated
    tempSurf = pygame.Surface((width, height), pygame.SRCALPHA, 32)
    tempSurf.set_alpha(255)

    for line in range(len(lines)):
        cardText = font.render(lines[line], True, color)
        tempSurf.blit(
            cardText,
            [
                0,
                line * (font.get_height() + 2)
            ]
        )
    
    # Add temporary surface at an angle
    tempSurf = pygame.transform.rotate(tempSurf, angle)
    source.blit(tempSurf, (
        origin[0] - ((tempSurf.get_width() / 2) if centeredX else 0),
        origin[1] - ((tempSurf.get_height() / 2) if centeredY else 0)
    ))
    return source
