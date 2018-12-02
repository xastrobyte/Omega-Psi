from util.file.database import loop
from util.file.server import Server
from util.file.omegaPsi import OmegaPsi

from util.image import areYouAwake
from util.image import expandingBrain
from util.image import burnLetter
from util.image import butILikeThis
from util.image import carSkidding
from util.image import cardSlam
from util.image import classroomStares
from util.image import didYouMean
from util.image import icarlyStopSign
from util.image import mastersBlessing
from util.image import nArmHandshake
from util.image import pigeon
from util.image import playstation
from util.image import puppetMeme
from util.image import runAway
from util.image import saveOne
from util.image import sayItAgain
from util.image import spontaneousAnger
from util.image import surprisedDwight
from util.image import surprisedPikachu
from util.image import trojanHorse
from util.image import whoKilledHannibal

from util.utils.discordUtils import sendMessage, getErrorMessage
from util.utils.miscUtils import loadImageFromUrl
from util.utils.stringUtils import generateRandomString, capitalizeSentences

from random import choice as choose, randint
from supercog import Category, Command
import discord, os, pygame, requests

pygame.init()

scrollEmbeds = {}

class Image(Category):

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Class Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    AVATAR_LIST = "https://api.adorable.io/avatars/list"
    AVATAR_API  = "https://api.adorable.io/avatars/face/{}/{}/{}/{}"

    ROBOHASH_API = "https://robohash.org/{}"

    TIMCHEN_API = "https://timchen.tk/api"

    MEME_SUBREDDITS = [
        "meme",
        "memes",
        "dankmeme",
        "dank_meme"
    ]
    MEME_RANDOM = "https://www.reddit.com/r/{}/.json?sort=top&limit=500"

    REDDIT_BASE = "https://www.reddit.com"

    NASA_RANDOM = "https://images-api.nasa.gov/search?media_type=image&year_start=1960"
    NASA_SEARCH = "https://images-api.nasa.gov/search?q={}&media_type=image"
    DESCRIPTION_THRESHOLD = 2000

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Errors
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    NO_GIFS_FOUND = "NO_GIFS_FOUND"
    NO_IMAGE = "NO_IMAGE"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Constructor
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, client):
        super().__init__(
            client, 
            "Image",
            description = "Anything having to do with images is here.",
            embed_color = 0x800080,
            locally_inactive_error = Server.getInactiveError,
            globally_inactive_error = OmegaPsi.getInactiveError,
            locally_active_check = Server.isCommandActive,
            globally_active_check = OmegaPsi.isCommandActive
        )

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Commands
        self._gif = Command(commandDict = {
            "alternatives": ["gif", "giphy", "g"],
            "info": "Sends a random gif from Giphy.",
            "parameters": {
                "keywords": {
                    "optional": True,
                    "info": "The keywords to search for in Giphy."
                }
            },
            "errors": {
                Image.NO_GIFS_FOUND: {
                    "messages": [
                        "Hmmm. No gifs were found with those keywords. Perhaps broaden your search?"
                    ]
                }
            },
            "command": self.gif
        })

        self._avatar = Command(commandDict = {
            "alternatives": ["avatar", "avatarMe"],
            "info": "Sends a random cute avatar.",
            "errors": {
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get an avatar, you don't need any parameters."
                    ]
                }
            },
            "command": self.avatar
        })

        self._robohash = Command(commandDict = {
            "alternatives": ["robohash", "robo"],
            "info": "Sends a robohash avatar based off the text you enter.",
            "parameters":{
                "content": {
                    "info": "The text to use to generate the robohash avatar.",
                    "optional": True,
                    "accepted": {
                        "random": {
                            "alternatives": ["random", "surprise", "surpriseMe"],
                            "info": "Allows you to have a completely random robohash to be sent."
                        }
                    }
                }
            },
            "command": self.robohash
        })

        self._timchen = Command(commandDict = {
            "alternatives": ["timchen", "tim", "chen", "t"],
            "info": {
                "text": "Sends a random picture of Timchen (a Repl.it moderator) using an API made by {}",
                "hyperlink": "https://repl.it/@mat1",
                "hyperlink_text": "mat#6207"
            },
            "errors": {
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get a picture of Timchen, you don't need any parameters."
                    ]
                }
            },
            "command": self.timchen
        })

        self._nasaImage = Command(commandDict = {
            "alternatives": ["nasa", "NASA", "nasaImage", "NASAImage", "nasaImg", "NASAImg"],
            "info": "Gives you a random NASA image given a search term or no search term.",
            "parameters": {
                "term": {
                    "info": "The term to search for a NASA image.",
                    "optional": True
                }
            },
            "errors": {
                Image.NO_IMAGE: {
                    "messages": [
                        "There were no images matching that search. Try again or broaden your search term."
                    ]
                }
            },
            "command": self.nasaImage
        })

        self._meme = Command(commandDict = {
            "alternatives": ["meme"],
            "info": "Sends a random meme from Reddit.",
            "errors": {
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to get a meme, you don't need any parameters."
                    ]
                },
                Image.NO_IMAGE: {
                    "messages": [
                        "Somehow there were no memes found??? Idk try again."
                    ]
                }
            },
            "command": self.meme
        })

        self._areYouAwake = Command(commandDict = {
            "alternatives": ["areYouAwake"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": areYouAwake.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "text": {
                    "info": "The text that goes inside the speech bubble for the brain.",
                    "optional": False
                }
            },
            "errors": {
                Image.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need a single set of text wrapped in quotes (\")."
                    ]
                },
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need a single set of text wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.areYouAwake
        })

        self._expandingBrain = Command(commandDict = {
            "alternatives": ["expandingBrain", "expBrain"],
            "info": {
                "text": "Sends a generated meme based off {} image.",
                "hyperlink": expandingBrain.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "firstText": {
                    "info": "The text to put in the first box.",
                    "optional": False
                },
                "secondText": {
                    "info": "The text to put in the second box.",
                    "optional": True
                },
                "thirdText": {
                    "info": "The text to put in the third box.",
                    "optional": True
                },
                "fourthText": {
                    "info": "The text to put in the fourth box.",
                    "optional": True
                },
                "fifthText": {
                    "info": "The text to put in the fifth box.",
                    "optional": True
                },
                "sixthText": {
                    "info": "The text to put in the sixth box.",
                    "optional": True
                },
                "seventhText": {
                    "info": "The text to put in the seventh box.",
                    "optional": True
                },
                "eighthText": {
                    "info": "The text to put in the eighth box.",
                    "optional": True
                },
                "ninthText": {
                    "info": "The text to put in the ninth box.",
                    "optional": True
                },
                "tenthText": {
                    "info": "The text to put in the tenth box.",
                    "optional": True
                },
                "eleventhText": {
                    "info": "The text to put in the eleventh box.",
                    "optional": True
                }
            },
            "errors": {
                Image.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need at least a single set of text wrapped in quotes (\")."
                    ]
                },
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you can have a maximum of 11 sets of text wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.expandingBrain
        })

        self._burnLetter = Command(commandDict = {
            "alternatives": ["burnLetter"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": burnLetter.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "letterText": {
                    "info": "The text that goes on the piece of paper.",
                    "optional": False
                },
                "spongebobText": {
                    "info": "The text that goes on spongebob.",
                    "optional": False
                }
            },
            "errors": {
                Image.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need 2 sets of text wrapped in quotes (\")."
                    ]
                },
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 2 sets of text wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.burnLetter
        })

        self._butILikeThis = Command(commandDict = {
            "alternatives": ["butILikeThis", "thisIsBetter"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": butILikeThis.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "redCarText": {
                    "info": "The text to put on the red car.",
                    "optional": False
                },
                "whiteCarText": {
                    "info": "The text to put on the white car.",
                    "optional": False
                }
            },
            "errors": {
                Image.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need 2 sets of text wrapped in quotes (\")."
                    ]
                },
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 2 sets of text wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.butILikeThis
        })

        self._carSkidding = Command(commandDict = {
            "alternatives": ["carSkidding", "carSkid"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": carSkidding.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "carText": {
                    "info": "The text to put on the car.",
                    "optional": False
                },
                "straightText": {
                    "info": "The text to put on the straight ahead part of the sign.",
                    "optional": False
                },
                "exitText": {
                    "info": "The text to put on the exit part of the sign.",
                    "optional": False
                }
            },
            "errors": {
                Image.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "To generate this meme, you need to give at least 3 sets of text wrapped in quotes (\")."
                    ]
                },
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You have too many parameters for this. You only need 3 sets of text wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.carSkidding
        })

        self._cardSlam = Command(commandDict = {
            "alternatives": ["cardSlam"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": cardSlam.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "cardText": {
                    "info": "The text to put on top of the card.",
                    "optional": False
                },
                "bodyText": {
                    "info": "The text to put on top of the man.",
                    "optional": False
                },
                "tableText": {
                    "info": "The text to put on top of the table.",
                    "optional": False
                }
            },
            "errors": {
                Image.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need to have 3 sets of text each wrapped in quotes (\")."
                    ]
                },
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 3 sets of text each wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.cardSlam
        })

        self._classroomStares = Command(commandDict = {
            "alternatives": ["classroomStares"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": classroomStares.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "bubbleText": {
                    "info": "The text that shows up on the bubble quote.",
                    "optional": False
                }
            },
            "errors": {
                Image.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "You need the bubble text to generate this meme."
                    ]
                },
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You only need the bubble text to generate this meme."
                    ]
                }
            },
            "command": self.classroomStares
        })

        self._didYouMean = Command(commandDict = {
            "alternatives": ["didYouMean"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": didYouMean.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "searchText": {
                    "info": "The text that goes in the search bar.",
                    "optional": True
                },
                "didYouMeanText": {
                    "info": "The text that goes where it says *Did You Mean*",
                    "optional": False
                }
            },
            "errors": {
                Image.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "You need at least 1 parameter to generate this meme."
                    ]
                },
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You only need 2 parameters to generate this meme."
                    ]
                }
            },
            "command": self.didYouMean
        })

        self._icarlyStopSign = Command(commandDict = {
            "alternatives": ["icarlyStopSign", "icarlyStop"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": icarlyStopSign.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "spencerText": {
                    "info": "The text that goes on top of Spencer.",
                    "optional": False
                },
                "stopText": {
                    "info": "The text that goes on top of the stop sign.",
                    "optional": True
                },
                "gibbyText": {
                    "info":"The text that goes on top of Gibby.",
                    "optional": False
                }
            },
            "errors": {
                Image.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "You need 3 parameters to generate this meme."
                    ]
                },
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "You only need 3 different sets of text to put on the meme."
                    ]
                }
            },
            "command": self.icarlyStopSign
        })

        self._mastersBlessing = Command(commandDict = {
            "alternatives": ["mastersBlessing"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": mastersBlessing.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "masterText": {
                    "info": "The text that goes on top of the master.",
                    "optional": False
                },
                "swordText": {
                    "info": "The text that goes on top of the sword.",
                    "optional": False
                },
                "apprenticeText": {
                    "info": "The text that goes on top of the apprentice.",
                    "optional": False
                }
            },
            "errors": {
                Image.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need to have 3 sets of text each wrapped in quotes (\")."
                    ]
                },
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 3 sets of text each wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.mastersBlessing
        })

        self._nArmHandshake = Command(commandDict = {
            "alternatives": ["armHandshake"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": nArmHandshake.IMAGE_TWO,
                "hyperlink_text": "this"
            },
            "parameters": {
                "handsText": {
                    "info": "The text that goes on the joined hands.",
                    "optional": False
                },
                "firstArm": {
                    "info": "The text that goes on the first arm.",
                    "optional": False
                },
                "secondArm": {
                    "info": "The text that goes on the second arm.",
                    "optional": False
                },
                "thirdArm": {
                    "info": "The text that goes on the third arm.",
                    "optional": True
                },
                "fourthArm": {
                    "info": "The text that goes on the fourth arm.",
                    "optional": True
                }
            },
            "errors": {
                Image.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need at least 3 sets of text wrapped in quotes (\")."
                    ]
                },
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you can have up to 5 sets of text wrapped in quotes (\")."
                    ]
                }
            },
            "commands": self.nArmHandshake
        })

        self._pigeon = Command(commandDict = {
            "alternatives": ["pigeon", "isThisAPigeon"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": pigeon.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "pigeonText": {
                    "info": "The text that goes over top of the pigeon.",
                    "optional": False
                },
                "personText": {
                    "info": "The text that goes over top of the person.",
                    "optional": False
                },
                "questionText": {
                    "info": "The text that asks a question.",
                    "optional": False
                }
            },
            "errors": {
                Image.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need 3 sets of text wrapped in quotes (\")."
                    ]
                },
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 3 sets of text wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.pigeon
        })

        self._playstation = Command(commandDict = {
            "alternatives": ["playstation"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": playstation.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "triangleText": {
                    "info": "The text that goes next to the triangle button.",
                    "optional": True
                },
                "squareText": {
                    "info": "The text that goes next to the square button.",
                    "optional": True
                },
                "xText": {
                    "info": "The text that goes next to the X button.",
                    "optional": False
                },
                "circleText": {
                    "info": "The text that goes next to the circle button.",
                    "optional": False
                }
            },
            "errors": {
                Image.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need at least 2 sets of text wrapped in quotes (\")."
                    ]
                },
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you can have a maximum of 4 sets of text wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.playstation
        })

        self._puppetMeme = Command(commandDict = {
            "alternatives": ["puppetMeme"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": puppetMeme.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "handText": {
                    "info": "The text that goes on the puppeteers hand.",
                    "optional": False
                },
                "puppetText": {
                    "info": "The text that goes on top of the puppet.",
                    "optional": False
                }
            },
            "errors": {
                Image.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need 2 sets of text wrapped in quotes (\")."
                    ]
                },
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 2 sets of text wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.puppetMeme
        })

        self._runAway = Command(commandDict = {
            "alternatives": ["runAway"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": runAway.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "chaserText": {
                    "info": "The text that goes on top of the chaser.",
                    "optional": False  
                },
                "runnerText": {
                    "info": "The text that goes on top of the runner.",
                    "optional": False
                }
            },
            "errors": {
                Image.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need 2 sets of text wrapped in quotes (\")."
                    ]
                },
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 2 sets of text wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.runAway
        })

        self._saveOne = Command(commandDict = {
            "alternatives": ["saveOne"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": saveOne.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "personText": {
                    "info": "The text that goes on top of the person.",
                    "optional": False
                },
                "leftBehindText": {
                    "info": "The text that goes on top of the person that is left behind.",
                    "optional": False
                },
                "savedText": {
                    "info": "The text that goes on top of the person who is being saved.",
                    "optional": False
                }
            },
            "errors": {
                Image.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need to have 3 sets of text each wrapped in quotes (\")."
                    ]
                },
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 3 sets of text each wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.saveOne
        })

        self._sayItAgain = Command(commandDict = {
            "alternatives": ["sayItAgain", "dexterMeme"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": sayItAgain.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "topText": {
                    "info": "The text that goes on the top part of the image.",
                    "optional": False
                },
                "bottomText": {
                    "info": "The text that goes on the bottom part of the image.",
                    "optional": False
                }
            },
            "errors": {
                Image.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need to have 2 sets of text each wrapped in quotes (\")."
                    ]
                },
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 2 sets of text each wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.sayItAgain
        })

        self._spontaneousAnger = Command(commandDict = {
            "alternatives": ["spontaneousAnger", "angerMeme"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": spontaneousAnger.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "angerText": {
                    "info": "The text that goes above the guy who gets angry.",
                    "optional": False
                },
                "questionText": {
                    "info": "The text that goes above the guy who questions the angry guy.",
                    "optional": False
                }
            },
            "errors": {
                Image.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need to have 2 sets of text each wrapped in quotes (\")."
                    ]
                },
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 2 sets of text each wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.spontaneousAnger
        })

        self._surprisedDwight = Command(commandDict = {
            "alternatives": ["surprisedDwight"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": surprisedDwight.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "dwightText": {
                    "info": "The text that goes above Dwight.",
                    "optional": False
                },
                "angelaText": {
                    "info": "The text that goes above Angela.",
                    "optional": False
                }
            },
            "errors": {
                Image.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need to have 2 sets of text each wrapped in quotes (\")."
                    ]
                },
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 2 sets of text each wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.surprisedDwight
        })

        self._surprisedPikachu = Command(commandDict = {
            "alternatives": ["surprisedPikachu"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": surprisedPikachu.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "firstLine": {
                    "info": "The first line to put on the meme.",
                    "optional": False
                },
                "secondLine": {
                    "info": "The second line to put on the meme.",
                    "optional": False
                },
                "thirdLine": {
                    "info": "The third line to put on the meme.",
                    "optional": False
                },
                "fourthLine": {
                    "info": "The fourth line to put on the meme.",
                    "optional": True
                },
                "fifthLine": {
                    "info": "The fifth line to put on the meme.",
                    "optional": True
                }
            },
            "errors": {
                Image.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need at least 3 lines to add."
                    ]
                },
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "There is a maximum of 5 lines you can put on this meme."
                    ]
                }
            },
            "command": self.surprisedPikachu
        })

        self._trojanHorse = Command(commandDict = {
            "alternatives": ["trojanHorse"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": trojanHorse.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "hidersText": {
                    "info": "The text that goes on top of the hiders in the horse.",
                    "optional": False
                },
                "horseText": {
                    "info": "The text that goes on top of the horse head.",
                    "optional": False
                },
                "castleText": {
                    "info": "The text that goes on top of the castle.",
                    "optional": False
                },
                "welcomersText": {
                    "info": "The text that goes on top of the welcomers.",
                    "optional": False
                }
            },
            "errors": {
                Image.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need 4 sets of text wrapped in quotes (\")."
                    ]
                },
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 4 sets of text wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.trojanHorse
        })

        self._whoKilledHannibal = Command(commandDict = {
            "alternatives": ["whoKilledHannibal"],
            "info": {
                "text": "Sends a generated meme based off of {} image.",
                "hyperlink": whoKilledHannibal.IMAGE,
                "hyperlink_text": "this"
            },
            "parameters": {
                "ericAndreText": {
                    "info": "The text that goes on top of Eric Andre.",
                    "optional": False
                },
                "gunText": {
                    "info": "The text that goes on top of the gun.",
                    "optional": False
                },
                "hannibalText": {
                    "info": "The text that goes on top of Hannibal.",
                    "optional": False
                },
                "questionText": {
                    "info": "The text that goes as the question text.",
                    "optional": False
                }
            },
            "errors": {
                Image.NOT_ENOUGH_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you need 4 sets of text wrapped in quotes (\")."
                    ]
                },
                Image.TOO_MANY_PARAMETERS: {
                    "messages": [
                        "In order to generate this meme, you only need 4 sets of text wrapped in quotes (\")."
                    ]
                }
            },
            "command": self.whoKilledHannibal
        })

        self.setCommands([
            self._gif,
            self._avatar,
            self._robohash,
            self._timchen,
            self._nasaImage,

            self._meme,
            self._areYouAwake,
            self._expandingBrain,
            self._burnLetter,
            self._butILikeThis,
            self._carSkidding,
            self._cardSlam,
            self._classroomStares,
            self._didYouMean,
            self._icarlyStopSign,
            self._mastersBlessing,
            self._nArmHandshake,
            self._pigeon,
            self._playstation,
            self._puppetMeme,
            self._runAway,
            self._saveOne,
            self._sayItAgain,
            self._spontaneousAnger,
            self._surprisedDwight,
            self._surprisedPikachu,
            self._trojanHorse,
            self._whoKilledHannibal
        ])

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Command Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def gif(self, message, parameters):
        """Returns a gif from giphy.
        """

        keywords = " ".join(parameters)

        # Get data involving gifs from Giphy
        if keywords == "random":
            gifData = await loop.run_in_executor(None,
                requests.get,
                os.environ["GIPHY_RANDOM_API_URL"]
            )
            gifData = gifData.json()

            result = gifData["data"]["embed_url"]
        
        else:
            gifsData = await loop.run_in_executor(None,
                requests.get,
                os.environ["GIPHY_SEARCH_API_URL"].format(
                    keywords.replace(" ", "+")
                )
            )
            gifsData = gifsData.json()

            # Return random embed url
            if len(gifsData) > 0:
                gifData = choose(gifsData["data"])
                result = gifData["embed_url"]
            else:
                result = getErrorMessage(self._gif, Image.NO_GIFS_FOUND)
        
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result.set_footer(
                    text = "Requested by {}#{}".format(
                        message.author.name,
                        message.author.discriminator
                    ),
                    icon_url = message.author.avatar_url
                )
            )
        
        else:
            await sendMessage(
                self.client,
                message,
                message = result
            )

    async def avatar(self, message, parameters):
        """Returns a random cute avatar that can be used as a placeholder.

        Parameters:
            parameters (list): The parameters that detect for too many parameters.
        """

        # Check for too many parameters
        if len(parameters) > self._avatar.getMaxParameters():
            embed = getErrorMessage(self._avatar, Image.TOO_MANY_PARAMETERS)
            await sendMessage(
                self.client,
                message,
                embed = embed.set_footer(
                    text = "Requested by {}#{}".format(
                        message.author.name,
                        message.author.discriminator
                    ),
                    icon_url = message.author.avatar_url
                )
            )
        
        # There were the proper amount of parameters
        else:

            # Get list of face features
            faceValues = await loop.run_in_executor(None,
                requests.get,
                Image.AVATAR_LIST
            )
            faceValues = faceValues.json()["face"]

            # Choose random eyes, nose, mouth, and color
            eyes  = choose(faceValues["eyes"])
            nose  = choose(faceValues["nose"])
            mouth = choose(faceValues["mouth"])
            color = hex(randint(0, 16777215))[2:].rjust(6, "0")

            # Load image
            image = await loop.run_in_executor(None,
                loadImageFromUrl,
                Image.AVATAR_API.format(
                    eyes, nose,
                    mouth, color
                )
            )

            # Save image temporarily
            avatarFile = "{}_{}_{}_{}.png".format(
                eyes, nose, mouth, color
            )
            pygame.image.save(image, avatarFile)

            # Send file then delete image
            await sendMessage(
                self.client,
                message,
                filename = avatarFile
            )

            os.remove(avatarFile)
    
    async def robohash(self, message, parameters):
        """Sends a random robohash avatar or a generated one based off of the content.
        """

        # Generate personal robohash if content is empty
        content = " ".join(parameters)

        if len(content) == 0:
            content = "{}-{}".format(
                message.author.name,
                message.author.discriminator
            )
        
        # Generate totally random robohash if content is random
        elif content in self._robohash.getAcceptedParameters("content", "random").getAlternatives():
            content = generateRandomString()
        
        # Load image
        image = await loop.run_in_executor(None,
            loadImageFromUrl,
            Image.ROBOHASH_API.format(content)
        )

        # Save image temporarily
        avatarFile = "{}.png".format(
            content
        )
        pygame.image.save(image, avatarFile)
        
        # Send the file and then delete it
        await sendMessage(
            self.client,
            message,
            filename = avatarFile
        )

        os.remove(avatarFile)
    
    async def timchen(self, message, parameters):
        """Returns a random picture of Timchen with the caption.
        """
        
        # Check for too many parameters
        if len(parameters) > self._timchen.getMaxParameters():
            embed = getErrorMessage(self._timchen, Image.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Get a random image
            timchen = await loop.run_in_executor(None,
                requests.get,
                Image.TIMCHEN_API
            )
            timchen = timchen.json()

            embed = discord.Embed(
                title = "Timchen!",
                description = capitalizeSentences(timchen["desc"]),
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            ).set_image(
                url = timchen["url"]
            )
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def nasaImage(self, message, parameters):
        """Returns an image from NASA.
        """

        keywords = " ".join(parameters)

        # Get data involving NASA images
        if keywords == "random":
            imageData = await loop.run_in_executor(None,
                requests.get,
                Image.NASA_RANDOM
            )

        else:
            imageData = await loop.run_in_executor(None,
                requests.get,
                Image.NASA_SEARCH.format(
                    keywords.replace(" ", "+")
                )
            )
        
        imageData = imageData.json()

        # Check if there are no images
        if len(imageData["collection"]["items"]) == 0:
            embed = getErrorMessage(self._nasaImage, Image.NO_IMAGE)
        
        # There are images
        else:

            # Choose random item from collection
            item = choose(imageData["collection"]["items"])

            # Get href from item
            imageLink = item["links"][0]["href"]

            # Make sure description is less than 2000 characters
            if len(item["data"][0]["description"]) < Image.DESCRIPTION_THRESHOLD:
                description = item["data"][0]["description"]
            else:
                description = item["data"][0]["description"][:Image.DESCRIPTION_THRESHOLD] + "[...]"

            embed = discord.Embed(
                title = item["data"][0]["title"],
                description = description,
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            ).set_image(
                url = imageLink
            )

        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def meme(self, message, parameters):
        """Returns a random meme from Reddit.\n

        Parameters:
            channel (discord.Channel): The channel to send to. Helps to determine NSFW memes
        """

        # See if channel has is_nsfw
        try:
            isNSFW = message.channel.is_nsfw()
        
        # Channel is private, allow NSFW
        except:
            isNSFW = True

        # Get data involving Reddit memes
        # Choose random subreddit between meme subreddits (meme, memes, dankmemes, dank_meme)
        subreddit = choose(Image.MEME_SUBREDDITS)

        redditData = await loop.run_in_executor(None,
            requests.get,
            Image.MEME_RANDOM.format(subreddit),
            headers = {
                "User-agent": "Omega Psi"
            }
        )
        redditData = redditData.json()

        # Make sure there are reddit posts
        if len(redditData["data"]["children"]) == 0:
            embed = getErrorMessage(self._meme, Image.NO_IMAGE)
        
        # There were reddit posts
        else:

            # Choose random reddit post
            redditPost = choose(redditData["data"]["children"])["data"]
            while redditPost["is_video"] or (redditPost["over_18"] and not isNSFW):
                redditPost = choose(redditData["data"]["children"])["data"]

            # Return an embed for the reddit post
            embed = discord.Embed(
                name = "Meme Result",
                description = "[{}]({})".format(
                    redditPost["title"],
                    Image.REDDIT_BASE + redditPost["permalink"]
                ),
                colour = self.getEmbedColor() if message.guild == None else message.author.top_role.color
            ).set_image(
                url = redditPost["url"]
            ).set_footer(
                text = "👍 {} 💬 {}".format(
                    redditPost["score"],
                    redditPost["num_comments"]
                )
            )
        
        await sendMessage(
            self.client,
            message,
            embed = embed.set_footer(
                text = "Requested by {}#{}".format(
                    message.author.name,
                    message.author.discriminator
                ),
                icon_url = message.author.avatar_url
            )
        )
    
    async def areYouAwake(self, message, parameters):
        """Generates and sends the Are You Awake meme.
        """

        # Check for not enough parameters
        if len(parameters) < self._areYouAwake.getMinParameters():
            result = getErrorMessage(self._areYouAwake, Image.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._areYouAwake.getMaxParameters():
            result = getErrorMessage(self._areYouAwake, Image.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                areYouAwake.generateImage,
                parameters[0]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
        
    async def expandingBrain(self, message, parameters):
        """Generates and sends the brain size meme.
        """

        # Check for not enough parameters
        if len(parameters) < self._expandingBrain.getMinParameters():
            result = getErrorMessage(self._expandingBrain, Image.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._expandingBrain.getMaxParameters():
            result = getErrorMessage(self._expandingBrain, Image.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                expandingBrain.generateImage,
                parameters
            )
        
        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def burnLetter(self, message, parameters):
        """Generates and sends the Burn Letter meme.
        """

        # Check for not enough parameters
        if len(parameters) < self._burnLetter.getMinParameters():
            result = getErrorMessage(self._burnLetter, Image.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._burnLetter.getMaxParameters():
            result = getErrorMessage(self._burnLetter, Image.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                burnLetter.generateImage,
                parameters[0],
                parameters[1]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def butILikeThis(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._butILikeThis.getMinParameters():
            result = getErrorMessage(self._butILikeThis, Image.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._butILikeThis.getMaxParameters():
            result = getErrorMessage(self._butILikeThis, Image.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                butILikeThis.generateImage,
                parameters[0],
                parameters[1]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def carSkidding(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._carSkidding.getMinParameters():
            result = getErrorMessage(self._carSkidding, Image.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._carSkidding.getMaxParameters():
            result = getErrorMessage(self._carSkidding, Image.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                carSkidding.generateImage,
                parameters[0],
                parameters[1],
                parameters[2]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def cardSlam(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._cardSlam.getMinParameters():
            result = getErrorMessage(self._cardSlam, Image.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._cardSlam.getMaxParameters():
            result = getErrorMessage(self._cardSlam, Image.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                cardSlam.generateImage,
                parameters[0],
                parameters[1],
                parameters[2]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def classroomStares(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._classroomStares.getMinParameters():
            result = getErrorMessage(self._classroomStares, Image.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._classroomStares.getMaxParameters():
            result = getErrorMessage(self._classroomStares, Image.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                classroomStares.generateImage,
                parameters[0]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def didYouMean(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._didYouMean.getMinParameters():
            result = getErrorMessage(self._didYouMean, Image.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._didYouMean.getMaxParameters():
            result = getErrorMessage(self._didYouMean, Image.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            # Check if only 1 parameter (only generate Did You Mean part)
            if len(parameters) == 1:
                result = await loop.run_in_executor(None,
                    didYouMean.generateImage,
                    "",
                    parameters[0]
                )
            
            else:
                result = await loop.run_in_executor(None,
                    didYouMean.generateImage,
                    parameters[0],
                    parameters[1]
                )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def icarlyStopSign(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._icarlyStopSign.getMinParameters():
            result = getErrorMessage(self._icarlyStopSign, Image.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._icarlyStopSign.getMaxParameters():
            result = getErrorMessage(self._icarlyStopSign, Image.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            
            # Check if there are only 2 parameters
            if len(parameters) == 2:
                result = await loop.run_in_executor(None,
                    icarlyStopSign.generateImage,
                    parameters[0],
                    "",
                    parameters[1]
                )
            else:
                result = await loop.run_in_executor(None,
                    icarlyStopSign.generateImage,
                    parameters[0],
                    parameters[1],
                    parameters[2]
                )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def mastersBlessing(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._mastersBlessing.getMinParameters():
            result = getErrorMessage(self._mastersBlessing, Image.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._mastersBlessing.getMaxParameters():
            result = getErrorMessage(self._mastersBlessing, Image.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                mastersBlessing.generateImage,
                parameters[0],
                parameters[1],
                parameters[2]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def nArmHandshake(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._nArmHandshake.getMinParameters():
            result = getErrorMessage(self._nArmHandshake, Image.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._nArmHandshake.getMaxParameters():
            result = getErrorMessage(self._nArmHandshake, Image.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            
            # Check if there are only 3 parameters
            if len(parameters) == 3:
                result = await loop.run_in_executor(None,
                    nArmHandshake.generateImage,
                    parameters[0],
                    parameters[1],
                    parameters[2]
                )
            
            # Check if there are 4 parameters
            elif len(parameters) == 4:
                result = await loop.run_in_executor(None,
                    nArmHandshake.generateImage,
                    parameters[0],
                    parameters[1],
                    parameters[2],
                    parameters[3]
                )
            
            # Check if there are 5 parameters
            else:
                result = await loop.run_in_executor(None,
                    nArmHandshake.generateImage,
                    parameters[0],
                    parameters[1],
                    parameters[2],
                    parameters[3],
                    parameters[4]
                )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def pigeon(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._pigeon.getMinParameters():
            result = getErrorMessage(self._pigeon, Image.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._pigeon.getMaxParameters():
            result = getErrorMessage(self._pigeon, Image.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                pigeon.generateImage,
                parameters[0],
                parameters[1],
                parameters[2]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def playstation(self, message, parameters):
        """Generates and sends the brain size meme.
        """

        # Check for not enough parameters
        if len(parameters) < self._playstation.getMinParameters():
            result = getErrorMessage(self._playstation, Image.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._playstation.getMaxParameters():
            result = getErrorMessage(self._playstation, Image.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:

            triangleText = ""
            squareText = ""

            # There were 2 parameters
            if len(parameters) == 2:
                xText, circleText = parameters
            
            # There were 3 parameters
            elif len(parameters) == 3:
                squareText, xText, circleText = parameters
            
            # There were 4 parameters
            else:
                triangleText, squareText, xText, circleText = parameters

            result = await loop.run_in_executor(None,
                playstation.generateImage,
                triangleText,
                squareText,
                xText,
                circleText
            )
        
        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def puppetMeme(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._puppetMeme.getMinParameters():
            result = getErrorMessage(self._puppetMeme, Image.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._puppetMeme.getMaxParameters():
            result = getErrorMessage(self._puppetMeme, Image.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                puppetMeme.generateImage,
                parameters[0],
                parameters[1]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def runAway(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._runAway.getMinParameters():
            result = getErrorMessage(self._runAway, Image.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._runAway.getMaxParameters():
            result = getErrorMessage(self._runAway, Image.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None, 
                runAway.generateImage,
                parameters[0],
                parameters[1]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def saveOne(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._saveOne.getMinParameters():
            result = getErrorMessage(self._saveOne, Image.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._saveOne.getMaxParameters():
            result = getErrorMessage(self._saveOne, Image.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                saveOne.generateImage,
                parameters[0],
                parameters[1],
                parameters[2]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def sayItAgain(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._sayItAgain.getMinParameters():
            result = getErrorMessage(self._sayItAgain, Image.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._sayItAgain.getMaxParameters():
            result = getErrorMessage(self._sayItAgain, Image.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                sayItAgain.generateImage,
                parameters[0],
                parameters[1]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def spontaneousAnger(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._spontaneousAnger.getMinParameters():
            result = getErrorMessage(self._spontaneousAnger, Image.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._spontaneousAnger.getMaxParameters():
            result = getErrorMessage(self._spontaneousAnger, Image.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(
                spontaneousAnger.generateImage,
                parameters[0],
                parameters[1]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def surprisedDwight(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._surprisedDwight.getMinParameters():
            result = getErrorMessage(self._surprisedDwight, Image.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._surprisedDwight.getMaxParameters():
            result = getErrorMessage(self._surprisedDwight, Image.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
           result = await loop.run_in_executor(None, 
                surprisedDwight.generateImage,
                parameters[0],
                parameters[1]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def surprisedPikachu(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._surprisedPikachu.getMinParameters():
            result = getErrorMessage(self._surprisedPikachu, Image.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._surprisedPikachu.getMaxParameters():
            result = getErrorMessage(self._surprisedPikachu, Image.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                surprisedPikachu.generateImage,
                parameters
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def trojanHorse(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._trojanHorse.getMinParameters():
            result = getErrorMessage(self._trojanHorse, Image.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._trojanHorse.getMaxParameters():
            result = getErrorMessage(self._trojanHorse, Image.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None, 
                trojanHorse.generateImage,
                parameters[0],
                parameters[1],
                parameters[2],
                parameters[3]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)
    
    async def whoKilledHannibal(self, message, parameters):
        """
        """
        
        # Check for not enough parameters
        if len(parameters) < self._whoKilledHannibal.getMinParameters():
            result = getErrorMessage(self._whoKilledHannibal, Image.NOT_ENOUGH_PARAMETERS)
        
        # Check for too many parameters
        elif len(parameters) > self._whoKilledHannibal.getMaxParameters():
            result = getErrorMessage(self._whoKilledHannibal, Image.TOO_MANY_PARAMETERS)
        
        # There were the proper amount of parameters
        else:
            result = await loop.run_in_executor(None,
                whoKilledHannibal.generateImage,
                parameters[0],
                parameters[1],
                parameters[2],
                parameters[3]
            )

        # Check if an error was made
        if type(result) == discord.Embed:
            await sendMessage(
                self.client,
                message,
                embed = result
            )
        
        # No error was made, send image
        else:

            # Send message then remove image
            await sendMessage(
                self.client,
                message,
                filename = result
            )

            os.remove(result)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Parsing
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def on_message(self, message):
        """Parses a message and runs an Image Category command if it can.\n

        message - The Discord Message to parse.\n
        """

        # Make sure message starts with the prefix
        if Server.startsWithPrefix(message.guild, message.content) and not message.author.bot:

            # Split up into command and parameters if possible
            command, parameters = Category.parseText(Server.getPrefixes(message.guild), message.content)
            
            # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

            # Iterate through commands
            for cmd in self.getCommands():
                if command in cmd.getAlternatives():

                    # Run the command but don't try running others
                    await self.run(message, cmd, cmd.getCommand(), message, parameters)
                    break

def setup(client):
    client.add_cog(Image(client))