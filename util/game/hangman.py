from util.file.database import omegaPsi

from random import choice as choose

def generateWord(difficulty = "easy"):
    """Generates a random word and returns it in hangman style.\n

    difficulty - The difficulty of the word to get.\n

        Examples:\n
            \"half-asleep\" --> \"_ _ _ _ - _ _ _ _ _ _\"\n
            \"ping pong\"   --> \"_ _ _ _  _ _ _ _\"\n
            \"apple\"       --> \"_ _ _ _ _\"\n
    """

    # Try getting difficulty
    try:
        word = choose(omegaPsi.getHangmanWords()[difficulty])
    
    # Difficulty was invalid, return None
    except:
        return None
    
    return word

def getWord(word, found = []):

    # Replace letters in word if letter was not found
    newWord = ""
    for char in range(len(word)):
        if word[char] in found:
            newWord += word[char]
        else:
            if word[char].isalpha():
                newWord += "_"
            else:
                newWord += word[char]

        # Only add extra space between letters if char is less than length - 1
        if char < len(word) - 1:
            newWord += " "
    
    return "`{}`".format(newWord)

def getHangman(guesses = 0):
    """Returns the Hangman ascii text depending on how many guesses there are.\n

    guesses - The amount of guesses a user has made.\n
    """

    hangman = (
        "```css\n" +
        "+----+    \n" +
        "|    |    \n" +
        "|    {0}    \n" +
        "|   {2}{1}{3}   \n" +
        "|    {4}    \n" +
        "|   {5} {6}   \n" +
        "|         \n" +
        "+--------+\n" +
        "|  {7}  |\n" +
        "+--------+\n" +
        "```"
    )

    return hangman.format(
        "0" if guesses >= 1 else " ",
        "|" if guesses >= 2 else " ",
        "\\" if guesses >= 3 else " ",
        "/" if guesses >= 4 else " ",
        "|" if guesses >= 5 else " ",
        "/" if guesses >= 6 else " ",
        "\\" if guesses >= 7 else " ",
        "DEAD" if guesses >= 7 else "    "
    )
