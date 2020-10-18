# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Keep a dictionary of formattings to follow when loading a BlackCard or WhiteCard
REPLACEMENTS = {
    "&reg;": "",
    "&trade;": "",
    "_": "\_\_\_\_\_\_\_\_\_",
    "<br/>": "\n",
    "&quot;": "\"",
    "&amp;": "&",
    "<i>": "*",
    "</i>": "*",
    "<br>": "\n",
    "&uarr;": ":arrow_up: ",
    "&darr;": ":arrow_down: ",
    "&larr;": ":arrow_left: ",
    "&rarr;": ":arrow_right: ",
    "</br>": "\n"
}

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class BlackCard:
    """A BlackCard object holds the data for a black card in Cards Against Humanity

    :param json: A JSON object containing the "text" on the card and how many white cards
            each player should "pick" from their hand
    """

    def __init__(self, json):
        self.text = json["text"]
        self.pick = json["pick"]

        # Replace all the text from the replacements object
        for replacement in REPLACEMENTS:
            self.text = self.text.replace(replacement, REPLACEMENTS[replacement])
    
    def __str__(self):
        return self.text
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Getters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    @property
    def text(self):
        return self.__text
    
    @property
    def pick(self):
        return self.__pick

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Setters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    @text.setter
    def text(self, text):
        self.__text = text
    
    @pick.setter
    def pick(self, pick):
        self.__pick = pick

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class WhiteCard:
    """A WhiteCard object holds the data for a white card in Cards Against Humanity

    :param text: The text on this WhiteCard
    """

    def __init__(self, text):
        self.text = text

        # Replace all the text from the replacements object
        for replacement in REPLACEMENTS:
            self.text = self.text.replace(replacement, REPLACEMENTS[replacement])
    
    def __str__(self):
        return self.text
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Getters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    @property
    def text(self):
        return self.__text

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Setters
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    @text.setter
    def text(self, text):
        self.__text = text