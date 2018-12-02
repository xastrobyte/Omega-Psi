from random import choice, randint

PROFANE_WORDS = [
    "asshole", "bastard", "bitch", "cock", "dick", "cunt", "pussy",
    "fuck", "shit", "chode", "choad", "wanker", "twat", "nigger", "nigga",
    "tits", "jizz", "dildo", "douche"
]

def censor(text, inCodeBlock = False):
    """Returns a censored version of the string given

    text - The string to censor
    """

    profaneWords = [profane for profane in PROFANE_WORDS if profane in text]

    # Replace text (keep first and last letters of word; replace middle with *)
    for profanity in profaneWords:
        censored = (
            "{}{}{}".format(
                profanity[0],                   # Add first letter of profane word
                "{}".format(                        # Make each letter in between first and last an asterik
                    "*" if inCodeBlock else "\*"        # If the censored word is in a code block, keep it normal
                ) * (len(profanity) - 2),               # If not, add a backslash to prevent text formatting
                profanity[len(profanity) - 1]   # Add last letter of profane word
            )
        )
        text = text.replace(profanity, censored)
    
    return text

def generateRandomString():
    """Generates a random string with a random length.
    """

    characters = (
        [chr(i) for i in range(ord("A"), ord("Z") + 1)] + 
        [chr(i) for i in range(ord("a"), ord("z") + 1)] +
        [chr(i) for i in range(ord("0"), ord("9") + 1)]
    )

    # Choose random length
    length = randint(1, 100)
    result = ""
    for index in range(length):

        # Choose random character
        character = choice(characters)
        result += character
    
    return result

def minutesToRuntime(minutes):
    """Turns minutes into a runtime string.

    Parameters:
        minutes (int): The minutes to turn into a runtime string.
    """

    hours = minutes // 60
    return "{}h {}m".format(hours, minutes - (hours * 60))

def splitText(text, size, byWord = True):
    """Splits text up by size.\n

     - text - The text to split.\n
     - size - The maximum size of each string.\n
     - byWord - Whether or not to split up the text by word or by letter.\n
    """

    # Split up by word
    if byWord:
        text = text.split(" ")

    # Keep track of fields and fieldText
    fields = []
    fieldText = ""
    for value in text:

        value += " " if byWord else ""
        
        if len(fieldText) + len(value) >= size:
            fields.append(fieldText)
            fieldText = ""
        
        fieldText += value
    
    if len(fieldText) > 0:
        fields.append(fieldText)
    
    return fields

def capitalizeSentences(string, delimiters = [".", "?", "!"]):
    """Splits up a string into sentences using the delimiters and capitalizes each one.

    If there is no space after a delimiter, there will be no split done.

    Parameters:
        string (str): The string to capitalize each sentence in.
        delimiters (list): A list of characters to split up sentences by.
    """

    # Keep track of sentences
    sentences = []
    last = 0

    # Iterate through string
    for index in range(len(string)):

        # Only split when not at the end; The end is automatically handled later
        if index < len(string) - 1:

            # See if the current character is a delimiter
            if string[index] in delimiters and string[index + 1] == " ":
                sentences.append(string[last: index + 1])
                last = index + 2
    
    # This is where we add the trailing sentence
    sentences.append(string[last:])

    # Now capitalize each sentence and join them
    for index in range(len(sentences)):
        sentences[index] = sentences[index].capitalize()
    
    return " ".join(sentences)