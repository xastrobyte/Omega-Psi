PIECES = {
    "K": "<:WK:773990181170053140> ",
    "Q": "<:WQ:773990181001887764> ",
    "B": "<:WB:773990181052743680> ",
    "R": "<:WR:773990180930715679> ",
    "N": "<:WN:773990181148819477> ",
    "P": "<:WP:773990180687708180> ",
    "WS": ":white_large_square: ",
    "BS": ":brown_square: ",
    "k": "<:BK:773990180980785163> ",
    "q": "<:BQ:773990181136498748> ",
    "b": "<:BB:773990180997955594> ",
    "r": "<:BR:773990180939235358> ",
    "n": "<:BN:773990181023383644> ",
    "p": "<:BP:773990180897685525> "
}

HIGHLIGHT = {
    "k": "<:SK:774072444150874163> ",
    "q": "<:SQ:774072444234498059> ",
    "b": "<:SB:774072444251275274> ",
    "r": "<:SR:774072444088614983> ",
    "n": "<:SN:774072444235415622> ",
    "p": "<:SP:774072444117844038> "
}

COLUMNS = {
    f"{str(num)}\u20e3": chr(num + 96)
    for num in range(1, 9)
}

NUMBERS = [
    f"{str(num)}\u20e3"
    for num in range(1, 9)
]

UNDO = "↩️"
RESIGN = "❌"