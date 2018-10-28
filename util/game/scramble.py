from random import choice as choose

WORDS = [
    "unused", "longing", "quaint", "remember", "windy",
    "correct", "science", "prevent", "chalk", "limit",
    "question", "dinosaurs", "flagrant", "fearful", "complete",
    "feigned", "trousers", "sisters", "wealthy", "treatment",
    "advertisement", "territory", "employ", "steam", "word",
    "discussion", "aromatic", "disgusted", "stitch", "share",
    "threatening", "report", "languid", "scrub", "wool",
    "squealing", "gleaming", "obscene", "useful", "locket",
    "reflective", "cautious", "shocking", "gaudy", "natural", 
    "honorable", "ragged", "stage", "prick", "haunt",
    "flash", "wheel", "spark", "jail", "test", 
    "scarecrow", "puncture", "needless", "bleach", "bottle",
    "silver", "apologize", "country", "abrasive", "march",
    "governor", "aboriginal", "illustrious", "religion", "wrong",
    "hurried", "elastic", "subsequent", "purring", "closed",
    "attract", "loving", "upbeat", "bathe", "oranges",
    "airplane", "faulty", "royal", "wound", "structure",
    "earsplitting", "materialistic", "knotty", "radiate", "flawless",
    "laughable", "productive", "achiever", "knotty", "error"
]

def generateWord():
    """Returns a random word from the list of words
    """
    return choose(WORDS)

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