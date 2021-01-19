PIECES = {
    "bn": ":brown_circle: ",
    "bk": ":brown_square: ",
    "rn": ":red_circle: ",
    "rk": ":red_square: "
}

HIGHLIGHT = {
    "k": ":orange_square: ",
    "n": ":orange_circle: "
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