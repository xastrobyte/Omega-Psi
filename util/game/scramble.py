from util.file.database import omegaPsi

from random import choice as choose

def generateWord():
    """Returns a random word from the list of words in the database
    """
    return choose(omegaPsi.getScrambleWords()["words"])

def scrambleWord(word, difficulty):
    """Returns a scrambled word.\n

    difficulty - The difficulty of the scrambled word.\n
        Note: A \"normal\" difficulty will scramble each word (if there are multiple words).\n
              An \"expert\" difficulty will scramble the entire phrase.\n
    """

    # Normal scramble
    if difficulty == "normal":

        # Split words into list
        wordList = word.split(" ")
        newWordList = []
        for word in wordList:
            newWordList.append(
                scrambleWord(word, "expert")
            )
        
        return " ".join(newWordList)
    
    # Expert scramble
    else:

        # Split up word normally
        wordList = list(word)
        newWord = ""
        while len(wordList) > 0:
            char = choose(wordList)
            wordList.remove(char)
            newWord += char
        return newWord
